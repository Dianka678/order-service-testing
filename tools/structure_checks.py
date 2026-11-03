"""Структурные проверки студенческого проекта (AST и файлы).

Этот модуль лежит и в студенческом наборе (tools/), и у преподавателя (grader/):
студенты видят, что именно проверяется. Результат — список Check.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Check:
    id: str
    step: str
    title: str
    max_points: float
    ok: bool
    detail: str = ""

    @property
    def points(self) -> float:
        return self.max_points if self.ok else 0.0


# ── вспомогательное ────────────────────────────────────────────────────
def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None


def _dotted(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _calls(tree: ast.Module | None, name: str) -> int:
    """Сколько раз встречается вызов/декоратор/атрибут с данным dotted-именем (с учётом хвоста)."""
    if tree is None:
        return 0
    call_funcs = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    count = 0
    for node in ast.walk(tree):
        if id(node) in call_funcs:
            continue  # саму функцию вызова считаем один раз — через ast.Call
        target = node.func if isinstance(node, ast.Call) else node
        if isinstance(target, (ast.Attribute, ast.Name)) and _dotted(target).endswith(name):
            count += 1
    return count


def _is_stub(func: ast.FunctionDef) -> bool:
    """Тело — только docstring/pass/raise NotImplementedError (то есть метод не реализован)."""
    for stmt in func.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            continue
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Raise) and _is_not_implemented(stmt):
            continue
        return False
    return True


def _is_fixture_decorator(dec: ast.AST) -> bool:
    node = dec.func if isinstance(dec, ast.Call) else dec
    return _dotted(node) in ("pytest.fixture", "fixture")


def _fixtures(tree: ast.Module | None) -> list[ast.FunctionDef]:
    if tree is None:
        return []
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and any(_is_fixture_decorator(d) for d in n.decorator_list)
    ]


def _is_not_implemented(node: ast.Raise) -> bool:
    exc = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
    return isinstance(exc, ast.Name) and exc.id == "NotImplementedError"


def _uses_mark(tree: ast.Module | None, mark: str) -> bool:
    return _calls(tree, f"pytest.mark.{mark}") > 0 or _calls(tree, f"mark.{mark}") > 0


# ── проверки ──────────────────────────────────────────────────────────
def run_checks(root: Path) -> list[Check]:
    tests = root / "tests"
    t_pricing = _parse(tests / "test_pricing.py")
    t_service = _parse(tests / "test_order_service.py")
    t_notify = _parse(tests / "test_notifications.py")
    t_repo = _parse(tests / "test_order_repository.py")
    conftest = _parse(tests / "conftest.py")
    fakes = _parse(tests / "fakes.py")
    out: list[Check] = []

    def add(id_, step, title, pts, ok, detail=""):
        out.append(Check(id_, step, title, pts, bool(ok), detail))

    # Шаг 1
    add("s1_parametrize", "pricing", "test_pricing.py: не менее 2 тестов с @pytest.mark.parametrize", 1,
        _calls(t_pricing, "pytest.mark.parametrize") >= 2)
    add("s1_raises", "pricing", "test_pricing.py: не менее 2 проверок pytest.raises", 1,
        _calls(t_pricing, "pytest.raises") >= 2)

    # Шаг 2
    fx = _fixtures(conftest)
    add("s2_fixtures", "service", "conftest.py: не менее 3 фикстур (товары, репозиторий, сервис…)", 2, len(fx) >= 3,
        f"найдено {len(fx)}")
    fake_classes = []
    if fakes:
        for cls in [n for n in fakes.body if isinstance(n, ast.ClassDef)]:
            methods = {m.name for m in cls.body if isinstance(m, ast.FunctionDef) and not _is_stub(m)}
            if {"get"} <= methods:
                fake_classes.append(cls.name)
    add("s2_fakes", "service", "fakes.py: не менее 2 fake-репозиториев (товары и заказы) с методом get", 2,
        len(fake_classes) >= 2, f"найдено {len(fake_classes)}")
    add("s2_parametrize", "service", "test_order_service.py: используется @pytest.mark.parametrize", 2,
        _calls(t_service, "pytest.mark.parametrize") >= 1)

    # Шаг 3
    spy = False
    raising = False
    if fakes or t_notify:
        for tree in (fakes, t_notify):
            if tree is None:
                continue
            for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
                for m in [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "send"]:
                    if any(isinstance(x, ast.Raise) and not _is_not_implemented(x) for x in ast.walk(m)):
                        raising = True
                    elif any(isinstance(x, ast.Call) and _dotted(x.func).endswith("append") for x in ast.walk(m)):
                        spy = True
    mock_used = _calls(t_notify, "Mock") + _calls(t_notify, "MagicMock") > 0
    add("s3_spy", "notify", "Есть spy/mock уведомителя (класс с send, запоминающий вызовы, или Mock(spec=…))", 1,
        spy or mock_used)
    side = any(
        isinstance(k, ast.keyword) and k.arg == "side_effect" for n in ast.walk(t_notify) if isinstance(n, ast.Call) for k in n.keywords
    ) if t_notify else False
    side = side or any(isinstance(n, ast.Attribute) and n.attr == "side_effect" for n in (ast.walk(t_notify) if t_notify else []))
    add("s3_failure", "notify", "Есть уведомитель, который падает (stub с raise в send или side_effect)", 1,
        raising or side)

    # Шаг 4
    has_params = any(
        isinstance(k, ast.keyword) and k.arg == "params"
        for f in _fixtures(conftest) + _fixtures(t_repo)
        for d in f.decorator_list if isinstance(d, ast.Call)
        for k in d.keywords
    ) or _calls(t_repo, "pytest.mark.parametrize") > 0
    add("s4_contract", "sqlite", "Контрактные тесты: один набор проверок для fake и SQLite (фикстура с params или parametrize)", 1,
        has_params)
    add("s4_marker", "sqlite", "test_order_repository.py помечен @pytest.mark.integration", 1,
        _uses_mark(t_repo, "integration"))

    # Шаг 5: pytest.ini и маркеры
    ini = root / "pytest.ini"
    ini_text = ini.read_text(encoding="utf-8") if ini.exists() else ""
    has_markers = bool(re.search(r"^\s*unit\b", ini_text, re.M)) and bool(re.search(r"^\s*integration\b", ini_text, re.M))
    unit_used = any(_uses_mark(_parse(p), "unit") for p in tests.glob("test_*.py")) if tests.exists() else False
    add("s5_markers", "infra", "pytest.ini регистрирует unit и integration, а unit реально используется в тестах", 2,
        has_markers and unit_used)

    # CI
    wf_dir = root / ".github" / "workflows"
    wf_text = "\n".join(p.read_text(encoding="utf-8") for p in list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))) if wf_dir.exists() else ""
    ci_ok = all(s in wf_text for s in ("pytest", "--cov", "upload-artifact", "always()"))
    add("s5_ci", "infra", "CI: .github/workflows/*.yml запускает pytest с --cov и сохраняет артефакты (upload-artifact, if: always())", 3,
        ci_ok)

    # REPORT.md
    report = root / "REPORT.md"
    answers_ok = False
    detail = "REPORT.md не найден"
    if report.exists():
        text = report.read_text(encoding="utf-8")
        parts = re.split(r"^##\s+Вопрос\s+\d+.*$", text, flags=re.M)[1:]
        lengths = []
        for part in parts:
            body = re.sub(r"<!--.*?-->", "", part, flags=re.S)
            body = re.sub(r"(?m)^>.*$", "", body)  # цитаты-подсказки
            lengths.append(len(re.sub(r"\s+", " ", body).strip()))
        answers_ok = len(lengths) >= 4 and all(n >= 150 for n in lengths[:4])
        detail = f"длины ответов: {lengths}"
    add("s5_report", "infra", "REPORT.md: ответы на 4 вопроса (каждый не короче 150 символов)", 2, answers_ok, detail)
    docs = root / "docs"
    shots = (docs / "allure.png").exists() and (docs / "coverage.png").exists()
    add("s5_screens", "infra", "docs/allure.png и docs/coverage.png (скриншоты отчётов)", 2, shots)
    return out


if __name__ == "__main__":
    import sys

    for c in run_checks(Path(sys.argv[1] if len(sys.argv) > 1 else ".")):
        print(("✓" if c.ok else "✗"), f"[{c.max_points:g}]", c.title, c.detail)

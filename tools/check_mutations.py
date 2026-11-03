import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
MUTATIONS = [
    ("discount_boundary_10", "app/pricing.py", "quantity >= 10", "quantity > 10"),
    ("discount_boundary_50", "app/pricing.py", "quantity >= 50", "quantity > 50"),
    ("rounding_half_even", "app/pricing.py", "ROUND_HALF_UP", "ROUND_HALF_EVEN"),
    ("full_stock_rejected", "app/service.py", "product.stock < quantity", "product.stock <= quantity"),
    ("order_not_saved", "app/service.py", "self._orders.add(Order(None, user_id, product_id, quantity, total))", "Order(1, user_id, product_id, quantity, total)"),
    ("wrong_notification_recipient", "app/service.py", "self._notifier.send(order.user_id, text)", "self._notifier.send(order.product_id, text)"),
    ("duplicate_notification", "app/service.py", "        self._notify(order, product)\n", "        self._notify(order, product)\n        self._notify(order, product)\n"),
    ("notification_error_escapes", "app/service.py", "        except Exception:\n", "        except Exception:\n            raise\n"),
    ("missing_user_filter", "app/sqlite_repo.py", "WHERE user_id = ? ORDER BY id", "WHERE ? IS NOT NULL ORDER BY id"),
    ("reversed_order", "app/sqlite_repo.py", "ORDER BY id\"", "ORDER BY id DESC\""),
    ("missing_quantity_constraint", "app/sqlite_repo.py", " CHECK (quantity > 0)", ""),
]


def run_tests(directory, report):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-o", "addopts=", f"--junitxml={report}"],
        cwd=directory,
        env={**os.environ, "PYTHONPATH": str(directory)},
        capture_output=True,
        text=True,
    )


def main():
    results = []
    with tempfile.TemporaryDirectory() as temporary:
        workspace = Path(temporary)
        for folder in ("app", "tests"):
            shutil.copytree(ROOT / folder, workspace / folder, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "pytest.ini", workspace / "pytest.ini")
        report = workspace / "results.xml"
        baseline = run_tests(workspace, report)
        if baseline.returncode:
            print(baseline.stdout + baseline.stderr)
            return 1
        for name, filename, old, new in MUTATIONS:
            path = workspace / filename
            original = path.read_text()
            if old not in original:
                raise RuntimeError(f"Не найден фрагмент для мутации {name}")
            try:
                path.write_text(original.replace(old, new))
                process = run_tests(workspace, report)
                cases = ET.parse(report).findall(".//testcase")
                failures = [f"{case.attrib['classname']}::{case.attrib['name']}" for case in cases if case.find("failure") is not None]
                errors = [case for case in cases if case.find("error") is not None]
                killed = process.returncode == 1 and bool(failures) and not errors
                result = {"mutation": name, "file": filename, "before": old, "after": new, "killed": killed, "failed_tests": failures}
                results.append(result)
                print(f"{'KILLED' if killed else 'SURVIVED/ERROR'} {name}: {len(failures)} failed tests")
            finally:
                path.write_text(original)
                for cache in (workspace / "app").rglob("__pycache__"):
                    shutil.rmtree(cache)
    (ROOT / "docs" / "mutations.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Мутационная проверка", "", "Изолированные копии проекта, по одной поломке за запуск. Исходный код проекта не меняется.", "", "| Мутация | Результат | Пример упавшего теста |", "|---|---|---|"]
    for result in results:
        example = result['failed_tests'][0] if result['failed_tests'] else "—"
        lines.append(f"| `{result['mutation']}` | {'Обнаружена' if result['killed'] else 'Не обнаружена / ошибка запуска'} | `{example}` |")
    (ROOT / "docs" / "MUTATIONS.md").write_text("\n".join(lines) + "\n")
    return 0 if all(result["killed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Предварительная самопроверка перед сдачей.

    python tools/self_check.py

Показывает то, что можно проверить у себя: примеры из задания, ваши тесты, покрытие,
структуру проекта. Чего здесь НЕТ (это проверяет преподаватель):
  * скрытые тесты вашей реализации (больше случаев, чем в spec/);
  * «мутации»: в эталонную реализацию вносят поломки и смотрят, замечают ли их ВАШИ тесты.
Поэтому зелёный self_check — условие необходимое, но не достаточное. Как проверить свои
тесты на «мутации» самому, написано в GUIDE.md (раздел «Мутационная самопроверка»).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from structure_checks import run_checks  # noqa: E402

COVERAGE_TIERS = [(90, 6), (80, 4), (70, 2), (50, 1)]


def run(args: list[str]) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=", *args]
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)


def tail(proc: subprocess.CompletedProcess, n: int = 6) -> str:
    return "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-n:])


def main() -> int:
    print("== 1. Примеры из задания (spec/) ==")
    p = run(["spec"])
    print(tail(p, 3))

    print("\n== 2. Ваши тесты (tests/) + покрытие по веткам ==")
    with tempfile.TemporaryDirectory() as tmp:
        cov = Path(tmp) / "cov.json"
        p2 = run(["tests", "--cov=app", "--cov-branch", f"--cov-report=json:{cov}"])
        print(tail(p2, 4))
        pct = round(json.loads(cov.read_text())["totals"]["percent_covered"], 1) if cov.exists() else 0.0
    pts = next((v for thr, v in COVERAGE_TIERS if pct >= thr), 0)
    print(f"Покрытие: {pct}%  → {pts}/6 баллов (порог полного балла — 90%)")
    if p2.returncode != 0:
        print("⚠ Тесты красные: исправьте реализацию или тест, прежде чем сдавать.")

    print("\n== 3. Структура и инфраструктура ==")
    checks = run_checks(ROOT)
    for c in checks:
        print(f" {'✓' if c.ok else '✗'} [{c.max_points:g}] {c.title} {c.detail}")
    got = sum(c.points for c in checks)
    total = sum(c.max_points for c in checks)
    print(f"Структура: {got:g}/{total:g}")

    print("\n== Итог локальной проверки ==")
    print(f"Баллы, которые видны вам: структура {got:g}/{total:g} + покрытие {pts}/6")
    print("Остальное (≈73 балла: реализация и качество тестов) посчитают скрытые тесты и мутации.")
    return 0 if p.returncode == 0 and p2.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

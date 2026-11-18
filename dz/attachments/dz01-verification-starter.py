#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 1. Верификация ИИ-сгенерированной сортировки — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-01 (Cases) и методикой верификации по шагам 1–4
(docs/ai-verification.md). Проверяемый код лежит рядом, в dz01-ai-code.py;
исправлять его до завершения верификации запрещено.

Запуск: python dz01-verification-starter.py --variant N
"""
from __future__ import annotations

import argparse
import importlib.util
import random
import statistics
import time
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. Загрузка проверяемого кода
# ---------------------------------------------------------------------------
# Имя файла содержит дефисы, поэтому обычный import не подходит —
# модуль загружается по пути через importlib.

AI_CODE_PATH = Path(__file__).with_name("dz01-ai-code.py")


def load_quicksort():
    """Загружает функцию quicksort из соседнего файла dz01-ai-code.py."""
    spec = importlib.util.spec_from_file_location("dz01_ai_code", AI_CODE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.quicksort


quicksort = load_quicksort()

# ---------------------------------------------------------------------------
# 1. Шаг 1 методики: инварианты сортировки
# ---------------------------------------------------------------------------


def is_sorted(a: list[int]) -> bool:
    """Инвариант 1: последовательность упорядочена по неубыванию."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def same_multiset(a: list[int], b: list[int]) -> bool:
    """Инвариант 2: b — перестановка a (мультимножества элементов совпадают)."""
    return Counter(a) == Counter(b)


def check_invariants(original: list[int], result: list[int]) -> list[str]:
    """Возвращает список нарушенных инвариантов (пустой список — нарушений нет)."""
    problems = []
    if not is_sorted(result):
        problems.append("И1: выход не упорядочен")
    if not same_multiset(original, result):
        problems.append(f"И2: выход не перестановка входа (длина {len(original)} -> {len(result)})")
    return problems


# ---------------------------------------------------------------------------
# 2. Шаг 2 методики: репрезентативные тесты
# ---------------------------------------------------------------------------


def representative_cases(rng: random.Random) -> list[tuple[str, list[int]]]:
    """Именованные тестовые входы по классам методики.

    Обязательные классы: граничные (пустой, один, два элемента);
    вырожденные (все элементы равны, уже отсортированный, обратно
    отсортированный); типовые случайные с дубликатами и отрицательными
    числами (генерируются через rng — seed по варианту).
    """
    return [
        ("граничный: пустой", []),
        ("граничный: один элемент", [7]),
        ("граничный: два элемента по возрастанию", [1, 2]),
        ("граничный: два элемента по убыванию", [2, 1]),
        ("вырожденный: два равных", [4, 4]),
        ("вырожденный: все равны (10)", [5] * 10),
        ("вырожденный: все равны (1000)", [3] * 1000),
        ("вырожденный: отсортированный (100)", list(range(100))),
        ("вырожденный: обратный (100)", list(range(100, 0, -1))),
        ("вырожденный: отсортированный (2000)", list(range(2000))),
        ("вырожденный: обратный (2000)", list(range(2000, 0, -1))),
        ("случайный с дубликатами и отрицательными (50)", [rng.randint(-10, 10) for _ in range(50)]),
        ("случайный с дубликатами и отрицательными (500)", [rng.randint(-100, 100) for _ in range(500)]),
        ("случайный без дубликатов (1000)", rng.sample(range(-5000, 5000), 1000)),
    ]


def run_representative_tests(rng: random.Random) -> None:
    """Прогоняет quicksort по всем классам входов и печатает нарушения инвариантов."""
    print("\n== Шаги 1–2: инварианты на репрезентативных входах ==")
    for name, data in representative_cases(rng):
        snapshot = list(data)
        try:
            result = quicksort(list(data))
        except RecursionError:
            print(f"  [ДЕФЕКТ] {name}: RecursionError")
            continue
        problems = check_invariants(snapshot, result)
        if result != sorted(snapshot) and not problems:
            problems.append("расхождение с sorted()")
        print(f"  [{'ДЕФЕКТ' if problems else 'ok'}] {name}" + (": " + "; ".join(problems) if problems else ""))


# ---------------------------------------------------------------------------
# 3. Шаг 3 методики: сравнение с эталоном sorted()
# ---------------------------------------------------------------------------

def _fails(data: list[int]) -> bool:
    try:
        return quicksort(list(data)) != sorted(data)
    except RecursionError:
        return True
 
 
def _shrink(data: list[int]) -> list[int]:
    """Удаляет элементы, пока вход остаётся расходящимся с эталоном."""
    cur = list(data)
    changed = True
    while changed:
        changed = False
        for i in range(len(cur)):
            cand = cur[:i] + cur[i + 1:]
            if _fails(cand):
                cur, changed = cand, True
                break
    return cur


def compare_with_reference(rng: random.Random, runs: int = 300) -> None:
    """Сверка quicksort с sorted() на сотнях случайных входов.

    Генерируйте входы разных размеров (включая маленькие: именно на них
    удобно локализовать расхождение), обязательно с дубликатами и
    отрицательными числами. Каждое расхождение печатайте вместе со входом,
    чтобы затем свести его к минимальному контрпримеру.
    """
    print(f"\n== Шаг 3: сравнение с sorted() ({runs} входов) ==")
    failing = []
    for _ in range(runs):
        n = rng.choice([0, 1, 2, 3, 5, 10, 30, 100, 200])
        span = rng.choice([3, 20, 1000])
        data = [rng.randint(-span, span) for _ in range(n)]
        if _fails(data):
            failing.append(data)
    print(f"  расхождений: {len(failing)} из {runs}")
    if failing:
        mini = _shrink(min(failing, key=len))
        print(f"  минимальный контрпример: вход {mini} -> получено {quicksort(list(mini))}, "
              f"ожидалось {sorted(mini)}")

# ---------------------------------------------------------------------------
# 4. Шаг 4 методики: бенчмарк на трёх классах входов
# (методика — docs/reproducibility.md: прогрев, >=5 повторов, медиана)
# ---------------------------------------------------------------------------

SIZES = [500, 1_000, 2_000, 4_000, 8_000]
REPEATS = 5
INPUT_KINDS = ("random", "sorted", "reversed")


def make_input(rng: random.Random, n: int, kind: str) -> list[int]:
    """Вход размера n одного из трёх классов: random / sorted / reversed."""
    a = [rng.randint(-1000, 1000) for _ in range(n)]
    if kind == "sorted":
        a.sort()
    elif kind == "reversed":
        a.sort(reverse=True)
    return a


def bench(fn, data: list[int]) -> float:
    """Медиана времени выполнения fn(data) по REPEATS запускам, с прогревом."""
    fn(data)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(data)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры quicksort на трёх классах входов; аварийные завершения фиксируются."""
    print("\n== Шаг 4: бенчмарк (прогрев, 5 повторов, медиана) ==")
    rng = random.Random(seed)
    for kind in INPUT_KINDS:
        print(f"\nкласс входа: {kind}")
        prev = None
        for n in SIZES:
            data = make_input(rng, n, kind)
            try:
                t = bench(quicksort, data)
                ratio = f"  (x{t / prev:.2f} к предыдущему)" if prev else ""
                print(f"  n={n:>6}  t={t:.6f} c{ratio}")
                prev = t
            except RecursionError:
                print(f"  n={n:>6}  RecursionError")
                prev = None
    print("\nАнализ: при удвоении n время должно расти в ~2,1–2,3 раза для n log n и в ~4 раза для n^2.")


# ---------------------------------------------------------------------------
# 5. Самопроверка каркаса (граничные случаи + сверка с эталоном stdlib)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Проверяет вспомогательные функции до основной верификации."""
    assert is_sorted([]) and is_sorted([7]) and is_sorted([1, 2, 2, 3])
    assert not is_sorted([3, 1, 2])
    assert same_multiset([], []) and same_multiset([2, 1, 2], [1, 2, 2])
    assert not same_multiset([1, 1, 2], [1, 2, 2])
    rng = random.Random(0)
    for _ in range(100):  # сверка помощников с эталоном стандартной библиотеки
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 30))]
        assert is_sorted(sorted(a))          # эталон sorted() упорядочен
        assert same_multiset(a, sorted(a))   # эталон — перестановка входа
    print("self_check: OK")


def main() -> None:
    global quicksort
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--code", type=Path, default=None, help="проверять другой файл (для повторной верификации)")
    args = ap.parse_args()
    if args.code:
        quicksort = load_quicksort(args.code)
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    rng = random.Random(seed)
    run_representative_tests(rng)
    compare_with_reference(rng, runs=300)
    run_benchmarks(seed)


if __name__ == "__main__":
    main()

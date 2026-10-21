#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: худший и средний случай O(n^2) (n(n-1)/2 сравнений и столько же
    обменов на обратном входе); лучший случай O(n) — упорядоченный вход, один
    проход без обменов и досрочный выход. Память O(1) сверх копии. Стабильна:
    обмен делается только при строгом a[j] > a[j+1].

    Подсказка: досрочный выход, если за проход не было ни одного обмена, —
    именно он даёт лучший случай на упорядоченном входе.
    """
    a = list(a)
    n = len(a)
    comparisons = swaps = 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps



def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Ожидаемая сложность:  худший и средний случай O(n^2) (обратный вход: n(n-1)/2
    сравнений и сдвигов); лучший случай O(n) — на упорядоченном входе каждый
    элемент сравнивается один раз (n-1 сравнений, 0 сдвигов). Сложность
    пропорциональна числу инверсий. Стабильна: сдвиг только при строгом >.
    Счётчик третьего значения — число сдвигов (перемещений элементов).
    """

    a = list(a)
    comparisons = shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    return a, comparisons, shifts



def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: Θ(n^2) на любом входе — поиск минимума в неотсортированной части
    всегда просматривает её целиком, поэтому сравнений ровно n(n-1)/2 независимо
    от порядка данных. Обменов не более n-1 (O(n)). Нестабильна: обмен
    дальнего минимума с a[i] может перепрыгнуть через равные ключи.
    """
    a = list(a)
    n = len(a)
    comparisons = swaps = 0
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            swaps += 1
    return a, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем Θ(n log n) на ЛЮБОМ входе —
    ожидаемое число сравнений E[C(n)] = 2(n+1)H(n) - 4n ≈ 1,39·n·log2 n; в
    худшем случае Θ(n^2): каждое разбиение отрезает O(1) элементов, T(n) =
    T(n-1) + Θ(n). Любая фиксированная пропорция разбиения 1:q даёт Θ(n log n),
    а квадрат возможен лишь при многократном выборе почти крайнего опорного.
    Рандомизация переносит случайность внутрь алгоритма: плохой вход подобрать
    нельзя, неудачными бывают только броски — в отличие от фиксированного
    первого/последнего опорного, который даёт n^2 на упорядоченном и обратном
    входах. Память: стек O(log n) благодаря рекурсии по меньшей части. Трёхстороннее разбиение (<, ==, >)
    делает сортировку устойчивой к большому числу равных ключей. Сама
    сортировка не стабильна. rng передаётся снаружи, чтобы запуск был воспроизводим по
    seed варианта.
    """
    if rng is None:
        rng = random.Random()
    a = list(a)
    stack = [(0, len(a) - 1)]
    while stack:
        lo, hi = stack.pop()
        while hi - lo > 0:
            pivot = a[rng.randrange(lo, hi + 1)]
            lt, i, gt = lo, lo, hi
            while i <= gt:
                x = a[i]
                if x < pivot:
                    a[lt], a[i] = a[i], a[lt]
                    lt += 1
                    i += 1
                elif x > pivot:
                    a[i], a[gt] = a[gt], a[i]
                    gt -= 1
                else:
                    i += 1
            if lt - lo < hi - gt:
                stack.append((gt + 1, hi))
                hi = lt - 1
            else:
                stack.append((lo, lt - 1))
                lo = gt + 1
    return a


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


class _Pair:
    """Пара (ключ, метка): все сравнения идут ТОЛЬКО по ключу.
 
    Сортировки используют лишь <, > и (косвенно) равенство, поэтому достаточно
    переопределить сравнения; метка нужна, чтобы увидеть порядок равных ключей.
    """
 
    __slots__ = ("key", "label")
 
    def __init__(self, key, label):
        self.key, self.label = key, label
 
    def __lt__(self, o): return self.key < o.key
    def __gt__(self, o): return self.key > o.key
    def __le__(self, o): return self.key <= o.key
    def __ge__(self, o): return self.key >= o.key
 
    def __repr__(self):
        return f"({self.key}, {self.label!r})"
 
 
STABLE_FNS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}
 
 
def find_stability_violation(fn, trials: int = 300):
    """Вернуть (вход, выход) с нарушенным порядком равных ключей или None."""
    rng = random.Random(1)
    for _ in range(trials):
        n = rng.randint(3, 12)
        src = [(rng.randint(0, 4), i) for i in range(n)]
        out = fn([_Pair(k, i) for k, i in src])
        got = [(p.key, p.label) for p in out]
        if got != sorted(src, key=lambda t: t[0]):
            return src, got
    return None
 
 
def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.
 
    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    print("\nстабильность (сравнение только по ключу, слайд 5 лекции):")
    pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    print(f"  вход: {pairs}")
    for name, fn in STABLE_FNS.items():
        res = [(p.key, p.label) for p in fn([_Pair(k, s) for k, s in pairs])]
        order = {k: "".join(s for kk, s in res if kk == k) for k, _ in pairs}
        print(f"  {name:<15} -> {res}  метки при ключе 1: {order[1]}, при ключе 2: {order[2]}")
    print("  итог по 300 случайным массивам (ключи 0..4, метка = исходный номер):")
    for name, fn in STABLE_FNS.items():
        bad = find_stability_violation(fn)
        if bad is None:
            print(f"    {name:<15} СТАБИЛЬНА (нарушений не найдено)")
        else:
            print(f"    {name:<15} НЕ стабильна, контрпример: вход {bad[0]} -> выход {bad[1]}")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}
 
 
def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))
 
 
class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""
 
 
def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)
 
 
def check_algorithm(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: получено {res}")
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
 
    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")
 
 
def check_counters() -> None:
    """Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе."""
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10,
           f"selection_sort: неверный счётчик сравнений — {comparisons}, ожидалось 10")
 
 
def count_inversions(a: list) -> int:
    """Число инверсий (пар i<j, a[i]>a[j]) прямым перебором; для малых n."""
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])
 
 
def check_counters_simple() -> None:
    """Счётчики пузырька и вставок против формул лекции (слайды 6–9, разбор Р2)."""
    n = 5
    asc, desc = list(range(n)), list(range(n, 0, -1))
    full = n * (n - 1) // 2
    expect(bubble_sort(asc)[1:] == (n - 1, 0), f"пузырёк, упорядоченный: {bubble_sort(asc)[1:]}")
    expect(bubble_sort(desc)[1:] == (full, full), f"пузырёк, обратный: {bubble_sort(desc)[1:]}")
    expect(insertion_sort(asc)[1:] == (n - 1, 0), f"вставки, упорядоченный: {insertion_sort(asc)[1:]}")
    expect(insertion_sort(desc)[1:] == (full, full), f"вставки, обратный: {insertion_sort(desc)[1:]}")
    expect(selection_sort(asc)[1:] == (full, 0), f"выбор, упорядоченный: {selection_sort(asc)[1:]}")
    # Малый пример из лекции (разбор Р2): [5, 2, 4, 6, 1, 3], 9 инверсий.
    x = [5, 2, 4, 6, 1, 3]
    expect(insertion_sort(x)[1:] == (12, 9), f"вставки на примере Р2: {insertion_sort(x)[1:]}")
    expect(bubble_sort(x)[1:] == (15, 9), f"пузырёк на примере Р2: {bubble_sort(x)[1:]}")
    expect(selection_sort(x)[1:] == (15, 3), f"выбор на примере Р2: {selection_sort(x)[1:]}")
    # Ключевой факт слайда 4: обменов (сдвигов) ровно столько, сколько инверсий.
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 6) for _ in range(rng.randint(0, 30))]
        inv = count_inversions(a)
        expect(bubble_sort(a)[2] == inv, f"обменов пузырька != инверсий на {a}")
        expect(insertion_sort(a)[2] == inv, f"сдвигов вставок != инверсий на {a}")
        expect(selection_sort(a)[1] == len(a) * (len(a) - 1) // 2,
               f"сравнений выбора != n(n-1)/2 на {a}")
 
 
def check_input_not_mutated() -> None:
    """Контракт: сортировки работают с копией и не меняют вход."""
    for name, fn in ALGORITHMS.items():
        a = [3, 1, 2, 3, 0]
        fn(a)
        expect(a == [3, 1, 2, 3, 0], f"{name} изменил входной список: {a}")
 
 
def check_stability() -> None:
    """Пузырёк и вставки обязаны быть стабильными; выбор — нет (пример слайда 5)."""
    for name in ("bubble_sort", "insertion_sort"):
        bad = find_stability_violation(STABLE_FNS[name])
        expect(bad is None, f"{name} нарушил стабильность: {bad}")
    res = [(p.key, p.label) for p in STABLE_FNS["selection_sort"](
        [_Pair(k, s) for k, s in [(2, "a"), (1, "b"), (2, "c"), (1, "d")]])]
    expect(res == [(1, "b"), (1, "d"), (2, "c"), (2, "a")],
           f"выбор на примере слайда 5 даёт {res}, в лекции (2,c) перед (2,a)")
 
 
def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_algorithm(fn)) for name, fn in ALGORITHMS.items()]
    checks.append(("счётчики", check_counters))
    checks.append(("счётчики пузырька/вставок", check_counters_simple))
    checks.append(("вход не изменяется", check_input_not_mutated))
    checks.append(("стабильность", check_stability))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))
    times = []
    for _ in range(REPEATS):
        arg = list(data)
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)
 
 
def counters_table(seed: int, n: int = 1000) -> list[str]:
    """Таблица счётчиков (сравнений / обменов-сдвигов) на трёх классах входов."""
    lines = [f"Счётчики операций, n = {n}, seed = {seed} (сравнений / обменов; у вставок — сдвигов)", "",
             "| вход | инверсий | пузырёк | вставки | выбор |", "|---|---|---|---|---|"]
    for cls, data in make_inputs(n, seed).items():
        cells = []
        for fn in (bubble_sort, insertion_sort, selection_sort):
            _, c, w = fn(data)
            cells.append(f"{c:,} / {w:,}".replace(",", " "))
        lines.append(f"| {cls} | {count_inversions(data):,} | ".replace(",", " ") + " | ".join(cells) + " |")
    return lines
 
 
def loglog_slope(sizes: list[int], times: list[float]) -> float:
    """Наклон прямой в log-log осях (МНК): t ≈ c * n^k  =>  k = наклон."""
    xs, ys = [math.log(n) for n in sizes], [math.log(t) for t in times]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
 
 
def plot_results(results: dict, path: str) -> None:
    """Log-log графики: по панели на алгоритм, по линии на класс входа."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
 
    style = {"упорядоченный": ("#1b7f5c", "o", "-"),
             "случайный": ("#222222", "s", "-"),
             "обратный": ("#c0561a", "^", "-")}
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, (name, per_cls) in zip(axes.flat, results.items()):
        for cls, series in per_cls.items():
            color, marker, ls = style[cls]
            ns = sorted(series)
            ax.loglog(ns, [series[n] for n in ns], marker=marker, ls=ls, color=color,
                      label=f"{cls} (наклон {loglog_slope(ns, [series[n] for n in ns]):.2f})")
        ns = sorted(per_cls["случайный"])
        n0, t0 = ns[0], per_cls["случайный"][ns[0]]
        ax.loglog(ns, [t0 * (n / n0) ** 2 for n in ns], ":", color="#888888", label="O(n²)")
        ax.loglog(ns, [t0 * (n * math.log(n)) / (n0 * math.log(n0)) for n in ns],
                  "--", color="#888888", label="O(n log n)")
        ax.set_title(name)
        ax.set_xlabel("размер входа n")
        ax.set_ylabel("время, с (медиана)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("ЛР 3: время сортировки, логарифмические шкалы")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
 
 
def run_benchmarks(seed: int, plot_path: str = "lab03_plots.png",
                   report_path: str = "lab03_results.md") -> None:
    """Замеры всех алгоритмов на трёх классах входов: таблицы, наклоны и график."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    report: list[str] = counters_table(seed)
    print("\n" + "\n".join(report))
 
    results: dict[str, dict[str, dict[int, float]]] = {}
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        results[name] = {cls: {} for cls in ("упорядоченный", "случайный", "обратный")}
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                results[name][cls][n] = t
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")
 
    report += ["", "Время, с (медиана 5 запусков); наклон — МНК по всем размерам в log-log", ""]
    for name, per_cls in results.items():
        ns = sorted(per_cls["случайный"])
        report += [f"{name}", "", "| n | " + " | ".join(per_cls) + " |", "|---|" + "---|" * len(per_cls)]
        for n in ns:
            report.append(f"| {n} | " + " | ".join(f"{per_cls[c][n]:.6f}" for c in per_cls) + " |")
        slopes = " | ".join(f"{loglog_slope(ns, [per_cls[c][n] for n in ns]):.2f}" for c in per_cls)
        report += [f"| **наклон** | {slopes} |", ""]
    text = "\n".join(report)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    plot_results(results, plot_path)
    print(f"\nтаблицы сохранены в {report_path}, графики — в {plot_path}")
 
 
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)
 
 
if __name__ == "__main__":
    main()
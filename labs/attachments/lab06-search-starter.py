#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 6. Линейный, бинарный и интерполяционный поиск — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-06 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Каждая функция поиска работает с отсортированным по неубыванию массивом
и возвращает пару (индекс найденного элемента или -1, число сравнений ключей).

Запуск: python lab06-search-starter.py --variant N
"""
from __future__ import annotations

import argparse
import bisect
import csv
import random
import statistics
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Алгоритмы поиска (реализуются вручную, без in/index/bisect в основной части)
# ---------------------------------------------------------------------------


def linear_search(a: list[int], key: int) -> tuple[int, int]:
    """Линейный поиск первого вхождения key.

    Возвращает (индекс первого вхождения или -1, число сравнений ключей).
    Сложность: O(n) в худшем и среднем случае (ключ отсутствует — ровно
    n сравнений; присутствует в случайной позиции — в среднем ~n/2).
    Сортированность не используется (досрочный выход по a[i] > key
    сознательно не делается, чтобы получить «классический» линейный поиск).
    """
    comparisons = 0
    for i, value in enumerate(a):
        comparisons += 1
        if value == key:
            return i, comparisons
    return -1, comparisons


def binary_search(a: list[int], key: int) -> tuple[int, int]:
    """Бинарный поиск key в отсортированном массиве.

    Инвариант (замкнутый отрезок [lo, hi]): если key есть в массиве,
    то он находится среди a[lo..hi]. Все элементы левее lo меньше key,
    все элементы правее hi больше key.
    Каждая итерация либо возвращает ответ, либо строго уменьшает длину
    отрезка hi - lo + 1 (mid исключается: lo = mid + 1 или hi = mid - 1),
    поэтому цикл гарантированно завершается.
    Сложность: O(log n) — не более floor(log2 n) + 1 итераций,
    на итерацию до 2 сравнений ключей.
    """
    lo, hi = 0, len(a) - 1
    comparisons = 0
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        comparisons += 1
        if a[mid] == key:
            return mid, comparisons
        comparisons += 1
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comparisons


def interpolation_search(a: list[int], key: int) -> tuple[int, int]:
    """Интерполяционный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений ключей).
    Позиция зонда: mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo]).
    Защиты:
      * key вне [a[lo], a[hi]] — сразу -1 (иначе mid вышел бы за отрезок);
      * a[hi] == a[lo] — деление на ноль; тогда весь отрезок состоит из
        одинаковых значений и ответ определяется одним сравнением.
    При a[lo] <= key <= a[hi] формула даёт lo <= mid <= hi, отрезок
    после зонда строго сужается, цикл завершается.
    Сложность: в среднем O(log log n) на равномерных данных,
    в худшем случае O(n) (сильно неравномерные данные).
    """
    lo, hi = 0, len(a) - 1
    comparisons = 0
    while lo <= hi:
        comparisons += 2
        if key < a[lo] or key > a[hi]:
            return -1, comparisons
        if a[hi] == a[lo]:
            return lo, comparisons
        mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo])
        comparisons += 1
        if a[mid] == key:
            return mid, comparisons
        comparisons += 1
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comparisons


def interpolation_binary_search(a: list[int], key: int) -> tuple[int, int]:
    """Защищённый вариант: чередование интерполяционного и бинарного зонда.

    Нечётные шаги — зонд по формуле интерполяции, чётные — середина отрезка.
    Бинарные шаги гарантируют уменьшение отрезка вдвое хотя бы через шаг,
    т.е. худший случай O(log n), а на равномерных данных интерполяционные
    шаги по-прежнему быстро «попадают» в ключ. Ответ на вопрос 4 защиты.
    """
    lo, hi = 0, len(a) - 1
    comparisons = 0
    use_interp = True
    while lo <= hi:
        comparisons += 2
        if key < a[lo] or key > a[hi]:
            return -1, comparisons
        if a[hi] == a[lo]:
            return lo, comparisons
        if use_interp:
            mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo])
        else:
            mid = lo + (hi - lo) // 2
        use_interp = not use_interp
        comparisons += 1
        if a[mid] == key:
            return mid, comparisons
        comparisons += 1
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comparisons


# ---------------------------------------------------------------------------
# 2. Данные по варианту: два распределения, присутствующие/отсутствующие ключи
# ---------------------------------------------------------------------------


def make_dataset(n: int, distribution: str, rng: random.Random) -> list[int]:
    """Отсортированный массив n ключей: 'uniform' — равномерное распределение,
    'exponential' — неравномерное (экспоненциальное, значения сгущаются у нуля)."""
    if distribution == "uniform":
        return sorted(rng.randint(0, 10 * n) for _ in range(n))
    if distribution == "exponential":
        return sorted(int(rng.expovariate(1.0 / 1000.0)) for _ in range(n))
    raise ValueError(f"неизвестное распределение: {distribution!r}")


def make_adversarial(n: int) -> list[int]:
    """Худший случай интерполяционного поиска: почти все значения малы,
    последний элемент — огромный выброс. Зонд всё время попадает в lo."""
    return list(range(n - 1)) + [10**12]


def pick_keys(a: list[int], rng: random.Random, count: int,
              present: bool) -> list[int]:
    """count ключей для серии поисков: присутствующие берутся из массива,
    отсутствующие подбираются вне множества его значений."""
    if present:
        return [a[rng.randrange(len(a))] for _ in range(count)]
    have = set(a)
    hi = (a[-1] if a else 0) + 2
    keys: list[int] = []
    while len(keys) < count:
        k = rng.randint(-hi, hi)
        if k not in have:
            keys.append(k)
    return keys


# ---------------------------------------------------------------------------
# 3. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------

ALGORITHMS = [
    ("linear", linear_search),
    ("binary", binary_search),
    ("interpolation", interpolation_search),
    ("interp+binary", interpolation_binary_search),
]


def self_check() -> None:
    """Граничные случаи + сверка с эталоном (оператор in, list.index, bisect)."""
    for name, fn in ALGORITHMS:
        # Пустой массив: элемент не найден, сравнений нет.
        assert fn([], 1) == (-1, 0), f"{name}: пустой массив"
        # Один элемент: найден / не найден.
        assert fn([7], 7)[0] == 0, f"{name}: один элемент, ключ найден"
        assert fn([7], 3)[0] == -1, f"{name}: один элемент, ключ отсутствует"
        # Первый, последний и отсутствующие ключи (внутри и вне диапазона).
        a = [1, 3, 3, 5, 8, 13, 21]
        assert fn(a, 1)[0] == 0, f"{name}: первый элемент"
        assert fn(a, 21)[0] == len(a) - 1, f"{name}: последний элемент"
        assert fn(a, 4)[0] == -1, f"{name}: отсутствующий ключ внутри диапазона"
        assert fn(a, 100)[0] == -1, f"{name}: ключ вне диапазона (справа)"
        assert fn(a, -5)[0] == -1, f"{name}: ключ вне диапазона (слева)"
        # Все элементы равны — проверка защиты от деления на ноль.
        assert fn([4] * 10, 4)[0] != -1, f"{name}: все равны, ключ есть"
        assert fn([4] * 10, 5)[0] == -1, f"{name}: все равны, ключа нет"
        # Выброс — худший случай интерполяции должен оставаться корректным.
        adv = make_adversarial(500)
        assert fn(adv, 498)[0] == 498, f"{name}: массив с выбросом"
        assert fn(adv, 10**12)[0] == 499, f"{name}: выброс — последний"

    # Сверка с эталоном стандартной библиотеки на случайных массивах.
    rng = random.Random(0)
    checks = 0
    for _ in range(3000):
        a = sorted(rng.randint(0, 60) for _ in range(rng.randint(1, 40)))
        key = rng.randint(-5, 65)
        # Эталон присутствия ключа — bisect_left (и, эквивалентно, оператор in).
        j = bisect.bisect_left(a, key)
        present = j < len(a) and a[j] == key
        assert present == (key in a)
        for name, fn in ALGORITHMS:
            idx, cmp_count = fn(a, key)
            checks += 1
            assert cmp_count >= 1, f"{name}: счётчик сравнений не ведётся"
            if present:
                # При дубликатах бинарный/интерполяционный могут вернуть
                # любое вхождение — проверяем значение по индексу.
                assert idx != -1 and a[idx] == key, f"{name}: ключ не найден"
            else:
                assert idx == -1, f"{name}: найден отсутствующий ключ"
        # Линейный поиск обязан возвращать первое вхождение — эталон list.index.
        if present:
            assert linear_search(a, key)[0] == a.index(key)

    # Оценка сверху для бинарного поиска: <= 2 * (floor(log2 n) + 1) сравнений.
    for n in (1, 2, 3, 7, 8, 100, 1000, 4096):
        a = list(range(0, 2 * n, 2))
        for key in range(-1, 2 * n + 1):
            assert binary_search(a, key)[1] <= 2 * n.bit_length()
    print(f"self_check: OK ({checks} сверок с эталоном + граничные случаи)")


# ---------------------------------------------------------------------------
# 4. Бенчмарк: сравнения и время от n (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5      # число повторов серии замеров (берётся медиана)
N_KEYS = 200     # число ключей в одной серии поисков


def bench(fn, a: list[int], keys: list[int]) -> float:
    """Медиана времени одной серии поисков по REPEATS запускам, с прогревом."""
    for k in keys:  # прогрев — не учитывается
        fn(a, k)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        for k in keys:
            fn(a, k)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def mean_comparisons(fn, a: list[int], keys: list[int]) -> float:
    """Среднее число сравнений ключей на один поиск."""
    return statistics.mean(fn(a, k)[1] for k in keys)


def run_benchmarks(seed: int, linear_max_n: int = 100_000) -> list[dict]:
    """Замеры по всем распределениям, размерам и типам ключей."""
    rng = random.Random(seed)
    rows: list[dict] = []
    for distribution in ("uniform", "exponential"):
        print(f"\nРаспределение: {distribution}")
        for n in SIZES:
            a = make_dataset(n, distribution, rng)
            for present in (True, False):
                keys = pick_keys(a, rng, N_KEYS, present)
                label = "есть" if present else "нет"
                for name, fn in ALGORITHMS:
                    if name == "linear" and n > linear_max_n:
                        continue
                    cmp_mean = mean_comparisons(fn, a, keys)
                    t_series = bench(fn, a, keys)
                    t_one = t_series / len(keys)
                    rows.append(
                        {
                            "distribution": distribution,
                            "n": n,
                            "present": present,
                            "algorithm": name,
                            "comparisons": cmp_mean,
                            "time_s": t_one,
                        }
                    )
                    print(
                        f"  n={n:>7}  ключ {label:<4}  {name:<13}"
                        f"  сравнений={cmp_mean:>10.1f}"
                        f"  t={t_one * 1e6:>10.2f} мкс/поиск"
                    )
    return rows

def run_adversarial(seed: int) -> list[dict]:
    """Демонстрация деградации интерполяционного поиска к O(n)."""
    rng = random.Random(seed)
    rows: list[dict] = []
    print("\nДеградация: массив 0..n-2 + выброс 10^12 (ключи присутствуют)")
    for n in SIZES:
        a = make_adversarial(n)
        keys = pick_keys(a[:-1], rng, N_KEYS, True)
        for name, fn in ALGORITHMS[1:]:
            cmp_mean = mean_comparisons(fn, a, keys)
            rows.append(
                {
                    "distribution": "adversarial",
                    "n": n,
                    "present": True,
                    "algorithm": name,
                    "comparisons": cmp_mean,
                    "time_s": float("nan"),
                }
            )
            print(f"  n={n:>7}  {name:<13}  сравнений={cmp_mean:>10.1f}")
    return rows

def save_csv(rows: list[dict], path: Path) -> None:
    """Сохраняет сырые результаты замеров."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


COLORS = {
    "linear": "#7f7f7f",
    "binary": "#1f77b4",
    "interpolation": "#d62728",
    "interp+binary": "#2ca02c",
}


def plot_results(rows: list[dict], outdir: Path) -> list[Path]:
    """Графики «сравнения от n» и «время от n» для каждого распределения."""
    import matplotlib  # pylint: disable=import-outside-toplevel

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel

    paths = []
    metrics = [
        ("comparisons", "Среднее число сравнений"),
        ("time_s", "Время одного поиска, мкс"),
    ]
    for dist in ("uniform", "exponential"):
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        for col, present in enumerate((True, False)):
            for row, (metric, ylabel) in enumerate(metrics):
                ax = axes[row][col]
                for name, _ in ALGORITHMS:
                    pts = [
                        r
                        for r in rows
                        if r["distribution"] == dist
                        and r["present"] == present
                        and r["algorithm"] == name
                    ]
                    if not pts:
                        continue
                    xs = [r["n"] for r in pts]
                    ys = [r[metric] * (1e6 if metric == "time_s" else 1) for r in pts]
                    ax.plot(xs, ys, "o-", label=name, color=COLORS[name])
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.set_xlabel("n")
                ax.set_ylabel(ylabel)
                ax.set_title(f"ключ {'присутствует' if present else 'отсутствует'}")
                ax.grid(True, which="both", alpha=0.3)
                ax.legend(fontsize=8)
        fig.suptitle(f"Распределение: {dist}")
        fig.tight_layout()
        p = outdir / f"plot_{dist}.png"
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths.append(p)

    # Деградация
    adv = [r for r in rows if r["distribution"] == "adversarial"]
    if adv:
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        for name, _ in ALGORITHMS[1:]:
            pts = [r for r in adv if r["algorithm"] == name]
            ax.plot(
                [r["n"] for r in pts],
                [r["comparisons"] for r in pts],
                "o-",
                label=name,
                color=COLORS[name],
            )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("n")
        ax.set_ylabel("Среднее число сравнений")
        ax.set_title("Худший случай: 0..n-2 + выброс 10^12")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        p = outdir / "plot_adversarial.png"
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths.append(p)
    return paths

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument(
        "--out", type=Path, default=Path("results"), help="каталог для CSV и графиков"
    )
    ap.add_argument("--no-plots", action="store_true", help="не строить графики")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    print(f"Вариант {args.variant}, seed = {seed}")
    self_check()
    rows = run_benchmarks(seed) + run_adversarial(seed)
    args.out.mkdir(parents=True, exist_ok=True)
    save_csv(rows, args.out / "results.csv")
    if not args.no_plots:
        for p in plot_results(rows, args.out):
            print(f"график: {p}")


if __name__ == "__main__":
    main()

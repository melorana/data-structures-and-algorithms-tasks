#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.
 
    Стабильность: при равенстве ключей элемент из left идёт раньше.
    Сложность: Θ(p + q) по времени (каждый элемент переносится один раз,
    не более p + q - 1 сравнений) и Θ(p + q) по памяти (результат).
    """
    out = []
    i = j = 0
    nl, nr = len(left), len(right)
    while i < nl and j < nr:
        if key(left[i]) <= key(right[j]):  # <=, а не <: при равенстве берём из left
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])   # остаток одного из списков копируется без сравнений
    out.extend(right[j:])
    return out
 
 
def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список.
 
    Сложность: T(n) = 2T(n/2) + Θ(n) = Θ(n log n) на любом входе;
    дополнительная память Θ(n); стабилен.
    """
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    return merge(merge_sort(a[:mid], key), merge_sort(a[mid:], key), key)
 
 
def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max].
 
    Схема: массив счётчиков -> префиксные суммы -> расстановка с конца.
    Время Θ(n + k), память Θ(n + k), где k = key_max + 1 (счётчики + результат).
    Линейна только при k = O(n). Если k >> n (например, 10^9 при n = 1000),
    время и память определяются массивом счётчиков (в Python около 7,5 ГиБ
    при k = 10^9) — алгоритм теряет смысл. Для диапазона [min, max] ключ
    сдвигают на min, тогда k = max - min + 1.
    """
    if not a:
        return []
    count = [0] * (key_max + 1)
    for x in a:
        count[x] += 1
    for v in range(1, key_max + 1):      # префиксные суммы: count[v] = число элементов <= v
        count[v] += count[v - 1]
    out = [0] * len(a)
    for x in reversed(a):                # с конца — иначе теряется устойчивость
        count[x] -= 1
        out[count[x]] = x
    return out
 
 
def _digit_pass(a: list[int], exp: int, stable: bool = True) -> list[int]:
    """Один проход по десятичной цифре (x // exp) % 10 (counting-сортировка, k = 10).
 
    stable=False — учебный НЕустойчивый вариант (обход с начала), нужен только
    для демонстрации, почему устойчивость прохода обязательна.
    """
    count = [0] * 10
    for x in a:
        count[(x // exp) % 10] += 1
    for d in range(1, 10):
        count[d] += count[d - 1]
    out = [0] * len(a)
    it = reversed(a) if stable else iter(a)
    for x in it:
        d = (x // exp) % 10
        count[d] -= 1
        out[count[d]] = x
    return out
 
 
def radix_sort_lsd(a: list[int], _stable: bool = True) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.
 
    Поверх устойчивой поразрядной counting-сортировки: от младшего разряда
    к старшему. Время Θ(d·(n + b)), b = 10, d — число разрядов максимума;
    память Θ(n + b).
 
    Почему нужна устойчивость: инвариант LSD — после прохода по разряду j
    числа упорядочены по младшим j + 1 разрядам. Проход по следующему разряду
    обязан сохранить этот порядок у чисел с равной цифрой; неустойчивый проход
    его ломает (21, 12, 22, 11 -> 11, 12, 21, 22 при устойчивом проходе
    и 12, 11, 22, 21 при неустойчивом).
    """
    if not a:
        return []
    m = max(a)
    out = list(a)
    exp = 1
    while m // exp > 0:
        out = _digit_pass(out, exp, _stable)
        exp *= 10
    return out
 
 
def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        big = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and a[l] > a[big]:
            big = l
        if r < n and a[r] > a[big]:
            big = r
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big
 
 
def build_heap(a: list[int]) -> None:
    """Построение max-кучи на месте: просейка от последнего внутреннего узла к корню, O(n)."""
    for i in range(len(a) // 2 - 1, -1, -1):
        sift_down(a, i, len(a))
 
 
def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте, без вспомогательного массива.
 
    Построение max-кучи просейками снизу вверх — O(n) (большинство узлов
    лежит у листьев и опускается на 1–2 уровня); затем n - 1 раз: обмен корня
    с последним элементом кучи и просейка — O(n log n).
    Итого Θ(n log n) в худшем случае, память O(1), нестабильна.
    """
    build_heap(a)
    for end in range(len(a) - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def quick_sort(a: list[int], rng: random.Random | None = None) -> list[int]:
    """QuickSort с рандомизацией опорного элемента — перенести из своей ЛР 3."""
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
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""
 
 
def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)
 
 
def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf
 
 
# Каждая функция возвращает отсортированный список; ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}
 
 
def check_sort(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [0],                   # нулевой ключ
        [5, 5, 5],             # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")
 
    # Случайные тесты: инвариант перестановки + сверка с эталоном
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")
 
 
def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, порядковый номер): эталон sorted() стабилен,
    поэтому при равных ключах порядок номеров обязан совпасть."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")
    # пример из лекции (разбор Р1): слияние с <= сохраняет порядок b, c, d
    got = merge([(1, "a"), (2, "b"), (2, "c")], [(2, "d"), (3, "e")], key=lambda p: p[0])
    expect(got == [(1, "a"), (2, "b"), (2, "c"), (2, "d"), (3, "e")],
           f"слияние нарушает порядок равных ключей: {got}")
 
 
def check_merge_inputs_untouched() -> None:
    """merge_sort возвращает НОВЫЙ список и не меняет вход."""
    a = [5, 3, 9, 1, 3]
    copy = list(a)
    res = merge_sort(a)
    expect(a == copy, "merge_sort изменил входной список")
    expect(res is not a, "merge_sort вернул тот же объект, а не новый список")
 
 
def check_counting_stability() -> None:
    """Устойчивость counting-схемы на записях (ключ, метка) — пример из лекции.
 
    counting_sort работает с целыми, поэтому устойчивость проверяется через
    сортировку индексов: ключи кодируются как key*N + номер, а затем
    сортируются только по ключу тем же алгоритмом (counting по key)."""
    rng = random.Random(1)
    n = 200
    keys = [rng.randint(0, 9) for _ in range(n)]
    # Сортируем индексы по ключу: используем counting_sort на закодированных значениях
    # key*n + i. Порядок равных ключей определяется i, а устойчивый counting
    # по старшей части ключа обязан сохранять порядок входа.
    encoded = [k * n + i for i, k in enumerate(keys)]
    expect(counting_sort(encoded, key_max=9 * n + n - 1) == sorted(encoded),
           "counting_sort неверно сортирует закодированные пары")
    # Прямая проверка устойчивости схемы: записи (ключ, метка), сортировка по ключу
    items = [(2, "a"), (0, "b"), (3, "c"), (2, "d"), (0, "e"), (1, "f")]
    count = [0] * 4
    for k, _ in items:
        count[k] += 1
    for v in range(1, 4):
        count[v] += count[v - 1]
    out = [None] * len(items)
    for item in reversed(items):
        count[item[0]] -= 1
        out[count[item[0]]] = item
    expect(out == [(0, "b"), (0, "e"), (1, "f"), (2, "a"), (2, "d"), (3, "c")],
           f"схема подсчёта с обходом с конца нестабильна: {out}")
 
 
def check_radix_stable_pass() -> None:
    """Устойчивость прохода radix обязательна: устойчивый проход даёт верный результат,
    неустойчивый — нет (пример из лекции: 21, 12, 22, 11)."""
    expect(radix_sort_lsd([21, 12, 22, 11]) == [11, 12, 21, 22],
           "radix_sort_lsd с устойчивым проходом дал неверный результат")
    expect(radix_sort_lsd([21, 12, 22, 11], _stable=False) != [11, 12, 21, 22],
           "неустойчивый проход почему-то дал верный результат — демонстрация не работает")
    # большие значения и разное число разрядов
    rng = random.Random(2)
    for _ in range(50):
        a = [rng.randint(0, 10**9) for _ in range(rng.randint(0, 200))]
        expect(radix_sort_lsd(a) == sorted(a), f"radix_sort_lsd неверен на {a[:5]}...")
 
 
def check_heap_property() -> None:
    """Свойство max-кучи после построения: a[parent(i)] >= a[i] для всех i > 0;
    построение — на месте (длина и содержимое как мультимножество сохраняются)."""
    rng = random.Random(3)
    for _ in range(100):
        a = [rng.randint(0, 99) for _ in range(rng.randint(0, 80))]
        before = sorted(a)
        build_heap(a)
        expect(sorted(a) == before, "построение кучи изменило набор элементов")
        for i in range(1, len(a)):
            expect(a[(i - 1) // 2] >= a[i],
                   f"нарушено свойство кучи в позиции {i}: родитель {a[(i - 1) // 2]} < {a[i]}")
    # пример из лекции (разбор Р7): [4, 10, 3, 5, 1, 8, 9] -> [10, 5, 9, 4, 1, 8, 3]
    lec = [4, 10, 3, 5, 1, 8, 9]
    build_heap(lec)
    expect(lec == [10, 5, 9, 4, 1, 8, 3], f"построение кучи расходится с лекцией: {lec}")
 
 
def check_heap_in_place() -> None:
    """heap_sort сортирует на месте: тот же объект списка, возвращаемое значение None."""
    a = [3, 1, 2]
    ident = id(a)
    res = heap_sort(a)
    expect(res is None, "heap_sort должен сортировать на месте и ничего не возвращать")
    expect(id(a) == ident and a == [1, 2, 3], "heap_sort не отсортировал переданный список")
 
 
def check_heap_unstable_demo() -> None:
    """Демонстрация нестабильности HeapSort (пример из лекции): метки a и b меняются местами.
 
    heap_sort сортирует сами числа, поэтому нестабильность показываем на копии
    алгоритма, сравнивающей записи по ключу."""
    arr = [(2, "a"), (2, "b"), (1, "c")]
 
    def sd(i: int, n: int) -> None:
        while True:
            big, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n and arr[l][0] > arr[big][0]:
                big = l
            if r < n and arr[r][0] > arr[big][0]:
                big = r
            if big == i:
                return
            arr[i], arr[big] = arr[big], arr[i]
            i = big
 
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        sd(i, n)
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        sd(0, end)
    expect(arr == [(1, "c"), (2, "b"), (2, "a")],
           f"ожидался результат из лекции [(1,c),(2,b),(2,a)], получено {arr}")
 
 
def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks += [
        ("стабильность merge_sort", check_merge_stability),
        ("merge_sort не меняет вход", check_merge_inputs_untouched),
        ("устойчивость counting_sort", check_counting_stability),
        ("устойчивый проход radix", check_radix_stable_pass),
        ("свойство кучи после построения", check_heap_property),
        ("heap_sort in-place", check_heap_in_place),
        ("нестабильность heap_sort (демо)", check_heap_unstable_demo),
    ]
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
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл
 
 
def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }
 
 
def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.
 
    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)
 
 
def print_properties_table() -> None:
    """Сводная таблица свойств шести сортировок (лекция, слайд 23)."""
    rows = [
        ("Алгоритм", "Лучший", "Средний", "Худший", "Память", "Стаб.", "Ограничения"),
        ("MergeSort", "Θ(n log n)", "Θ(n log n)", "Θ(n log n)", "Θ(n)", "да",
         "нужна доп. память; не адаптивен"),
        ("CountingSort", "Θ(n+k)", "Θ(n+k)", "Θ(n+k)", "Θ(n+k)", "да",
         "целые ключи из [0,k-1], k=O(n)"),
        ("RadixSort LSD", "Θ(d(n+b))", "Θ(d(n+b))", "Θ(d(n+b))", "Θ(n+b)", "да",
         "целые/фикс. длина; нужен устойч. проход"),
        ("HeapSort", "Θ(n log n)", "Θ(n log n)", "Θ(n log n)", "O(1)", "нет",
         "плохая работа с кэшем"),
        ("QuickSort (случ.)", "Θ(n log n)", "Θ(n log n)", "Θ(n²)", "O(log n)", "нет",
         "худший случай маловероятен"),
        ("sorted() Timsort", "Θ(n)", "Θ(n log n)", "Θ(n log n)", "O(n)", "да",
         "сравнение через функцию/ключ"),
    ]
    widths = [max(len(r[c]) for r in rows) for c in range(len(rows[0]))]
    print("\nСводная таблица свойств:")
    for idx, r in enumerate(rows):
        print("  " + " | ".join(r[c].ljust(widths[c]) for c in range(len(r))))
        if idx == 0:
            print("  " + "-+-".join("-" * w for w in widths))
 
 
def plot_results(results: dict, sizes: list[int]) -> None:
    """log-log графики времени от n — по одному на распределение."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — графики пропущены")
        return
    for dist, algos in results.items():
        plt.figure(figsize=(7, 5))
        for name, ts in algos.items():
            xs = [n for n, t in zip(sizes, ts) if t is not None]
            ys = [t for t in ts if t is not None]
            if ys:
                plt.loglog(xs, ys, marker="o", label=name)
        plt.xlabel("n")
        plt.ylabel("время, с")
        plt.title(f"Распределение: {dist}")
        plt.grid(True, which="both", alpha=0.3)
        plt.legend()
        plt.tight_layout()
        fname = f"lab04_{dist}.png"
        plt.savefig(fname, dpi=130)
        plt.close()
        print(f"график сохранён: {fname}")
 
 
def counting_range_demo(rng: random.Random) -> None:
    """Зависимость counting_sort от k при фиксированном n (для отчёта)."""
    n = 1000
    print(f"\nCountingSort: n = {n}, влияние диапазона k")
    for key_max in (10**3, 10**5, 10**6, 10**7):
        data = [rng.randint(0, key_max) for _ in range(n)]
        t = bench(lambda a, km=key_max: counting_sort(a, km), data)
        print(f"  k = {key_max + 1:>10}: t = {t:.6f} c")
 
 
def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort (ЛР 3)", quick_sort),
        ("sorted() (эталон)", sorted),
    ]
    results: dict[str, dict[str, list]] = {}
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                slot = results.setdefault(dist_name, {}).setdefault(algo_name, [])
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    # счётчики размера ~10^9 не помещаются в память — граница
                    # применимости counting
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    slot.append(None)
                    continue
                t = bench(fn, data)
                slot.append(t)
                print(f"    {algo_name:>18}: t = {t:.6f} c")
    plot_results(results, SIZES)
    counting_range_demo(rng)
    print_properties_table()
    print(
        "\nКомментарий к расхождениям с асимптотикой: sorted() (Timsort на C) быстрее\n"
        "реализаций на чистом Python на порядки; HeapSort самый медленный из-за\n"
        "большого числа сравнений (~в 2 раза больше, чем у MergeSort) и плохой локальности\n"
        "обращений 2i+1/2i+2; MergeSort на упорядоченном входе быстрее (остатки копируются\n"
        "без сравнений), но не адаптивен; counting/radix быстрее сортировок сравнением\n"
        "при малых k/d, а при k ≫ n counting теряет смысл; QuickSort с трёхсторонним\n"
        "разбиением быстр на узком диапазоне ключей (много дубликатов)."
    )
 
 
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)
 
 
if __name__ == "__main__":
    main()

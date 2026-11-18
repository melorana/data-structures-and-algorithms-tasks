#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 2. Эксперимент: высота BST и деградация операций — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-02 (Cases) и правилами использования генеративного ИИ
(docs/ai-verification.md). Класс BST из ЛР 5 рекомендуется подключить как
модуль; ниже дан минимальный узел и сигнатуры на случай автономного запуска.

Запуск: python dz02-bst-height-starter.py --variant N
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import time
from collections import deque

# ---------------------------------------------------------------------------
# 1. Узел и итеративная вставка
#    Внимание: на упорядоченном потоке дерево вырождается в список глубиной
#    до 10^4, поэтому вставка и обходы должны быть итеративными —
#    рекурсивные варианты вызовут RecursionError.
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


def insert_iter(root: Node | None, key: int) -> Node:
    """Итеративная вставка ключа в BST; возвращает корень. Дубликаты игнорируются."""
    new = Node(key)
    if root is None:
        return new
    node = root
    while True:
        if key < node.key:
            if node.left is None:
                node.left = new
                return root
            node = node.left
        elif key > node.key:
            if node.right is None:
                node.right = new
                return root
            node = node.right
        else:
            return root


def build_bst(keys: list[int]) -> Node | None:
    """Строит BST последовательной итеративной вставкой ключей."""
    root: Node | None = None
    for key in keys:
        root = insert_iter(root, key)
    return root


# ---------------------------------------------------------------------------
# 2. Измеряемые величины: высота и средняя глубина узла
# ---------------------------------------------------------------------------


def tree_height(root: Node | None) -> int:
    """Высота в рёбрах: пустое дерево -1, один узел 0. Обход в ширину по уровням."""
    if root is None:
        return -1
    height = -1
    level = deque([root])
    while level:
        height += 1
        for _ in range(len(level)):
            node = level.popleft()
            if node.left is not None:
                level.append(node.left)
            if node.right is not None:
                level.append(node.right)
    return height


def sum_depths(root: Node | None) -> int:
    """Сумма глубин всех узлов (глубина корня — 0). Итеративно."""
    if root is None:
        return 0
    total = 0
    stack = [(root, 0)]
    while stack:
        node, d = stack.pop()
        total += d
        if node.left is not None:
            stack.append((node.left, d + 1))
        if node.right is not None:
            stack.append((node.right, d + 1))
    return total

def count_nodes(root: Node | None) -> int:
    """Число узлов дерева. Итеративно."""
    if root is None:
        return 0
    count = 0
    stack = [root]
    while stack:
        node = stack.pop()
        count += 1
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return count


def avg_depth(root: Node | None) -> float:
    """Средняя глубина узла: sum_depths / count_nodes (0.0 для пустого)."""
    n = count_nodes(root)
    return 0.0 if n == 0 else sum_depths(root) / n


def inorder_keys(root: Node | None) -> list[int]:
    """Ключи in-order-обхода (итеративно, с явным стеком)."""
    result: list[int] = []
    stack: list[Node] = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        result.append(node.key)
        node = node.right
    return result


# ---------------------------------------------------------------------------
# 3. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные деревья, аналитические значения, сверка с эталоном sorted()."""
    # Граничные случаи: пустое дерево и один узел
    assert tree_height(None) == -1
    assert avg_depth(None) == 0.0
    assert inorder_keys(None) == []
    single = build_bst([42])
    assert tree_height(single) == 0
    assert count_nodes(single) == 1
    assert avg_depth(single) == 0.0

    # Типовой случай: [2, 1, 3] — идеально сбалансированное дерево из 3 узлов
    small = build_bst([2, 1, 3])
    assert tree_height(small) == 1
    assert sum_depths(small) == 2  # 0 (корень) + 1 + 1

    # дубликаты игнорируются
    assert count_nodes(build_bst([5, 5, 5])) == 1

    # вырожденные деревья: по возрастанию и по убыванию
    n = 100
    for keys in (list(range(1, n + 1)), list(range(n, 0, -1))):
        deg = build_bst(keys)
        assert tree_height(deg) == n - 1
        assert avg_depth(deg) == (n - 1) / 2
    # то же на n = 10^4 (без RecursionError)
    big = build_bst(list(range(1, 10_001)))
    assert tree_height(big) == 9_999
    assert avg_depth(big) == 9_999 / 2

    # инвариант BST: in-order == sorted()
    rng = random.Random(0)
    for _ in range(200):
        keys = rng.sample(range(-1000, 1000), rng.randint(1, 60))
        root = build_bst(keys)
        assert inorder_keys(root) == sorted(keys)
        assert count_nodes(root) == len(keys)
        assert tree_height(root) >= math.floor(math.log2(len(keys)))
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Эксперимент и каркас замеров (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [100, 300, 1_000, 3_000, 10_000]
REPEATS = 5
TRIALS = 20  # независимых случайных деревьев на каждое n для усреднения


def random_keys(n: int, rng: random.Random) -> list[int]:
    """n уникальных случайных ключей (детерминированно по seed варианта)."""
    return rng.sample(range(10 * n), n)


def ordered_keys(n: int) -> list[int]:
    """n упорядоченных ключей 1..n — худший поток вставок для BST."""
    return list(range(1, n + 1))


def bench_search(root: Node | None, queries: list[int]) -> float:
    """Медиана времени поиска всех ключей queries по REPEATS запускам."""

    def run() -> None:
        for q in queries:
            node = root
            while node is not None and node.key != q:
                node = node.left if q < node.key else node.right

    run()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        run()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_experiment(seed: int) -> None:
    rng = random.Random(seed)
    rows = []
    print(f"{'n':>7} {'h_случ':>7} {'h_ср':>7} {'d_случ':>7} "
          f"{'h_упор':>7} {'d_упор':>8} {'log2n':>6} "
          f"{'t_случ,мс':>10} {'t_упор,мс':>10}")
    for n in SIZES:
        keys = random_keys(n, rng)
        root_rand = build_bst(keys)
        root_ord = build_bst(ordered_keys(n))
        h_r, d_r = tree_height(root_rand), avg_depth(root_rand)
        h_o, d_o = tree_height(root_ord), avg_depth(root_ord)
        # усреднение по дополнительным случайным деревьям
        hs = [h_r]
        for _ in range(TRIALS - 1):
            hs.append(tree_height(build_bst(random_keys(n, rng))))
        h_mean = statistics.mean(hs)
        # одинаковые запросы (по 1000 ключей) для обоих деревьев
        q_rand = [rng.choice(keys) for _ in range(1000)]
        q_ord = [rng.randint(1, n) for _ in range(1000)]
        t_r = bench_search(root_rand, q_rand) * 1000
        t_o = bench_search(root_ord, q_ord) * 1000
        rows.append((n, h_r, h_mean, d_r, h_o, d_o, math.log2(n), t_r, t_o))
        print(f"{n:>7} {h_r:>7} {h_mean:>7.1f} {d_r:>7.2f} {h_o:>7} "
              f"{d_o:>8.1f} {math.log2(n):>6.1f} {t_r:>10.2f} {t_o:>10.2f}")
    plot(rows)


def plot(rows) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен: графики не построены")
        return
    ns = [r[0] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].plot(ns, [r[1] for r in rows], "o-", label="h(n), случайный поток")
    ax[0].plot(ns, [r[4] for r in rows], "s-", label="h(n), упорядоченный поток")
    ax[0].plot(ns, [math.log2(n) for n in ns], "--", label="log₂(n)")
    ax[0].plot(ns, ns, ":", label="n")
    ax[0].set_title("Высота BST")
    ax[1].plot(ns, [r[3] for r in rows], "o-", label="средняя глубина, случайный")
    ax[1].plot(ns, [r[5] for r in rows], "s-", label="средняя глубина, упорядоченный")
    ax[1].plot(ns, [math.log2(n) for n in ns], "--", label="log₂(n)")
    ax[1].plot(ns, [n / 2 for n in ns], ":", label="n/2")
    ax[1].set_title("Средняя глубина узла")
    for a in ax:
        a.set_xscale("log")
        a.set_yscale("log")
        a.set_xlabel("n")
        a.grid(True, which="both", alpha=0.3)
        a.legend()
    fig.tight_layout()
    fig.savefig("bst_height.png", dpi=150)
    print("график сохранён: bst_height.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_experiment(seed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_experiment(seed)


if __name__ == "__main__":
    main()

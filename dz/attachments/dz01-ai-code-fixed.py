#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ИСПРАВЛЕННАЯ КОПИЯ dz01-ai-code.py (оригинал не изменялся).
# Исправления: (1) трёхстороннее разбиение — дубликаты больше не теряются;
# (2) случайный опорный элемент — нет систематической деградации на
# упорядоченных/обратных входах; (3) рекурсия только по меньшей части,
# больший участок обрабатывается циклом — глубина стека O(log n);
# (4) docstring приведён в соответствие с реальностью.
"""Fast sorting utilities.
 
In-place (на копии входа) quicksort с трёхсторонним разбиением.
Ожидаемое время O(n log n); худший случай O(n^2) возможен, но при
случайном выборе опорного элемента его вероятность пренебрежимо мала.
Память: O(n) на копию входа + O(log n) стек рекурсии (гарантированно).
"""
from __future__ import annotations
 
import random
 
_rng = random.Random()
 
 
def quicksort(data: list[int]) -> list[int]:
    """Sort a list of integers using three-way randomized quicksort.
 
    The input list is not modified; a new sorted list is returned.
    Duplicates are preserved.
 
    Examples
    --------
    >>> quicksort([3, 1, 2])
    [1, 2, 3]
    >>> quicksort([2, 2, 1, 2])
    [1, 2, 2, 2]
    >>> quicksort([])
    []
    """
    a = list(data)
    _sort(a, 0, len(a) - 1)
    return a
 
 
def _sort(a: list[int], lo: int, hi: int) -> None:
    while lo < hi:
        pivot = a[_rng.randint(lo, hi)]
        lt, i, gt = lo, lo, hi
        # инвариант: a[lo:lt] < pivot, a[lt:i] == pivot, a[gt+1:hi+1] > pivot
        while i <= gt:
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            elif a[i] > pivot:
                a[i], a[gt] = a[gt], a[i]
                gt -= 1
            else:
                i += 1
        # рекурсия по меньшей части, цикл по большей -> стек O(log n)
        if lt - lo < hi - gt:
            _sort(a, lo, lt - 1)
            lo = gt + 1
        else:
            _sort(a, gt + 1, hi)
            hi = lt - 1
 
 
if __name__ == "__main__":
    example = [5, 2, 9, 1, 7, 2, 5]
    print("Input :", example)
    print("Sorted:", quicksort(example))
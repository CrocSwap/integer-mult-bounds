#!/usr/bin/env python3
"""Separate Kronecker assembly and fraction-free exact determinant audit.

No primary-verifier import. Same AI worker, distinct arithmetic algorithm;
not a claim of independent human or formal-kernel review.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from math import factorial
import json


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def kronecker(a,b):
    return [[x*y for x in row_a for y in row_b]
            for row_a in a for row_b in b]


def fraction_free_det(source):
    a = [row[:] for row in source]
    n = len(a)
    old, sign = 1, 1
    for j in range(n-1):
        pivot_row = next((i for i in range(j,n) if a[i][j] != 0), None)
        if pivot_row is None:
            return 0
        if pivot_row != j:
            a[pivot_row],a[j] = a[j],a[pivot_row]
            sign = -sign
        pivot = a[j][j]
        for i in range(j+1,n):
            for k in range(j+1,n):
                numerator = a[i][k]*pivot-a[i][j]*a[j][k]
                quotient,remainder = divmod(numerator,old)
                need(remainder == 0, "Bareiss exact divisibility")
                a[i][k] = quotient
        for i in range(j+1,n):
            a[i][j] = 0
        old = pivot
    return sign*a[-1][-1]


def difference(matrix,order):
    permuted = [[matrix[r][c] for c in order] for r in order]
    result = [row[:] for row in permuted]
    for r in range(1,len(order)):
        for c in range(1,len(order)):
            result[r][c] -= permuted[r-1][c-1]
    return result


def inverse(matrix):
    n = len(matrix)
    a = [[Fraction(v) for v in row]+[Fraction(i==j) for j in range(n)]
         for i,row in enumerate(matrix)]
    for k in range(n):
        r = next(i for i in range(k,n) if a[i][k])
        a[k],a[r] = a[r],a[k]
        pivot = a[k][k]
        a[k] = [x/pivot for x in a[k]]
        for i in range(n):
            if i != k:
                t = a[i][k]
                a[i] = [x-t*y for x,y in zip(a[i],a[k])]
    return [row[n:] for row in a]


def rational_det(matrix):
    a = [list(map(Fraction,row)) for row in matrix]
    value = Fraction(1)
    for k in range(len(a)):
        r = next((i for i in range(k,len(a)) if a[i][k]),None)
        if r is None:
            return Fraction(0)
        if r != k:
            a[k],a[r] = a[r],a[k]
            value = -value
        pivot = a[k][k]
        value *= pivot
        for i in range(k+1,len(a)):
            ratio = a[i][k]/pivot
            for j in range(k+1,len(a)):
                a[i][j] -= ratio*a[k][j]
    return value


def main():
    h = [[1]]
    for upper,lower in ((2,3),(5,7),(11,13)):
        h = kronecker(h,[[1,upper],[lower,1]])
    digest = sha256()
    minimum,maximum,count = None,0,0
    for order in permutations(range(8)):
        value = fraction_free_det(difference(h,order))
        need(value != 0,"integer zero determinant at "+str(order))
        absolute = abs(value)
        minimum = absolute if minimum is None else min(minimum,absolute)
        maximum = max(maximum,absolute)
        digest.update(bytes(order)+(value%1000000007).to_bytes(4,"big"))
        count += 1
    need(count == factorial(8),"all orders included")
    h_inverse = inverse(h)
    h_det = fraction_free_det(h)
    inverse_orders = ((0,1,2,3,4,5,6,7),(0,1,2,4,3,6,7,5),
                      (0,1,2,4,6,5,3,7),(7,2,5,1,6,0,3,4))
    for order in inverse_orders:
        left = rational_det(difference(h_inverse,order))
        right = Fraction(fraction_free_det(difference(h,tuple(reversed(order)))),
                         h_det*h_det)
        need(left == right and left != 0,"inverse requires reversed displacement")
    e = difference(h,(0,1,2,4,3,6,7,5))
    mutant = [row[:] for row in e]
    for row in mutant:
        row[3] = row[2]
    need(fraction_free_det(mutant) == 0,"returning duplicate-column mutant")
    print(json.dumps({
        "status":"PASS_THREE_AXIS_INTEGER_REVIEW",
        "all_orders":count,"zero_determinants":0,
        "minimum_absolute_integer_determinant":minimum,
        "maximum_absolute_integer_determinant":maximum,
        "ordered_residue_sha256":digest.hexdigest(),
        "exact_inverse_reversal_checks":len(inverse_orders),
        "negative_controls":["duplicated displacement column"],
        "scope":"Independent arithmetic algorithm in same AI worker; source/analytic proof reviewed separately."
    },sort_keys=True,indent=2))


if __name__ == "__main__":
    main()

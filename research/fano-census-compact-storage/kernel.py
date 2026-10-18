#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Compact exact equality classes for the retained reduced-triple census.

The multiplication and full matrix-key functions are supplied unchanged by
the authenticated predecessor.  A singleton stores one base-n word code;
only a genuine collision allocates a member list.  Lists retain every member,
including classes larger than the pairs found in the retained instance.
"""

from collections import Counter


def decode_word(code, base):
    """Inverse of ((a * base) + b) * base + c on three base-n digits."""
    if type(base) is not int or base < 1 or type(code) is not int or not 0 <= code < base ** 3:
        raise ValueError("word code outside three-digit base-n domain")
    prefix, c = divmod(code, base)
    a, b = divmod(prefix, base)
    return a, b, c


class CompactClasses:
    """Insertion-ordered exact classes; callers supply valid base-n word codes.

    Matrix keys are kept in full.  Python dictionary equality, not its internal
    hash value, distinguishes them.  An auxiliary list references only classes
    that have collided, avoiding a second scan of all singleton members.
    """

    def __init__(self, base):
        if type(base) is not int or base < 0:
            raise ValueError("nonnegative word base")
        self.base = base
        self.classes = {}
        self.collisions = []

    def add(self, key, code):
        previous = self.classes.get(key)
        if previous is None:
            self.classes[key] = code
        elif type(previous) is int:
            words = [previous, code]
            self.classes[key] = words
            self.collisions.append(words)
        else:
            previous.append(code)

    def finish(self):
        singletons = len(self.classes) - len(self.collisions)
        sizes = Counter({1: singletons}) if singletons else Counter()
        total, relations = singletons, set()
        for encoded in self.collisions:
            sizes[len(encoded)] += 1
            total += len(encoded)
            words = [decode_word(code, self.base) for code in encoded]
            for left in words:
                for right in words:
                    if left != right:
                        a, b, c = left
                        d, e, f = right
                        word = a, b, c, f, e, d
                        if all(word[i] != word[(i + 1) % 6] for i in range(6)):
                            relations.add(word)
        return total, sizes, relations


def relation_census(matrices, mul, pack):
    """Same reduced triples, products, exact keys and ordered relators as PR3168."""
    n = len(matrices)
    classes = CompactClasses(n)
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            ab = mul(matrices[a], matrices[b])
            prefix = (a * n + b) * n
            for c in range(n):
                if c != b:
                    classes.add(pack(mul(ab, matrices[c])), prefix + c)
    return classes.finish()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent ordered-word counting of the capped direct-flow forest.

A unit is labelled by an ordered word of target slots.  The target slot k
of a child labelled v corresponds to the one parent labelled v followed by
k.  Thus matching uses a bijection of labelled slots, not a multinomial
formula or the producer's point matcher.  The compressed mode sums words
with equal products only after this matching rule has been specified.
"""
from collections import Counter
from itertools import product
from math import prod


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def profile(value, label):
    need(isinstance(value, dict) and value, label + ' nonempty inventory')
    need(all(type(k) is int and k > 0 and type(v) is int and v > 0
             for k, v in value.items()), label + ' positive integer entries')
    return dict(sorted(value.items()))


def _products(alphabet, degree, cap):
    """Count ordered words by product, retaining multiplicity of every letter."""
    levels = [Counter({1: 1})]
    for _ in range(degree):
        following = Counter()
        for old, count in levels[-1].items():
            for letter, copies in alphabet.items():
                if old * letter <= cap:
                    following[old * letter] += count * copies
        levels.append(following)
    return levels


def forest(targets, paid, n, height=None, *, literal=False, word_limit=1000000):
    """Return whole-job inventories and explicit raw-unit column counts.

    ``literal=True`` enumerates individual ordered target and paid words;
    it is intended for small fixtures.  The default performs exact integer
    convolution on their products.  Both use the same append-one-letter
    correspondence and preserve repeated target/paid positions.
    """
    targets, paid = profile(targets, 'target'), profile(paid, 'paid')
    m, smallest = max(targets), min(targets)
    need(type(n) is int and n >= m, 'top rank at least ambient')
    need(smallest >= 2 and max(paid) < m, 'strict recursive rank contract')
    cap = n // m
    if height is None:
        height, least = 0, 1
        while least * smallest <= cap:
            height += 1
            least *= smallest
    need(type(height) is int and height >= 0, 'nonnegative integral height')
    sources, exits, boundary, columns = Counter(), Counter(), Counter(), Counter()
    matched = 0
    W, P = sum(targets.values()), sum(paid.values())

    if literal:
        target_letters = tuple(k for k, count in targets.items() for _ in range(count))
        paid_letters = tuple(k for k, count in paid.items() for _ in range(count))
        # Bound enumeration before allocating any lists, including duplicate
        # rank letters: those duplicates represent distinct physical slots.
        need(sum(W ** g for g in range(height + 1)) +
             sum(P ** d for d in range(height + 1)) <= word_limit,
             'literal ordered-word limit')
        target_words = [list(product(target_letters, repeat=g)) for g in range(height + 1)]

        def target_products(g):
            return ((prod(word), 1) for word in target_words[g])

        def path_products(d):
            return ((prod(word), 1) for word in product(paid_letters, repeat=d)
                    if prod(word) <= cap)
    else:
        target_levels = _products(targets, height, cap)
        path_levels = _products(paid, height, cap)

        def target_products(g):
            return target_levels[g].items()

        def path_products(d):
            return path_levels[d].items()

    # Root target slots have no parent and are all distinct source jobs.
    for c, copies in target_products(height):
        if c <= cap:
            for k, count in targets.items():
                sources[c * k] += copies * count

    for depth in range(height + 1):
        remaining = height - depth
        for rho, paths in path_products(depth):
            for c, copies in target_products(remaining):
                if rho * c <= cap:
                    columns[rho * c] += paths * copies
            for r, rounds in paid.items():
                if remaining == 0:
                    # The sole empty target word has one raw unit here.
                    if rho <= cap:
                        exits[rho * r] += paths * rounds
                    continue
                # A parent word is v followed by its final target letter k.
                # Its paid r-job and the child v's k-slot have the same rank.
                for prefix, words in target_products(remaining - 1):
                    child_exists = rho * r * prefix <= cap
                    for k, slots in targets.items():
                        parent_exists = rho * prefix * k <= cap
                        copies = paths * rounds * words * slots
                        rank = rho * r * prefix * k
                        if parent_exists and child_exists:
                            matched += copies
                        elif parent_exists:
                            exits[rank] += copies
                            boundary[rank] += copies
                        elif child_exists:
                            sources[rank] += copies

    sources, exits, boundary, columns = map(lambda c: dict(sorted(c.items())),
                                           (sources, exits, boundary, columns))
    units = sum(columns.values())
    column_mass = sum(c * count for c, count in columns.items())
    S, E = sum(sources.values()), sum(exits.values())
    # These are slot-accounting checks, not the rank-mass identity that the
    # independent expanded-program verifier is intended to establish.
    need(S > 0 and S + matched == W * units, 'all target slots accounted for')
    need(E + matched == P * units, 'all issued paid slots accounted for')
    need(all(1 <= s <= n for s in sources), 'source rank range')
    need(all(1 <= e < n for e in exits), 'strict exit rank descent')
    return {'n': n, 'height': height, 'sources': sources, 'exits': exits,
            'boundary_exits': boundary, 'units_by_column': columns,
            'units': units, 'column_mass': column_mass, 'source_count': S,
            'matched_jobs': matched, 'routing_slots': S + E + (W + P) * units}

"""Order-preserving mask enumeration of PR968's eight-by-eight frame splits.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
The exact search and output order are inherited from themilkman216's PR968.
"""
from itertools import product


def frame_pair_solutions(F0, F1, ip):
    if len(F0) != 8 or len(F1) != 8 or len(set(F0 + F1)) != 16:
        raise ValueError('two disjoint ordered eight-element frames required')
    neighbors = [sum(bool(ip[g][f]) << j for j, f in enumerate(F0)) for g in F1]
    reverse_neighbors = [sum(bool(ip[f][g]) << j for j, g in enumerate(F1)) for f in F0]
    output = []
    for selected in range(256):
        left = [j for j in range(8) if selected >> j & 1]
        partners = [[] for _ in range(8)]
        for g, adjacent in enumerate(neighbors):
            hit = adjacent & selected
            if hit and hit & (hit - 1) == 0:
                partners[hit.bit_length() - 1].append(g)
        if any(not partners[f] for f in left):
            continue
        for choice in product(*(partners[f] for f in left)):
            # Retain the reference's injectivity guard even though singleton
            # neighborhoods already partition these first-partner lists.
            if len(set(choice)) != len(left):
                continue
            chosen = sum(1 << g for g in choice)
            right = [g for g in range(8) if not chosen >> g & 1]
            remainder = [f for f in range(8) if not selected >> f & 1]
            second = [[] for _ in range(8)]
            for f in remainder:
                hit = reverse_neighbors[f] & (255 ^ chosen)
                if hit and hit & (hit - 1) == 0:
                    second[hit.bit_length() - 1].append(f)
            if any(not second[g] for g in right):
                continue
            for choice2 in product(*(second[g] for g in right)):
                if len(set(choice2)) != len(right):
                    continue
                output.append([(F0[f], F1[g]) for f, g in zip(left, choice)] +
                              [(F1[g], F0[f]) for g, f in zip(right, choice2)])
    return output

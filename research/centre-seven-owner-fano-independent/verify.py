#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent check of the support-seven (Fano) exclusion for selected centre repair.

Re-derives the 112 owner routes through the predecessor's *independent*
chart-swap derivation (not the forward interpreter used by the audited
package), recomputes every cyclically reduced length-six route relation with a
separate row-major GF(2) product on the exact 17-coordinate active block, and
then replaces the written braid/triangle step with two exhaustive searches:

1. every 7-point incidence structure meeting the support-seven degree and
   pair conditions is a Fano plane;
2. no flag labelling of the Fano plane satisfies all 28 six-cycle relations.

Exact dict keys (Python ints) decide matrix equality; there is no hash bucket.
Prepared with substantial Claude (Anthropic) assistance.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INDEPENDENT = ROOT / 'research/centre-block-repair-information/independent.py'
AUDITED = ROOT / 'research/centre-seven-owner-information-floor/RESULT.json'
ACTIVE = 17
PORTS = 112


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def check_pins():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source pin: ' + row['path'])


def load_routes():
    """Routes from the chart-swap derivation, compiled from authenticated bytes."""
    module = types.ModuleType('pinned_independent_routes')
    module.__file__ = str(INDEPENDENT)
    exec(compile(INDEPENDENT.read_bytes(), module.__file__, 'exec'), module.__dict__)
    word, phases = module.sources()
    routes, _, _ = module.route_certificates(word, phases)
    need(len(routes) == PORTS and len(set(routes)) == PORTS, 'route count')
    return routes


def to_rows(columns):
    """Restrict a 73-column involution to its active block, as packed rows."""
    need(all(columns[k] == 1 << k for k in range(ACTIVE, len(columns))), 'spectator block')
    need(all(columns[k] < 1 << ACTIVE for k in range(ACTIVE)), 'active block closed')
    return tuple(sum(((columns[j] >> i) & 1) << j for j in range(ACTIVE)) for i in range(ACTIVE))


def mul(a, b):
    """Row-major GF(2) product: row i of AB is the XOR of B's rows selected by A's row i."""
    out = []
    for row in a:
        acc = 0
        while row:
            j = (row & -row).bit_length() - 1
            acc ^= b[j]
            row &= row - 1
        out.append(acc)
    return tuple(out)


def pack(rows):
    return sum(r << (ACTIVE * i) for i, r in enumerate(rows))


IDENTITY = tuple(1 << i for i in range(ACTIVE))


def relation_census(m):
    """All reduced triples; exact classes keyed by the packed matrix."""
    n = len(m)
    classes = {}
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            ab = mul(m[a], m[b])
            for c in range(n):
                if c != b:
                    classes.setdefault(pack(mul(ab, m[c])), []).append((a, b, c))
    sizes = Counter(map(len, classes.values()))
    relations = set()
    for words in classes.values():
        for left in words:
            for right in words:
                if left != right:
                    a, b, c = left
                    d, e, f = right
                    w = (a, b, c, f, e, d)
                    if all(w[i] != w[(i + 1) % 6] for i in range(6)):
                        relations.add(w)
    return sum(sizes[k] * k for k in sizes), sizes, relations


def closed_under_symmetry(words):
    out = set()
    for w in words:
        for r in range(6):
            v = w[r:] + w[:r]
            out.add(v)
            out.add(v[::-1])
    return out


def product_is_identity(m, w):
    acc = IDENTITY
    for x in w:
        acc = mul(acc, m[x])
    return acc == IDENTITY


def support_seven_structures(points=7, min_line=3, min_degree=3, pair_cap=1):
    """All families of lines (subsets of size >= min_line) with each point pair in
    at most pair_cap lines and each point on at least min_degree lines."""
    candidates = [frozenset(s) for k in range(min_line, points + 1)
                  for s in combinations(range(points), k)]
    found = []

    def extend(start, chosen, pair_count):
        degree = Counter(p for line in chosen for p in line)
        if all(degree[p] >= min_degree for p in range(points)):
            found.append(tuple(sorted(tuple(sorted(l)) for l in chosen)))
        for i in range(start, len(candidates)):
            line = candidates[i]
            pairs = list(combinations(sorted(line), 2))
            if all(pair_count[p] < pair_cap for p in pairs):
                for p in pairs:
                    pair_count[p] += 1
                chosen.append(line)
                extend(i + 1, chosen, pair_count)
                chosen.pop()
                for p in pairs:
                    pair_count[p] -= 1

    extend(0, [], Counter())
    return found


FANO = tuple(tuple(sorted({i, (i + 1) % 7, (i + 3) % 7})) for i in range(7))


def fano_six_cycles(lines):
    """Six-cycles g-L1-h-L3-k-L2-g of the incidence graph, as six flags in
    cycle order: (g,L1),(h,L1),(h,L3),(k,L3),(k,L2),(g,L2)."""
    on = [[i for i, l in enumerate(lines) if p in l] for p in range(7)]
    cycles = set()
    for g in range(7):
        for l1, l2 in combinations(on[g], 2):
            for h in lines[l1]:
                for k in lines[l2]:
                    if g in (h, k):
                        continue
                    for l3 in set(on[h]) & set(on[k]):
                        if l3 in (l1, l2):
                            continue
                        flags = ((g, l1), (h, l1), (h, l3), (k, l3), (k, l2), (g, l2))
                        # one representative per undirected cycle
                        key = frozenset(flags)
                        cycles.add((key, flags))
    by_key = {}
    for key, flags in cycles:
        by_key.setdefault(key, flags)
    return list(by_key.values())


def labelings(lines, relations, alphabet, first=False):
    """Backtracking over flag labels; returns every labelling meeting all six-cycle
    relations, with distinct labels at each point and on each line."""
    cycles = fano_six_cycles(lines)
    flags = sorted({f for c in cycles for f in c})
    index = {}
    for w in relations:
        for pos, x in enumerate(w):
            index.setdefault((pos, x), set()).add(w)
    cyc_of = {f: [(c, c.index(f)) for c in cycles if f in c] for f in flags}
    label = {}
    found = []

    def consistent(cycle):
        sets = [index.get((pos, label[f]), set()) for pos, f in enumerate(cycle) if f in label]
        return not sets or bool(set.intersection(*sets))

    def go(i):
        if found and first:
            return
        if i == len(flags):
            found.append(dict(label))
            return
        f = flags[i]
        used = {label[o] for o in label if o[0] == f[0] or o[1] == f[1]}
        for x in alphabet:
            if x in used:
                continue
            label[f] = x
            if all(consistent(c) for c, _ in cyc_of[f]):
                go(i + 1)
            del label[f]

    go(0)
    return cycles, found


def build():
    check_pins()
    routes = load_routes()
    m = [to_rows(r) for r in routes]
    need(all(mul(x, x) == IDENTITY for x in m), 'involutions')
    pair_products = {pack(mul(m[a], m[b])) for a in range(PORTS) for b in range(PORTS) if a != b}
    need(len(pair_products) == PORTS * (PORTS - 1), 'unique ordered products')

    total, sizes, rel = relation_census(m)
    need(total == PORTS * (PORTS - 1) ** 2, 'reduced triple count')
    rel6 = closed_under_symmetry(rel)
    need(rel6 == rel, 'relation set closed under rotation and reversal')
    need(all(product_is_identity(m, w) for w in rel6), 'relations multiply to identity')
    braid = sorted({tuple(sorted(set(w))) for w in rel6})
    need(all(len(set(w)) == 2 for w in rel6), 'every relation is a braid word')

    audited = json.loads(AUDITED.read_bytes())
    need([list(e) for e in braid] == audited['braid_edges'], 'braid edges differ from audited receipt')
    need({str(k): v for k, v in sorted(sizes.items())}
         == audited['exact_product_class_size_histogram'], 'class histogram differs from audited receipt')

    structures = support_seven_structures()
    need(all(len(s) == 7 and all(len(l) == 3 for l in s) for s in structures), 'non-Fano structure')
    need(len(structures) == 30, 'labelled Fano plane count')
    loose = support_seven_structures(min_degree=2)
    need(len(loose) > len(structures), 'degree control is not vacuous')

    cycles, found = labelings(FANO, rel6, range(PORTS))
    need(len(cycles) == 28, 'Heawood six-cycle count')
    need(not found, 'a Fano labelling meets every six-cycle relation')

    # Positive control: plant a Fano labelling realised in the abelian group
    # Z2^4 (label = point code XOR line code; every six-cycle word XORs to 0),
    # admit only its own cycle words, and require the search to recover it.
    # Removing one admitted cycle word must lose it: the pruning is not vacuous.
    points, line_codes = (1, 2, 4, 8, 3, 5, 6), (9, 10, 12, 7, 11, 13, 14)
    planted = {(p, l): points[p] ^ line_codes[l]
               for l, line in enumerate(FANO) for p in line}
    planted_words = {tuple(planted[f] for f in c) for c in cycles}
    need(all(w[0] ^ w[1] ^ w[2] ^ w[3] ^ w[4] ^ w[5] == 0 for w in planted_words),
         'planted words are group relations')
    _, control = labelings(FANO, closed_under_symmetry(planted_words), range(16))
    need(planted in control, 'search positive control lost the planted labelling')
    admitted = closed_under_symmetry(planted_words)
    dropped = admitted - closed_under_symmetry([min(planted_words)])
    need(dropped != admitted, 'mutant removes a relation class')
    _, mutant = labelings(FANO, dropped, range(16))
    need(planted not in mutant, 'search accepted a labelling with a missing relation')

    return {
        'status': 'PASS_CENTRE_SEVEN_OWNER_FANO_INDEPENDENT',
        'audited_package': 'research/centre-seven-owner-information-floor',
        'route_derivation': 'centre-block-repair-information/independent.py chart swaps',
        'active_block': ACTIVE,
        'reduced_triples': total,
        'class_size_histogram': {str(k): v for k, v in sorted(sizes.items())},
        'cyclic_length6_relation_words_with_symmetry': len(rel6),
        'braid_edges': len(braid),
        'support_seven_structures': len(structures),
        'support_seven_structures_all_fano': True,
        'fano_six_cycles': len(cycles),
        'fano_labellings_meeting_all_relations': 0,
        'positive_control_planted_labelling_recovered': True,
        'positive_control_labellings_found': len(control),
        'mutant_control_rejects_planted': True,
        'scope': 'independent finite check of the audited support-7 exclusion; no supplier, tariff or kappa change',
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = build()
    if args.write:
        args.write.write_bytes(canonical(result))
    else:
        need(canonical(result) == (HERE / 'RESULT.json').read_bytes(), 'receipt mismatch')
    print('PASS_CENTRE_SEVEN_OWNER_FANO_INDEPENDENT braid_edges=50 fano_structures_only '
          'fano_labellings=0 no_new_kappa')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Independent exact E8 frame-orbit and signed-transport audit (stdlib)."""

import argparse
from collections import Counter, deque
from hashlib import sha1, sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def inner(a, b):
    n = sum(x * y for x, y in zip(a, b))
    need(n % 4 == 0, 'nonintegral root pairing')
    return n // 4


def canonical(v):
    return v if next(x for x in v if x) > 0 else tuple(-x for x in v)


def geometry():
    """Generate root lines as a set, independent of PR1212's root ordering."""
    all_roots = set()
    for a, b in combinations(range(8), 2):
        for sa, sb in product((-2, 2), repeat=2):
            v = [0] * 8
            v[a], v[b] = sa, sb
            all_roots.add(tuple(v))
    for signs in product((-1, 1), repeat=8):
        if sum(x < 0 for x in signs) % 2 == 0:
            all_roots.add(signs)
    need(len(all_roots) == 240 and all(tuple(-x for x in r) in all_roots
                                        for r in all_roots), '240 antipodal roots')
    lines = sorted({canonical(r) for r in all_roots})
    need(len(lines) == 120 and all(inner(r, r) == 2 for r in lines),
         '120 root lines of norm two')
    index = {r: i for i, r in enumerate(lines)}
    gram = [[inner(a, b) for b in lines] for a in lines]
    need(all(gram[i][j] in (-1, 0, 1) for i in range(120)
             for j in range(120) if i != j), 'off-diagonal Gram alphabet')
    frame = []
    for a in range(4):
        for sign in (-1, 1):
            v = [0] * 8
            v[2 * a], v[2 * a + 1] = 2, 2 * sign
            frame.append(index[canonical(tuple(v))])
    frame = tuple(sorted(frame))
    need(len(set(frame)) == 8 and
         all(gram[a][b] == 0 for a, b in combinations(frame, 2)),
         'FRAME0 is orthogonal')
    return lines, index, gram, frame


def all_frames(gram):
    """Enumerate 8-cliques in the orthogonality graph by increasing indices."""
    orth = []
    for i in range(120):
        orth.append(sum(1 << j for j in range(i + 1, 120)
                        if gram[i][j] == 0))
    frames = []

    def visit(prefix, candidates):
        if len(prefix) == 8:
            frames.append(prefix)
            return
        while candidates:
            bit = candidates & -candidates
            i = bit.bit_length() - 1
            candidates -= bit
            visit(prefix + (i,), candidates & orth[i])

    visit((), (1 << 120) - 1)
    need(len(frames) == 2025 and len(set(frames)) == 2025,
         'complete 2025-frame census')
    return frames


def reflections(lines, index, gram):
    result = []
    for a, root in enumerate(lines):
        perm, signs = [], []
        for i, v in enumerate(lines):
            reflected = tuple(x - gram[i][a] * y for x, y in zip(v, root))
            representative = canonical(reflected)
            need(representative in index, 'reflection leaves root set')
            perm.append(index[representative])
            signs.append(1 if reflected == representative else -1)
        need(len(set(perm)) == 120, 'reflection is a line permutation')
        result.append((tuple(perm), tuple(signs)))
    return result


def compose(g, h):
    """Apply h, then g; preserve representative-root signs."""
    gp, gs = g
    hp, hs = h
    return (tuple(gp[hp[i]] for i in range(120)),
            tuple(gs[hp[i]] * hs[i] for i in range(120)))


def stabilizer_generators(refs, frame):
    fixed = set(frame)
    table = {}
    for g in refs:
        if {g[0][i] for i in frame} == fixed:
            table[g[0]] = g
    for a, b in combinations(range(120), 2):
        g = compose(refs[a], refs[b])
        if {g[0][i] for i in frame} == fixed:
            table[g[0]] = g
    need(len(table) == 204, '204 distinct one/two-reflection stabilizer maps')
    return list(table.values())


def gram_transport(gram, generators):
    """Verify sign-aware Gram conjugation and sign-free label pairing."""
    for perm, signs in generators:
        for i in range(120):
            for j in range(120):
                need(gram[perm[i]][perm[j]] == signs[i] * signs[j] * gram[i][j],
                     'signed Gram transport')
                need(((gram[perm[i]][perm[j]] + 1) & 1) ==
                     ((gram[i][j] + 1) & 1), 'binary label pairing transport')


def orbit_partition(items, generators, action):
    remaining = set(items)
    parts = []
    while remaining:
        rep = min(remaining)
        seen = {rep}
        queue = deque([rep])
        while queue:
            item = queue.popleft()
            for perm, _ in generators:
                nxt = action(perm, item)
                need(nxt in items, 'group action leaves domain')
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        need(seen <= remaining, 'overlapping orbit partitions')
        parts.append(seen)
        remaining -= seen
    return parts


def hit_type(gram, frame0, frame):
    classes = Counter()
    for i in frame:
        support = tuple(f for f in frame0 if gram[i][f])
        signs = tuple(gram[i][f] for f in support)
        need(len(support) == 4, 'four pivot neighbors')
        classes[support, sum(x < 0 for x in signs) & 1] += 1
    return tuple(sorted(classes.values(), reverse=True))


def source_numbering(index):
    """Translate PR1212's published line numbers, without its group code."""
    roots = []
    for a, b in combinations(range(8), 2):
        for sa, sb in product((1, -1), repeat=2):
            v = [0] * 8
            v[a], v[b] = 2 * sa, 2 * sb
            roots.append(tuple(v))
    roots.extend(signs for signs in product((1, -1), repeat=8)
                 if sum(x < 0 for x in signs) % 2 == 0)
    numbered, seen = [], set()
    for r in roots:
        c = canonical(r)
        if c not in seen:
            numbered.append(index[c])
            seen.add(c)
    need(len(numbered) == 120 and len(set(numbered)) == 120,
         'published 120-line numbering')
    return numbered


def class_profile(gram, live, pivot):
    classes = {}
    for i in live:
        if i in pivot:
            continue
        support = tuple(f for f in pivot if gram[i][f])
        need(len(support) == 4, 'four pivot neighbors in class profile')
        signs = tuple(gram[i][f] for f in support)
        key = (support, sum(x < 0 for x in signs) & 1)
        classes.setdefault(key, []).append((i, signs))
    all_blocks = {tuple(f for f in pivot if gram[i][f])
                  for i in range(120) if i not in pivot}
    need(len(all_blocks) == 14, '14 geometric D4 blocks')
    complete = sum(len(rows) == 4 for rows in classes.values())
    incomplete = sum(len(rows) != 4 for rows in classes.values())
    blocks = sum(any(len(classes.get((support, parity), [])) == 4
                     for parity in (0, 1)) for support in all_blocks)
    return classes, (complete, incomplete, blocks)


def class_witnesses(gram, live, pivot, classes):
    """Independently check PR1212 Lemma 5's fixed P104 group witnesses."""
    checks = 0
    for (support, _), rows in classes.items():
        if len(rows) != 4:
            continue
        for c, d in combinations(range(4), 2):
            for sign in (-1, 1):
                group = [i for i, values in rows
                         if values[c] * values[d] == sign]
                need(len(group) == 2, 'complete class group is a pair')
                candidates = [j for j in live if j not in pivot and
                              set(support) &
                              {f for f in pivot if gram[j][f]} ==
                              {support[c], support[d]} and
                              all(gram[i][j] == 0 for i in group)]
                need(bool(candidates), 'missing live class group witness')
                checks += 1
    return checks


def class_geometry(gram, pivot, classes):
    """Check the Hadamard and gluing geometry used by Lemmas 5–6."""
    blocks = sorted({support for support, _ in classes})
    need(len(blocks) == 14 and all(len(b) == 4 for b in blocks),
         '14 four-point blocks')
    triple_counts = Counter(t for block in blocks for t in combinations(block, 3))
    need(len(triple_counts) == 56 and set(triple_counts.values()) == {1},
         'Steiner S(3,4,8) triple coverage')
    complete = [(support, rows) for (support, _), rows in classes.items()
                if len(rows) == 4]
    hadamard = 0
    for support, rows in complete:
        signs = [row for _, row in rows]
        need(all(sum(a * b for a, b in zip(x, y)) == 0
                 for x, y in combinations(signs, 2)),
             'orthogonal sign rows in complete class')
        need(all(sum(row[a] * row[b] for row in signs) == 0
                 for a, b in combinations(range(4), 2)),
             'orthogonal sign columns in complete class')
        hadamard += 1
    gluing = 0
    for (support, rows), (other, others) in permutations(complete, 2):
        overlap = sorted(set(support) & set(other))
        if support == other or len(overlap) != 2:
            continue
        k, kp = overlap
        a, b = support.index(k), support.index(kp)
        c, d = other.index(k), other.index(kp)
        for j, sj in others:
            # PR1212 Lemma 6: j is orthogonal to exactly the two rows i of
            # the other class with eps_ik eps_ik' = -eps_jk eps_jk'.
            orthogonal = [i for i, _ in rows if gram[i][j] == 0]
            rule = [i for i, si in rows if si[a] * si[b] == -sj[c] * sj[d]]
            need(len(orthogonal) == 2 and orthogonal == rule,
                 'cross-class orthogonal rows follow the sign rule')
            gluing += 1
    need(hadamard == 24 and gluing > 0, 'full class geometry')
    return {'steiner_triples': len(triple_counts),
            'hadamard_classes': hadamard,
            'cross_class_gluing_checks': gluing}


def representative_profiles(gram, frame0, frames, orbit_records, index):
    numbering = source_numbering(index)
    original_frame0 = []
    for a in range(4):
        for sign in (1, -1):
            v = [0] * 8
            v[2 * a], v[2 * a + 1] = 2, 2 * sign
            original_frame0.append(index[canonical(tuple(v))])
    need(set(original_frame0) == set(frame0), 'published FRAME0 identity')
    original_p112 = [i for i in numbering if i not in frame0]
    pr717 = tuple(sorted(original_p112[q]
                         for q in (9, 15, 24, 46, 52, 66, 94, 104)))
    need(pr717 in frames and hit_type(gram, frame0, pr717) == (1,) * 8,
         'PR717 P104 is in the admissible class-hit type')
    original44 = tuple(sorted(numbering[i] for i in
                              (2, 3, 16, 17, 46, 47, 52, 53)))
    original44_pivot = tuple(sorted(numbering[i] for i in
                                    (4, 5, 14, 15, 48, 49, 50, 51)))
    need(original44 in frames and hit_type(gram, frame0, original44) == (4, 4),
         'PR1212 original type-44 representative')
    live44 = set(range(120)) - set(frame0) - set(original44)
    _, original44_profile = class_profile(gram, live44, original44_pivot)
    need(original44_profile == (24, 0, 12),
         'PR1212 chosen type-44 pivot has two empty blocks')
    # P104 type (2,2,2,2) and the cited live pivot are published as
    # line numbers in PR1212 §10. Match that exact representative and
    # independently check its non-SAT proof hypotheses.
    puncture = {numbering[i] for i in (2, 3, 18, 19, 40, 41, 52, 53)}
    pivot = tuple(sorted(numbering[i] for i in
                         (12, 13, 22, 23, 30, 31, 36, 37)))
    live = set(range(120)) - set(frame0) - puncture
    need(tuple(sorted(puncture)) in frames and set(pivot) <= live and
         tuple(sorted(pivot)) in frames,
         'published P104 type-2222 unit and pivot')
    classes, profile = class_profile(gram, live, pivot)
    need(profile == (24, 0, 14), 'type-2222 complete classes and blocks')
    witnesses = class_witnesses(gram, live, pivot, classes)
    need(witnesses == 24 * 6 * 2, 'all type-2222 group witnesses')
    # For the other two orbit representatives, evaluate the class profile
    # at every live frame and retain the best incomplete-class count.
    min_profiles = []
    alternate_44 = None
    for record in orbit_records:
        deletion = (set(original44) if record['size'] == 28
                    else set(record['representative']))
        live = set(range(120)) - set(frame0) - deletion
        candidates = (fr for fr in frames if set(fr) <= live)
        census = [(class_profile(gram, live, fr)[1], fr) for fr in candidates]
        best = min((p for p, _ in census),
                   key=lambda p: (p[1], -p[2], -p[0]))
        min_profiles.append({'orbit_size': record['size'],
                             'best_profile': list(best)})
        if record['size'] == 28:
            complete = Counter(p[2] for p, _ in census if p[1] == 0)
            need(complete == {12: 1, 14: 24},
                 'type-44 complete-pivot census')
            pivot44 = min(fr for p, fr in census if p == (24, 0, 14))
            # Bind the displayed pivot to PR1212's published numbering.
            # It is also PR1212's published type-(2,2,2,2) pivot.
            need(pivot44 == pivot, 'alternate pivot is PR1212 lines '
                 '{12,13,22,23,30,31,36,37}')
            classes44, profile44 = class_profile(gram, live, pivot44)
            witness44 = class_witnesses(gram, live, pivot44, classes44)
            need(witness44 == 288, 'alternate type-44 group witnesses')
            geometry44 = class_geometry(gram, pivot44, classes44)
            published = {j: i for i, j in enumerate(numbering)}
            alternate_44 = {'pr1212_numbering': {
                                'deletion': sorted(published[i] for i in original44),
                                'pivot': sorted(published[i] for i in pivot44),
                                'pr1212_chosen_pivot':
                                sorted(published[i] for i in original44_pivot)},
                            'deletion': sorted(original44),
                            'pr1212_chosen_pivot': list(original44_pivot),
                            'pr1212_chosen_profile': list(original44_profile),
                            'pivot': list(pivot44),
                            'profile': list(profile44),
                            'group_witnesses': witness44,
                            'class_geometry': geometry44,
                            'complete_pivots_by_block_coverage':
                            {str(k): v for k, v in sorted(complete.items())}}
    need(min_profiles == [
        {'orbit_size': 28, 'best_profile': [24, 0, 14]},
        {'orbit_size': 336, 'best_profile': [24, 0, 14]},
        {'orbit_size': 896, 'best_profile': [22, 4, 14]}],
        'P104 best class profiles: ' + repr(min_profiles))
    return {'pr717_type': [1] * 8,
            'published_2222_profile': list(profile),
            'published_2222_group_witnesses': witnesses,
            'p104_best_profiles': min_profiles,
            'alternate_44': alternate_44}


def zero_pattern_cnf(gram, live, pivot):
    """Necessary two-term/diagonal zero-pattern clauses for the new pivot.

    A positive main variable means that the corresponding complex matrix
    entry is nonzero. The Boolean constraints are necessary over every
    characteristic-zero field; they never approximate coefficient values.
    """
    nonpivot = sorted(set(live) - set(pivot))
    need(len(nonpivot) == 96, 'P104 nonpivot count')
    support = {i: tuple(f for f in pivot if gram[i][f]) for i in nonpivot}
    need(all(len(support[i]) == 4 for i in nonpivot),
         'four slots per nonpivot row')
    variable = {}

    def var(key):
        if key not in variable:
            variable[key] = len(variable) + 1
        return variable[key]

    for side in ('a', 'b'):
        for i in nonpivot:
            for f in support[i]:
                var((side, i, f))
    main_variables = list(range(1, len(variable) + 1))
    clauses = []
    two = 0
    for i in nonpivot:
        for j in nonpivot:
            if i == j or gram[i][j] != 0:
                continue
            overlap = sorted(set(support[i]) & set(support[j]))
            if len(overlap) != 2:
                continue
            f, h = overlap
            x, y = var(('a', i, f)), var(('b', j, f))
            u, v = var(('a', i, h)), var(('b', j, h))
            # If one product is nonzero, the other must be nonzero too.
            clauses.extend(((-x, -y, u), (-x, -y, v),
                            (-u, -v, x), (-u, -v, y)))
            two += 1
    for i in nonpivot:
        products = []
        for f in support[i]:
            x, y = var(('a', i, f)), var(('b', i, f))
            z = var(('product', i, f))
            # z iff both entries are nonzero.
            clauses.extend(((-z, x), (-z, y), (z, -x, -y)))
            products.append(z)
        clauses.append(tuple(products))
    # Refute the existence of at least one zero among the supported entries.
    clauses.append(tuple(-v for v in main_variables))
    need(two == 3904 and len(variable) == 1152 and len(clauses) == 16865,
         'alternate-pivot reduced CNF size')
    return clauses, len(variable), {'two_term_equations': two,
                                    'diagonal_equations': len(nonpivot),
                                    'main_variables': len(main_variables),
                                    'variables': len(variable),
                                    'clauses': len(clauses)}


def rup_replay(clauses, variable_count, proof_lines):
    """Check each added lemma by reverse unit propagation; ignore deletions."""
    database = []
    occurrence = {}
    units = []

    def add_clause(clause):
        idx = len(database)
        database.append(clause)
        if len(clause) == 1:
            units.append(clause[0])
        for literal in set(clause):
            occurrence.setdefault(literal, []).append(idx)

    for clause in clauses:
        add_clause(tuple(clause))

    def implies(clause):
        assigned = [0] * (variable_count + 1)
        queue = deque()

        def assign(literal):
            v = abs(literal)
            value = 1 if literal > 0 else -1
            if assigned[v] == -value:
                return False
            if assigned[v] == 0:
                assigned[v] = value
                queue.append(literal)
            return True

        for literal in clause:
            if not assign(-literal):
                return True
        for literal in units:
            if not assign(literal):
                return True
        while queue:
            just_true = queue.popleft()
            for idx in occurrence.get(-just_true, ()):
                remaining = None
                satisfied = False
                for literal in database[idx]:
                    value = assigned[abs(literal)]
                    if value == (1 if literal > 0 else -1):
                        satisfied = True
                        break
                    if value == 0:
                        if remaining is None:
                            remaining = literal
                        else:
                            remaining = 0
                if satisfied or remaining == 0:
                    continue
                if remaining is None or not assign(remaining):
                    return True
        return False

    added = deleted = 0
    empty = False
    for number, raw in enumerate(proof_lines, 1):
        raw = raw.strip()
        if not raw or raw.startswith('c'):
            continue
        if raw.startswith('d '):
            deleted += 1
            continue
        values = tuple(int(x) for x in raw.split())
        need(values and values[-1] == 0, f'proof terminator at line {number}')
        lemma = values[:-1]
        need(all(1 <= abs(v) <= variable_count for v in lemma),
             f'proof variable range at line {number}')
        need(implies(lemma), f'non-RUP lemma at line {number}')
        add_clause(lemma)
        added += 1
        if not lemma:
            empty = True
            break
    need(empty, 'proof must derive empty clause')
    return {'added_lemmas': added, 'ignored_deletions': deleted,
            'derived_empty': empty}


def proof_controls(clauses, variable_count, proof_lines):
    # Without the hypothesized zero, the witness gauge solves every
    # remaining necessary condition. Its loss must invalidate the proof.
    try:
        rup_replay(clauses[:-1], variable_count, proof_lines)
    except ValueError:
        pass
    else:
        raise ValueError('RUP proof accepted without some-zero hypothesis')
    try:
        rup_replay(clauses, variable_count, ['1 0'] + proof_lines)
    except ValueError:
        pass
    else:
        raise ValueError('RUP proof accepted a spurious unit lemma')
    try:
        rup_replay(clauses, variable_count, proof_lines[:-1])
    except ValueError:
        pass
    else:
        raise ValueError('RUP proof accepted after final-line omission')


def cost_bridge_controls(lines, gram, frame0, frames, generators):
    """Exact support and signed-gauge spot controls; general bridge is written."""
    # A diagonal invertible gauge can change nonzero entries, but never
    # support. Check the complete matrix, not just row counts, on each of
    # the three orbit representatives plus P112/P120.
    sample_frames = [frame0] + [min(part) for part in frames]
    checks = 0
    for deletion in [()] + sample_frames:
        live = [i for i in range(120) if i not in deletion]
        scale = [1 + (i % 7) for i in range(120)]
        for i in live:
            for j in live:
                g = gram[i][j]
                value_num = 2 * g * scale[i]
                need((value_num != 0) == (g != 0), 'gauge support invariance')
                # Since K_ij = 2 G_ij d_i/d_j, check its E constraints
                # exactly without constructing Fraction objects.
                if i == j:
                    need(value_num == 4 * scale[j], 'gauge diagonal')
                elif g == 0:
                    need(value_num == 0, 'gauge orthogonal entry')
                checks += 1
    # The sign cocycle must also transport a nonconstant gauge. Checking
    # every pair for each generator is inexpensive and catches omission
    # of the representative-root signs.
    for perm, signs in generators:
        for i in range(120):
            for j in range(120):
                lhs = gram[perm[i]][perm[j]] * (1 + i % 7) * (1 + j % 7)
                rhs = signs[i] * signs[j] * gram[i][j] * (1 + i % 7) * (1 + j % 7)
                need(lhs == rhs, 'gauged signed transport')
    return checks


def pins():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    need(manifest['base_commit'] == 'a18b4b0136d647529971e9fcb99fa83f5b9a0b81',
         'base commit pin')
    for source in manifest['files']:
        if source['usage'] == 'provenance':
            continue  # Historical bytes are checked against base Git by metadata.
        data = (ROOT / source['path']).read_bytes()
        need(sha256(data).hexdigest() == source['sha256'],
             'SHA-256 source pin ' + source['path'])
        need(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() ==
             source['git_blob'], 'Git blob source pin ' + source['path'])
    # PR1212 head 57099cb5's PROOF.md is now on main byte-for-byte.
    archived = (ROOT / manifest['pr1212_proof']['path']).read_bytes()
    need(sha256(archived).hexdigest() == manifest['pr1212_proof']['sha256'],
         'PR1212 proof SHA-256')
    need(sha1(b'blob ' + str(len(archived)).encode() + b'\0' + archived).hexdigest() ==
         manifest['pr1212_proof']['git_blob'], 'PR1212 proof Git blob')
    proof = (HERE / 'proof-alt-p104-44.drup').read_bytes()
    need(sha256(proof).hexdigest() == manifest['generated_proof']['sha256'],
         'new RUP proof SHA-256')


def mutation_controls(gram, generators):
    odd = next((i, j) for i in range(120) for j in range(i + 1, 120)
               if gram[i][j] != 0)
    changed = [list(row) for row in gram]
    a, b = odd
    changed[a][b] *= -1
    changed[b][a] *= -1
    try:
        gram_transport(changed, generators)
    except ValueError:
        pass
    else:
        raise ValueError('undetected Gram sign mutation')
    perm, signs = generators[0]
    bad_perm = list(perm)
    bad_perm[0], bad_perm[1] = bad_perm[1], bad_perm[0]
    try:
        gram_transport(gram, [(tuple(bad_perm), signs)])
    except ValueError:
        pass
    else:
        raise ValueError('undetected transport permutation mutation')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    pins()
    lines, index, gram, frame0 = geometry()
    frames = all_frames(gram)
    need(frame0 in frames, 'FRAME0 enumerated')
    refs = reflections(lines, index, gram)
    # All 2025 frames are reached by root reflections; it is enough to
    # transport a P112 statement from FRAME0 to every frame complement.
    frame_set = set(frames)
    frame_orbit = orbit_partition(frame_set, refs,
        lambda perm, fr: tuple(sorted(perm[i] for i in fr)))
    need(len(frame_orbit) == 1 and len(frame_orbit[0]) == 2025,
         'Weyl frame transitivity')
    gens = stabilizer_generators(refs, frame0)
    gram_transport(gram, gens)
    mutation_controls(gram, gens)
    live112 = set(range(120)) - set(frame0)
    lines_orbits = orbit_partition(live112, gens, lambda perm, i: perm[i])
    need(len(lines_orbits) == 1 and len(lines_orbits[0]) == 112,
         'P112 line transitivity')
    frames112 = {fr for fr in frames if set(fr) <= live112}
    need(len(frames112) == 1260, '1260 live second frames')
    parts = orbit_partition(frames112, gens,
        lambda perm, fr: tuple(sorted(perm[i] for i in fr)))
    orbit_records = []
    for part in parts:
        types = {hit_type(gram, frame0, fr) for fr in part}
        need(len(types) == 1, 'class-hit type invariant within orbit')
        orbit_records.append({'size': len(part), 'hit_type': list(next(iter(types))),
                              'representative': list(min(part))})
    orbit_records.sort(key=lambda item: item['size'])
    need([(r['size'], r['hit_type']) for r in orbit_records] == [
        (28, [4, 4]), (336, [2, 2, 2, 2]), (896, [1] * 8)],
        'P104 frame orbit sizes/types')
    profiles = representative_profiles(gram, frame0, frames, orbit_records, index)
    alternate = profiles['alternate_44']
    deletion = set(alternate['deletion'])
    live44 = live112 - deletion
    cnf, variable_count, cnf_stats = zero_pattern_cnf(
        gram, live44, tuple(alternate['pivot']))
    cnf_digest = sha256('\n'.join(' '.join(map(str, clause))
                                  for clause in cnf).encode()).hexdigest()
    proof_bytes = (HERE / 'proof-alt-p104-44.drup').read_bytes()
    proof_lines = proof_bytes.decode('ascii').splitlines()
    rup = rup_replay(cnf, variable_count, proof_lines)
    proof_controls(cnf, variable_count, proof_lines)
    gauge_entries = cost_bridge_controls(lines, gram, frame0, parts, gens)
    result = {'schema_version': 1, 'base_commit':
              'a18b4b0136d647529971e9fcb99fa83f5b9a0b81',
              'root_lines': len(lines), 'all_frames': len(frames),
              'weyl_frame_orbits': [len(p) for p in frame_orbit],
              'stabilizer_generators': len(gens),
              'p112_line_orbits': [len(p) for p in lines_orbits],
              'p112_frames': len(frames112), 'p104_orbits': orbit_records,
              'representative_profiles': profiles,
              'alternate_44_zero_exclusion':
              {'cnf': cnf_stats, 'cnf_sha256': cnf_digest,
               'proof_sha256': sha256(proof_bytes).hexdigest(),
               'rup': rup},
              'gauge_matrix_entries_checked': gauge_entries}
    if args.write:
        with args.write.open('x', encoding='utf-8') as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write('\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text()),
             'full receipt comparison')
    print('PASS_E8_RANK8_TRANSPORT_AUDIT frames=2025 stabilizer_generators=204 '
          'p112_frames=1260 p104_orbits=28,336,896 alt44=24 '
          f"RUP={rup['added_lemmas']} gluing="
          f"{profiles['alternate_44']['class_geometry']['cross_class_gluing_checks']}")


if __name__ == '__main__':
    main()

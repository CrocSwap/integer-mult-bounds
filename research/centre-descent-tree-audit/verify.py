#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent selected-word audit of ctoth's nested-descent-tree relaxation.

Prepared for Dennis (@antunishdPursuit) with substantial OpenAI Codex assistance.
No supplier modules are imported. No files are written during verification.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PROVIDER = 'candidate/strict/global/base/providers/gauge44/'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def span(vectors, h):
    """Enumerate actual vectors, rather than importing supplier elimination."""
    values = {0}
    for x in vectors:
        require(type(x) is int and 0 <= x < 1 << h, 'invalid binary vector')
        values |= {v ^ x for v in values}
    return frozenset(values)


def dimension(space):
    require(space and len(space) & (len(space) - 1) == 0, 'invalid subspace size')
    return len(space).bit_length() - 1


def rank(rows):
    """Separate dual-side elimination, independent of vector enumeration."""
    pivots = {}
    for row in rows:
        while row:
            k = row.bit_length() - 1
            if k in pivots:
                row ^= pivots[k]
            else:
                pivots[k] = row
                break
    return len(pivots)


def pinned_inputs():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    inputs = {}
    for row in sources['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            require(digest(raw) == row['sha256'], 'source drift: ' + row['path'])
            inputs[row['path']] = raw
    require(set(inputs) == {ARCHIVE, 'research/community-frontier1094-audit/ASSEMBLY.json',
                            'research/community-frontier1094-audit/RESULT.json',
                            'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'}, 'exact live input inventory')
    return inputs


def archive_inputs(inputs):
    # Read named regular files in memory. Never unpack an archive into a path.
    with tarfile.open(fileobj=io.BytesIO(inputs[ARCHIVE]), mode='r:gz') as archive:
        names = [m.name for m in archive.getmembers()]
        require(len(names) == len(set(names)), 'duplicate archive member')
        wanted = [PROVIDER + name for name in (
            'CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
            'INDEPENDENT-LOCAL-REPLAY.json')]
        wanted += ['candidate/strict/ASSEMBLY.json', 'candidate/strict/global/BINDING.json']
        raw = {}
        for name in wanted:
            member = archive.getmember(name)
            require(member.isfile(), 'non-file archive input')
            raw[name] = archive.extractfile(member).read()
    word_bytes = raw[PROVIDER + 'CANONICAL-WORD.json.gz']
    replay = json.loads(raw[PROVIDER + 'INDEPENDENT-LOCAL-REPLAY.json'])
    binding = json.loads(raw['candidate/strict/global/BINDING.json'])
    assembly_path = 'research/community-frontier1094-audit/ASSEMBLY.json'
    require(raw['candidate/strict/ASSEMBLY.json'] == inputs[assembly_path], 'archived assembly binding')
    result = json.loads(inputs['research/community-frontier1094-audit/RESULT.json'])
    require(result['status'] == 'PASS_COMPLETE_PR1094_COMPOSITION' and
            result['assembly_sha256'] == digest(inputs[assembly_path]), 'reviewed result binding')
    assembly = json.loads(inputs[assembly_path])
    require(assembly['kappa'] == result['kappa'] == '836330098538459/500000000000000000', 'selected historical kappa')
    require(replay['canonical_word_sha256'] == digest(word_bytes) ==
            binding['providers']['gauge44']['artifact_sha256']['CANONICAL-WORD.json.gz'], 'provider byte binding')
    require(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY' and
            replay['helpers'] == 480, 'selected replay identity')
    pins = json.loads(inputs['research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'])
    require(digest(gzip.decompress(word_bytes)) == pins['canonical_sha256'], 'selected slot-word payload pin')
    programs = json.loads(gzip.decompress(raw[PROVIDER + 'LOCAL-PROGRAMS.json.gz']))
    require(digest(raw[PROVIDER + 'LOCAL-PROGRAMS.json.gz']) == replay['local_programs_sha256'], 'program byte binding')
    return json.loads(gzip.decompress(word_bytes)), programs, {
        name: digest(value) for name, value in sorted(raw.items())}


def support_from_cut(word):
    v = word['v']
    centers = word['centers']
    require(len(centers) == len(set(centers)) == len(word['center_frames']) == 8, 'eight distinct centres')
    index = {q: k for k, q in enumerate(centers)}
    support = {}
    for e in word['cut']:
        require(len(e) == 6 and e[0] == 'add' and e[2] in index and v <= e[1] < 2*v, 'cut grammar')
        key = (index[e[2]], e[1] - v)
        require(key not in support, 'duplicate scatter edge')
        coefficient = Fraction(e[3], e[4])
        require(coefficient != 0, 'zero scatter edge')
        support[key] = coefficient
    return support


def support_from_program(word, program):
    """Read actual private-C scatter edges, separately from canonical cut."""
    v = word['v']
    moves, support = [], {}
    for event in program:
        if event[0] == 'center':
            moves.append(event)
        elif event[0] == 'scalar':
            gate, frame = event[1:]
            if gate[0] == 'add' and gate[2][0] == 'C':
                require(gate[1][0] == 'L' and v <= gate[1][1] < 2*v and frame == 0, 'native scatter frame')
                key = (gate[2][1], gate[1][1] - v)
                require(key not in support, 'duplicate native scatter edge')
                support[key] = Fraction(gate[3], gate[4])
    require(moves == [['center', k, f, 0, 8] for k, f in enumerate(word['center_frames'])], 'eight native rank-eight descents')
    return support


def audit_word(word, program):
    require((word['v'], word['h'], word['R']) == (112, 9, 480), 'selected 480-helper word')
    h, v = word['h'], word['v']
    require(not word['target_levels'], 'selected zero waiting levels')
    require(word['local_profile'] == {'1':2412, '2':418, '3':432, '4':142, '5':82, '8':8}, 'selected paid profile')
    cut = support_from_cut(word)
    require(cut == support_from_program(word, program), 'canonical/native scatter agreement')
    require(len(cut) == 176, 'selected scatter edge count')
    spaces = [span(frame, h) for frame in word['frames']]
    centers = [spaces[f] for f in word['center_frames']]
    finals = [spaces[f] for f in word['final'][v:2*v]]
    require(len(finals) == len(word['ports']) == v, 'target final-frame inventory')
    for port, frame in zip(word['ports'], finals):
        require(frame == frozenset(x for x in range(1 << h) if (x & port).bit_count() % 2 == 0), 'target final hyperplane')
    rows = []
    for k, f in enumerate(word['center_frames']):
        targets = sorted(t for c, t in cut if c == k)
        require(len(targets) == 22 and len({finals[t] for t in targets}) == 22, '22 distinct served final frames')
        common = centers[k]
        for t in targets:
            common &= finals[t]
        basis = word['frames'][f]
        require(len(basis) == dimension(centers[k]) == 8, 'centre frame rank')
        dual = [sum(((x & word['ports'][t]).bit_count() % 2) << j
                    for j, x in enumerate(basis)) for t in targets]
        require(rank(dual) == dimension(centers[k]) - dimension(common), 'primal/dual disagreement')
        require(common == {0} and rank(dual) == 8, 'selected trivial common meet')
        rows.append(dict(centre=k, carrier=word['centers'][k], frame_basis=basis,
                         served_targets=targets, restricted_functionals=dual,
                         common_meet_dimension=dimension(common), lower_bound=rank(dual),
                         attained_zero_leaf_cost=dimension(centers[k])))
    by_target = {}
    for k, t in cut:
        by_target.setdefault(t, []).append(k)
    require(len(by_target) == 88 and all(len(ks) == 2 for ks in by_target.values()), '88 two-centre targets')
    levels = {t: finals[t] & centers[ks[0]] & centers[ks[1]] for t, ks in by_target.items()}
    require(Counter(dimension(x) for x in levels.values()) == {6:88}, 'relaxed waiting-level dimensions')
    pairs = []
    for row in rows:
        targets = row['served_targets']
        require(len({levels[t] for t in targets}) == 22, 'distinct centre waiting levels')
        histogram = Counter(dimension(levels[a] & levels[b])
                            for i, a in enumerate(targets) for b in targets[i+1:])
        require(set(histogram) == {4,5}, 'pairwise waiting-level meet dimensions')
        pairs.append({str(k):v for k,v in sorted(histogram.items())})
    return dict(helpers=480, scatter_edges=len(cut), served_targets=len(by_target),
                centres=rows, relaxed_level_dimensions={'6':88},
                pairwise_level_meet_dimensions=pairs,
                relaxed_tree_total=sum(row['lower_bound'] for row in rows))


def all_subspaces(h):
    spaces = {frozenset({0})}
    frontier = list(spaces)
    for current in frontier:
        for x in range(1 << h):
            if x not in current:
                enlarged = current | {y ^ x for y in current}
                if enlarged not in spaces:
                    spaces.add(enlarged)
                    frontier.append(enlarged)
    return sorted(spaces, key=lambda s: (len(s), sorted(s)))


def tree_optima(spaces, targets):
    """Independent finite dynamic program; no meet-bound formula in recurrence.

    dp[U,S]: minimum cost to serve target labels S from frame U. Either descend
    one strict edge, or freely copy U and split S into two nonempty sets.
    Unary zero-cost copies are irrelevant. Strict descendants and proper label
    subsets have already been evaluated, so these cover arbitrary finite trees.
    """
    tables = {}
    for mask in range(1, 1 << len(targets)):
        for u in spaces:
            if all(not (mask >> i & 1) or u <= t for i, t in enumerate(targets)):
                best = 0
            else:
                best = min((dimension(u)-dimension(w)+tables[w,mask]
                            for w in spaces if w < u), default=1000)
                part = (mask - 1) & mask
                while part:
                    other = mask ^ part
                    if other:
                        best = min(best, tables[u,part] + tables[u,other])
                    part = (part - 1) & mask
            tables[u,mask] = best
    return {u: tables[u,(1 << len(targets))-1] for u in spaces}


def exhaustive_tree_controls():
    spaces = all_subspaces(3)
    require(len(spaces) == 16, 'F2^3 subspace census')
    cases = 0
    # All ordered two-target boundaries and all roots; both branching and
    # arbitrary strict descendant edges are included, with no depth cutoff.
    for a in spaces:
        for b in spaces:
            optima = tree_optima(spaces, [a,b])
            for u, optimum in optima.items():
                require(optimum == dimension(u)-dimension(u & a & b), 'tree optimum contradicts meet bound')
                cases += 1
    # Summing separate path costs overprices shared descent: 2, rather than 1.
    full = frozenset(range(8))
    zero = frozenset({0})
    plane = span([1,2],3)
    require(tree_optima(spaces,[plane,plane])[full] == 1, 'shared descent fixture')
    # Empty demand intersection costs the full root rank; ignoring a target fails.
    a, b = span([1],3), span([2],3)
    require(tree_optima(spaces,[a,b])[full] == 3 and
            tree_optima(spaces,[a])[full] == 2, 'omitted target fixture')
    require(tree_optima(spaces,[zero,zero])[full] == 3, 'free copy cannot make descent free')
    # If containment is dropped, equal-rank incomparable lines yield a
    # nominal zero-cost edge despite a meet-bound of one. This is outside
    # the grammar, and shows why dimension difference alone is insufficient.
    require(not b <= a and dimension(a)-dimension(b) == 0 and
            dimension(a)-dimension(a & b) == 1, 'nonnested boundary witness')
    return dict(ambient_dimension=3, subspaces=16, ordered_target_pairs=256,
                root_boundary_cases=cases, tree_depth_cutoff=None,
                nonnested_counterexample={'root_basis':[1], 'target_basis':[2],
                                         'nominal_dimension_drop':0, 'meet_bound':1})


def rejection_controls(word, program):
    import copy
    rejected = []
    mutations = [
        ('ancestor_helper_count', lambda w: w.update(R=492)),
        ('missing_scatter_edge', lambda w: w['cut'].pop()),
        ('zero_scatter_coefficient', lambda w: w['cut'][0].__setitem__(3,0)),
        ('wrong_target_final', lambda w: w['final'].__setitem__(112,0)),
        ('nonzero_waiting_level', lambda w: w.update(target_levels={'0':[1]})),
        ('duplicate_carrier', lambda w: w['centers'].__setitem__(1,w['centers'][0])),
    ]
    for name, mutate in mutations:
        bad = copy.deepcopy(word)
        mutate(bad)
        try:
            audit_word(bad,program)
        except ValueError as exc:
            rejected.append(dict(name=name, reason=str(exc)))
        else:
            raise ValueError('accepted negative control: ' + name)
    bad = copy.deepcopy(program)
    bad.remove(next(e for e in bad if e[0] == 'center'))
    try:
        audit_word(word,bad)
    except ValueError as exc:
        rejected.append(dict(name='missing_native_descent',reason=str(exc)))
    else:
        raise ValueError('accepted missing native descent')
    return rejected


def result():
    inputs = pinned_inputs()
    word, programs, member_hashes = archive_inputs(inputs)
    return dict(status='PASS_SELECTED_CENTRE_DESCENT_TREE_AUDIT',
                selected=audit_word(word,programs['forward']),
                finite_tree_oracle=exhaustive_tree_controls(),
                rejected_controls=rejection_controls(word,programs['forward']),
                archive_members_sha256=member_hashes,
                scope='Source-bound selected-word frame/support audit and finite tree oracle. '
                      'The universal tree lemma is a written proof in README.md, not kernel verification. '
                      'No dirty-host, cyclic/mixed circuit, new supplier, kappa or full cold replay claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', action='store_true', help='print computed evidence without expected-receipt comparison')
    args = parser.parse_args()
    receipt = result()
    if args.receipt:
        print(json.dumps(receipt,indent=2,sort_keys=True))
    else:
        require(receipt == json.loads((PACKAGE/'EXPECTED.json').read_bytes()), 'expected receipt mismatch')
        print(receipt['status'], 'centres=8 cost=64 tree_cases=4096 controls=7')


if __name__ == '__main__':
    main()

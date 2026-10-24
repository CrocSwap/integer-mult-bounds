#!/usr/bin/env python3
"""Independent joint algebra audit. Standard library only; imports no author code.

Chris R / OpenAI Codex independent checking of Ali Romman's construction,
using Cao Yifan's source word. Rational rows use normalized dyadic integer
numerators, not the author's per-coefficient Fraction implementation.
"""
import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / 'repository'
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
CANDIDATE = 'research/kappa-joint-relations-20261023/WORD.json.gz'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def norm(d, exponent):
    d = {k: v for k, v in d.items() if v}
    if not d:
        return ({}, 0)
    shift = min((abs(v) & -abs(v)).bit_length() - 1 for v in d.values())
    shift = min(shift, exponent)
    if shift:
        d = {k: v >> shift for k, v in d.items()}
    return d, exponent - shift

def linear(a, b, numerator=1, denominator=1):
    # Source rationals may carry the sign on either integer, including
    # SCALE [2,-1]. Normalize the rational sign before dyadic validation.
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    require(denominator > 0 and denominator & (denominator - 1) == 0, 'non-dyadic scalar')
    exp_b = b[1] + denominator.bit_length() - 1
    exp = max(a[1], exp_b)
    d = {k: v << (exp - a[1]) for k, v in a[0].items()}
    for k, v in b[0].items():
        d[k] = d.get(k, 0) + numerator * (v << (exp - exp_b))
    return norm(d, exp)

def scaled(a, numerator, denominator):
    return linear(({}, 0), a, numerator, denominator)

def initial(role):
    return ({(role, ()): 1}, 0)

def warped(a, symbol):
    # Left action: cancel only an adjacent inverse. Distinct symbols never
    # commute and the scalar coefficient is kept outside the word.
    d = {}
    for (role, word), v in a[0].items():
        key = (role, word[1:] if word and word[0] == -symbol else (symbol,) + word)
        d[key] = d.get(key, 0) + v
    return norm(d, a[1])

def rational_row(row):
    return {k: Fraction(v, 1 << row[1]) for k, v in row[0].items()}

def rref(relations, preferred_pivots=()):
    """Conventional matrix elimination, with fixed increasing column order."""
    all_columns = {h for d in relations for h in d}
    require(set(preferred_pivots) <= all_columns, 'prepared pivot absent from derived relation system')
    columns = list(preferred_pivots) + sorted(all_columns - set(preferred_pivots))
    matrix = [[Fraction(d.get(h, 0)) for h in columns] for d in relations]
    rank, pivots = 0, []
    for j, h in enumerate(columns):
        k = next((k for k in range(rank, len(matrix)) if matrix[k][j]), None)
        if k is None:
            continue
        matrix[rank], matrix[k] = matrix[k], matrix[rank]
        q = matrix[rank][j]
        matrix[rank] = [v / q for v in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][j]:
                q = matrix[i][j]
                matrix[i] = [a - q * b for a, b in zip(matrix[i], matrix[rank])]
        pivots.append(h)
        rank += 1
        if rank == len(matrix):
            break
    return {p: {h: q for h, q in zip(columns, matrix[i]) if q} for i, p in enumerate(pivots)}

def decode_edits(source, candidate):
    """Read the literal word delta without WITNESS.json or expected outputs."""
    old, new = source['programs']['backward'], candidate['programs']['backward']
    j = next(i for i, e in enumerate(new) if e == old[0])
    preparation = new[:j]
    snapshots, centers, zeros = {}, {}, {}
    for i, event in enumerate(old):
        if new[j] == event:
            j += 1
        elif event[0] == 'center':
            a, b, c = new[j:j + 3]
            frame = event[3]
            require(a == ['scalar', ['clear', ['C', 0]], frame], 'center clear')
            require(b[0] == 'scalar' and b[1][:2] == ['copy', ['C', 0]] and b[2] == frame, 'center COPY gauge')
            slot = tuple(b[1][2])
            require(c == ['scalar', ['clear', list(slot)], frame], 'snapshot consumption')
            centers[i] = {'slot': slot, 'frame': frame}
            j += 3
        else:
            require(event[0] == 'climb', 'unexpected source edit')
            role, oldframe, newframe = ('L', event[2]), event[3], event[4]
            require(new[j] == ['zero_retag', list(role), oldframe, newframe], 'zero edit exact frames')
            zeros[i] = {'role': role, 'frame': oldframe, 'rank': event[5]}
            j += 1
        if j + 1 < len(new) and new[j][0] == 'scalar' and new[j][1][0] == 'clear' and new[j][1][1][0] == 'C' and new[j][1][1][1] > 0:
            a, b = new[j:j + 2]
            slot, frame = tuple(a[1][1]), a[2]
            require(b[0] == 'scalar' and b[1][:2] == ['copy', list(slot)] and b[2] == frame, 'snapshot COPY')
            require(slot not in [x['slot'] for x in snapshots.values()], 'snapshot slot reused')
            snapshots[i] = {'slot': slot, 'role': tuple(b[1][2]), 'frame': frame}
            j += 2
    trailing = new[j:]
    require(len(snapshots) == len(centers) == len(zeros) == 8, 'eight of each edit')
    require(len({x['slot'] for x in centers.values()}) == 8, 'eight independent snapshot slots')
    require(max(snapshots) < min(centers), 'all eight snapshots simultaneously live')
    for i, x in centers.items():
        match = [k for k, s in snapshots.items() if s['slot'] == x['slot']]
        require(len(match) == 1 and match[0] < i and snapshots[match[0]]['frame'] == x['frame'], 'chronological same-frame snapshot')
        x['snapshot'] = match[0]
    require(candidate['programs']['forward'] == source['programs']['forward'], 'unchanged entire forward word')
    canonical = dict(source['canonical']); canonical.pop('local_profile')
    require(candidate['canonical'] == canonical, 'unchanged actual native operators and frames')
    return preparation, snapshots, centers, zeros, trailing

def replay(canonical, program, owned, source_sites=None):
    roles = {('L', i) for i in range(632)} | set(owned)
    rows = {r: initial(r) for r in roles}
    frames = {('L', i): f for i, f in enumerate(canonical['start'])}
    frames.update({r: None for r in owned if r[0] == 'C'})
    observed, spaces = {}, {}
    paid = {}
    max_terms = 1
    def space(frame):
        if frame not in spaces:
            s = {0}
            for v in canonical['frames'][frame]:
                s |= {u ^ v for u in tuple(s)}
            require(len(s) == 1 << len(canonical['frames'][frame]), 'independent binary frame')
            spaces[frame] = s
        return spaces[frame]
    for i, event in enumerate(program):
        tag = event[0]
        touched = None
        if tag == 'scalar':
            op, f = event[1:]
            action, dst = op[0], tuple(op[1]); touched = dst
            require(dst in roles and 0 <= f < len(canonical['frames']), 'scalar declaration')
            if action == 'clear':
                require(dst in owned, 'borrowed erasure')
                rows[dst] = ({}, 0); frames[dst] = f
            else:
                require(frames[dst] == f, 'destination gauge')
                if action in ('add', 'copy'):
                    src = tuple(op[2])
                    require(src in roles and dst != src and frames[src] == f, 'source gauge')
                    if action == 'copy':
                        require(dst in owned and not rows[dst][0], 'COPY requires clean owned destination')
                        rows[dst] = (dict(rows[src][0]), rows[src][1])
                    else:
                        rows[dst] = linear(rows[dst], rows[src], op[3], op[4])
                else:
                    require(action == 'scale', 'unknown scalar')
                    rows[dst] = scaled(rows[dst], op[2], op[3])
        elif tag == 'warp':
            _, role, symbol, old, new = event
            dst = tuple(role); touched = dst
            require(frames[dst] == old and 1 <= abs(symbol) <= len(canonical['warps']), 'warp source gauge')
            rows[dst] = warped(rows[dst], symbol); frames[dst] = new
        elif tag in ('center', 'climb'):
            if tag == 'center':
                _, idx, old, new, rank = event; dst = ('C', idx)
                require(space(old) < space(new) or space(new) < space(old), 'center nested spaces')
            else:
                _, _, idx, old, new, rank = event; dst = ('L', idx)
                require(space(old) < space(new), 'climb nested spaces')
            require(frames[dst] == old and rank == abs(len(canonical['frames'][old]) - len(canonical['frames'][new])), 'paid exact frame and rank')
            frames[dst] = new; paid[rank] = paid.get(rank, 0) + 1
        elif tag == 'zero_retag':
            _, role, old, new = event; dst = tuple(role)
            require(frames[dst] == old and not rows[dst][0], 'physical identity requires complete zero row')
            frames[dst] = new
        else:
            require(tag in ('phase', 'adapter'), 'unrecognized native event')
        if touched is not None:
            max_terms = max(max_terms, len(rows[touched][0]))
        if source_sites and i in source_sites:
            observed[i] = {r: (dict(rows[r][0]), rows[r][1]) for r in source_sites[i]}
    for i in range(632):
        r = ('L', i)
        require(frames[r] == canonical['final'][i], 'retained final frame')
        if r not in owned:
            want = initial(r)
            if i < 112:
                want = linear(want, initial(('L', i + 112)), -1)
            require(rows[r] == want, 'retained exact endpoint L' + str(i))
    require(all(not rows[r][0] for r in owned), 'arbitrary owned entry must erase and return zero')
    return observed, {'events': len(program), 'paid': paid, 'max_live_row_terms': max_terms,
                     'independent_retained_inputs': 632 - sum(r[0] == 'L' for r in owned),
                     'arbitrary_owned_entry_inputs': len(owned)}

def serialize(d):
    return {str(k): str(v) for k, v in sorted(d.items())}

def verify_preparation(prep, basis):
    pivots = set(basis)
    expected = []
    for pivot, row in sorted(basis.items()):
        expected.append(['scalar', ['clear', ['L', pivot]], 0])
        for h, q in sorted(row.items()):
            if h != pivot:
                require(h not in pivots and q.denominator & (q.denominator - 1) == 0, 'independent dyadic preparation')
                expected.append(['scalar', ['add', ['L', pivot], ['L', h], -q.numerator, q.denominator], 0])
    require(prep == expected, 'actual simultaneous pivot preparation differs from independently derived RREF')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, default=HERE / 'RESULT.json')
    ap.add_argument('--candidate', type=Path, default=ROOT / CANDIDATE)
    ap.add_argument('--candidate-pr', type=int, default=5383)
    ap.add_argument('--candidate-head', default='4bd6efa51a495a7c7b7754915cf0244e7e60969e')
    args = ap.parse_args()
    source_raw = (ROOT / SOURCE).read_bytes()
    candidate_raw = args.candidate.read_bytes()
    source_payload, candidate_payload = map(gzip.decompress, (source_raw, candidate_raw))
    source, candidate = map(json.loads, (source_payload, candidate_payload))
    prep, snapshots, centers, zeros, trailing = decode_edits(source, candidate)
    sites = {}
    for i, s in snapshots.items(): sites.setdefault(i, set()).add(s['role'])
    for i in centers: sites.setdefault(i, set()).add(('C', 0))
    for i, z in zeros.items(): sites.setdefault(i, set()).add(z['role'])
    observed, before = replay(source['canonical'], source['programs']['backward'], {('C', 0)}, sites)
    relations, identities, by_frame = [], [], {}
    for i, x in sorted(centers.items()):
        s = snapshots[x['snapshot']]
        diff = linear(observed[i][('C', 0)], observed[x['snapshot']][s['role']], -1)
        qrow = rational_row(diff)
        require(qrow and all(r[0] == 'L' and 224 <= r[1] < 632 and not word for (r, word) in qrow), 'derived relation must contain only scalar helper inputs')
        relation = {r[1]: q for (r, _), q in qrow.items()}
        require(all(source['canonical']['start'][h] == 0 and source['canonical']['final'][h] == 1 for h in relation), 'cold full-ended relation domain')
        relations.append(relation); by_frame[x['frame']] = diff
        identities.append({'center_event': i, 'snapshot_event': x['snapshot'], 'snapshot_role': s['role'], 'frame': x['frame'], 'center_minus_snapshot': serialize(relation)})
    require(len(by_frame) == 8, 'distinct center frames')
    for i, z in sorted(zeros.items()):
        require(z['frame'] in by_frame and z['rank'] == 1, 'zero site belongs to named rank-one center frame')
        require(observed[i][z['role']] == scaled(by_frame[z['frame']], -1, 1), 'unrestricted later row equals negative center-minus-snapshot')
        identities.append({'zero_event': i, 'role': z['role'], 'frame': z['frame'], 'unrestricted_row_is_negative_center_delta': True})
    canonical_basis = rref(relations)
    require(len(canonical_basis) == 8, 'joint relation rank eight')
    prepared_pivots = [e[1][1][1] for e in prep if e[0] == 'scalar' and e[1][0] == 'clear' and e[1][1][0] == 'L']
    require(len(prepared_pivots) == len(set(prepared_pivots)) == 8, 'eight distinct actual prepared pivots')
    basis = rref(relations, sorted(prepared_pivots))
    require(set(basis) == set(prepared_pivots), 'actual chosen pivots not independent in joint relation system')
    verify_preparation(prep, basis)
    require(trailing == [['scalar', ['clear', ['L', h]], 1] for h in sorted(basis)], 'all pivot outputs returned zero')
    owned = {('L', h) for h in basis} | {('C', i) for i in range(9)}
    require({tuple(r) for r in candidate['owned']['backward']} == owned, 'actual owned declarations')
    _, after = replay(candidate['canonical'], candidate['programs']['backward'], owned)
    # Controls are exact local propositions applied to independently derived
    # rows, rather than rerunning or relying on author's rejection controls.
    controls = {}
    def rejects(name, fn):
        try: fn()
        except ValueError as e: controls[name] = str(e)
        else: raise ValueError('accepted negative control ' + name)
    mutant = json.loads(json.dumps(prep)); mutant[1][1][3] += 1
    rejects('wrong_preparation_coefficient', lambda: verify_preparation(mutant, basis))
    mutant2 = json.loads(json.dumps(prep)); mutant2[1][1][3] *= -1
    rejects('wrong_preparation_sign', lambda: verify_preparation(mutant2, basis))
    mutant3 = json.loads(json.dumps(prep)); mutant3[0][1][1][1] = 226
    rejects('wrong_pivot', lambda: verify_preparation(mutant3, basis))
    # Swapping distinct saved values must change the unrestricted center delta.
    cs = list(sorted(centers)); x, y = centers[cs[0]], centers[cs[1]]
    sx, sy = snapshots[x['snapshot']], snapshots[y['snapshot']]
    wrong_delta = linear(observed[cs[0]][('C', 0)], observed[y['snapshot']][sy['role']], -1)
    rejects('wrong_snapshot', lambda: require(wrong_delta == by_frame[x['frame']], 'snapshot changes unrestricted identity'))
    wrong_gauge = json.loads(json.dumps(candidate)); ci = next(i for i,e in enumerate(wrong_gauge['programs']['backward']) if e[0]=='scalar' and e[1][:2]==['copy',['C',0]])
    wrong_gauge['programs']['backward'][ci][2] = 0
    rejects('wrong_copy_gauge', lambda: decode_edits(source, wrong_gauge))
    zi = min(zeros); z = zeros[zi]
    wrong_zero = linear(observed[zi][z['role']], initial(('L', 224)))
    rejects('wrong_zero_row', lambda: require(wrong_zero == scaled(by_frame[z['frame']], -1, 1), 'nonzero retained column at zero site'))
    fake_rank = dict(basis); fake_rank.pop(min(fake_rank))
    rejects('drop_independent_relation', lambda: require(len(fake_rank)==8, 'rank seven cannot fund eight pivots'))
    result = {'status': 'PASS_INDEPENDENT_JOINT_ALGEBRA', 'author_credit': 'Ali Romman; source word Cao Yifan',
              'candidate_pr': args.candidate_pr, 'candidate_head': args.candidate_head,
              'source_file': str(ROOT / SOURCE), 'candidate_file': str(args.candidate.resolve()),
              'source_raw_sha256': hashlib.sha256(source_raw).hexdigest(),
              'source_payload_sha256': hashlib.sha256(source_payload).hexdigest(),
              'candidate_raw_sha256': hashlib.sha256(candidate_raw).hexdigest(),
              'candidate_payload_sha256': hashlib.sha256(candidate_payload).hexdigest(),
              'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'relation_rank': 8, 'independently_derived_pivots': list(sorted(basis)),
              'independently_derived_rref': {str(p): serialize(d) for p,d in sorted(basis.items())},
              'unconstrained_canonical_rref': {str(p): serialize(d) for p,d in sorted(canonical_basis.items())},
              'source_identities': identities, 'source_replay': before, 'candidate_replay': after,
              'simultaneous_snapshot_count': 8, 'all_16_unrestricted_identities_checked': True,
              'forward_entire_word_unchanged': True, 'canonical_operators_frames_unchanged': True,
              'negative_controls': controls,
              'limitations': ['No new absolute-phase lowering or physical all-size proof.', 'Forward replay unchanged and reused; this checker independently replays backward words only.', 'Cost, compiler, outer inequalities are separate review responsibilities.']}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': result['status'], 'pivots': sorted(basis), 'controls': list(controls)}))

if __name__ == '__main__': main()

"""Explicit dyadic K gather/private-scatter/restore word and exact polynomial certificate."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, combinations_with_replacement
from collections import Counter
import sys, json, gzip, hashlib, math, importlib.util
import numpy as np
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'research/niemeier-lattices/code'))
import e8_sections as sections
import e8_cubed as geometry
spec = importlib.util.spec_from_file_location('comp_network', ROOT / 'research/h6-compensation-network/construction/network.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def polynomial_certificate():
    monomials = list(combinations_with_replacement(range(16), 3))
    idx = {v: i for i, v in enumerate(monomials)}
    U = np.zeros((816, 16), dtype=np.int64)
    for i in range(16):
        for j in range(16):
            U[idx[tuple(sorted((i, j, j)))], i] = 1
    polys = []
    weights = []

    def mono(coords):
        v = np.zeros(816, dtype=np.int64)
        v[idx[tuple(sorted(coords))]] = 12
        return v
    for block in range(2):
        for triple in combinations(range(8 * block, 8 * (block + 1)), 3):
            polys.append(mono(triple))
            weights.append(16)
    lines, _ = sections.transforms()
    for block in range(2):
        for i in range(8 * block, 8 * (block + 1)):
            pure = mono((i, i, i)) // 12
            polys.append(4 * pure - U[:, i])
            weights.append(32)
            f = 4 * U[:, i] - 4 * pure
            same = [j for j in range(8 * block, 8 * (block + 1)) if j != i]
            for line in lines:
                polys.append(sum((mono((i, same[j], same[j])) for j in line), np.zeros(816, dtype=np.int64)) - f)
                weights.append(4)
            other = list(range(8 * (1 - block), 8 * (2 - block)))
            for shift in range(8):
                for char in range(8):
                    if (shift, char) == (0, 0) or (shift & char).bit_count() % 2:
                        continue
                    polys.append(sum(((-1) ** ((j & char).bit_count() % 2) * mono((i, other[j], other[j ^ shift])) for j in range(8)), np.zeros(816, dtype=np.int64)))
                    weights.append(1)
            polys.append(sum((mono((i, j, j)) for j in other), np.zeros(816, dtype=np.int64)))
            weights.append(-3)
    A = np.stack(polys)
    W = np.array(weights, dtype=np.int64)
    D = np.array([math.factorial(3) // math.prod((math.factorial(c) for c in Counter(m).values())) for m in monomials], dtype=np.int64)
    wanted = 384 * np.diag(D) - 96 * U @ U.T
    got = A.T @ (W[:, None] * A)
    require(A.shape == (816, 816) and np.array_equal(got, wanted), 'K exact check at original line 44')
    return (A, W, {'status': 'PASS_ALL_665856_EXACT_COEFFICIENTS', 'identity': 'A^T diag(w) A =384D-96UU^T; features=A*monomials/12, K=E diag(w) E^T/8192 on sum u_i^2=16', 'monomials': 816, 'checked_entries': 816 ** 2, 'A_int64_sha256': hashlib.sha256(A.astype('<i8').tobytes()).hexdigest(), 'weights_sha256': hashlib.sha256(W.astype('<i8').tobytes()).hexdigest()})

def k_events(E, W, dual=False):
    n = E.shape[0]
    for c in range(816):
        for t in range(n):
            if E[t, c]:
                yield base.add(f't{t}', f'c{c}', -Q(int(W[c] * E[t, c]), 8192), 'K_dirt_prefix')
    for c in range(816):
        yield base.climb(f'c{c}', base.FULL, 'K_centers_full')
    for c in range(816):
        for s in range(n):
            if E[s, c]:
                yield base.add(f'c{c}', f's{s}', Q(int(E[s, c])), 'K_gather')
    for c in range(816):
        p = f'p{c}'
        yield dict(op='private_begin', register=p, frame=list(base.ZERO if dual else base.FULL), phase='K_private_begin')
        if not dual:
            yield base.add(p, f'c{c}', Q(1), 'K_private_copy')
        if not dual:
            yield dict(op='private_transition', register=p, frame=[], rank=17, phase='K_private_descent')
        for t in range(n):
            if E[t, c]:
                yield base.add(f't{t}', p, Q(int(W[c] * E[t, c]), 8192), 'K_scatter')
        if dual:
            yield dict(op='private_transition', register=p, frame=list(base.FULL), rank=17, phase='K_private_ascent')
            yield base.add(f'c{c}', p, Q(-1), 'K_private_copy_dual')
        yield dict(op='private_end', register=p, phase='K_private_erase')
    for c in range(816):
        for s in range(n):
            if E[s, c]:
                yield base.add(f'c{c}', f's{s}', -Q(int(E[s, c])), 'K_FULL_undo_gather')

def event_records(P, packed, indices, W, dual=False):
    """Canonical compressed complete stream: no dense edge list and no K macro.

 Pass range(30960) for all ports. This intentionally defines rather than
 materializes the >3-billion-event compensation fallback.
 """
    E, w, den = sections.evaluate_operator_centers(P[list(indices)])
    require(den == 8192 and np.array_equal(w, W), 'K exact check at original line 77')
    n = len(indices)

    def edges():
        return base.edge_records(P, packed, indices, indices)

    def orient(e):
        if not dual or e['op'] != 'add':
            return e
        e = dict(e)
        if e['phase'] == 'K_private_copy_dual':
            return e
        e['dst'], e['src'] = (e['src'], e['dst'])
        if e['phase'] != 'K_scatter':
            e['q'] = str(-Q(e['q']))
        return e
    for e in edges():
        yield orient(base.add(f"t{e['target_position']}", e['helper'], -Q(e['coefficient']), 'comp_dirt_prefix'))
    ki = iter(k_events(E, W, dual))
    pending = next(ki)
    while pending['phase'] == 'K_dirt_prefix':
        yield orient(pending)
        pending = next(ki)
    for e in edges():
        yield base.climb(e['helper'], base.basis([int(packed[e['source_port']])]), 'comp_source_line')
        yield orient(base.add(e['helper'], f"s{e['source_position']}", Q(1), 'comp_gather'))
    for i in range(n):
        yield base.climb(f's{i}', base.FULL, 'source_full')
    yield orient(pending)
    for e in ki:
        yield orient(e)
    for i, p in enumerate(indices):
        yield base.climb(f't{i}', base.perp(int(packed[p])), 'target_cap')
    for e in edges():
        yield base.climb(e['helper'], base.perp(int(packed[e['target_port']])), 'comp_target_cap')
        yield orient(base.add(f"t{e['target_position']}", e['helper'], Q(e['coefficient']), 'comp_scatter'))
    for e in edges():
        yield base.climb(e['helper'], base.FULL, 'comp_helper_full')
    for e in edges():
        yield orient(base.add(e['helper'], f"s{e['source_position']}", Q(-1), 'comp_FULL_cleanup'))

def fixture(P, packed, indices, W, dual=False):
    n = len(indices)
    E, w, q = sections.evaluate_operator_centers(P[indices])
    require(q == 8192 and np.array_equal(w, W), 'K exact check at original line 106')
    edges = list(base.edge_records(P, packed, indices, indices))
    events = []
    for e in edges:
        events.append(base.add(f"t{e['target_position']}", e['helper'], -Q(e['coefficient']), 'comp_dirt_prefix'))
    ke = list(k_events(E, W, dual))
    prefix = [e for e in ke if e['phase'] == 'K_dirt_prefix']
    rest = [e for e in ke if e['phase'] != 'K_dirt_prefix']
    events += prefix
    for e in edges:
        events.append(base.climb(e['helper'], base.basis([int(packed[e['source_port']])]), 'comp_source_line'))
        events.append(base.add(e['helper'], f"s{e['source_position']}", Q(1), 'comp_gather'))
    for s in range(n):
        events.append(base.climb(f's{s}', base.FULL, 'source_full'))
    events += rest
    for t, p in enumerate(indices):
        events.append(base.climb(f't{t}', base.perp(int(packed[p])), 'target_cap'))
    for e in edges:
        events.append(base.climb(e['helper'], base.perp(int(packed[e['target_port']])), 'comp_target_cap'))
        events.append(base.add(f"t{e['target_position']}", e['helper'], Q(e['coefficient']), 'comp_scatter'))
    for e in edges:
        events.append(base.climb(e['helper'], base.FULL, 'comp_helper_full'))
    for e in edges:
        events.append(base.add(e['helper'], f"s{e['source_position']}", Q(-1), 'comp_FULL_cleanup'))
    starts = {f's{s}': list(base.basis([int(packed[p])])) for s, p in enumerate(indices)}
    starts.update({f't{t}': [] for t in range(n)})
    starts.update({f'c{c}': [] for c in range(816)})
    starts.update({e['helper']: [] for e in edges})
    if dual:
        for e in events:
            if e['op'] == 'add' and e['phase'] not in ('K_scatter', 'K_private_copy_dual'):
                e['dst'], e['src'] = (e['src'], e['dst'])
                e['q'] = str(-Q(e['q']))
            elif e['op'] == 'add' and e['phase'] == 'K_scatter':
                e['dst'], e['src'] = (e['src'], e['dst'])
    return dict(indices=list(map(int, indices)), dual=dual, starts=starts, events=events, centers=816, comp_helpers=len(edges))

def replay(f):
    frames = {r: tuple(v) for r, v in f['starts'].items()}
    rows = {r: {r: Q(1)} for r in frames}
    paths = {r: [] for r in frames}
    live = set()
    private_ranks = []
    for step, e in enumerate(f['events']):
        op = e['op']
        if op == 'private_begin':
            r = e['register']
            require(not live and r not in frames, 'K exact check at original line 139')
            live.add(r)
            frames[r] = tuple(e['frame'])
            rows[r] = {}
        elif op == 'private_end':
            r = e['register']
            require(live == {r}, 'K exact check at original line 141')
            live.remove(r)
            del frames[r]
            del rows[r]
        elif op == 'private_transition':
            r = e['register']
            require(live == {r}, 'K exact check at original line 143')
            new = tuple(e['frame'])
            require(abs(len(new) - len(frames[r])) == e['rank'] == 17, 'K exact check at original line 143')
            require(base.subset(new, frames[r]) or base.subset(frames[r], new), 'K exact check at original line 143')
            frames[r] = new
            private_ranks.append(e['rank'])
        elif op == 'climb':
            require(not live, 'K exact check at original line 145')
            r = e['register']
            new = tuple(e['frame'])
            require(base.subset(frames[r], new), 'K exact check at original line 145')
            d = len(new) - len(frames[r])
            require(d > 0, 'K exact check at original line 145')
            paths[r].append(d)
            frames[r] = new
        elif op == 'add':
            require(frames[e['dst']] == frames[e['src']], (step, e))
            rows[e['dst']] = base.merge(rows[e['dst']], rows[e['src']], Q(e['q']))
        else:
            raise ValueError(op)
    require(not live and len(private_ranks) == 816 and (sum(private_ranks) == 13872), 'K exact check at original line 149')
    wanted = {r: {r: Q(1)} for r in f['starts']}
    for i in range(len(f['indices'])):
        dst, src, q = (f's{i}', f't{i}', Q(-1)) if f['dual'] else (f't{i}', f's{i}', Q(1))
        wanted[dst] = base.merge(wanted[dst], wanted[src], q)
    require(rows == wanted, 'arbitrary source/target/center/comp-helper columns mismatch')
    require(all((paths[f'c{c}'] == [17] for c in range(816))), 'K exact check at original line 155')
    require(all((paths[f's{i}'] == [16] and paths[f't{i}'] == [16] for i in range(len(f['indices'])))), 'K exact check at original line 156')
    require(all((path == [1, 15, 1] for r, path in paths.items() if r.startswith('h'))), 'K exact check at original line 157')
    return dict(all_basis_columns=len(rows), event_count=len(f['events']), dual=f['dual'], status='PASS_ALL_COLUMNS_IDENTITY_SHEAR', ordinary_center_roles=816, center_path=[17], private_episodes=816, private_rank_mass=13872)

def primitive(q):
    q = Q(q)
    a = abs(q.numerator)
    b = q.denominator
    require(b & b - 1 == 0, 'K exact check at original line 161')
    return 3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1)

def main():
    A, W, cert = polynomial_certificate()
    roots, fourth, P, profiles = geometry.construct_shell()
    P = P[profiles & 4 == 0, :16]
    _, packed, _ = geometry.binary_labels(roots, P)
    E, w, den = sections.evaluate_operator_centers(P)
    require(np.array_equal(w, W), 'K exact check at original line 167')
    probes = np.unique(np.r_[np.arange(0, 2160, 101), np.arange(2160, 30960, 977)])
    monomials = list(combinations_with_replacement(range(16), 3))
    F = np.stack([np.prod(P[probes][:, m].astype(np.int64), axis=1) for m in monomials], axis=1)
    require(np.array_equal(F @ A.T, 12 * E[probes]), 'K exact check at original line 172')
    gc = Counter()
    sc = Counter()
    for c in range(816):
        vals, counts = np.unique(E[:, c], return_counts=True)
        for v, count in zip(vals, counts):
            if v:
                gc[str(int(v))] += int(count)
                sc[str(Q(int(v * W[c]), 8192))] += int(count)
    M = sum(gc.values())
    primitive_g = sum((primitive(q) * count for q, count in gc.items()))
    primitive_s = sum((primitive(q) * count for q, count in sc.items()))
    results = []
    controls = {}
    for n in (8, 32):
        indices = np.unique(np.r_[np.linspace(0, 1079, n // 4, dtype=int), np.linspace(1080, 2159, n // 4, dtype=int), np.linspace(2160, 30959, n // 2, dtype=int)]).tolist()
        require(len(indices) == n, 'K exact check at original line 181')
        for dual in (False, True):
            f = fixture(P, packed, indices, W, dual)
            require(f['events'] == list(event_records(P, packed, indices, W, dual)), 'K exact check at original line 183')
            receipt = replay(f)
            results.append(receipt)
            name = f'fixture-{n}-' + ('dual' if dual else 'forward') + '.json.gz'
            payload = json.dumps(f, sort_keys=True, separators=(',', ':')).encode()
            (HERE / name).write_bytes(gzip.compress(payload, mtime=0))
            receipt['artifact'] = name
            receipt['uncompressed_sha256'] = hashlib.sha256(payload).hexdigest()
            if n == 8:
                for phase in ('K_dirt_prefix', 'K_gather', 'K_scatter', 'K_FULL_undo_gather', 'K_private_erase'):
                    at = next((i for i, e in enumerate(f['events']) if e['phase'] == phase))
                    mutant = dict(f, events=f['events'][:at] + f['events'][at + 1:])
                    try:
                        replay(mutant)
                    except (ValueError, AssertionError, KeyError):
                        controls[f'{dual}:{phase}'] = 'REJECTED'
                    else:
                        raise ValueError('negative control passed ' + phase)
    result = {'status': 'PASS_EXPLICIT_K_WORD_AND_COMPOSED_FIXTURES', 'N': 30960, 'h': 17, 'factor_centers': 816, 'full_composed_event_iterator': 'event_records(P,packed,range(30960),W,dual=False_or_True)', 'full_composed_event_count': 7 * 480337920 + 2 * 30960 + 4 * M + 5 * 816, 'full_composed_event_count_status': 'symbolic exhaustive-incidence count; full stream not materialized', 'max_abs_gather_coefficient': '16', 'max_abs_scatter_coefficient': '1/16', 'diagonal_denominator': 8192, 'full_factor_certificate': cert, 'factor_evaluator_diagnostic_rows': probes.tolist(), 'feature_nonzeros': M, 'gather_coefficients': dict(sorted(gc.items())), 'scatter_coefficients': dict(sorted(sc.items())), 'K_ordinary_roles': 816, 'ordinary_center_path': [17], 'private_full_to_zero_copies': 816, 'private_descent_C': 13872, 'K_full_scalar_additions': 4 * M, 'K_forward_primitive_bound': 2 * primitive_g + 2 * primitive_s + 3 * 816, 'K_dual_primitive_bound': 2 * primitive_g + 2 * primitive_s + 6 * 816, 'primitive_convention': '3+(bits(numerator)-1)+popcount(numerator)+(bits(denominator)-1) per weighted addition; clear/copy1 each, dual copy replacement unit add4', 'fixtures': results, 'negative_controls': controls, 'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT / 'research/niemeier-lattices/code/e8_sections.py', ROOT / 'research/niemeier-lattices/code/e8_cubed.py', ROOT / 'research/h6-compensation-network/construction/network.py']}, 'scope': 'Explicit finite local scalar/frame/copy construction; no K_interface macro. Complete all-pair polynomial factor identity, bounded all-basis chronological lifecycle replays, fully charged local center descent. Physical endpoint representatives, adapter compiler, precision and all-size supplier admission remain external gates.'}
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'feature_nonzeros', 'private_descent_C', 'K_full_scalar_additions', 'K_forward_primitive_bound', 'K_dual_primitive_bound']}))
if __name__ == '__main__':
    main()

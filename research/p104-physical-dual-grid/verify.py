"""Source-bound caller-grid audit; imports no predecessor executable.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import physical

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    """Authenticate data/definition bytes before parsing; never execute them."""
    pins = json.loads((PACKAGE / 'DEPENDENCY.json').read_text())
    for item in pins['files']:
        raw = (PACKAGE / item['local']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'dependency SHA256')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == item['git_blob'], 'dependency Git blob')
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage'] == 'input':
            raw = (ROOT / item['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'chart-definition SHA256')
    return json.loads((PACKAGE / 'WORD.json').read_text())


def span(vectors):
    """Literal subspace enumeration, separate from predecessor elimination."""
    out = {0}
    for value in vectors:
        require(type(value) is int and 0 < value < 512, 'binary frame vector')
        require(value not in out, 'independent frame basis')
        out |= {x ^ value for x in out}
    return frozenset(out)


def v2(value):
    """2-adic valuation, including numerator powers, of a nonzero rational."""
    require(value != 0, 'nonzero coefficient')
    d = value.denominator
    require(d & (d - 1) == 0, 'dyadic coefficient')
    n = abs(value.numerator)
    return (n & -n).bit_length() - 1 - (d.bit_length() - 1)


def reverse_row(program, cut, role, inputs):
    """Separate reverse functional, without frames or forward row operations."""
    weights = {role: Q(1)}
    for event in reversed(program[:cut]):
        kind, target = event[:2]
        if kind == 'add':
            source, factor = event[2], Q(event[3])
            weights[source] = weights.get(source, Q(0)) + factor * weights.get(target, Q(0))
        elif kind == 'sign':
            weights[target] = -weights.get(target, Q(0))
        elif kind == 'zero':
            weights.pop(target, None)
        elif kind == 'erase':
            require(not weights.get(target, 0), 'reverse private lifetime')
        else:
            require(kind == 'transport', 'reverse event type')
    return {r: a for r, a in weights.items() if r in inputs and a}


def replay(word):
    require(word['chart'] == 'Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)', 'canonical dual chart')
    initial = word['initial_frames']
    names = list(initial)
    require(len(names) == 358 and set(names) == set(word['final_frames']), 'public roles')
    initial_dim = {r: len(f) for r, f in initial.items()}
    spaces = {}

    def frame(f):
        key = tuple(f)
        if key not in spaces:
            spaces[key] = span(f)
        return spaces[key]

    frames = {r: frame(f) for r, f in initial.items()}
    rows = {r: {r: Q(1)} for r in names}
    counts, profile = Counter(), Counter()
    forms, witnesses = {}, {}
    max_l1, l1_witness, max_denominator = Q(0), None, 1
    boundaries, nonzero_terms, erases = 0, 0, []

    def observe(cut, role):
        nonlocal max_l1, l1_witness, max_denominator, boundaries, nonzero_terms
        boundaries += 1
        row = rows[role]
        nonzero_terms += len(row)
        norm = sum(map(abs, row.values()), Q(0))
        if norm > max_l1:
            max_l1, l1_witness = norm, (cut, role, dict(row))
        current_dim = len(frames[role]).bit_length() - 1
        for source, coefficient in row.items():
            a, b = current_dim + initial_dim[source], -v2(coefficient)
            max_denominator = max(max_denominator, coefficient.denominator)
            if a not in forms or b > forms[a]:
                forms[a] = b
                witnesses[a] = (cut, role, source, str(coefficient))

    for r in names:
        observe(0, r)
    for cut, event in enumerate(word['program'], 1):
        kind, target = event[:2]
        counts[kind] += 1
        if kind == 'transport':
            _, _, old, new, rank = event
            a, b = frame(old), frame(new)
            require(frames[target] == a, 'transport entry frame')
            require(a < b or b < a, 'strict nested transport')
            require(type(rank) is int and rank == abs(len(new) - len(old)), 'transport rank')
            profile[rank] += 1
            frames[target] = b
        elif kind == 'add':
            _, _, source, scalar, f = event
            require(target != source and frames[target] == frames[source] == frame(f), 'ADD common frame')
            scalar = Q(scalar)
            v2(scalar)
            update = dict(rows[target])
            for r, a in rows[source].items():
                update[r] = update.get(r, Q(0)) + scalar * a
                if not update[r]:
                    del update[r]
            rows[target] = update
        elif kind == 'sign':
            require(event[2] == '-1' and frames[target] == frame(event[3]), 'sign contract')
            rows[target] = {r: -a for r, a in rows[target].items()}
        elif kind == 'zero':
            require(target not in rows and target == 'C', 'fresh owned zero')
            rows[target], frames[target] = {}, frame(event[2])
        elif kind == 'erase':
            require(target == 'C' and not rows[target] and frames[target] == frame(event[2]), 'strict ideal zero erase')
            erases.append(cut)
            del rows[target], frames[target]
            continue
        else:
            raise ValueError('unknown event')
        observe(cut, target)

    require(set(rows) == set(names), 'private lifetime closed')
    require(frames == {r: frame(f) for r, f in word['final_frames'].items()}, 'final frames')
    for r in names:
        if not r.startswith('X'):
            require(rows[r] == {r: Q(1)}, 'dirty public restoration')
        else:
            require(rows[r].get(r) == 1 and all(s == r or s.startswith('Y') for s in rows[r]), 'dual shear support')
    probes = {(len(word['program']), r): rows[r] for r in names}
    cut, role, row = l1_witness
    probes[cut, role] = row
    reverse_terms = 0
    for (cut, role), expected in probes.items():
        got = reverse_row(word['program'], cut, role, set(names))
        require(got == expected, 'independent reverse coefficients')
        reverse_terms += len(got)
    for cut, role, source, coefficient in witnesses.values():
        got = reverse_row(word['program'], cut, role, set(names))
        require(got.get(source) == Q(coefficient), 'independent grid witness')
    return {
        'events': len(word['program']), 'counts': dict(sorted(counts.items())),
        'profile': {str(k): n for k, n in sorted(profile.items())},
        'rank_mass': sum(k*n for k, n in profile.items()),
        'changed_field_boundaries_including_entries': boundaries,
        'nonzero_term_visits': nonzero_terms,
        'max_logical_row_l1': str(max_l1), 'max_scalar_denominator': max_denominator,
        'l1_witness': {'cut': l1_witness[0], 'role': l1_witness[1]},
        'grid_forms': {str(a): b for a, b in sorted(forms.items())},
        'grid_witnesses': {str(a): list(w) for a, w in sorted(witnesses.items())},
        'reverse_public_outputs': len(names), 'reverse_coefficient_checks': reverse_terms,
        'ideal_zero_erase_cuts': erases,
    }


def separating_column():
    """Literal conjugated full Fourier column; integer Gaussian arithmetic."""
    state = [(1, 0)]
    for _ in range(9):
        # Delta: ((1-i)I + (1+i)X)/2. Denominator 2^9.
        state = [(a+b, b-a) for a, b in state] + [(a-b, a+b) for a, b in state]
    require(all(a*a+b*b == 512 for a, b in state), 'full Fourier column magnitudes')
    require(sum(a*a+b*b for a, b in state) == 512**2, 'unit norm full column')
    physical = [(Q(-a, 1024), Q(-b, 1024)) for a, b in state]
    require(physical[0] == (Q(-1, 64), Q(1, 64)), 'ordinary physical transpose witness')
    require(any((a*32).denominator != 1 or (b*32).denominator != 1 for a, b in physical),
            'five fractional bits fail on an integer input')
    return {'entries': 512, 'input': 'Y2=delta_0', 'X0_at_0': ['-1/64', '1/64'],
            'rejects_fractional_bits': 5}


def all_depth_witness(word):
    """Finite premises for the written all-depth interior/endpoint separation."""
    event = word['program'][2142]
    require(event[:2] == ['transport', 'D18'] and len(event[3]) == 9,
            'interior witness at FULL chart')
    require(not word['initial_frames']['Y2'], 'integer physical probe enters at ZERO')
    inputs = set(word['initial_frames'])
    coefficient = reverse_row(word['program'], 2143, 'D18', inputs).get('Y2')
    require(coefficient == Q(-1, 4), 'interior witness logical coefficient')
    for r in inputs:
        row = reverse_row(word['program'], len(word['program']), r, inputs)
        if r.startswith('X'):
            require(len(word['final_frames'][r]) == 9, 'final X full chart')
            require(row.get('Y2', Q(0)).denominator <= 2, 'final probe half-integral coefficient')
        elif r == 'Y2':
            require(row == {'Y2': Q(1)} and len(word['final_frames'][r]) == 8,
                    'final probe rank-eight chart')
        else:
            require(not row.get('Y2', 0), 'remaining probe fields vanish')
    require(reverse_row(word['program'], len(word['program']), 'X0', inputs).get('Y2') == Q(-1, 2),
            'final half coefficient attains endpoint grid')
    # The all-depth proof uses (1-i)^2=-2i. These sample depths additionally
    # check its integer exponent formula; sampling is not the universal proof.
    a, b = 1, 0
    for depth in range(1, 9):
        a, b = a+b, b-a
        d = max(Q(a, 1 << (5*depth+2)).denominator.bit_length()-1,
                Q(b, 1 << (5*depth+2)).denominator.bit_length()-1)
        require(d == (9*depth+1)//2+2, 'Gaussian tensor witness exponent')
    return {'input': 'Y2=delta_(0,...,0), all others zero',
            'cut': 2143, 'role': 'D18', 'logical_coefficient': '-1/4',
            'interior_component': '-(1-i)^lambda / 2^(5*lambda+2)',
            'required_fractional_bits': 'ceil(9*lambda/2)+2',
            'exact_final_max_fractional_bits_for_this_input': 'ceil(9*lambda/2)+1',
            'scope': 'One input at all positive integer depths; sufficient global format remains conservative'}


def controls(word, result):
    failures = []

    def reject(label, changed):
        try:
            replay(changed)
        except ValueError:
            failures.append(label)
        else:
            raise ValueError('mutation accepted: ' + label)

    bad = deepcopy(word)
    bad['program'].pop(0)
    reject('omitted decreasing entry conversion', bad)
    bad = deepcopy(word)
    j = next(i for i, e in enumerate(bad['program']) if e[0] == 'transport')
    bad['program'][j][4] += 1
    reject('wrong recursive transport rank', bad)
    bad = deepcopy(word)
    j = next(i for i, e in enumerate(bad['program']) if e[0] == 'add')
    bad['program'][j][3] = '1/3'
    reject('non-dyadic scalar alphabet', bad)
    bad = deepcopy(word)
    j = next(i for i, e in enumerate(bad['program']) if e[0] == 'erase')
    k = max(i for i, e in enumerate(bad['program'][:j]) if e[0] == 'add' and e[1] == 'C')
    bad['program'].pop(k)
    reject('private compensation omitted', bad)
    equivalent = deepcopy(word)
    for f in equivalent['initial_frames'].values():
        f.reverse()
    for e in equivalent['program']:
        if e[0] == 'transport':
            e[2].reverse(); e[3].reverse()
        elif e[0] == 'add':
            e[4].reverse()
    require(replay(equivalent) == result, 'equivalent subspace bases')
    return failures


def compute():
    word = authenticate()
    result = replay(word)
    require(result['max_logical_row_l1'] == '127/2', 'credited logical growth')
    # Finite affine certificate implies max(10*l,9*l+2) for all integers l>=1:
    # check l=1 and l=2, then every slope is at most 10.
    for a, b in result['grid_forms'].items():
        a = int(a)
        require(a <= 10 and a+b <= 11 and 2*a+b <= 20, 'all-depth sufficient grid envelope')
    require(Q(127, 2) < 64, 'component growth power-of-two guard')
    literal = physical.execute(word)
    try:
        physical.execute(word, fractional_budget=6)
    except ValueError as error:
        require(str(error) == 'physical fixture leaves claimed grid', 'physical grid control failure')
    else:
        raise ValueError('endpoint-only six-bit grid falsely accepted')
    return {
        'schema_version': 1, 'status': 'PASS',
        'scope': 'Exact atomic-instruction physical component bounds; all integer tensor depths lambda>=1',
        'replay': result, 'separating_column': separating_column(), 'physical_fixture': literal,
        'all_depth_interior_witness': all_depth_witness(word),
        'grid_extra_bits': 'max(10*lambda, 9*lambda+2)',
        'component_magnitude_guard_bits': 'ceil((9*lambda+1)/2)+6',
        'controls': controls(word, result) + ['endpoint-only six-bit physical grid'],
        'no_new_supplier_or_kappa': True,
    }


def canonical(value):
    # JSON types matter: bools may not impersonate integer evidence.
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write a new receipt exclusively')
    args = parser.parse_args()
    if args.out:
        require(not args.out.exists(), 'output already exists')
    result = compute()
    if args.out:
        with args.out.open('x') as out:
            out.write(json.dumps(result, indent=2) + '\n')
    else:
        require(canonical(result) == canonical(json.loads((PACKAGE / 'RESULT.json').read_text())),
                'complete typed receipt mismatch')
    print('PASS_P104_PHYSICAL_DUAL_GRID events=5398 all_positive_tensor_depths no_new_kappa')


if __name__ == '__main__':
    main()

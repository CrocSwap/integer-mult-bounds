#!/usr/bin/env python3
"""Finite cold-hyperplane source binding; no Lean build or supplier claim.

Aaron Wang / navinor, with help from chatgpt. Apache-2.0.
Source constructors produce candidates; acceptance uses an independent
Gaussian-integer evaluator and a faithful packed-basis comparison.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/direct-delivery504-global/vendor/clifford/clifford_exact.py'
N = 512
RADIX = 1 << 18
BOUND = 4**8


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe_radix(radix):
    require(type(radix) is int and radix-1 > BOUND+16, 'unsafe packed radix')


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def check_sources():
    pins = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    out = {}
    for pin in pins['files']:
        if pin['usage'] == 'input':
            raw = (ROOT/pin['path']).read_bytes()
            sha = hashlib.sha256(raw).hexdigest()
            require(sha == pin['sha256'], 'source drift: '+pin['path'])
            out[pin['path']] = sha
    return out


def load_producer():
    spec = importlib.util.spec_from_file_location('cold_candidate_producer', ROOT/SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def hyperplane(normal):
    require(type(normal) is int and 1 <= normal < N, 'invalid normal')
    plane = {x for x in range(N) if (x & normal).bit_count() % 2 == 0}
    span, basis = {0}, []
    for x in sorted(plane):
        if x not in span:
            basis.append(x)
            span |= {y ^ x for y in span}
    require(len(plane) == 256 and span == plane and len(basis) == 8,
            'hyperplane basis/width')
    return tuple(basis), tuple(sorted(plane))


def permutation(rows):
    require(len(rows) == 9 and all(type(r) is int and 0 <= r < N for r in rows),
            'invalid permutation rows')
    result = [sum(((r & x).bit_count() % 2) << j for j, r in enumerate(rows)) for x in range(N)]
    require(len(set(result)) == N, 'singular permutation')
    return result


def phases(qrows, alpha, phase=0):
    require(len(qrows) == len(alpha) == 9
            and all(type(r) is int and 0 <= r < N for r in qrows)
            and all(type(a) is int and 0 <= a < 4 for a in alpha)
            and type(phase) is int and 0 <= phase < 4, 'invalid phase data')
    require(all(((qrows[i] >> j) & 1) == ((qrows[j] >> i) & 1)
                for i in range(9) for j in range(9)), 'nonsymmetric quadratic')
    require(all(alpha[i] % 2 == ((qrows[i] >> i) & 1) for i in range(9)),
            'phase parity mismatch')
    return [(phase + sum(alpha[i] for i in range(9) if x >> i & 1)
             + 2*sum(1 for i in range(9) for j in range(i+1,9)
                     if x >> i & 1 and x >> j & 1 and qrows[i] >> j & 1)) % 4
            for x in range(N)]


def rotate(a, b, p):
    return ((a,b), (-b,a), (-a,-b), (b,-a))[p % 4]


def monomial_inverse(record, real, imag):
    p = permutation(record['matrix_rows'])
    b = record['offset']
    require(type(b) is int and 0 <= b < N, 'invalid translation')
    phi = phases(record['quadratic_rows'], record['linear_Z4'], record['phase'])
    out = [rotate(real[p[x]^b], imag[p[x]^b], -phi[x]) for x in range(N)]
    return [a for a,b in out], [b for a,b in out]


def literal(circuit, real, imag):
    """Unnormalized exact gate action. C-count supplies the common denominator."""
    denominator = 0
    for gate in circuit:
        kind = gate[0]
        if kind == 'P':
            require(len(gate) == 2, 'permutation gate arity')
            p = permutation(gate[1])
            rr, ii = [0]*N, [0]*N
            for x,y in enumerate(p):
                rr[y], ii[y] = real[x], imag[x]
            real, imag = rr, ii
        elif kind == 'D':
            require(len(gate) == 3, 'phase gate arity')
            phi = phases(gate[1], gate[2])
            out = [rotate(a,b,p) for a,b,p in zip(real,imag,phi)]
            real, imag = [a for a,b in out], [b for a,b in out]
        elif kind == 'phase':
            require(len(gate) == 2 and type(gate[1]) is int and 0 <= gate[1] < 4,
                    'invalid global phase')
            out = [rotate(a,b,gate[1]) for a,b in zip(real,imag)]
            real, imag = [a for a,b in out], [b for a,b in out]
        elif kind == 'X':
            require(len(gate) == 2 and type(gate[1]) is int and 0 <= gate[1] < N,
                    'invalid XOR gate')
            real, imag = [real[x^gate[1]] for x in range(N)], [imag[x^gate[1]] for x in range(N)]
        elif kind == 'C':
            require(len(gate) == 3 and type(gate[1]) is int and 0 < gate[1] < N
                    and type(gate[2]) is int and gate[2] in (-1,1), 'invalid C gate')
            q, sign = gate[1:]
            plus = [rotate(a,b,sign) for a,b in zip(real,imag)]
            minus = [rotate(a,b,-sign) for a,b in zip(real,imag)]
            real, imag = ([real[x]+plus[x][0]+real[x^q]+minus[x^q][0] for x in range(N)],
                          [imag[x]+plus[x][1]+imag[x^q]+minus[x^q][1] for x in range(N)])
            denominator += 1
        else:
            raise ValueError('unknown literal gate')
    return real, imag, denominator


def c8_kernel(real):
    """Closed form, not gate execution: 16*(-i)^popcount(delta), denominator256."""
    classes = [[d for d in range(256) if d.bit_count() % 4 == k] for k in range(4)]
    rr, ii = [], []
    for y in range(N):
        rr.append(16*(sum(real[y^d] for d in classes[0])-sum(real[y^d] for d in classes[2])))
        ii.append(16*(sum(real[y^d] for d in classes[3])-sum(real[y^d] for d in classes[1])))
    return rr, ii


def wrapped(circuit, left, right, real, imag):
    real, imag = monomial_inverse(right, real, imag)
    real, imag, den = literal(circuit, real, imag)
    real, imag = monomial_inverse(left, real, imag)
    return real, imag, den


def require_equal(actual, target):
    require(actual[2] == 8, 'cold denominator/width mismatch')
    require(actual[0] == target[0] and actual[1] == target[1], 'cold factorization mismatch')


def controls(circuit, left, right, packed, target):
    faults = []
    l = copy.deepcopy(left); l['phase'] = (l['phase']+1) % 4
    faults.append(('global_phase', circuit, l, right))
    r = copy.deepcopy(right); r['offset'] ^= 256
    faults.append(('spectator_translation', circuit, left, r))
    index = next(i for i,g in enumerate(circuit) if g[0] == 'C')
    c = copy.deepcopy(circuit); c[index] = ('C', c[index][1], -c[index][2])
    faults.append(('C_direction', c, left, right))
    c = copy.deepcopy(circuit); c[index] = ('C', 256, c[index][2])
    faults.append(('spectator_C', c, left, right))
    c = copy.deepcopy(circuit); del c[index]
    faults.append(('omitted_C', c, left, right))
    rejected = []
    for name,c,l,r in faults:
        try:
            require_equal(wrapped(c,l,r,packed,[0]*N), target)
        except ValueError as error:
            rejected.append({'name': name, 'reason': str(error)})
        else:
            raise ValueError('mutation accepted: '+name)
    # [2,-1] is a nonzero coefficient vector evaluating to zero at radix 2.
    # A coefficient bound is essential, even if the one input happens to agree.
    require(sum(c*2**j for j,c in enumerate((2,-1))) == 0, 'small-radix alias control')
    try:
        safe_radix(2)
    except ValueError as error:
        require(str(error) == 'unsafe packed radix', 'wrong radix rejection')
    else:
        raise ValueError('unsafe radix control accepted')
    return rejected


def evaluate(probe=False):
    sources = check_sources()
    producer = load_producer()
    require(producer.canonical_frame(9,()).circuit == [], 'empty entrance not literal identity')
    safe_radix(RADIX)
    packed = [1 << (18*x) for x in range(N)]
    target = c8_kernel(packed)
    records, planes = [], set()
    mutations = None
    normals = (1,511) if probe else range(1,N)
    for normal in normals:
        basis, plane = hyperplane(normal)
        require(basis == tuple(producer.nullspace((normal,),9)),
                'producer hyperplane basis convention disagreement')
        require(plane not in planes, 'duplicate hyperplane')
        planes.add(plane)
        op = producer.canonical_frame(9,basis)
        record, _ = producer.lower_child(op)
        require(record['rank'] == 8 and record['left'] is not None and record['right'] is not None,
                'producer cold rank mismatch')
        require(sum(g[0] == 'C' for g in op.circuit) == 8, 'canonical C-count mismatch')
        require_equal(wrapped(op.circuit,record['left'],record['right'],packed,[0]*N), target)
        records.append({'normal': normal, 'basis': basis, 'width': 8, 'spectators': 1,
                        'circuit_sha256': digest(op.circuit), 'wrappers_sha256': digest(record)})
        if normal == 1:
            mutations = controls(op.circuit,record['left'],record['right'],packed,target)
    require(len(planes) == (2 if probe else 511), 'family coverage mismatch')
    return {'sources': sources, 'hyperplanes': len(records), 'normal_range': [1,511],
            'columns_per_operator': N, 'matrix_entries_per_operator': N*N,
            'total_semantic_columns': len(records)*N,
            'total_matrix_entries': len(records)*N*N,
            'packed_radix': RADIX, 'literal_coefficient_bound': BOUND,
            'reference_coefficient_bound': 16, 'denominator_exponent': 8,
            'records_sha256': digest(records), 'mutations': mutations,
            'scope': 'finite conditional cold binding; no Lean build, emitted-word or supplier claim'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--result', type=Path, default=HERE/'RESULT.json')
    args = parser.parse_args()
    result = evaluate(args.probe)
    if args.probe:
        print('PASS_COLD_HYPERPLANE_PROBE normals=1,511 controls=5')
        return
    path = args.result
    if args.write:
        path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:
        expected = json.loads(path.read_text(encoding='utf-8'))
        require(json.dumps(expected,sort_keys=True,separators=(',',':'))
                == json.dumps(result,sort_keys=True,separators=(',',':')), 'result receipt mismatch')
    print('PASS_COLD_HYPERPLANE_SEMANTIC_BINDING hyperplanes=511 columns=261632 '
          'entries=133955584 controls=5 global_phase spectator_preserved no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError) as error:
        raise SystemExit('FAIL_COLD_HYPERPLANE_SEMANTIC_BINDING: '+str(error))

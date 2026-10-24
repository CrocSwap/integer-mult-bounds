"""Check actual Gaussian sources, independent solves and complete residuals.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
from dataclasses import replace
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
from consumer import prepare, execute, dyadic_gap
from solver import solve, trunc


def need(value, message):
    if not value:
        raise ValueError(message)


def reject(call):
    try:
        call()
    except (ValueError, TypeError):
        return
    raise ValueError('invalid input accepted')


def source():
    raw = {}
    for row in json.loads((ROOT/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input' or '/vendor/' in row['path']:
            b = (REPO/row['path']).read_bytes()
            need(hashlib.sha256(b).hexdigest() == row['sha256'], 'source byte mismatch')
            raw[row['path']] = b
    sys.path.insert(0, str(REPO/'research/rational-unitary-fft'))
    from gaussian_reference import Reference
    return Reference, raw


def dense_solve(matrix, rhs):
    n = len(matrix)
    a = [list(row)+[Q(x) for x in pair] for row, pair in zip(matrix, rhs)]
    for k in range(n):
        pivot = next(i for i in range(k, n) if a[i][k])
        a[k], a[pivot] = a[pivot], a[k]
        value = a[k][k]
        a[k] = [x/value for x in a[k]]
        for i in range(n):
            if i != k:
                value = a[i][k]
                a[i] = [x-value*y for x, y in zip(a[i], a[k])]
    return [row[n:] for row in a]


def run(small):
    Reference, raw = source()
    specifications = [(9,1,1,2,2,64), (13,5,1,3,3,64)]
    if not small:
        specifications += [(31,1,2,3,4,80),(32,7,1,3,4,64),(65,13,2,3,5,80),
                           (97,1,2,4,6,80),(129,7,2,4,7,96),(257,1,2,4,9,96)]
    rng = random.Random(52845315)
    receipt, dense_checks, entries, controls = [], 0, 0, 0
    for index, spec in enumerate(specifications):
        reference = Reference(raw, *spec)
        target = (12,18,24)[index % 3]
        p = prepare(reference, target)
        n, period = spec[0], reference.target_size
        before = repr(p.factors)
        setup_caches = dict(weights=len(reference.weights), kernels=len(reference.kernel), entries=len(reference.entries),
                            weight_precision=reference.weight_precision, kernel_error_bits=reference.kernel_error_bits)
        matrix = [[reference.entry('narrow',i,j).value for j in range(period)] for i in range(period)]
        entries += period**2
        selected = tuple(reference.selected)
        holes = set(reference.holes)
        # This scans the literal matrix, not the consumer's sparse table.
        for i in range(period):
            need(matrix[i][i] == 1 and sum(abs(x) for j,x in enumerate(matrix[i]) if j!=i) <= 1-p.gap,
                 'full original row gap')
            for j in range(period):
                if i in holes or j in holes:
                    need(matrix[i][j] == int(i==j), 'literal hole identity')
                elif matrix[i][j]:
                    a,b = selected.index(i), selected.index(j)
                    need(min(abs(a-b), n-abs(a-b)) <= spec[3], 'literal cyclic support')
        max_residual = Q(0)
        output_digest = hashlib.sha256()
        scale = 1 << p.bits
        for trial in range(3):
            if trial == 0:
                data = tuple((scale if j%2 else -scale,0) for j in range(period))
            elif trial == 1:
                data = tuple((0,scale if j in holes else -scale) for j in range(period))
            else:
                data = tuple((a, rng.randint(-(scale-abs(a)), scale-abs(a)))
                             for a in (rng.randint(-scale,scale) for _ in range(period)))
            saved = data
            output,bill = execute(p,data)
            need(data == saved and repr(p.factors) == before, 'borrowed input or factors changed')
            need(all(output[j] == data[j] for j in holes), 'hole output changed')
            need(bill['products'] <= 8*n*spec[3], 'solve count bound')
            residual = max(sum(abs(sum(matrix[i][j]*Q(output[j][c],scale) for j in range(period))
                                   - Q(data[i][c],scale)) for c in (0,1)) for i in range(period))
            need(residual <= (2-p.gap)*sum(p.error_terms[1:]), 'original-reference residual envelope')
            raw_answer, _ = solve(p.factors, tuple(data[j] for j in selected), p.bits)
            raw_bits = p.factors['plan']['bits']
            fine = [[Q(x,scale) for x in z] for z in data]
            for j,z in zip(selected,raw_answer):
                fine[j] = [Q(x,1 << raw_bits) for x in z]
                need(output[j] == tuple(trunc(x,1 << (raw_bits-p.bits)) for x in z),
                     'public output differs from final grid rounding')
            raw_residual = max(sum(abs(sum(matrix[i][j]*fine[j][c] for j in range(period))
                                      - Q(data[i][c],scale)) for c in (0,1)) for i in range(period))
            need(raw_residual/p.gap + p.error_terms[0] + p.error_terms[3] <= Q(1,1 << target),
                 'independent residual plus final rounding target')
            max_residual = max(max_residual,residual/p.gap)
            if index < 2:
                exact = dense_solve(matrix, [[Q(x,scale) for x in z] for z in data])
                distance = max(sum(abs(Q(output[i][c],scale)-exact[i][c]) for c in (0,1)) for i in range(period))
                need(distance <= sum(p.error_terms[1:]), 'independent dense solution')
                dense_checks += 1
            output_digest.update(json.dumps(output).encode())
        need(p.source_requests == n*(2*spec[3]+1)+spec[1], 'complete source call bill')
        receipt.append({'specification':list(spec),'target':target,'period':period,'holes':list(p.holes),
                        'gap':str(p.gap),'boundary_bits':p.bits,'coefficient_bits':p.coefficient_bits,
                        'internal_bits':p.factors['plan']['bits'],'word_bits':p.factors['plan']['word_bits'],
                        'error_terms':[str(x) for x in p.error_terms],
                        'source_requests':p.source_requests,'source_setup':setup_caches,'factor':p.factors['statistics'],
                        'solve':bill,'output_sha256':output_digest.hexdigest(),
                        'reference_hash':p.source_hash,
                        'final_grid_residual_certificate_meets_target':max_residual < Q(1,1 << target),
                        'internal_residual_plus_rounding_meets_target':True})
        if index == 0:
            reject(lambda: execute(p,list(data)));controls+=1
            reject(lambda: execute(p,data[:-1]));controls+=1
            reject(lambda: execute(p,((scale+1,0),)+data[1:]));controls+=1
            reject(lambda: prepare(reference,target,boundary_bits=target));controls+=1
            for gap in (Q(0),Q(-1),Q(1)):
                bad = copy.copy(reference);bad.narrow_gap=gap
                reject(lambda: prepare(bad,target));controls+=1
            bad = copy.copy(reference);bad.errors={'narrow':Q(1)}
            reject(lambda: prepare(bad,target));controls+=1
            bad = copy.copy(reference);bad.errors={'narrow':p.gap/4}
            reject(lambda: prepare(bad,target));controls+=1
            bad = copy.copy(reference);bad._holes=()
            reject(lambda: prepare(bad,target));controls+=1
            key=('narrow',selected[0],selected[1]);old=reference.entries[key]
            reference.entries[key]=replace(old,value=-Q(1,8))
            try:reject(lambda: prepare(reference,target));controls+=1
            finally:reference.entries[key]=old
    for e in (0,1,15,16,17,80,1000):
        need(dyadic_gap(Q(3, 1 << (e+2))) == Q(1, 1 << (e+1)), 'no fixed gap floor')
    return {'status':'PASS','fixtures':receipt,'original_entries':entries,
            'dense_rhs_checks':dense_checks,'complete_rhs_checks':3*len(specifications),
            'controls':controls,'small_gap_checks':7}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--small',action='store_true');ap.add_argument('--write-result',action='store_true')
    args=ap.parse_args();result=run(args.small)
    if not args.small:
        if args.write_result:(ROOT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
        else:need(result == json.loads((ROOT/'RESULT.json').read_text()), 'receipt differs')
    print(json.dumps(result,sort_keys=True))
    print('PASS_PERIODIC_GAUSSIAN_UNIFORM_SOLVE')


if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""Replay the original periodic reference and the complete direct consumer."""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(HERE))
from solver import prepare,execute,certify,need


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def reject(action, label):
    try:
        action()
    except (ValueError,TypeError):
        return label
    raise ValueError('control accepted: '+label)


def oracle(rows, bits, data, data_bits):
    n = len(rows)
    a = [[Q(int(i == j)) for j in range(n)]+[Q(x,1<<data_bits) for x in data[i]] for i in range(n)]
    for i,row in enumerate(rows):
        for j,value in row:
            a[i][j] = Q(value,1<<bits)
    for k in range(n):
        pivot = next(i for i in range(k,n) if a[i][k])
        a[k],a[pivot] = a[pivot],a[k]
        d = a[k][k]
        a[k] = [x/d for x in a[k]]
        for i in range(n):
            if i != k:
                d = a[i][k]
                a[i] = [x-d*y for x,y in zip(a[i],a[k])]
    return [row[n:] for row in a]


def small_checks():
    cases = endpoints = 0
    for n in range(1,8):
        for seed in range(5):
            s = 1<<33
            rows = tuple(tuple((j,((i*7+j*11+seed)%15+1)*s//(16*max(1,n-1)))
                               for j in range(n) if i != j) for i in range(n))
            p = prepare(rows,33,Q(1,16),target=16)
            cert = dict(p.certificate)
            for kind in range(3):
                scale = 1<<p.source_bits
                data = tuple((((i*17+kind)%33-16)*scale//32,
                              ((i*13+seed)%33-16)*scale//32) for i in range(n))
                original = digest(data)
                answer,bill = execute(p,data)
                exact = oracle(rows,33,data,p.source_bits)
                error = max(sum(abs(Q(answer[i][c],scale)-exact[i][c]) for c in range(2)) for i in range(n))
                need(error <= cert['error_bound'], 'independent dense solve differs')
                need(digest(data) == original, 'input changed')
                need(bill['products'] == 2*(sum(map(len,p.lower))+sum(map(len,p.upper))-n), 'solve product bill')
                endpoints += 1
            cases += 1
    rows = (((1,1<<30),),((0,1<<30),))
    p = prepare(rows,33,Q(1,2))
    s = 1<<p.source_bits
    data = ((s,0),(0,-s))
    controls = [reject(lambda:execute(p,list(data)), 'mutable input'),
                reject(lambda:execute(p,data[:-1]), 'missing row'),
                reject(lambda:execute(p,((True,0),data[1])), 'boolean alias'),
                reject(lambda:execute(p,((s,s),data[1])), 'radius overflow'),
                reject(lambda:execute(replace(p,width=64),data), 'word overflow'),
                reject(lambda:prepare(rows,33,Q(1,2),target=60), 'unfunded precision'),
                reject(lambda:prepare((((1,-1),),rows[1]),33,Q(1,2)), 'negative coefficient'),
                reject(lambda:prepare((((1,1),(1,1)),rows[1]),33,Q(1,2)), 'duplicate coefficient')]
    altered = list(p.upper)
    altered[0] = ((0,(1<<p.bits)//2),)+tuple((j,v) for j,v in altered[0] if j != 0)
    controls.append(reject(lambda:certify(rows,33,p.lower,tuple(altered),p.bits,Q(1,2),1,20), 'corrupt factor'))
    controls.append(reject(lambda:certify(rows,33,p.upper,p.lower,p.bits,Q(1,2),1,20), 'factor order'))
    need(execute(p,((0,0),(0,0)))[0] == ((0,0),(0,0)), 'zero reuse')
    return dict(matrices=cases,complex_rhs=endpoints,controls=controls)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record',type=Path)
    parser.add_argument('--timing',type=Path)
    parser.add_argument('--small',action='store_true')
    args = parser.parse_args()
    small = small_checks()
    if args.small:
        print('PASS_DIRECT_SMALL '+json.dumps(small,sort_keys=True))
        return
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage'] == 'input':
            need(sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], 'source pin '+item['path'])
    sys.path[:0] = [str(ROOT/'research/periodic-reference-rounded-inverse-service'),
                   str(ROOT/'research/periodic-gaussian-weighted-power-bound'),
                   str(ROOT/'research/rational-unitary-fft')]
    from service import prepare as old_prepare,execute as old_execute
    from weighted import adopt
    from gaussian_reference import Reference
    from gaussian import INTERVALS
    start = time.perf_counter()
    reference = Reference({INTERVALS:(ROOT/INTERVALS).read_bytes()},384,1,2,4,18,320)
    need(reference.description_hash == '4001280a290db7fe1afbbbed80704821796da86c3de8f86516b8debaf099591c', 'original Reference')
    original = old_prepare(reference)
    source_seconds = time.perf_counter()-start
    need((original.bits,original.steps,len(original.rows)) == (33,276,385), 'original source parameters')
    previous,weighted,_,_ = adopt(reference,original)
    need(previous.steps == 120, 'weighted predecessor')
    start = time.perf_counter()
    direct = prepare(original.rows,original.bits,original.gap)
    preparation_seconds = time.perf_counter()-start
    cert = dict(direct.certificate)
    n = len(original.rows)
    s = 1<<original.bits
    data = [(((i*17)%65-32)*s//64,((i*29)%65-32)*s//64) for i in range(n)]
    data[0],data[-1],data[192] = (s//2,s//2),(-s,0),(s//4,-s//2)
    data = tuple(data)
    before = digest(data)
    answer,bill = execute(direct,data)
    old_answer,old_bill = old_execute(previous,data)
    need(digest(data) == before and answer[192] == data[192], 'ownership and hole')
    need(bill['products'] == 1398 and old_bill['products'] == 731136, 'complete solve bills')
    need(dict(direct.setup)['products'] == 319 and cert['certificate_products'] == 668, 'setup product bills')
    original_entries = len(reference.entries)
    residual = old_residual = Q(0)
    for i in range(n):
        supplied = {j for j,v in original.rows[i]}|{i}
        r = [-Q(data[i][c],1<<direct.source_bits) for c in range(2)]
        rold = [-Q(data[i][c],s) for c in range(2)]
        for j in range(n):
            a = reference.entry('narrow',i,j).value
            need(j in supplied or a == 0, 'original support')
            if a:
                for c in range(2):
                    r[c] += a*Q(answer[j][c],1<<direct.source_bits)
                    rold[c] += a*Q(old_answer[j][c],s)
        residual = max(residual,sum(map(abs,r)))
        old_residual = max(old_residual,sum(map(abs,rold)))
    need(residual/original.gap <= cert['error_bound'], 'exact original-source residual')
    need(old_residual/original.gap <= previous.error_bound, 'previous source residual')
    ideal = reference.errors['narrow']
    analytic = ideal/(original.gap*(original.gap-ideal))
    need(cert['error_bound']+analytic < Q(1,1<<20), 'complete analytic target')
    # A factorization of a matrix without the true wrap must fail this certificate.
    wrong_rows = tuple(tuple((j,v) for j,v in row if abs(i-j)<=10) for i,row in enumerate(original.rows))
    wrong = prepare(wrong_rows,original.bits,original.gap)
    control = reject(lambda:certify(original.rows,original.bits,wrong.lower,wrong.upper,
                                    wrong.bits,original.gap,1,20), 'dropped periodic entries')
    bounds = {k:str(v) if type(v) is Q else v for k,v in direct.certificate}
    record = dict(status='PASS_PERIODIC_GAUSSIAN_DIRECT_SOLVE',no_new_kappa=True,
                  reference=reference.description_hash,source_bits=original.bits,factor_bits=direct.bits,output_bits=direct.source_bits,
                  source_gap=str(original.gap),source_entry_requests=original.source_entries,
                  source_entry_cache=original_entries,source_table_records=sum(map(len,original.rows)),
                  weight_cache=len(reference.weights),kernel_cache=len(reference.kernel),
                  pi_cache_entries=reference.exp.oracle.pi_interval.cache_info().currsize,
                  certificate=bounds,setup=dict(direct.setup),bill=bill,previous_bill=old_bill,
                  verification_entries=n*n,small_checks=small,periodic_control=control,
                  input_sha256=before,output_sha256=digest(answer),
                  residual_upper=str(Q(-(-residual.numerator*(1<<80)//residual.denominator),1<<80)),
                  analytic_error_upper=str(Q(-(-analytic.numerator*(1<<120)//analytic.denominator),1<<120)))
    record['source_sha256'] = {name:sha256((HERE/name).read_bytes()).hexdigest()
                              for name in ('README.md','solver.py','verify.py','TASK.json','SOURCES.json','VERIFY.json')}
    encoded = json.dumps(record,sort_keys=True,indent=2)+'\n'
    if args.record:
        args.record.write_text(encoded)
    else:
        need((HERE/'RESULT.json').read_text() == encoded, 'receipt differs')
    if args.timing:
        trials = []
        for _ in range(5):
            start = time.perf_counter();old_execute(previous,data);old_time = time.perf_counter()-start
            start = time.perf_counter();p=prepare(original.rows,original.bits,original.gap);execute(p,data);new_time=time.perf_counter()-start
            start = time.perf_counter();execute(direct,data);reuse_time=time.perf_counter()-start
            trials.append(dict(previous=old_time,direct_prepare_and_solve=new_time,direct_reuse=reuse_time))
        args.timing.write_text(json.dumps(dict(python=sys.version,source_setup_seconds=source_seconds,
                                             direct_preparation_seconds=preparation_seconds,trials=trials),indent=2)+'\n')
    print(record['status']+' products=1398 previous_products=731136 no_new_kappa')


if __name__ == '__main__':
    main()

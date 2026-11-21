# SPDX-License-Identifier: Apache-2.0
"""Build or verify a directed paid-support transport for the literal paired BIT tape."""
from argparse import ArgumentParser
from array import array
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import chain
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from zero_support import packed_counts

TRIAL=Fraction('0.003890115286594461129996943')
SCALE=10**30


def exact_inputs(graph,caller,rank_price,ordered):
    targets,paid,_=packed_counts(graph,caller)
    sizes={r for r,_ in targets+paid}
    t=1-TRIAL
    prices={r:rank_price(r,t) for r in sizes}
    demand=[(prices[r][1]*SCALE).__ceil__() for r,_ in targets]
    grouping=Counter()
    for r,support in paid:
        indices=(i for i in support if not ordered or targets[i][0]>=r)
        via=tuple(indices)
        if not via:
            raise ArithmeticError('A literal paid source lacks a permitted dependency')
        grouping[r,via]+=1
    supply=[((prices[r][0]*SCALE).__floor__()*count,r,array('I',via))
            for (r,via),count in grouping.items()]
    return demand,supply


def check_certificate(demand,supply,handle):
    deficit=int(next(handle))
    if deficit:
        raise ArithmeticError(f'Flow is short by {deficit} ticks')
    remaining=demand.copy()
    spent=[0]*len(supply)
    count=0
    for line in handle:
        i,j,x=map(int,line.split())
        if not (0<=i<len(demand) and 0<=j<len(supply) and x>0 and i in supply[j][2]):
            raise ValueError('Unauthorized dependency arc')
        remaining[i]-=x
        spent[j]+=x
        count+=1
    if any(remaining) or any(x>m for x,(m,_,_) in zip(spent,supply,strict=True)):
        raise ValueError('Transport has unsatisfied target mass or overspends a paid slot')
    return count


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('certificate',type=Path)
    p.add_argument('--solver',type=Path)
    p.add_argument('--allow-unordered',action='store_true')
    a=p.parse_args()
    sys.path.insert(0,str(a.source))
    from upstream import install
    install()
    from independent_binary_price import rank_price
    from strong_binary import graph,caller
    demand,supply=exact_inputs(graph(),caller(),rank_price,not a.allow_unordered)
    print('directed mass pool',sum(s for s,_,_ in supply)-sum(demand),flush=True)
    if a.solver:
        data=a.certificate.with_suffix('.in')
        with data.open('w') as f:
            print(len(demand),len(supply),file=f)
            print(*demand,file=f)
            for value,_,support in supply:print(value,len(support),*support,file=f)
        with data.open() as f, gzip.GzipFile(filename='',fileobj=a.certificate.open('wb'),mode='wb',mtime=0) as out:
            done=subprocess.run([str(a.solver)],stdin=f,stdout=subprocess.PIPE,check=True)
            out.write(done.stdout)
    with gzip.open(a.certificate,'rt') as f:
        receipt=check_certificate(demand,supply,f)
    with gzip.open(a.certificate,'rt') as f:
        header=next(f); i,j,amount=map(int,next(f).split())
        try:
            check_certificate(demand,supply,chain((header,f'{i} {j} {amount-1}\n'),f))
        except ValueError as error:
            if 'unsatisfied target mass' not in str(error):
                raise
        else:
            raise ValueError('The one-tick corruption passed')
    print(json.dumps({'trial':str(TRIAL),'scale':SCALE,'target_count':len(demand),'grouped_paid_count':len(supply),
        'permitted_dependencies':sum(len(x) for _,_,x in supply),'certificate_arcs':receipt,
        'ordered':not a.allow_unordered,'certificate_sha256':sha256(a.certificate.read_bytes()).hexdigest()}))
    print('PASS_DIRECTED_PAID_SUPPORT_TRANSPORT',flush=True)


if __name__=='__main__':main()

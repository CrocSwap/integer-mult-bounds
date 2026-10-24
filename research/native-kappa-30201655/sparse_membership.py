"""Paid sparse membership tables for native fused groups, Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
"""
from random import Random
import json


def need(ok,why):
    if not ok:raise ValueError(why)


def prepare(width):
    need(1<=width<=16,'finite model width')
    # Each row contains membership and r-th-set-bit dispatch. All rows are paid.
    rows=[]
    for mask in range(1<<width):
        chosen=tuple(j for j in range(width) if (mask>>j)&1)
        rows.append(chosen)
    return rows


def scatter_union(values,headers,width):
    need(len(values)==len(headers),'stream shape')
    table=prepare(width)
    buckets=[[] for _ in range(width)]
    visits=0
    for index,(value,mask) in enumerate(zip(values,headers)):
        need(0<=mask<1<<width,'header range')
        dispatch=table[mask]
        # Runtime work is proportional to actual visits, not width per record.
        for r in range(len(dispatch)):
            j=dispatch[r];buckets[j].append((index,value));visits+=1
    return buckets,visits


def check():
    rng=Random(20261022);cases=visits=records=0
    for width in range(1,11):
        values=[rng.randrange(-1000,1000) for _ in range(97)]
        headers=[rng.randrange(1<<width) for _ in values]
        got,count=scatter_union(values,headers,width)
        expected=[[(i,x) for i,x in enumerate(values) if (headers[i]>>j)&1] for j in range(width)]
        need(got==expected,'independent sparse membership/scatter formula')
        need(count==sum(mask.bit_count() for mask in headers),'actual visit accounting')
        cases+=1;visits+=count;records+=len(values)
    try:scatter_union([1],[4],1)
    except ValueError:pass
    else:raise ValueError('invalid header accepted')
    return dict(status='PASS',group_shapes=cases,records_checked=records,actual_sparse_visits=visits,
                invalid_header_control=True,scope='finite native membership/dispatch; full selected-bit projection theorem is separate')


if __name__=='__main__':print(json.dumps(check(),indent=2))

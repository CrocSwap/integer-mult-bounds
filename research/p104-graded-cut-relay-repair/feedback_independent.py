#!/usr/bin/env python3
"""Independent low-pivot and zeroed-receipt audit of 27 feedback claims."""
from collections import defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

SOURCE_SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'

def add(basis, val):
    while val:
        pivot=(val & -val).bit_length()-1
        if pivot not in basis:
            basis[pivot]=val
            return True
        val ^= basis[pivot]
    return False

def basis(rows):
    result={}
    for row in rows:add(result,row)
    return result

def replay(g, target):
    n=g['public']; dim={int(k):v['dim'] for k,v in g['frames'].items()}
    where=list(g['start'])+[None]*g['owned_fields']
    original=[1<<i for i in range(n)]+[0]*g['owned_fields']
    zeroed=original.copy()
    h0=defaultdict(list);h1=defaultdict(list)
    for owner,c in enumerate(g['start']):h0[c].append(original[owner]);h1[c].append(zeroed[owner])
    source_before=None; payload=None
    for tick,row in enumerate(g['program']):
        op,i,*args=row
        if op=='INIT':
            assert where[i] is None
            where[i]=args[0];original[i]=zeroed[i]=0
        elif op=='CLEAR':
            assert where[i]==args[0] and i>=n
            where[i]=None;original[i]=zeroed[i]=0
        elif op=='ADD':
            j,c=args;assert where[i]==where[j]==c
            original[i]^=original[j];zeroed[i]^=zeroed[j]
        elif op=='SWAP':
            j,=args
            where[i],where[j]=where[j],where[i]
            original[i],original[j]=original[j],original[i]
            zeroed[i],zeroed[j]=zeroed[j],zeroed[i]
        elif op=='MOVE':
            a,b=args;assert where[i]==a
            if tick==target:
                source_before=list(h0[a]);payload=original[i]
                assert dim[a]>dim[b]
                zeroed[i]=0
            where[i]=b;h0[b].append(original[i]);h1[b].append(zeroed[i])
        else:raise AssertionError(op)
    assert where[:n]==g['final'] and all(x is None for x in where[n:])
    assert payload and not add(basis(source_before),payload)
    rows=original[:n];zrows=zeroed[:n]
    assert rows==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
    assert all((a^b) in (0,payload) for a,b in zip(rows,zrows))
    return payload,h0,h1,rows,zrows

def check(path, receipt_path):
    raw=Path(path).read_bytes();assert sha256(raw).hexdigest()==SOURCE_SHA
    g=json.loads(gzip.decompress(raw)); receipt=json.loads(Path(receipt_path).read_text())
    dims={int(k):v['dim'] for k,v in g['frames'].items()}
    sites=[(k,r) for k,r in enumerate(g['program']) if r[0]=='MOVE' and dims[r[2]]>dims[r[3]]]
    cases=0; odd=[]
    assert len(sites)==len(receipt['certificate'])==27
    for (k, row), item in zip(sites,receipt['certificate']):
        _,owner,src,dst=row
        assert (k,owner,src,dst)==tuple(item[x] for x in ('clock','owner','source','destination'))
        f,h0,h1,outputs,zero=replay(g,k)
        affected={g['final'][i] for i,(x,y) in enumerate(zip(outputs,zero)) if x^y}
        assert len(affected)==item['odd_terminal_charts']
        odd.append(len(affected))
        pair=item['witness_pair'];joint=[]
        for w in pair:
            c=w['chart']; obs=h0[c]; suppressed=h1[c]
            assert len(obs)==len(suppressed)==3
            joint += obs
            deltas=[x^y for x,y in zip(obs,suppressed)]
            assert all(d in (0,f) for d in deltas)
            shift=sum((x==f)<<j for j,x in enumerate(deltas))
            assert shift==w['shift_mask']
            out=outputs[w['odd_public_output']]
            assert g['final'][w['odd_public_output']]==c
            mask=w['native_output_mask']
            assert out == (obs[0] if mask&1 else 0) ^ (obs[1] if mask&2 else 0) ^ (obs[2] if mask&4 else 0)
            assert (mask&shift).bit_count()%2==1
            valid=0
            for table in range(256):
                output_by_observation={}; ok=True
                for x in range(8):
                    z=x^(shift if table>>x&1 else 0);y=(x&mask).bit_count()%2
                    if z in output_by_observation and output_by_observation[z]!=y:ok=False;break
                    output_by_observation[z]=y
                valid+=ok
            assert valid==w['recoverable_nonlinear_boolean_functions_out_of_256']==16
        assert pair[0]['chart']!=pair[1]['chart'] and len(basis(joint))==6
        # Grant every candidate and destination their full zeroed histories.
        dst_basis=basis(h1[dst]);subcases=0;grade=dims[src]-dims[dst]
        assert not add(basis(h1[src]), f)
        for c,dim in dims.items():
            if abs(dim-dims[dst])>=grade:continue
            b=dst_basis.copy()
            for x in h1.get(c,()):add(b,x)
            assert add(b,f), (k,c)
            subcases+=1
        assert subcases==item['cheaper_dimensions_tested']
        cases+=subcases
    assert cases==4643 and sorted(odd)==[55]*15+[63]*12
    result={'source_sha256':SOURCE_SHA,'low_pivot_zeroed_replays':len(sites),
            'full_history_cheaper_sender_exclusions':cases,'positive_native_senders':len(sites),
            'independent_six_observation_pairs':len(sites),'truth_tables_per_witness':256,
            'surviving_local_truth_tables_per_witness':16,'distinct_charts_counts':{'55':15,'63':12}}
    return result
if __name__=='__main__':print(json.dumps(check(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))

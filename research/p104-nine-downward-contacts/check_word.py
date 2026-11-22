#!/usr/bin/env python3
"""Replay the frozen nine-downward-contact word without producer code."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

NATIVE_SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
CHANGED_SHA='4a4bd4faf0b084fbdc4c3e671eea3895c8318bb42aaf44c7afebef7859bb8f2a'
NATIVE=Path(__file__).resolve().parent / 'pinned/strong-bit.json.gz'
CHANGED=Path(__file__).resolve().parent / 'NINE-WORD.json.gz'

def load(path,digest):
    b=path.read_bytes()
    assert sha256(b).hexdigest()==digest
    return json.loads(gzip.decompress(b))

def run_forward(g,skip_clock=None):
    public=g['public']
    sites=dict(enumerate(g['start']))
    value={i:1<<i for i in range(public)}
    cleared={}; moves=[]; peak=len(sites)
    for t,row in enumerate(g['program']):
        if t==skip_clock:continue
        op,i,*args=row
        if op=='INIT':
            c,=args
            assert i>=public and i not in sites
            sites[i]=c; value[i]=0
        elif op=='ADD':
            j,c=args
            assert i!=j and sites[i]==sites[j]==c
            value[i]^=value[j]
        elif op=='MOVE':
            a,b=args
            assert sites[i]==a
            moves.append((i,a,b)); sites[i]=b
        elif op=='SWAP':
            j,=args
            assert i!=j
            value[i],value[j]=value[j],value[i]
            sites[i],sites[j]=sites[j],sites[i]
        elif op=='CLEAR':
            c,=args
            assert i>=public and sites.pop(i)==c and i not in cleared
            cleared[i]=(c,value.pop(i))
        else: raise AssertionError((t,row))
        peak=max(peak,len(sites))
    assert sites==dict(enumerate(g['final'])) and set(value)==set(range(public))
    return [value[i] for i in range(public)],cleared,moves,peak

def run_adjoint(g):
    # Transpose every instruction in reverse order on fresh formal output axes.
    # The adjoint of dropping a private register is a zero initial cotangent.
    public=g['public']
    sites=dict(enumerate(g['final']))
    cot={i:1<<i for i in range(public)}
    for op,i,*args in reversed(g['program']):
        if op=='CLEAR':
            c,=args
            assert i not in sites
            sites[i]=c;cot[i]=0
        elif op=='MOVE':
            a,b=args
            assert sites[i]==b
            sites[i]=a
        elif op=='ADD':
            j,c=args
            assert i!=j and sites[i]==sites[j]==c
            cot[j]^=cot[i]
        elif op=='SWAP':
            j,=args
            sites[i],sites[j]=sites[j],sites[i]
            cot[i],cot[j]=cot[j],cot[i]
        elif op=='INIT':
            c,=args
            assert sites.pop(i)==c
            cot.pop(i)
        else:raise AssertionError(op)
    assert sites==dict(enumerate(g['start'])) and set(cot)==set(range(public))
    return [cot[i] for i in range(public)]

def transpose(rows):
    return [sum(((rows[j]>>i)&1)<<j for j in range(len(rows))) for i in range(len(rows))]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('native',nargs='?',type=Path,default=NATIVE)
    ap.add_argument('changed',nargs='?',type=Path,default=CHANGED)
    args=ap.parse_args()
    a=load(args.native,NATIVE_SHA);b=load(args.changed,CHANGED_SHA)
    assert set(a)==set(b)
    assert all(a[k]==b[k] for k in a if k not in ('program','owned_fields'))
    assert a['public']==630
    x,ca,ma,pa=run_forward(a); y,cb,mb,pb=run_forward(b)
    target=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
    assert x==y==target
    xa=run_adjoint(a); ya=run_adjoint(b)
    assert xa==transpose(x) and ya==transpose(y)
    assert xa==ya
    missing=sorted(set(ca)-set(cb))
    assert not (set(cb)-set(ca)) and len(missing)==18
    assert all(cb[k]==ca[k] for k in cb)
    assert len(ca)==a['owned_fields']==3433 and len(cb)==b['owned_fields']==3415
    assert all(v for c,v in ca.values())
    d={int(c):v['dim'] for c,v in a['frames'].items()}
    def hist(ms,direction):
        return Counter(abs(d[v]-d[u]) for _,u,v in ms if (d[v]-d[u])*direction>0)
    an,bn=hist(ma,-1),hist(mb,-1)
    au,bu=hist(ma,1),hist(mb,1)
    changed_down=[(o,u,v) for o,u,v in mb if d[u]>d[v]]
    assert len(changed_down)==9 and all((u,v)==(1,0) for o,u,v in changed_down)
    I=[[int(i==j) for j in range(8)] for i in range(8)]
    assert a['frames']['0']=={'A':I,'B':[],'dim':0}
    assert a['frames']['1']=={'A':[],'B':I,'dim':8}
    assert au==bu and [(o,u,v) for o,u,v in ma if d[u]<d[v]]==[(o,u,v) for o,u,v in mb if d[u]<d[v]]
    assert an==Counter({1:17,2:1,4:1,5:8}) and bn==Counter({8:9})
    assert len(ma)==2803 and len(mb)==2785 and sum(au.values())==2776
    assert sum(k*v for k,v in (au+an).items())==4813
    assert sum(k*v for k,v in (bu+bn).items())==4822
    # Delete the final top-chart donor before the first return.  This preserves
    # owner/chart legality and should spoil some actual public output rows.
    down_clock=next(t for t,r in enumerate(b['program']) if r[0]=='MOVE' and r[2:]==[1,0])
    faulty=b['program'][down_clock-1]
    assert faulty[0]=='ADD' and faulty[1]==b['program'][down_clock][1] and faulty[3]==1
    damaged,_,_,_=run_forward(b,skip_clock=down_clock-1)
    wrong=[i for i in range(630) if damaged[i]!=target[i]]
    assert wrong
    print(json.dumps({
        'native_sha256':NATIVE_SHA,'changed_sha256':CHANGED_SHA,
        'native_instructions':len(a['program']),'changed_instructions':len(b['program']),
        'independent_forward_rows_checked':630,'independent_adjoint_rows_checked':630,
        'upward_move_count':sum(au.values()),'upward_move_sequence_unchanged':True,
        'native_downward_histogram':dict(sorted(an.items())),
        'changed_downward_histogram':dict(sorted(bn.items())),
        'changed_downward_endpoints':{'source_chart':1,'destination_chart':0,'count':len(changed_down)},
        'endpoint_projectors_verified':{'source':'identity','destination':'zero','nested':True},
        'native_grade_sum':4813,'changed_grade_sum':4822,
        'native_clears':len(ca),'changed_clears':len(cb),
        'removed_private_owners':missing,'all_retained_typed_clears_identical':True,
        'peak_live_native':pa,'peak_live_changed':pb,
        'corruption_control':{'removed_changed_instruction':down_clock-1,
            'wrong_output_count':len(wrong),'first_wrong_outputs':wrong[:12]},
    },indent=2,sort_keys=True))

if __name__=='__main__':main()

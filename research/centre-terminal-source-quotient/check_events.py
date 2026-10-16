#!/usr/bin/env python3
"""Independent literal-event replay on all source columns, using integer grids.

Does not import the primary model, compute local endpoint shortcuts, or use its
elimination/factorization routines. ywz65, OpenAI Codex assistance, Apache-2.0.
"""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SCALE=1<<256

def require(ok,message):
    if not ok:raise ValueError(message)

def read():
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage']=='input':
            require(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'source corruption')
    receipt=json.loads((HERE/'RESULT.json').read_text())
    with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz') as t:
        global_data=json.loads(gzip.decompress(t.extractfile('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz').read()))
        program=json.loads(gzip.decompress(t.extractfile('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz').read()))
    calls=sorted([c for c in global_data['calls'] if c['time']<=10],key=lambda x:x['time'])
    require([c['time'] for c in calls]==list(range(11)),'literal prefix')
    allowners={x[0] for call in calls for x in call['owners']}
    private=max(allowners)+1
    words=[]
    for call in calls:
        ow=[x[0] for x in call['owners']]
        def address(a):
            require(a[0] in ('L','C'),'unknown register bank')
            return ow[a[1]] if a[0]=='L' else private+a[1]
        for event in program[call['orientation']]:
            if event[0]=='scalar':
                x=event[1];name=x[0];dst=address(x[1])
                if name=='clear':words.append((0,dst,0,0,1))
                elif name=='copy':words.append((1,dst,address(x[2]),0,1))
                elif name=='scale':words.append((2,dst,dst,x[2],x[3]))
                elif name=='add':words.append((3,dst,address(x[2]),x[3],x[4]))
                else:raise ValueError('unknown scalar')
            elif event[0]=='center' and call['time'] in (0,10):
                words.append((4,private+event[1],0,0,1))
            else:
                require(event[0] in ('center','phase','climb','adapter','residual_adapter'),'unknown event')
    return receipt,allowners,private,words

def execute(initial,private,words,ablate,private_dirt=0):
    a=[0]*(private+8)
    for i,v in initial.items():a[i]=v*SCALE
    for k in range(8):a[private+k]=(private_dirt+k if private_dirt else 0)*SCALE
    for op,d,s,n,den in words:
        if op==0:a[d]=0
        elif op==1:a[d]=a[s]
        elif op==4:
            if ablate:a[d]=0
        else:
            v=n*a[s]
            require(v%den==0,'integer grid insufficient: no truncation permitted')
            if op==2:a[d]=v//den
            else:a[d]+=v//den
    require(not any(a[private:]),'private scratch not cleared')
    return a

def expected(receipt,initial):
    p=receipt['first_centre_source_maps'];f=receipt['terminal_repair_from_first_centres']
    z={int(k):sum(Fraction(q)*initial.get(int(j),0) for j,q in row.items()) for k,row in p.items()}
    out={int(i):sum(Fraction(q)*z[int(k)] for k,q in row.items())*SCALE for i,row in f.items()}
    require(all(v.denominator==1 for v in out.values()),'nonintegral expected grid')
    return {i:int(v) for i,v in out.items()}

def main():
    r,owners,private,words=read()
    checks=0
    for column in r['source_columns']:
        x={column:1};want=expected(r,x)
        full=execute(x,private,words,False);muted=execute(x,private,words,True)
        require(all(full[i]-muted[i]==want.get(i,0) for i in owners),'literal source endpoint differs')
        checks+=len(owners)
    # Independently replay all columns of the actual sixteen-by-sixteen lower minor.
    minor=r['variable_target_lower_minor']
    for j,column in enumerate(minor['columns']):
        full=execute({column:1},private,words,False)
        muted=execute({column:1},private,words,True)
        for i,row in enumerate(minor['rows']):
            require(Fraction(full[row]-muted[row],SCALE)==Fraction(minor['minor'][i][j]),'variable target minor differs')
            checks+=1
    # Fixed means equal in paired differences, not zero or secretly initialized.
    dirt={i:(17*i)%11-5 for i in owners if i not in set(r['source_columns'])}
    dx={i:(5*i)%7-3 for i in r['source_columns']}
    shifted=dict(dirt);shifted.update(dx)
    h=execute(dirt,private,words,False,23);ha=execute(dirt,private,words,True,23)
    dh=execute(shifted,private,words,False,23);dha=execute(shifted,private,words,True,23)
    want=expected(r,dx)
    require(all((dh[i]-dha[i])-(h[i]-ha[i])==want.get(i,0) for i in owners),'fixed dirty affine difference')
    checks+=len(owners)
    print('PASS_CENTRE_TERMINAL_LITERAL_EVENTS source_columns=112 minor_columns=16 endpoint_checks='+str(checks)+' dirty_controls=1')

if __name__=='__main__':main()

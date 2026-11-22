#!/usr/bin/env python3
"""Independently audit frozen-upward sender-stock intersections using low pivots."""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

SOURCE=Path(__file__).resolve().parent / 'pinned/strong-bit.json.gz'
DIGEST='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'

def add(b,x):
    while x:
        p=x&-x
        if p not in b:
            b[p]=x
            return True
        x^=b[p]
    return False

def extend(b,rows):
    c=b.copy()
    for x in rows:add(c,x)
    return c

def rank(b):return len(b)

def overlap(z,f,hs):
    zf=extend(z,f); zh=extend(z,hs); zfh=extend(zf,hs)
    return rank(zf)+rank(zh)-rank(zfh)-rank(z)

def trace(g):
    p=g['public']; dims={int(k):v['dim'] for k,v in g['frames'].items()}
    v={i:1<<i for i in range(p)};at=dict(enumerate(g['start']))
    history=defaultdict(list)
    for i,c in at.items():history[c].append(v[i])
    F=[];snap={};num_up=0
    for t,(op,i,*a) in enumerate(g['program']):
        if op=='INIT':assert i not in at;at[i]=a[0];v[i]=0
        elif op=='ADD':
            j,c=a;assert at[i]==at[j]==c;v[i]^=v[j]
        elif op=='MOVE':
            s,d=a;assert at[i]==s
            if dims[s]<dims[d]:history[d].append(v[i]);num_up+=1
            if d==0:F.append(v[i])
            at[i]=d
        elif op=='SWAP':
            j,=a;at[i],at[j]=at[j],at[i];v[i],v[j]=v[j],v[i]
        elif op=='CLEAR':assert at.pop(i)==a[0];v.pop(i)
        else:raise AssertionError(op)
        if t in (11104,18875):snap[t]={c:tuple(rows) for c,rows in history.items()}
    assert at==dict(enumerate(g['final']))
    assert len(F)==9 and num_up==2776 and len(history[0])==516
    return F,snap,dims

def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',nargs='?',type=Path,default=SOURCE)
    args=parser.parse_args();raw=args.source.read_bytes();assert sha256(raw).hexdigest()==DIGEST
    g=json.loads(gzip.decompress(raw));assert g['public']==630
    forms,snap,dims=trace(g);result=[]
    for t,m in ((11104,0),(18875,8)):
        data=snap[t];z=extend({},data[0]+tuple(forms[:m]));f=forms[m:]
        assert rank(z)==516+m and rank(extend(z,f))-rank(z)==9-m
        overlaps={c:overlap(z,f,data.get(c,())) for c in dims}
        assert overlaps[1]==9-m and all(not k for c,k in overlaps.items() if c!=1)
        result.append({'inclusive_clock':t,'z_rank':rank(z),'target_rank_mod_z':9-m,
                       'charts_checked':len(dims),'charts_with_nonzero_intersection':{'1':overlaps[1]}})
    z=extend({},snap[11104][0]);replacement=None
    for c in sorted(dims):
        if c in (0,1):continue
        for row in snap[11104].get(c,()):
            if add(z.copy(),row):replacement=(c,row);break
        if replacement:break
    assert replacement
    c,row=replacement
    mutated=[row]+forms[1:]
    assert overlap(z,mutated,snap[11104][c])>0
    print(json.dumps({'source_sha256':DIGEST,'public_inputs':630,'frozen_upward_contacts':2776,
                      'original_downward_return_forms':len(forms),'epochs':result,
                      'corruption_control':{'inserted_sender_form_into_target_list':c,
                      'unexpected_sender_detected':True}},indent=2,sort_keys=True))

if __name__=='__main__':main()

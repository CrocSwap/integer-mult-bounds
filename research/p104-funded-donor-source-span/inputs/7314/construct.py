# SPDX-License-Identifier: Apache-2.0
"""Retire the exact #7277 public helper 863 with a charged donor split."""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()


def need(ok,msg):
    if not ok:raise ValueError(msg)


def span(basis):
    out={0}
    for v in basis:out|={x^v for x in tuple(out)}
    return out


def construct(old,witness=None):
    W=witness if witness is not None else json.loads((HERE/'WITNESS.json').read_bytes())
    need(sha256(canonical(old)).hexdigest()==W['source_word_sha256'],'Exact #7277 source word')
    r=W['role'];s=W['short_chart'];a=W['early_chart'];k=W['short_cache_clock']
    d=W['split'];skip=set(W['retire'])
    n=old['public'];aux=n+old['owned_fields'];p=old['program']
    need((r,s,a,k,d)==(863,240,3,37753,48166) and W['short_cache_coefficient']=='1','Exact witness scope')
    need(skip=={58031,58032,58131,59030,59159} and old['final'][r]==127 and old['initial'][r]==a,'Exact retirement')
    need(p[58031]==['MOVE',r,s,127,False] and
         all(p[i][0]=='ADD' and p[i][2]==r for i in skip-{58031}),'Source-only omitted rank-nine work')
    need(all(i in skip for i,e in enumerate(p) if i>=58031 and
             r in (e[1:3] if e[0] in ('ADD','COPY') else e[1:2])),'All retired helper contacts')
    C=defaultdict(list)
    seen=set()
    for t,q,f,v in W['corrections']:
        need(f in (a,s) and q!=aux and v and 0<=t<=len(p) and (t,q) not in seen,'Unique literal correction')
        need((f==a and t<k) or (f==s and k<=t),'Chronological correction')
        seen.add((t,q));C[t].append((q,f,str(Fraction(v))))
    need(len(seen)==16 and len(C[d])==1 and C[d][0][:2]==(1355,s),'One paid split and fifteen existing coframes')
    out=deepcopy(old);out['owned_fields']+=1;out['final'][r]=s
    frames=old['initial']+[None]*(old['owned_fields']+1);S=list(map(span,old['frames']))
    program=[]
    def append(e):
        op,r,*z=e
        if op=='MOVE':
            x,y,o=z
            need(frames[r]==x and o==(r>=n) and (S[x]<S[y] or o and S[y]<S[x]),'Legal nested MOVE')
            frames[r]=y
        elif op=='INIT':
            need(r>=n and frames[r] is None,'Owned INIT');frames[r]=z[0]
        elif op=='CLEAR':
            need(r>=n and frames[r]==z[0],'Owned CLEAR');frames[r]=None
        else:
            need(frames[r]==e[-1] and (op=='SCALE' or frames[e[2]]==e[-1]),'Literal scalar coframe')
        program.append(e)
    append(['INIT',aux,a]);append(['ADD',aux,r,'1',a])
    for t in range(len(p)+1):
        if t==k:
            append(['CLEAR',aux,a]);append(['INIT',aux,s]);append(['ADD',aux,r,'1',s])
        if t==d:
            need(p[t]==['MOVE',1355,739,127,False],'Exact donor route')
            append(['MOVE',1355,739,s,False])
        for q,f,v in C.get(t,()):append(['ADD',q,aux,v,f])
        if t==len(p):break
        if t==d:append(['MOVE',1355,s,127,False])
        elif t not in skip:append(p[t])
    append(['CLEAR',aux,s])
    need(frames==out['final']+[None]*out['owned_fields'],'Every actual output chart')
    out['program']=program
    return out


if __name__=='__main__':
    old=json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
    Path(sys.argv[2]).write_bytes(gzip.compress(canonical(construct(old)),compresslevel=6,mtime=0))

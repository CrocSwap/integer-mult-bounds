#!/usr/bin/env python3
"""Exact screening of additional equal-frame raw-dirt basis kernels.

No constructor/admission claim. Source-preserving constant-A helpers only.
Apache-2.0; OpenAI Codex assisted research, 2026-10-16.
"""
import argparse,collections,gzip,hashlib,json
from fractions import Fraction as F
from pathlib import Path

PINS={'WORD-base.json.gz':'001b14314d8db873d4d80826d4af9c40a3e5a1fecde743e5a26391bdf673f458',
      'WORD-extra.json.gz':'bc5bfe51178f0c3312d28318412ec490463c896ceed0660b9c443fcb76496546'}
def read_word(path):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PINS.get(path.name):raise ValueError('source hash mismatch')
    return raw,json.loads(gzip.decompress(raw))

def basis(vs):
    p={}
    for v in vs:
        while v:
            b=v.bit_length()-1
            if b in p:v^=p[b]
            else:p[b]=v;break
    for b in sorted(p):
        for c in p:
            if c>b and p[c]>>b&1:p[c]^=p[b]
    return tuple(p[b] for b in sorted(p,reverse=True))

def kernel(rows,n):
    a=[[F(x) for x in row] for row in rows if any(row)]
    piv=[];rank=0
    for col in range(n):
        k=next((k for k in range(rank,len(a)) if a[k][col]),None)
        if k is None:continue
        a[k],a[rank]=a[rank],a[k];q=a[rank][col]
        a[rank]=[x/q for x in a[rank]]
        for i in range(len(a)):
            if i!=rank and a[i][col]:
                q=a[i][col];a[i]=[x-q*y for x,y in zip(a[i],a[rank])]
        piv.append(col);rank+=1
    out=[]
    for c in range(n):
        if c in piv:continue
        v=[F(0)]*n;v[c]=F(1)
        for i,p in enumerate(piv):v[p]=-a[i][c]
        if not all(sum(x*y for x,y in zip(row,v))==0 for row in rows):raise ValueError('bad kernel')
        out.append(v)
    return rank,out

def screen(path):
    raw,w=read_word(path)
    excluded=set(w['removed'])|set(map(int,w['start_extra']))
    init_sources={x['source'] for x in w['initial_corrections']}
    writes={g[1] for g in w['A']}
    uses=collections.defaultdict(list)
    for i,g in enumerate(w['A']):
        for q in (g[1:3] if g[0]=='add' else g[1:2]):uses[q].append((i,g))
    C=collections.defaultdict(lambda:collections.defaultdict(F))
    for g in w['compensation']:
        if g[0]!='add':raise ValueError('unsupported compensation')
        C[g[2]][g[1]]+=F(g[3],g[4])
    elig={}
    for q in range(224,704):
        if q in excluded or q in init_sources or len(uses[q])!=1:continue
        i,g=uses[q][0]
        if g[0]!='add' or g[1]!=q or g[2] in writes:continue
        U=basis(g[-1])
        if not U:continue
        elig[q]=(i,g[2],str(F(g[3],g[4])),U)
    groups=collections.defaultdict(list)
    for q,(_,_,_,U) in elig.items():groups[U].append(q)
    equal=[]
    for U,qs in sorted(groups.items()):
        rows=[[C[q][t] for q in qs] for t in range(112,224)]
        rank,ks=kernel(rows,len(qs))
        equal.append({'frame':U,'helpers':qs,'rank':rank,'nullity':len(ks),'kernels':[{str(q):str(x) for q,x in zip(qs,k) if x} for k in ks]})
    # Allow different first frames with one common line. This is only an
    # algebraic necessary condition: mixed-frame synthesis and all cost unknown.
    byline=collections.defaultdict(list)
    for q,(_,_,_,U) in elig.items():
        S={0}
        for u in U:S|={s^u for s in list(S)}
        for line in S-{0}:byline[line].append(q)
    lines=[]
    for line,qs in sorted(byline.items()):
        if len(qs)<2:continue
        rows=[[C[q][t] for q in qs] for t in range(112,224)]
        rank,ks=kernel(rows,len(qs))
        if ks:lines.append({'line':line,'helpers':qs,'rank':rank,'nullity':len(ks),'kernels':[{str(q):str(x) for q,x in zip(qs,k) if x} for k in ks]})
    qs=[460,461,468,469,462,463,470,471,478,479,490,491,480,481,492,493]
    rows=[[C[q][t] for q in qs] for t in range(112,224)]
    rank,ks=kernel(rows,len(qs))
    joint={'helpers':qs,'rank':rank,'nullity':len(ks),'kernels':[{str(q):str(x) for q,x in zip(qs,k) if x} for k in ks],
           'status':'independent corroboration of PR2857 PROOF, not a new obstruction'}
    if rank!=12 or len(ks)!=4:raise ValueError('source joint rank changed')
    independent=[q for q in qs if any(C[q].values())]
    rs=[[C[q][t] for q in independent] for t in range(112,224)]
    support={t for t in range(112,224) if any(C[q][t] for q in independent)}
    extended=[];count=0;support_rejected=0;zero_columns=[]
    for r in range(224,704):
        if r in excluded or r in init_sources or r in qs:continue
        if not any(C[r].values()):zero_columns.append(r);continue
        count+=1
        if any(C[r][t] for t in set(range(112,224))-support):support_rejected+=1;continue
        rr,kk=kernel([row+[C[r][t]] for row,t in zip(rs,range(112,224))],len(independent)+1)
        if rr==12:extended.append({'helper':r,'kernel':[{str(q):str(x) for q,x in zip(independent+[r],k) if x} for k in kk]})
    # Actual controls for the rank predicate, including an injected algebraic
    # candidate and independent new-coordinate obstruction.
    positive=[row+[row[0]] for row in rs]
    if kernel(positive,len(independent)+1)[0]!=12:raise ValueError('positive span control')
    negative=positive+[[F(0)]*len(independent)+[F(1)]]
    if kernel(negative,len(independent)+1)[0]!=13:raise ValueError('negative span control')
    return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'eligible':{str(q):info for q,info in elig.items()},'equal_frame_groups':equal,'common_line_kernels':lines,
            'joint_rank':joint,'extended_nonzero_columns':{'screened':count,'outside_support':support_rejected,'candidates':extended},
            'outside_zero_columns':zero_columns,'controls':{'duplicate_column_has_rank12':True,'independent_new_row_has_rank13':True}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--words',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result={'scope':'exact compensation matrix kernels among zero-entry, once-A-written helpers with constant source; all endpoints/physical/all-size admission unproved','orientations':{}}
    for s in ['base','extra']:
        result['orientations'][s]=screen(a.words/f'WORD-{s}.json.gz')
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    for s,v in result['orientations'].items():
        print(s,'eligible',len(v['eligible']),'equal-frame nullities',[(r['frame'],r['nullity']) for r in v['equal_frame_groups'] if r['nullity']],'common-line candidates',len(v['common_line_kernels']))
if __name__=='__main__':main()

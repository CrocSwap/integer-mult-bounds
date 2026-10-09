"""Complete marginal-cost filtering for PR125 saturated deferrals.

Chafik Boukhalfa with OpenAI Codex assistance, Apache-2.0. Retains eumemic's
PR114/PR125 nested saturated-placement loop; the actual paid marginal score
uses exterior, first-transition and target-front changes as in DanieleCorso's
PR126 cost-aware descending construction. Here insertion may be between both
existing target levels. Degenerate initial caps may contribute a nondegenerate
part instead of being discarded. All inherited attribution remains attached.
"""
from collections import defaultdict
from fractions import Fraction
import math,os


def repair_candidate(B, algebra):
    mode=os.environ.get('R12_DEFER_MODE','original')
    if algebra['nondeg'](B):return B
    if mode.startswith('radical') or mode=='gain_priority':
        return list(algebra['sat_nonsingular_part'](algebra['sat_basis'](B)))
    return []


def place(cand,reach,F0,h,m,algebra):
    mode=os.environ.get('R12_DEFER_MODE','original')
    assert mode in ('original','cost_filter','radical_cost','radical_original','gain_priority')
    if mode=='original':return algebra['saturated_placement'](cand,reach),dict(mode=mode)
    basis=algebra['sat_basis'];inside=algebra['sat_contained'];cap=algebra['sat_cap']
    nondeg=algebra['sat_nondeg'];part=algebra['sat_nonsingular_part']
    cand={s:basis(B) for s,B in cand.items()};byT=defaultdict(list);placed={};levels=defaultdict(set)
    weight=[0]+[round(d*math.log(d)*10**9) for d in range(1,m+1)]
    def gain(s,d):
        r=len(F0(s)); ext=m-h
        assert 0<=d<=r<=h
        g=weight[r-d]+weight[ext+d]-weight[r]-weight[ext]
        for t in reach[s]:
            ds=levels[t]
            if d in ds:continue
            a=max((x for x in ds if x<d),default=0)
            b=min((x for x in ds if x>d),default=h-1)
            assert a<=d<=b
            g+=weight[d-a]+weight[b-d]-weight[b-a]
        return g
    if mode=='gain_priority':order=sorted(cand,key=lambda s:(-gain(s,len(cand[s])), -len(cand[s]),s))
    else:order=sorted(cand,key=lambda s:(Fraction(-(1<<len(cand[s])),max(1,len(reach[s]))**2),-len(cand[s]),s))
    receipt=dict(mode=mode,candidates=len(cand),nonpositive_rejections=0,empty_rejections=0,accepted=0,accepted_integer_gain=0)
    for s in order:
        X=cand[s];changed=True
        while changed and X:
            changed=False
            for t in sorted(reach[s]):
                for w in byT[t]:
                    B=placed[w]
                    if (len(B)>=len(X) and not inside(X,B)) or (len(B)<len(X) and not inside(B,X)):
                        X=cap(X,B);changed=True
                    if not X:break
                if not X:break
            if X and not nondeg(X):
                before=X;X=part(X);assert inside(X,before) and nondeg(X) and len(X)<len(before);changed=True
        if not X:
            receipt['empty_rejections']+=1;continue
        g=gain(s,len(X))
        if mode!='radical_original' and g<=0:
            receipt['nonpositive_rejections']+=1;continue
        assert nondeg(X) and inside(X,cand[s])
        placed[s]=X;receipt['accepted']+=1;receipt['accepted_integer_gain']+=g
        for t in reach[s]:byT[t].append(s);levels[t].add(len(X))
    for t,ss in byT.items():
        ss.sort(key=lambda s:(len(placed[s]),s))
        assert all(inside(placed[a],placed[b]) for a,b in zip(ss,ss[1:]))
    print('R12 deferral placement',receipt,flush=True)
    return placed,receipt

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independent exact interface check for the source33 / line30 prelude.

Uses only our independent integer/operator utilities; imports no predecessor
builder, native checker, census or target_transport module. No admission claim.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
from check_interface import H,N,SOURCE,HERE,SOURCE_PINS,span,linear,phase_recipe,mono,equal,require,sha,rotate

G=[1,2,4,32,50,128,124,60,474]
U=[266,138,75,30]
E=[504,30,95,20]
F=[486,65,20,10]
TARGETS={135,146,162,220}

def coordinate(state,axis,sign):
    values,exponent=state;out={}
    for x,(r,i) in values.items():
        for y,z in ((x,(r-sign*i,i+sign*r)),(x^(1<<axis),(r+sign*i,i-sign*r))):
            a,b=out.get(y,(0,0));out[y]=(a+z[0],b+z[1])
    return {x:z for x,z in out.items() if z!=(0,0)},exponent+1

def frame_recipe(basis):
    require(len(span(basis))==1<<len(basis),'dependent frame basis')
    columns=list(basis)
    for j in range(H):
        if (1<<j) not in span(columns):columns.append(1<<j)
    return phase_recipe(columns),len(basis)

def frame(state,recipe,sign):
    change,d=recipe;state=mono(state,change,-1)
    for axis in range(d):state=coordinate(state,axis,sign)
    return mono(state,change,1)

def physical(unit,S,T,K,sign=1):
    return frame(mono(frame(unit,S,-1),K,sign),T,1)

def unit_entry(state):
    row,exponent=state
    if len(row)!=1:return None
    x,(r,i)=next(iter(row.items()));n=1<<exponent
    if (abs(r)==n and i==0):return [x,0 if r>0 else 2]
    if (abs(i)==n and r==0):return [x,1 if i>0 else 3]
    return None

def read(p):return json.loads(gzip.decompress(p.read_bytes()))

def main():
    for name,digest in SOURCE_PINS.items():require(sha(SOURCE/name)==digest,'immutable source pin: '+name)
    require(linear(G,138)==30,'entrance flag')
    require({linear(G,x) for x in span(U)}==span(E)==span(F),'retirement flag')
    K=phase_recipe(G);S=frame_recipe([138]);T=frame_recipe([30]);RU=frame_recipe(U);RE=frame_recipe(E)
    CU=frame_recipe([384,193,75,30]);CE=frame_recipe(F)
    recipes={'prelude':[],'handoff':[],'canonical_handoff':[]};bad_target=bad_omitted_map=bad_inverse_phase=0
    wrong=frame_recipe([51]);identity=phase_recipe([1<<j for j in range(H)])
    for column in range(N):
        unit=({column:(1,0)},0)
        pre=physical(unit,S,T,K)
        entry=unit_entry(pre);require(entry is not None,'prelude is not exact unit monomial')
        recipes['prelude'].append(entry)
        hand=physical(unit,RU,RE,K)
        entry=unit_entry(hand);require(entry is not None,'handoff is not exact unit monomial')
        recipes['handoff'].append(entry)
        canonical_hand=physical(unit,CU,CE,K)
        entry=unit_entry(canonical_hand);require(entry is not None,'canonical handoff is not exact unit monomial')
        recipes['canonical_handoff'].append(entry)
        # Actual reverse physical adapter must restore arbitrary physical source.
        restored=physical(pre,T,S,K,-1)
        require(equal(restored,unit),'temporary source warp not restored')
        # Removing target representation gives the desired logical transformed row.
        require(equal(frame(pre,T,-1),mono(frame(unit,S,-1),K,1)),'wrong correction source')
        bad_target+=unit_entry(physical(unit,S,wrong,K)) is None
        bad_omitted_map+=unit_entry(physical(unit,RU,RE,identity)) is None
        wrong_phase=({x:(-r,-i) for x,(r,i) in restored[0].items()},restored[1])
        bad_inverse_phase+=not equal(wrong_phase,unit)
    require(bad_target==N and bad_omitted_map==N and bad_inverse_phase==N,'mutation control')
    # Independently check inverse-transpose of the whole two-register macro.
    perm=[x[0] for x in recipes['prelude']];phase=[x[1] for x in recipes['prelude']]
    inverse=[0]*N
    for x,y in enumerate(perm):inverse[y]=x
    dual=(perm,inverse,[(-p)%4 for p in phase])
    for column in range(N):
        unit=({column:(1,0)},0)
        require(equal(mono(mono(unit,dual,1),dual,-1),unit),'dual source round trip')
        # Y input column: dual scalar adds -Y/2 into warped source, then unwarps.
        actual=mono(({column:(-1,0)},1),dual,-1)
        x=inverse[column]
        expected=({x:rotate((-1,0),phase[x])},1)
        require(equal(actual,expected),'dual macro differs from inverse transpose')
    cases={};pins={}
    for name,tag in [('gauge44','base'),('extra','extra')]:
        canon=SOURCE/'inputs'/(name+'.canonical.json.gz');emitted=SOURCE/'words'/('BORROW-WORD-80'+tag+'.json.gz')
        w=read(canon);word=read(emitted);v=w['v'];pins[str(canon.relative_to(SOURCE))]=sha(canon);pins[str(emitted.relative_to(SOURCE))]=sha(emitted)
        require(w['frames'][w['start'][33]]==[138] and w['frames'][211]==U,'actual source frame pins')
        coeff={162:Q(-1),220:Q(1)}
        for g in w['precondition']:
            if g[0]=='scale':
                if g[1] in coeff:coeff[g[1]]*=Q(g[2],g[3])
            else:
                t,s=g[1:3];value=coeff.get(t,Q(0))+Q(g[3],g[4])*coeff.get(s,Q(0))
                if value:coeff[t]=value
                else:coeff.pop(t,None)
        require(set(coeff)==TARGETS,'precondition transports outside target set')
        require(coeff=={135:Q(1,2),146:Q(-1,2),162:Q(1,2),220:Q(1,2)},'exact transported coefficients')
        first={}
        for t in sorted(TARGETS):
            events=[(part,i,g) for part in ('A','B') for i,g in enumerate(word[part])
                    if t in (g[1:3] if g[0]=='add' else g[1:2])]
            require(events and events[0][0]=='B' and span(events[0][2][-1])==span([30]),'first target touch is not line30')
            require(all(30 in span(g[-1]) for _,_,g in events),'later target frame excludes line30')
            first[t]=dict(section=events[0][0],index=events[0][1],frame=events[0][2][-1])
        centers=dict(zip(word['centers'],word['center_frames']));affected=set();old=Counter();new=Counter();center_evidence=[]
        require(word['target_levels']=={},'unexpected old target levels')
        for center,C in centers.items():
            served={g[1] for g in word['cut'] if g[2]==center}
            require(len(C)==8 and served,'center geometry')
            old[8]+=1
            if served&TARGETS:
                require(served-TARGETS,'affected center has no remaining frame-zero target')
                require(30 in span(C),'center does not contain line30')
                affected.add(center);new[7]+=1;new[1]+=1
                center_evidence.append(dict(center=center,basis=C,raised_targets=sorted(served&TARGETS),other_targets=len(served-TARGETS)))
            else:new[8]+=1
        require(affected=={9,92,224,240},'affected center set')
        delta={k:new[k]-old[k] for k in set(old)|set(new) if new[k]!=old[k]}
        require(delta=={1:4,7:4,8:-4} and sum(k*c for k,c in delta.items())==0,'COPY delta')
        cases[name]=dict(precondition_transported_coefficients={str(t):str(q) for t,q in sorted(coeff.items())},
                         first_target_touches=first,all_later_target_frames_contain_line30=True,
                         moved_target_climbs={'1':4},moved_target_climb_profile_delta={},center_evidence=center_evidence,
                         center_copy_profile_delta=delta,center_copy_mass_delta=0)
    result=dict(status='PASS_INDEPENDENT_FLAG_PRELUDE_INTERFACE_NOT_NATIVE_ADMISSION',
                G_columns=G,source_entrance=[138],raised_target_frame=[30],source_retirement=U,handoff_basis=E,
                exact_columns_each=N,dual_macro_source_columns=N,dual_macro_target_columns=N,recipe_sha256={k:hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest() for k,v in recipes.items()},
                negative_controls=dict(wrong_target_line_nonmonomial_columns=bad_target,omitted_G_handoff_nonmonomial_columns=bad_omitted_map,wrong_inverse_phase_failed_columns=bad_inverse_phase),
                source_sha256=pins,cases=cases,
                scope='Exact prelude/handoff operators and source restoration on512 columns; target transport and internal COPY delta. Lender restoration at later handoff, complete changed program, backward/dual replay, recursive labels, prefix/row bounds, global hosting and outer bound remain separate obligations.')
    (HERE/'FLAG-PRELUDE-INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()

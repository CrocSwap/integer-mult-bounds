"""Integer-power certificate; no logarithm, exp, repair or original pricer import.
@woklerx with substantial OpenAI Codex assistance, Apache-2.0.
"""
import json,hashlib
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
def need(v,s):
    if not v:raise ValueError(s)
def root10(z):
    x=1<<((z.bit_length()+9)//10)
    while True:
        y=(9*x+z//x**9)//10
        if y>=x:break
        x=y
    while x**10>z:x-=1
    while (x+1)**10<=z:x+=1
    return x

def audit(c):
    need(c['status']=='PASS_DEFAULT_PRECISION_FALSE_BRACKETS_AND_CERTIFIED_REPAIR','status')
    need((c['default_terms'],c['default_digits'])==(34,24),'original defaults')
    need(len(c['fixtures'])==4,'four-case coverage')
    a=Q(1,20);d=Q(1,10**24);seen=set();false=0
    for row in c['fixtures']:
        surcharge=row['surcharge'];offset=row['offset'];seen.add((surcharge,offset))
        need(type(surcharge) is bool and type(offset) is int and offset in (0,1),'case types')
        m,W=row['m'],row['W'];need(m==9 and W==10**64,'fixed dimensions')
        factor=Q(1)+(Q(2592,10**16) if surcharge else Q(0));need(Q(row['factor'])==factor,'surcharge')
        p,q=factor.numerator,factor.denominator;B=m*W
        N=root10((B*q)**10//(3*p**10));need(3*(N*p)**10<(B*q)**10<3*((N+1)*p)**10,'algebraic floor')
        need(row['n']=={'1':N+offset},'coefficient count')
        n=N+offset;need(n*factor<B,'root strictly positive')
        need(9*(n*p)**5>(B*q)**5,'root below1/10')
        need(N*d>1,'strict adjacent tick separation')
        # 9^d >1+d, since log9>1. The algebraic floor then proves:
        # N*A*9^(a+d)>B and (N+1)*A*9^(a-d)<B.
        neighboring_sign=(Q(N,N+1)*(1+d)>1) if offset==0 else (Q(N+1,N)/(1+d)<1)
        need(neighboring_sign,'rational neighboring sign')
        truth=[a,a+d] if offset==0 else [a-d,a]
        need(row['known_root_side_of_1_over_20']==('above' if offset==0 else 'below'),'root-side claim')
        need(list(map(Q,row['repair']['certified_bracket']))==truth,'true repaired bracket')
        need(row['repair']['status']=='CERTIFIED','repair status')
        legacy=list(map(Q,row['legacy_bracket']));need(legacy==[a-d,a],'legacy returned bracket')
        nomination=list(map(Q,row['legacy_nomination_bracket']));need(nomination[0]<a-d and nomination[1]>a+d,'nomination already encloses true root')
        excluded=offset==0;need(row['legacy_bracket_excludes_root'] is excluded,'false bracket classification')
        false+=excluded
        coarse=list(map(Q,row['normalized_residual_at_grid_terms34']));need(coarse[0]<0<coarse[1],'legacy uncertainty')
    need(seen=={(False,0),(False,1),(True,0),(True,1)} and false==2,'complete witness pairs')
    need(c['false_brackets']==2 and c['neighbor_controls']==2,'reported coverage')
    cap=c['capped_control'];need(cap['status']=='UNRESOLVED_INTERIOR_SIGN','bounded budget must not certify')
    need(list(map(Q,cap['certified_bracket']))==[Q(0),Q(1,10)],'initial certified bracket retained')
    return dict(status='PASS_INDEPENDENT_INTEGER_POWER_ROOT_SEPARATION',cases=4,false_brackets=2,neighbor_controls=2,transcendental_library_calls=0)

if __name__=='__main__':print(json.dumps(audit(json.loads((P/'EXPECTED.json').read_bytes())),sort_keys=True))

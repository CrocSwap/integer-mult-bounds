"""Literal independent body-bearing retirement, followed by retained D retirement."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
def ordinary_inverse(events):
    out=deepcopy(list(reversed(events)))
    for e in out:
        if e[0]=='ADD': e[-1]=str(-Q(e[-1]))
        elif e[0]=='SCALE': e[-1]=str(1/Q(e[-1]))
        elif e[0]=='LAMBDA': e[-1]=-e[-1]
        elif e[0]!='SWAP': raise ValueError('ordinary inverse opcode')
    return out

SLOTS={'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),'Q_POWER':(1,),'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}

def retire(w,pivot,E,A,stages,head,expected_cut):
    w=deepcopy(w);fresh=w['roles'];cut=w['events'].index(['IDLE_ONE',2,stages])
    assert cut==expected_cut
    def rename(e):
        e=deepcopy(e)
        for j in SLOTS[e[0]]:
            if e[j]==pivot:e[j]=fresh
        return e
    ev=E+w['events'][:cut+1]+A;handoff=len(ev)-1
    ev +=[rename(e)for e in ordinary_inverse(A)+w['events'][cut+1:]+ordinary_inverse(E)]
    old=w['diagonal'][pivot];prefix=[0]*(w['stages']+2);prefix[0]=-head
    for s in stages:prefix[s+1]=1
    suffix=[x-y for x,y in zip(old,prefix)]
    w['events']=ev;w['roles']+=1;w['diagonal'][pivot]=prefix;w['diagonal'].append(suffix)
    w['schema']='two-paid-fragments-two-independent-retirements/1'
    return w,dict(cut_after=cut,handoff_after=handoff,pivot=pivot,fresh=fresh,input_basis=E,cut_basis=A,prefix_stages=stages,head=head,prefix_target=prefix,suffix_target=suffix)

def construct(base):
    one,a=retire(base,6,[['ADD', 6, 7, '1'], ['SCALE', 6, '-1'], ['ADD', 7, 6, '2'], ['SWAP', 6, 7], ['ADD', 7, 6, '-1']],[['ADD', 0, 2, '1'], ['ADD', 2, 1, '-1'], ['SWAP', 2, 6]],[5, 6, 7, 8],0,158)
    two,b=retire(one,4,[['SCALE', 5, '-1'], ['SCALE', 4, '-1'], ['ADD', 5, 4, '-2']],[['ADD', 1, 2, '1'], ['ADD', 2, 0, '-1'], ['SWAP', 2, 4], ['LAMBDA', 4, -1]],[10],1,394)
    return one,two,[a,b]

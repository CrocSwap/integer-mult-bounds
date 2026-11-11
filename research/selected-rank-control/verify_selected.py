"""Exact finite tests for rank-one cutoff/remainder control."""
import json
from fractions import Fraction
from selected_control import compile_selected,inputs,Machine,ONE,BLANK,CUTOFF

def need(ok,msg):
    if not ok:raise ValueError(msg)

def oracle(m,s,e,L):
    if e<max(m,L):return [('L',e),('X',e)],e,1,0
    r=e%m;q=e//m;out=[('E',e),(f'B{r}',e)];mass=e;nodes=1;depth=0
    for i in range(s):
        ev,z,n,d=oracle(m,s,q,L);out += [(f'D{i}',q)]+ev+[(f'U{i}',e)];mass+=z;nodes+=n;depth=max(depth,d+1)
    return out+[(f'A{r}',e),('X',e)],mass,nodes,depth

def observed(code,tapes,bound):
    z=Machine(code,tapes);ev=[]
    while not z.halted:
        need(z.steps<bound,'transition budget')
        ins=code[z.pc]
        if ins[0]=='emit':ev.append((ins[1],sum(x==ONE for x in tapes[0].cells.values())))
        z.step()
    return z,ev

def one(m,s,e,L,org=(0,0,0,0)):
    code,abc=compile_selected(m,s);need(len(code)==30*m+42+s*(69+3*m),'instruction formula')
    ts=inputs(e,L,org);snap=[(x.cells.copy(),x.head) for x in ts]
    ev,mass,nodes,d=oracle(m,s,e,L);z,seen=observed(code,ts,200*(s+1)*mass)
    need(seen==ev,'width/remainder/shape')
    need(all(x.cells==c and x.head==h for x,(c,h) in zip(ts,snap)),'restoration')
    need(all(x.low>=o-1 for x,o in zip(ts,org)),'ancestor locality')
    span=sum(x.high-x.low+1 for x in ts)
    need(span<=2*(e+2)+Fraction(e,1-Fraction(1,m))+d+2+min(e,L)+2,'backing')
    need(ts[3].high-org[3]<=min(e,L),'cutoff prefix')
    return z.steps,nodes,mass,ev

def dense(code,ts,limit):
    lo=min(x.head for x in ts)-30;hi=max(x.head for x in ts)+10000
    arr=[[BLANK]*(hi-lo+1) for _ in ts];heads=[x.head for x in ts]
    for j,t in enumerate(ts):
        for p,c in t.cells.items():arr[j][p-lo]=c
    pc=steps=0;ev=[]
    while steps<limit:
        ins=code[pc];op=ins[0];steps+=1
        if op=='halt':return steps,ev,heads,arr,lo
        if op=='goto':pc=ins[1];continue
        if op=='read':pc=ins[2][arr[ins[1]][heads[ins[1]]-lo]];continue
        if op=='move':heads[ins[1]]+=ins[2]
        elif op=='write':arr[ins[1]][heads[ins[1]]-lo]=ins[2]
        elif op=='emit':ev.append((ins[1],arr[0].count(ONE)))
        else:raise ValueError('dense opcode')
        pc+=1
    raise ValueError('dense budget')

def main():
    count=steps=nodes=0
    for m in range(2,6):
        for s in range(1,4):
            for e in range(1,21):
                for L in range(1,11):
                    t,n,_,_=one(m,s,e,L);count+=1;steps+=t;nodes+=n
    independent=0
    for m,s,e,L in [(3,2,14,5),(3,3,27,9),(5,3,76,15),(2,5,64,3)]:
        for org in [(0,0,0,0),(-7,19,31,-11)]:
            code,_=compile_selected(m,s);t,n,mass,ev=one(m,s,e,L,org);orig=inputs(e,L,org)
            dt,de,dh,da,lo=dense(code,inputs(e,L,org),t+1)
            need((dt,de,dh)==(t,ev,list(org)),'independent CPU')
            need(all({k+lo:v for k,v in enumerate(a) if v!=BLANK}==o.cells for a,o in zip(da,orig)),'dense cells')
            independent+=1
    controls=[]
    for m,s in [(1,2),(3,0),(3,True)]:
        try:compile_selected(m,s)
        except ValueError:controls.append('invalid-template')
        else:raise ValueError('invalid accepted')
    code,_=compile_selected(3,2);bad=list(code)
    j=next(i for i,x in enumerate(bad) if x[0]=='read' and x[1]==CUTOFF)
    targets=dict(bad[j][2]);targets[BLANK]=bad[j+1][2][BLANK];bad[j]=('read',CUTOFF,targets)
    _,ev=observed(tuple(bad),inputs(5,5),5000);need(ev!=oracle(3,2,5,5)[0],'equality cutoff fault');controls.append('equality-cutoff')
    for mode in ['wrong','omitted']:
        bad=list(code);j=next(i for i,x in enumerate(bad) if x==('emit','A1'))
        bad[j]=('emit','A0') if mode=='wrong' else ('goto',j+1)
        _,ev=observed(tuple(bad),inputs(4,1),5000);need(ev!=oracle(3,2,4,1)[0],'post remainder fault');controls.append(mode+'-post-remainder')
    bad=list(code);j=next(i for i,x in enumerate(bad) if x==('move',CUTOFF,1));bad[j]=('move',CUTOFF,0)
    try:z,ev=observed(tuple(bad),inputs(8,5),5000)
    except (ValueError,KeyError):caught=True
    else:caught=ev!=oracle(3,2,8,5)[0]
    need(caught,'cutoff motion fault');controls.append('cutoff-head')
    need(2*(5//3)==2 and (2*5)//3==3,'mixed rounding control');controls.append('raw-mixed-law-mismatch')
    print(json.dumps({'status':'PASS_SELECTED_UNIFORM_CONTROL','cases':count,'transitions':steps,'nodes':nodes,'independent_dense_cases':independent,'controls':len(controls),'m3_sites2_instructions':len(code),'remainder_zero':'explicit B0/A0 hooks; consumer must skip payload work','kappa':'unchanged','cutoff':'supplied input; production not claimed'},sort_keys=True,indent=2))
if __name__=='__main__':main()

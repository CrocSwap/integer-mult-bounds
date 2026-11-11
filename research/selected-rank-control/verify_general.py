"""Finite corroboration of the written all-size theorem."""
import itertools,json
from fractions import Fraction
from controller_reference import compile_controller,initial_tapes,Machine,BLANK,ONE,MARK

def need(ok,why):
    if not ok: raise ValueError(why)

def oracle(m,ranks,f):
    ev=['L'] if f<m else ['E']; mass=f; nodes=1; depth=0
    if f>=m:
        for i,r in enumerate(ranks):
            e,t,n,d=oracle(m,ranks,r*f//m)
            ev += [f'D{i}']+e+[f'U{i}']; mass+=t; nodes+=n; depth=max(depth,d+1)
    return ev+['X'],mass,nodes,depth

def width_oracle(m,ranks,f):
    result=[('L' if f<m else 'E',f)]
    if f>=m:
        for i,r in enumerate(ranks):
            child=r*f//m
            result += [(f'D{i}',child)]+width_oracle(m,ranks,child)+[(f'U{i}',f)]
    return result+[('X',f)]

def observed_run(code,tapes,bound):
    z=Machine(code,tapes); widths=[]
    while not z.halted:
        need(z.steps<bound,'transition bound')
        instruction=code[z.pc]
        if instruction[0]=='emit':
            widths.append((instruction[1],sum(s==ONE for s in tapes[0].cells.values())))
        z.step()
    return z,widths

def run_case(m,ranks,f,origins=(0,0,0)):
    code,abc=compile_controller(m,ranks)
    need(len(code)==10*m+13+len(ranks)*(67+3*m)+2*sum(ranks),'state formula')
    need(len(abc)==len(ranks)+4,'alphabet formula')
    tapes=initial_tapes(f,origins); saved=[(t.cells.copy(),t.head) for t in tapes]
    ev,mass,nodes,depth=oracle(m,ranks,f); bound=100*(len(ranks)+1)*mass
    z,seen_widths=observed_run(code,tapes,bound)
    need(seen_widths==width_oracle(m,ranks,f),'event-width mismatch')
    need(z.events==ev,'shape/event mismatch')
    need(all(t.cells==c and t.head==h for t,(c,h) in zip(tapes,saved)),'endpoint')
    need(all(t.low>=o-1 for t,o in zip(tapes,origins)),'ancestor visit')
    span=sum(t.high-t.low+1 for t in tapes); rho=Fraction(max(ranks),m)
    need(span<=2*(f+2)+Fraction(f,1-rho)+depth+2,'retained span')
    return z.steps,nodes,mass,z.events

def dense_run(code,tapes,limit):
    lo=min(t.head for t in tapes)-100; hi=max(t.head for t in tapes)+20000
    a=[[BLANK]*(hi-lo+1) for _ in tapes]; h=[t.head for t in tapes]
    for j,t in enumerate(tapes):
        for p,s in t.cells.items(): a[j][p-lo]=s
    pc=steps=0; events=[]
    while steps<limit:
        ins=code[pc]; op=ins[0]; steps+=1
        if op=='halt': return steps,events,h,a,lo
        if op=='read': pc=ins[2][a[ins[1]][h[ins[1]]-lo]]; continue
        if op=='goto': pc=ins[1]; continue
        if op=='move': h[ins[1]]+=ins[2]
        elif op=='write': a[ins[1]][h[ins[1]]-lo]=ins[2]
        elif op=='emit': events.append(ins[1])
        else: raise ValueError('dense opcode')
        pc+=1
    raise ValueError('dense budget')

def main():
    count=steps=nodes=0; ratio=Fraction(0)
    for m in range(2,5):
        for s in range(1,4):
            for ranks in itertools.product(range(1,m),repeat=s):
                for f in range(1,17):
                    st,no,mass,_=run_case(m,ranks,f)
                    count+=1; steps+=st; nodes+=no; ratio=max(ratio,Fraction(st,(s+1)*mass))
    independent=0
    for m,ranks,f in [(2,(1,1,1),32),(5,(1,3,4),17),(7,(2,3,6),21)]:
        for org in [(0,0,0),(-19,29,7),(73,-11,41)]:
            code,_=compile_controller(m,ranks); original=initial_tapes(f,org)
            st,no,mass,ev=run_case(m,ranks,f,org)
            ds,de,dh,da,lo=dense_run(code,initial_tapes(f,org),st+1)
            need((ds,de,dh)==(st,ev,list(org)),'dense CPU mismatch')
            for j,t in enumerate(original):
                need({i+lo:v for i,v in enumerate(da[j]) if v!=BLANK}==t.cells,'dense restoration')
            independent+=1
    controls=[]
    for m,ranks in [(1,(1,)),(3,(0,)),(3,(3,)),(3,()),(3,(True,))]:
        try: compile_controller(m,ranks)
        except ValueError: controls.append('invalid-profile')
        else: raise ValueError('invalid profile admitted')
    code,_=compile_controller(3,(1,2)); expected,mass,_,_=oracle(3,(1,2),9)
    bad=list(code); j=next(i for i,x in enumerate(bad) if x==('write',2,'t0')); bad[j]=('write',2,'t1')
    need(Machine(tuple(bad),initial_tapes(9)).run().events!=expected,'wrong return missed'); controls.append('wrong-return')
    bad=list(code); j=next(i for i,x in enumerate(bad) if x==('write',1,BLANK)); bad[j]=('write',1,ONE)
    try:
        z=Machine(tuple(bad),initial_tapes(9)).run(1000)
    except ValueError: detected=True
    else: detected=z.events!=expected or z.tapes[1].cells!={-1:MARK}
    need(detected,'scratch leak missed'); controls.append('scratch-leak')
    bad=list(code); j=next(i for i,x in enumerate(bad) if x==('write',1,ONE)); bad[j]=('write',1,BLANK)
    try: z=Machine(tuple(bad),initial_tapes(9)).run(1000)
    except ValueError: detected=True
    else: detected=z.events!=expected
    need(detected,'floor-transducer fault missed'); controls.append('floor-transducer')
    narrow,_=compile_controller(3,(2,)); bad=list(narrow)
    j=next(i for i,x in enumerate(bad) if x==('write',1,ONE)); bad[j]=('goto',j+2)
    z,seen=observed_run(tuple(bad),initial_tapes(3),1000)
    good,_,_,_=oracle(3,(2,),3)
    need(z.events==good and seen!=width_oracle(3,(2,),3),'shape-only width fault missed')
    controls.append('shape-identical-wrong-width')
    try: Machine(code,initial_tapes(9)).run(1)
    except ValueError: controls.append('undercharged-time')
    else: raise ValueError('undercharged run admitted')
    blowup=[]
    for d in range(9):
        f=2**d; expected_nodes=(3**(d+1)-1)//2
        _,_,n,_=oracle(2,(1,1,1),f); need(n==expected_nodes,'node formula')
        blowup.append({'depth':d,'width':f,'nodes':n})
    print(json.dumps({'status':'PASS_ONLINE_RANK_CONTROL','finite_cases':count,'transitions':steps,'nodes':nodes,
      'independent_dense_cases':independent,'negative_controls':len(controls),'maximum_observed_steps_over_splus1_mass':str(ratio),
      'shape_blowup':blowup,'kappa':'unchanged','formal_kernel':'not_run','selected_payload_implementation':'not_claimed'},sort_keys=True,indent=2))
if __name__=='__main__': main()

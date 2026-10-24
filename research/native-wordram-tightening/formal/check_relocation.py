"""Finite executable controls for DIRTY-ARENA-RELOCATION.md, not a kernel proof."""
import json, random

def need(p,m):
    if not p: raise ValueError(m)

def step(program,state,w):
    if state is None: return None
    pc,mem,inp,out=state
    if pc>=len(program): return None
    ins=program[pc];op=ins[0];a=ins[1:];mod=1<<w
    mem=mem.copy();nxt=pc+1
    get=lambda i:mem[i%mod]
    def put(i,v): mem[i%mod]=v%mod
    if op=='halt': return None
    if op=='set':put(a[0],a[1])
    elif op=='load':put(a[0],get(get(a[1])))
    elif op=='store':put(get(a[0]),get(a[1]))
    elif op=='jump':nxt=a[0]
    elif op=='jzero':nxt=a[1] if get(a[0])==0 else nxt
    elif op=='read':
        if not inp:return None
        put(a[0],inp[0]);inp=inp[1:]
    elif op=='write':out=out+(get(a[0])%mod,)
    elif op=='not':put(a[0],mod-1-get(a[1]))
    else:
        x,y=get(a[1]),get(a[2])
        if op=='add':v=x+y
        elif op=='sub':v=max(x-y,0)
        elif op=='mul':v=x*y
        elif op=='div':v=x//y if y else 0
        elif op=='and':v=x&y
        elif op=='shiftl':v=x<<y
        else:raise ValueError(op)
        put(a[0],v)
    return nxt,mem,inp,out

def relocated(program,b,A):
    c,s=b+A,b+A+1;pad=('set',s,0);result=[('set',c,b)]
    for ins in program:
        op=ins[0];a=ins[1:]
        if op=='load':block=[('add',s,c,b+a[1]),('load',b+a[0],s),pad]
        elif op=='store':block=[('add',s,c,b+a[0]),('store',s,b+a[1]),pad]
        elif op=='jump':block=[pad,pad,('jump',1+3*a[0])]
        elif op=='jzero':block=[pad,pad,('jzero',b+a[0],1+3*a[1])]
        elif op=='halt':block=[pad,pad,('halt',)]
        elif op=='set':block=[('set',b+a[0],a[1]),pad,pad]
        else:block=[(op,*(b+i for i in a)),pad,pad]
        result.extend(block)
    return result

def main():
    checks=0;admissible=0;w=8;A=16;b=41;mod=1<<w
    for seed in range(1200):
        rng=random.Random(seed)
        program=[]
        for j in range(35):
            op=rng.choice(('set','load','store','jump','jzero','read','write','not',
                           'add','sub','mul','div','and','shiftl','halt'))
            a=rng.randrange(A)
            if op=='halt':ins=(op,)
            elif op=='set':ins=(op,a,rng.randrange(mod))
            elif op=='jump':ins=(op,rng.randrange(40))
            elif op=='jzero':ins=(op,a,rng.randrange(40))
            elif op in ('read','write'):ins=(op,a)
            elif op in ('load','store','not'):ins=(op,a,rng.randrange(A))
            else:ins=(op,a,rng.randrange(A),rng.randrange(A))
            program.append(ins)
        mem=[rng.randrange(mod) for _ in range(mod)]
        for i in range(A):mem[i]=rng.randrange(A)
        targetmem=[rng.randrange(mod) for _ in range(mod)]
        for i in range(A):targetmem[b+i]=mem[i]
        outside=targetmem.copy();inp=tuple(rng.randrange(mod) for _ in range(40))
        source=(0,mem,inp,());target=(0,targetmem,inp,())
        q=relocated(program,b,A);target=step(q,target,w)
        for t in range(80):
            pc,mem,_,_=source
            if pc<len(program):
                ins=program[pc]
                if ins[0]=='load' and mem[ins[2]]>=A:break
                if ins[0]=='store' and mem[ins[1]]>=A:break
            sn=step(program,source,w)
            for _ in range(3):target=step(q,target,w)
            if sn is None:
                need(target is None,'halt mismatch');checks+=1;break
            need(target is not None,'early halt')
            need(target[0]==1+3*sn[0],'counter')
            need(target[2:]==sn[2:],'input/output')
            need(all(target[1][b+i]==sn[1][i] for i in range(A)),'active cells')
            need(all(target[1][i]==outside[i] for i in range(mod)
                     if not b<=i<b+A+2),'dirty exterior')
            checks+=1;admissible+=1;source=sn
    print(json.dumps({'status':'PASS_FINITE_REGRESSION_ONLY','seeds':1200,
                     'checked_step_or_halt_correspondences':checks,
                     'checked_completed_steps':admissible},indent=2))

if __name__=='__main__':main()

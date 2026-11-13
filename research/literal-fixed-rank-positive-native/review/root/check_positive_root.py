"""Independent sparse Graph CPU and closed Hamming-kernel oracle for rank-four positive central join."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,sys,time
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).with_name('source').resolve()
sys.path.insert(0,str(P))
import adapter as a
def require(ok,why):
    if not ok:raise ValueError(why)
def word(x,w):return format(x%(1<<w),f'0{w}b')
def gamma(x):
    b=bin(x)[2:];return '0'*(len(b)-1)+b

def interpret(graph,fields,stages,budget=90000000):
    origins=[-31+7*t for t in range(a.TAPES)];heads=origins.copy()
    text=['^'+'|'.join(fields)+'|$']+['^']*(a.TAPES-1)
    tapes=[{o+i:c for i,c in enumerate(s)} for o,s in zip(origins,text)]
    for t,o in enumerate(origins):tapes[t][o-4]='1';tapes[t][o+1000000]='0'
    low=origins.copy();high=[o+len(s)-1 for o,s in zip(origins,text)];high[-1]+=100003
    entry=sum(y-x+1 for x,y in zip(low,high));pc=graph.start;steps=writes=early=0
    returned=False;checkpoints={}
    while pc!='HALT':
        if pc==stages['primitive_return']:returned=True
        if pc in (stages['core_entry'],stages['core_return'],stages['primitive_return']):
            checkpoints[pc]=dict(steps=steps,home_writes=writes)
        found=None
        for rule in graph.rules[pc]:
            if all(tapes[t].get(heads[t],'_')==c for t,c in rule.tests):
                require(found is None,'ambiguous transition');found=rule
        require(found is not None,'literal rejection in valid fresh fixture')
        for t,c in found.writes:
            require(heads[t]!=origins[t] or c=='^','origin changed')
            if c=='_':tapes[t].pop(heads[t],None)
            else:tapes[t][heads[t]]=c
            if t==0:writes+=1;early+=not returned
        for t,d in found.moves:
            require(d in (-1,0,1),'nonunit head');heads[t]+=d
            low[t]=min(low[t],heads[t]);high[t]=max(high[t],heads[t])
        pc=found.target;steps+=1;require(steps<=budget,'bounded sparse CPU exhausted')
    require(heads==origins,'head restoration')
    for t,o in enumerate(origins):
        require(tapes[t].get(o)=='^' and tapes[t].get(o-4)=='1' and tapes[t].get(o+1000000)=='0','origin/exterior')
        if t:require(set(tapes[t])=={o,o-4,o+1000000},'private retirement')
    raw=''.join(tapes[0].get(origins[0]+i,'_') for i in range(len(text[0])))
    require(raw.startswith('^') and raw.endswith('|$'),'HOME framing')
    return raw[1:-2].split('|'),dict(steps=steps,HOME_writes=writes,early_HOME_writes=early,
        entry_head_history=entry,final_head_history=sum(y-x+1 for x,y in zip(low,high)),checkpoints=checkpoints)


def multiply(x,y):
    a,b=x;c,d=y
    return a*c-b*d,a*d+b*c

def power(z,n):
    r=(1,0)
    for _ in range(n):r=multiply(r,z)
    return r

def closed_tensor(values,rank,sign=1):
    """Direct matrix kernel by Hamming distance, not sequential gate replay.

    Stream addresses put the first native slot in the most-significant bit.
    C tensor rank has entry (1+i)^(rank-h)(1-i)^h /2^rank.
    Every inactive low-bit spectator is retained separately.
    """
    count=1<<rank;spectators=1<<(9-rank);den=1<<rank
    kernels=[multiply(power((1,sign),rank-h),power((1,-sign),h)) for h in range(rank+1)]
    out=[None]*512
    for tail in range(spectators):
        for target in range(count):
            re=im=0
            for source in range(count):
                z=multiply(kernels[(target^source).bit_count()],values[source*spectators+tail])
                re+=z[0];im+=z[1]
            require(re%den==im%den==0,'closed kernel exact Gaussian output')
            out[target*spectators+tail]=(re//den,im//den)
    return out

def check_embedding(graph,stages,core,rank):
    labels=[s for s in graph.rules if s.startswith('POSITIVE_R'+str(rank)+'.')]
    require(len(labels)==len(core),'complete core state count')
    for i,(op,*args) in enumerate(core):
        nxt=labels[i+1] if i+1<len(labels) else stages['core_return']
        if op=='read':expected=[a.D.Rule(((a.CORE_BASE+args[0],c),),(),(),labels[j]) for c,j in args[1].items()]
        elif op=='write':expected=[a.D.Rule((),((a.CORE_BASE+args[0],args[1]),),(),nxt)]
        elif op=='move':expected=[a.D.Rule((),(),((a.CORE_BASE+args[0],args[1]),),nxt)]
        elif op=='goto':expected=[a.D.Rule((),(),(),labels[args[0]])]
        else:
            require(op=='halt','literal core operation')
            expected=[a.D.Rule((),(),(),stages['core_return'])]
        require(graph.rules[labels[i]]==expected,'exact core embedding')

def main():
    rank=4;graph,stages=a.compile_home(rank);core=a.core(rank)
    check_embedding(graph,stages,core,rank)
    values=[(16*((19*n+7)%3-1),16*((11*n+5)%3-1)) for n in range(512)]
    exact=closed_tensor(values,rank)
    require(exact!=values,'nonidentity witness')
    require(exact!=closed_tensor(values,rank-1),'missing fourth slot control')
    require(exact!=closed_tensor(values,rank,sign=-1),'positive orientation control')
    width=10
    require(all(-(1<<(width-1))<=z<(1<<(width-1)) for v in exact for z in v),'final signed width')
    header=''.join(gamma(n) for n in (1,1,1,1,width,rank))
    packet=header+''.join(word(z,width) for v in values for z in v)
    expected=header+''.join(word(z,width) for v in exact for z in v)
    parked=('1101010001'*((len(packet)+9)//10))[:len(packet)]
    actual,receipt=interpret(graph,(parked,packet),stages)
    require(actual==[parked,expected],'closed tensor output and parked HOME')
    require(receipt['HOME_writes']==len(packet) and receipt['early_HOME_writes']==0,'one late complete scatter')
    V=2*512*width;E=len(header);F=V+E
    require(receipt['steps']<=128*(F+1)+(1<<24)*(V+E+1),'complete direct time bound')
    require(receipt['final_head_history']<=receipt['entry_head_history']+2112*(F+1),'historical backing bound')
    result={'status':'PASS_ROOT_RANK4_POSITIVE_HOME','rank':rank,'shape':[1,1,1,1,width,rank],
        'states':len(graph.rules),'tapes':a.TAPES,'core_instructions':len(core),
        'core_sha256':hashlib.sha256(repr(core).encode()).hexdigest(),'F':F,'receipt':receipt,
        'input_sha256':hashlib.sha256(packet.encode()).hexdigest(),
        'output_sha256':hashlib.sha256(expected.encode()).hexdigest(),
        'oracle':'Independent direct Hamming-distance tensor kernel with integer Gaussian numerators, not emitted swaps or author oracle',
        'controls':['missing fourth slot gives different output','negative direction gives different output'],
        'scope':'One complete nontrivial rank4 f1 call plus static embedding audit; universal proof is separate and no caller or nonleaf tariff is admitted.'}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()

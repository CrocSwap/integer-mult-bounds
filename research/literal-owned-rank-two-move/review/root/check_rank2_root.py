"""Independent sparse Graph CPU and dense rational original-frame oracle for MOVE28141."""
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

def interpret(graph,fields,stages,budget=60000000):
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

def rotate(z,k):
    r,i=z
    return ((r,i),(-i,r),(-r,-i),(i,-r))[k%4]

def original_frame(values,directions,sign):
    """Dense Fractions, span-set basis extension and inverse permutation.

    This is a separate evaluation of the original frame definition, without
    importing either the native verifier or the emitted rank-two recipe.
    """
    span={0};columns=[]
    for v in (*directions,*(1<<j for j in range(9))):
        if v not in span:
            columns.append(v);span|={x^v for x in tuple(span)}
    require(len(columns)==9 and len(span)==512,'complete frame basis')
    perm=[]
    for n in range(512):
        z=0
        for j,c in enumerate(columns):
            if n>>j&1:z^=c
        perm.append(z)
    inverse=[0]*512
    for j,k in enumerate(perm):inverse[k]=j
    dual=[inverse[1<<j] for j in range(9)]
    q=[[int(i==j)^((dual[i]&dual[j]).bit_count()%2) for j in range(9)] for i in range(9)]
    phases=[]
    for n in range(512):
        bits=[n>>j&1 for j in range(9)]
        phases.append((sum(q[j][j]*bits[j] for j in range(9))+2*sum(q[j][k]*bits[j]*bits[k] for j in range(9) for k in range(j+1,9)))%4)
    v=[(Fraction(0),Fraction(0))]*512
    for n,z in enumerate(values):v[inverse[n]]=rotate(z,-phases[n])
    for axis in range(len(directions)):
        w=[None]*512;bit=1<<axis
        for n in range(512):
            if n&bit:continue
            a,b=v[n];c,d=v[n|bit]
            w[n]=((a-sign*b+c+sign*d)/2,(b+sign*a+d-sign*c)/2)
            w[n|bit]=((a+sign*b+c-sign*d)/2,(b-sign*a+d+sign*c)/2)
        v=w
    out=[None]*512
    for n,z in enumerate(v):out[perm[n]]=rotate(z,phases[perm[n]])
    return out

def source_image(values,reverse=False):
    rev=lambda n:int(format(n,'09b')[::-1],2)
    x=[None]*512
    for n,z in enumerate(values):x[rev(n)]=tuple(Fraction(a) for a in z)
    if reverse:x=original_frame(original_frame(x,(75,137,265),-1),(137,),1)
    else:x=original_frame(original_frame(x,(137,),-1),(75,137,265),1)
    out=[x[rev(n)] for n in range(512)]
    require(all(z.denominator==1 for row in out for z in row),'exact final source image')
    return [tuple(int(z) for z in row) for row in out]

def main():
    graph,stages=a.compile_home();core=a.core()
    labels=[s for s in graph.rules if s.startswith('MOVE28141.')]
    require(len(labels)==len(core),'core location count')
    for i,(op,*args) in enumerate(core):
        nxt=labels[i+1] if i+1<len(labels) else stages['core_return']
        if op=='read':expected=[a.D.Rule(((a.CORE_BASE+args[0],c),),(),(),labels[j]) for c,j in args[1].items()]
        elif op=='write':expected=[a.D.Rule((),((a.CORE_BASE+args[0],args[1]),),(),nxt)]
        elif op=='move':expected=[a.D.Rule((),(),((a.CORE_BASE+args[0],args[1]),),nxt)]
        elif op=='goto':expected=[a.D.Rule((),(),(),labels[args[0]])]
        else:require(op=='halt','core opcode');expected=[a.D.Rule((),(),(),stages['core_return'])]
        require(graph.rules[labels[i]]==expected,'literal core embedding')
    values=[(4*((17*n+3)%3-1),4*((7*n+2)%3-1)) for n in range(512)]
    exact=source_image(values)
    require(exact!=values and exact!=source_image(values,reverse=True),'orientation discriminant')
    width=6
    require(all(-(1<<(width-1))<=z<(1<<(width-1)) for row in exact for z in row),'final signed width')
    header=''.join(gamma(n) for n in (1,1,1,1,width,2))
    raw=header+''.join(word(z,width) for row in values for z in row)
    expected=header+''.join(word(z,width) for row in exact for z in row)
    parked=('10100101'*((len(raw)+7)//8))[:len(raw)]
    actual,receipt=interpret(graph,(parked,raw),stages)
    require(actual==[parked,expected],'original-frame exact source and parked owner')
    require(receipt['HOME_writes']==len(raw) and not receipt['early_HOME_writes'],'one post-return scatter')
    require(receipt['steps']<=128*(len(raw)+1)+(1<<24)*(2*512*width+len(header)+1),'published complete bill')
    print(json.dumps({'status':'PASS_ROOT_RANK2_HOME','states':len(graph.rules),'tapes':a.TAPES,'embedded_instructions':len(core),'core_sha256':hashlib.sha256(repr(core).encode()).hexdigest(),'shape':[1,1,1,1,width,2],'F':len(raw),'receipt':receipt,'input_sha256':hashlib.sha256(raw.encode()).hexdigest(),'output_sha256':hashlib.sha256(expected.encode()).hexdigest(),'source_oracle':'Separate dense Fraction frame definition using span-set basis extension and inverse permutations; no author oracle/native verifier/recipe import.','independence':'Sparse signed-origin graph interpreter retained from prior independent root review; original-frame arithmetic independently written for this task.','scope':'One fresh dense full f=1 packet, exact embedding of every instruction, original ownership and all heads/private/exterior restored; universal proof separate.','files':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ('adapter.py','rank2.py','SOURCES.json','RECIPE.json')}},indent=2))

if __name__=='__main__':main()


"""Separate sparse graph CPU and closed original-frame Gaussian kernel for MOVE24476."""
from pathlib import Path
import hashlib,json,sys
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).with_name('source').resolve()
sys.path.insert(0,str(P))
import adapter as a
def require(ok,why):
    if not ok:raise ValueError(why)
def gamma(n):
    b=bin(n)[2:];return '0'*(len(b)-1)+b
def word(x,w):
    require(-(1<<(w-1))<=x<(1<<(w-1)),'signed oracle fit')
    return format(x%(1<<w),f'0{w}b')
def mul(z,w):return z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0]
def power(z,n):
    out=(1,0)
    for _ in range(n):out=mul(out,z)
    return out
def rotate(z,k):
    a,b=z;return ((a,b),(-b,a),(-a,-b),(b,-a))[k%4]
def rev9(x):return int(format(x,'09b')[::-1],2)
def interpret(graph,fields,stages,budget=150000000):
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




def original_frame_kernel():
    # Complete the exact source frame using explicit span sets, not the
    # retained circuit compiler, source-state interpreter or factor recipe.
    frame=(75,137,265);basis=[];span={0}
    for v in frame+tuple(1<<i for i in range(9)):
        if v not in span:
            basis.append(v);span|={x^v for x in tuple(span)}
    require(len(basis)==9 and len(span)==512,'source basis completion')
    B=[0]*512
    for x in range(512):
        for i,v in enumerate(basis):
            if (x>>i)&1:B[x]^=v
    inverse=[None]*512
    for x,y in enumerate(B):
        require(inverse[y] is None,'source chart bijective');inverse[y]=x
    inverse_columns=[inverse[1<<i] for i in range(9)]
    diagonal=[1^(v.bit_count()%2) for v in inverse_columns]
    def q(x):
        return (sum(diagonal[i] for i in range(9) if (x>>i)&1)+
            2*sum((inverse_columns[i]&inverse_columns[j]).bit_count()%2
                  for i in range(9) for j in range(i+1,9) if (x>>i)&1 and (x>>j)&1))%4
    kernel=[]
    for physical_source in range(512):
        x=rev9(physical_source);entries=[]
        for delta in range(8):
            y=x^B[delta];h=delta.bit_count()
            z=rotate(mul(power((1,1),3-h),power((1,-1),h)),q(y)-q(x))
            entries.append((rev9(y),z[0],z[1]))
        kernel.append(entries)
    # The chart diagonal changes phase but not the support; each row/column
    # has8entries of modulus squared1/8, directly at denominator8.
    require(all(sum(a*a+b*b for _,a,b in row)==64 for row in kernel),'kernel column norm')
    return kernel,tuple(basis),tuple(diagonal)

def image(values,outer,kernel):
    out=[[0,0] for _ in values]
    for p in range(outer):
        for x,row in enumerate(kernel):
            u,v=values[p*512+x]
            for y,a,b in row:
                out[p*512+y][0]+=a*u-b*v;out[p*512+y][1]+=b*u+a*v
    require(all(a%8==0 and b%8==0 for a,b in out),'closed frame output integral')
    return [(a//8,b//8) for a,b in out]

def embedding(graph,stages,core):
    labels=[s for s in graph.rules if s.startswith('MOVE24476.')]
    require(len(labels)==len(core),'full core state count')
    for i,(op,*args) in enumerate(core):
        nxt=labels[i+1] if i+1<len(labels) else stages['core_return']
        if op=='read':expected=[a.D.Rule(((3+args[0],c),),(),(),labels[j]) for c,j in args[1].items()]
        elif op=='write':expected=[a.D.Rule((),((3+args[0],args[1]),),(),nxt)]
        elif op=='move':expected=[a.D.Rule((),(),((3+args[0],args[1]),),nxt)]
        elif op=='goto':expected=[a.D.Rule((),(),(),labels[args[0]])]
        else:
            require(op=='halt','literal operation');expected=[a.D.Rule((),(),(),stages['core_return'])]
        require(graph.rules[labels[i]]==expected,'literal source core relocation')

def main():
    graph,stages=a.compile_home();core=a.core();embedding(graph,stages,core)
    require(a.C.SOURCE['event_index']==24476 and a.C.SOURCE['event']==['MOVE',727,3,470,False], 'actual public MOVE event')
    outer,width=2,10
    values=[(8*((x+3*p+((x>>3)^x))%7-3),8*((3*x+2*p+(x>>5))%7-3)) for p in range(outer) for x in range(512)]
    kernel,basis,diagonal=original_frame_kernel();expected_values=image(values,outer,kernel)
    require(expected_values!=values and any(z!=(0,0) for z in expected_values),'nontrivial frame fixture')
    data=''.join(word(c,width) for z in values for c in z)
    expected_data=''.join(word(c,width) for z in expected_values for c in z)
    header=''.join(gamma(x) for x in (1,1,outer,1,width,3));packet=header+data
    parked=('011001001'*((len(packet)+8)//9))[:len(packet)]
    actual,receipt=interpret(graph,(parked,packet),stages,budget=250000000)
    require(actual==[parked,header+expected_data],'complete original-frame output')
    require(receipt['HOME_writes']==len(packet) and receipt['early_HOME_writes']==0,'late whole HOME scatter')
    V,E=len(data),len(header);F=V+E
    require(receipt['steps']<=(1<<25)*(V+E+1)+128*(F+1),'complete stated direct time')
    require(receipt['final_head_history']<=receipt['entry_head_history']+2112*(F+1),'stated history')
    print(json.dumps({'status':'PASS_ROOT_SOURCE_AFFINE_MOVE','event_index':24476,'frame':list((75,137,265)),'source_chart_basis':basis,'source_chart_diagonal':diagonal,'shape':[1,1,outer,1,width,3],'V':V,'E':E,'F':F,'states':len(graph.rules),'tapes':a.TAPES,'core_instructions':len(core),'core_sha256':hashlib.sha256(repr(core).encode()).hexdigest(),'receipt':receipt,'input_sha256':hashlib.sha256(packet.encode()).hexdigest(),'output_sha256':hashlib.sha256((header+expected_data).encode()).hexdigest(),'oracle':'Closed original-frame Gaussian kernel from an explicit span-set chart and Hamming powers; no author factor recipe/circuit-state oracle imported','scope':'Fresh complete f1 two-outer-row packet; all-f proof and actual caller remain separate.'},indent=2,sort_keys=True))
if __name__=='__main__':main()

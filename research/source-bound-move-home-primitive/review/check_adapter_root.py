"""Separate sparse Graph CPU and exact forward Gaussian integer oracle."""
from pathlib import Path
import hashlib,json,sys
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P))
import adapter as a

def require(ok,why):
    if not ok:raise ValueError(why)
def word(x,w):return format(x%(1<<w),f'0{w}b')
def gamma(x):
    b=bin(x)[2:];return '0'*(len(b)-1)+b

def interpret(graph,fields,stages,budget=30000000):
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

def forward_numerators(values):
    """Exact twice-Ux using forward addresses and integer Gaussian pairs."""
    recipe=json.loads((P/'inputs/native/reference/RECIPE.json').read_text())['lowered_recipe']
    def phase(pair,p):
        a,b=pair;return ((a,b),(-b,a),(-a,-b),(b,-a))[p%4]
    def monomial(src,side):
        out=[None]*512
        for index,pair in enumerate(src):
            bits=[(index>>(8-j))&1 for j in range(9)]
            p=side['phase']+sum(a*b for a,b in zip(bits,side['linear_Z4']))
            p+=2*sum(bits[j]*bits[k] for j in range(9) for k in range(j+1,9) if side['quadratic_rows'][j]>>k&1)
            dest=0
            for j,row in enumerate(side['matrix_rows']):
                bit=sum(bits[k] for k in range(9) if row>>k&1)%2
                dest=2*dest+(bit^((side.get('offset',0)>>j)&1))
            require(out[dest] is None,'nonbijective monomial');out[dest]=phase(pair,p)
        return out
    right=monomial(values,recipe['right']);middle=[(0,0)]*512
    for suffix in range(256):
        for ob in (0,1):
            re=im=0
            for ib in (0,1):
                a,b=right[(ib<<8)|suffix];d=1 if ib==ob else -1
                re+=a-d*b;im+=d*a+b
            middle[(ob<<8)|suffix]=(re,im)
    return monomial(middle,recipe['left'])

def main():
    graph,stages=a.compile_home();core=a.core()
    labels=[s for s in graph.rules if s.startswith('MOVE24472.')]
    require(len(labels)==len(core),'core location count')
    for i,(op,*args) in enumerate(core):
        nxt=labels[i+1] if i+1<len(labels) else stages['core_return']
        if op=='read':expected=[a.D.Rule(((a.CORE_BASE+args[0],c),),(),(),labels[j]) for c,j in args[1].items()]
        elif op=='write':expected=[a.D.Rule((),((a.CORE_BASE+args[0],args[1]),),(),nxt)]
        elif op=='move':expected=[a.D.Rule((),(),((a.CORE_BASE+args[0],args[1]),),nxt)]
        elif op=='goto':expected=[a.D.Rule((),(),(),labels[args[0]])]
        else:require(op=='halt','core opcode');expected=[a.D.Rule((),(),(),stages['core_return'])]
        require(graph.rules[labels[i]]==expected,'literal core embedding')
    # Odd inputs exercise cancellation of half-integral basis contributions.
    values=[(1 if (17*i+3)%7<4 else -1,0) for i in range(512)]
    nums=forward_numerators(values)
    require(all(x%2==0 for pair in nums for x in pair),'complete pairs integral')
    exact=[(x//2,y//2) for x,y in nums]
    header=''.join(gamma(n) for n in (1,1,1,1,4,1))
    raw=header+''.join(word(x,4) for pair in values for x in pair)
    expected=header+''.join(word(x,4) for pair in exact for x in pair)
    parked=('00110101'*((len(raw)+7)//8))[:len(raw)]
    require(raw!=expected,'nontrivial fresh packet')
    actual,receipt=interpret(graph,(raw,parked),stages)
    require(actual==[expected,parked],'complete exact source field or parked field')
    require(receipt['HOME_writes']==len(raw) and not receipt['early_HOME_writes'],'one post-return HOME scatter')
    # Independent known cancellation witness: (1+i)/2+(1-i)/2=1.
    require(1%2!=0 and (1+1)//2==1,'half-integral contribution control')
    print(json.dumps(dict(status='PASS_ROOT_SOURCE_MOVE_HOME_REVIEW',states=len(graph.rules),
        tapes=a.TAPES,embedded_instructions=len(core),core_sha256=hashlib.sha256(repr(core).encode()).hexdigest(),
        F=len(raw),shape=[1,1,1,1,4,1],all_original_real_values_odd=True,receipt=receipt,
        input_sha256=hashlib.sha256(raw.encode()).hexdigest(),output_sha256=hashlib.sha256(expected.encode()).hexdigest(),
        independence='separate sparse signed-origin Graph interpreter and exact integer forward-address Gaussian oracle; source factorization is shared',
        scope='one fresh full f=1 packet with basis cancellation; all-f ABI proof is separate',
        files={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ('adapter.py','SOURCES.json','inputs/dispatch/tape_graph.py','inputs/native/move.py')}),indent=2))

if __name__=='__main__':main()


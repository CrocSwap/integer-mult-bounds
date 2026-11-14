"""Independent sparse infinite-tape interpretation and integer payload oracle."""
from pathlib import Path
import hashlib,json,random,sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P))
from emit import Emitter,L
from inputs import literal_oracle as O
from tape_graph import compile_graph

def require(ok,message):
    if not ok:raise ValueError(message)

def interpret(graph,initial,origins,entry=None,existing=None):
    if existing is None:
        tapes=[{o+i:c for i,c in enumerate(s)} for o,s in zip(origins,initial)]
        heads=list(origins)
        visited=[set(range(o,o+len(s))) for o,s in zip(origins,initial)]
    else:tapes,heads,visited=existing
    sentinels=[o+100000 for o in origins]
    for tape,p in zip(tapes,sentinels):tape[p]='1'
    pc=graph.start if entry is None else entry;steps=0
    while pc!='HALT':
        applicable=[]
        for rule in graph.rules[pc]:
            if all(tapes[t].get(heads[t],'_')==c for t,c in rule.tests):applicable.append(rule)
        require(len(applicable)==1,'transition failed or was ambiguous')
        rule=applicable[0]
        for t,c in rule.writes:tapes[t][heads[t]]=c
        for t,d in rule.moves:
            require(d in (-1,0,1),'nonlocal head move')
            heads[t]+=d;visited[t].add(heads[t])
        pc=rule.target;steps+=1
        require(steps<2000000,'bounded review execution exhausted')
    require(heads==origins,'heads not restored')
    for tape,p in zip(tapes,sentinels):require(tape[p]=='1','opaque exterior changed')
    for tape,o,p in zip(tapes[1:],origins[1:],sentinels[1:]):
        require(tape.get(o)=='^','origin marker changed')
        require(all(c=='_' for x,c in tape.items() if x not in (o,p)),'scratch not retired')
    return steps,(tapes,heads,visited)

def values_oracle(events,homes,values,width):
    value=dict(zip(homes,values));mask=(1<<width)-1
    for e in events:
        if not e.service:continue
        if e.service=='ZERO':value[e.owners[0]]=0
        elif e.service=='NOT':value[e.owners[0]]^=mask
        elif e.service=='FIRST':value[e.owners[0]]^=1<<(width-1)
        elif e.service=='XOR':value[e.owners[1]]^=value[e.owners[0]]
        elif e.service=='REV':
            x=value[e.owners[0]];r=0
            for _ in range(width):r=(r<<1)|(x&1);x>>=1
            value[e.owners[0]]=r
        else:raise ValueError('unknown primitive')
    return [value[o] for o in homes]

def physical_values(state,origin,k,width):
    tape=state[0][0];pos=origin+1;out=[]
    require(tape[origin]=='^','HOME marker')
    for _ in range(k):
        v=0
        for _ in range(width):
            c=tape.get(pos,'_');require(c in '01','binary field');v=2*v+int(c);pos+=1
        require(tape.get(pos)=='|','field delimiter');pos+=1;out.append(v)
    require(tape.get(pos)=='$','HOME end')
    return out

def main():
    rng=random.Random(20261113)
    roles=(('x',2),('y',3));rounds=((1,'x'),(1,'bank'));owned=('bank',)
    rows,flows=O.library(roles,rounds,owned,3,6)
    c=L.Compiler(L.C.Rule(roles,rounds,owned,3),rows,'root-independent')
    segments=((('XOR',('x','bank')),),(('XOR',('bank','y')),('NOT',('bank',))),(('XOR',('y','bank')),('NOT',('x',))))
    events,homes=Emitter(c,segments,lambda _: 'REV').compile()
    b=rows[6].width;k=len(homes)
    graph=compile_graph(events,homes,productive_count=b)
    for rules in graph.rules.values():
        for rule in rules:
            require(all(0<=t<4 and s in '_01^|$' for t,s in rule.tests+rule.writes),'finite tape/alphabet set')
            require(all(d in (-1,0,1) for t,d in rule.moves),'unit movements')
    receipts=[]
    for width in (1,2,7,17,73):
        values=[rng.randrange(1<<width) for _ in range(b)];bits=[format(v,f'0{width}b') for v in values]
        initial=['^'+'|'.join(bits)+'|$','^','^','^'];origins=[-7,19,-31,4]
        expected=values_oracle(events,homes,values+[0]*(k-b),width)
        steps,state=interpret(graph,initial,origins)
        require(physical_values(state,origins[0],k,width)==expected,'independent exact physical outcome')
        history=sum(len(s) for s in state[2])
        require(history==k*(width+1)+2+3*(width+2),'paid history including every head visit')
        expected2=values_oracle(events,homes,expected,width)
        steps2,state2=interpret(graph,initial,origins,entry=graph.execution_start,existing=state)
        require(physical_values(state2,origins[0],k,width)==expected2,'same-owner repeat')
        require(sum(len(s) for s in state2[2])==history,'reuse grew history')
        receipts.append({'F':width,'steps':steps,'repeat_steps':steps2,'history':history})
    result={'marker':'PASS_ROOT_COMPILER_PHYSICAL_REVIEW','base':'e54523517d0f03e58352e647c403a5af3e525a57','seed':20261113,'states':len(graph.rules),'events':len(events),'B':b,'K':k,'receipts':receipts,'independence':'separate sparse infinite-tape interpreter and integer word oracle; chronological source equality is separate author matched-slot proof','coverage':'fixture primitives and actual emitted small compiler trace; no full scientific primitive or selected root execution','hashes':{f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ('emit.py','tape_graph.py','SOURCES.json')}}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

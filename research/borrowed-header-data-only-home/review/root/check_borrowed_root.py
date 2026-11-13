"""Independent sparse machine and closed rank-two kernel for DATA-only borrowed HEADER."""
from pathlib import Path
import hashlib,json,sys
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).with_name('source').resolve()
sys.path.insert(0,str(P))
import adapter as a
def require(ok,why):
    if not ok:raise ValueError(why)
def gamma(n):
    b=bin(n)[2:];return '0'*(len(b)-1)+b
def word(n,w):
    require(-(1<<(w-1))<=n<(1<<(w-1)),'signed fit')
    return format(n%(1<<w),f'0{w}b')
def mul(z,w):return z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0]
def power(z,n):
    out=(1,0)
    for _ in range(n):out=mul(out,z)
    return out

def interpret(graph,fields,header,stages,budget=100000000):
    origins=[-47+11*t for t in range(a.TAPES)];heads=origins.copy()
    original=['^'+'|'.join(fields)+'|$']+['^']*(a.TAPES-1)
    original[3]='^'+header+'|^101$0'
    tapes=[{o+i:c for i,c in enumerate(s)} for o,s in zip(origins,original)]
    for t,o in enumerate(origins):tapes[t][o-4]='1';tapes[t][o+1000000]='0'
    header_original=tapes[3].copy()
    low=origins.copy();high=[o+len(s)-1 for o,s in zip(origins,original)];high[-1]+=70001
    entry=sum(y-x+1 for x,y in zip(low,high));pc=graph.start;steps=writes=early=header_writes=0
    returned=False;checkpoints={};header_reads=set()
    while pc!='HALT':
        if pc==stages['primitive_return']:returned=True
        if pc in (stages['core_entry'],stages['core_return'],stages['primitive_return']):checkpoints[pc]={'steps':steps,'HOME_writes':writes}
        found=None
        for rule in graph.rules[pc]:
            for t,c in rule.tests:
                if t==3:header_reads.add(heads[t]-origins[t])
            if all(tapes[t].get(heads[t],'_')==c for t,c in rule.tests):
                require(found is None,'ambiguous graph transition');found=rule
        require(found is not None,'literal rejection on valid rank2 fixture')
        for t,c in found.writes:
            require(heads[t]!=origins[t] or c=='^','permanent origin overwritten')
            if c=='_':tapes[t].pop(heads[t],None)
            else:tapes[t][heads[t]]=c
            if t==0:writes+=1;early+=not returned
            if t==3:header_writes+=1
        for t,d in found.moves:
            require(d in (-1,0,1),'nonunit move');heads[t]+=d
            low[t]=min(low[t],heads[t]);high[t]=max(high[t],heads[t])
        pc=found.target;steps+=1;require(steps<=budget,'bounded independent CPU exhausted')
    require(heads==origins,'all34heads restore')
    require(tapes[3]==header_original and header_writes==0,'borrowed full header/suffix changed')
    require(header_reads==set(range(1,len(header)+1)),'header reads exactly six codes, no suffix read')
    for t,o in enumerate(origins):
        require(tapes[t].get(o)=='^' and tapes[t].get(o-4)=='1' and tapes[t].get(o+1000000)=='0','origin/exterior changed')
        if t not in (0,3):require(set(tapes[t])=={o,o-4,o+1000000},'private retirement')
    raw=''.join(tapes[0].get(origins[0]+i,'_') for i in range(len(original[0])))
    require(raw.startswith('^') and raw.endswith('|$'),'HOME frame')
    return raw[1:-2].split('|'),{'steps':steps,'HOME_writes':writes,'early_HOME_writes':early,'HEADER_writes':header_writes,'header_read_first':min(header_reads),'header_read_last':max(header_reads),'entry_head_history':entry,'final_head_history':sum(y-x+1 for x,y in zip(low,high)),'checkpoints':checkpoints}

def static_embedding(graph,stages,core):
    labels=[s for s in graph.rules if s.startswith('POSITIVE.')]
    require(len(labels)==len(core),'complete fixed-rank core')
    for i,(op,*args) in enumerate(core):
        nxt=labels[i+1] if i+1<len(labels) else stages['core_return']
        if op=='read':expected=[a.D.Rule(((3+args[0],c),),(),(),labels[j]) for c,j in args[1].items()]
        elif op=='write':expected=[a.D.Rule((),((3+args[0],args[1]),),(),nxt)]
        elif op=='move':expected=[a.D.Rule((),(),((3+args[0],args[1]),),nxt)]
        elif op=='goto':expected=[a.D.Rule((),(),(),labels[args[0]])]
        else:
            require(op=='halt','literal instruction');expected=[a.D.Rule((),(),(),stages['core_return'])]
        require(graph.rules[labels[i]]==expected,'exact positive-core injection')
    seen=set();pending=[graph.start]
    while pending:
        state=pending.pop()
        if state=='HALT' or state in seen:continue
        seen.add(state)
        for rule in graph.rules[state]:
            require(all(t!=3 for t,_ in rule.writes),'reachable borrowed-header write')
            pending.append(rule.target)
    return len(seen)

def dense_image(values,spectators,rank):
    out=[];suffix_bits=9-rank
    for address in range(512):
        for spectator in range(spectators):
            z=[0,0]
            for prefix in range(1<<rank):
                source=(prefix<<suffix_bits)|(address&((1<<suffix_bits)-1))
                h=(prefix^(address>>suffix_bits)).bit_count()
                coefficient=mul(power((1,1),rank-h),power((1,-1),h))
                x=mul(coefficient,values[source*spectators+spectator]);z[0]+=x[0];z[1]+=x[1]
            den=1<<rank;require(z[0]%den==z[1]%den==0,'kernel output integral');out.append((z[0]//den,z[1]//den))
    return out

def main():
    graph,all_stages=a.compile_home(2);stages=all_stages[0];core=a.core(2)
    reachable=static_embedding(graph,stages,core)
    spectators,width,cutoff=2,7,(1<<129)+1
    values=[(4*((address+3*s+(address>>3))%5-2),4*((3*address+s+(address>>5))%5-2)) for address in range(512) for s in range(spectators)]
    expected=dense_image(values,spectators,2)
    require(expected!=values and expected!=dense_image(values,spectators,1),'nontrivial exact rank2 fixture')
    body=''.join(word(c,width) for z in values for c in z)
    expected_body=''.join(word(c,width) for z in expected for c in z)
    header=''.join(gamma(n) for n in (1,1,1,spectators,width,cutoff))
    parked=('001010011'*((len(body)+8)//9))[:len(body)]
    actual,receipt=interpret(graph,(parked,body),header,stages)
    require(actual==[parked,expected_body],'DATA-only output with independent tensor kernel')
    require(receipt['HOME_writes']==len(body) and receipt['early_HOME_writes']==0,'exact DATA extent after primitive return')
    V,E=len(body),len(header)
    # One service, two HOMEs and at most two B1 operand buffers. B1 is paid
    # separately from the primitive wrapper and inherited native core.
    bound=(1<<24)*(V+E+1)+256*(V+1)+16*(1+1)*(2+2+1)*(V+2)
    require(receipt['steps']<=bound,'complete core/wrapper/B1 time bill')
    require(receipt['final_head_history']<=receipt['entry_head_history']+2112*(V+E+1)+8*(V+2),'primitive plus conservative B1 history')
    print(json.dumps({'status':'PASS_ROOT_BORROWED_HEADER_RANK2','shape':[1,1,1,spectators,width,cutoff],'cutoff_bit_length':cutoff.bit_length(),'V':V,'E':E,'HOME_body_length':V,'states':len(graph.rules),'reachable_states':reachable,'tapes':a.TAPES,'core_instructions':len(core),'core_sha256':hashlib.sha256(repr(core).encode()).hexdigest(),'receipt':receipt,'input_sha256':hashlib.sha256(body.encode()).hexdigest(),'output_sha256':hashlib.sha256(expected_body.encode()).hexdigest(),'oracle':'Closed two-axis Hamming-distance Gaussian kernel; no author CPU/fixture/oracle imported','scope':'One fresh complete rank2 f1 DATA-only call with spectators and an immediate opaque HEADER suffix; no actual header/view producer or caller admission.'},indent=2,sort_keys=True))
if __name__=='__main__':main()

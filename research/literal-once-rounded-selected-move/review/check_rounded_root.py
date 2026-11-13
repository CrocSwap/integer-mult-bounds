"""Separate sparse CPU and exact integer review; shared source factorization."""
from pathlib import Path
import hashlib,json,sys
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P))
import rounded as q

def require(ok,why):
    if not ok:raise ValueError(why)
def word(x,w):return format(x%(1<<w),f'0{w}b')
def gamma(x):
    b=bin(x)[2:];return '0'*(len(b)-1)+b

def interpret(code,words,guards=True,budget=1000000,commit=None):
    origins=[-19+3*t for t in range(q.TAPES)];heads=origins.copy()
    tapes=[{o+i:c for i,c in enumerate(words.get(t,''))} for t,o in enumerate(origins)]
    if guards:
        for t in q.PRIVATE:tapes[t][origins[t]-1]='|'
    for t,o in enumerate(origins):tapes[t][o-5]='1';tapes[t][o+1000000]='0'
    low,high=origins.copy(),origins.copy();high[-1]+=100003
    entry=sum(b-a+1 for a,b in zip(low,high))
    pc=steps=public=early=0;rejected=False
    while True:
        op,*a=code[pc];steps+=1
        require(steps<=budget,'bounded separate interpreter exhausted')
        if op=='read':
            c=tapes[a[0]].get(heads[a[0]],'_')
            if c not in a[1]:rejected=True;break
            pc=a[1][c]
        elif op=='write':
            t,c=a
            if c=='_':tapes[t].pop(heads[t],None)
            else:tapes[t][heads[t]]=c
            if t==q.DATA:public+=1;early+=commit is None or pc<commit
            pc+=1
        elif op=='move':
            t,d=a;require(d in (-1,1),'nonunit move');heads[t]+=d
            if heads[t]<low[t]:low[t]=heads[t]
            if heads[t]>high[t]:high[t]=heads[t]
            pc+=1
        elif op=='goto':pc=a[0]
        elif op=='halt':break
        else:raise ValueError('nonlocal opcode')
    for t,o in enumerate(origins):
        require(tapes[t].get(o-5)=='1' and tapes[t].get(o+1000000)=='0','opaque exterior changed')
    return dict(tapes=tapes,heads=heads,origins=origins,steps=steps,public_writes=public,
                early=early,rejected=rejected,entry_head_history=entry,
                final_head_history=sum(b-a+1 for a,b in zip(low,high)))

def content(s,t,n):
    o=s['origins'][t];return ''.join(s['tapes'][t].get(o+i,'_') for i in range(n))

def forward_numerators(values):
    """Exact twice-Ux using forward addresses and integer Gaussian pairs."""
    recipe=json.loads((P/'reference/RECIPE.json').read_text())['lowered_recipe']
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
    code,alphabet,entries=q._compile_rounded();old,_=q.h.core.compile_move()
    start,end=entries['core'],entries['round']
    require(end-start==len(old),'embedded core size')
    for i,(op,*a) in enumerate(old):
        if op=='read':expected=(op,q.CORE_PORTS[a[0]],{s:start+j for s,j in a[1].items()})
        elif op in ('write','move'):expected=(op,q.CORE_PORTS[a[0]],a[1])
        elif op=='goto':expected=(op,start+a[0])
        else:require(op=='halt','core opcode');expected=('goto',end)
        require(code[start+i]==expected,'literal core relocation')
    require(not any(x[0]=='write' and x[1] in (0,1) for x in code[:entries['commit']]),'precommit public write')
    require(not any(x[0]=='write' and x[1]==0 for x in code),'public header write')
    rc,_=q.compile_converter('round');ic,_=q.compile_converter('ingress')
    cases=[];faults=0
    for w,k in ((2,1),(3,2),(4,4),(5,1),(6,4)):
        scale=1<<k;M=1<<(w-1);W=w+2*k+1
        values=list(range(-M*scale-scale//2,M*scale-scale//2))
        wide=''.join(word(z,W) for z in values)
        wanted=''.join(word((z+scale//2)//scale,w) for z in values);public='01'*37
        guides={q.WIDTH:'1'*w,q.K:'1'*k,q.MARGIN:'1'*(k+1),q.HIGH:'1'*(w+k+1),q.COUNT:'1'*len(values)}
        out=interpret(rc,{**guides,q.WD:wide,q.DATA:public},budget=5000000)
        require(not out['rejected'] and out['heads']==out['origins'],'rounded return')
        require(content(out,q.OUTPUT,len(wanted))==wanted,'exact nearest-up result')
        require(not out['public_writes'] and content(out,q.DATA,len(public))==public,'public preservation')
        for bad in (-M*scale-scale//2-1,M*scale-scale//2,(1<<(W-1))-1,-(1<<(W-1))):
            state=interpret(rc,{**guides,q.COUNT:'11',q.WD:word(0,W)+word(bad,W),q.DATA:public})
            require(state['rejected'] and not state['public_writes'],'true overflow precommit control')
            require(content(state,q.OUTPUT,w)=='0'*w,'late control reached staging');faults+=1
        signed=list(range(-M,M));raw=''.join(word(x,w) for x in signed)
        lift=interpret(ic,{**guides,q.COUNT:'1'*len(signed),q.DATA:raw})
        require(not lift['rejected'] and lift['heads']==lift['origins'],'lift return')
        require(content(lift,q.WD,len(signed)*W)==''.join(word(x*scale,W) for x in signed),'signed-min ingress')
        cases.append(dict(w=w,k=k,complete_fit_z_values=len(values),round_steps=out['steps'],all_signed_inputs=len(signed),lift_steps=lift['steps']))
    require((-5+1)//2==-2 and -5//2==-3,'pre-round fit control')
    require((1+1)//2==1 and round(.5)==0,'ties-even control')
    require((3+1)//2==2 and 3//2==1,'truncation control')
    hc,_=q.compile_header();headers=[]
    for f,w in ((1,2),(2,3),(5,7),(8,31),(17,5),(65,17)):
        shape=(f,2,3,5,w,1<<511);raw=''.join(gamma(n) for n in shape)
        expected=''.join(gamma(n) for n in shape[:4]+(w+2*((f+1)//2)+1,shape[-1]))
        s=interpret(hc,{q.HEADER:raw+'|010|'},guards=False,budget=2000000)
        require(not s['rejected'] and s['heads']==s['origins'],'header return')
        require(content(s,q.WH,len(expected))==expected,'widened Gamma')
        require(content(s,q.HEADER,len(raw)+5)==raw+'|010|','header source')
        headers.append(dict(f=f,w=w,cutoff_bits=512,steps=s['steps']))
    values=[((7*i+3)%5-2,(11*i+1)%5-2) for i in range(512)];values[93]=(-8,0)
    nums=forward_numerators(values);rounded=[((a+1)//2,(b+1)//2) for a,b in nums]
    require(all(-8<=x<8 for pair in rounded for x in pair),'fresh packet fits')
    raw=''.join(word(x,4) for pair in values for x in pair)
    expected=''.join(word(x,4) for pair in rounded for x in pair)
    header=''.join(gamma(n) for n in (1,1,1,1,4,1))
    s=interpret(code,{q.HEADER:header+'|011|',q.DATA:raw},guards=False,budget=50000000,commit=entries['commit'])
    require(not s['rejected'] and s['heads']==s['origins'],'full restored return')
    require(content(s,q.DATA,len(expected))==expected,'full integer kernel')
    require(s['public_writes']==len(raw) and not s['early'],'one final full commit')
    require(content(s,q.HEADER,len(header)+5)==header+'|011|','full public header')
    for t in range(2,q.TAPES):
        o=s['origins'][t];require(set(s['tapes'][t])=={o-5,o+1000000},'private body or guard not retired')
    result=dict(status='PASS_ROOT_ONCE_ROUNDED_REVIEW',locations=len(code),tapes=q.TAPES,
        graph_sha256=hashlib.sha256(repr(code).encode()).hexdigest(),embedded_core_instructions=len(old),
        converters=cases,late_true_overflow_controls=faults,semantic_controls=3,headers=headers,
        fresh_full_packet={key:s[key] for key in ('steps','public_writes','early','entry_head_history','final_head_history')},
        nonintegral_final_components=sum(x%2!=0 for pair in nums for x in pair),includes_original_signed_minimum=True,
        independence='separate sparse signed-origin interpreter and exact integer forward-address kernel; shared source factorization, not an independent source theorem',
        history_note='Head-window monitor includes an old blank visit; true K_entry additionally includes all opaque backing and previous history.',
        scope='full f=1 execution and complete listed converter domains; universal bounds require the written proof',
        hashes={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ('rounded.py','move.py','endpoint.py','ROUNDED-SOURCES.json')})
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

"""Separate instruction relocation and exact integer converter review."""
from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(P))
import endpoint as e

def require(x,s):
    if not x:raise ValueError(s)

def machine(code,words,limit=1000000):
    origins=[-13+3*t for t in range(e.TAPES)]
    tapes=[{o+i:c for i,c in enumerate(words.get(t,''))} for t,o in enumerate(origins)]
    for t in e.WRAPPER_PRIVATE:tapes[t][origins[t]-1]='|'
    heads=origins.copy();visits=[{o} for o in origins]
    pc=steps=writes=0;rejected=False
    while True:
        op,*a=code[pc];steps+=1
        require(steps<=limit,'bounded unit review exhausted')
        if op=='read':
            symbol=tapes[a[0]].get(heads[a[0]],'_')
            if symbol not in a[1]:rejected=True;break
            pc=a[1][symbol]
        elif op=='write':
            tapes[a[0]][heads[a[0]]]=a[1];pc+=1;writes+=a[0]==e.DATA
        elif op=='move':
            require(a[1] in (-1,1),'nonunit move')
            heads[a[0]]+=a[1];visits[a[0]].add(heads[a[0]]);pc+=1
        elif op=='goto':pc=a[0]
        elif op=='halt':break
        else:raise ValueError('nonlocal opcode')
    return tapes,heads,origins,steps,writes,rejected,visits

def get(tapes,origins,t,n):return ''.join(tapes[t].get(origins[t]+i,'_') for i in range(n))
def word(x,w):return format(x%(1<<w),f'0{w}b')
def gamma(n):
    b=bin(n)[2:];return '0'*(len(b)-1)+b

def main():
    code,alphabet,entries=e._compile_endpoint();core,_=e.core.compile_move()
    start=entries['core'];end=entries['egress']
    require(end-start==len(core),'embedded core size')
    for i,ins in enumerate(core):
        op,*a=ins
        if op=='read':expected=(op,e.CORE_PORTS[a[0]],{s:start+j for s,j in a[1].items()})
        elif op in ('write','move'):expected=(op,e.CORE_PORTS[a[0]],a[1])
        elif op=='goto':expected=(op,start+a[0])
        else:require(op=='halt','unknown core opcode');expected=('goto',end)
        require(code[start+i]==expected,'embedded core relocation')
    require(not any(ins[0]=='write' and ins[1] in (e.HEADER,e.DATA) for ins in code[:entries['commit']]),'early public write')
    require(not any(ins[0]=='write' and ins[1]==e.HEADER for ins in code),'public header write')
    ingress,_=e.compile_converter('ingress');egress,_=e.compile_converter('egress')
    records=[];rejections=0
    for w,k in ((2,0),(3,1),(4,2),(5,3),(6,5),(7,9)):
        values=list(range(-(1<<(w-1)),1<<(w-1)))
        raw=''.join(word(x,w) for x in values);wide=''.join(word(x*(1<<k),w+2*k) for x in values)
        guides={e.WIDTH:'1'*w,e.K:'1'*k,e.COUNT:'1'*len(values)}
        a,h,o,s,wr,bad,seen=machine(ingress,{**guides,e.DATA:raw})
        require(not bad and h==o and not wr,'ingress full signed range boundary')
        require(get(a,o,e.WD,len(wide))==wide,'ingress integer scaling')
        require(get(a,o,e.DATA,len(raw))==raw,'ingress public source preservation')
        b,h2,o2,s2,wr2,bad2,seen2=machine(egress,{**guides,e.WD:wide,e.DATA:raw})
        require(not bad2 and h2==o2 and not wr2,'egress return boundary')
        require(get(b,o2,e.OUTPUT,len(raw))==raw,'exact signed integer quotient')
        if k:
            for position in (len(wide)-1,len(wide)-(w+2*k)+k):
                damaged=wide[:position]+('1' if wide[position]=='0' else '0')+wide[position+1:]
                t,hh,oo,ss,ww,rejected,vv=machine(egress,{**guides,e.WD:damaged,e.DATA:raw})
                require(rejected and not ww and get(t,oo,e.DATA,len(raw))==raw,'late egress rejection safety')
                rejections+=1
        records.append({'w':w,'k':k,'all_signed_values':len(values),'ingress_steps':s,'egress_steps':s2})
    hc,_=e.compile_header();headers=[]
    for f,w in ((2,2),(6,5),(18,33),(34,65),(66,129)):
        shape=(f,2,3,5,w,1<<511);expected=shape[:4]+(w+2*((f+2)//4),shape[5])
        raw=''.join(gamma(x) for x in shape)+'|0110|'
        a,h,o,s,wr,bad,seen=machine(hc,{e.HEADER:raw})
        wanted=''.join(gamma(x) for x in expected)
        require(not bad and h==o and not wr,'header restored boundary')
        require(get(a,o,e.HEADER,len(raw))==raw,'header opaque tail')
        require(get(a,o,e.WH,len(wanted))==wanted,'paid widened Gamma header')
        headers.append({'f':f,'w':w,'cutoff_bits':512,'steps':s})
    print(json.dumps({'marker':'PASS_ROOT_LITERAL_ENDPOINT_REVIEW','locations':len(code),'relocated_core_instructions':len(core),'graph_sha256':hashlib.sha256(repr(code).encode()).hexdigest(),'converters':records,'late_rejection_controls':rejections,'headers':headers,'independence':'separate sparse signed-origin local-instruction interpreter and exact-integer complete small signed-range oracle','scope':'modular converter/header and exact whole-core relocation; author integrated f1 replay and written all-f proof are separate evidence','files':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ('endpoint.py','move.py','endpoint_verify.py')}},indent=2))
if __name__=='__main__':main()

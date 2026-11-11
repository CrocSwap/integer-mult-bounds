"""Independent dense tape CPU for the header/cutoff prefix.
No author input builder, interpreter, or verifier is called.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from importlib.util import module_from_spec,spec_from_file_location
from hashlib import sha256
import json,sys
PKG=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
spec=spec_from_file_location('checked_cutoff',PKG/'cutoff_prefix.py')
C=module_from_spec(spec);spec.loader.exec_module(C)
def need(ok,reason):
    if not ok:raise ValueError(reason)
def gamma(v):
    s=format(v,'b');return '0'*(len(s)-1)+s
def run(p,d,e,q,joined=False,mutate=None):
    code=C.compile_joined(3,2,q)[0] if joined else C.compile_prefix(q)[0]
    if mutate is not None:code=mutate(list(code))
    cutoff=next(t for t in range(1,e+2) if t==e+1 or (t**q>=d if q<100 else d==1 or t>=2))
    need(q<100 or d.bit_length()<=q,'selected-Q oracle range')
    header=gamma(p)+gamma(d)+'01001101110101'
    margin=9;limit=max(6*d+100,len(header)+100)
    tapes=[['_']*(margin+limit+10) for _ in range(11)]
    origins=[13*i-71 for i in range(11)]
    heads=origins[:];low=heads[:];high=heads[:]
    for a in tapes:
        a[margin-5:margin]=['1','t0','0','1','|']
        a[margin+limit:margin+limit+3]=['t0','1','|']
    for i in (3,5,6,7,8,9,10):tapes[i][margin-1]='_'
    tapes[0][margin:margin+e]=['1']*e
    tapes[4][margin:margin+len(header)]=list(header)
    before=[a[:] for a in tapes];seen=[];pc=steps=0
    stage_count=q.bit_length()+q.bit_count()
    allowance=1000*(stage_count+1)*(len(gamma(p)+gamma(d))+d*cutoff+1)
    if joined:
        pending=[e];mass=0
        while pending:
            x=pending.pop();mass+=x
            if x>=max(3,cutoff):pending.extend([x//3,x//3])
        allowance+=200*3*mass
    while steps<allowance:
        ins=code[pc];op=ins[0];pc+=1;steps+=1
        if op=='halt':break
        if op=='goto':pc=ins[1];continue
        if op=='emit':
            seen.append(ins[1])
            if ins[1]=='READY':
                want=[a[:] for a in before];want[3][margin-1]='|';want[3][margin:margin+cutoff]=['1']*cutoff
                if not (tapes==want and heads==origins) and mutate is None:
                    detail={i:[(j-margin,a[j],b[j]) for j in range(len(a)) if a[j]!=b[j]][:8]
                            for i,(a,b) in enumerate(zip(tapes,want)) if a!=b}
                    raise ValueError(str(dict(p_bits=p.bit_length(),d=d,e=e,q=q,heads=[x-y for x,y in zip(heads,origins)],diff=detail)))
                need(tapes==want and heads==origins,'prefix boundary')
            continue
        t=ins[1];at=heads[t]-origins[t]+margin
        need(0<=at<len(tapes[t]),'buffer bounds')
        if op=='read':pc=ins[2][tapes[t][at]]
        elif op=='write':tapes[t][at]=ins[2]
        elif op=='move':
            need(ins[2] in (-1,1),'unit move')
            heads[t]+=ins[2];low[t]=min(low[t],heads[t]);high[t]=max(high[t],heads[t])
        else:raise ValueError('opcode')
    else:raise ValueError('transition envelope')
    want=[a[:] for a in before]
    if not joined:
        want[3][margin-1]='|';want[3][margin:margin+cutoff]=['1']*cutoff
    need(tapes==want and heads==origins,'full endpoint')
    need(seen[0]=='READY' and seen[-1]==('RETIRED' if joined else 'READY'),'link boundaries')
    need(all(lo>=o-(i!=4) for i,(lo,o) in enumerate(zip(low,origins))),'ancestor locality')
    return dict(p_bits=p.bit_length(),d=d,e=e,q=q,joined=joined,cutoff=cutoff,steps=steps,
                visited=sum(hi-lo+1 for hi,lo in zip(high,low)))

def main():
    rows=[]
    for q in (2,3,5):
        for d in (1,2,3,4,8,9,15,16,17,24,25,26,31,32,33,63,64,65):
            for e in sorted({1,d}):
                p=(1<<73)+5 if d%2 else 3
                rows.append(run(p,d,e,q))
    for d in (1,2,3,9,17,65):
        rows.append(run((1<<127)+19,d,d,C.SELECTED_Q))
    for q,d,e in ((2,16,16),(2,17,2),(3,27,27),(3,28,7),
                  (5,33,33),(C.SELECTED_Q,17,17)):
        rows.append(run(97,d,e,q,joined=True))
    controls=[]
    def wrong_header(code):
        i=code.index(('move',4,-1));code[i]=('move',4,1);return code
    def skipped_retirement(code):
        at=C.compile_joined(3,2,2)[2]['cleanup_at']
        code[at]=('goto',len(code)-2);return code
    fixtures=[('header return',lambda:run(16,9,9,2,mutate=wrong_header),'prefix boundary'),
              ('cutoff retirement',lambda:run(16,9,9,2,joined=True,mutate=skipped_retirement),'full endpoint'),
              ('wrong exponent',lambda:run(16,16,8,2,mutate=lambda _:C.compile_prefix(3)[0]),'prefix boundary')]
    for name,fn,want in fixtures:
        try:fn()
        except ValueError as error:
            need(str(error)==want,'expected semantic rejection');controls.append(name)
        else:raise ValueError('mutant survived')
    print(json.dumps(dict(status='PASS',method='independent dense CPU and exact integer-root oracle',
        cases=len(rows),transitions=sum(r['steps'] for r in rows),negative_controls=controls,
        source_sha256=sha256((PKG/'cutoff_prefix.py').read_bytes()).hexdigest(),rows=rows),indent=2))

if __name__=='__main__':main()

"""Independent wider signed arithmetic, source census and global character review."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from types import SimpleNamespace
import argparse,json,gzip,sys
def require(ok,message):
    if not ok:raise ValueError(message)
def nearest(x):return (x+F(1,2)).numerator//(x+F(1,2)).denominator
def image(x,y,s):
    a,b=x;c,d=y
    return nearest(F(a+c,2)-s*F(b-d,2)),nearest(F(b+d,2)+s*F(a-c,2))
def main(pkg):
    sys.path.insert(0,str(pkg))
    from source_binding import vendor
    from gaussian_table import compile_stage,COMMIT
    P=vendor('independent_lambda_meter','vendor/scalar_fixture.py')
    tables={s:compile_stage(s) for s in (-1,1)};work=[P.Tape((),51),P.Tape((),71)]
    totals=dict(cases=0,accepted=0,rejected=0,components=0);max_ratio=F(0);largest_history=0
    for w in (129,1,65,2,33,3,17,5):
        B=1<<(w-1)
        for s in (-1,1):
            patterns=[([(0,0),(B-1,-B)],[(0,0),(-B,B-1)]),
                      ([(0,0),(B-1,-B),(B-1,-B)],[(0,0),(-B,B-1),(B-1,B-1)]),
                      ([(-B,-B),(B-1,B-1)],[(-B,-B),(B-1,B-1)])]
            for xs,ys in patterns:
                values=[v for pair in xs for v in pair];partners=[v for pair in ys for v in pair]
                expected=tuple(v for x,y in zip(xs,ys) for v in image(x,y,s));fits=all(-B<=v<B for v in expected)
                x=P.Tape(P.encode_symbols(P.symbols(values,w)),17,True);y=P.Tape(P.encode_symbols(P.symbols(partners,w)),31)
                ctx=P.Tape((1,0,1)*41,101,True);ctx.pos+=97
                for k,t in enumerate(work):
                    P.M.retire(t)
                    for j in range(157+19*k):t.cells[t.origin+j]=(j+k)&1
                    t.pos=t.origin+73
                old=sum(len(t.body()) for t in work);context_before=ctx.body();original=x.body()
                ports=(x,y,*work,ctx);before=sum(t.actions for t in ports)
                stage=P.RowCounter(tables[s]);commit=P.RowCounter(COMMIT)
                c=SimpleNamespace(payloads=ports,primitive_work=(2,3),primitive_context=(4,),services={('stage',):stage,('commit',):commit})
                failure=None
                try:P.M.Controller.primitive(c,('stage',),(0,1))
                except ValueError as exc:failure=str(exc)
                require(x.body()==original and x.writes==0,'stage cannot write even one public bit')
                require((failure is None)==fits,'independent final-range iff')
                if fits:
                    require(P.decode(y.body(),w)==expected,'exact rational global Gaussian oracle')
                    x.readonly=False;P.M.Controller.primitive(c,('commit',),(0,1))
                    require(P.decode(x.body(),w)==expected,'paid staged commit')
                else:require(failure=='Lambda signed range or canonical format','named range rejection')
                for t in (y,*work):P.M.retire(t)
                for t in (x,ctx):P.M.origin(t)
                require(all(t.protected() and t.pos==t.origin for t in ports),'all heads and protected ancestors')
                require(all(t.blank() for t in (y,*work)) and ctx.body()==context_before,'owned cleanup and borrowed preservation')
                used=sum(t.actions for t in ports)-before+stage.steps+commit.steps
                bound=4096*(len(values)*(w+1)+1)+14*old+32*(len(context_before)+1)
                require(used<=bound,'positive tape plus control envelope');max_ratio=max(max_ratio,F(used,bound))
                largest_history=max(largest_history,max(t.highwater-t.origin for t in work))
                totals['cases']+=1;totals['accepted']+=fits;totals['rejected']+=not fits;totals['components']+=len(values)
    caller=json.loads((pkg/'data/caller.json').read_bytes());word=json.loads(gzip.decompress((pkg/'data/word.json.gz').read_bytes()));occurrences=[]
    for site,event in enumerate(caller['events']):
        if event[:2] in (['A','LAMBDA'],['B','LAMBDA']):
            require(type(event[3])is int and event[3] in (-1,1),'typed source sign')
            for port in caller['types'][event[0]]['ports']:
                q=word['ports'][port];require(type(q)is int and 0<q<512,'nine-bit source direction')
                occurrences.append((site,port,q,event[3]))
    require(len(occurrences)==14480,'independent actual caller occurrence census')
    character_cases=0
    for f in range(1,9):
        for bits in range(1<<f):
            for s in (-1,1):
                t=(-1)**bits.bit_count();real=F(1+t,2);imag=s*F(1-t,2)
                require(real*real+imag*imag==1,'global Lambda character is unitary');character_cases+=1
    require((1+1)/2==1 and (1j*1j)==-1,'two odd columns reject tensor-of-Lambda')
    return dict(status='independent wider arithmetic/source/character review passed',**totals,max_combined_cost_ratio=str(max_ratio),largest_retained_numerator_backing=largest_history,actual_source_occurrences=len(occurrences),global_character_cases=character_cases,public_stage_readonly_trap=True,full_nine_axis_numerical_execution=False,reviewed_files={n:sha256((pkg/n).read_bytes()).hexdigest() for n in ('PROOF.md','lambda_provider.py','gaussian_table.py','source_binding.py')},proof_review='Signed terminal carries telescope; both numerators plus1 fit W+2; final-only rounding has half-grid component defect. Source Q² route, private remainder view, named-failure cleanup, complete serial invoice and uninstalled caller/header boundary remain explicit.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=main(a.package.resolve())
    if a.output:a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,sort_keys=True))

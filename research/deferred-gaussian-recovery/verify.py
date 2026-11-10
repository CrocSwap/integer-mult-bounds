"""Independent exact allocation checks and genuine native endpoint witness.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from allocation import allocation,bounds,need,clog
from source_binding import authenticate,opened

def trunc(a,b):return (-1 if a<0 else 1)*(abs(a)//b)
def nearest_positive(a,b):return (2*a+b)//(2*b)
def checks():
    count=widths=source_orders=0
    for b in range(1,11):
        for S in sorted({1,3,(1<<b)-1}):
            if S>=1<<b:continue
            for Gamma in (0,1,2,7,31):
                for m in (1,3,16):
                    d=allocation(S,b,Gamma,m,Lmax=37,normalizers=(0,1,4))
                    z=bounds(S,b,Gamma,d['q'],d['a'])
                    need(z['first']<Fraction(1,2) and z['product']<Fraction(1,4) and z['opposite']<Fraction(1,2),'actual normalized field radii')
                    need(z['restored']<2*z['epsilon'] and z['integer_error']<Fraction(1,4),'strict recovered real error')
                    # Independent integer scale cancellation, not the float log.
                    need((1<<(3*Gamma))*z['lam']**3==1,'three exact normalizers spent once')
                    need(d['q']>=d['a']+3*Gamma+7 and d['z']==d['a']+3*Gamma+clog(m)+3,'source-first target ordering')
                    need(3*Fraction(1,1<<d['tau'])/(1<<Gamma)<z['eta'],'sum of three public stage allowances')
                    source_orders+=1
                    # Maximum legal half-disk real numerator at each native step.
                    x=1<<(d['q']-1);once=x*S;twice=once*S;shifted=twice*(1<<d['recovery_shift'])
                    need(max(x,S,once,twice,shifted)<1<<(d['W']-1),'all exact recover scalar and shifted widths')
                    need(d['W']-1-(d['q']+4*b+3*Gamma+3)==2,'two extra signed margin bits')
                    widths+=1;count+=1
    controls=[]
    for args in ((8,3,0),(3,1,0),(3,3,-1)):
        try:allocation(*args)
        except ValueError:controls.append('source_descriptor_rejection')
        else:raise ValueError('missing source descriptor rejection')
    # Missing S² or Gamma is an interface mismatch, not an old-domain defect.
    c=Fraction(51);S=5;b=3;G=2
    target=c/(S*S*(1<<(2*b+4+3*G)))
    need(target*S*S*(1<<(2*b+4))!=c,'old recovery shift misses deferred Gamma')
    need(target*S*(1<<(2*b+4+3*G))!=c,'one source S factor cannot replace two')
    need(target*S*S*(1<<(2*b+4+G))!=c,'one Gamma cannot replace three')
    return dict(allocation_cases=count,width_cases=widths,source_order_cases=source_orders,controls=controls+['missing_3Gamma','missing_S','one_Gamma'])

def main():
    pins=authenticate();math=checks();receipts=[]
    with opened() as state:
        from deferred_tail import DeferredTail
        from cardinal_counts import Count
        from records import Tape
        from ring_words import Signed,write_signed
        from router_metadata import owned
        from session import initialize_marker,erase_marker
        from check_support import no_decode
        from words import BLANK
        from compact_counts import append_bits
        def field(values,q):
            tape=Tape();erase_marker(tape);initialize_marker(tape)
            with owned(Count.literal(q+2)) as (width,):
                for pair in values:
                    for val in pair:
                        with owned(Signed(Count.literal(abs(val)),val<0)) as (s,):write_signed(s,tape,width)
            tape.rewind();return tape
        def read(tape,N,W):
            data=tape.cells[1:1+N*W];need(len(data)==N*W and all(x in (0,1) for x in data),'complete native output bits')
            result=[]
            for start in range(0,len(data),W):
                row=data[start:start+W];v=sum(bit<<i for i,bit in enumerate(row))
                result.append(v-(1<<W) if row[-1] else v)
            return result
        def clean(tape):tape.clear();erase_marker(tape)
        S,b=5,3;digits1=[7,6,1];digits2=[4,2,5]
        coeff=[sum(digits1[i]*digits2[j] for i in range(3) for j in range(3) if i+j==k) for k in range(S)]
        for G in (0,2):
            a=2*clog(S)+2*b+7;q=a+3*G+7;W=q+3*G+4*b+6
            parameters=[Count.literal(x) for x in (S,b,q,G)];saved_meta=[bytes(x.tape.cells) for x in parameters]
            machine=DeferredTail(state,*parameters)
            vals=[((i+1)*(1<<(q-G-5)),(-1)**i*(1<<(q-G-6))) for i in range(S)]
            other=[((S-i)*(1<<(q-G-6)),(-1)**(i+1)*(1<<(q-G-7))) for i in range(S)]
            left,right=field(vals,q),field(other,q);saved=(bytes(left.cells),bytes(right.cells))
            with no_decode():out=machine.run(left,right)
            actual=read(out,2*S,q+2)
            expect=[]
            for (u,v),(x,y) in zip(vals,other):expect.extend((trunc(u*x-v*y,1<<q),trunc(u*y+v*x,1<<q)))
            need(actual==expect,'actual native complex product and single grid drop')
            need(bytes(left.cells)==saved[0] and bytes(right.cells)==saved[1] and left.head==right.head==1,'borrowed product fields restored')
            try:machine.run(left,right)
            except ValueError:pass
            else:raise ValueError('missing pending endpoint protection')
            machine.consume()
            factor=S*S*(1<<(2*b+4+3*G))
            normalized=[(int(Fraction(c*(1<<q),factor)),0) for c in coeff]
            # The actual public radius-2/3 external ABI is q+3, not q+2.
            text=''.join(''.join(str(int(v<0))+format(abs(v),'0'+str(q+2)+'b') for v in pair)+'#' for pair in normalized)
            external=state.B.Tape('normalized compact public return',text)
            codec=state.codec.Codec(state.B,Tape,BLANK,initialize_marker,erase_marker,
                                    state.codec.Format(q+3,q,q+3,q,0))
            source=Tape();erase_marker(source);initialize_marker(source)
            with no_decode():
                wide=codec.prepare_input(external)
                narrow=machine.carrier(wide)
                append_bits(narrow,source);source.rewind()
            need(read(source,2*S,q+2)==[v for pair in normalized for v in pair],'exact wide external/native to narrow scalar carrier')
            machine.consume();codec.abort();saved_source=bytes(source.cells)
            need(external.inspect()==text and external._head==1,'borrowed wide external source and origin')
            state.B.clear(external)
            for template in codec.templates:state.B.clear(template);state.B.home(template)
            with no_decode():integers=machine.run(source)
            recovered=read(integers,S,W)
            need(recovered==coeff,'actual native deferred scale and nearest recovery')
            need(bytes(source.cells)==saved_source and source.head==1,'borrowed normalized opposite return')
            digest=sha256(bytes(integers.cells)).hexdigest();machine.consume()
            with no_decode():wide_conjugate=machine.carrier(left,narrow=False,conjugate=True)
            need(read(wide_conjugate,2*S,q+3)==[v for x,y in vals for v in (x,-y)],'exact opposite-sign conjugation and widening')
            machine.consume()
            failures=[]
            for name,values in (('short_original_field',normalized[:-1]),('unextracted_target_field',normalized+[(0,0)]),('outside_half_disk',[(3*(1<<(q-2)),0)]+normalized[1:])):
                bad=field(values,q);before=bytes(bad.cells)
                try:
                    with no_decode():machine.run(bad)
                except ValueError:failures.append(name)
                else:raise ValueError('missing endpoint guard '+name)
                need(bytes(bad.cells)==before and bad.head==1 and machine.closed and not machine.pending,'failed borrowed field and cleanup')
                clean(bad)
            for alias in (parameters[0].tape,machine.q.tape,machine.pool.tapes[0],machine.output):
                try:machine.run(alias)
                except ValueError:failures.append('descriptor_or_work_alias')
                else:raise ValueError('missing endpoint ownership guard')
            need(all(bytes(x.tape.cells)==raw and x.tape.head==1 for x,raw in zip(parameters,saved_meta)),'borrowed descriptor bytes and origins')
            need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in machine.pool.tapes),'owned endpoint scratch erased')
            scalar_calls=dict(machine.word.calls);machine.close()
            if G:
                wrong_params=[Count.literal(x) for x in (S,b,q,0)]
                wrong=DeferredTail(state,*wrong_params)
                with no_decode():wrong_result=wrong.run(source)
                wrong_values=read(wrong_result,S,q+4*b+6)
                need(wrong_values!=coeff,'actual unchanged-scale endpoint differs on deferred return')
                wrong.consume();wrong.close()
                for v in wrong_params:v.close()
            else:wrong_values=None
            receipts.append(dict(S=S,b=b,Gamma=G,q=q,W=W,recovered=recovered,old_scale_result=wrong_values,
                                 native_product=actual,scalar_calls=scalar_calls,negative_controls=failures,output_sha256=digest))
            for t in (left,right,source):clean(t)
            for v in parameters:v.close()
    print('PASS_DEFERRED_GAUSSIAN_RECOVERY')
    print(json.dumps(dict(canonical_inputs=pins[0],public_files=pins[1],mathematics=math,native_endpoints=receipts,
                         production_transforms_executed=False,CRT_or_extraction_executed=False,no_new_kappa=True),indent=2,sort_keys=True))
if __name__=='__main__':main()

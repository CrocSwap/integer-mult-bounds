"""Independent exact endpoints and actual rounded-native checks.

Prepared for @CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor verifier or dense endpoint routine is imported.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from sources import load,need,PREFIX
from adapter import AdaptedProgram,Request,canonical,norm2
from native import RoundedGaussian


# Independent complex arithmetic and exact elimination.
def z(value=0):
    if isinstance(value,tuple):return (Q(value[0]),Q(value[1]))
    if hasattr(value,'re'):return (Q(value.re),Q(value.im))
    return (Q(value),Q(0))
def plus(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def times(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def reciprocal(a):
    d=a[0]*a[0]+a[1]*a[1];need(d>0,'oracle nonzero pivot')
    return (a[0]/d,-a[1]/d)
def matmul(a,b):
    result=[]
    for row in a:
        out=[]
        for j in range(len(b[0])):
            total=z()
            for k,x in enumerate(row):total=plus(total,times(x,b[k][j]))
            out.append(total)
        result.append(out)
    return result
def invert(matrix):
    n=len(matrix);a=[[z(x) for x in row]+[z(i==j) for j in range(n)]
                     for i,row in enumerate(matrix)]
    for j in range(n):
        pivot=next(k for k in range(j,n) if a[k][j]!=z())
        a[j],a[pivot]=a[pivot],a[j]
        d=reciprocal(a[j][j]);a[j]=[times(x,d) for x in a[j]]
        for k in range(n):
            if k!=j:
                c=a[k][j];a[k]=[plus(x,neg(times(c,y))) for x,y in zip(a[k],a[j])]
    result=[row[n:] for row in a]
    wanted=[[z(i==j) for j in range(n)] for i in range(n)]
    raw=[[z(x) for x in row] for row in matrix]
    need(matmul(raw,result)==matmul(result,raw)==wanted,'independent two-sided root inverse')
    return result
def reference(E,matrix,vector,indices):
    values=[[z(vector[i])] for i in indices]
    product=matmul([[z(x) for x in row] for row in matrix],values)
    out=E.Vec(vector)
    for i,address in enumerate(indices):out[address]=E.C(*product[i][0])
    return out
def error2(a,b):
    return sum(((x.re-y.re)**2+(x.im-y.im)**2 for x,y in zip(a,b)),Q(0))
def h0(E,vector,bit):
    """Direct H/2 oracle, independent of Gaussian phases/butterfly code."""
    out=E.Vec(vector);step=1 << bit
    for block in range(0,len(out),2*step):
        for low in range(step):
            i=block+low;j=i+step;a,b=vector[i],vector[j]
            out[i]=E.C((a.re+b.re)/2,(a.im+b.im)/2)
            out[j]=E.C((a.re-b.re)/2,(a.im-b.im)/2)
    return out
class ExactH:
    def apply(self,state,request,E):
        state[:]=h0(E,state,request.bit)
        return state
class NonlinearBoundedH:
    """Robustness probe; not a claimed realizable Gaussian fault pattern."""
    def apply(self,state,request,E):
        sign=1 if state[0].re>=0 else -1
        state[:]=h0(E,state,request.bit)
        state[0]+=E.C(sign*request.sigma/2)
        return state
def rejected(fn,text):
    try:fn()
    except (ValueError,TypeError) as exc:
        need(text in str(exc),'wrong rejection reason: '+str(exc))
        return str(exc)
    raise ValueError('control accepted: '+text)
def summary_fraction(value,bits=80):
    """Outward display only; exact rationals decide every check."""
    value=Q(value);scale=1 << bits
    return str(Q((value.numerator*scale+value.denominator-1)//value.denominator,scale))


def check_run(program,lower,rounded,vector,wanted,label,nonlinear=False):
    E=program.e;a=AdaptedProgram(program,lower)
    original,_,_=program.execute(vector)
    exact,exact_stats=a.execute(vector,ExactH())
    need(exact==original,'zero-defect execution equals retained source rounding trajectory')
    observations=dict(calls=0,nonzero_defects=0,max_input_norm2=Q(0),max_defect2=Q(0))
    def observe(index,request,before,after,adapter):
        need(norm2(before)<=adapter.domain_bound**2,'whole-program native input invariant')
        need(all(x.norm2()<=1 for x in before),'actual unit-disk native inputs')
        expected=h0(E,before,request.bit);defect=error2(after,expected)
        need(defect<=request.sigma**2,'actual completed native defect')
        observations['calls']+=1;observations['nonzero_defects']+=defect!=0
        observations['max_input_norm2']=max(observations['max_input_norm2'],norm2(before))
        observations['max_defect2']=max(observations['max_defect2'],defect)
    backend=RoundedGaussian(rounded)
    actual,stats=a.execute(vector,backend,observe)
    need(error2(actual,wanted)<=a.total_error**2,'full native output versus exact root')
    need(error2(actual,wanted)<a.tau**2,'complete target strictly met')
    need(observations['calls']==program.h_count,'every actual native entrance observed')
    need(all(stats[k]==exact_stats[k] for k in ('diagonal_real_products','host_complex_roundings',
             'native_calls','rescale_components')),'unchanged ordinary work and stage count')
    if program.context is not None:
        need(a.margin >= 3*a.tau/(4*(program.radius+1)),'all-size Full margin lower bound')
    row=dict(label=label,allocation=a.record(),input_sha256=E.vector_hash(vector),
             exact_root_output_sha256=E.vector_hash(wanted),retained_output_sha256=E.vector_hash(original),
             rounded_native_output_sha256=E.vector_hash(actual),
             actual_error_squared_upper=summary_fraction(error2(actual,wanted),max(80,2*program.target+20)),
             output_differs_from_exact_H=actual!=original,
             observation=dict(calls=observations['calls'],nonzero_defects=observations['nonzero_defects'],
               max_input_norm_squared_upper=summary_fraction(observations['max_input_norm2']),
               max_defect_squared_upper=summary_fraction(observations['max_defect2'],max(80,2*(a.error_bits or 0)+20))),
             work=stats,native_work={k:v for k,v in backend.stats.items() if k!='peak_numerator'},
             peak_native_numerator_bits=backend.stats['peak_numerator'].bit_length(),nonlinear_probe=nonlinear)
    if nonlinear:
        probe,_=a.execute(vector,NonlinearBoundedH(),observe)
        need(error2(probe,wanted)<=a.total_error**2,'nonlinear actual-input substitution')
    return row,a


def source_cases(dense,lower,source,rounded):
    E=source.e
    cases=[('real-two',E.Mat([[2,1],[1,2]]),4,False,8),
      ('complex-two',E.Mat([[E.C(2,1),E.C(Q(1,4),Q(1,8))],
                           [E.C(Q(-1,8),Q(1,16)),E.C(2,1)]]),4,True,8),
      ('indefinite-two',E.Mat([[1,2],[2,1]]),4,False,9),
      ('nonhermitian-four',E.Mat([[E.C(Q(5,4)) if i==j else
                 E.C(Q(1,16*(j-i)),Q(1,32)) if j>i else
                 E.C(Q(-1,32*(i-j)),Q(1,64)) for j in range(4)] for i in range(4)]),4,True,512),
      ('large-scalar-two',E.Mat([[1<<12,0],[0,1<<12]]),4,False,8),
      ('tiny-scalar',E.Mat([[Q(1,1<<80)]]),4,False,512),
      ('zero-shear-eight',E.eye(8),4,True,8)]
    rows=[];retained=[]
    for label,matrix,radius,reversed_wires,incoming in cases:
        n=len(matrix);indices=list(reversed(range(n))) if reversed_wires else list(range(n))
        root=dense.FullRoot(source,matrix,radius,12,indices);inverse=invert(matrix)
        v=E.Vec(E.C(Q((3*i)%7-3,8*n),Q((5*i)%7-2,8*n)) for i in range(n))
        if label=='large-scalar-two':v=E.Vec([Q(1,2),Q(1,4)])
        if incoming==512:v[indices[0]]+=E.C(Q(1,1<<512))
        for backwards,ref in ((False,matrix),(True,inverse)):
            p=root.lower(backwards,incoming);wanted=reference(E,ref,v,indices)
            row,a=check_run(p,lower,rounded,v,wanted,label+('-inverse' if backwards else '-forward'),
                            nonlinear=(label=='real-two'))
            rows.append(row);retained.append((label,p,a,v))
        print('CHECK_FULL_NATIVE_DOMAIN',label,flush=True)
    specs=[('empty',4,[],512),('singleton-idle',1,[[]],8),
           ('mixed-oriented',4,[[((3,0),E.Mat([[1,0],[E.C(1,2),1]])),
                                ((2,),E.Mat([[E.C(2,-1)]]))]],8)]
    for label,n,plan,incoming in specs:
        # Direct fixture bounds 16 cover logical prefixes, their inverses,
        # and endpoint. No bound is inferred from a completed endpoint alone.
        p=dense.NativeProgram(source,n,plan,16,16,4,12,incoming)
        v=E.Vec(E.C(Q(i+1,16*n),Q(-1,32*n)) for i in range(n))
        if incoming==512:v[0]+=E.C(Q(1,1<<512))
        wanted=E.Vec(v)
        for layer in plan:
            old=E.Vec(wanted)
            for ids,gate in layer:
                for i,address in enumerate(ids):
                    total=z()
                    for j,src in enumerate(ids):total=plus(total,times(z(gate[i][j]),z(old[src])))
                    wanted[address]=E.C(*total)
        row,a=check_run(p,lower,rounded,v,wanted,label,nonlinear=(label=='mixed-oriented'))
        rows.append(row);retained.append((label,p,a,v))
    return rows,retained


def controls(dense,lower,source,rounded,retained):
    E=source.e;out={};_,p,a,v=retained[0]
    old=a.error_bits;a.error_bits-=1
    out['underfunded_native_request']=rejected(lambda:a.execute(v,ExactH()),'unchanged adapter allocation')
    a.error_bits=old
    old=a.scale;a.scale=1
    out['missing_power_of_two_scale']=rejected(lambda:a.execute(v,ExactH()),'unchanged adapter allocation')
    a.scale=old
    # A genuine unscaled-domain witness in the actual large-scalar Full word.
    _,big,_,bv=next(x for x in retained if x[0]=='large-scalar-two')
    state=E.Vec(bv);maximum=Q(0);first=None
    for k,(kind,value) in enumerate(big.stages):
        if kind=='D':state=E.Vec(E.rounded(x*c,big.bits) for x,c in zip(state,value))
        else:
            bad=max(x.norm2() for x in state);maximum=max(maximum,bad)
            if bad>1 and first is None:first=k
            state=E.Vec(E.rounded(x,big.bits) for x in h0(E,state,value))
    need(first is not None and maximum>1,'actual Full needs unit-disk input scaling')
    out['actual_unscaled_domain_witness']=dict(first_h_stage=first,max_coordinate_norm_squared=str(maximum))
    data=[(16,0),(0,0)]+[(0,0)]*6;rounded.call(data,1,0,10)
    wrong=E.Vec([E.C(Q(data[0][0],16),Q(data[0][1],16)),
                 E.C(Q(data[1][0],16),Q(data[1][1],16))])
    wanted=h0(E,E.Vec([1,0]),0)
    need(error2(wrong,wanted)>Q(1,16),'missing C phase/normalization counterexample')
    out['missing_C_normalization']=str(error2(wrong,wanted))
    P=8;h=Q(1,1<<P);data=[(1,0),(0,0)]*4;rounded.call(data,1,0,P+4)
    bad=E.Vec([0]*8);need(data==[(0,0)]*8,'reachable all-pair half-even loss')
    want=h0(E,E.Vec([h,0]*4),0)
    need(error2(bad,want)>h*h,'per-coordinate tolerance is not whole-field tolerance')
    out['omitted_dimension_conversion']=str(error2(bad,want)/(h*h))
    tie=Q(1,1<<9)
    need(E.round_q(tie,8)==Q(1,256) and rounded.half_even(1)==0,'distinct host/native tie rules')
    need(E.round_q(-tie,8)==0 and rounded.half_even(-1)==0,'negative ties explicit')
    out['replaced_host_tie_rule']='retained upward tie is 1/256, even tie is zero'
    _,fp,fa,fv=next(x for x in retained if x[0]=='nonhermitian-four')
    finest=E.C(Q(1,1<<fp.incoming))/fa.scale
    need((finest.re*(1<<fp.incoming)).denominator!=1
         and (finest.re*(1<<(fp.incoming+fa.scale_bits))).denominator==1,'incoming-height increment')
    out['omitted_incoming_height_increment']=fa.scale_bits
    req=Request(8,0,12,12);vector=E.Vec([Q(1,4)]+[0]*7)
    good=E.Vec(vector);wrong=E.Vec(vector)
    RoundedGaussian(rounded).apply(good,req,E)
    RoundedGaussian(rounded).apply(wrong,Request(8,2,12,12),E)
    need(error2(good,wrong)>req.sigma**2,'wrong native bit distinguished')
    out['wrong_native_bit']=str(error2(good,wrong))
    idx=next(i for i,(kind,_) in enumerate(p.stages) if kind=='D')
    old=p.stages[idx][1][0];p.stages[idx][1][0]+=E.C(1)
    out['changed_source_page']=rejected(lambda:a.execute(v,ExactH()),'unchanged source plan and coefficient pages')
    p.stages[idx][1][0]=old
    out['non_dyadic_incoming']=rejected(lambda:a.execute(E.Vec([Q(1,3),0]),ExactH()),'original input grid')
    path=PREFIX+'dense.py'
    out['changed_retained_source']=rejected(lambda:load({path:(HERE.parents[1]/path).read_bytes()+b'\n'}),'source SHA256')
    out['bad_request_type']=rejected(lambda:Request(8,True,10,10).validate(),'native selected bit')
    out['native_internal_overflow']=rejected(lambda:rounded.call([(4,0)]*8,1,0,4),'signed word overflow')
    return out


def run():
    dense,lower,source,rounded=load();rows,retained=source_cases(dense,lower,source,rounded)
    control=controls(dense,lower,source,rounded,retained)
    need(any(r['observation']['nonzero_defects'] for r in rows),'actual deterministic defects exercised')
    need(any(r['output_differs_from_exact_H'] for r in rows),'native rounding changes complete trajectory')
    return dict(schema_version=1,claim='source-bound all-size numerical adapter; no new kappa',cases=rows,
                controls=control,summary=dict(trajectories=len(rows),
                  actual_native_calls=sum(r['work']['native_calls'] for r in rows),
                  executed_gaussian_butterflies=sum(r['native_work']['butterflies'] for r in rows),
                  nonzero_internal_roundings=sum(r['native_work']['rounding_events'] for r in rows),
                  host_complex_roundings=sum(r['work']['host_complex_roundings'] for r in rows),
                  real_diagonal_products=sum(r['work']['diagonal_real_products'] for r in rows),
                  controls=len(control),directions='forward and stored inverse'))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
    result=run();encoded=canonical(result)
    if args.write:args.write.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((HERE/'RESULT.json').read_text()),'complete exact scientific receipt')
    print('PASS_FULL_NATIVE_DOMAIN_ADAPTER',json.dumps(result['summary'],sort_keys=True),flush=True)
    print('RECEIPT_SHA256',sha256(encoded).hexdigest(),flush=True)


if __name__=='__main__':main()

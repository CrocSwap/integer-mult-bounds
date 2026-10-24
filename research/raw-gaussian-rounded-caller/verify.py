"""Actual raw factory with independent exact matrix and rounded-state oracle."""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/rational-unitary-fft'))
from exact import C, apply as source_apply
from gaussian_reference import Reference
from raw_gaussian import RawGaussian

RAW_PATHS=[
 'research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py',
 'research/rational-unitary-fft/vendor/stein_rational.py',
 'research/rational-unitary-fft/vendor/STEIN-PROVENANCE.json',
 'research/cubic-cyclic-inverse/vendor/interval_kernel.py',
 'research/certified-gaussian-recovery/intervals.py',
 'research/capped-fusion-t74-k554/outer/check_gaugefree.py']


def need(ok,message):
    if not ok:raise ValueError(message)


def ceil_log(q):
    q=Q(q);n=q.numerator.bit_length()-q.denominator.bit_length()
    return n+int(Q(2)**n<q)


def norm2(v):return sum((z.re*z.re+z.im*z.im for z in v),Q(0))


def product(a,b):
    return [[sum((x*b[k][j] for k,x in enumerate(row)),C()) for j in range(len(b[0]))] for row in a]


def eye(n):return [[C(int(i==j)) for j in range(n)] for i in range(n)]


def inverse(a):
    n=len(a);rows=[list(x)+y for x,y in zip(a,eye(n))]
    for j in range(n):
        k=next((i for i in range(j,n) if rows[i][j]!=0),None)
        need(k is not None,'independent inverse pivot')
        rows[j],rows[k]=rows[k],rows[j];q=rows[j][j]
        rows[j]=[x/q for x in rows[j]]
        for i in range(n):
            if i!=j:
                q=rows[i][j];rows[i]=[x-q*y for x,y in zip(rows[i],rows[j])]
    return [row[n:] for row in rows]


def mv(a,v):return [sum((x*y for x,y in zip(row,v)),C()) for row in a]


def rounded(value,bits):
    def part(q):
        q=q*(1<<bits)+Q(1,2)
        return Q(q.numerator//q.denominator,1<<bits)
    return C(part(value.re),part(value.im))


def execute(plan,vector,bits=None):
    out=list(vector);states=[list(out)];rounds=0
    if bits is not None:
        need(all((q*(1<<bits)).denominator==1 for z in out for q in (z.re,z.im)),
             'independent input grid')
    for layer in plan:
        used=set()
        for ids,a in layer:
            need(not used.intersection(ids),'independent matching layer');used.update(ids)
            before=[out[i] for i in ids]
            values=mv(a,before)
            for i,value in zip(ids,values):
                out[i]=value if bits is None else rounded(value,bits)
                rounds+=int(bits is not None)
        states.append(list(out))
    return out,states,rounds


def operator(plan,n):
    columns=[execute(plan,[C(int(i==j)) for i in range(n)])[0] for j in range(n)]
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def reject(call,fragment):
    try:call()
    except ValueError as exc:need(fragment in str(exc),'wrong rejection: '+str(exc))
    else:raise ValueError('missed rejection: '+fragment)


def one_case(raw,reference,kind,start):
    n,radius,target,incoming=2,Q(4),6,9
    caller=RawGaussian(raw,reference,kind,start,n,radius,target,incoming)
    tau=Q(1,1<<target);g,h=caller.gauge_bound,caller.middle_bound
    delta=tau/(24*g*h*(radius+1));grid=caller.data_bits
    need(caller.diagonal_error==delta,'independent diagonal allocation')
    need(caller.relative_bits==max(1,ceil_log(4*g/delta)),'independent reciprocal precision')
    need(caller.middle_radius==2*g*(radius+1) and caller.middle_target==target+ceil_log(16*g),
         'independent child radius and target')
    need(grid>=incoming and grid>=target+ceil_log(24*n*g*h),'one shared grid input budget')
    for row in caller.diagonal_records:
        need(Q(row['value'])>0 and Q(row['direct_error'])<=delta and Q(row['inverse_error'])<=delta,
             'actual positive direct and reciprocal receipts')
    if kind=='narrow':need(all(a*b==1 for a,b in zip(caller.a_values,caller.b_values)),
                           'one stored chirp exact reciprocal')
    plan=caller.compile();back=caller.inverse_plan
    need(caller.child.builder.bound['data_bits']==grid,'same actual normalized grid')
    need(plan[1:-1]==list(caller.child.plan),'actual normalized child between diagonals')
    forward,reverse=operator(plan,n),operator(back,n)
    need(product(reverse,forward)==eye(n),'exact stored inverse endpoint')
    need(back[0][0][1][0][0]==1/caller.a_values[0]
         and back[-1][0][1][0][0]==1/caller.b_values[0],'stored inverse wrapper order')
    wrong=[back[-1]]+list(back[1:-1])+[back[0]]
    discriminates=operator(wrong,n)!=reverse
    r=n*Q(1,1<<grid);enorm=max(caller.child.forward_error,caller.child.inverse_error)
    need(enorm<=tau/(16*g),'normalized theorem target allowance')
    derived=2*g*enorm+3*g*h*delta*radius+3*g*h*r
    need(caller.raw_error==derived and derived<3*tau/8,'independent three-stage composition budget')
    need((g+delta)*radius+r<=caller.middle_radius,'actual intermediate radius premise')
    need(caller.reference_error<=tau/(8*(radius+1)*caller.raw_inverse_bound**2),'same reference admission')
    need(caller.forward_error==derived+caller.reference_error*radius
         and caller.inverse_error==derived+2*caller.raw_inverse_bound**2*caller.reference_error*radius,
         'forward and resolvent reference charges')
    reference_inverse=inverse(caller.reference_matrix)
    vectors=[[C(Q(3,4),Q(1,8)),C(Q(-1,2),Q(1,4))],
             [C(1),C(-2,Q(1,2))],[C(Q(1,1<<incoming)),C()]]
    trajectories=rounds=0
    for direction,program,wanted,allowance in (
        ('forward',plan,caller.reference_matrix,caller.forward_error),
        ('inverse',back,reference_inverse,caller.inverse_error)):
        for vector in vectors:
            need(norm2(vector)<=radius*radius,'input radius')
            output,states,count=execute(program,vector,grid)
            source,stats=source_apply(program,vector,grid)
            need(output==list(source) and count==stats['rounded_outputs'],'independent versus actual rounded execution')
            need(norm2(states[1])<=caller.middle_radius**2,'actual normalized entrance')
            error=norm2([x-y for x,y in zip(output,mv(wanted,vector))])
            need(error<=allowance**2 and allowance<tau,'complete same-reference error')
            trajectories+=1;rounds+=count
    return dict(kind=kind,start=start,n=n,center_beta=str(caller.beta),data_bits=grid,
                layers=len(plan),trajectories=trajectories,rounded_coordinates=rounds),discriminates


def main():
    raw={p:(ROOT/p).read_bytes() for p in RAW_PATHS}
    reference=Reference.for_cap(raw,97,1,1,2,4,6)
    results=[];order_control=False
    for kind in ('narrow','broad'):
        for start in (8,60):
            result,order=one_case(raw,reference,kind,start)
            results.append(result);order_control|=order
    need(order_control,'wrong stored inverse wrapper control')
    bad=RawGaussian(raw,reference,'narrow',0,1,Q(4),6,9)
    bad.data_bits+=1
    reject(bad.compile,'one raw and normalized data grid')
    bad=RawGaussian(raw,reference,'narrow',0,1,Q(4),6,9)
    bad.middle_radius=Q(4)
    reject(bad.compile,'rounded input diagonal fits common normalized radius')
    value,perturbed=Q(1,16),Q(1,16)+Q(1,1024)
    need(abs(1/perturbed-1/value)>abs(perturbed-value),'direct-only reciprocal error control')
    # Input x is on the F=1 grid. B=1/2 creates a half-grid value;
    # T=4 amplifies its rounding before an exact output layer.
    vector=[C(Q(1,2))]
    plan=[[((0,),[[C(Q(1,2))]])],[((0,),[[C(4)]])],[((0,),[[C(1)]])]]
    out,_,_=execute(plan,vector,1)
    exact=execute(plan,vector)[0]
    need(abs(out[0].re-exact[0].re)>Q(1,2),'omitted input-diagonal rounding control')
    print(json.dumps(dict(cases=results,controls=5),sort_keys=True))
    print('PASS_RAW_GAUSSIAN_ROUNDED_CALLER actual_factory scoped_composition no_new_kappa')


if __name__=='__main__':main()

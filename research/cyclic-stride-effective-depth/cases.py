"""Exact small-cycle, long-chain and scalar-decay evidence."""
from fractions import Fraction as F
from common import need,original as st
from early import solve as truncated
from uniform import admission,error_bound


def compare(length,stride,beta,bits,dense):
    u=F(1,1<<bits)
    phases=[st.ONE,(F(3,5),F(4,5)),(F(-5,13),F(12,13))]
    b=[tuple((1-beta)*v for v in phases[i%3]) for i in range(length)]
    x=[(F((5*i)%9-4,8)+u,F((7*i)%11-5,16)-u) for i in range(length)]
    before=(tuple(x),tuple(b))
    full_tape,short_tape=st.Tape(),st.Tape()
    trace=[]
    full=st.solve(x,b,stride,bits,full_tape)
    short=truncated(x,b,stride,bits,short_tape,trace)
    need(full==short,'exact output equivalence')
    need(before==(tuple(x),tuple(b)),'input source and coefficients unchanged')
    record=admission(beta,bits)
    depth=max(row['level'] for row in trace)
    need(depth<=record['effective_depth'],'effective depth')
    need(full_tape.records<=40*length and short_tape.records<=44*length,'complete traffic bills')
    for row in trace:
        need(2*row['stride']<=row['length'],'chain length at least two')
        need(all(st.norm2(v)<=(1-record['beta0'])**2 for v in row['b']),'certified margin throughout')
    B=max(abs(v[0])+abs(v[1]) for v in x)
    bound=error_bound(B,beta,bits)
    actual=None
    if dense:
        exact=st.exact_cycle_solve(x,b,stride)
        actual=max(st.norm2(st.sub(v,e)) for v,e in zip(full,exact))
        need(actual<=bound*bound,'length-independent original-solver error bound')
    return dict(length=length,stride=stride,beta=beta,**record,
                structural_depth=st.levels(length,stride),effective_observed_depth=depth,
                original_records=full_tape.records,truncated_records=short_tape.records,
                exact_output_equal=True,inputs_unchanged=True,actual_error_squared=actual,
                uniform_error_bound=bound,terminal_zero=all(v==st.ZERO for v in trace[-1]['b']))


def scalar_decay():
    rows=[]
    for g in [1,4,16,64,256]:
        beta=F(1,1<<g)
        for extra in [0,64]:
            bits=2*g+8+extra
            record=admission(beta,bits)
            for phase in [st.ONE,(F(3,5),F(4,5)),(F(-5,13),F(12,13))]:
                for chain_length in [2,3,7]:
                    value=tuple((1-beta)*v for v in phase)
                    steps=0
                    while value!=st.ZERO and steps<=record['effective_depth']:
                        product=value
                        for _ in range(chain_length-1):
                            product=st.rounded(st.mul(value,product),bits)
                        value=product
                        steps+=1
                        need(st.norm2(value)<=(1-beta)**2,'scalar path stable margin')
                    need(value==st.ZERO and steps<=record['effective_depth'],'exact coefficient extinction')
                    rows.append(dict(g=g,bits=bits,phase=phase,chain_length=chain_length,
                                     steps=steps,depth_cap=record['effective_depth']))
    return rows


def main():
    rows=[]
    for g in [1,2,4]:
        for length in range(1,15):
            for stride in range(length):
                rows.append(compare(length,stride,F(1,1<<g),2*g+8,True))
    for length,stride in [(408,169),(985,408),(2378,985),(5741,2378)]:
        rows.append(compare(length,stride,F(1,2),10,False))
    for beta in [F(1,3),F(2,7),F(5,17),F(1,1000)]:
        for length in [7,19]:
            for stride in range(length):
                rows.append(compare(length,stride,beta,40,True))
    decay=scalar_decay()
    print('PASS stride cases',len(rows),'scalar coefficient paths',len(decay),flush=True)
    return dict(cases=rows,scalar_decay=decay,
                scalar_scope='Finite scalar product paths, not executions of arrays with exponentially large length.')

"""All original PR846 kernels with uniform admission and exact output equivalence."""
from fractions import Fraction as F
from common import need,predecessor as source,original as st
from early import solve as truncated
from uniform import admission,error_bound


def main():
    predecessor=source.pinned_vendor()
    rows=[]
    original_bound,original_apply=source.cascade_bound,source.apply_kernel
    comparisons=[]

    def bound(state,length,stride):
        beta,bits,r=state['beta'],state['bits'],state['radix']
        record=admission(beta,bits)
        beta0=record['beta0']
        u=F(1,1<<bits)
        error,norm=F(0),F(r)
        for _ in state['factors']:
            error=error/beta0+error_bound(norm+error,beta,bits)+u
            norm/=beta0
        rows.append(dict(radix=r,length=length,stride=stride,**record,
                         uniform_execution_bound=error))
        return error

    def apply(*args,**kwargs):
        result=original_apply(*args,**kwargs)
        # Swap only this invocation's solve callback; always restore it.
        saved=st.solve
        try:
            st.solve=truncated
            other=list(args)
            other[6]=st.Tape()
            short=original_apply(*other,**kwargs)
        finally:
            st.solve=saved
        need(result==short,'original kernel exact output equivalence')
        comparisons.append(True)
        return result

    source.cascade_bound,source.apply_kernel=bound,apply
    try:
        result=source.kernels(predecessor)
        need(len(result)==300 and len(comparisons)==300,'complete original kernel inventory')
        kernel_rows=rows.copy()
        inherited_controls=source.controls(predecessor)
    finally:
        source.cascade_bound,source.apply_kernel=original_bound,original_apply
    # Float log summaries in the original verifier are presentation only.
    # Preserve exact budgets instead for platform-independent receipts.
    result=[{k:v for k,v in row.items() if k not in ('execution_bound_log2','total_bound_log2')}
            for row in result]
    print('PASS 300 original kernel cases with uniform depth admission',flush=True)
    return dict(cases=result,uniform_budgets=kernel_rows,exact_output_equalities=300,
                inherited_controls=inherited_controls,control_budgets=rows[len(kernel_rows):])

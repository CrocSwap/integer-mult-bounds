"""Independent original-target Reference inverse oracle for periodic outputs.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
No RUN, folded page, Schur assembly or periodic stage function is used.
"""
from fractions import Fraction as Q

def need(ok,why):
    if not ok:raise ValueError(why)

def inverse(matrix):
    n=len(matrix)
    need(n>0 and all(len(row)==n for row in matrix),'square original target matrix')
    augmented=[[Q(x) for x in row]+[Q(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    for column in range(n):
        pivot=next((i for i in range(column,n) if augmented[i][column]),None)
        need(pivot is not None,'invertible original Reference')
        augmented[column],augmented[pivot]=augmented[pivot],augmented[column]
        value=augmented[column][column]
        augmented[column]=[x/value for x in augmented[column]]
        for row in range(n):
            if row!=column and augmented[row][column]:
                value=augmented[row][column]
                augmented[row]=[a-value*b for a,b in zip(augmented[row],augmented[column])]
    result=tuple(tuple(row[n:]) for row in augmented)
    for i in range(n):
        for j in range(n):
            need(sum(Q(matrix[i][k])*result[k][j] for k in range(n))==int(i==j),
                 'all original inverse identity residuals')
    return result

def action(matrix,values):
    return tuple(sum(Q(a)*Q(b) for a,b in zip(row,values)) for row in matrix)

def check(reference,inputs,outputs,precision,error_bound,requested_error=None):
    size=reference.spec.source_size+reference.spec.excess
    need(len(inputs)==len(outputs)==size and all(len(x)==2 for x in (*inputs,*outputs)),
         'complete original complex target data')
    entries=tuple(tuple(reference.entry('narrow',i,j) for j in range(size)) for i in range(size))
    matrix=tuple(tuple(Q(e.value) for e in row) for row in entries)
    inv=inverse(matrix);unit=1<<precision
    rhs=tuple(tuple(Q(row[c],unit) for row in inputs) for c in (0,1))
    actual=tuple(tuple(Q(row[c],unit) for row in outputs) for c in (0,1))
    expected=tuple(action(inv,x) for x in rhs)
    errors=tuple(sum(abs(actual[c][i]-expected[c][i]) for c in (0,1)) for i in range(size))
    residual=tuple(action(matrix,x) for x in actual)
    residuals=tuple(sum(abs(residual[c][i]-rhs[c][i]) for c in (0,1)) for i in range(size))
    need(max(errors)<=Q(error_bound),'complete original Reference inverse error')
    source_size=reference.spec.source_size; excess=reference.spec.excess
    selected=tuple(i+(2*excess*i+source_size)//(2*source_size) for i in range(source_size))
    holes=tuple(i for i in range(size) if i not in set(selected))
    need(holes==tuple(reference.holes),'independent original coordinate geometry')
    need(all(matrix[i][j]==Q(i==j) and matrix[j][i]==Q(i==j)
             for i in holes for j in range(size)), 'exact original identity-hole rows and columns')
    need(all(inputs[i]==outputs[i] for i in holes),'exact original identity-hole values')
    wrong_matrix=tuple(tuple(Q(0) if e.lift and e.value else Q(e.value) for e in row) for row in entries)
    wrong_inverse=inverse(wrong_matrix)
    wrong=tuple(action(wrong_inverse,x) for x in rhs)
    wrong_error=max(sum(abs(actual[c][i]-wrong[c][i]) for c in (0,1)) for i in range(size))
    result=dict(source_hash=reference.description_hash,target_size=size,
                original_entries=size*size,inverse_identity_residuals=size*size,
                input_component_l1_radius=max(sum(abs(rhs[c][i]) for c in (0,1)) for i in range(size)),
                maximum_error=max(errors),maximum_residual=max(residuals),allowance=Q(error_bound),
                identity_holes=holes,wrap_entries=sum(bool(e.lift and e.value) for row in entries for e in row),
                wrong_wrap_error=wrong_error,wrong_wrap_exceeds_declared_bound=wrong_error>Q(error_bound))
    if requested_error is not None:
        result.update(requested_error=Q(requested_error),
                      wrong_wrap_exceeds_requested_bound=wrong_error>Q(requested_error))
    return result

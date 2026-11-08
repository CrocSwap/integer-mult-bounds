"""Independent original-matrix RUN oracles; no author factor replay.
Prepared for @CubeJerry with separate OpenAI Codex assistance. Apache-2.0.
Host arithmetic is external oracle work, not a physical algorithm claim.
"""
from fractions import Fraction as Q

def need(ok,why):
    if not ok: raise ValueError(why)

def nearest_up(x):
    x=Q(x)+Q(1,2)
    return x.numerator//x.denominator

def exact_inverse(matrix):
    matrix=tuple(tuple(Q(x) for x in row) for row in matrix);n=len(matrix)
    need(n>=1 and all(len(row)==n for row in matrix),'square original matrix')
    work=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    for column in range(n):
        pivot=next((r for r in range(column,n) if work[r][column]),None)
        need(pivot is not None,'nonsingular original matrix')
        work[column],work[pivot]=work[pivot],work[column]
        value=work[column][column];work[column]=[x/value for x in work[column]]
        for row in range(n):
            if row!=column and work[row][column]:
                value=work[row][column]
                work[row]=[a-value*b for a,b in zip(work[row],work[column])]
    result=tuple(tuple(row[n:]) for row in work)
    for i in range(n):
        for j in range(n):
            need(sum(matrix[i][k]*result[k][j] for k in range(n))==int(i==j),'original inverse residual')
    return result

def apply(matrix,vector):
    need(all(len(row)==len(vector) for row in matrix),'matrix-vector shape')
    return tuple(sum(a*Q(b) for a,b in zip(row,vector)) for row in matrix)

def infinity_norm(matrix):
    return max(sum(abs(Q(x)) for x in row) for row in matrix)

def original_reference_matrix(reference,start,length):
    """Rounded source Reference block, distinct from ideal unperiodized G."""
    s=reference.spec.source_size;t=s+reference.spec.excess
    need(0<=start and length>=1 and start+length<=s,'ordinary source interval')
    need(2*(length-1)<s,'unique zero lifts')
    indices=tuple(range(start,start+length))
    selected=tuple(nearest_up(Q(t*i,s)) for i in indices)
    phases=tuple(q-i for q,i in zip(selected,indices))
    need(len(set(phases))==1,'one original phase only')
    need(selected==tuple(range(selected[0],selected[0]+length)),'contiguous selected coordinates')
    rows=[];kinds={}
    for row in selected:
        entries=[]
        for column in selected:
            e=reference.entry('narrow',row,column)
            need(e.lift==0,'no nonzero periodic lift')
            need(e.kind in ('unit-diagonal','shared-weight-ratio','omitted'),'ordinary entry class')
            kinds[e.kind]=kinds.get(e.kind,0)+1;entries.append(Q(e.value))
        rows.append(tuple(entries))
    return tuple(rows),dict(source_start=start,source_length=length,phase=phases[0],target_start=selected[0],source_identity=reference.description_hash,entry_kinds=kinds,periodic_lifts=[0])

def check_output(matrix,input_words,output_words,precision,error_bound):
    need(len(matrix)==len(input_words)==len(output_words),'complete inverse output')
    inverse=exact_inverse(matrix)
    expected=apply(inverse,tuple(Q(x,1<<precision) for x in input_words))
    actual=tuple(Q(x,1<<precision) for x in output_words)
    errors=tuple(abs(a-b) for a,b in zip(actual,expected))
    need(max(errors)<=Q(error_bound),'original-reference action error')
    residual=apply(matrix,actual)
    residual_norm=max(abs(z-Q(x,1<<precision)) for z,x in zip(residual,input_words))
    return dict(maximum_error=max(errors),residual_norm=residual_norm,exact_inverse_norm=infinity_norm(inverse),exact_expected=expected,all_rows=len(matrix))

def rational_original_G(m,base,start,length):
    """Exact G with rho=(m+1)/m,a=-m^2 log(base); S=3m,T=3(m+1).
    Entries come directly from the original Gaussian exponent, not D/F/H.
    """
    base=Q(base)
    need(type(m)is int and m>=2 and 0<base<1,'rational exponential witness')
    need(0<=start and start+length<=3*m,'ordinary witness interval')
    indices=tuple(range(start,start+length))
    selected={i:nearest_up(Q((m+1)*i,m)) for i in indices}
    need(len({selected[i]-i for i in indices})==1,'one original phase')
    matrix=[]
    for i in indices:
        row=[]
        for j in indices:
            exponent=((m+1)*j-m*selected[i])**2-((m+1)*j-m*selected[j])**2
            need(exponent>=0,'nearest integer minimizes Gaussian exponent')
            row.append(base**exponent)
        matrix.append(tuple(row))
    return tuple(matrix)

def decode_twos_complement_bits(bits,width):
    need(width>=1 and len(bits)%width==0,'complete Signed widths')
    result=[]
    for offset in range(0,len(bits),width):
        record=bits[offset:offset+width]
        need(all(b in (0,1) for b in record),'binary Signed body')
        value=sum(bit<<i for i,bit in enumerate(record))
        result.append(value-(1<<width) if record[-1] else value)
    return tuple(result)

def selfcheck():
    for m,base,start,length in ((4,Q(9,10),2,4),(5,Q(24,25),3,5)):
        matrix=rational_original_G(m,base,start,length);inverse=exact_inverse(matrix)
        rhs=tuple(Q((7*i+3)%11-5,8) for i in range(length));answer=apply(inverse,rhs)
        need(apply(matrix,answer)==rhs,'all original action residuals')
        transposed=tuple(tuple(matrix[j][i] for j in range(length)) for i in range(length))
        need(apply(transposed,answer)!=rhs,'orientation control separated')
    bad=False
    try:rational_original_G(4,Q(9,10),2,5)
    except ValueError:bad=True
    need(bad,'cross-phase control')
    print('PASS_ORIGINAL_RUN_ORACLE_SELF_CHECK exact_matrices=2 controls=3')
if __name__=='__main__':selfcheck()

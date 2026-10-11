"""Explicit GL cover row invoice; no orthogonal group dimension discount."""
def bound(m,physical,maxchild,depth):
    assert 0<maxchild<m and 2*maxchild**depth<m**depth
    assert physical<2**80
    # |GL_m(F_q)| < q^(m^2); physical < q, with q>2^80.
    # The source GL high-matrix chart has m^2(w-1) digits.
    per_level=m*m+1
    return dict(cover='GL',dimension=m,physical=physical,depth=depth,
                low_stock_digits=per_level,high_matrix_digits=m*m,
                fixed_rows=9909,endpoint_rows=252,
                complete_row_coefficient=depth*per_level+9909+252)

def controls():
    rejected=[]
    for name,values in [('nonhalving',(78,9609,56,2)),('stock_overflow',(78,2**80,56,3)),('nonshrinking',(78,9609,78,3))]:
        try:bound(*values)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    assert bound(78,9609,56,3)['complete_row_coefficient']==28416
    return rejected

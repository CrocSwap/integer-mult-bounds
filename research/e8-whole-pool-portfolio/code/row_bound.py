"""Elementary orthogonal-cover row count; no exact group-order formula is needed.

Over an odd finite field, diagonalize a nondegenerate d-dimensional symmetric
form. Fixing d-1 coordinates of a vector leaves a nonzero-coefficient quadratic
in the last coordinate; hence a prescribed nonzero norm has at most 2*q^(d-1)
solutions. The orthogonal complement of such a vector is nondegenerate.
Induction while choosing the images of a diagonal orthogonal basis gives
|O_m(q)| <= product(d=1..m, 2*q^(d-1)) = 2^m*q^(m*(m-1)/2).
Since q>=3, this is strictly below q^(m*(m+1)/2). Physical family stock adds
ceil(log_3(physical)) to this uniform exponent. The restored-row divisor
argument in PR234/PR386 multiplies it by the halving depth, then adds the
unchanged 9909 and 252 allowances. Routing-time bills still use m^2.

This arithmetic checker verifies the exponent calculation and strict margins;
the preceding elementary induction is the all-q proof, not a finite q sample.
chafreaky with OpenAI Codex assistance, Apache-2.0.
"""
from fractions import Fraction

def bound(m,physical,child,depth):
    assert m>1 and physical>0 and 0<child<m and depth>0
    assert m**depth>2*child**depth
    overhead=0
    while 3**overhead<=physical:overhead+=1
    column_exponent=sum(d-1 for d in range(1,m+1))
    assert column_exponent==m*(m-1)//2 and 2**m<3**m
    cover_exponent=column_exponent+m
    stock_exponent=cover_exponent+overhead
    assert physical<3**overhead and 2**m*physical<3**(m+overhead)
    row=depth*stock_exponent+9909+252
    assert row<20161 and Fraction(10**6)-Fraction(51*20161,25)>0
    return dict(method='successive nonzero-norm vectors in nondegenerate complements',
                minimum_q=3,column_exponent=column_exponent,factor_two_power=m,
                cover_exponent=cover_exponent,physical_families=physical,
                physical_exponent=overhead,stock_exponent=stock_exponent,
                halving_depth=depth,complete_row_coefficient=row,retained_row_coefficient=20161)

def controls():
    rejected=[]
    for name,args in [('false two-level halving',(78,9609,56,2)),
                      ('understated row reserve',(100,9609,90,7))]:
        try:bound(*args)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('accepted '+name)
    # The original coarse enumeration bound does NOT fit this retained row cap.
    assert 3*(78**2+1)+9909+252==28416>20161
    return rejected

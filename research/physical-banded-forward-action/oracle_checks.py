"""Portable finite controls for the independent forward observer.
Prepared for @CubeJerry with separate OpenAI AI verification. Apache-2.0.
"""
from fractions import Fraction as Q


def run(oracle):
    matrix=tuple(tuple(Q(x,3) for x in row) for row in ((1,-1,0),(-1,2,-1),(0,-1,1)))
    rhs=((91,-73,61),(-117,83,-41),(51,-31,101))
    expected=oracle.check_action(matrix,rhs,4,8,Q(1))
    oracle.need(oracle.product_matrix(matrix,((Q(1),),(Q(1),),(Q(1),)))==((Q(),),)*3,
                'nonzero source nullvector without an inverse-F premise')
    short=tuple(tuple(Q(oracle.grid_integer(x,8),256) for x in row) for row in matrix)
    oracle.need(all(sum(row,Q())==0 for row in short)
                and short[0][0]*short[1][1]-short[0][1]*short[1][0] != 0,
                'this P8 rounded fixture also has exact rank two')
    other_grid=tuple(tuple(Q(oracle.grid_integer(x,7),128) for x in row) for row in matrix)
    det=(other_grid[0][0]*(other_grid[1][1]*other_grid[2][2]-other_grid[1][2]*other_grid[2][1])
         -other_grid[0][1]*(other_grid[1][0]*other_grid[2][2]-other_grid[1][2]*other_grid[2][0]))
    oracle.need(det != 0,'singularity is not preserved by arbitrary source rounding')
    floored=tuple(tuple(Q((x.numerator<<8)//x.denominator,256) for x in row) for row in matrix)
    oracle.need(oracle.check_pages(matrix,4,8)!=oracle.check_pages(floored,4,8),
                'negative floor is not source truncation toward zero')
    opposite=tuple(tuple(-x for x in row) for row in matrix)
    oracle.need(oracle.action(matrix,rhs,4,8)!=oracle.action(opposite,rhs,4,8),
                'sign of the lifted coupling is essential')
    bad_lift=tuple(row for source in rhs for row in (source,source))
    bad=oracle.solve_pages(expected['page_words'],bad_lift,4,8)
    oracle.need(bad[::2]!=expected['words'],'nonzero target initialization is not a forward action')
    tiny=((Q(1),Q(),Q(1,1<<80)),(Q(),Q(1),Q()),(Q(),Q(),Q(1)))
    try:
        oracle.check_pages(tiny,4,8)
    except ValueError as error:
        oracle.need('admitted interleaved scalar band' in str(error),'exact-source band control')
    else:raise ValueError('tiny exact off-band entry admitted after rounding')
    three=tuple(tuple(Q(1,4) if i==6 and j in (3,6,9) else Q() for j in range(10)) for i in range(10))
    incoming=tuple((3 if j in (3,6,9) else 0,) for j in range(10))
    separate=oracle.check_action(three,incoming,8,2,Q(1))
    oracle.need(separate['words'][6]==(0,) and oracle.grid_integer(Q(9,16),2)==2,
                'three staged rounds differ from a single completed-dot rounding')
    return dict(exact_source_rank=2,p8_rounded_rank=2,p7_rounded_rank=3,
                controls=('singular nullvector','negative floor pages','opposite lift sign',
                'nonzero target initialization','tiny exact off-band coefficient','three separate rounding sites'),
                scope='finite external observer controls; actual physical cases are registered separately')

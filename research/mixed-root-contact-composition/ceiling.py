"""Bound every binary-child size for the rank 2,3,3,2 root.

Adapted from the prior fixed-root ceiling by Ali Romman with OpenAI Codex.
The contracted native source stays fixed. Other roots and sources are outside
this claim. All arithmetic in this checker uses rational intervals.
"""
from fractions import Fraction as Q

CEILING=Q('.00328587')
BIT_CAP=Q('.0034')
TAIL=100


def run(local,E,root):
    def need(ok,message):
        if not ok:raise ValueError(message)
    need(0<CEILING<1,'Concave price exponent')
    need(root['masks']==[[1,1,1,1],[1,1,0,0],[0,0,1,1],
                         [0,0,0,0],[0,0,1,0],[0,1,0,0]],
         'The ceiling uses the actual paired root masks')
    need([s['stage_rank'] for s in root['sites'] if s['full']]==[2,3,3,2]
         and sum(not s['full'] for s in root['sites'])==3,
         'The ceiling pays both root idles and all thin queries')
    t=1-CEILING
    helper=E.moment(local['helpers'],t)
    paid=E.moment(local['paid'],t)
    native_lower=(paid[0]-helper[1])/104
    derivative_lower=(sum(c*E.power(r,1-BIT_CAP)[0]*E.log_bounds(r)[0]
                          for r,c in local['helpers'].items())
                      -sum(c*r*E.log_bounds(r)[1] for r,c in local['paid'].items()))/104
    need(derivative_lower>0,'The native deficit increases throughout the admitted range')
    h={r:E.power(r,t) for r in range(1,8*TAIL+2)}
    lower=[Q(0)]*TAIL
    upper=[Q(0)]*TAIL
    split_checks=0
    for n in range(2,TAIL):
        node_lower=2*h[8*n][0]+1-2*h[8*n+1][1]
        node_upper=2*h[8*n][1]+1-2*h[8*n+1][0]
        lower[n]=min(lower[a]+lower[n-a]+node_lower for a in range(1,n))
        upper[n]=min(upper[a]+upper[n-a]+node_upper for a in range(1,n))
        need(lower[n]<=upper[n],'Binary subtree interval')
        split_checks+=n-1
    pairs={}
    for n in range(2,TAIL-1):
        pairs[n]=max(h[8*n+1][1]-n*native_lower-lower[n-b]-lower[b]
                     +h[8*b+1][1]-h[8*b][0] for b in range(1,n))
    margins=[]
    for n in range(4,TAIL):
        for a in range(2,n-1):
            margins.append(h[8*n+1][1]+pairs[a]+pairs[n-a]-2)
    finite_upper=max(margins)
    need(finite_upper<0,'Every finite child sum fails at the ceiling')
    # Every binary node costs at least -1 by concavity. For total n,
    # Jensen bounds the two pair outputs and each added increment is at
    # most H9-H8. The resulting upper bound is decreasing for n >= TAIL.
    tail_upper=(h[8*TAIL+1][1]+2*h[4*TAIL+1][1]-TAIL*(native_lower-1)
                +2*(h[9][1]-h[8][0])-6)
    derivative_upper=(8*t*(h[8*TAIL+1][1]/(8*TAIL+1)
                           +h[4*TAIL+1][1]/(4*TAIL+1))-(native_lower-1))
    need(tail_upper<0 and derivative_upper<0,'All larger child sums fail')
    return {'ceiling':str(CEILING),'first_tail_total':TAIL,'binary_split_checks':split_checks,
            'admitted_saving_cap':str(BIT_CAP),'native_derivative_lower':str(derivative_lower),
            'finite_pair_checks':len(margins),'finite_margin_upper':str(finite_upper),
            'tail_margin_upper':str(tail_upper),'tail_derivative_upper':str(derivative_upper),
            'scope':'All positive integer child sizes and all binary tree shapes for this fixed root and PR6372 source.'}

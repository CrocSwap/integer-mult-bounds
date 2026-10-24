# Sharp radii for integer shear reflections

Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.
The orbit/stabilizer method is credited to Nick Petalas, PR #5079.

## Statement

Let `A_k(x,y)=(x+k*y,-y)`, k an integer, K=|k|, and m>=2 an integer.
Minimize `sup_(x in D) ||Q(x)-x||_infinity` over all `Q:D -> Z^2` satisfying
`Q(A_k x)=A_k Q(x)`, with D the complete refined grid or R^2. No continuity,
linearity or translation equivariance is imposed. Requiring Q to fix every
integer point does not change the answer. The attained minima are:

| K | `R_m(k)` on `(1/m)Z^2` | `R_R(k)` on `R^2` |
|---|---|---|
| 0 | `floor(m/2)/m` | `1/2` |
| 1 | `floor(2m/3)/m` | `2/3` |
| positive even | `(K/2+1)*floor(m/2)/m` | `(K+2)/4` |
| odd, at least 3 | `floor(((K+1)*m-e_m*max(K-m,0))/4)/m` | `(K+1)/4` |

Here e_m is one for odd m and zero for even m. One rule on all R^2 attains
all these optima simultaneously on its grid restrictions.

## Orbit reduction and a compatible attaining rule

For an error `(u,v)`, the largest error at the two orbit points is

    N_k(u,v)=max(|u|,|v|,|u+k*v|).

Equivariance forces the second error to be `A_k(u,v)`. For y nonzero the
stabilizer is trivial, so any integer output at one orbit representative
determines both outputs. At y=0 the output must have second coordinate zero.
Nearest-integer rounding of x on that axis has radius at most 1/2, and at
most `floor(m/2)/m` on the grid. It is also an unrestricted N_k-nearest
integer point: an output with nonzero second coordinate has error at least 1.

Thus the optimum is the covering radius of Z^2 in N_k. This follows from
the predecessor's stabilizer-compatible orbit principle, but requires a new
sharp covering-radius computation. Lattice distance is invariant under
integer translations; Q itself need not be translation equivariant. For
distance computations restrict to `0<=x,y<1`. Conjugation by `(x,y)->(-x,y)`
replaces k with -k while preserving the norm and lattice, so assume k=K>=0.

The rule Q is as follows. If y<0, apply A_k to the input, use the positive
half-plane rule, then apply A_k to the output. If y=0, return
`(nearest_integer(x),0)`. For y>0, try `b=floor(y),ceil(y)`. For each b, try
the floor and ceiling of `x+k*(y-b)/2` as a. Among these at most four outputs
minimize `N_k(a-x,b-y)`, breaking ties lexicographically. The next sections
prove that this is a lattice minimizer. The canonical half-plane and fixed-axis
branch ensure equivariance even at ties. Integer inputs have the unique
zero-error candidate and are fixed. This is a mathematical rule using exact
floor/comparison operations, not a physical arithmetic or real-encoding model.

## K=0 and the requested K=1

K=0 is independent nearest-integer rounding in both coordinates, with the
radii in the table. For K=1 and `0<=x,y<=1`, the four corner costs are

    x+y,  max(1-x,y),  max(x,1-y),  2-x-y.

Their minimum is at most 2/3. Swapping x,y and simultaneously complementing
both preserve this minimum, reducing to `y<=x` and `x+y<=1`. There it is

    min(x+y,1-x) <= min(2x,1-x) <= 2/3.

Any output outside the four corners has horizontal or vertical error at
least 1 and cannot improve this bound. Thus this is the exact distance.
The point `(1/3,1/3)` attains 2/3, proving the real optimum.

Every m-grid candidate cost is an integer multiple of 1/m. This gives upper
bound `floor(2m/3)/m`. For attainment put

    p=floor((m+1)/3), q=floor(m/3).

At `(p/m,q/m)` the triangle formula gives numerator
`min(p+q,m-p)=floor(2m/3)`, by the three residue classes of m modulo 3.
This includes the m=2 witness on the fixed axis.

For fixed b the identity

    N_1(u,v)=max(|v|,|u+v/2|+|v|/2)

shows that a nearest integer to `x+(y-b)/2` minimizes the cost. A corner
already achieves at most 2/3; b outside the two adjacent integers has vertical
error at least 1. Hence the attaining rule is a true minimum, also for K=1.

## K>=2: real inputs and even-K grids

Using `max(|u|,|u+K*v|)=|u+K*v/2|+K*|v|/2`, and K/2>=1, gives

    N_K(u,v)=|u+K*v/2|+(K/2)|v|.

Put `t=x+K*y/2`. For fixed b, minimizing over a gives

    dist(t-K*b/2,Z)+(K/2)|b-y|.                 (1)

For K=2h, the first term is independent of b. The exact distance is
`dist(t,Z)+h*dist(y,Z)`, with real maximum `(h+1)/2` at y=t=1/2.
On the m-grid, for each y, t ranges through all m residues as x does.
Both distances can attain `floor(m/2)/m` together. This proves the even row.

For odd K>=3, the first term in (1) depends only on the parity of b.
For `0<=y<=1`, the closest even b is 0 and the closest odd b is 1. Put
`delta=dist(t,Z)`, which is in `[0,1/2]`. The exact distance is

    min(delta+(K/2)y, 1/2-delta+(K/2)(1-y)).    (2)

The arguments sum to `(K+1)/2`, giving upper bound `(K+1)/4`. Equality
holds at y=1/2, delta=1/4. This proves the real odd row. Translating y by an
integer merely exchanges the two parities when appropriate; hence the two
adjacent b values in the rule suffice on all R^2, not just this unit square.

## Odd K>=3: the refined-grid parity correction

Write x=p/m, y=q/m with residues p,q. For fixed q, the possible values of
`j=2m*dist((2p+K*q)/(2m),Z)` are exactly

    0<=j<=m, j=q (mod 2).

Surjectivity follows by solving `2p+K*q=j (mod 2m)`. Equation (2) yields

    2m*d=min(j+K*q,(K+1)*m-j-K*q).             (3)

Both arguments are even. Put `s=(j+K*q)/2`, `L=(K+1)*m/2`. Then
`m*d=min(s,L-s)<=A=floor((K+1)*m/4)`. If m is even, q=j=m/2 is allowed
and makes the arguments equal, proving attainment and the claimed formula.

If m is odd, put q0=(m-1)/2. For q<=q0, the parity constraint gives

    s<=B=floor((K*q0+m)/2)=floor((K*(m-1)+2m)/4).

For q>=q0+1, replace `(q,j)` by `(m-q,m-j)`. This preserves the constraint
and exchanges s and L-s, so `m*d<=B` in this half too. Hence the global
upper bound is min(A,B). At q=q0 the permitted j values make s range over
every integer from `ceil(K*q0/2)` to B. Moreover A is at least this lower
endpoint: before rounding the difference is `(m+K)/4>=3/2`; whenever
`x-y>=1`, `floor(x)>=floor(y)+1>=ceil(y)`. Thus
s=min(A,B) is available and is at most L/2, proving attainment in (3).
Finally

    min(A,B)=floor(((K+1)*m-max(K-m,0))/4).

This is exactly the claimed odd-m correction. These are proofs for every
integer K and m in the stated ranges, not extrapolations from the finite checks.

## Explicit witnesses and consequence

The proof gives attaining grid residues without search. For K=0 use
`(p,q)=(floor(m/2),0)`; for K=1 use the p,q above. For positive even K=2h,
use `q=floor(m/2)`, `p=(floor(m/2)-h*q) mod m`. For odd K>=3 and even m,
use `q=j=m/2`, `p=(j-K*q)/2 mod m`. For odd m, use
`q=(m-1)/2`, `s=min(A,B)`, `j=2s-K*q`, `p=(j-K*q)/2 mod m`.
For negative k replace p by -p modulo m.

Real witnesses are `(1/2,0)` for K=0, `(1/3,1/3)` for K=1,
`(1/2-K/4,1/2)` for positive even K, and `(1/4-K/4,1/2)` for odd K>=3.
Negate the first coordinate for negative k. Lower bounds require the complete
two-point orbit, not merely the error at the chosen representative.

All groups `{I,A_k}` have order two in dimension two, but their optimal real
radii grow as `|k|/4+O(1)`. Finiteness, dimension and group order alone therefore
do not bound the required error allowance. This quantifies the predecessor's
existence theorem; it does not prove reachability of a worst-case orbit at a
physical caller, or price arithmetic, restoration, storage or tape movement.

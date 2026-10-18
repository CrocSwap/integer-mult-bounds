# Soundness of the finite symbolic certificate

The object is the literal eight-operation equation
`eq:eight-packed-additions` in the pinned manuscript. Each operation has a
target t, sign s in {-1,1} and a parity predicate on the other coordinate.
An incoming state supplies carry s at the corresponding operation when its
bit is set. The source bit c is fixed during all eight operations.

## 1. Parity lifting removes the unbounded variables

Set B=2N, N an integer >=2, and write the initial digits as
`u=2g+a, w=2h+b`, with a,b in {0,1} and 0<=g,h<=N-1.
Define an unwrapped trajectory `U_k=(2g,2h)+v_k`, initially v_0=(a,b), by
applying each gate without modular reduction, adding its incoming signed carry
at that gate. Each v_k is an ordinary integer pair depending only on the
incoming state, c, a and b.

Induction over gates proves the actual modular coordinate is `U_k mod B`:
subtracting multiples of **even** B preserves every parity predicate. Thus
all unbounded dependence is contained in g,h,N and exact quotient witnesses
`q_{k,t}=floor((2g_t+v_{k,t})/(2N))`. The signed outgoing carry at a gate is
`q_{k+1,t}-q_{k,t}`. The other coordinate's quotient is unchanged. This also
follows by substituting the previously reduced digit before the update.
The checker verifies each difference is zero or that gate's sign; no carry
magnitude or direction is silently discarded.

## 2. A complete finite partition and exact floor inequalities

For each guard independently use these disjoint intervals:

- left: g=0, length 1;
- middle: 1<=g<=N-2, length N-2;
- right: g=N-1, length 1.

They cover every allowed guard. At N=2 the middle interval is empty and its
polynomial length is zero. For nonempty middle cells we work with N>=3;
all other cells use N>=2. There are 5*2*4*3*3=360 cells.

For a constant proposed quotient q and affine endpoints l(N),h(N), prove

`2 l(N)+v-2Nq >= 0`,

`2N-1-(2 h(N)+v-2Nq) >= 0`.

Because the expression is increasing in the guard, these two inequalities
are exactly sufficient to place every integer in the cell in [0,2N-1].
They certify the quotient for every allowed N, not only at endpoints of a
finite N range. For an affine expression A N+C, nonnegativity for every
integer N>=N0 is equivalent to A>=0 and A N0+C>=0. Both conditions are tested
with exact integers. A negative slope is rejected even if it passes at N0
or at the generator's sample N=4.

All 9 stages (including the input) and both coordinates are checked: 360*9*2*2
=12,960 inequalities. No bounded-height assumption on N is used. Constant
quotients happen to suffice on this partition; soundness would be unaffected
if generation failed to discover them.

## 3. Equality, exclusion, closure and counting

The ideal digit output is `(2g+(a XOR c), 2h+b)`. Its difference from the
actual output on a cell is an affine function of N, since g,h cancel.
A matching cell must have both affine functions identically zero. Every
other cell must have at least one difference provably >=1 or <=-1 for all
allowed N, using the same slope/intercept rule. Therefore no cell with an
unresolved equality at some large radix can be classified as a mismatch.

On matching cells the derived outgoing carry mask is checked to be in
{0,5,10,80,160}. A cell's cardinality is the product of its two affine lengths;
parities are separate cells. Adding the degree-two coefficient vectors gives
the table in README.md exactly. For each incoming-state/control pair the
**total** over both matching and failing cells is checked to be 4N^2=B^2.
Together with unique complete cell inventory, this excludes a missing boundary
region. The middle-cell terms vanish at N=2, covering that endpoint despite
the separate N>=3 inequalities on those cells.

Consequently every matching-prefix transition is certified for all even B>=4.
Induction from incoming state zero proves closure of the matching states at
all segment counts. A mismatch in a low digit cannot be repaired by operations
on higher digits because the cyclic additions propagate carries upward only.
The sum of signed state bits separately on each coordinate is zero for all
five matching states, as checked, so an inactive suffix is restored modulo its
own width. These are the local facts needed by the binary packed caller;
they do not by themselves implement its record motion or correction.

## 4. Inherited fixed-source corollary (not a new formula)

Normalize the table by B^2 and aggregate the four nonzero states into mass E,
with A the zero-state mass. Source zero maps `(A,E)` to
`(A+(1-1/B)E, E/B)`; source one maps it to
`((1-2/B)A, 2A/B)`. All dirty-digit pairs must be present for this counting.

After any matching source one, the proportions are `(1-2/B,2/B)`.
If consecutive source ones are distance d>=1 apart, the intervening d-1 zeros
reduce nonzero-state mass to 2/B^d; this mass and only this mass fails at the
next one. Leading zeros do nothing and trailing zeros preserve total mass.
Thus the survival fraction is the PR1245 product

`product over consecutive source ones of (1-2/B^distance)`.

This derivation requires no independence hypothesis on the chosen source
pattern, but it requires the complete dirty-field product. It establishes no
uniform average bound for a source-restricted physical caller. The mismatch
example `(x,y,z)=(65,65,0)` at K=6,f=3 has the right target and wrong dirty z;
checking only the target would invalidate both closure and the count.

## Trust boundary

This is a written proof plus a finite certificate checked by ordinary Python,
not a proof-assistant formalization. The critical checker consists of literal
source parsing, unwrapped integer gate evaluation, affine inequalities, complete
cell inventory and polynomial summation. The generator's N=4 sample is not a
premise of acceptance. The retained whole-word simulator is used in separately
reported finite checks; those checks are not the universal proof.

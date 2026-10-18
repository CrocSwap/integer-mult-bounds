# Fixed-header stream lowering and hosted support completion

## 1. Domain and inherited call

Fix an eligible odd prime q and m=64. For every integer width w>=1, write

    g = g0 + qG,  g0 in GL_m(F_q),  G in [0,Q)^(m*m),  Q=q^(w-1).

Invertibility over Z/q^w depends only on g0. Thus each low class has the
complete Cartesian high fiber. Order each packet as its low-class label,
then row-major high fields, then payload/spectator fields. Allow arbitrary
complete outside prefix and suffix fields, and arbitrary fields between
the two high fields that a step exchanges. We permute only the current
packet coordinates; we preserve those outside coordinates pointwise.

Assume a completed previous-stage ordinary routine that exchanges two
equal binary chunks with arbitrary intervening and outside spectators,
restores its borrowed fields, and costs at most C_old V u^(1-a_old) on
volume V and chunk width u>=1, where 0<=a_old<1. Its own implementation,
stock admission and borrowing contract remain premises. We do not borrow
another external row divisor for its internals.

Fix the rational route word before choosing w. Require its denominators
and scaling numerators to be units modulo q. The selected words use only
powers of two. Constants below may depend on q and the fixed catalogue,
but not on w or the lengths of spectator fields. We do not claim a
uniform-in-q machine or a bound for incomplete high fibers.

## 2. Carry-aware high-field updates

Consider a column addition y <- y+(a/d)x, with d>0 and gcd(d,q)=1. Write
x=x0+qX and y=y0+qY. From the current low class, compute

    t = (d*y0+a*x0)*d^(-1) mod q,  0<=t<q,
    C = (d*y0+a*x0-d*t)/q.

C is a signed integer. The exact high update modulo Q is

    Y' = d^(-1)*(dY+aX+C) mod Q.

For scaling y <- (a/d)y, use t=a*y0*d^(-1) mod q,
C=(a*y0-d*t)/q and Y'=d^(-1)*(aY+C) mod Q. Negative numerators need no
change to these formulas. Reducing the low and high products separately
without C gives the wrong map in general, as PR2140 already demonstrates.

For one elementary column factor, freeze the current g0 while updating
all 64 high rows. Then permute the complete low classes by that factor.
Each high-row carry uses the low values before that factor. The next
factor uses the next current low class. Since right multiplication by a
unit elementary matrix permutes GL_m(F_q), the low-class map is bijective.

Implement the low permutation by splitting each complete low-class block
onto its destination-class tape, then merging those tapes in class order.
There are |GL_m(F_q)| classes, a fixed number at fixed q. One may instead
use at most |GL_m(F_q)|-1 block transpositions and reuse a fixed set of
split tapes. Both constructions cost K(q)V. They move each whole updated
high/payload block intact. They do not pretend that the 4096 low entries
are independent Cartesian fields.

At w=1, Q=1 and the high operations are identities. The low permutation
still moves complete payload blocks. The complete GL2 packet tests check
this case; returning a changed low index alone would not suffice.

## 3. Sequential primitives and their cost

Use the ordered-affine construction in
`upstream/build/sections/02-streams.tex`, especially lines124-196.
For a complete Q-block fiber, a cyclic shift has two monotone pieces.
Split at Q-offset onto two tapes, then merge the second piece before the
first. Repeat this for each ordered prefix. A fixed integer unit c>0
has c monotone pieces, indexed by floor(cY/Q); merge by the finite
residue condition Y'+jQ=0 mod c. Reverse the split/merge for c^-1.
For negation, keep block 0 and reverse blocks 1 through Q-1 while
preserving each block's internal bit order, using two stack tapes.
Signed rational units combine these operations.

If X precedes Y, implement the addition by Y*=d, then
Y+=aX+C, then Y*=d^-1. The prefix before X contains the low type, so
the finite carry table is available before the ordered shift. If X
follows Y, first exchange the two high fields, execute the same ordered
update, and exchange them back. The intervening fields keep their order.
A column swap exchanges its two high fields in each of 64 rows and
performs the corresponding low-class permutation. A column scaling uses
the scaling formula without an ordinary interchange.

For the high-field exchange, let P=2^u, u=ceil(log2 Q). Sequentially
pad each of the two Q-fields to a P-field, putting zeros outside their
Cartesian Q-by-Q rectangle. Call the completed ordinary routine once;
then remove the padding sequentially. The rectangle is invariant under
exchange and the padded volume is (P/Q)^2 V<4V. We retain all middle and
suffix coordinates. This padding uses the ordinary call's completed
contract; it does not supply that contract or another free routing oracle.

For tape complexity, do not treat Python's large-integer operations as
unit-cost instructions. Maintain local source-field counters and the
fixed-multiplier residue counter independently of unrelated spectators.
Prepare an offset in polynomial time in b=w-1. The complete Q-target
fiber pays for that work because any fixed polynomial in b is O_q(q^b).
Ripple-counter scans and resets have amortized linear cost, as in the
retained lemma. Add linear rewinds and scratch erasure. A constant number
of split/merge passes therefore costs K V, without a per-payload log V
factor. Additional stream scratch uses O(V) cells; the completed ordinary
callee retains its own workspace bound.

Suppose a fixed column word has N_swap swaps and N_late additions whose
source column follows their target. Its reduction invokes

    M = 64*N_swap + 128*N_late

completed ordinary routines. It also invokes a fixed number of ordered
shifts, fixed-unit passes and finite low permutations. Thus, for w>=2,

    T_route(V,w) <= K_aff V + 4 M C_old V u^(1-a_old)
                 <= K V w^(1-a_old).

The w=1 branch costs K V. Inverting the column word reverses its factors,
negates additive coefficients and inverts scaling units; the same bounds
apply. We prove a reduction for these fixed routes, conditional on the
completed callee. The retained BIT proof already states the generic
high-field bound; this package gives selected bindings and explicit bills.

## 4. Selected data routes

For each selected doubled E8 root v, let U_v=[v/2,A_v] be its retained
orthogonal basis. Check U_v^T U_v=I8 and form

    rho_v = [[v v^T/4, A_v], [A_v^T, 0_7]].

We check this exact symmetric involution against the retained geometry.
At stage 0 use identity. At stage s=1,...,8, embed rho_v on axes 0,...,7
and 8+7(s-1),...,8+7s-1. We check all 111 roots and 999 stage descriptors.

If Gaussian reduction gives E_k ... E_1 rho=I, then
rho=E_1^-1 ... E_k^-1. A row addition in E_i becomes the transposed-index
column addition in E_i^-1. `column_word` checks its literal product, so
the symmetry of rho does not conceal a reversed program convention.
The selected words contain at most 77 factors and 3,520 ordinary calls
after the 64-row expansion. Every data route type occurs 64 times in the
retained nine-stage template, including the identity types.

## 5. Hosted residual completion

The selected template has one residual chart, with entrance rank 0 and
identity basis on the first eight axes D={0,...,7}. PR442's hosting lemma
requires an isometry sigma taking that residual subspace onto eight
pending coordinates. It does not prescribe an ordered basis there.

For a retained idle child from level a to b, its pending chart axes are

    {1,...,8+7b-1}                if a=-1,
    {8+7a,...,8+7b-1}            otherwise.

Each serialized hosted descriptor selects an eight-axis slice S. Define
pi by exchanging the sorted sets D\S and S\D pairwise, fixing their
intersection and all other axes. Then pi carries span(D) to span(S).
This permutation needs |D\S| transpositions. No axis-transposition
completion can use fewer: each crossing transposition can move at most
one of the |D\S| required basis axes across the D boundary.

All selected overlapping slots have S={1,...,8}. Here pi is just(0 8).
For all exterior slots, D and S are disjoint and pi uses eight swaps.
We enumerate 111 overlapping descriptors, each occurring 192 times,
and 13 exterior descriptors, totaling 126,432 owner occurrences.

Choose

    sigma = (U_v direct-sum I56)*pi   for the overlapping slot,
    sigma = pi                       for exterior slots.

Compile the owner right action sigma^-1 by pi^T followed by U_v^T on
the first eight axes in the overlapping case. We check the exact 64-by-64
product and the first-eight image subspace for all 124 descriptors.
For the overlapping slot, its projector is
(I8-vv^T/4) direct-sum E8; for an exterior slot it is the coordinate
projector onto S. Thus this completion realizes the same hosted
residual operator D_(sigma P sigma^T) as any ordered-basis completion.

This argument retains PR442's complete arbitrary-correlated-helper
endpoint premise. Distinct same-family slots have distinct residual
projectors, so their owner matrices remain distinct; different physical
families already distinguish their streams. We change no slot assignment
or invocation order. We do not claim that these facts alone prove the
full dirty local program on the stopped GL chart.

We count at most 1,664 ordinary calls per hosted action. Summing
one action over the actual occurrence list gives 76,197,888 calls.
These are route constants; a supplier must still count its actual
route invocations and all other work.

## 6. Remaining obligations

This theorem covers fixed data/header and hosted-owner right actions on
complete stopped GL high fibers. To admit the full selected producer,
a researcher must also supply data-dependent good-child normalizers,
bad-residue fallback and weighted recursive calls, fresh child-weight
reads, full COPY/ERASE lifetimes, and the finite orthogonal-cover to
stopped-GL domain bridge. The inherited completed ordinary implementation
also remains outside this package. We neither select a new frontier nor
derive an improved multiplication exponent from these route constants.

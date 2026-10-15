# Physical controlled adapters with explicit preparation cost

## 1. Contract and selected binding

Fix an odd prime q, atom width w>=1 and B=q^w. A normalizer ADD acts on
addresses by `y <- y+c(prefix)*x mod B`. It permutes the payload bits
stored at those addresses. It does not add or multiply the payload bits.

Place the full parent matrix chart and permitted ancestor controls before
the head/tail address fields. Keep fresh child stock separate from those
controls. Each target is a complete B-element address field. Allow
arbitrary complete intervening fields and arbitrary suffix payload blocks.
The coefficient may depend on the full parent matrix and earlier ancestor
weights; it may not depend on unused child stock or head/tail values.
The offset also uses the designated earlier source address x.

The retained selected template has idle child 6 from level 2 to level 8 on
pair 0. Its pending coordinates are 22,...,63. Copies 0,...,212 host forty
of those coordinates; copies 213,...,221 host none. We select the first
unhosted copy, 213, as PR2160 does. Thus

    P0 = diag(0_22,I_42),  P(g)=g P0 g^-1.

The verifier reads this directly from the retained template and checks the
selected assembly citation. It also recovers 288 rank-42 children over 32
replicas. The current g is the physical idle-stream header, not a local
invocation parameter requiring another owner route.

We use complete stopped-GL charts g=g0+qG. The selected finite template
names an orthogonal cover; we retain that domain bridge as an assumption.
We prove the adapter implementation on the stated GL domain, without
claiming a full dirty hosted invocation.

## 2. One sequential controlled ADD

We instantiate the ordered-affine argument in the retained
`upstream/build/sections/02-streams.tex`, lines 124-196.

For fixed permitted prefix p and source x, set `a=c(p)*x mod B`. A record
at target y must move to y+a modulo B. Split the B consecutive target
blocks at B-a onto two append-only tapes. Merge the second piece before
the first. Repeat in prefix order. During the merge, recompute the same
offset from the same unchanged controls. The target translation is a
bijection for any c, including zero and nonunits.

`controlled_stream.py` implements this order with sequential reads and
append-only writes. It never seeks into payload data. The routine uses
two split tapes and one output tape, restores input/output heads, and
erases the split scratch. A caller may alternate input/output tapes and
erase the superseded input in another linear scan. Additional workspace
is O(V), besides the coefficient evaluator's work. The routine uses zero
ordinary interchange calls.

Parent headers, unused stock, source x, middle coordinates and suffix-bit
positions keep their labels. The routine moves each complete suffix block
without changing its contents. Prefix-controlled execution does not need
to enumerate the parent's entire GL high fiber to prove this per-prefix
identity. The selected caller can apply the same instruction to that
whole fiber, with one fixed program shape.

At w=1, B=q. The parent's high matrix is trivial, but the address ADD need
not be identity. The high-field bypass from fixed header routing does not
apply to these atom fields.

## 3. Full-parent coefficient preparation

The normal-form algebra is the retained source527 theorem, instantiated
by PR2160. We recompute it with an independent implementation to supply
the physical evaluator. From the full g, compute `P=g P0 g^-1` over
Z/q^w. On a good low class, northeast elimination of PC has unit pivots,
giving unit-lower L,R and diagonal pivot vector delta:

    L P C R = E diag(delta) F^T.

Here E selects the first 42 coordinates and F selects the last 42 in
reverse order. All pivot unit tests depend only on the low chart, so
goodness persists across its high lifts. Coefficients still need the
full chart. Inversions occur in coefficient preparation; they are not
free variable address-scaling passes.

For the unweighted normal form, the evaluator computes

    A0 = -(first42 rows of L P L^-1),
    B0 = -R^-1 C L^-1 E,
    K = -(B0+F diag(delta)^-1) E^T
        + F diag(delta)^-1 A0 (I-EE^T).

For diagonal parent weights A, use `L_A=A L A^-1` and `K_A=K A^-1`.
The tail normalizer remains R^-1. We preserve the parent chart throughout
the ADDs. We retain the pivots in

    A_child[k*f+j] = A[k*f+j]*delta[k].

Thus the middle operation remains one contiguous weighted 42f-atom
reversed child. Its implementation and internal borrowing remain a
callee premise. We do not replace it by an ordinary swap and an unpriced
variable-unit scaling.

For an explicit varying coefficient, reorder P0 into active-first form
and take the parent chart's block on coordinates 0,42 to be

    [[1,b],[c,1+bc]],  p=1+bc a unit.

The other coordinates are identity. Direct substitution gives

    L = I-c e42 e0^T,       R = I+(b/p)e63 e21^T,
    delta = (p,1,...,1),
    K[21,0]=c,             K[63,42]=b/p,

with other K entries zero. Weighted coefficients divide these entries
by A[0] and A[42], respectively. For b=1 and c=5t modulo 25, the second
coefficient is 1,21,16,11,6 for t=0,...,4. These matrices have identical
low charts. The complete normalizer also detects the defect: with
A=I, c=5, H=e42 and D=0, replacing only K by its low-chart value changes
the output H[0] from 1 to 6 and D[21] from 20 to 0.

## 4. Common adapter program

For each atom column j, retain all 1785 row-elimination slots, all 1785
column-elimination slots and all 4096 cross-bank slots. A zero coefficient
means a zero-offset pass. We choose this fixed program shape explicitly;
we do not infer a lower bound against other conditional implementations.

Every head slot targets `H[i*f+j]` from `H[k*f+j]` with i>k. Every tail
slot targets `D[i*f+f-1-j]` from `D[k*f+f-1-j]` with i>k. Every cross
slot targets a tail field from a head field. Thus each target follows its
source, even with arbitrary intervening spectators. Execute the forward
slots, the one weighted child, then the reverse slot order with negated
coefficients. Across both adapter halves,

    N = 2f(1785+1785+4096) = 15332f < 240 n_current.

We use the inherited normal-form identity and implement each emitted ADD
as in Section 2. Composition gives a physical reduction with zero ordinary
adapter calls and one separately charged weighted child. The number of
instruction slots does not grow with the
number of high matrices in the stream.

## 5. Good-ancestor weights without a prefix oracle

`GoodWeightChain` stores older-to-newer full parent charts, explicit
coordinate-projector labels and each ancestor's coarse atom-column width
f_l. The fixtures use the selected rank-42 idle label at both levels.
Binding all other selected local-frame labels remains separate work.
Start with a fixed unit root
weight. For current flat index i, evaluate

    A[i] = root_unit * product_l delta_l[floor(i/f_l)] mod B.

This is repeated substitution of the retained contiguous index rule;
each ancestor sees the same flat index i. The evaluator computes each
delta_l from that ancestor's full chart. It checks that the descendant
index fits every ancestor child, and that successive coarse widths are
`floor(r_l*f_l/64)`. The matrices and atom index are allowed controls;
unused child fields are not arguments to this evaluator.

The physical fixture has coarse widths 4,2,1. The first child has 168
atoms; the next has 84. The current 64-atom coarse block fits after the
usual remainder peeling. At index 42, ancestor pivots at indices 10 and 21
are 6 and 11, giving weight 16 modulo 25 from root weight 1. We recompute
these pivots on both stream passes. A low-only ancestor evaluator gives
the wrong physical permutation.

This implements the stated coordinate-projector good ancestry. A literal supplied ancestor-weight
vector is also accepted by the primitive evaluator, with its input-copy
work counted. Mixed bad-class descriptor generation remains outside this
package. Ring-operation counters and control-cell counts are explicit
algorithmic costs, not unit-cost Turing-machine instructions.

## 6. Preparation-sensitive tape bill

Let slot l have suffix-block size S_l>=1 and F_l=V/(B S_l) complete
target fibers. Let E_l bound its fixed-tape control work per fiber:
fetch permitted active controls, compute coefficient and offset, and
restore control-work heads. Recomputing for split and merge gives

    T_adapters <= C N V + 2 sum_l F_l E_l
               <= N V (C+2 E_max/q^w).

Charge shape preparation, stream rewinds, scratch erasure and local
ripple counters in C N V. Keep arbitrary unrelated spectator counters
separate; do not reread their full values for each target fiber. The
simulator caches one coefficient across the source/middle fibers of a
parent header, so this per-fiber preparation allowance is conservative.

For fixed 64-dimensional matrices, schoolbook arithmetic, unit inversion
and sequential work-tape access admit a polynomial bound in w. The
explicit good-chain evaluator uses D ancestor preparations and at most
O(n_current D) weight products. Packed active-header access and copying
its literal unit scratch vectors also have polynomial cost in
`w,D,n_root`. The generated good-chain evaluator therefore has a fixed
polynomial E_max in those variables. More general descriptors may carry
an additional actual access cost R_A, which must stay in E_max until a
caller proves its bound. No arbitrary prefix function receives a free
evaluation oracle here.

To absorb preparation, use the actual stopped-recursion domain. Fix 0<s<1
and root digit width E0, choose `w=ceil(E0^s)`, and keep w fixed down the
coarse recursion. Require

    n_current <= n_root <= E0,
    D <= c_D (1+log2 E0).

Then `E0<=w^(1/s)` and `log E0<=s^-1 log w`. The explicit good-chain
cost is `w^O(1)`, so its ratio to q^w has a uniform finite bound. The
adapters cost O(V n_current), with a constant depending on q,s and the
fixed implementation. A descriptor bound of the more general form
`C(1+w+D+log E0)^k B0^D` also becomes polynomial in w.

Use root width in this argument. A near-leaf call can have small current
n and deep ancestry. For arbitrary independent n,w,D, retain the
preparation-sensitive bound instead of asserting uniform absorption.
Charge the weighted child separately in either formulation.

## 7. Limits

The finite stream tests cover a line of full parent headers and a
two-level ancestry fixture; they do not enumerate GL64. Exact source
binding, direct address checks and the written composition argument
support the stated adapter result. Full weighted-child implementation,
mixed fallback descriptors, complete hosting, fresh-field cylinders,
COPY/ERASE lifetimes, precision and outer transfer remain separate.
We do not change the selected frontier or prove a new exponent.

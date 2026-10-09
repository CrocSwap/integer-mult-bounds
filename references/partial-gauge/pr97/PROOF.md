# Deferred bit endpoints and a signed two-stage complex interface

Under the analytic and fixed finite-alphabet multitape interfaces already
retained by main, the networks in this package give the conditional bound

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
\kappa=63965813/10^{12}>2^{-14}.
\]

The finite checks do not formalize these inherited interfaces or establish an
unconditional integer-multiplication theorem. Repository integration validation
is recorded separately; mathematical certificates and validation receipts have
different purposes. This is not a current-record or global-priority claim.

The scalar/frame inputs are Swapnil Jain's round7 bit network and round6 complex
network, pinned at `741e7aa078392553815df7926ee17ac5e25a8c38`. The original source,
notes, licenses and assistance disclosures are preserved in `swapnil-round7/`.
That source reports a slightly larger final number under its own analytic
stack. We instead use main's retained semantic guard and balanced assembly.
Our additions are explicit reflected scheduling, the commuting fan-order
clarification, gauged exits, a signed complex endpoint correction and a bridge
to the existing main interfaces. No separately researched local role saving is
added to these networks without recompilation.

## Bit word, geometry and common basis

The pinned producer at h=23 has v=1771 and R=28866. Its frozen supports, links,
deferred readouts, V leaves and rational frames are checked by the original
`check_word.py`, `check_frames.py` and `check_lifted.py`. In particular, the
deferred scratch slots are untouched before their deferred readout; their
entrance frames lie in every required target hyperplane. These are conditions
on the complete physical word, not just its ordinary-input support.

`round7_literal_frame_ledger.py` expands that word into 1080616 events and
checks the forward shear on all 32408 ordinary/dirty F2 basis vectors. Gates
with several fan recipients are expanded in stable order of their starting
frame dimension. The recipients are distinct targets of the same unchanged
source, so these XORs commute. The separately checked chains prove nesting;
rank order alone is insufficient. This changes the internal order of160 fan
groups and avoids otherwise uncharged frame retreats, preserving their scalar
map and all costs. The imported source is left intact.

Reverse time, complement the factor frames and exchange the data banks for
stage two. All ordinary gates retain their XOR direction after the exchange.
The new ledger checks continuity and the complete opposite shear; a logical
transpose alone would not prove this statement. A copied-center scatter is a
macro: copy the unchanged center, transport the copy, scatter and discard the
copy. Its reflection creates a new copy at the complemented source and moves
it to the complemented target. No unknown dirty register is erased.

For an idempotent A write D_A=[[I-A,A],[A,I-A]]. Commuting idempotents satisfy
D_A D_B=D_(A+B-2AB). Let P,Q be the two rank-one triple projectors, sigma the
local auxiliary entrance projector of rank f, m=h², and r=h-f. Stage one's
incoming gauge is A=sigma tensor Q, its last live frame is T=I tensor Q,
and its terminal gauge is I-A. Its exterior is

\[
E_1=I-T+A=I-(I-\sigma)\otimes Q,\qquad\operatorname{rank}E_1=m-r.
\]

Direct multiplication gives D_(I-A)D_T=D_E1 and D_(I-A)D_A=D_I. For stage two
put B=(I-P) tensor I and lift a factor frame K to B+P tensor K. Its entrance
is B, last live frame is I-P tensor sigma, terminal gauge is I-B, and

\[
E_2=B+P\otimes\sigma,\qquad\operatorname{rank}E_2=m-r.
\]

Again D_(I-B)D_(I-P tensor sigma)=D_E2 and D_(I-B)D_B=D_I. These are genuine
commuting-idempotent exits, not an assumption that all endpoint movements are
nested. Scalar dirty restoration and complementary gauges give the full
address swap. Both exteriors are charged as block m-2r and the inner(r,h)
profile of their complementary small residual.

With U=P tensor Q, stage-one data ends at (I tensor Q,(I-P) tensor Q), while
stage two begins at (B+U,B). Each connector is (I-P) tensor (I-Q), of rank
(h-1)², and both are charged. The final F2 scalar shear pair gives (y,x+y);
the temporary rank-one correction uses D_U D_I=D_(I-U) to remove the extra
term, retaining one paid rank-one child per pair.

The common rational tensor basis and inner residual profiles use the preserved
`notes/flag-basis.tex`, `notes/partial-swap-batching.tex` and the round7 lifted
checks. The staircase corner adds runs h-2,h-5,1^6, alongside the outer block
m-4h+2. `check_stair.py` checks its finite witnesses and symbolic cut bounds.
The GL_h×GL_h family acts transitively on line pairs; nonzero polynomial
witnesses, together with identically imposed triangular zero conditions, give
a common rational point for the finite family. This is an existence argument,
not a claim that sampled pairs enumerate the family or that one modular basis
is already a common integer basis. Rational enumeration avoiding the finitely
many nonzero determinant polynomials is an effective fixed finite choice.
Its denominators and required minors exclude finitely many odd primes, as in
the retained transfer. All choices are independent of n. The two orientations
and newly gauged residuals occur among the checked inner families.

The actual event histogram, including exits, connectors and corrections,
matches the pinned one with m=529, W=108516254 and s=57403754177. An independent
rational moment enclosure proves saving a_b=31987/500000000.

## Complex scalar word and phases

For the h24 paired triple-exclusion producer, let M be its invertible role
mixer, V the source injection and A the complete signed readout. The retained
totals are T and E_i=sum of triples avoiding i, for i<h-1. Twice the center
scatter at S is 2T-sum_(i in S)E_i if h-1 is absent, and
(5-h)T+sum_(i<h-1,i notin S)E_i otherwise. Adding the signed side pieces gives
2x_S. The exact dense support audit checks all4096576 coefficients of AMV=I.

On arbitrary scratch z, the literal word first subtracts AMz from y, restores
z, injects Vx, adds AM(z+Vx), and then restores z by M^-1 and -V. Thus the
complete shear is y+=x with arbitrary dirty restoration. Reverse order AND
negate every coefficient for the inverse; exchanging the data banks gives
x-=y. This proof applies to the actual fixed h24 word. The independent small
h8/h10 checks replay all formal ordinary/dirty inputs using exact signed
integer encodings with coefficient bounds, and reject missing cancellation
and wrong inverse signs. They are controls, not substitutes for AMV=I.

`round6_complex_literal_ledger.py` explicitly traces all535744 events, the
24 temporary center copies and124369 actual geometric transitions at h24.
Each ordinary scalar gate has equal frames. For the reflected word every
frame and copied-center endpoint is checked. Binary frame inclusion and
nondegenerate nonalternating residuals are verified exactly. Tensor lifting
by an odd triple line preserves the Gram form and oddness. The stage-one
auxiliary exit and stage-two auxiliary entrance each cost m-h=552. Both
data connectors have rank529. Each inner move and center-copy move is a
whole-residual child with its sign wrappers, as in the retained complex
normal form. The rebuilt histogram equals the pinned histogram exactly:
W=207387136, m=576, s=119453132304 and largest child552. Its independent
rational moment certifies a_c=36926111/500000000000.

Complex phases require an additional endpoint argument. Write
C_U=H diag(i^q_U)H, q_U(z)=wt(P_U z) modulo4. For nested nondegenerate
orthogonal sums these phases add. At a tensor data pair let u=q_U(z) and
w=wt(z) modulo4. The two signed shears, with source frames (C_U,I) and
terminal frames (C_F,C_(Uperp)), give

\[
X'=-i^w y,\qquad Y'=i^{w-2u}x+i^{w-u}y.
\]

Pre-translate x by P_U*1, multiplying its Fourier coordinate by (-1)^u.
Copy X', apply C_U^-1, add to Y', and negate X'. The outputs are C_F y and
C_F x, so after the role exchange every data role has the same completed
C_F contract as every restored auxiliary role. The correction is one inverse
rank-one child. Translation and the minus sign have no recursive child.
This works because q_U(z) modulo2 equals z dot P_U*1. For a tensor of two
triple lines, its generator has weight9. No repeated phase2q_U is discarded.
The retained identity C^-1=-i Z C Z executes inverse children with unit
wrappers. Both stage connectors have the same orthogonal increments as on
the bit side, so their phase difference is q_C. Exhaustive controls over all
65536 Fourier addresses at h4 reject omission of the translation or use of
C_U instead of its inverse, each on32768 addresses.

## Integer recursion, precision and fixed tapes

Use the existing whole-residual compiler, compact source/target adapters and
integer-width recursion. At width e, first process e mod m axes individually;
all children then have t floor(e/m) axes for the paid widths t<m. A residual
basis orders its selected axes consecutively. The bit common-basis profiles
above use the inherited aligned and shifted runs. The complex wrappers are
binary address maps and unit phases. All finite descriptors and coefficients
are fixed constants. Unchanged analytic routing/error/recovery assumptions
remain exactly those in main's `notes/structured-bulk-assembly.tex`.

Every completed complex child on u axes is C^tensor u (or its wrapped inverse)
on EVERY returned role, including arbitrary scratch. Its coefficients lie in
2^-u Z[i] and its absolute row sum is at most2^u. This is now applicable to
the changed two-stage word by the signed endpoint proof above. Originals of
temporary copies and all other operands remain parked on the fixed stack
tapes. A completed copy has the same bound as any other completed child.
There is no return rounding, encoding change or promotion of an unfinished
child intermediate to a parent operand.

The actual h24 word has374340 literal scalar updates per invocation. With
two stages, center-copy overhead and four endpoint groups per pair, use
G=1531908928. Coefficients have magnitude at most19/2 and denominator at
most2. A weighted update can be expanded into at most19 unit additions and
one half; its magnitude/denominator excess is at most a fixed20 units.
The conservative charge2GW² dominates these updates and temporary copies,
since W=207387136. Unit phases and address translations add no denominator
loss. With all other retained overhead paid by8s+4W+4+32m, set

\[
E=64(W+m+G+1)^3,\quad B=s+E,\quad C_0=32mB^2.
\]

The exact bridge checks literal charge<E. For f=floor(e/576), the largest
active child has552f axes, while completed children contribute at most sf
to the semantic exponent. Consequently

\[
A(e)\le A(552f)+sf+E\le2Be,
\]

because2B(576-552)>=s+E and direct leaves obey A(e)<=8e. Prefix kernels and
outer normalization add at most18e, below the C0e allowance. Thus the same
fixed fine-grid proof yields C1=1; it does not concatenate temporary internal
excess of already completed children. E and C0 are large but fixed.

The actual maximum child and width determine each least halving degree d_j
and bitlength w_j. Reserve the product W_c^D_c W_b^D_b, with
D_j=d_j ceil(log2(e)), rather than the maximum of the two stocks. The existing
physically preceding transformed prefix and one complete-row padding supply
the recomputed stock; nested bit stock is restored before another complex
child. Sequential temporary copies use this existing row field and do not
introduce a separately live recursive row reservation. The certificate gives
the exact coefficient and sufficient stock degree. These operations preserve
the fixed alphabet, fixed tape count and polynomial descriptor bounds of the
inherited interfaces; the number of fixed-role streams is not the number of
physical tapes.

## Final exact combination

Use beta=1/10 and eta=10^-8. The stopped complex saving (1-beta)a_c exceeds
a_b. Put q=a_b(1-2eta), c=q(1+eta), epsilon=(1-eta)/(1+c+q), lambda'=1-q,
lambda=((1-a_b)+lambda')/2, g=epsilon*q,
r=(g+1-epsilon)/2 and delta=eta/8. The inherited balanced combination now
has all47 strict constraints and all7 margins above63965813/10^12; the
next10^-12 grid point is rejected. This includes the recomputed scalar
charge, product-row gap, compact reservations, phase-cell separation, prime
packing and exact recovery allowances. A second moment implementation
checks both complete recursive histograms with exact rational logarithm and
exponential enclosures. Passing arithmetic does not by itself establish any
of the physical or analytic lemmas above.

## Attribution and scope

Zhihao Chen (jacklightChen): explicit reflected event ledgers, commuting
fan-order clarification, nonzero auxiliary endpoint proof, signed complex
phase controls and corrected rank-one endpoint, and integration with the
retained balanced semantic assembly, with Codex assistance. Subsequent work
using these specific contributions should explicitly acknowledge Zhihao Chen.
Historical GPT-6 Astra assistance attribution on PR7/PR23/PR29 remains;
no claim about the current runtime model is made.

Swapnil Jain supplies deferred readouts, V leaves, lifted frames, the h24
producer, common flag/staircase family and frozen witnesses, with the original
Claude assistance disclosure. Avi Eisenberg/ikeboy PR62 supplies interval
strips and core-aware pair assembly; RaD/hipotures PR41 supplies alternating
order/links, and Rohan Arun PR44 the weighted-link precedent. Aurel Prosz/
Paureel supplies two-stage/complement scheduling; icekylinx PR36 supplies
copied-center and bridge precedents; James Chang PR34 supplies balanced
combination and reversed geometry; Zhihao Chen PR23/PR29 and RaD supply
semantic precision, bulk routing and transfer. All earlier author, license
and AI disclosures in the preserved source and main remain in force.


# Delaying the BIT cover until the whole finite program is compiled

Status: a constructive native-interface argument, with an exact local-ring
audit. This closes the particular common-weight mismatch identified in the
first mixed BIT proposal, conditional on the finite mixed-flow compiler
producing the stated finite projector program. It is not an independent
proof of that compiler's asymptotic termination or of integer multiplication.

Substantial OpenAI assistance. Apache-2.0. This argument uses the arbitrary-
projector GL cover and weighted-child normal form in
[`notes/three-stage-cover-bit.tex`](../../../notes/three-stage-cover-bit.tex),
the retained PR589 local word and its predecessors, and the finite
precompilation proposal in `../architecture/FINITE-PRECOMPILATION.md`.
The decisive order of operations was proposed jointly with the architecture
research task: compile all internal jobs first; apply one common cover and
one common external weight only afterwards.

## 1. The earlier obstruction was real

A productive rank-eight helper is a proper projector job inside a larger
ambient address space. After an ambient GL cover, its endpoint is

\[
D_{gPg^{-1}},
\]

not the same fixed eight-coordinate interchange on every cover row.
Lowering this job immediately to a canonical recursive query introduces a
diagonal weight determined by the pivot coefficients of `g P g^-1`.
Jobs from different parents can have different such weights. The inherited
scalar word accepts one common external weight across every fresh role;
simply placing differently weighted jobs in its roles is invalid.

The solution below does not identify these weights. It avoids creating
weighted internal jobs at all. Only leaves of the entire precompiled word
are lowered to canonical weighted calls.

## 2. Native projector jobs before canonical lowering

Fix an ambient rational head space of dimension `N` and the atom-reversal
matrix `C_N`. For any rational idempotent `P` put

\[
D_P=\begin{pmatrix}
I-P & PC_N\\
C_NP & I-C_NPC_N
\end{pmatrix}.
\]

For `G` invertible let

\[
Q_G=\operatorname{diag}(G,C_NGC_N).
\]

Direct block multiplication gives

\[
Q_GD_PQ_G^{-1}=D_{GPG^{-1}},\qquad
D_PD_{I-P}=D_I.
\]

No symmetry of `P` is required. The second identity says that any source
job and its complementary projector complete the full interchange on that
array. If a unit of rank `m` is used at column multiplicity `c`, first embed
its rational projectors into the chosen `mc`-dimensional coordinate block
of the common `N`-dimensional space. Complete unused coordinates are
spectators. All these dimensions and embeddings are constants of the
finite precompiled program.

The local PR589 primitive, the new global controller, its pointwise boundary
adapters, and owned COPY storage can all be treated as a finite chronological
word of pointwise scalar operations, proper projector requests, restores,
and fixed right-multiplication symbols on one future cover coordinate.
Their exact finite operator identities are established independently of a
generic canonical child normalizer. An internal request may therefore be
replaced by a finite native word computing the same `D_P` on arbitrary data.

This schematic qualification matters. The p3 construction already uses
per-port chart routes to share one local helper bank across 111 data ports.
It is not a 3,739-field word with those routes silently deleted. Before
choosing the final cover, embed every local projector and every port chart
into the common ambient `N`. Preserve all fixed right-route symbols during
substitution. Only then instantiate that single `GL_N` cover. A helper's
endpoint is the rank-eight local-space projector at its local invocation
vertex, while main data endpoints use their port-specific line and stage
projectors. `BIT-P3-NATIVE-BINDING.json` checks every fixed rational port
chart, this ownership distinction, and the complete recursive tariff.

## 3. Equal rank gives a fixed rational matcher

For rational idempotents `P,Q` of the same rank, choose a rational basis of
their images and kernels. Let `B_P` and `B_Q` be the corresponding full basis
matrices, with image columns first. Then

\[
S=B_PB_Q^{-1},\qquad SQS^{-1}=P.
\]

This is a finite rational matrix construction. A physical execution of the
dense address map `Q_S` is **not** assumed. The matcher is used only as a
right multiplication of the full cover row, as follows.

Choose a fixed odd prime `q` avoiding the denominators and nonzero
determinants of every native matrix and matcher in the finite program.
For atom width `w`, use one global cover

\[
\mathcal G=\operatorname{GL}_N(\mathbb Z/q^w\mathbb Z).
\]

All matchers reduce to invertible matrices over this local ring.
An array role is accompanied by the full cover coordinate `g in G`.
Its entries at different `g` are independent data.

Suppose a parent role at cover row `g` requests `D_(g P g^-1)` and a child
target role at its cover row `h` computes `D_(h Q h^-1)`. Before running
the child, route that complete target-role fiber by

\[
x_g\longmapsto y_{gS}=x_g.
\]

Execute the child word on these routed inputs, then undo the role-specific
route. The endpoint on the parent's original `x_g` is exactly

\[
D_{(gS)Q(gS)^{-1}}=D_{gPg^{-1}}.
\]

Every child target role can use its own fixed matcher `S`. Each mapping
`g -> gS` is a bijection of the *whole* cover fiber, so no input is copied,
discarded, or assumed zero. The child word can mix its roles at a common
child row `h`, because those routed inputs are arbitrary independent data.
After the completed word returns its independent endpoints, undoing the
routes restores the parent ordering. The finite flow's ownership and
chronology are still required; cover routing does not repair an aliased
or cyclic flow.

## 4. One common external weight survives every internal routing

At column multiplicity `f`, let the outer invocation's diagonal weight
`A` be any permitted generated descriptor on its `Nf` head atoms. It can
depend on exposed ancestor rows and atom indices. It must be independent
of all fresh role and cover fields of this entire compiled invocation.
Write `Lambda_A=diag(A,I)`.

Conjugate the entire completed covered word by `Lambda_A`. Pointwise scalar
ADDs commute with this common address permutation across roles. Every
internal role route also commutes with it: a route changes only a fresh
role or the current cover row, while `A` is independent of both. Thus the
matching identity becomes

\[
\Lambda_A D_{(gS)Q(gS)^{-1}}\Lambda_A^{-1}
=\Lambda_A D_{gPg^{-1}}\Lambda_A^{-1}.
\]

There is no child-specific weight to reconcile inside the precompiled
word. The source/complement product gives

\[
\Lambda_A D_I\Lambda_A^{-1}=F_A
\]

on every productive source array. This is exactly the inherited weighted
full-interchange endpoint. Owned zero storage is unaffected by address
permutations and is excluded from productive output credit; its allocation,
initialization and final erasure still belong to the finite word.

The condition on `A` is essential. The companion audit exhibits a concrete
failure when `A` is allowed to depend on the current fresh cover row. The
argument does not quietly weaken the old ancestor-only contract.

## 5. Only the final leaves become weighted children

After the mixed finite compiler has replaced every internal request, suppose
the remaining paid projector requests have rank one. At multiplicity `f`,
each is a rank-`f` residual on the outer atom space. Apply the inherited
generic ordered normal form to this *finished* leaf list.

For a generic residue class, that proof produces unit lower intrabank and
cross-bank adapters around one contiguous weighted reversed interchange.
For column `j`, the resulting weight is

\[
A_{\rm child}[j]=A[i_0f+j]D_P[0],
\]

with the inherited reversed tail pairing. The pivot coefficient is evaluated
from the current outer cover row and the fixed leaf projector. Those are
ancestor data when the recursive rank-`f` child is invoked. Its fresh roles
come from unused row stock, so the child's weight is independent of them.

Different leaf calls can have different weights; the ordinary recursion
already permits this. Each such child itself receives one common weight
across all of *its* fresh roles and cover rows. This is the critical
distinction from calling a mixed unit on several already-normalized,
differently weighted parent jobs.

Bad residue classes use the inherited genuine local-ring fallback, including
its swaps, paired scalings and reversals. This is charged explicitly rather
than declaring a nonunit pivot invertible.

## 6. Routing is priced by the retained native lemma

The cover row has the unique chart `g=g0+qG1`, with `g0` in `GL_N(F_q)`.
For each fixed matcher `S`, right multiplication gives a permutation of
the finite low type and a fixed affine map on the high matrix, with carry
determined by the low type. The retained proof of finite cover routing
implements this with a constant number of fixed scalings, ordered shifts
and old atom interchanges. Its cost is

\[
O(Vw^{1-a_{\rm old}})
\]

per fixed route. It is not a free address-gather operation. A precompiled
word contains finitely many matchers, so their total remains a finite
constant times this term. High matrices are streamed by fixed low type;
the number of tapes and program types does not grow with `w`.

The same statement holds for nonintegral rational matchers: choose `q`
avoiding their fixed denominators, use their local-ring representatives,
and apply the retained fixed-rational routing lemma. The exact small audit
uses integral unimodular matchers to exercise the carry formula directly.

## 7. Moment and row-stock consequences

Let the finite uniform compiler have `B` productive source arrays, ambient
rank `N`, and `P` rank-one leaves, with a certified strict inequality

\[
\frac PB N^{-\tau}<1.
\]

The covered, weighted word has the same normalized good-class leaf count.
Choose `q` large enough that the full fallback surcharge fits the displayed
slack. For example, the conservative inherited per-leaf bounds yield

\[
\mu_\tau\le
\frac PB N^{-\tau}
\left(1+\frac{2N^3}{q}\,32N^2\right)<1.
\]

No old fixed choice of `q` or old numerical fallback envelope is reused for
the potentially enormous new `N`. Prime avoidance and a sufficiently large
prime exist because the whole precompiled program is finite.

For the present candidate, use the exact mixed saving
`C0=69/25000=0.00276` for the finite compiler and retain
`C1=11/4000=0.00275` after covering. Put `d=C0-C1=1/100000`.
The former gives `P/B<N^(1-C0)`, so the good moment at `1-C1` is less
than `N^(-d)`. Choose an allowed odd prime

\[
q>\frac{256N^5}{d}=25,600,000N^5.
\]

Then the fallback multiplier is less than `1+d/4`, while
`N^d >= 1+d/2` for `N>=2`, using `log 2>1/2` and `exp x>=1+x`.
Thus the complete moment is strictly below
`(1+d/4)/(1+d/2)<1`. This uses an explicit exponent gap and does not
require knowing the eventual winning template's numerical moment slack.

The cover consumes `N^2(w-1)` high-row digits plus a fixed low-type and role
reserve. Its finite owned-storage and scalar costs may be enormous. They
replace the old constants. For fixed `N` and a fixed finite word, the
ancestor reserve remains `O(w log e)`, and the previous eventual-threshold
arguments still apply after substituting those constants. They cannot be
reused numerically without that substitution.

The existing weighted recursion can now be applied to this one uniform
supplier: every paid query has width at most `f`, the endpoint is `F_A`, and
all routing and scalar terms have the inherited permitted form. This is a
native-interface bridge. The complete final exponent still depends on the
mixed compiler's termination theorem, its exact leaf-count saving, and the
outer multiplication transfer.

## 8. The ordinary BIT saving and explicit template constants

The retained stopped recurrence gives

\[
T(n,w)=O(n+n^{1-C_1}w^{1-a_{\rm old}}),\qquad
a_{\rm old}=384599/10^{10}.
\]

The old atom exponent `1/1000` cannot be reused here: its linear `n` term
would limit the ordinary saving to `0.001`. Instead choose
`delta=3/1000` and `w=ceil(e^delta)` from the original chunk width `e`.
For the whole compiled program set

\[
W(w)=B|\operatorname{GL}_N(\mathbb F_q)|q^{N^2(w-1)}.
\]

A safe reserve is `W(w)^D * S_old`, with
`D >= floor(log_N ceil(e/w))`; all final ordinary children have rank at
most `floor(n/N)`. Therefore the borrowed high-digit count satisfies

\[
k\le D\left(N^2(w-1)+
\left\lceil\log_q(B|\operatorname{GL}_N(\mathbb F_q)|)\right\rceil\right)
+\left\lceil\log_qS_{\rm old}\right\rceil+1
=O_{N,B,q}(w\log e).
\]

This is `o(e)`. For sufficiently large `e`, borrow `k<e/2` high digits,
pad their complete row range once by a factor below two, complete the
ordinary body wrapper, restore the row range, and exchange the high pieces
with the old arbitrary-width supplier. For clarity, the inherited ordinary
wrapper is the chronological sequence

\[
D\leftarrow D-H;\quad F_n;\quad D\leftarrow D+H;\quad
F_n;\quad D\leftarrow H-D.
\]

For `F_n(H,D)=(C_n D,C_n H)` its successive states are
`(H,D-H)`, `(C_n(D-H),C_n H)`, `(C_n(D-H),C_n D)`,
`(D,D-H)`, and `(D,H)`. Thus the two completed reversed body calls
reuse the restored reserve; they are a fixed multiplicity outside the
recurrence. The three bank additions cost `O(Vn)` and are included in the
linear adapter term below. All original complete spectator fields remain
present.

The three root costs are

\[
O\left(V\left[
e^{1-\delta}
+e^{(1-\delta)(1-C_1)+\delta(1-a_{\rm old})}
+e^\delta\log e\right]\right).
\]

Consequently

\[
a_{\rm BIT}=(1-\delta)C_1+\delta a_{\rm old}
=\frac{27418653797}{10^{13}}=0.0027418653797.
\]

Both `delta>a_BIT` and `delta<1-a_BIT` hold strictly. The linear adapter
term and the borrowed-stock logarithm are lower order. One may relax the
ordinary saving to the simpler rational `27/10000=0.0027`.
`BIT-ALLSIZE-PARAMETERS.json` records all strict rational gaps and the
exact mixed margin at `C0`. This remains conditional on the finite uniform
compiler premise; the enormous word is not materialized in this package.

The final ambient dimension is `N`, the productive role count is `B`, and
the rank-one leaf count is `P`. They are not the old `64`, `661`, `3739`,
or the base unit's literal counts. Let `C` be the total allocated owned
array fields, `L` the literal scalar/copy/erase count, and `R` all fixed
right routes including inverses. Keep the full finite matrix and
coefficient-height list. The new fixed tape inventory can use one stream
per productive or owned role, with the inherited parking stack; it is
finite in `B+C`. Every route is charged, and every final leaf has its own
normalization and possible fallback. A rank-one generic normalizer and
its inverse use at most `4N^2-2N` elementary lower/cross-bank shears; the inherited bad
normalizer uses at most `32N^2` recursive calls of width at most `f`.

These constants can be enormous and affect the eventual threshold. Their
dependence on the fixed compiled template does not introduce a new power
of the later input length. The mixed-flow argument is used to bound the
normalized number of paid rank-one leaves; it must not assume that dense
matrix routing costs stay uniformly bounded while the candidate template
dimension `N` is increased in the existence search.

## 9. Exact finite audit

Run:

```sh
python3 -B research/kappa-rebuild/bit/delayed_cover_bridge.py
```

The audit enumerates every one of the 3,888 rows of `GL_2(Z/9Z)` for each
of two independently matched target roles. It checks 7,776 exact physical
projector identities, both full cover bijections, the affine high-row carry
formula, and every one of the 6,561 addresses for common-gauge scalar
commutation. Its external weight is `(2,4)`, so it is not restricted to an
unweighted or constant-across-axis input. The emitted leaf-weight histogram
is nonconstant. Two explicit negative controls reject omitting a matcher
and allowing the external weight to depend on the fresh cover row.

These are independent checks of concrete algebra and a genuine local ring.
The general argument is the conjugacy calculation above, not an inference
from the finite sample.

## Open next questions

1. Independently audit that the finite lockstep compiler only substitutes
   whole arbitrary-input jobs and gives each simultaneously live child role
   a distinct physical array. The row matching here assumes that ownership.
2. Bind the new BIT p3 native physical projector list and its exact local
   primitive into the abstract finite compiler, including all COPY centers.
3. Write the parameter substitutions for the eventual row reserve and the
   final BIT/complex outer exponent. A finite numerical mixed moment alone
   is still insufficient for a new multiplication claim.

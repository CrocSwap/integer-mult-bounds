# Joint native and compiler closure for the selected construction

**Status: proposed source-specific theorem, pending independent review.**
The checks below are complete where their receipts say so; they do not by
themselves establish the universal joint implication.

## Statement and source boundary

Fix canonical main `e54523517d0f03e58352e647c403a5af3e525a57` and the selected
#7000/#7001 raw words. Assume the following three contracts, with the exact
meanings used in `certificates/selected-result.json`:

| ID | Retained statement |
| --- | --- |
| `owned_erasure` | Owned streams and suspended centers obey the retained allocation, erasure and ownership contracts. |
| `precision_tape` | Retained fixed-tape movement and precision/storage prescriptions apply to the new fixed finite template. |
| `analytic_recovery` | Analytic decomposition, fine-prime avoidance and exact integer recovery follow the retained upstream/outer framework. |

The selected raw words then have a constructive alternative implementation
with the same complete conditional bound

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
\kappa=363005817/100000000000.
\]

The construction below supplies the required `native_all_columns` and
`compiler` instances together. It does not infer their conjunction from the
two implications “native implies compiler” and “compiler implies native.”
It first builds finite syntax using exact operator identities; only after
that syntax has been frozen does it construct the execution by a decreasing
runtime measure. No execution of an unavailable fast query enters the first
construction.

This is an alternative selected-source implementation. Its finite carriers
are larger than the original selected carriers; it is not a claim that the
original unmaterialized transition table has been executed. The selected
certificate remains unchanged. No new κ or unconditional theorem is claimed.

The two principal proof inputs are:

* Ali Romman's single-grade compiler, [#7828 at 03b572b3](https://github.com/aliromman/integer-mult-bounds/blob/03b572b3b9ab72c6ba67762e85e1630cda1daad5/research/single-grade-rank-compiler/PROOF.md), with its [application](https://github.com/aliromman/integer-mult-bounds/blob/03b572b3b9ab72c6ba67762e85e1630cda1daad5/research/single-grade-rank-compiler/APPLICATION.md).
* The exact selected native specialization, [#7840 at adf2e0aa](https://github.com/CubeJerry/integer-mult-bounds/blob/adf2e0aa6777977a280ce50f8938f4a0f4f19b76/research/selected-native-four-premise-specialization/PROOF.md), building on Ali Romman's [#7837](https://github.com/CrocSwap/integer-mult-bounds/pull/7837).

The #7846 uniform proof concerns another mixed-rank construction. Its
enumerated compiler was inspected during this investigation, but its claimed
removal of the five assumptions is not a premise of this result.

## 1. Separate denotation from implementation

Write \(Q_E\) for the positive transform on an indicated set \(E\) of active
axes, tensored with the identity on every other axis of the *same complete
field*. A query is a formal instruction with this specified linear operator
as its denotation. This definition makes no fast-algorithm claim.

For complex fields, the selected one-column chart catalogue gives exact
Gaussian-Clifford operators. Tensor multiplicativity proves their identities
at every positive column multiplicity. A scalar coefficient on a graph edge
acts once on the entire array. An intrinsic phase of a tensor-powered chart
acts once per column. The whole-field LAMBDA is a two-term combination after
taking the whole Q²; it is never distributed as a tensor product of sums.
The selected scalar endpoint and full caller identity therefore give the
required direct-sum input/output identity with formal \(Q_E\) queries.

For binary fields, use the selected rational split projectors. In logical
head/reversed-tail coordinates,

\[
D(P)=\begin{pmatrix}I-P&P\\P&I-P\end{pmatrix}.
\]

For complementary disjoint projectors, \(D(P+Q)=D(P)D(Q)\). Nested differences
and whole image/kernel matchers are exact rational identities. The selected
own-word scalar endpoint has precisely the 111 coupled X-to-Y pairs needed
by its paired common routes; the 437 helper returns are independent. This
proves the binary caller identity with formal positive queries on every
complete field, before choosing a cover prime or executing a route.

These are the denotational parts of #7840 §§2–4 and §8. Their proofs use
finite operator equalities, scalar chronology, full spectator factors and
the owned meanings of INIT/CLEAR. They do not use the finite compiler or an
already fast positive query. In particular, temporarily correlated private
values do not become new independent inputs.

The selected source data are unchanged: ambient 153, 23,392 productive
fields and 117,612 paid occurrences for the complex caller; ambient 134,
19,950 productive fields and 107,352 paid occurrences for the paired binary
caller. The raw binary record's stale 127 is not a working ambient.

## 2. Construct finite syntax without executing a query

Here is the needed parametric compiler lemma. Suppose a fixed raw word has
the direct-sum denotation in §1 at every positive integer multiplicity,
with ambient \(A\), target multiplicities \(W_k\) and its actual ordered
paid requests of ranks \(r_j\). Assume its complete normalizers and its
positive disjoint splits have their stated formal identities. Local owned
storage and scalar instructions keep their declared costs.

For two words U,V, start one U instance for every productive role of V.
Different instances receive distinct arbitrary fields and private tags.
Suspend all U instances at the same paid occurrence. The resulting distinct
owners form precisely the roles of one V invocation. Its role-specific
complete adapter normalizes the requested whole job, executes the formal
V word, and returns before U continues. The working ambient is the product
of the two true ambients. All target/paid ranks multiply, while every
spectator remains part of its original array. This is a finite substitution
of instruction lists; the query denotations prove its correctness.

Take power \(v\), and retain all labelled target paths of one type
\((n_k)_k\), where \(\sum n_k=v\). Their common rank and number are

\[
K=\prod_k k^{n_k},\qquad
B=\frac{v!}{\prod_k n_k!}\prod_k W_k^{n_k}.
\]

Give every other target its own zero input. These fields receive no
productive credit. Run all of their instructions and all of their paid
queries, including a query whose current value is zero. The direct-sum
endpoint implies that each such field returns to zero even though it may
have contained nonzero combinations during the word. Retire it only after
that completed endpoint. Nonzero private clears inside the raw word still
use `owned_erasure`.

Split a paid rank larger than \(J\) into consecutive positive blocks of
size \(J\) and its positive remainder, keeping the *original whole*
input/output adapters outside all these blocks. This produces a homogeneous
word of true ambient \(M=A^v\), B independent targets of rank K, and paid
ranks \(h_i\leq J<K\). It has not called an implementation of any query.

Fix a terminal rank \(N\geq2M\). A homogeneous job of e active axes uses
\(c=\lfloor e/K\rfloor\) copies of every active axis and its first Mc
working axes. Its child ranks are \(h_i c<e\); its residual \(e-Kc\)
axes are one-axis queries. All descendants reuse the original N-axis
field. They allocate no missing tensor factor and turn no spectator into
a separate input. Define

\[
D(e)=0\ (e<K),\qquad
D(e)=1+D(h_{\max}\lfloor e/K\rfloor)\ (e\geq K).
\]

A batch divisible by \(B^{D(e)}\) can be grouped into distinct B-role
instances. At a paid occurrence, each instance lends one actual current
owner. There are no aliases, including when that owner is a private
center. The resulting batch size is divisible by the smaller required
width, since D is nondecreasing and a child has depth at most D(e)−1.
Complete the child and restore the role order before advancing that
occurrence. Induction on e therefore generates a finite chronological
word containing only one-axis queries.

Partition N root axes into consecutive tiles of capacity
\(K\lfloor N/M\rfloor\), with the last positive remainder. Reuse the
same batch of \(B^{D(\mathrm{capacity})}\) independently arbitrary full
fields for every tile. Each field receives all N axes exactly once. The
identity on disjoint factors proves the full-rank endpoint. Different
tiles do not introduce additional productive fields.

This supplies the finite compiler contract under the denotational input
of §1. It does not invoke `native_all_columns` as an efficient algorithm
or invoke the selected `compiler` assumption.

## 3. Independent funding of the selected finite words

Put \(t=1-C\), \(T(t)=\sum W_k k^t\) and
\(P(t)=\sum_j r_j^t\). The included arithmetic check reads the exact selected
histograms, imports no contributor scientific module, and checks the
recorded #7828 types with a separate rational-series engine.

It certifies every exchange inequality for the actual weights
\(a_k=W_k k^t\):

\[
\frac{a_i}{n_i+1}\leq\frac{a_j}{n_j}\quad(n_j>0).
\]

Thus all selected last priorities dominate all unselected next priorities.
The type is a multinomial mode. There are at most \((v+1)^d\) types, so

\[
BK^t\geq T(t)^v/(v+1)^d.
\]

The checks use lower/upper rational enclosures \(T_-\leq T(t)\) and
\(P(t)\leq P_+\), and a strictly positive common bound

\[
\delta\leq1-P_+/T_-,\qquad
\delta\leq\log(T_-/P(1))+C\log8.
\]

For \(v=2^j\), the certificate has
\(v\delta\geq d(j+1)+3\) and \(K\geq16^v\). Splitting at \(J=8^v\)
costs at most \(P(t)^v+2J^{t-1}P(1)^v\). Consequently its paid-to-target
moment ratio is at most

\[
3(v+1)^d e^{-v\delta}<3e^{-3}<3/8.
\]

The finite homogeneous recursion satisfies

\[
F(e)=(e\bmod K)+B^{-1}\sum_iF(h_i\lfloor e/K\rfloor),
\quad F(e)=e\text{ for }e<K.
\]

Induction using the moment ratio below one half gives
\(F(e)\leq2K^{1-t}e^t\). There are at most \(3M/K\) root tiles;
concavity over their lengths yields

\[
P_N/W_N\leq2(3M)^C N^{1-C}.
\]

For \(N=2^H\), the exact checks

\[
H\geq1+v\lceil\log_2 A\rceil,\qquad
H(C-U)>1+C(2+v\lceil\log_2 A\rceil)
\]

therefore give \(P_N/W_N<N^{1-U}\). All introduced zeros, private
lifetimes, split adapters, complete routes and local records stay in the
separate physical bill; they are not additional productive credits.

| Selected source | v | H in N=2^H | Raw C | Uniform U |
| --- | ---: | ---: | ---: | ---: |
| Binary | 68,719,476,736 | 21,179,507,725,498,843,136 | .00385253 | .0038525299 |
| Complex | 281,474,976,710,656 | 817,416,431,103,305,304,760,123,392 | .00363005817007 | .00363005817006 |

For both selected sources, \(W_N\leq N^{15}\). The conservative existing
\(O_{\rm source}(N^{51})\) bound covers pre-cover logical records and
bank occurrences. It counts the entire expanded chronology, not physical
bits or the binary cover. The proof of §2 provides the required constructive
generator even though this enormous finite word has not been materialized.

## 4. Fix the whole template and only then lower the queries

Binary compilation is done over the rationals. After the finite word,
every whole-job matcher, inverse and rank witness have been generated,
choose an odd prime \(q>2^{45}N^5\) outside the complete finite exclusion
list. A raw-frame exclusion list alone would not suffice. On every
\(\mathrm{GL}_N(\mathbb Z/q^w)\), right multiplication by a fixed matcher
is a full-row bijection. Its exact low/high carry and inverse are supplied
by #7840 §4. The role-diagonal compiled endpoint permits independent whole-job
matchers; the coupled raw pairs retain their common matcher.

One common exterior weight conjugates the whole completed binary word.
It may read exposed ancestors and atom indices, and is independent of the
fresh role and cover. Hence it commutes with every fresh right route. New
weights created at a rank-one leaf read the now-exposed parent; they do not
silently become functions of the child's fresh cover.

Only the final one-axis query list is normalized into runtime children.
The full-ring argument supplies one width-f child on a good row and at
most \(32N^2\) children of width at most f on a bad row. The bad fraction
is at most \(2N^3/q\), including every low type and high lift. The resulting
moment factor is less than \(1+64N^5/q\), not one. The separate saving
loss \(d=10^{-10}\) pays it, because

\[
64/2^{45}<d/4,\qquad N^d\geq1+d/2.
\]

The completed covered binary saving is therefore .0038525298, exactly
the rate used by the selected cold ordinary chain.

For the complex template, all split and placement identities retain the
full left and right factors and their absolute phases. The final one-axis
query at outer multiplicity f is one width-f positive complex child; inverse
orientation has its existing ordinary correction. A completed query returns
before any dependent scalar or unscale. No scalar sum is tensor-distributed.

## 5. A well-founded execution, with an elementary base

First implement a radix digit exchange by elementary complete scans. This
has saving zero, restores arbitrary payload, gaps, suffixes and heads, and
requires no compiled fast service. Now construct ordinary stages 1,2,3 in
that order, at savings .0034, .0038507 and .00385248. Fix the previous
stage's algorithm, constants and cutoff before constructing the next.

Within one stage, a recursive native call at active width d has
\(f=\lfloor d/N\rfloor<d\) whenever the uniform word is entered. Its
good and bad normalized children have width at most f. A smaller than N
case and a remainder use elementary completed work. Route interchanges
use the already completed previous ordinary stage, at any required width.
All other newly generated instructions are finite local scans, scalars,
descriptors and ownership services under the retained contracts.

Order calls by the lexicographic pair (stage, active width), with the
elementary stage first. Every same-stage recursive edge strictly decreases
width; every ordinary-control edge strictly decreases stage. This gives
termination and correctness by nested strong induction. It is the required
simultaneous implementation argument, rather than a cycle between two
existence statements.

The exact ordinary recurrence with \(\rho=1/250\) and covered saving b
admits any next saving below \((1-\rho)b+\rho a\), also below \(\rho\)
and \(1-\rho\). The three positive rational gaps are respectively

\[
546399601/1250000000000,\quad
24601/1250000000000,\quad
53101/1250000000000.
\]

After stage 3 is completed, construct the complex service as the next
tier. Its numerical children decrease active width, and its ordinary
movement invokes the completed stage 3. The same lexicographic induction
applies. The .00385248 service exceeds the selected .00376669 movement
requirement. No cold seed assumes the fast operation it is meant to build.

### 5.1 The recurrence is parameterized by the new fixed template

The exact retained source for this use is
[`DELAYED-COVER-BRIDGE.md` §§6–8](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md).
Section 7 begins with arbitrary fixed productive width B, terminal rank N
and paid count P satisfying a strict moment inequality. Section 8 gives
the ordinary conversion with its *new* N,B,P, full route and owned counts,
and explicitly permits those constants to change. Its displayed numerical
example is not the hypothesis of the parameterized argument. The selected
application's §3 uses that argument with atom exponent 1/250; #7840 §6
starts it from the elementary service. Here B is the newly constructed
W_N and N has the binary H in §3, throughout all three stages.

Let F denote the now-frozen binary template, including its chosen q and
all lowered routes. Put t=1-b, where b=.0038525298. By §4 its complete
weighted moments satisfy

\[
m_F(t)<\frac{1+d/4}{1+d/2}<1,\qquad m_F(1)\leq m_F(t),
\quad d=10^{-10}.
\]

For completed predecessor saving a, charge the actual finite routes,
normalizers, private work, local scans, returns and parking by a constant
A_F(a), times complete volume, with node tariff
`n+w^(1-a)`. This is the retained primitive tariff in its stated domain,
not a claim that a matcher is a free permutation. A weighted base pair
is lowered into three ordered shifts, four completed predecessor swaps
and a fixed sign, as in `three-stage-cover-bit.tex`, “Weighted leaves.”
Consequently a width induction with the two moments gives

\[
T_{F,a}(n,w)/V\leq K_F(a)\,[n+n^t w^{1-a}].
\]

Choose K_F(a) to cover the finite n<N base range and both positive
denominators `1-m_F(1)`, `1-m_F(t)`. No ordinary execution is needed to
compute F or its moments. A previously completed stage supplies the
ordinary calls in A_F(a); it does not supply the same-stage numerical
children used by this width induction.

For original digit width e put `w=ceil(e^(1/250))`,
`n=ceil(e/w)`, and define the actual productive-cover stock by

\[
R_F(w)=W_N|\mathrm{GL}_N(\mathbb F_q)|q^{N^2(w-1)},\qquad
D_F(e)=2+\lceil\log_N\max(1,n)\rceil.
\]

Borrow `R_F(w)^D_F(e)` rows before the body. More explicitly let
`ell_F=ceil(log_q(W_N |GL_N(F_q)|))`; the high-digit reservation

\[
k_F(e)=D_F(e)[N^2(w-1)+\ell_F]+1
\]

suffices. These are the new W_N,N,q, not the raw 19,950 roles or ambient
134. For e>=1 the conservative bound

\[
k_F(e)\leq C_{\rm row}e^{1/250}\log_2(2e),\qquad
C_{\rm row}=16(N^2+\ell_F+1),
\]

follows from w<=2e^(1/250) and D_F(e)<=4log_2(2e).
Every actual old-leaf external divisor, if an implementation retains one,
is multiplied in as `S_old`, exactly as in the pinned prescription. The
elementary stage needs none. The completed ordinary stages constructed
here borrow and restore their own digits, so their public arbitrary-width
interface likewise needs no external row divisor. Their internal reserves
are still retained during a nested invocation. There are at most three
fast ordinary stages on a live chain; building all of them in the same
radix q keeps each lower-stage target width at most e above the stock
cutoff. The sum of their live productive-cover reservations is therefore
at most `3 C_row e^(1/250) log_2(2e)`. This bound concerns productive-cover
rows; owned banks and compact controls have the separate stock factors
in §6 and are not credited by it.

Choose the new cutoff so that this bound is <e/2, all primitive and
descriptor domains hold, and all prior-stage cutoffs are fixed. Such a
cutoff is effective: on dyadic e, the fixed linear factor in log e is
eventually dominated by e^(249/250); choose a strict integer inequality
and an index beyond its decreasing-ratio boundary. The complete wrapper
borrows once, pads the complete row by less than two, executes the two
reversed-body calls and three bank additions in their prescribed order,
restores and unpads, and exchanges borrowed high pieces using the
completed predecessor. The two body calls reuse the same reserve. There
is no new padding at each same-stage recursive edge. Any padding nested
across the three *different* completed ordinary stages costs a fixed
factor, which is included in the stage constant.

This gives precisely

\[
O_F\!\left(V\left[e^{1-\rho}
+e^{(1-\rho)(1-b)+\rho(1-a)}
+e^\rho\log(2e)\right]\right),\quad \rho=1/250.
\]

At stage i freeze its actual constant K_i, its restored-stock interface,
and a cutoff E_i at least the thresholds just described. Widths below
E_i use the completed predecessor; since this is a finite range its
slower bound enlarges only K_i. Above E_i, the three strict rational
gaps displayed earlier pay all three terms. Each new E_i may depend on
the enormous F and all previous constants. The same fixed N and q work
at every stage because stage changes alter only the predecessor service
inside A_F(a), never the finite rational template or its paid moment.
Numerical embedding back to binary costs the retained factor below q²
after completion. These quantifiers do not require one threshold or
constant uniform over a family of growing templates.

## 6. Verify the new template's admitted boundaries

### 6.1 The retained premise is a parameterized grammar contract

The phrase “new fixed finite template” in `precision_tape` must be read
through its pinned proof supplements; its one-line label alone does not
license replacing a particular source by an arbitrary program. At the
canonical base, [`SPECIALIZATION.md` §§1,3,6](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/final4610-independent-admission/SPECIALIZATION.md)
explicitly admits fixed finite Gaussian-dyadic monomial/positive-child
programs with arbitrary complete owners and spectators. Its §6 permits
new dimensions, operation counts, coefficient allowances and owned-bank
allocations. The selected #7000 [application §6](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)
instantiates exactly this substitution after finite compilation and says
that N is determined independently of these implementation constants.
`DELAYED-COVER-BRIDGE.md` §§6–8 supplies the distinct rational-cover
grammar. Its right-route alphabet is fixed unit scaling, ordered shift,
completed predecessor interchange, low-type selection and inverse return.
Thus the retained prescription applies to a new fixed template **after**
its operations and parameter domains have been checked, rather than by
adding an assumption that our template itself is physically admissible.

The required mapping for this compiler is explicit:

| Generated instruction | Retained grammar and condition |
| --- | --- |
| An original complex raw occurrence, including whole LAMBDA and odd scale | Same selected scalar/ADD/positive-child/monomial alphabet; the coefficients and their per-occurrence common-grid bounds are unchanged. |
| Product/scheduler placement and return | A fixed permutation of complete coordinate blocks and genuine role rows, lowered into selected elementary additions/moves; inverse return is retained. |
| Positive disjoint split | Successive positive children on disjoint coordinate blocks; retain both original whole-job factors around the entire split. |
| Binary image/kernel matcher | A fixed rational invertible matrix in the complete new N-dimensional cover; choose q after all matrices, lower its full right-route expansion by §4, and charge inverse/low return. |
| Retained/discarded target and private bank | A distinct actual complete field and tagged lifetime; zero targets earn no productive credit. Initialization, retirement and nonzero raw clears remain `owned_erasure`. |
| Rank-one numerical child | Same positive complete-field service at strictly smaller active width, with the same retained precision/layout ABI. |
| Low type, phase, carry, coefficient or owner descriptor | A fixed finite recipe with polynomial address-length work, charged to the complete record fibre under the existing descriptor tariff. |

No instruction requires a generic dense address gather, a new scalar
species or an input-dependent tape alphabet. For a complex coordinate
monomial on N axes, the selected elimination has at most `4(N+1)^2`
elementary records. For a binary directed right route, #7840 §4 gives
at most `2N^3` previous-stage swaps, `N^3` ordered shifts including carry
and `N^2` fixed scalings, plus actual low-selection/return scans. These
larger N-dependent bounds are charged, not replaced by raw-frame counts.

The physical tariff's parameter domain is also unchanged. The ideal
operator identities hold for every positive multiplicity f. The fast
complex movement tariff is used only with `f<=p`, descriptor address
bound `A_desc=O(p)`, record parameter `K_rec/log p -> infinity`, complete
dirty-control reservations, and a record fibre exceeding every needed
fixed polynomial. These are the explicit domains in `SPECIALIZATION.md`
§3; arbitrary independent choices of f,p and geometry are outside the
claim. In the actual selected layer, `f<=D<=p^epsilon`, epsilon<1.
All template dimensions and descriptor degrees are fixed before p varies,
so their new coefficients change eventual thresholds but preserve these
asymptotic domains. Binary coefficient formulas are evaluated with
`w=ceil(e^(1/250))`; fixed branching through O(log e) ancestor levels
has fixed polynomial cost in e and therefore in w. The complete q^w
target fibre admits that work beyond a new fixed threshold. Small cases
use completed elementary/predecessor evaluation.

### 6.2 Substitute actual counts and verify the source depth

Changing the finite compiler changes its constants. Use the actual
generated number of owned fields, scalar records, split adapters, whole
routes, full N-dimensional right-route expansions, low-type tables,
descriptor production, parking and retirement. No raw `<10^12` allowance
is substituted for all those new operations. The original fixed-template
stock and tariff prescriptions are applied to their new finite counts;
for example the retained guard is formed from the actual W,P,O,G values:

\[
Z=W+O,\quad E_0=64(Z+N+P+G+1)^3,\quad
B_0=P+E_0,\quad C_0=32NB_0^2.
\]

These are effective integers defined by the finite instruction generator.
Over-reserving a separate complete bank for every owned/discarded-target
occurrence is permitted by the retained prescription. For each selected
complex raw caller charge the source's scalar coefficient 44,943,309,537,280
and elementary movement count 29,531,542,656, with their actual primitive
constants; binary raw occurrences use their separate source allowance.
Add every compiler placement, full new route and primitive workspace after
that multiplication. The new N,W,P,O,G enter simultaneous compact/row
stock, parked-parent extents, setup degrees and cutoffs. This is a use of
`precision_tape` in its existing parameterized meaning, with the grammar
mapping above, and not a proof of that retained physical contract.

The new compiler's unfinished raw-context depth also has an explicit
check. A chronological product has at most v open raw levels, and a
homogeneous recursion has depth at most H/v because every paid child
shrinks by at least \(2^v\). Allowing the caller/native boundary gives

\[
L\leq2v(H/v+1)=2(H+v).
\]

With the selected common-grid factor 356, the two values 356L have bit
lengths 74 and 99, respectively. Both are strictly smaller than their
new N, checked without materializing N. For an outer original root of D
axes and \(\ell=\lfloor\log_ND\rfloor\geq1\),

\[
356L\ell<N\ell\leq N^\ell\leq D.
\]

At \(\ell=0\), elementary base work applies. Thus the original selected
prefix height/mass bounds admit the new stack depth. The entire D-axis
root stays present, completed siblings return their own denominator debt,
and there is no intermediate truncation. The existing common grid,
temporary W+26 allowance and once-only final truncation can be used with
the new finite constants. This does not prove actual fixed-tape storage,
blank grants or erasure: those remain the named retained contracts.

Since the compiler and all catalogues are fixed before operand length
varies, their finite extra constants and polynomial reservations have an
effective eventual threshold in the retained prescription. All smaller
lengths use elementary algorithms. No practical crossover is asserted.

## 7. Apply the unchanged outer price and delimit the progress

The complex uniform saving exceeds the selected κ by exactly \(6\cdot
10^{-14}\). The covered and ordinary binary rates are unchanged. Apply
the source-bound selected outer argument with these rates and the new
permitted fixed-template constants, retaining `analytic_recovery`. This
gives the theorem stated at the beginning.

The new contribution is the explicit joint construction and its selected
source binding. The finite source denotations, product idea, modal funding,
native normalization and cold ordinary formulas retain their predecessor
credit. The separate arithmetic engine checks both selected carrier
certificates and all 493 modal exchange comparisons against actual power
intervals. Finite checks support the arithmetic and implementation; the
universal statement rests on the inductions above and the cited exact raw
identities. This is model-assisted review, not independent human review or
formal-kernel acceptance of the multiplication theorem.

### Open next questions

1. Give a complete physically priced allocator/eraser for the additional
   compiler target zeros together with a real nonzero raw private clear and
   its suspended parent. Endpoint zero alone does not supply fresh backing
   or pay a nonzero clear. This targets `owned_erasure`.
2. Lower a generated N-dimensional binary right matcher through its full
   descriptor, carry, parking and return services at the stated tariff.
   Algebraic bijectivity and an effective finite catalogue do not price the
   actual full-array movement. This targets `precision_tape`.
3. Independently review the retained complete analytic and integer-recovery
   implication at the unchanged outer parameters. The present construction
   does not discharge that separate premise.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Ali Romman, the selected CubeJerry/DreamingOfClouds raw-word lineage,
Jacob Alan Sussman, zxv, Cinna Davis, and the original source notices.

# Owned nested rises are ordinary paid jobs under the retained contracts

This is a source-bound conditional implication, not a new primitive theorem or
complete supplier admission. It resolves the direction and current-content
part of the `A6` question in CrocSwap/integer-mult-bounds#6902. **No new κ.**

The exact proposal is frozen at `e4d42607f24d7a049b0fca329dc4c34882405c25`;
the canonical mathematical contracts are frozen at
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. All quoted source files are retained
unchanged, with original paths, commits, Git blobs and SHA256 in
`RETAINED.json`. The original strict verifier and the proposal remain unchanged.

## 1. The quantified claim

Fix the exact nine-axis frame representatives and 23 owned-rise events of
the frozen proposal. Let `f` be any positive integer. Replace each of the
nine logical axes by `f` axes, retain arbitrary complete spectator fields,
and let the currently owned input field have arbitrary contents. The contents
may be a previously read or updated linear combination of other fields.

Under the **retained** positive-child, monomial movement, complete-field
ownership and chronological compiler contracts, every one of these rises
is implemented by:

1. Its recorded input monomial on the actual owned field.
2. One completed positive rank-`r*f` child on that same field.
3. Its recorded output monomial on that field.

Here `r` is the difference of the two frame dimensions. No fresh productive
input is created, no owned target is credited, no additional owned bank is
needed, and the two monomials fit the route group already charged for the
event. This holds at every positive width in the algebraic sense. Its physical
tariff retains the original admissible layer domain and complete-control
reservations, including `f<=p`, `A=O(p)` and the superpolynomial record fiber.

Consequently **upward direction, earlier reads and intervening scalar contacts
do not require an additional operator or ownership axiom**, once the stated
generic contracts are applied to the actual source fields and fresh finite
constants as below. The historical P104 descending-only verifier is a genuine
restriction of that verifier's admitted family; the proposal is outside it.
This theorem supplies the larger-family implication. It neither changes the
verifier's policy nor declares the full proposal accepted.

The five framework contracts themselves are not proved here. In particular,
nonzero owned erasure, the physical compact-control primitive, complete
recursive native execution, global source/caller endpoint correctness and
outer analytic recovery remain separate. A convention called `A6` may remain
in a proposal's metadata pending review, but its direction/content clause need
not be treated as an unexplained new physical primitive.

## 2. Exact operators, not just rank counts

For the fixed one-column frame representative `T_U`, the retained convention
is `L(T_U)=T_U^{-1} L_0`. A physical change from `U` to `V` is

\[
M_{U,V}=T_VT_U^{-1}.
\]

The source `notes/general-clifford-frames.tex` proves for arbitrary binary
subspaces that

\[
d(L_U,L_V)=\dim U+\dim V-2\dim(U\cap V).
\]

For `U` strictly contained in `V`, the Fourier rank is therefore
`r=dim(V)-dim(U)`. The same note's **Exact representatives and nested children**
statement explicitly quantifies over every such pair and factors the exact
operator as

\[
M_{U,V}=L_{U,V}F_rR_{U,V},\qquad
F_r=C^{\otimes r},\quad
C=\frac{1+i}{2}I+\frac{1-i}{2}X.
\tag{1}
\]

Both adapters are Gaussian-dyadic monomials, including their absolute fourth-
root phases. They need not be an inverse pair. This positive statement, not
symmetry of a cost formula alone, licenses the required upward transition.
The source's lowering algorithm emits (1) for every actual event; the package
compares those complete matrices independently, as described in §6.

For completeness the reverse direction has the same child class. Since
`C^2=X`,

\[
F_r^{-1}=X_{(1,\ldots,1)}F_r,
\quad
M_{U,V}^{-1}=R_{U,V}^{-1}X_{(1,\ldots,1)}F_rL_{U,V}^{-1}.
\]

The extra translation is monomial. This does not replace exact phase checking
by equality of binary symplectic matrices. Using the adjoint child without its
correction changes the operator and is rejected by the checker.

At width `f`, tensor functoriality applied to the **product** (1) gives

\[
(T_VT_U^{-1})^{\otimes f}
 =L_{U,V}^{\otimes f}F_r^{\otimes f}R_{U,V}^{\otimes f}.
\tag{2}
\]

After the fixed regrouping of axes, the middle term is the canonical positive
rank-`r*f` job, identity on every other coordinate. A constant monomial phase
`i^a` becomes `i^(a*f)`, not `i^a`. Each exterior scalar ADD/COPY coefficient
of the role program remains unchanged. No tensor power is distributed over a
matrix sum. Identity on complete spectators in (2) implies the operator
identity on arbitrary correlated arrays, not only product-state arrays.

## 3. Why the actual contents and read history are allowed

The relevant contract is stated positively in
`FINITE-PRECOMPILATION.md` §1 and §6:

* Productive jobs accept arbitrary complete arrays and preserve complete
  spectators.
* An owned center may be the physical input field of a paid round, even when
  it contains a nonzero linear combination made by its parent.
* A child receives that very field, with separate tags for its own centers;
  distinct physical slots cannot be aliased.
* The parent resumes, reads or erases the field only after the entire child
  unit has completed, including its adapters and role restoration.

The reviewed #4416 chronological-product proof states the same requirements
for owners that may be correlated and may be owned centers. The source
`SPECIALIZATION.md` §§3–4 applies this general grammar to fixed catalogs of
arbitrary nested frames, rather than to one historical list of chart labels.

To apply that contract, maintain the current frame `U` and current physical
array `a=T_U^{\otimes f}z` of each live field. At an owned rise, take `a` as
the child input. Formula (2) returns `T_V^{\otimes f}z` in the same bank.
This equation is valid for every `a`, so it needs no assertion that `z` is
independent of other current values. A prior scalar read did not modify that
field. A prior scalar write merely changes `z` to another allowed arbitrary
array. A later read occurs after the completed child and uses the new actual
chart. Scalar contacts between two rises use the actual intermediate chart.
Nothing is moved across those contacts; no commutativity is assumed.

This is an induction over the literal chronological events. It is not an
inverse-transpose transformation of INIT/CLEAR, a replacement of a private
fanout by a collector, or a claim that a discarded value was uncomputed.
The older #2479 warning correctly forbids transplanting a pure-copy owner
bill to a changed accumulator without this additional contract and charge.
Its finite dual remains credited precedent; it is not used as the admission
theorem for these fields.

The source-bound lifetime scan checks all 38,334 events. It finds:

| Property | Exact result |
| --- | ---: |
| Public physical fields | 1375 |
| Reserved native owned labels | 51 |
| Owned lifetimes / peak live | 54 / 30 |
| Dirty clears, under retained owned-erasure | 53 |
| Owned-rise events / rank mass | 23 / 56 |
| Lifetimes with a read before the first rise | 3 |
| Lifetimes with a scalar contact between rises | 3 |
| Owned reads of the second target plane | 8 |

`LIFETIMES.json` gives each exact birth, death, frame and intervening event.
The scan checks current charts, initialized ownership, same-frame scalar
incidences, distinct physical sources and destinations, and final owned return.
Its ideal symbolic COPY is addition into an ideal zero. It is not assignment
semantics that would discard a numerical residual.

## 4. Complete local payment and owned allocation

The 23 rises have paid profile

\[
10H_1+4H_2+H_3+6H_4+H_5+H_6,
\]

and rank mass 56. These events are already included in the literal native
histogram `{1:4262,2:855,3:770,4:220,5:306,6:13,7:10,8:4}`, of rank mass
10,872. This package does not add a Gaussian job, remove one, create credit,
or change that histogram.

For each monomial, the fixed record realization of #5445 uses `XROW`, `NOT`,
`S`, `CZ` and lifted global `I` records. Its explicit general nine-axis bound
is 171 records. Thus two adapters have at most 342 records, fitting the
retained 1000-unit **group** allowance from `SPECIALIZATION.md` §5. Every
actual pair is serialized and checked: the largest monomial has 79 records,
the largest pair has 147, and all 23 pairs total 2019. The existing route
charge for these 23 events is 23,000. There is no use-dependent fusion or
discount. The 1000 units are finite primitive-record accounting, not literal
tape steps; every movement retains its width-dependent source tariff.

The owned fields retain the same complete ambient address rectangle as other
fields. A smaller child rank changes the selected coordinate action, not the
bank's capacity or its spectator ranges. The local word uses its declared 51
distinct owned labels, with the exact lifetimes above. The compiled adapters
act on the current bank and use the retained movement primitive's restored
complete control fields/work tapes. No additional full data bank is needed
for the direction change. That statement does not make the movement workspace
or its initialization/return free.

For the eventual finite compiler, use a disjoint tag for every instantiated
native occurrence. Reserve all 51 native banks for each such occurrence until
it finishes; this conservative allocation suffices even though only 30 are
simultaneously live within one invocation. Add the separately required query,
completion, splitting and compiler-owned banks. A child receiving a parent's
center uses that existing field as its productive slot; its own banks have
different occurrence tags. The parent remains suspended until the child's
complete return. No one-bank-per-recursion-depth reuse is claimed.

If `J` is the number of native occurrences in the final fixed finite template,
`51J` is a valid native-bank contribution to its full owned inventory `O`.
It is not its complete `O`, and no factor of it contributes to productive
width `W`. The full-field storage and all init/scalar/route/erase/parking
operations are retained in the physical bill. The template and these finite
counts are fixed before the multiplication input size grows.

## 5. Numerical interpretation and fresh finite constants

Neither a rise nor the above argument introduces a new numerical opcode.
Monomial permutations/unit phases preserve magnitude and denominator height.
A completed rank-`r*f` positive child has the inherited conservative row-sum
and dyadic-denominator bound `2^(r*f)`. Its orientation has the same bound.
If its incoming error is `E`, a conservative output error is therefore
`2^(r*f) E + R`, where `R` includes the child and its two actual adapters'
implementation errors. Correlation with other fields is immaterial to this
operator norm estimate.

COPY must be executed as ADD into the currently initialized owned field.
Any residual is propagated with that ADD and through later children. Erasing
the owned bank later does not erase its earlier effect on another field.
Dirty erase and subsequent initialization continue to require the retained
owned-erasure interface. This package does not supply that physical algorithm.

The final expanded word must use its own `W,P,O,R,G,N`: productive width,
rank-one paid children, complete owned allocation, all routing/native records,
fresh scalar/phase allowance and fixed ambient rank. Define `G` by charging
the literal scalar instructions (including COPY as an ADD majorant for
residual propagation), and the retained non-scalar/unit-phase overhead.
No old one-center count, old prefix norm, old caller raw cap or historical
precision word width is substituted for these new constants.

Under the retained semantic precision contract, the same source prescription
then uses

\[
Z=W+O,\quad E_0=64(Z+N+P+G+1)^3,\quad B=P+E_0,\quad C_0=32NB^2.
\]

The completed-child argument from `FINITE-TEMPLATE-CLOSURE.md` gives
`A(e)<=A(floor(e/N))+P floor(e/N)+E_0` and hence `A(e)<=2Be`.
The fresh `C_0` and matrix/record counts determine a fresh eventual threshold,
row reserve, stock and tape setup. This is a conditional finite-template
specialization; no enormous template is materialized and no global precision
assumption is independently discharged here.

The same source-specific pattern already appears in the merged independent
validation of Ali Romman's #5377 construction, documented in
`research/owned-relation-independent-validation/README.md`: changed owned
lifetimes require fresh constants and
distinct suspended banks, while remaining in the existing five-contract
framework. The present result supplies the exact event, operator and
allowance evidence for the 23 different rises in #6902.

## 6. Exact verification and the extent of independence

`verify.py` authenticates the retained inputs before loading the credited
Clifford compiler. It checks strict frame inclusion independently by explicit
finite subspace enumeration, scans the actual owned lifetimes, emits every
rise's exact two-sided recipe, checks signed tableaux and global phases, and
constructs every fixed monomial record list. The frozen recipes and lifetime
artifact must reproduce completely, not only by matching counts.

`independent.py` imports neither that compiler nor the primary verifier. It
constructs the exact frame operators directly from their displayed basis and
quadratic-phase formula, using span membership to extend the basis. It applies
each quotient to **all 512 basis inputs**, in Python integer Gaussian
numerators over powers of two, and compares every matrix entry to the
serialized positive-child factorization. It also executes every adapter's
record list on all one-column addresses and sampled width-two/three addresses
with arbitrary spectators and correctly multiplied absolute phases.

These two algorithms were written by the same research agent; code/mechanism
independence is not a claim of separate authorship or human review. The lead
researcher separately reviewed the nested-factorization/arbitrary-owner
implication against the pinned source grammar, the full-spectator product
lift, the fresh `51J` bank contribution and the scoped remaining premises.
The written
product/ownership argument above supplies the universal-width implication;
finite matrices authenticate its exact unary inputs. A full native/caller
replay, physical fixed-tape execution and a multiplication theorem are not
claimed by these checks.

Controls reject a public/owned alias, a missing clear, a rank-zero substituted
MOVE, a changed global phase, an uncorrected adjoint child and a tensor phase
left unmultiplied by `f`. The historical descending-only condition rejects
exactly the 23 indexed events, identifying the old family boundary rather
than treating that rejection as a mathematical counterexample.

## 7. Related recent work and remaining obligations

The bounded successor survey checked the following exact open heads. None is
silently treated as a current-supplier physical implementation:

* #6890, `e56a5bcf239fa0cd4ee57459af04c0ba7acb2c03`, proves the selected #6030
  assembled algebra with ideal resets. Its operator-product lift is credited;
  its 29-label source and native inventory are not the new #6902 word.
* #6896, `0ca312ed12585a1dc56bcb3d90354f8c6307dc28`, and #6897,
  `f04a672856f8f7cf9fc290bbd55ee4a7a77a126b`, prove capacity and word margins
  for the historical dimension-64/rank-at-most-42 physical caller. Their
  explicit exclusions prevent transplanting those bank bounds here.
* #6901, `4c7a4f00f09665276e145ac2cc1d12f8b8f9a7ac`, proves a current ideal
  compiler common format and leaves actual owner presentation, nonzero erase
  and physical native interiors separate. No sharp word-format constant from
  it is reused for this changed word.

The next consequential obligation is the complete current-source physical
entry/return and owned-erasure implementation, with its full stock, setup,
allocation and visited-space bill. Separately, the exact full #6902 native and
caller endpoint, its global normalization, proposed BIT supply and complete
outer inequality application need their own admissions. Resolving the owned
rise's local direction/content clause does not settle those questions.

## Credit

Prepared for **@CubeJerry**, with substantial **OpenAI Codex assistance**.
DreamingOfClouds supplied #6902/#6883 and its explicit A6 question. Credit the
general Clifford frame and native/compiler work of icekylinx, Dugongue, zxv,
Cinna Davis, Jacob Alan Sussman and the retained source authors; Chris R /
Clear1nsight supplied the #5241 specialization and the independent validation
of Ali Romman's #5377 owned-relation construction; Matarener supplied #5445's fixed monomial record
realization. The #2479 dual warning and recent @CubeJerry proofs are credited
within their stated scopes. Apache-2.0. No independent human, formal-kernel or
maintainer acceptance is claimed.

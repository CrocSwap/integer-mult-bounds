# Exact matched profiles for PR6375 and its retained PR6372 baseline

This is a finite, source-bound **formal recursive-invoice audit**, not a
supplier-admission result. The two independently written profile extractors
read the literal words and fixed controller as data. Neither executes the
vendored constructor/controller code or imports the author's invoice engine.
The tables and accounting identities below are derived from those data, rather
than copied from the author's RESULT receipt.

This first checkpoint establishes the exact invoice to which a later
tariff-exponent proof must apply. It does **not** establish the approximately
0.873 relative-gain threshold or any new kappa. In particular, the author's
separate proof that the complete raw-kappa crossing is unique below its cap
is already predecessor coverage; that is not the missing threshold addressed
by the planned continuation.

## 1. Frozen source and common boundary

The candidate is PR6375 head
`247b5c319b9f58fe9ee61dbf80697f8a9a429831`. The baseline is the exact PR6372
word retained by that head, originating at
`b556600ffe14be72406b03a47c661f3c7f1aff06`. The candidate WORD Git blob is
`b1cfd03abe9128cf5a3908fbd82652e5e8a2e292`; the retained baseline WORD blob
is `0af79e58172f85c302c35b193205c0b185b09393`. Their compressed source bytes
are authenticated separately; compression is not used to define mathematical
word equality. [SOURCE-PINS.json](SOURCE-PINS.json) gives their SHA256 pins
and the other exact inputs.

Both invoices use the same retained controller blob
`1f2e375b24aba5fb25580dfea7fab7a2049f3eb8`: nineteen LOCAL calls,
sixteen thin QUERY calls and sixteen paired whole IDLE calls. Both local words
have 770 public roles, the same 104 live input ports, and 29 owned role labels.
Main public roles are precisely `live` and `live+112`, giving 208 main roles;
the other 562 public roles supply the local helper targets. Owned roles are
not productive public helpers.

The source frame tables, final public frames, main-role list, ports and owned
inventory are unchanged. Exactly six public initial frames change. All later
comparisons use this common caller and boundary: no target, idle, query or
unchanged paid job is dropped because it cancels in the final difference.

## 2. Declared rank tariff and its applicability boundary

For a frame label `a`, let `S_a` be the binary span of its literal generators
in `F_2^9`, and let `d_a=dim(S_a)`. Dimension is established by binary linear
algebra, not by assuming that the supplied generators are independent.

The retained nested-frame recursive tariff charges a MOVE from `a` to `b`
one job of rank

`rho(a,b) = |d_b-d_a|`,

provided the two source spans are strictly nested. The extraction checks the
actual source labels against the evolving role frames and checks strict
containment. This is important: unrelated frames of the same dimensional
difference would not acquire this tariff by a mere rank-count coincidence.
Every literal MOVE is charged, including owned-role MOVEs and both directions
of a trip. The trailing ownership flag changes no recursive charge into a
free operation.

A public non-main helper whose initial span is contained in its final span
contributes one productive target of rank

`tau(r) = d_final(r)-d_initial(r)`.

That is the declared endpoint target contract, conditional on realization of
the corresponding independent native helper channel. Changing an initial frame
therefore changes its productive credit even if the scalar program still has
the same number of roles. No owned lifetime supplies a productive helper
credit. INIT, CLEAR, ADD and SCALE supply no extra recursive job under this
model; their actual ordinary implementation and funding remain obligations.
In particular, excluding them from this recursive histogram does not assign
their physical work zero cost.

These rules identify the finite invoice being audited. They do not prove that
every charged native transition, output channel or erasure is physically
realized. Strict binary containment establishes the rank geometry needed by
the declared tariff, not native phases, all-column correctness or an all-width
implementation. A frame-valid trace alone does not establish arbitrary-input
scalar or native endpoint equality.

## 3. Complete local histograms

Counting all literal MOVE events and all 562 public helper boundaries gives:

| Rank | Baseline paid | Candidate paid | Baseline helper targets | Candidate helper targets |
|---:|---:|---:|---:|---:|
| 1 | 2231 | 2237 | 14 | 14 |
| 2 | 453 | 453 | 8 | 8 |
| 3 | 494 | 491 | 4 | 4 |
| 4 | 106 | 109 | 107 | 107 |
| 5 | 154 | 151 | 15 | 15 |
| 6 | 8 | 8 | 3 | 3 |
| 7 | 9 | 9 | 9 | 9 |
| 8 | 1 | 1 | 32 | 38 |
| 9 | 0 | 0 | 370 | 364 |
| **Total** | **3456** | **3459** | **562** | **562** |

Both words include the same 25 owned MOVE charges, distributed as
`{1:11, 2:5, 3:2, 4:6, 5:1}`. These charges are inside the table, not added
afterwards. Each word has 43 INIT and 43 CLEAR occurrences; these event counts
do not assert that a physically valid erasure implementation exists.

The baseline event census is ADD13363, SCALE852, MOVE3456, INIT43, CLEAR43,
for 17757 events. The candidate is ADD13371, SCALE852, MOVE3459, INIT43,
CLEAR43, for 17768 events. Event counts by themselves are not a complete
ordinary-work tariff or a funding proof.

### The six endpoint debits and three carrier trips

Write `Z=3` and `Omega=127`. The literal frame generators give
`S_Z={0}`, `d_Omega=9`, frame106=`span{30}` and
frame105=`span{51}`, both of dimension one.

| Carrier | Its old first destination | Entrance F | Lifted helper, old first destination | First MOVE ranks old to new |
|---:|---:|---:|---|---|
| 171 | 412, dimension2 | 106 | 520 to739, dimension3; 655 to1052, dimension5 | helper ranks3,5 to2,4; carrier2 to1+1 |
| 208 | 450, dimension2 | 105 | 544 to748, dimension3; 671 to1048, dimension5 | helper ranks3,5 to2,4; carrier2 to1+1 |
| 130 | 336, dimension2 | 105 | 472 to533, dimension3; 624 to117, dimension5 | helper ranks3,5 to2,4; carrier2 to1+1 |

For each row, `F` is strictly contained in both helper first-destination
spans and the carrier's old first-destination span. The actual candidate
carrier trace replaces `Z -> G_carrier` with the ordered pair
`Z -> F -> G_carrier`. The actual helper first departure begins at `F`.
All remaining MOVE records cancel in the complete old/new MOVE multiset,
while their chronological validity is checked separately.

One cluster changes its paid profile by

`(H_2-H_3) + (H_4-H_5) + (2H_1-H_2)`
`= 2H_1-H_3+H_4-H_5`.

There are three clusters. Thus the local paid difference, candidate minus
baseline, is exactly

`Delta P = 6H_1-3H_3+3H_4-3H_5`.

All six lifted helpers formerly began at `Z` and still end at `Omega`; they
now begin at a one-dimensional `F`. Their six target ranks change from9
to8. Carrier endpoint frames do not change. Hence

`Delta T = 6H_8-6H_9`.

This derives the productive debit from literal endpoints, rather than
retaining six rank-nine credits merely because the helper count is unchanged.
It also retains both legs of all three carrier trips. Response/restore ADDs
do not provide an additional recursive target or cancel either trip charge.
Their arbitrary-input correctness is a separate endpoint question.

## 4. Exact fixed-caller expansion

Let `p_r,t_r` be the local paid and helper-target multiplicities above, and
let `e_r` denote one job/target at rank `r`. Reading the controller events
directly gives nineteen LOCAL stages, sixteen QUERY events, and IDLE stage-set
sizes with multiplicities

`m_2=9, m_3=1, m_4=4, m_7=1, m_8=1`.

The same counts follow from the retained binary forest with root sizes4,7,8:
it has19 leaves and16 internal nodes. Each internal node has one query, one
paired idle and two declared main boundary fields. The two final main fields
have all19 stages. This is an independent finite counting route; it is not an
independent proof of the emitted controller's physical action.

Under the retained interface, a thin query costs104 rank-one jobs, a whole
paired idle on `k` stages costs208 rank-`8k` jobs, and a main field on `k`
stages contributes104 targets of rank`1+8k`. The signs of the two central
powers do not change these declared absolute ranks. Therefore the complete
profiles are exactly

`P = 19 p + 1664 e_1 + 208 sum_k m_k e_(8k)`,

`T = 19 t + 208 e_153 + 208 sum_k m_k e_(1+8k)`.

The factor208 at a node counts both main fields, each with104 ports; it is
not two credits for one field. LOCAL helper credits occur once per actual
stage. The formulas retain every whole idle and query independently of
whether its relative old/new difference vanishes.

### Complete paid profiles

| Rank | Baseline | Candidate |
|---:|---:|---:|
| 1 | 44053 | 44167 |
| 2 | 8607 | 8607 |
| 3 | 9386 | 9329 |
| 4 | 2014 | 2071 |
| 5 | 2926 | 2869 |
| 6 | 152 | 152 |
| 7 | 171 | 171 |
| 8 | 19 | 19 |
| 16 | 1872 | 1872 |
| 24 | 208 | 208 |
| 32 | 832 | 832 |
| 56 | 208 | 208 |
| 64 | 208 | 208 |
| **Total** | **70656** | **70713** |

### Complete productive profiles

| Rank | Baseline | Candidate |
|---:|---:|---:|
| 1 | 266 | 266 |
| 2 | 152 | 152 |
| 3 | 76 | 76 |
| 4 | 2033 | 2033 |
| 5 | 285 | 285 |
| 6 | 57 | 57 |
| 7 | 171 | 171 |
| 8 | 608 | 722 |
| 9 | 7030 | 6916 |
| 17 | 1872 | 1872 |
| 25 | 208 | 208 |
| 33 | 832 | 832 |
| 57 | 208 | 208 |
| 65 | 208 | 208 |
| 153 | 208 | 208 |
| **Total** | **14214** | **14214** |

Both full profiles have target rank mass minus paid rank mass808. That
linear-cost check is a consistency invariant, not a sign proof at a nonlinear
tariff or proof that either complete margin is favorable.

## 5. What a subsequent threshold certificate must certify

For any declared rank tariff `H_r`, define the formal complete margin
`M(H)=sum_r(T_r-P_r)H_r`. The exact matched-profile identity is

`M_new(H)-M_old(H) = 19 g(H)`,

`g(H) = 6(H_8-H_9)-6H_1+3(H_3-H_4+H_5)`.

This identity holds coefficient by coefficient, independently of any
monotonicity or concavity assumption on `H`. In particular it is zero at
linear rank cost. For the power tariff `H_r=r^s`, the later question concerns
the zeros and signs of this **relative gain** on the specified exponent
domain. It is different from the zero of either complete margin as a function
of kappa. No grid, Decimal bisection, approximate sign-switch prose or
author-engine agreement establishes a complete root count.

This checkpoint leaves that whole-domain sign/threshold proof open. The
existing canonical general-rank power-variation tool and prior tariff proofs
are available methods with retained credit, not new general theorems claimed
by this audit.

## 6. Remaining obligations and predecessor credit

The finite formal billing gate does not prove the new lift response maps,
arbitrary-input endpoint identity, native phases/all columns, the physical
fixed-caller contact map, owned erasure, complete ordinary funding,
all-width implementation, compiler or outer admission. It supplies no new
selected frontier, no admitted kappa and no global optimality theorem. The
five retained framework assumptions remain: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`.

DreamingOfClouds with Claude Opus5.5 assistance supplies PR6375 and its
reported read-only row/ownership and sensitivity audit. Ali Romman supplies
PR6372, PR6353, PR6349 and PR6348 with OpenAI Codex assistance;
PR6349 builds on DreamingOfClouds PR6314. Their source words, joint bases,
native input-lift move class, fixed caller, price engines and complete
retained NOTICE chain remain credited. Cinna Davis supplies the productive
controller/thin-query interface; Jacob Alan Sussman supplies productive
recursion; zxv and Cao Yifan supply the interval/compiler line, with the
remaining P104/native/BIT/analytic authors retained in
[sources/NOTICE](sources/NOTICE).

Independent PR6359 already audits PR6353's finite invoice and one fixed-saving
sign. PR6376 audits PR6372's two-anchor scalar boundary/endpoint. Their
evidence is preserved and their conclusions are not silently transferred to
PR6375. General rank-exchange thresholds such as PR5174 and the different
P104 chart-tariff switches in PR5772 are earlier mathematical context.
The new work here is the exact matched-source profile extraction and scoped
accounting proof, by ToikY with substantial OpenAI Codex assistance. Agreement
between two agent implementations is reproducibility evidence, not independent
human or proof-kernel acceptance.

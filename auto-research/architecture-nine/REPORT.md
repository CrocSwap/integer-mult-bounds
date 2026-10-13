# Architecture comparison for a conditional saving above 2^-9

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Research screen, not a new multiplication result.

## Decision

Neither of the two specified proposals earns a construction search. Both
fail an optimistic target budget. We ran **zero construction experiments**;
the small exact matrices below are controls for a general rank identity,
not a new search over candidates. The parked rank-two triple-label search
was not reopened. No selected witness, upstream proof, or release changed.

The useful new diagnostic is that sequential reuse of the two stages'
auxiliary roles, at the specified tensor cuts, loses **two units of rank
deficit per reused role**. It cannot be credited with the cost-free bank
reuse that works at nested boundaries. The cube comparison separately shows
that even a miraculous side compiler cannot rescue its dimension-32
rank-one geometry while retaining the specified two-stage data macros.

These are scoped architectural failures, not barriers for all composition,
all cube constructions, the finite transfer theorem, or multiplication.

## Pinned target and verification boundary

The starting point is the reviewed PR82 snapshot at
`3410b940aa26e5876202152dfa7c4f66451ee22c`, stored with source URLs and hashes
in [the baseline manifest](../kappa-nine/baseline/SOURCE.json). Its reviewed
conditional witness is 5203279888519/10^17; it is not substituted for the
selected release. The selected release remains
25508460085039/500000000000000000.

The existing assembly requires bit saving a>1/511 for kappa>1/512. At
beta=1/20, it also requires complex saving b>20/9709. We screen at the
weaker equality a=1/511: a moment already greater than one excludes a
strictly stronger saving in this model.

Write F(t)=(t/m)^(510/511). A child inventory passes the finite recurrence
test only if sum n_t F(t)<W. Every numerical decision here uses rational
enclosures of 511th roots, checked by integer powers. Decimal values are
display aids. The script replays the pinned profile reconstruction and the
47-row *hypothetical* assembly check; it does not re-audit the upstream
theorem or turn the hypothetical exponents into finite constructions.

## Proposal A: sequentially reuse the two stages' auxiliary banks

**Operation and obligations.** Execute the existing first-axis invocation,
then a second-axis invocation using some of the same physical auxiliary
roles. Each invocation must restore its arbitrary initial auxiliary values.
Consequently the sequential composition can reuse a dirty register without
allocating a clean one. Data outputs must equal the original composition;
no source may be overwritten before its last read. Each surviving physical
role remains an independent input and must meet the complete endpoint
contract. For an auxiliary that is restored, its source-to-sink frame
difference must be I. The scalar reuse itself does not authorize omitting
any frame transition.

**Changed assumption.** The earlier source-floor screen counted separate
source ports for the two invocations. This proposal identifies those ports
across time. It retains internal computations, the data/growth macros and
the following outer cuts. It does not borrow data registers or recode their
values, and does not perform the earlier coordinate-carry construction.

Let P,Q be rank-one rational idempotents on dimensions d_a,d_b. The proposed
first-stage exit and second-stage entrance are

    E = I_a tensor Q,        D = (I_a-P) tensor I_b.

These are the tensor boundaries appearing in the
[two-invocation model](../../docs/research/stage-pair-audit.md). The screen
concerns gluing at **these specified cuts**, not every auxiliary transition
in every later copied-stream implementation. A proposed different physical
cut would require a new inventory and is outside the conclusion.

Separately stored roles have boundary paths E -> I and 0 -> D. Reuse
replaces both by the physical join E -> D. Subdividing the join cannot
improve its rank lower bound. Even a general nonprojector intermediate
matrix must pay at least rank(D-E).

**Exact join identity.** Decompose the two factors into image/kernel of
their idempotents. On their four tensor products, D-E has eigenvalues
-1,0,0,+1, with nonzero multiplicities 1 and (d_a-1)(d_b-1). Thus

    rank(D-E) = m-d_a-d_b+2,       m=d_a*d_b.
    rank(I-E)+rank(D) = 2m-d_a-d_b.
    rank saved = m-2;             role capacity removed = m.

The deficit Wm-s therefore falls by two. This holds for oblique idempotents
as well as orthogonal projections. The intersecting direction P tensor Q
cannot be eliminated by choosing another pairing of rank-one labels on
the two independent factors. This is unlike the previously proved nested
first/third-stage bank reuse, where the full m units can be saved.

**Optimistic target budget.** Normalize by the number N of data pairs and
take d_a=23,d_b=25,m=575. Grant zero fixed central loss, perfect batching
of every retained macro and only one source role per label on each axis.
The unshared lower-bound inventory is

    data/growth: 2*[528] + [1] + 2*[22] + 2*[24],
    auxiliary:  [23] + [552] + [25] + [550],    W/N=4.

Its moment is approximately 1.00007003731157. Sharing a fraction x of the
N possible source-role pairs replaces x*[552]+x*[550] by x*[529], and
changes W/N to 4-x. For the unnormalized feasibility residual H=sum F-W,

    H(x) = H(0) + x*(1+F(529)-F(552)-F(550)).

The exact lower bound for the slope is positive; its value is approximately
0.00346848735174. Hence **every 0<=x<=1 fails**, and sharing worsens this
already favorable budget. At x=1 the normalized moment is approximately
1.00124954553267. Extra unpaired auxiliary roles have coefficients
F(d)+F(m-d)>1. An extra paired role has coefficient
F(23)+F(25)+F(529)>1; even its total rank is 577>575. Adding such roles
cannot repair the feasibility residual. Restoring central costs only hurts.

This is a lower-bound model for the stated retained macros. Fractional x
is a relaxation covering physical integer sharing counts; it is not a
fractional physical implementation. Rank batching is also a favorable
allowance, not a supplied fixed-tape operation.

**Missing lemma and smallest informative test.** Before calculation, the
candidate needed a shared-port join cheap enough to reduce both volume and
recurrence cost. The four-block identity above disproves that requirement
at the specified cuts. Exact rational controls check nonsymmetric labels,
the join ranks, and the contrasting full-capacity saving for nested cuts.
No large circuit or frame search is justified by this proposal.

**Complex counterpart and transfer.** Reusing restored complex auxiliary
registers is also a possible scalar operation, but requires its own phase
frames, signed/weighted gates and physical child list. No complex saving
is credited here. If reuse were viable, new role counts, ordered profiles,
maximum children, gate charges and the finite bridge would all need to be
recomputed. Changing a copied-stream obligation cannot be treated as an
additional free independent register. The bit rejection already stops this
particular route regardless of the complex partner.

## Proposal B: a global cube side program instead of pairwise scratch

**Concrete computation.** Use the binary cube core q=16 from the
[existing core derivation](../../docs/research/cube-core-family.md). Labels
are x in F2^31 with rational vectors

    v_x=(1,(-1)^x_1,...,(-1)^x_31),   dimension d=32.

Its binary central operator C is convolution by delta_0 plus the indicator
of Hamming weight 16. Off-diagonal ones join orthogonal rational lines.
The certified binary factor has size

    n=2^31,       r=2*sum_{i=0}^7 binom(31,i)=7,144,448.

The alternative side topology would compute (I+C)x globally using Boolean
subset transforms and the degree-16 square-zero-algebra convolution, rather
than separate scratch roles for orthogonal pairs. The identity C=Z M Z in
the existing derivation gives an explicit target arithmetic map. It does
not furnish inexpensive rational frames for a recursive implementation.

**Complete obligations.** A side program must be embedded into reversible
linear updates and restore arbitrary side inputs. With central Cx and side
(I+C)x, the transparent invocation must implement y <- y+x over F2 while
leaving x and every auxiliary unchanged. The complete compiler must realize
its declared terminal operation on all roles; the retained two-stage/copying
adapter, if used, must explicitly retain its copied-stream obligations.
Rational endpoint frames and every physical rank transition remain paid.
The proposed global DAG and its frame certificate have not been constructed.

**Changed assumption.** This abandons the triple intersection-one side
graph and its common-point producer topology. It permits a global recursive
side circuit and arbitrary internal rational frames. It retains rank-one
labels and the following optimistic two-stage data/growth macro model;
that retained part alone is enough to reject it. The q=16 core is an old
ingredient, credited above; this is a new target-budget comparison, not a
claim to have discovered a new core or a new circuit.

**Optimistic target budget.** With m=32^2=1024, grant **no auxiliary roles,
no central losses, no side computation costs**, and ideal whole-macro
batching. The remaining data/growth inventory per pair is

    2*[961] + [1] + 4*[31],       W/N=2.

Its exact target moment is greater than one, approximately
1.00005083850934. Each added auxiliary role, even batched into [32]+[992],
has coefficient greater than one relative to its unit volume. Consequently
arbitrary compression within this retained ledger cannot reach a=1/511.
For orientation, retaining a full-dimensional central span for the supplied
factor raises the zero-role moment to 1.00015551142815; retaining one source
role per label on each axis but still erasing central cost gives
1.00016184768867. Neither less favorable number is needed for the rejection.

The rank total of the zero-role inventory is 2047<2048. Thus there is a
positive rank deficit in this *hypothetical* inventory, yet its child-size
distribution cannot support the target exponent. This is why merely scoring
rank deficit would give an incorrect continuation decision.

**Missing lemma and smallest informative test.** A global side program
would need a rational frame realization preserving a useful characteristic
separation after completion. But even perfect success confined to the side
program cannot pass the scoped budget. The smallest informative test is
the three-width exact moment above, so no zeta-network construction search
is launched. A circuit that also changes the data macros or number of
stages is a different proposal and remains unexcluded. We also retain the
existing warning that an exact characteristic-zero realization of the full
all-role permutation would reject the original rational-frame contract;
absence of such a realization is not proved for a new global side program.

**Complex counterpart and transfer.** This core supplies no competitive
complex companion. Direct reduction of all signed vectors modulo two gives
the same all-ones vector, with self-pairing 32=0, so it does not supply the
existing nondegenerate phase labels. A different phase geometry or separate
complex network with b>20/9709 is required. A new topology would also need
its ordered child profiles, scalar charge, reservations, recurrence and
finite bridge audited. The existing hypothetical assembly check does not
waive any of these requirements.

## What would earn another experiment

Neither proposal merits an immediate extension. Do not repeat bank-pairing
searches at E,D or optimize the cube's side program for this target while
retaining its data macros. Neither do these failures justify reopening the
parked rank-two triple-label search.

The missing ingredient for composition is a concrete operation that changes
the outer cuts or eliminates an internal/data operation *along with* storage,
so the two-unit penalty and existing macro floor no longer apply. For a new
topology, it is a complete computation with a different data-stage profile,
or a better characteristic-dependent geometry with a quantitatively viable
profile and a complex companion. A proposed scalar identity alone is not
enough. We recommend no next construction experiment until one of those
ingredients is specified. This is a stopping decision for the two proposals,
not a claim that a route to 2^-9 is impossible.

## Reproduction and completion audit

```sh
python3 research/architecture-nine/audit.py --output /tmp/architecture-nine.json
python3 -m unittest discover -s research/architecture-nine -p 'test_*.py' -v
```

[The certificate](certificate.json) records exact intervals, input hashes,
the baseline pin, and matrix controls. [Validation](validation.json) records
reproduction, focused tests and preservation checks.

Goal requirements: one explicit proposal per direction; complete obligations
and changed assumptions; scoped optimistic budgets; missing lemma and minimal
test; complex/transfer obligations; exact rejection before construction;
zero of at most two construction experiments; reproducible artifacts and
decision; no new bound, merge, push or publication. All are covered above.

# Exact partial width-seven packing for the PR589 bit slot model

**Research result about a hosting relaxation; no new κ or physical supplier.**
For each `k=0,...,74` converted helpers per call and every real
`0<a<=1/100`, this package gives an optimal idle profile in the exact mixed
width-seven/width-eight slot model of Sagar Thakrar's [PR1023](https://github.com/CrocSwap/integer-mult-bounds/pull/1023).
The replica-local optimum improves **45 of the 74 positive partial placements**.
The same certificate also proves the **32-replica pooled relaxation optimum**,
which improves **60 of 74** compared with repeating the local optimum. PR1023 explicitly presented those partial placements as constructive,
not optimal; its claims are not contradicted.

The new result is the uniform, finite-capacity optimality certificate and the
correct treatment of partially unused slots. The current selected bit supplier
is still DreamingOfClouds' PR589 on eumemic's PR555; the selected complex-bound
κ remains `0.001672660197076918`. No selected record is modified.

## Replica-local model and result

One replica contains 666 slots of capacity 7 and 444 each of capacities 14,
28 and 42. The total capacity is 41,958. There are nine calls per replica,
with `9k` indivisible width-seven roles and `9(439-k)` indivisible width-eight
roles. Slots may contain any mixture that fits. There are no extra banks,
role splitting, capacity changes, temporal constraints or helper identities.
Each nonempty remainder is billed as one idle child.

Put `S=45+9k=5q+t`, with `0<=t<5`. An optimum places every width-seven role
alone in a capacity-seven slot, leaves `q` capacity-42 slots empty, and uses
the following single additional partial slot when `t>0`:

| Slack residue t | Partial slot capacity | Width-eight roles in it | Idle rank | PR1023's idle rank and capacity |
|---:|---:|---:|---:|---:|
| 0 | none | — | — | none |
| 1 | 14 | 0 | 14 | 10 in capacity 42 |
| 2 | 28 | 1 | 20 | 18 in capacity 42 |
| 3 | 28 | 0 | 28 | 26 in capacity 42 |
| 4 | 42 | 1 | 34 | 34 in capacity 42 |

All other slots contain as many width-eight roles as fit. The remaining
capacity-seven slots stay empty. The 75 complete integer placements and
histograms are in `EXPECTED.json`; each is checked against all slot and role
counts. At most 143 capacity-42 slots are affected, within the 444 available.

The strict improvement occurs exactly when `k mod 5` is 2, 3 or 4. In particular,
the published `k=1` and `k=10` placements are already optimal; `k=37` and `k=74`
are improved. This does not claim uniqueness of the physical assignments.

For the **pooled 32-replica relaxation**, multiply all capacities and role
counts by 32 and replace `S` by `32(45+9k)` before taking its quotient and
remainder modulo five. Use the same single-partial-slot table, now across the
whole pool. No per-replica inventory constraint is imposed in this relaxation.
Its optimum is strictly cheaper than 32 repetitions of the replica-local
optimum exactly when `k` is not divisible by five: **60 cases**. This additional
concentration is not an admitted cross-replica owner map. Both relaxation
models and all 150 attaining placements are retained separately.

## Proof

Write `g_a(r)=r(64/r)^a` for `r>0` and `g_a(0)=0`.
For `0<a<1`, this is increasing, strictly concave and subadditive.
The inherited bad-residue surcharge can be included by billing
`g_a(r)+lambda_a*1[r>0]` per idle slot, where
`lambda_a=32*64^2*64^a/10^16>0`. The common positive normalization is `64W`.
Any fixed local child profile contributes the same amount to every placement.

**1. Move the width-seven roles.** Since `9k<=666`, if any width-seven role
lies outside a capacity-seven slot, an empty capacity-seven slot exists.
Move that role there. If its old slot had idle rank `r`, the two affected
remainders change from `(r,7)` to `(r+7,0)`. Subadditivity implies
`g_a(r+7)<=g_a(r)+g_a(7)`. The number of positive remainders cannot increase.
Repeatedly applying this move proves that an optimum exists with all
width-seven roles in capacity-seven slots. This is a mathematical move in
the declared relaxation, not a legal chronological owner-map operation.

**2. Reduce the width-eight problem.** With all other slots maximally filled,
the minimal remainders are 6, 4 and 2 in capacities 14, 28 and 42. A slot of
capacity `c` can leave `u=1,...,floor(c/8)` width-eight places unused, at
incremental cost

`d(c,u)=g_a(c mod 8+8u)-g_a(c mod 8)`.

There are nine possible moves. Exactly `S=45+9k` unused places are needed.
All these slots retain positive remainders, so the surcharge is constant:
there are exactly `1998-9k` positive idle children after step 1.

Temporarily remove the limits on the number of slots of each capacity.
Let `V(S)` be the least incremental cost in that unbounded relaxation.
Define `A=g_a(42)-g_a(2)` and

`B=(0, g_a(14)-g_a(6), g_a(20)-g_a(4), g_a(28)-g_a(4), g_a(34)-g_a(2))`.

The proposed value is `V*(S)=floor(S/5)*A+B[S mod 5]`. It is attained by the
explicit moves in the table. It also satisfies every Bellman lower-bound
inequality `V*(S)<=V*(S-u)+d(c,u)`.
It suffices to check `S=5,...,9`: simultaneous translation of `S` and `S-u`
by five adds `A` to both sides. Every valid small `S` inequality has the same
coefficients as one of these representatives. There are 45 comparisons:
nine exact identities and 36 strict inequalities, with 30 distinct signed
coefficient vectors. Induction from `V*(0)=0` proves `V*=V` for every
nonnegative integer `S` in the unbounded relaxation.

**3. Certify the analytic inequalities uniformly.** Each strict difference
has the form `f(a)=sum_r c_r*r*exp(a*L_r)`, where `L_r=log(64/r)` and
`sum_r c_r*r=0`. For `0<a<=A0=1/100`, Taylor's theorem gives

`f(a)/a >= sum_r c_r*r*L_r - (A0/2)*sum_r |c_r|*r*L_r^2*exp(A0*L_r)`.

The pinned exact rational log/exponential engine bounds every term outward.
All 30 resulting lower bounds are positive; the smallest exceeds **1.009**.
The full rational bounds and coefficients are retained. The expression is
an analytic certificate on an interval, not a numerical grid search.

**4. Return to finite capacities.** For `0<=k<=74`, the displayed optimum
uses at most 143 of the 444 capacity-42 slots and at most one special 14- or
28-slot. Every constructed placement has exactly the prescribed width-seven
and width-eight counts. Therefore the lower bound from the unbounded
relaxation is attained in the original finite model. The pooled case has
exactly 32 times as many bins and roles; its `q=floor(32S/5)` empty 42-slots
and at most one partial slot also fit. The same proof and all 45 analytic
comparisons apply without alteration. Each of the 75 pooled placements is
checked against its scaled inventory and capacity, and all 60 strict
pooling improvements are certified by the same uniform Taylor bound.

## Conditional prices, including the surcharge

The following are **bit primitive endpoints for hypothetical profiles**.
They inherit PR1023's assumption that converting each helper removes exactly
one rank unit from one distinct local child, with no additional adapter work.
“Optimistic” removes rank-one children; “pessimistic” trims the largest
available distinct children. They are not bounds for an arbitrary unimplemented
width-seven mechanism.

| k and local assumption | Prior replica-local | Optimal replica-local | Optimal pooled32 |
|---|---:|---:|---:|
| 1, optimistic | 0.001734846264120199 | 0.001734846264120199 | 0.001734900431583947 |
| 2, optimistic | 0.001736285595407293 | 0.001736327170598943 | 0.001736378166034284 |
| 2, pessimistic | 0.001735799419401112 | 0.001735840971303414 | 0.001735891938199934 |
| 37, optimistic | 0.001789627464386639 | 0.001789671631346367 | 0.001789725802593009 |
| 37, pessimistic | 0.001780512649923341 | 0.001780556367920637 | 0.001780609989052612 |
| 74, optimistic | 0.001849705707539871 | 0.001849754238370428 | 0.001849803954130003 |
| 74, pessimistic | 0.001831202097168173 | 0.001831249661111874 | 0.001831298387323686 |

Displayed decimals are rounded; exact rationals and strict adjacent
`10^-24`-grid brackets are in `EXPECTED.json`. Both retained independent
moment engines certify every priced endpoint with the inherited bad-residue
surcharge and reject the next grid point. The complete rank mass remains
`64*28416-10272=1808352`. Source access, helper construction, restoration,
frame transitions and recursive adapters beyond the hypothetical local
one-unit change are **not supplied** and must be priced by a future caller.

## Reproduce and failure controls

Standard-library Python 3.12, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/bit-partial-width7-optimum
```

Expected markers include `PASS_BIT_PARTIAL_WIDTH7_OPTIMUM`,
`PASS_BIT_PARTIAL_WIDTH7_PACKAGE` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Direct commands are `python3 -I -B research/bit-partial-width7-optimum/verify.py`
and `python3 -I -B research/bit-partial-width7-optimum/test_package.py`.
Verification does not regenerate or overwrite evidence. An explicit
`verify.py --write NEW_FILE` reproduces the canonical certificate.

The primary verifier checks all 45 analytic comparisons, all finite slack
states through 711 and the 75 pooled slack states, all 150 placements, both
moment engines for nine priced scenarios (replica-local, pooled and relevant
predecessor profiles), and six negative controls.
A separately implemented original-bin dynamic program enumerates mixed
width-seven/width-eight fills in three bins of each capacity. It compares
60 complete cases at `a=1/1000` using outward rational bounds from the second
engine, without importing the production policy, reduction or Bellman code.
This finite cross-check supports the implementation; the written argument
and uniform certificate establish the declared theorem.

Controls reject a dropped helper, an extra slot, the unsupported `k=75`,
negative slack, a false linear-mass cancellation, and a false optimality
claim for the predecessor's partial-42 policy. Every price rejects its
next grid point. A minimal relocated, isolated optimized replay passes;
real on-disk source corruption, evidence corruption and missing evidence
are rejected. Package metadata and selected-record integrity checks are
recorded separately in the handoff.

## Scope, overlap and attribution

Base: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; OS-random assignment seed **3**,
bit-supplier track. Three candidates and the initial one-helper refinement
are retained in `CLAIM.json`. The same method was then extended through
`k=74` after it exposed the nonoptimal remainder cases, and to the pooled
32-replica model to distinguish local from global relaxation optimality. This is a declared
side result relative to the catalogue's H2/K-interface card, not a new
helper mechanism. Search is complete in the stated finite slot domain;
no heuristic optimizer or random search is used.

The live semantic overlap check initially covered 859 open PR bodies and 24 discussion
records; the 21:37 UTC refresh covered 868 open PRs and 30 discussions, plus local package notes and the review ledger. This is bounded
novelty evidence. PR1128/1256 and the concurrent later-boundary census study
physical width-seven obstructions; PR1179/1253 study kernel entrances.
This package changes none of their words or premises and does not add their
savings. Our claim is [discussion1269](https://github.com/CrocSwap/integer-mult-bounds/discussions/1269).

Credit Sagar Thakrar / PR1023 for the slot reconstruction, pure-width-eight
optimum, all-width-seven endpoint, partial placements and pricing brackets;
DreamingOfClouds for PR589 and the PR510/463 template; eumemic for PR555;
DaysSky for idle-axis hosting; Jeremy Kothe and Dominik Scholz for the earlier
complex width-seven mechanisms; and the retained exact-moment engine authors.
The accepted Rohan Arun / Jeremy Kothe complex construction is unchanged.
Exact Git blob/SHA256 pins are in `SOURCES.json`. Prepared for **Philipp /
mightyOil**, with substantial **OpenAI Codex GPT-6 Astra** assistance in
proof, implementation and checking. Apache-2.0. No independent human review
or formal proof of the full multiplication theorem is claimed.

## Open next questions

1. **Can the optimal relaxed assignment be hosted chronologically for one
   actual width-seven bit helper?** This determines whether any price is
   usable. Start with PR1179's explicitly changed entry/exit contract and
   audit its owners, windows, source accesses and restoration. The physical
   width-seven provider and its interface admission are blockers; the slot
   calculation supplies neither.
2. **What is the optimum after the 666 capacity-seven slots are exhausted?**
   This would price `k>=75`. First enumerate the mixed-width patterns after
   fixing the width-seven roles which must stay in larger slots, then look
   for an integer dual or a bounded DP. The move-to-seven reduction is no
   longer sufficient, so the present certificate must not be extrapolated.

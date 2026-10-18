# Coupled gauges escape PR1263's coordinate minimum

**Finite scalar construction and scoped all-integer local optimum; no new κ.**
The second open question of [PR1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263)
asks whether a coupled move improves its coordinate-stationary 237-helper gauge.
Exactly two pairs do. Two best-pair descent steps save six further primitives
per complex invocation, then no change to any one or two eligible helpers can
improve the complete scalar price, for arbitrary integer dyadic exponents.
This is not a global optimum over the 237-dimensional integer lattice.

| Complete scalar price | Forward | Backward |
|---|---:|---:|
| Selected-at-base PR1094 word | 149,002 | 149,018 |
| PR1263 simultaneous gauge | 136,002 | 136,018 |
| This finite candidate | 135,996 | 136,012 |
| Total saving from original | 13,006 | 13,006 |

The small extra saving is not the principal result: the exact all-pair certificate
resolves the predecessor's open local-search question and demonstrates why
single-coordinate stationarity was correctly distinguished from optimality.
The paid recursive profile and every nonscalar event are unchanged; no kappa,
native/hosted admission, practical speedup or full multiplication proof follows.

## Exact moves and price

The eligibility contract is inherited from Hanson Sun / @bbMisk's
[PR1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214): 237 cold-entry,
FULL-exit, unwrapped, non-center helpers with no incident COPY or clear. Their
constant gauges are uniform scalar multiplications of the complete registers.
For each original ADD `t += q*s`, the coefficient becomes `q*2^(k_t-k_s)`.
Every original SCALE, frame, source access and instruction order remains.
Entry `2^k_h` and exit `2^-k_h` scales restore arbitrary helper dirt.
The conjugation/telescoping proof is inherited from @woklerx's PR1161 and PR1263;
full 712-column scalar endpoints are rechecked here for both new words.

The forward incremental moves from the frozen PR1263 vector are:

| Pair | Increment to both exponents | Separate single deltas | Shared-edge correction | Net real delta |
|---|---:|---:|---:|---:|
| L400, L409 | −1 | +2 | −4 | −2 |
| L482, L494 | +1 | +5 | −6 | −1 |

Backward increments have the opposite signs and the same prices. Shared ADDs
are charged once. The final vector has 216 nonzero gauges; the 432 added scale
macros cost **630 real / 1,260 complex primitives**, exactly as much boundary
work as PR1263. The complete price includes coefficient-work initialization and
clearing under Sagar Thakrar's PR696 copy-init lowerer. Source/target registers,
private centers, helper dirt and coefficient-work dirt are included in the
literal endpoint checks. Positive local primitive-prefix bounds remain 52/68
bits, denominator depths 24/26, within the inherited local 192-bit allowance.
These are local checks, not a revised global precision invoice.

## Why the finite pair census covers all integer exponents

For a dyadic coefficient `|q|=p*2^e`, p positive odd, write
`f_p(z)=|z|-[p=1 and z=0]`. This is the variable part of the literal lowerer's
ADD price. The full real-component gauge-dependent cost, up to a fixed constant,
is

```
F(k) = 2 Σ_h |k_h| + Σ_ADD f_p(e+k_target-k_source).
```

The first sum includes every entry/exit scale. Original SCALEs and all other
costs are constant. The unit discount is essential; replacing it with plain
absolute value changes the problem. This is not a convexity argument.

Fix the complete current vector and two helpers a,b. Let x,y be incremental
integer changes, and let E be each ADD's valuation after the current gauges.
The slope-change/discount lines are:

- `x=-k_a`, `y=-k_b` from the boundary scales;
- `x=-sE` or `y=-sE` for ADDs with exactly one of a,b as an operand;
- `x-y=-sE` for their shared ADDs, s=+1 if a is target and −1 otherwise.

Between these lines the objective is affine. On each open line segment, every
already-active unit discount is constant and the objective is affine as well.
Moving to its boundary can only introduce further **negative** unit discounts.
The boundary price makes the full function coercive: every ADD has a finite
lower bound and `2|k_a+x|+2|k_b+y|` grows at infinity. Thus a minimum on any
face can be moved to a lower-dimensional boundary without increasing its cost;
no decreasing infinite ray is possible. Iterating reaches a vertex. All vertices
are integral, being intersections of vertical/horizontal or diagonal lines.
A minimum over all real pairs, hence over integer pairs, is attained at a vertex.
This is the PR1214 arrangement argument extended to an arbitrary fixed nonzero
gauge, including its shifted boundary costs.

The executable census tests every such vertex for all **27,966 pairs** in each
orientation. Pairs without shared ADDs separate. The first census has exactly
the two improving pairs above; after the first move only the second improves;
the final census has minimum delta zero for every pair. Per orientation the
three censuses examine **850,739; 852,025; 850,728 vertices**. Complete row-stream
and pair-minimum hashes bind every pair, not merely the winning examples.
Deterministic descent takes the lexicographically selected global best pair;
the 25-step cap is not reached (two strict steps, then stationarity).

`independent.py` does not call that arrangement census or `f_p`. It prices
actual lowerer outputs and exhaustively enumerates the integer square
**[-31,31]²** for all 2,414 interacting pairs, using independent one-dimensional
minima for the other 25,552 pairs. Its radius formula
`max|k| + 2 max|E| + 1` contains every listed type of arrangement vertex,
so the written face argument extends these grid minima to the entire lattice.
The two orientations use **25,601,436 integer evaluations** in total and agree
on every final pair minimum. A separate set of 80 tiny random signed/odd-dyadic
instances checks the arrangement algorithm against brute-force squares.
Both implementations are AI-assisted; this is not independent human review.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/k8-coupled-gauge-stationarity
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/k8-coupled-gauge-stationarity outcome=completed`.
The seven test groups recompute both complete three-census receipts, all formal
endpoints, the independent grid/primitive receipt, synthetic exhaustive cases,
and controls that reject omitted entry/exit scales, an inverted entry scale,
a changed ADD coefficient, a corrupted certificate and changed source bytes.
Execution under isolated optimized Python retains all checks.
The deterministic certificate may be regenerated with `verify.py --write` only
when its output does not already exist. The registered check never overwrites it.

Base: **bce54fb3f895cbe5cd4c0eb477c3afeed100190f**. The actual selected certificate,
review, reconstruction archive and provider were followed; accepted conditional
κ at this base is 0.001672660197076918. `SOURCES.json` binds all transitive input
files, and `PREDECESSORS.json` authenticates byte-identical used predecessor
sources. `CERTIFICATE.json` stores the full final gauge and exact local invoice;
`INDEPENDENT.json` stores the separate literal/grid check.
No upstream, selected-frontier or frozen predecessor files are modified.

## Selection, overlap and credit

OS seed **35** assigns complex-supplier work. Seed modulo three selects the
third narrow candidate: phase-varying gauges already overlap PR1259/1270;
X54 donor kernels overlap discussion1251 and PR1297; coupled moves around
PR1263 resolve its explicitly open question. The initial live scan covered
794 open PR bodies and 22 discussions, all local sprint claims, the ledger
and relevant negative results. The claim is a follow-up in
[discussion1258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1258#discussioncomment-18910213).
No pinned coordination issue existed. This is an explicitly labelled scalar
side result, not completion of the current repository inventory task card.

Credit **Hanson Sun / @bbMisk**, PR1214 head
`26162c56ec9c50a80e49949f36d4dd9a137a76a6`, for the exact pair-arrangement method,
which is adapted here, and the original eligibility contract. PR1214 studies
at most two nonzero gauges **from zero**; this package fixes a simultaneous
237-helper vector and varies any two entries. Credit **Philipp / @mightyOil**,
PR1263 head `5fbaca13028846bddbb001e8e07addc2ab8e5816`, for the many-helper
construction and explicit follow-up. Its source loader, transformation,
all-column replay, invoice and primitive utilities are reused, not described
as independently reimplemented. Byte-identical sources and notices are retained.
Credit **@woklerx** PR1161, **Sagar Thakrar** PR696 and PR1259, icekylinx,
Jeremy Kothe, Rohan Arun, Hao Yan, Douglas Colkitt and the retained supplier
lineage. No composition with PR1170 scale merging or PR1259/1270 varying gauges.

Prepared for **Philipp (@mightyOil)** with substantial **OpenAI Codex / GPT-6
Astra** assistance in mathematics, implementation, verification and writing.
New material is Apache-2.0; inherited notices remain. No mechanism/literature
priority claim. Finite checks and the written arrangement proof do not discharge
all-size/compiler, realization, whole-call hosting, precision/tape, analytic or
bit-interface assumptions. Native C++, controller/global admission, selected
cold replay, Lean and independent human review are outside this package.

## Open next questions

1. Admit the exact final gauge through the pinned native k8 emitter and full
   hosted/controller invoice. Start by carrying all 432 added scale macros
   into that emitter. No new native artifact is supplied here; this is the
   blocker between the scalar candidate and accepted supplier integration.
2. Test coupled changes on at least three helpers. Start with connected triples
   in the 2,414-edge interaction graph, charge shared edges once and all boundary
   work. No triple census or global certificate is supplied; pair stationarity
   does not justify a global lower bound. Structured questions are in `TASK.json`.

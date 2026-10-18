# Four-unit signed connector: the root ports are forced

**Scoped negative result and exact finite census; no new kappa.**
For the fixed signed 3x3 connector, twelve ordinary signed child queries and
four unit transfers in the named direction `z += +/-w` force one root-port
assignment:

| Operator | B0 | B1 | B2 | A0 | A1 | A2 |
|---|---|---|---|---|---|---|
| Root | w | w | z | z | z | w |

Here `B_j` writes `B_j x_j` into its root; `A_i` reads its root into `y_i`.
Both roots, all outputs and all private workspace start arbitrary-dirty. The
required map is `y_i += sum_j M_ij A_i B_j x_j`, where
`M=[[1,1,1],[1,1,-1],[1,-1,0]]`; sources and roots restore.

Ross Richardson's [PR1651](https://github.com/CrocSwap/integer-mult-bounds/pull/1651)
already attains this assignment. This contribution proves that rearranging its
four-unit-transfer class cannot move an expensive operator to the other port.
The earlier search stopped at the first four-transfer witness. We add a short
structural port-rigidity argument and complete coverage of all 64 port masks.
The transfer-count minimum and twelve-query construction are predecessor work.

## Evidence and reproducible command

From the repository root, Python 3.12 plus a C++17 compiler named `c++` suffice;
there are no Python package dependencies and no network access is required:

```sh
python3.12 scripts/research_package.py --package research/signed-connector-port-frontier
```

Expected final markers:

```
PASS_SIGNED_CONNECTOR_PORT_RIGIDITY traces=7257600 restored=3343680 feasible=80 sole_mask=35 symbolic_controls=38 dense_controls=39 no_new_kappa
PASS_PORT_PACKAGE_CONTROLS corruptions=7 readonly_full_replay=true optimized=true
PASS_REGISTERED_RESEARCH_PACKAGE research/signed-connector-port-frontier outcome=negative-result
```

The portable direct command `python3 -I -O -B research/signed-connector-port-frontier/verify.py`
works from an exported package without Git history. The registered launcher
additionally checks historical base/catalogue provenance and runs corruption
and read-only relocation tests. It needs the repository's Git history.
The verifier builds both programs in a temporary directory and compares every
receipt field; it never rewrites a certificate. Local C++ compilation is paid
verification work, not part of the mathematical supplier cost.

[PROOF.md](PROOF.md) proves the two-call pair/port reduction and the structural
singleton argument, using PR944's freshly replayed 720-path obstruction. The
exhaustive source-trace domain is
`8 * 720 * 210 * 6 = 7,257,600`: source pair ports, signed source orders,
shear positions, and balanced shear sign orders. Exactly 3,343,680 restore the
roots and 80 admit all three reader rows; every one admits mask 35. The count
80 concerns source/shear traces, **not** all reader insertions or full words.

The primary implementation executes chronological integer coefficient states.
A separate subagent's implementation computes coefficients from source interval
endpoints and shear-prefix sums, without reading or importing the primary
implementation. Both exhaust the full domain, with no modular arithmetic or
sampling. Six additional complete endpoint censuses check target permutations,
a column sign, the zero entry, an all-ones target, and deliberately omitted dirty
cancellation. That last invalid relaxation admits 11,488 traces and seven masks,
showing why dirty-root equality cannot be omitted. All-ones admits 15 masks.

The literal certificate passes free noncommutative replay, its inverse, a
transpose/reverse/root-swap control, and 38 sign/removal/port mutations. An
independent balanced lowerer and integer-matrix oracle check four noncommuting
fixtures in dimensions 2 and 3 on all 110 independent dirty input columns,
including inverse restoration and 39 additional mutations. Seven actual file
corruptions fail; a relocated read-only optimized replay passes.
These are independently implemented AI checks, not independent human review,
a proof-assistant proof, or a formal proof of the multiplication theorem.

## Complete costs and limitations

For complete fixed signed-query prices, set
`q_F,r = c_F,r,+ + c_F,r,-`. The exact additive bill throughout this class is

```
I + P + D + q_B0,w + q_B1,w + q_B2,z
          + q_A0,z + q_A1,z + q_A2,w + 2t_+ + 2t_-.
```

Every child price includes source/coefficient access, full-row arithmetic,
frames/routing, private restoration, head return and dispatch. `I,P,D` pay
remaining admission, preparation and control and must be common to the compared
words. State- or chronology-dependent overhead needs separate pricing.
The forced surcharge over independent cheapest-port choices is
`sum_F max(0,q_F,forced-q_F,other)`. With every pair priced 20 at z and 200 at w,
and transfer prices 1, the actual bill excluding `I,P,D` is 664, not the
unattainable all-z relaxation 124. A longer one-root repair can be cheaper;
there is no optimum claim across different query counts.

The inherited balanced product lowering pays
`C(F)=2C(left)+2C(right)+dispatch`, with one restored private row per level;
for sign-asymmetric costs price the four literal invocations separately.
The B lengths 2,3,4 and A lengths 5,6,7 fixture expands to 300 factor calls,
four root passes and three private child rows in addition to the two roots.
It reserves eleven mutable rows and 27 supplied factor matrices. No hidden
row initialization, copy, restoration, frame change or recursive child is free.

For the exact dense integer layout in the credited
[PR1651 cost specification](sources/PR1651-COST.md), the new literal witness
has the **same** operation invoice and head movement
`9636L^4+2044L^3+8L^2+5560L-608`. Literal traces at L=1,2,3 check the polynomial.
Coefficient reads/multiplications are `300L^2`; source reads, target updates,
additions and work clears are `300L^2+4L`. Admission scans `11L+27L^2` cells,
program loading, control, scalar cleanup, factor preparation and bit tariffs
remain paid. For initial entries bounded by X and factor entries by H, a
conservative magnitude bound is `X*2^4*(1+LH)^300`, with sufficient signed
integer and product width. The bound is deliberately loose; approximate
complex precision is not established. These are model counts, not timings.

The exact negative result fixes the target, named direction, unit coefficients,
signed ordinary queries, two roots and no output feedback. Choosing the
opposite global direction swaps the root names and gives complementary mask
28; it is outside the named-direction census. Nonunit/bidirectional shears,
extra queries, extra roots, mutable sources and specialized operator identities
are not excluded. Native selected-supplier realization, whole-call hosting,
precision/tape and analytic assembly remain open or inherited. No improvement
to the paid recursive profile, selected supplier or kappa is claimed.

## Pins, overlap and attribution

Base: `418e40eb2572d930b58c1cf9b82b41c0fc7ee08d`; OS assignment seed **31**.
At that base the selected PR1094 conditional kappa is
`836330098538459/500000000000000000`, with complex binding. The selected source
record was followed to its PR1094 assembly, actual T16 exchange construction,
source inventory and maintainer review. It is unchanged by this package.
[SOURCES.json](SOURCES.json) pins the base, historical catalogue and predecessor
bytes; [CLAIM.md](CLAIM.md) records the local claim and three candidate tasks.
The explicit user track takes precedence over the broader catalogue card;
[TASK.json](TASK.json) declares the changed scope as a side result.

The initial fresh overlap snapshot covered 461 open PRs and 326 discussion
records with complete pagination and no warnings. [OVERLAP.json](OVERLAP.json)
retains scope and leads; [VALIDATION.md](VALIDATION.md) records final refresh.
Cinna Davis's [PR1675](https://github.com/CrocSwap/integer-mult-bounds/pull/1675)
extends the short-transfer lower bound to both directions and explicitly leaves
four-pass schedule pricing open. It is credited and is not a proof dependency.

Prepared for **Ross Richardson with substantial OpenAI Codex assistance**,
including three scoped subagents. New work is Apache-2.0. Credit Ross Richardson
(PR944 target/one-root obstruction; PR1651 attaining four-pass word), Charles
Bethin (PR1637 two-root twelve-query construction and cost fixture), martinxxx9
(PR1088 weighted one-root repairs), and the retained predecessors named in
[NOTICE.md](NOTICE.md). No selected record, frozen predecessor or `upstream/`
file is modified.

## Open next questions

[TASK.json](TASK.json) records two concrete follow-ups: classify nonunit
four-shear height patterns before any new coefficient search, and obtain actual
native port prices to compare the forced four-transfer bill against the
credited fourteen-query one-root repairs. The first needs a new exact reduction;
the second is blocked by native frame/hosting and full precision/tape pricing.
Neither is needed for the completed unit-shear port-rigidity result.

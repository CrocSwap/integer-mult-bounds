# How many late block interfaces must change to reach the planning target?

Under the retained width-73 coverage model, **a uniform replacement word must
escape at least eight of the selected word's twelve late block interfaces
before the optimistic complex-side screen opens at `a=1/99`**. Retaining any
five excludes that target, even if we grant every other unit of paid mass
a rank-51 child and discard additional costs.

We combine Ali Romman's [PR1429 block theorem](../complex-block-rank-optimum/PROOF.md)
with Douglas Colkitt's [PR1240 cost relaxation](../complex-local-word-ceiling/README.md).
We add the target consequence, exact interface-count boundary and an independent
integer-root check. We propose no new supplier or kappa and report no defect
in either predecessor.

## Model and exact result

We keep width `m=73`, `w=896/9` live families per complete call, one unpaid
coordinate per family, eight rank-8 centre copies per call, and the halving
guard `73^2 > 2r^2` on every other child. Hence `r<=51`. We assume the retained
coverage identity for the redesigned core:

`total paid rank mass per call = 72w + 64 = 7232`.

Any copy, adapter, restoration or other work outside that identity adds to
the bill. A researcher cannot deduct its mass from the old idle remainder
without proving a new coverage identity.

The pinned selected certificate contains seven blocks with common frame
dimension four and five with common dimension five. PR1429 proves the following
complete helper costs for every finite program in each retained interface,
where `s=1-a`:

| Type | Unavoidable unnormalized moment | Fixed rank mass |
|---|---|---:|
| `u=4` | `24 + 8*2^s + 4*3^s` | 52 |
| `u=5` | `32 + 4*4^s` | 48 |

With all twelve interfaces retained, their minimum profile is
`{1:328, 2:56, 3:28, 4:20}`, of mass 604. The centres add mass 64.
We assign the remaining 6,564 units to fractional rank-51 children, including
the other local paths. This grants more freedom than idle repacking of the
unchanged word.

At `a=1/99`, we obtain these outward rational intervals. The displayed decimals
are exact decimal-grid endpoints, rather than floating-point tests:

| Retained block interfaces | Optimistic normalized moment | Decision |
|---|---|---|
| All seven type-4 and five type-5 | `[1.001859955557, 1.001859955558]` | Excluded |
| Cheapest five: five type-5 | `[1.000068880070, 1.000068880071]` | Excluded |
| Dearest four: four type-4 | `[0.999909410227, 0.999909410228]` | Relaxation open |

For all twelve, the inherited rational engine also brackets the ceiling in
`[0.007340317424863, 0.007340317424864]`. Under the retained balanced transfer,
the corresponding conditional kappa cap is
`229384919527/31479384919527`, approximately `0.00728683`. This is a bound on
the declared redesign class, not an attained exponent or a change to the
selected result. The bit side would still need its own improvement.

## Proof of the target screen

For each retained helper, sum its monotone frame increments. Starting at rank
`d` and ending at rank nine costs exactly `9-d` units of rank mass, regardless
of splitting, scalar gate count or order. Four helpers start at rank one and
four at rank `u`, so each block has fixed mass

`4(9-1) + 4(9-u) = 68-4u`.

This telescoping step matters: a moment lower bound with unknown mass would
not justify subtracting its mass before pricing the remainder.

Put `c_r(a)=(r/73)^(1-a)`. For `a>0`, the cost per unit mass
`c_r(a)/r = 73^(a-1) r^(-a)` decreases with `r`. Thus replacing all residual
mass by rank-51 children can only lower its cost. Fractional child counts
also enlarge the allowed set.

For retained counts `i` and `j`, define

`L(i,j) = {8:8} + i*{1:24,2:8,3:4} + j*{1:32,4:4}`.

The complete normalized moment is at least

`F(i,j,a) = [sum_r L(i,j)[r]*c_r(a)
             + (7232-mass(L(i,j)))*c_51(a)/51] / w`.

The block theorem supplies its pointwise minimum with the same fixed mass,
so these substitutions can be made together. We omit other nonnegative
charges. The conclusion therefore remains valid when a caller adds them.

At `a=1/99`, let `b4=F(1,0,a)-F(0,0,a)` and
`b5=F(0,1,a)-F(0,0,a)`. Both exact interval engines certify
`b4 > b5 > 0`. The cheapest five retained blocks are therefore five type-5
blocks, while the dearest four are four type-4 blocks. The two strict
inequalities in the table prove the count boundary. We also check all
48 pairs `0<=i<=7`, `0<=j<=5`: 33 exclude the target and 15 leave this
relaxation open.

Every child has rank below 73, so its cost increases with `a`. Exclusion at
`1/99` excludes larger primitive savings. Under `kappa<a/(1+a)`, a target
`kappa>0.01` requires `a>1/99`. A positive relaxed margin supplies no
construction, physical owner map or sufficient adoption criterion.

We state the integer eight-interface consequence for a common replacement
provider used on each call. With heterogeneous providers, use the weighted
average of their affine bills; the integer claim does not force every call
in a heterogeneous schedule to change eight interfaces.

## A small extra charge can erase the remaining margin

For the dearest-four case, one extra rank-one recursive call outside the
coverage identity raises the moment into
`[1.000053102390, 1.000053102391]`, so it excludes the target.
If an implementer instead inserts that call into the local profile while
keeping the old total mass, the calculator deducts one unit from the ideal
remainder and returns `[0.999915005181, 0.999915005182]`. That is an
invalid accounting credit for the declared extra call. We include both
calculations as a hypothesis-sensitivity control, not as a defect in PR1240,
whose contract requires the coverage identity.

## Reproduce and checked evidence

Use Python 3.12 and the standard library from the repository root:

```sh
python3.12 scripts/research_package.py --package research/complex-block-target-screen
python3 -I -O -B research/complex-block-target-screen/verify.py
```

The verifier checks source hashes before loading the predecessor arithmetic,
extracts the selected block inventory by its source filename, checks both
orientation/profile bindings, and emits the 48-case table as JSON. It writes
no files. Explicit checks remain active under `-O`.

For an independent target oracle, we compute `(r/73)^(98/99)` using binary
search on integers. At scale `S=2^160`, each returned interval has endpoints
`q/S` and `(q+1)/S`, with

`q^99 * 73^98 <= S^99 * r^98 < (q+1)^99 * 73^98`.

We compare its enclosures with PR1240's logarithm/Taylor intervals for all
48 cells. The full-inventory ceiling bracket uses the pinned predecessor
engine; we do not claim an independent root enclosure at its other exponents.
Eleven controls cover seven altered block/orientation premises, an invalid
rank cap, an unresolved interval, removal of the centre premise and the
invalid extra-work credit above.

We also ran the predecessor's complete finite-premise replay in this session:

```sh
python3.12 -I -B research/complex-block-rank-optimum/verify.py
```

It passed 36 block interfaces, 9,180 subset checks, 36 independence minors and
12 controls. The new registered replay consumes the pinned certificate and
proof; it does not rerun that predecessor command or establish its all-order
theorem through finite testing.

The registered replay passed on macOS arm64 with CPython 3.12.13. Optimized
CPython 3.14.6 produced identical JSON bytes, including all 48 intervals and
11 controls. The selected-record integrity check and package metadata/source
pins passed. We report hosted CI separately in the contribution PR.

## Scope and credit

For each retained block, a redesigned exterior must preserve the predecessor's
independent dirty inputs, eight existing equal-volume helpers, input frames,
late additive output frames, monotone common-frame operations, final rank
nine, and coupled forward/backward provider contract. Cross-block coding,
extra arrays, target scratch, frame descent or earlier outputs may escape
that class. Source prefix minors certify the original word; a researcher
changing exterior work must establish these boundary premises again.

We retain the coverage law as a conditional hypothesis, alongside the centre
charge and global rank cap. Changed templates, port counts, copied-total
contracts or halving depths need a separate screen. We do not establish
compiler/hosting, precision/tape, analytic transfer, the bit interface or
the full multiplication theorem, and we do not claim Lean or human review.

Base main is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, priority revision 3.
[TASK.json](TASK.json) records the refined lower-bound task and
[SOURCES.json](SOURCES.json) gives exact input hashes and predecessor heads.
We coordinated in [Discussion1723](https://github.com/CrocSwap/integer-mult-bounds/discussions/1723).
Our entry overlap snapshot covered 408 open PRs and 358 Discussion records
with complete pagination at 07:50–07:51 UTC on 2026-10-14. We found the
predecessor block theorem, with no matching target-count screen. The search
does not cover arbitrary code diffs or establish novelty.

We credit Ali Romman (@aliromman) for PR1429's all-order block theorem,
Thomas DiFiore for the preceding helper-basis screen, Douglas Colkitt for
PR1240 and its exact engine, and the PR1012 coverage-law authors. We retain
Rohan Arun's PR1094, Jeremy Kothe's PR1087 and the cumulative k8/T16 lineage.
We do not claim to have discovered the block minima or the packing relaxation.

Prepared for Jose Manuel (@jmbarrancoml) with substantial OpenAI Codex
assistance in proof, implementation and prose. A read-only exploration
subagent identified the predecessor consequence and extracted its source
premises. New work follows Apache-2.0; we preserve predecessor files and licenses.

## Open next questions

A researcher can propose new contracts for at least eight of these blocks,
then price the complete replacement, including copied information, adapters,
restoration and hosting. The first step is to name the blocks and their new
array/frame/output boundaries. A concrete admitted replacement is the blocker;
the 15 open cells alone supply none. Changing the centre path, coverage law
or rank cap instead requires a new screen. See the structured handoff in
[TASK.json](TASK.json).

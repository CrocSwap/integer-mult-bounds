# Native frame realization of the P104 two-target correction

This closes one explicitly open finite obligation in [Ross Richardson's
PR2445](https://github.com/CrocSwap/integer-mult-bounds/pull/2445), at
`6def43ad673b91dbd491389964d1dcd059bf2ac2`: its two-target correction now has
concrete native frame-transport recipes in PR1991's physical coordinates.
The 78-helper construction, its lifetime minimum and its scalar schedule
belong to that predecessor. No new supplier or kappa is claimed.

## Scope and evidence

There are **161 distinct added transport edges**, all absent from PR1991's
740-edge recipe catalogue. They cover all **236 added occurrences**. Every
edge and its inverse has an exact Gaussian monomial / positive child /
Gaussian monomial realization at the declared dimension-gap rank. An
independent interpreter checks the signed action on all 18 Pauli generators
and an exact Gaussian state column, including global phase. The inverse-edge
checks do **not** establish the supplier's reverse-orientation interface.

The checker then binds every recipe to the literal merged 4,734-event word,
checks all 1,646 transport occurrences, 208 intrinsic endpoint adapters and
14,400 physical root pairings, and proves its forward endpoint by a complete
rational row induction over **358 independent logical input arrays**. That is
128,164 exact endpoint coefficients, not sampled numerical inputs.

Y0 and Y1 end as `y_t+x_t`; the other 102 Y rows retain `y_t+(Gx)_t/2`.
All 150 original/added dirty helper logical values restore at their specified
final FULL charts. The eight original owned private-copy lifetimes remain
under their inherited allocation/discard contract. This package does not
claim their nonzero private values were reversibly uncomputed to zero.

The added native profile is unchanged:
`142 H1 + 16 H2 + 18 H6 + 60 H7`, rank mass **702**.
The full partial word has rank mass **3070** and 3064 rational scalar ADDs.
These are finite local charges; productive helper boundary progress is not
automatically recursive excess cost. [PROOF.md](PROOF.md) states the precise
operator implication. [RESULT.json](RESULT.json) is the checked receipt.

Eight controls reject wrong forward/inverse phase, a false rank charge,
missing recipe coverage, removed dirty compensation/capture/collector mixing,
and an ADD declared at the wrong physical chart. Reversing the order of every
binary frame basis is a positive control. The default checker imports neither
the Clifford compiler nor PR2445's generator/checkers, and fails on missing
or changed source evidence instead of regenerating it.

The original `p104-side-correction` card is explicitly narrowed to this native
interface in [TASK.json](TASK.json). Exact base/source Git blobs and SHA256
pins are in [SOURCES.json](SOURCES.json) and
[EXTERNAL-SOURCES.json](EXTERNAL-SOURCES.json). The literal predecessor circuit
and its proof/attribution are retained unchanged under `inputs/`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -O -B research/p104-two-target-native/verify.py
python3.12 scripts/research_package.py --package research/p104-two-target-native
```

To regenerate recipes, use a new output path:

```sh
python3.12 -I -B research/p104-two-target-native/compile.py --out /new/path/native.json.gz
```

Compare the complete decompressed JSON with `NATIVE.json.gz`; compression
headers are not mathematical evidence. Direct verification requires only the
package and the declared source files, with no Git or network. The generic
package metadata check additionally resolves historical Git provenance.

Native frame admission here means exact finite 512-address operators and
their composition with rational common-chart scalar shears. It does not
provide a bit/tape implementation of those scalars, recursive rounding bounds,
arbitrary-size lifting, the supplier reverse orientation, global owners,
idle/residual charges, or a favorable completed 104-target moment. Hosted CI,
human review and a proof assistant are not claimed.

## Open next questions

Can this exact partial word satisfy the supplier's reverse-orientation and
precision contracts? First state the required intrinsic entry/exit charts
and derive that orientation from this literal word. Merely inverting each
native edge is insufficient, particularly around the private-copy contract.
Then derive physical prefix bounds for the actual scalar-address lowering.
These gates remain separate from extending the correction to 104 targets and
finding chronological global owners. Structured next steps are in TASK.json.

## Credit

Ross Richardson / PR2445 supplies the complete two-target word and sharp
78-lifetime construction; commdata2338 / PR2393 supplies the one-target
acquisition proof and sharing handoff. Hiroki Kumazaki / PR2353 and Philippe
Van Velzen supply the relay model and lifetime distinction. Rohan Arun /
PR1972 supplies the original channel, Chafik Boukhalfa / PR1991 its native
realization and label isometry, Adam Gall / PR1940 the schedule, Josie Elliston
/ PR1071 the fixture, and Ali Romman / PR1125 and the retained E8 lineage the
underlying geometry. The Clifford compiler is retained from icekylinx's
frame-sa504 work; the independent Gaussian interpreter is Ali Romman's PR1862
implementation as retained by PR1991. Existing notices remain in that package.

Prepared for ywz65 with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. The standard Clifford uniqueness and
linear-induction arguments are not claimed as new mathematics. Apache-2.0;
no independent human review or formal-kernel proof is claimed.

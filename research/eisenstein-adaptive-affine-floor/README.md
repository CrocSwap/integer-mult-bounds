# Adaptive affine broadcasts retain the sharp Eisenstein floor

On the source-pinned forty Eisenstein E8 lines, every execution of an exact
adaptive affine **public broadcast** protocol costs at least the total demand
`N=sum b_t` under the stated additive pairing-rank price. Direct broadcasts
attain N. For equal b-bit demands the sharp bound is therefore **40b on every
input**, including worst-case and expected cost under any input distribution.

The controller may change coefficients, source supports, widths and stopping
time based on prior paid answers. Each query is affine on the original input;
the resulting global encoder can be nonlinear. All receivers see every paid
answer, and every branch/header choice must be determined by those answers.
Privately chosen uncharged metadata and genuinely nonlinear node queries are
excluded. This is an abstract priced observation model, not a physical supplier.

## What is new

Jose Manuel's [PR2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017)
proves the sharp fixed-support block-linear floor using a Hermitian Gram
matrix reduced to F4. It does not cover input-dependent query selection.
[PROOF.md](PROOF.md) transfers that retained floor to each reachable adaptive
transcript, including variable termination and nonlinear leaf decoding.

The key new contract check is equality of the entire leaf fiber with its
frozen affine equation set. An input solving those equations follows exactly
the same path by induction, since the controller has no additional private
information. The difference kernel then forces each demanded coordinate to
be a linear combination of frozen queries and permitted orthogonal side
information. That produces a fixed fitting matrix on this path. PR2017's
Schur-rank argument gives the path's charge at least N.

The affine-fiber and kernel/row-space facts are standard linear algebra and
are not claimed as new methods. The contribution is their quantified,
source-bound use at this adaptive interface. It does not prove a floor 40b
for arbitrary nonlinear Eisenstein encoders; Michael Fischler's PR814 broader
fixed-support nonlinear model retains its separate 22b-to-40b interval.
Jerry Chen's Hurwitz adaptive-routing result treats another geometry and a
nonlinear paid-header expected-cost bound, not this pathwise affine theorem.

## Exact adaptive examples and evidence

The ten orthogonal four-frame partition and its cost-40 broadcast construction
are retained predecessor work. Our example first broadcasts frame parity z0,
then broadcasts z1 when z0=0 and z1+z2 when z0=1, followed by z2 and the other
frame parities. Its second output is `z1+z0*z2`, a globally nonlinear function.
Every node query is affine; the paid first answer determines the branch.
Every path costs 40. A variant has an extra redundant paid query on one
branch, giving costs 40 and 44. Block and unequal-demand examples retain
their actual source-span and per-bit charges.

The exact primary replay covers:

- 2,137 reachable leaves across full forty-bit, variable-length, affine-offset,
  block, unequal-demand and empty-demand fixtures.
- 62,768 complete-kernel directions and exact fiber cardinalities; their
  disjoint sum accounts for every input, including all `2^40` inputs of each
  full fixture without enumerating them individually.
- A fitting recovery matrix for each frozen query path, the lifted Hadamard
  identity, and actual rational/K/F4 source-price comparisons.
- The unchanged original PR2017 verifier, including its exact geometry and
  seven original controls, followed by seven new effective controls.

The new controls remove a frame query, undercharge block width, omit source
support, drop affine constants, freeze the wrong adaptive coefficient, and
reject leaf-fiber equality for a hidden private header or a nonlinear query.
The header/nonlinear examples delimit the theorem; they do not provide legal
lower-cost protocols in this model.

[SMALL-TREES.json](SMALL-TREES.json) contains literal query nodes. The separate
[independent checker](independent.py) imports no new producer code and traverses
all 8,320 inputs in three smaller trees. It checks 98,816 receiver observations
for conflicting demanded values, all 24 exact whole leaf fibers, and six actual
rational support prices using its own Fraction and binary elimination.

These finite checks corroborate the written all-width proof. Neither a finite
search nor a proof assistant establishes its universal quantifiers here.

## Cost screen and limits

The assigned ceiling verifier and lever table were run first. Applying the
incumbent 112-port ceiling to this changed alphabet would be unjustified.
Under the **additional inherited Eisenstein Dfc stage identity**, the matching
replacement screen is instead

    D/T = (s-1)*80b - 2s*C <= -80b

for every positive stage count s. Thus public-history affine adaptivity cannot
supply positive deficit in that conditional format, even if all other work
were free. This is not a native realization or a new kappa.

Every bit, including redundant or constant bits, pays `c(All,A)`; this additive
physical interpretation remains an assumption. All branches and descriptors
are functions of already-paid answers and reveal no further private bits.
Localized observations, private routing headers, nonlinear payload queries,
correlated entrance restrictions, errors, cheaper physical sharing, changed
geometries and changed stage laws remain outside the result. No selected
source, record, invoice, hosting, compiler, precision or analytic transfer is
changed. The full selected cold replay was not run.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -I -O -B research/eisenstein-adaptive-affine-floor/verify.py
python3.12 -I -O -B research/eisenstein-adaptive-affine-floor/independent.py
python3.12 -I -O -B research/eisenstein-adaptive-affine-floor/integrity.py
python3.12 -B scripts/research_package.py --package research/eisenstein-adaptive-affine-floor
```

The primary command reports `PASS_EISENSTEIN_ADAPTIVE_AFFINE_FLOOR leaves=2137
kernel_directions=62768 controls=7` and compares the typed committed receipt.
`--output NEW_PATH` refuses to replace an existing file. Default replay is
read-only. All source SHA-256/Git-blob checks precede executable source imports.
The integrity checker performs two optimized Git-free relocated replays and
eight source/receipt/tree/CLI corruption checks. It confirms that deleting a
literal query is rejected independently as a receiver-conflict witness.

Primary, independent and integrity commands passed under CPython 3.12.14.
A separate Codex agent reviewed the proof, model and both scientific checkers
and independently replayed the primary and truth-table checks with CPython
3.12.7, finding no blocker. Parent proof review corrected the singleton-price
justification to use actual rational pairing rank. No independent human,
hosted CI or proof-assistant review is claimed.

## Provenance and selection

[SOURCES.json](SOURCES.json) pins six unchanged predecessor/context files at
canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, with SHA-256 and
Git blobs. This includes PR2017's README/verifier, Jonathan Lam's actual
geometry, the nonlinear and adaptive prior interfaces, and the Eisenstein
phase cost screen. The task catalogue is historical provenance.

Picker seed `dea0cac7d7721c90e0a3629c8b5b4dbc` selected complex mechanisms;
the chosen card is `complex-rank-shape-decoder`. TASK.json records the change
from a positive decoder search to this precise adaptive-interface obstruction.
The first `complex-local-word-ceiling/verify.py` and `levers.py` runs passed.
[OVERLAP.json](OVERLAP.json) records the complete coordinated cache of 798 open
PRs and 1,252 Discussion records at 15:55:59/15:59:22 UTC on 2026-10-15.
Main was freshly fetched unchanged at 16:00 UTC. This metadata/local-note
coverage is not every diff or closed historical result, nor a novelty guarantee.

## Open next questions

- Can a fully priced localized observation protocol improve the Eisenstein
  cost? First specify each receiver's observations and charge any header or
  routing choice. Such private observations can break the common leaf-fiber
  recovery argument; no protocol or physical bill is supplied here.
- Can genuinely nonlinear payload queries improve the nonlinear 22b-to-40b
  interval? First exhibit an exact small-block code with declared supports,
  widths, orthogonal side information and additive charges. The affine-fiber
  premise is the present blocker; no nonlinear construction is claimed.

Credit Jose Manuel's PR2017 good reduction and block-linear rank argument;
Jonathan Lam's PR798 geometry and frame construction, following Joel Pulikkan;
Michael Fischler's PR814 nonlinear model; Jerry Chen's Hurwitz adaptive-routing
boundary; and the retained project lineage. New work by ywz65, with substantial
OpenAI Codex assistance in proof, code, tests, writing and separate-agent review.
Apache-2.0; submitted for independent review.

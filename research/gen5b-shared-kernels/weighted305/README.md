# Bounded shared-donor port to the pinned restart-packed word

This additive PR302 verifier builds on PR305 at
`a17c42903bbe8d9d26c4bc712d7216a7176237e9`, package
`research/gen5b-weighted-repacked` in `eumemic/integer-mult-bounds`.
The parent directory and earlier `weighted275/` evidence remain unchanged.
All comparisons here are historical pinned comparisons, with no current-best,
exclusive-priority or global-optimality claim.

## Conditional results

| Fixed case | κ | Literal stock | Calls | Rank mass |
|---|---:|---:|---:|---:|
| Independently reproduced PR305 | 0.000751140529238897 | 1,229,665 | 482,030 | 2,454,930 |
| Complete 154-group port | 0.000751160050810041 | 1,229,280 | 483,000 | 2,454,160 |
| Single reclosure, 156 pivots | **0.000751160060489770** | **1,229,275** | **483,015** | **2,454,150** |

The 156 result is approximately 0.00260021% above the pinned baseline. The
advantage over 154 is only 9.679729×10^-12 in κ. Both cases are fully checked
for the represented changed obligations under the inherited interfaces.
Finite certificate success does not establish an unconditional multiplication
theorem or practical performance improvement.

## Exactly what was searched

The new base occupies six logical roles used by the previous line2/3 group:
7955, 8998, 8999, 9146, 9147 and 9263. The complete 136-pivot line16/17 group
and retained 18-pivot line6/7 group are disjoint from the new occupied support.
They form the first fixed candidate, with 154 pivots.

Exactly one additional maximum-closure computation is run on the five
surviving relations of the **existing** line2/3 group. It selects three; the
declared even-parity trim removes pivot9355, leaving two. Thus the second
candidate has 156 pivots. No new lines, donor bases, matching exchanges or
other search domain is introduced.

`selection.json` stores exact indices into the already published 166 witness.
`witness.py` reconstructs the two complete JSON witnesses and checks their
immutable SHA-256 values. This avoids duplicating their large entry lists.
The discovery replay independently regenerates the same selections and hashes.

## Fresh integration, not an additive headline estimate

The baseline already contains 1,734 inherited kernel entries, 87 second-descent
retimings, 440 early restorations and **eight** sinks. These are not added again.
The old final12 endpoint saving is not transferred.

For 156, the measured local histogram change is
`{1:+197, 2:+283, 3:-283, 4:+70, 5:-70}`; residual widths change by
`{24:-156, 23:+156}`. The construction has 197 distinct donors, 353 active
physical slots and 2,545 setup ADDs, followed by 2,545 inverse ADDs. It removes
1,928 initial unit ADDs; the finite bill takes no credit for them.

Both candidates use the actual eight sink entries. Literal sink incidence and
target sets are independently checked. The scalar majorant contains 16 actual
sink redirects, 684 acyclic target edges and 912 vertices. Fresh bounds are
F=438151 and B=14104135, giving
`64 F^3 B^2 = 1070888631470889114458162912766400` (110 bits).
The original 104-bit ceiling **fails**; the explicitly reviewed 112-bit
fixed-recipe certificate passes. No unchanged upstream checker is relabeled
as passing after that change.

The 156 chart certificate has 281 exact rational programs and 706 role uses,
with at most 508 factors and factor numerators/denominators at most 615/810.
The retained combined normalizer bound is 815. Concrete full-bank allocation
checks all 15,424 helpers in 60 replicas: 925,440 addresses per stage and
4,627,200 across five disjoint stages. Every width-120 bank is full.

The displayed finite coefficient is 90,417,469,526,202,901 (<2^80); the selector
bound is 905,817,884,400. The bit root is rigorously bracketed by
`[751724726385730, 751724726385731] / 10^18`. All three bootstrap steps and 47
exact rational inequalities pass, and the next κ grid tick is rejected.

## Reproduction

Python 3.11+ standard library only, with assertions enabled. From this directory:

```sh
python3 -B acquire_inputs.py --output /tmp/weighted305-inputs
export PR305_INPUTS=/tmp/weighted305-inputs
export PR305_OUTPUTS=/tmp/weighted305-results
python3 -B -m unittest discover -s . -p 'test_*.py' -v
python3 -B run_checks.py --check --inputs "$PR305_INPUTS" --output "$PR305_OUTPUTS"
```

Absolute invocation from another working directory is supported. `--case 154`
or `--case 156` narrows the aggregate to one construction; both are the default.
Run the earlier directories' suites as separate Python processes with their
own documented source variables. Their original files and source pins are
unchanged.

`inputs.json` pins 39 external files by immutable URL, exact byte count,
SHA-256 and Git blob hash. Upstream Python is stored as inert `.py.txt` and
never imported or executed. We reuse the parent exact-interval/assembly code
and sibling pure chart, closure and acquisition helpers. `DEPENDENCIES.json`
records their hashes. Downloaded source bundles and large generated bank/chart
outputs are excluded from the diff.

## Verification boundary

The checker proves changed physical prefix relations and forward/inverse
compositional F2 identities on all 18,952 pre-compaction physical columns.
It checks complete aliased paths and FULL endpoints, not a literal regeneration
of the entire inherited scalar stream. Its complete physical decoder and
source-span/chronological admission remain hypotheses.

Unchanged compiler, primitive chart/cover, routing, row conversion, eligible
prime supply, precision/recovery, complex semantic and analytic all-size
interfaces remain inherited. Exact complex profile arithmetic is replayed;
that is not a proof of its physical construction. The displayed finite invoice
does not instantiate the unspecified full primitive constant C_full or an
exact universal-machine cutoff. PROOF.md explains the composition and the
explicit payload-ceiling change. NOTICE.md preserves attribution and disclosure.

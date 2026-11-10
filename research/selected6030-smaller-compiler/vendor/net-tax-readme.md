# Structural rank compiler (18.28× smaller uniform-rank exponent)

This package gives reusable reductions in the tensor power and sufficient
uniform ambient rank. On my unchanged native profile from
[PR4453](https://github.com/CrocSwap/integer-mult-bounds/pull/4453), it reduces
the specified sufficient rank from **`2^2299850000000` to
`2^125790000000`**, while retaining conditional **κ = 0.00300120**.
The exponent decreases by **18.2832×** and the chronological tensor power
decreases from **675 to 260**. These are sufficient mathematical bounds;
they do not estimate physical runtime or the size of the materialized word.

The contribution is four connected proof steps and a generic exact checker:

1. **Net splitting and completion taxes.** Charge the increase in paid
   moment and retain the productive moment added by same-owner completion.
   For `C<=u<=1`, the splitting coefficient scales as `O(C/u)` rather
   than a fixed two.
2. **Normalized logarithmic majorants.** Use `(1+log2(n)/h)^p`, checking the
   entire ordinary base range at one endpoint. The scale is a certified
   parameter adapted to the finite unit.
3. **The exact paid exit law.** All terminal exits are the `(G+1)`-fold
   paid inventory. Their average logarithm can replace the maximum paid
   rank in the compiler bound, using finite coefficient comparisons.
4. **Tensor concentration and logarithmic moments.** Preserve concentration
   of the raw tensor log law, bound the full paid perturbation, and compare
   Bell-polynomial coefficients. No product histogram needs to be emitted.

The last two statements are about the separated compiler. The paid product,
completion and splitting remain necessary here to obtain separation.

## Exact benchmarks and controlled comparisons

All rows use the full paid completion and splitting construction. `C` is
the tested moment saving; κ is the retained multiplication endpoint.

| Profile and method | C | Tensor power | Log power p | Sufficient H in N=2^H |
|---|---:|---:|---:|---:|
| Native PR4453 parameters | .00300122 | 675 | 160 | 2,299,850,000,000 |
| Net taxes and normalized logarithm | .00300122 | 476 | 108 | 967,750,000,000 |
| Paid mean certificate | .00300122 | 227 | 28 | 286,650,000,000 |
| Concentrated log moments | .00300122 | 227 | 21 | **189,350,000,000** |
| Concentrated moments, balanced C | 90037/30000000 | 260 | 24 | **125,790,000,000** |
| P7 PR4433 predecessor | .00268648 | 150 | 13 | 349,300,000,000 |
| P7 net taxes and normalized logarithm | .00268648 | 113 | 7 | **130,200,000,000** |
| P7 with balanced C | 11551891/4300000000 | 100 | 8 | **88,580,000,000** |

The unchanged-C native comparison improves H by **12.146×**. Balancing the
already-certified moment and uniform-saving slack gives the 18.28× result;
it does not change the raw native profile. P7 retains κ = 0.00268647 and
demonstrates that the machinery applies to a second invoice. No least rank,
globally optimal parameters or new κ is claimed. The concurrent stronger
endpoint in [PR4447](https://github.com/CrocSwap/integer-mult-bounds/pull/4447)
uses the same native profile; this package makes a compiler contribution.
The selected frontier remains the record in `certificates/selected-result.json`.

For the main native witness, exact rational intervals certify:

```
v=260, c=20, b=21, u=171/1000,
C=90037/30000000, kappa=0.00300120,
p=24, h=3900,
net moment gap > 9.4810102643e-8,
raw normalized paid log mean < .860094 < 431/500,
full relative paid excess < 1.448e-6 < 1/100000,
largest polynomial coefficient ratio < .019353,
source complement capacity > .0196759.
```

The final check is the exact integer inequality

```
(3900+125790000000)^24 < 3900^24 * 2^599.
```

The previous specified grid point fails. Degree 23 fails this particular
moment-envelope certificate, and dropping tensor concentration makes the
degree-24 certificate fail. These are discriminating checks of the new
argument, not lower bounds on every possible compiler.

## Reproduction and future use

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B research/net-tax-rank-compiler/verify.py
python3.12 -B scripts/research_package.py --package research/net-tax-rank-compiler
```

The first command authenticates the pinned sources, reproduces all seven
certificates, compares the committed receipt, checks the exact exit law
against six literal pinned compiler flows, and runs the mathematical and
rejection controls. It does not rerun the native or outer producer suites.
Use `--write` only after inspecting intentional changes to the exact receipt.

The generic checker accepts a profile with positive integer `targets` and
`paid` histograms, and a rational witness. See [BENCHMARKS.json](BENCHMARKS.json)
for complete examples of the three compiler methods:

```sh
python3.12 -B research/net-tax-rank-compiler/compiler.py --example native-concentrated-balanced
python3.12 -B research/net-tax-rank-compiler/compiler.py profile.json witness.json
```

The supported profile contract takes the ambient rank as the largest
productive rank and requires all paid ranks to fit. The witness specifies
`saving`, `kappa`, `v`, integer `cutoff` and `floor`, rational `u`, integer
`p` and `log_shift`. `uniform_method` selects `shifted`, `weighted`, or
`log-moments`. The latter two additionally give rational log bounds under
`weighted`; `log-moments` names its raw bound `raw_mean_upper` and requires
`raw_log_bound` and `paid_excess_upper`. The checker verifies every proposed
inequality; numerical search results are never accepted as evidence.

For a new submission, bind its actual complete native histogram and native
hypotheses, propose a witness, run the checker, then bind the resulting
uniform saving to that submission's complete consumer. A generic profile
file is a conditional mathematical input, not a native admission.

## Proof and verification boundaries

Read [PROOF.md](PROOF.md), [SHIFTED-LOG.md](SHIFTED-LOG.md),
[WEIGHTED-EXITS.md](WEIGHTED-EXITS.md), and [LOG-MOMENTS.md](LOG-MOMENTS.md).
[RESULT.json](RESULT.json) records directed interval bounds, the complete
rational coefficient lists, source hashes, exact rank witnesses and rejected
mutations. Interval arithmetic is adapted from my PR4433 code, using exact
fractions, explicit series tails and outward rounding at 192 fractional bits.

The package verifies the changed finite moment and leaf-count arguments.
The exact raw invoices, native operator receipts and outer parameter points
are inherited from the source-pinned predecessors. Every retained endpoint
has the same κ and a supplied uniform saving at least as strong as its
original consumer requires. This monotone comparison reuses its outer point
and recorded positive margins; checking receipt consistency is explicitly
different from replaying the producer's native or outer proof engines.

All-column arbitrary-input correctness, whole-job adapters, spectators,
owned-center restoration, native tensor closure, analytic decomposition,
precision, fixed-tape costs, fine-prime exclusions and exact recovery remain
inherited hypotheses. The transformed words are finite algorithmic
prescriptions. Their numerical productive widths, denominator growth,
scalar counts and precision/storage constants are not materialized here;
their complete finite-word counting prescriptions remain required.
No Lean, Docker or all-history replay was run.

## Open next questions

- **Tighter raw log moments.** Replace the raw bounded-support chord bound
  with exact raw moment enclosures, then check whether the positive
  coefficient test reduces the integer degree. This needs a complete,
  directed moment list; numerical precision alone is insufficient.
- **A changed paid profile for κ.** Replay one actual native transition
  change with its complete invoice, then apply this compiler. The current
  profile's raw moment ceiling is unchanged by smaller rank bounds.
- **Width and physical constants.** Start with one small separated unit's
  exact batch-width recurrence. Ambient rank does not control the full
  materialized word or its owned-bank requirement.

Structured questions and blockers are in [TASK.json](TASK.json).

## Attribution and review state

zxv, with substantial OpenAI Codex assistance, including user-requested
Sol 6.1 xhigh subagents for divergent probes and independent mathematical
audits. These are author-side AI checks, not formal verification or an
independent human review. The user authorized submission of this reviewed contribution on 2026-10-22.

The finite integer compiler is Jacob Alan Sussman's Theorem 1G, retained
through PR4268/PR4359. Chronological product/completion and logarithmic
predecessors are retained through PR4414/PR4416, PR4411 and my PR4433.
Native4453 retains Cinna Davis's PR4440/PR4441 contributions and the complete
predecessor attribution, including my κ=.0023 construction.
[SOURCES.json](SOURCES.json) pins exact bytes. New work is Apache-2.0;
existing source notices and frozen evidence are unchanged.

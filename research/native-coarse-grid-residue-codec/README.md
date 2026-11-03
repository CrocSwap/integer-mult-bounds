# Unbiased native coarsening with an exact residue codec

A Gaussian native child can now accept a fine grid and return an unbiased
coarse-grid output while retaining exactly the information needed for inversion.
For N=512^f, a=r*f active axes and grid ratio 2^k with k>=ceil(a/2), the codec
uses 2*k*N retained bits and one fresh uniform seed of k+ceil(a/2) bits. It
attains the minimum possible unbiased mean squared error at every input. The
retained information and fixed fair-bit count are sharp in the stated classes.

The [proof](PROOF.md), [executable codec](codec.py), [generated receipt](RESULT.json)
and [source pins](SOURCES.json) give the contracts and limits. This is a
numerical interface and representation codec, not a new kappa or a finite-state
reversible circuit. Its storage optimum concerns the full fine input grid;
actual caller correlations can reduce the required information.

## Selected source binding

The selected PR6030 word has 3453 MOVE events, with ranks 1 through 8. The
complete frame ledger and rank census pass; an independent binary matrix and
finite-span pass checks every B block and the full census. The unchanged native compiler,
independent coordinate oracle and new interpreter check all 512 columns for
the first event of each rank. The other 2878 distinct edge recipes are not
instantiated by this package. The theorem applies to any supplied L C_r R
recipe in the stated class.

At width one, k=5 accepts the h/32 grid and returns the h grid used by the
PR6499/PR6506 scalar interfaces. A full-grid record uses 5120 retained bits and
6–9 fresh seed bits. One record slot for each MOVE uses 17,679,360 retained
bits and 21,683 separate fresh seed bits. These are proposed uncompressed
slots, not a complete invoice or joint storage lower bound. At larger widths
k must satisfy ceil(r*f/2); fixed k=5 is not an all-width result.

## Verification

The checks enumerate 25,184 complete quotient endpoints, 16 retained-bit
witnesses, 36 independent dense tensor cases and 432 small seed round trips.
Source checks include all 4096 representative columns in each of two
interpreters, 128 signed native round trips, 64 arbitrary residue endpoints
and exact means/variances for all 1920 seeds. All four seeds of a complete
262,144-coordinate tensor input pass with a 524,288-bit residue code.
Eleven semantic/domain controls and three source corruption controls pass.

Use CPython 3.12 and NumPy 2.3.4:

```sh
python3.12 -B scripts/research_package.py --package research/native-coarse-grid-residue-codec
```

The registered commands use isolated, warning-strict normal and optimized
modes. The unchanged source compiler/oracle run in a normal subprocess with
assertions enabled in both modes. Expected markers are
`PASS_NATIVE_COARSE_GRID_RESIDUE_CODEC` and `PASS_REGISTERED_RESEARCH_PACKAGE`.

## Complete scope

The proof gives the direct native, triangular, monomial, digit, arithmetic,
copy, width and buffer bills. It includes every encode/decode pass. The
O((a+k+f)*N*(w+a+k+f)) indexed bit-work bound is not an accelerated recursive
supplier or a fixed multitape schedule. Exact input recovery requires the
residue and seed. It does not justify free erasure, additivity, native-graph
consistency or cleanup after intervening arithmetic.

All five selected assumptions remain. The scalar predecessors' completed error
constants are not imported into this changed stochastic contract. Sampling,
physical seed access, residue lifetimes, reversible bit circuits, full caller
probability/restoration and outer admission remain open. A selected cold replay,
all native instances, predecessor full suites, independent human acceptance and
proof-kernel review were not run. See the PR for publication and hosted status.

## Open next questions

The next step is a complete caller join with a paid residue and randomness
schedule. First bind its error budget and every retained record lifetime to
the source rank census. The higher tensor precision requirement and physical
routing/circuit costs are blockers. No next scope is reserved.

## Credit and overlap

Ali Romman with substantial OpenAI Codex assistance; no subagents. [NOTICE](NOTICE)
credits the Gaussian Smith, modular capacity, stochastic sampling, scalar-grid,
selected word and native compiler predecessors. Those sources are unchanged.
The new contribution combines the explicit coarse-period quotient codec,
pointwise stochastic optimum, exact capacity/sampling statements and selected
source bindings. Classical factors and prior results are not counted again.

Canonical main: 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8,
selected PR6030. Public open/closed PR and Discussion metadata was refreshed
before the claim; related coarsening, Smith, unbiased, mixed-grid and entrance
work was inspected. Arbitrary diffs and unpublished work remain coverage limits.

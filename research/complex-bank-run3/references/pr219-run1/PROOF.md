# Construction argument and scope

## Claim

On the retained multiplication interfaces, absorbing the rank-22 residual family of
the PR200/PR205 terminal-modified bit word into the banks yields the conditional
exponent

    kappa = 700427501305159 / 10^18 = 0.000700427501305159

with the complex supplier binding. This is certified **at the accounting level**
(Steps 1–4 below, all machine-replayed by `verify.py`) and is **conditional on the
physical realization obligations R1–R4** (`obligations.json`).

## Step 1 — the absorbed family is exactly enumerated

`inputs/absorbed-occurrences.json` lists every rank-22 ledger child of the per-vertex
histogram with its provenance, derived from the pinned PR200 word
(`word_p12.json`, `frames_p12.json`, the bit certificate and the base checker, all
sha256-pinned in that file): 1,320 physical-chain frame jumps, 24 copied-centre
children, 880 source-chain frame jumps, 0 target jumps — 2,224 per vertex, i.e. the
full `hist[22] = 6,672` bin under the row's factor-3 normalization. No other bin is
touched.

## Step 2 — whole-bank volume and retained ledger

Under the three-copy integer normalization of the published packed row
(W = 56,402, rank mass 4,055,136, deficit 5,808, 877,638 children):

* absorbed volume `22 × 20,016 = 440,352` registers = `72 × 6,116` whole banks;
* retained mass `3,614,784`, retained children `857,622`, largest child 21;
* row identity `72·50,286 − 3,614,784 = 5,808`, deficit unchanged, stock drop
  `56,402 − 50,286 = 6,116` exactly the bank count.

This is the accounting form of "absorbing a family into the banks drops its dirt
and, by the row identity W = (mass + D)/m, drops the stock with it" (PR #208).
`schedule.py` also enumerates every block tiling of width 72 over the word's
residual families {4, 24} plus the new 22-blocks and checks pattern divisibility.

## Step 3 — exact paid moments

`arithmetic.py` prices the absorbed profile with PR200's exact rational interval
moment engine, including the complete worst-case envelope (bad fraction 10^-16,
fallback `32·72²` per retained child). Before the absorption is applied the same
pipeline reproduces PR #205's certified packed coarse saving
`683528191056257/10^18` **to the digit**, which validates the engine against a
published certificate.

* complex coarse saving (unchanged): `700918443859411/10^18`;
* bit coarse saving before absorption: `683528191056257/10^18`;
* bit coarse saving after absorption: `728251090009891/10^18` — the bit word now
  clears the complex cap `7.009184e-4`;
* three-level finite ordinary composition from PR200's completed ordinary supplier
  gives the bit leaf `≈ 7.282510899902281e-4`, strictly above the complex cap.

## Step 4 — balanced assembly

The unchanged 47-constraint balanced assembly (eta = beta = 10^-24, weak = 10^-30)
takes `a = min(bit leaf, (1−β)·b − weak)`. The bit leaf clears the cap, so
`a = (1−β)·b − weak` and the complex branch binds:

    kappa = 700427501305159 / 10^18 = 0.000700427501305159

All 47 strict constraints and 7 margins are positive; the adjacent grid point
`kappa + 10^-18` is rejected by the same assembly. This is the exact 10^-18-grid
sharpening of PR #208's priced rung-1 target `7004273/10^10`.

## What remains conditional (R1–R4)

The rank-22 bin is not the gauge-exterior species the current bank construction
absorbs: it is frame-transition increments. Non-gauge chains already bank their
residual projectors and keep every increment child, so the published mechanism
cannot absorb this family — this is exactly the "genuinely different residual type"
the suppliers' crossover notes reserve. A completed finite witness must add:

* R1: the residual-type definition, block shapes and per-occurrence block
  assignment (schedule.py supplies the admissible tilings);
* R2: formal-column replay of the modified word (F2 identity and defining-integer
  decoder) under bank re-assignment at the enumerated transitions;
* R3: exact charts, incidence colouring and prime witnesses for the new blocks;
* R4: moment-envelope parity (any completion child R1 introduces must be added to
  the ledger and the kappa recomputed).

Until then the claim is an accounting construction and certified target, in the
same sense every repository witness is conditional on its stated interfaces — and
strictly more limited than the published witnesses, which have their physical
realizations built and replayed.

## Inherited conditions

The retained analytic, uniform-recursion, fixed-tape, all-size compiler, selector,
routing, precision and finite-bridge hypotheses of the PR184/PR186/PR193/PR200
lineage are inherited, not proved. This is not an unconditional multiplication
theorem, a formal verification of the algorithm, or a runtime benchmark.

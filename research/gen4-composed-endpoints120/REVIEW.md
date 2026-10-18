> This is an intermediate-stage proof/review. Final endpoint-aware quantities and exponent are in README.md and PROOF.md.

# Independent review of combined native audit ports

Date: 2026-10-09. Reviewer: synthesis lane. Result: no blocking interface or accounting defect found in the reviewed versions.

This is an independent source/interface review against the actual completed receipts, not a claim of another complete verifier execution or a Lean certification. I read `lead/combined-{banks,finite,global,price,fixed}.cpp` and `lead/audit-combined.py`, and compared `codes/gen4/emitted-sinks` and `codes/gen4/emitted-sinks11` receipts. The separate unchanged upstream nine-stage replay was executed in this lane and passed.

## Dimensions, census and stock

| Quantity | 16 sinks + 741 kernels | 11 sinks + 746 kernels |
|---|---:|---:|
| Local physical registers n | 19914 | 19919 |
| Source and target width v | 1760 | 1760 |
| Helper roles R=n-2v | 16394 | 16399 |
| Base full residual roles R-2466 | 13928 | 13933 |
| New entrance rank S | 1552 | 1603 |
| Banks per stage before kernels | 343870 | 343990 |
| Banks per stage after kernels | 342318 | 342387 |
| Literal stock | 2556390 | 2556735 |
| Normalized stock W | 511278 | 511347 |
| Global formal columns | 23434 | 23439 |
| Literal child-rank mass | 306238800 | 306280200 |
| Literal deficit | 528000 | 528000 |
| Selector invoice | 2323671154800 | 2324379328800 |
| Full counted primitive coefficient | 186046575255584401 | 186081373697626201 |
| Final conditional kappa | 0.000724251636106082822039023 | 0.000724152960079789482950702 |

The dimensions are derived from the supplied compacted states, not stale public n=19930/R=16410 constants. The unchanged gauged families are 266 residual-rank-3 and 2200 residual-rank-4 roles. The full residual family is R-2466 before new kernels and R-2466-changed afterwards. `combined-banks` checks the entire resulting census, every actual role/replica/stage slot, nondegenerate charts, complementary projectors, and exact tilings.

With 120 physical replicas, rank-3 roles use 798 banks of width pattern 3^40. A new residual width r is packed four copies at a time with (30-r) width-4 fillers, in 30 banks per role. Unused rank-4 copies occupy width pattern 4^30. Full residual roles occupy 24 banks per role of width pattern 24^5. The code checks nonnegative allocations, complete role-copy counts, and the invariant

    banks = 798 + 8800 + 24*(R-2466) - S.
    literal_stock = 4*1760*120 + 5*banks.
    W = literal_stock/5 = 119374 + 24*R - S.

Thus the sink gain and kernel gain are composed in actual compacted stock; they are not added as independent kappa improvements.

## Boundary and replica accounting

The local rank histogram is recounted from actual binary MOVE/COPY records. The literal five-stage replicated histogram equals 600 times the local histogram, plus 422400 children at each boundary rank 4, 23, 46, 50. The normalized histogram equals one fifth of this literal histogram. Every coefficient is checked against the price receipt, all child ranks are below 60, and the literal deficit is checked to equal 528000.

For the winning case, the local rank mass is 423806. Its replicated mass is 254283600. Boundary mass is (4+23+46+50)*422400=51955200, giving 306238800. The parent volume is 120*2556390=306766800. Their difference is exactly 528000.

The scalar global replay checks all 23434 independent physical input columns for one five-stage template, including arbitrary helper dirt and all six bridge-omission controls. The 120-replica extension is the direct sum together with the explicit bank-assignment audit, not a claim that the global matrix checker materialized 120 copies of every column. Fresh center copies are checked to have immutable source roles; reverse COPY/DISCARD semantics and signed cancellation-free prefix bounds are accounted separately.

## Charts, selectors, finite invoice and exact pricing

New kernel chart matrices and their orthogonal complements are checked by exact rational inversion and residual conjugacy. The new maximum chart factor count is 312. The inherited conservative ceiling is 744: four times the public 186-factor maximum, covering the chosen convention that a row swap costs four elementary factors. This is a conservative local convention, not an assertion that PR276's primitive-swap convention is wrong. The additional 239 factors cover block normalization and placement, giving ceiling 983. The selector charge is recomputed as

    2*5*120*((literal_stock-1) + R*120*983).

The finite program and fixed-prime program independently recompute the invoice from actual R, literal stock and actual additions. The route count is 120*(24*1760+10*R). The external/internal row coefficients 20161/14401 and the retained route geometry are unchanged. Actual signed prefix bounds are 96 bits and remain below the stated 104-bit allowance. Counted coefficients remain below 2^80.

The fixed program binds the actual histogram and invoice. It verifies p=2^127-1 with 125 Lucas-Lehmer iterations, then uses two separate exact interval constructions for moment pricing. Floating/high-precision decimal calculations only propose candidates. Both comparison runs use eight ordinary finite levels, all 47 strict constraints, and reject the adjacent 10^-27 grid value at both the finite level and the coarse cap.

The inherited public common-ancestor compiler, rational address-grid and complex recovery results remain assumptions of the conditional public framework. Old frame admission is inherited from the pinned upstream replay; new frame admission is checked by the new bank audit. The sinks introduce no new address frames. Global F2 formal-column replay is not being relabeled as an exhaustive signed-integer decoder proof; the pinned signed decoder and computed signed prefix bill are distinct evidence. Full inherited asymptotic constants C_full may exceed the counted coefficient; the cutoff rule explicitly allows replacing the latter by C_full. These scope boundaries are accurately retained in the receipts.

## Reviewed source hashes

- combined-banks.cpp: `83084ba276a5b8887f8fbd4cfa02f6bcf1b8aab6eaf900390044a72080d0d6f3`
- combined-finite.cpp: `bd5c031eaeaddaf006ff112d55610c68fc3af477d361566a76e7744a7cd249e2`
- combined-fixed.cpp: `fa4111e0cf9f25375c59d1889399fcad52fd41813787872027638a2d4a4b8dc5`
- combined-global.cpp: `e30793b75670b6dfeea1a0adf14e63c9bf1ed46a7d4c5e33b0ad43013eea7240`
- combined-price.cpp: `4f1b62c0b0ec4d558b7de3dead261d697d5d8fcc559f21991a916e7ad970b0ed`

## Upstream replay and portable export commands

Upstream mathematical pin: PR276, DreamingOfClouds/integer-mult-bounds at `d428ab0462b9dfd3131ab4e89999f0adcd6173dd`.
The later head `cf6cb4ebb55f0ee5f03918033e96a29209ff6798` adds only `.github/workflows/five-stage-gen4-banks.yml`; none of the mathematics, package code or mathematical inputs changed.

The frozen vendor archive is `pr276-d428ab0-source.zip`, SHA256 `1fe3f2a50137dd60dff09863c80caa2385cc0a8b8d5f33e8cd0803fafc55f065`. Extract it to an empty package directory. Archive members are rooted directly at the package contents. Python 3.11 or newer and `sympy==1.14.0` are required. Example commands from a portable bundle directory:

```powershell
python -X utf8 -m pip install -r ./pr276/requirements.txt
python -X utf8 -B ./pr276/verify.py --output ./upstream-replay
python -X utf8 -B ./export276.py ./pr276 ./gen4-export
```

The verifier output directory must not already exist and must be outside the package. UTF-8 mode is important on Windows: the default cp1252 reader failed on a retained UTF-8 complex source file before the successful unchanged UTF-8 replay. Do not modify vendor files to work around encoding.

The successful lane replay used the equivalent portable invocation above, with the output directory named `pr276-replay-utf8`. All temporary files were directed to the available bulk-storage volume.

This completed all stages (virtual, raw, bit, scalar, primes, banks, complex, math, finite) in 479.234 seconds; `pr276-replay-utf8/verification.json` is the receipt. Its exact input manifest hash is `6381aa8d881a4a89cf6c40db5bcd705b928a27599540a270bf3cd15f604c705d`.

`export276.py` has SHA256 `97e1c479cd88caf1d6c47fb233eede3eebe02789355d8484b87f3e2a12375d4b`. It imports the unchanged pinned prepare/physical/parity components and emits a generic schema without editing the package. Original export n=19930, R=16410, cut=520031 must not be confused with the compacted sink exports. The sink transform produces a complete physical old-to-new map; only physical IDs are compacted. Donor ownership keys are virtual labels and remain unchanged, interpreted through `states.regs`.

## Post-review corrections and scope of the winning successor

The codes lane caught stale diagnostic metadata: `max_block_scalar` was hardcoded to 30 while the actual width-3 pattern contains 40 blocks. The lead corrected it to the maximum actual pattern length. The source hash above includes that correction. The correct maximum is 40, far below the admitted prime; allocation, selectors and all pricing formulas already counted the actual patterns, so this correction does not change the invoice or kappa.

After this review, the frames lane supplied a retimed successor with parent-reported fully audited kappa 0.000724956086062147312838780. The numerical tables above intentionally document the two independently reviewed pre-retiming controls. They must not be substituted for the final retimed source-bound receipts. The dimension, census, bank-allocation and invoice interface conclusions transfer only with that successor's own regenerated receipts.

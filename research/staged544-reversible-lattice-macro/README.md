# Staged544 residual: replace one clean word with dirty reversible scratch

This implements the actual rank-five residual for helper 277 in both pinned
PR3945 providers on a finite Gaussian lattice. Reversible numerical lifting and
finite-state bit circuits replace a destructive rounding step. One arbitrary
dirty `(b+1)`-bit workspace word is returned exactly, with no clean ancillary
bits in the explicit generalized-controlled-X circuit model.

Compared with our explicitly constructed clean-accumulator implementation, this
removes `(b+1)` required clean bits and adds four real-word operations per C pair.
The comparison is **a clean-space tradeoff, not a speedup or a paid supplier
improvement**. Both implementations realize the same rounded map. The source
compiler is an exact operator evaluator; it does not provide this physical
finite-grid baseline.

For one 512-coordinate spectator lane, the completed source-bound `L C_[5] R`
macro has 1280 pairs. Full dirty implementation:23040 real-word arithmetic
primitives,3792 real swaps,2304 real negations, one dirty word reusable serially.
The bit realization costs at most `10240b²+41584b+10240` NOT/generalized
controlled-X gates. The clean comparison costs 17920 word primitives and
`8960b²+35184b+10240` gates, with the same routing. The generalized gates are
also compiled into literal X/CNOT/Toffoli gates, borrowing only existing pair
bits and restoring them after each gate. At b=32, the dirty macro costs 442109184
Toffolis per lane versus 380425984 for the clean comparison, plus separately
counted X/CNOT gates. Recursive tariff/owner admission remains unknown; this
concrete implementation is expensive.

For `f` spectator lanes and grid spacing Delta, the completed Hilbert error is
at most `80 sqrt(f) Delta`. Every scratch bit is restored for **every** finite
data/scratch bit pattern. Numerical error claims additionally require the
proved no-wrap data range; scratch itself may overflow freely. The explicit
allowance maps this macro to PR3994's full-state logical-cut bound, retaining
the caller's tensor/range/lifecycle premises.

**Why direct replacement stops:** the actual rounded rank-five macro is
nonlinear. For dirty helper and source `h=s=e0`, `Q(h+s)-Q(h)-Q(s)` has 24
nonzero coordinates. Local reversible inversion therefore does not preserve
the whole provider's linear compensation/borrowed-buffer identities after
intervening arithmetic. No provider replacement, selected stock coefficient,
new kappa, or frontier change is claimed.

## Reproduce

Run `python3 -B verify.py` and `python3 -O -B verify.py` from this directory.
Default verification is read-only and uses only the standard library. Optional
`--print-result` prints recomputed mathematical evidence without writing files.
The repository registry is `python3 scripts/research_package.py --package
research/staged544-reversible-lattice-macro` from the repository root.

Checks authenticate source bytes, bind helper 277 in both actual providers,
replay the credited PR3987 canonical-frame/recipe oracle on all 512 columns,
exhaust 279552 modular half-sum cases and 67584 pair states, and compare literal
bit circuits with the arithmetic specification on 17408 half-sum cases and 2048
pair states. They also check actual full-macro dirty return/inversion, exact
Gaussian error bounds, the nonlinear witness, and meaningful source/parity/
sign-extension/phase mutations. Finite tests support the parameterized proof;
they do not replace it or prove the full multiplication theorem.

See PROOF.md for the derivation, RESULT.json for exact replay output,
LEDGER.json for the complete boundary/cost status and FROZEN-SOURCES.json for
immutable source pins. Exact predecessor notices are retained under frozen/.

## Open next questions

1. Bind the explicit bounded-fanin circuit to an affordable actual caller and
   serial or parallel scratch lifecycle. The rank-five recursive charge alone
   cannot pay the scalar circuit by declaration; optimize only after stating
   the real allowance.
2. Resolve nonlinear dirty compensation across actual intervening arithmetic.
   First replay the exhibited actual-macro witness through one concrete helper
   lifetime with reversible recovery information fully charged. Do not infer
   whole-word restoration from local invertibility.
3. Bind the actual caller's spectator dimension, dirty amplitude and budget to
   the completed-error bound. Only then derive selected stock/tape coefficients.

Credit Dugongue, dataisfire, Jeremy Kothe, Sagar Thakrar, roger-sato, Arham Tahir,
DreamingOfClouds, chafreaky, Cinna Davis, and the preserved native/owner/outer
lineage. Chris R / Clear1nsight with substantial OpenAI Codex assistance. No
independent human or proof-kernel review is asserted.

The dirty borrowed-bit controlled-X decomposition is credited to
[Barenco et al., Lemma 7.2](https://arxiv.org/pdf/quant-ph/9503016), not presented
as a new gate theorem. Its finite implementation and application here are
checked independently of that paper's diagram.

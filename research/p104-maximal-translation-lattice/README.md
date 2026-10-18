# The P104 lifting lattice is maximal

For the fixed integer lifting word of Tekalign's PR3025/3033, the
prefix-parity lattice of [PR3035](https://github.com/CrocSwap/integer-mult-bounds/pull/3035)
is exactly the full constant-translation group at every rank. This closes
PR3035's open question 2. At rank seven its **343-bit coset domain is
optimal among exact translation-lattice splits**. No coarser lattice can
reduce that domain further. This is a scoped mathematical theorem, with
finite executable checks, and gives no new runtime bound, supplier or kappa.

Base main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
PR3035 is pinned at `0cc430349a3f3dc200666bc22e997076e0a557ed`.
[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18981896).

## Why the sufficient conditions are necessary

[PROOF.md](PROOF.md) gives the complete argument. A pair's rounding error
is `(Im(a-b) mod 2 - Re(a-b) mod 2)*(1-i)/2` at both outputs.
Its increment under fixed shifts c,d is constant for all pair inputs
exactly when c-d has even real and imaginary parts. The output difference
is always `i*(a-b)` and the pair is bijective.

Now split a rank-r input into its independently variable lower halves.
Subtracting the last pair's output increments forces each lower half's
increment to be constant. Induction forces all earlier prefix conditions.
Bijectivity lets the last pair's inputs range independently, so pair
rigidity forces the final prefix conditions. This rules out the proposed
cancellation between stages on all inputs, rather than just a finite sample.
The full inverse group is the ideal image `U_r Gamma_r`, not necessarily
`Gamma_r`. Gaussian monomial wrappers and independent blocks transport
these exact groups in the stated way.

PR3035's retained modular index checker reproduces indices
`2^2, 2^6, 2^15, 2^34, 2^75, 2^161, 2^343` at ranks one through seven.
Its source is preserved byte-identically and authenticated before execution.
It is the predecessor's computation, not a newly independent index algorithm.
The new theorem makes its rank-seven count optimal within the coset contract.
Four independent rank-seven blocks require 1,372 coset bits in that contract.

## Evidence and limitations

`model.py` implements the literal pair, ideal numerator map and prefix test
separately from predecessor code. The complete rank-one and rank-two shift
domains contain 16 and 65,536 shifts modulo two and four. Testing the error
at three specified inputs leaves exactly 4 and 1,024 prefix-lattice members.
Thus every other shift has an explicit failure witness among those probes.
At rank two the survivor counts are `10240, 3072, 1024`, rejecting all
64,512 nonmembers. The origin-only test would wrongly retain 9,216 extra
shifts. The sufficient-prefix argument justifies modular table wraparound.
These finite checks support the proof and do not replace its all-rank induction.

The replay also checks 625 signed pairs, all parity inputs for 81 signed
pair shifts, signed forward/inverse identities at ranks zero through seven,
and a counterexample to reusing the forward lattice for the inverse.
Behavioral tests cover the misleading origin-only test, literal signed
floors, finite input limits, corruption rejected before source execution,
stale/incorrectly typed receipts, and read-only ordinary/optimized Git-free
exports. An internal read-only mathematical review independently checked
the proof and its source conventions; no independent human or formal-kernel
review is claimed.

The result does not bound general nonlinear encoding, circuit size, runtime
or storage. Different lifting words and noncoset contracts remain open.
No reducer, wide backend, physical caller, dirty restoration, precision/tape,
native admission, outer release or full multiplication theorem is certified.
The selected frontier is unchanged. This session stops at the theorem and
does not initiate another dependent circuit campaign.

## Reproduction

Python 3.12 and the standard library suffice. From repository root:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/p104-maximal-translation-lattice
```

Use `python3.12` directly if available. [RESULT.json](RESULT.json) is a
deterministic receipt. Verification never rewrites it or needs Git/network
access. The generic metadata check separately resolves historical source
provenance. All executable index input is retained within this package.
Tests place disposable exports under one private directory in
`~/.cache/integer-mult-bounds-runs/`; `IMB_RUN_ROOT` can select an existing
session directory. They remove those exports on exit.

## Open next questions

1. Can the existing 343-bit domain support a cheaper complete implementation?
   Price a sparse or staged HNF reducer, both narrow passes, all intermediate
   widths and buffers, and disposal before starting a dependent construction.
   The blocker remains the complete consumer/restoration bill; the theorem
   eliminates only the larger-translation-lattice route.
2. Can a different rounded pair or a noncoset encoding reduce the paid work?
   First name the changed contract and test the smallest exact pair/block.
   The theorem applies to the fixed pair word and its exact translation
   contract, so it gives no obstruction for a different model. A useful next
   construction needs an optimistic complete cost allowance.

## Attribution and implementation choices

Nick Petalas contributes the necessity theorem, inverse/maximality corollaries
and separate finite tests. Tekalign's PR3025 supplies the lifting word and
collector; PR3033 `b12bbaeb5ca2e83f15433fc2dd0ba3b766595281` supplies the scalar
split. Nick Petalas's PR3035 supplies the sufficient lattice, index algorithm
and bounded coset construction. Its modular checker is retained in
`vendor/prefix_index.py` with exact head, Git-blob and SHA256 provenance in
[PREDECESSOR.json](PREDECESSOR.json). Retain ywz65/PR2586/2555's native recipe
and rounded-shear context, Arham Tahir/PR2999's occurrence/collision lineage
and the broader credited P104 geometry/native contributors. Generic parity
kernels, Hermite forms and reversible lifting are not claimed as new.
Apache-2.0. Substantial automated assistance was used; process and review
limits are recorded in [TASK.json](TASK.json).

Build the Lever led to a complete, reproducible small-rank shift census.
Prove It Works required signed literal checks, source corruption controls
and read-only Git-free execution. Power of Ten bounds and justified runtime
deviations are recorded in [ENGINEERING.md](ENGINEERING.md).

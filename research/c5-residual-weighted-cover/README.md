# Sharp cost 20 on one residual physical C5

This package resolves PR3268's named residual `(10,12,23,35,16)`. Every finite
asymmetric strict-scalar fit over Q, R or C has complete-plane binary pairing
cost at least 20; five explicit terms attain 20. The new six-block rank cover
needs no term-count bound or equality-trace census. [PROOF.md](PROOF.md) gives
the argument and [RESULT.json](RESULT.json) records its exact finite premises.

The cover gives singleton weights `2,1,1` on planes `1,3,4` and pair weights
one on `{0,2},{0,3},{2,4}`, in the displayed cycle order. Its weighted forced
ranks sum to 20. Both implementations check all 1,024 actual rectangular
tariffs. The margin histogram is `{0:496,1:410,2:110,3:8}`. An independently
written dense-matrix implementation agrees on every tariff and proves an
independent ten-term upper bound. Eight behavioral control groups cover source
corruption, an invalid strengthened cover, changed geometry, binary ranks,
signed asymmetric factors and the distinction between free and forced entries.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/c5-residual-weighted-cover
```

For a direct source export containing this package and its two declared inputs:

```sh
python3 -W error -B research/c5-residual-weighted-cover/verify.py
python3 -W error -B research/c5-residual-weighted-cover/independent.py
python3 -OO -W error -B research/c5-residual-weighted-cover/test_verify.py
```

Set `TMPDIR` to a session-owned cache directory to keep the corruption controls
outside the checkout. CHECKS.json records the actual environment and validation.
`verify.py --emit` writes the deterministic receipt to standard output.

## Scope and source closure

The task card is `coverage-law-change`, priority revision 6, explicitly changed
to one local obstruction relevant to the plane-port decoder. Its first working
packing-ceiling control and lever calculation passed before this refinement.
The scientific baseline is canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`. The family decision is to stop after
this named residual, not start a dependent construction campaign.

PR3268's other four residuals remain outside this package and are not assigned
to a peer. Worker 4 is instead studying rank-shape equality on already covered
cores, starting with `(13,23,35,16,34)`. Neither package depends on the other.
No global decoder floor, native program, dirty restoration, hosting/precision
bill, supplier or kappa is claimed.
Selected cold replay, Lean, Docker and independent human review were not run.

The only live scientific inputs are PR2782's DATA-PHASES.json.gz and MATCHING.json
retained on canonical main. Their exact Git blobs and SHA256 values are pinned.
No pending PR executable, foreign Git object, network access or Git command is
needed by the mathematical scripts. The pending PR3268 head identifies the
handoff and credit, not a live proof dependency. A cold canonical checkout plus
this contribution therefore contains the complete replay source closure.

## Verification design

Build the Lever changed the deliverable from a floating proposal to a rerunnable
exact certificate. Prove It Works requires every physical tariff and an actual
strict scalar fit, rather than a graph-only transfer or matching cost histogram.
No primary or predecessor executable is imported by the separate implementation.

Power of Ten bounds all scientific domains: two files of at most 2MB, a 2MB
decompressed payload, 112 scalar ports, 56 planes, five selected planes, ten
scalar coordinates and 1,024 support pairs. There is no recursion. Functions
stay below 60 lines. All mathematical rejection checks remain active under
`-OO`. Managed Python arithmetic allocates dynamically, a deviation from fixed
allocation; fixed input and matrix sizes bound live scientific data. Unittest's
bounded dispatch is the only test callback mechanism. Python allocator internals
are not audited. Any extension of these domains must reconsider those bounds.
The registered replay runs warning-strict scripts; lint and formatting checks
are recorded in CHECKS.json.

## Open next questions

Can any of the other four named PR3268 residuals be settled with another exact
rank cover, coefficient constraints or a cheaper complete identity? This matters
to the remaining local decoder gap. First inspect each actual tariff table and
its surviving count states. The present cover is not assumed to transfer to
another cycle. No worker in the present split is assigned those four residuals.

Can a changed scalar mask or component-specific tariff evade this local floor?
First provide an exact full fitting identity and justify the changed native
contract. Legal reads, restoration and a complete physical consumer bill are
still required before construction expansion.

## Sources and credit

PR3268 by thakrarsagar at `ee5d4f466e6e44a1897896324a36aa4c64cf3912` supplies the
explicit residual handoff and the eighteen covered physical cores. PR3256 by
thakrarsagar supplies the earlier weighted-rank/equality-trace method. This
package supplies the changed six-block physical cover for one residual.

Credit Tekalign/PR2782 for the complete-plane tariffs and canonical physical
inputs; Arham Tahir/PR2879 for principal-block bounds; Sagar Thakrar/PR2484 for
the C5 scalar setting; Cinna Davis/PR1825 for the matching; Adam Gall/PR1889 for
the strict scalar mask; Nick Petalas/PR3248 for the complementary five-term
asymmetric theorem; PR3232 for the Gram floor. Retain ctoth, Philippe Van Velzen
and the E8/P112 geometry lineage. The full theorem is proved here without
assuming the pending predecessor packages. Apache-2.0.

# A finite numerical contract for one QQ16 child and half-ADD

This package constructs a finite rounded implementation of B1_2 events
11795 and 11796 on one 512-coordinate payload. A p-bit rank-one native
child has completed Hilbert error at most `(2 epsilon+epsilon^2)||x||`,
where `epsilon=2^-p`. The following half-ADD has error at most
`epsilon (||d||+||xhat||/2)`, using the actual returned child value xhat.
Both operations permit nonzero rounding.

With bounded dyadic entry components, a working quantum q/4 and signed
width `W=b-ell+6` cover every numerator and output. Two owned buffers return
to zero. The direct bill is 3,072 rounded additions/subtractions, 2,048
exact halvings, 2,048 signed moves and 4,096 scratch component clears.
The [uniform proof](PROOF.md) derives the error and range bounds and states
the 4,104-word logical payload-storage schedule. RN remains an explicitly
implemented compound integer operation in that invoice.

Consequently `p>=beta+delta+104` meets PR3235's local completed-operation
allowance `u=2^(-beta-delta-102)`. This is a local numerical construction,
not a full producer or a favorable physical/recursive bill. Owner routing,
input preparation, recursive tariffs and F17 consumption remain unpriced.
No kappa or selected-frontier change is claimed.

## Literal source and corrected working example

The source is canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`,
priority revision 6. Live source Git blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). The retained joint-query certificate originates
at `a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`. Native recipes are taken
from the immutable selected replay archive, member
`slots/local/CLIFFORD-RECIPES.json`, SHA256
`d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731`.

Zero-based indices refer to the complete 27,019-event B1_2 expansion:

```text
11795  climb A L470 frame0 -> frame5, rank1
11796  L524 += -L470/2, frame5
```

The initial proposed example was corrected by reading the literal source.
Event13489, L344 frame226->236, feeds the unit ADD
`L346 += -L344` at event13491. It is not the half-ADD example.
The checker binds all four event records, tests the second rank-one recipe
as a separate arithmetic control, and distinguishes unit and half coefficients.
No claim that these two pairs are the same source boundary is made.

The pending dependencies are documentary premises, pinned through Git objects:

- [PR3235](https://github.com/CrocSwap/integer-mult-bounds/pull/3235),
  `fafe9cc1af84bb10b6113c88b3fb36c11fc5a1fc`, supplies the conditional
  completed-operation allowance and this local implementation handoff.
- [PR3216](https://github.com/CrocSwap/integer-mult-bounds/pull/3216),
  `af5b2ff1c0afa3100c961fa11b4d6e1fe18714cb`, supplies the adjacent L344
  native error-direction warning. Its full suffix is not replayed here.
- [PR3226](https://github.com/CrocSwap/integer-mult-bounds/pull/3226),
  `6b17b9b7c76d60726bd87123b9bf9905aa3151dd`, supplies a different exact-grid
  theorem for the full F0 reference. This result permits actual local rounding
  in B1 and does not repeat or admit that whole-producer construction.

No pending executable is imported. Native recipe semantics are inherited;
signed monomial tables and both mixing formulas are implemented locally.
All 512 complex components are handled, including mathematical phases.

## Evidence and reproduction

The proof, not finite sampling, supplies uniformity under its stated input
format. The exact integer reference has capacity limits `2<=p<=4096` and
`1<=b-ell<=2048`. It checks range and exact halvings during execution.
Its 14 fixtures cover two literal recipes and seven precisions, including
104 and 256. Every fixture has nonzero native and half-ADD rounding.
All 28,679 small scalar checks satisfy the RN relative bound.

Six behavioral groups add a separately enumerated rounding oracle, an actual
binary64 replay of all output components, all 625 small complex-input pairs,
zero/cancellation cases, invalid/aliased entry formats, and phase/coefficient
failure controls. The binary64 check shares the source-bound monomial tables;
it independently performs the rounded arithmetic, not source extraction.
The direct four-term exact formula is separate from the rounded butterfly.

```sh
python3.12 -Werror -I -B scripts/research_package.py --package research/qq16-finite-child-halfadd
python3.14 -Werror -I -O -B research/qq16-finite-child-halfadd/verify.py
python3.14 -Werror -O -B research/qq16-finite-child-halfadd/test_verify.py
```

Expected marker: `PASS_QQ16_FINITE_CHILD_HALFADD`. The replay reads committed
evidence; it does not regenerate it. [RESULT.json](RESULT.json) records exact
event bindings, counts and output digests. [TASK.json](TASK.json) records the
refinement, stopping rule and the original card. Scientific evidence is
author-checked; no independent human or formal-kernel review is claimed.

The initial overlap snapshot completely paginated 285 open PRs at
2026-10-17T19:03:47Z and 2,063 Discussion records at19:04:16Z. Live #2727
comments and exact dependency heads were also read. Coverage excludes
arbitrary diffs and unpublished work and is not proof of novelty.
[The canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-19003012)
records the scope correction and public evidence status.

## Open next questions

Bind one actual caller's entry lattice, range and p-bit representability for
both fields. Start at a named admitted cut; a Hilbert norm bound alone does
not establish the needed component grid. Then attach both owned buffers and
the monomial tables to a priced owner schedule and a complete F17 consumer.
Those interfaces and the recursive tariff block a full budget comparison.
No further construction search is proposed from this local result alone.

## Credit and implementation limits

Credit commdata2338 for PR3235/3226, Nick Petalas for PR2965, the PR3216
contributor for the L344 handoff, Sricharan Vagvala for the pair-first native
rounding reference, Tekalign for the exact native vector conventions, and
Ali Romman, Sagar Thakrar, DLamdata, ywz65, Arham Tahir, Ross Richardson and
the retained QQ16/native source lineage. The source notices are unchanged.
The error argument uses standard normwise rounding analysis. The new result
binds that finite implementation, scratch/range proof and direct invoice to
one literal local boundary. New work is Apache-2.0.

Power-of-ten rule3 has a managed-runtime deviation in the Python reference
and tests: integer and Fraction objects allocate dynamically. Explicit source
byte limits, fixed 512-coordinate arrays, bounded integer precision/span and
fixed test domains bound live work. The 4,104-word count describes the written
numeric schedule, not Python objects or the test oracle's memory. Every
function has a finite scope; no recursion, dynamic code loading or background
process is used. Source extraction and test-oracle allocations are initialization
or verification work. A physical backend must enforce the same capacities
with preallocated storage before using this direct invoice as a bit-cost claim.

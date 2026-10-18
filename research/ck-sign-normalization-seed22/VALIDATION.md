# Validation and handoff

Tested on macOS arm64, 2026-10-13 UTC, with CPython **3.14.6** and system CPython
**3.9.6**. Both versions pass the complete `check.py` command and all three
`test_package.py` tests under `-I -O -B`. No third-party dependencies are needed.

The package verifies both orientations and all 4,438 runs. The Fraction scalar
projection and independent integer run-operator implementation agree on exact
emitted-stream digests, complete counts and boundary maps. There are 56 rejected
actual-run mutants (one missing final restoration and one changed add sign per
gain-producing run/orientation), five rejected toy mutations, a positive
boundary-segmentation check and a positive copy-fanout cost-growth check.
The minimal relocated source closure also passes after gzip recompression;
source corruption and a forged saving are rejected.

`make selected-record-check` passes at the original base. The new files do not
alter the selected result, `upstream/`, any existing generator or certificate.
`git diff --check` passes. A separate AI reviewer found no blocking algebraic or
accounting defect; its minor success-message issue was fixed and the package
rerun. This is AI-assisted review, not independent human peer review.

The repository-wide `make verify`, selected cold supplier replay, full native
Clifford/frame replay, global admission/owner/invoice/assembly, Lean and remote CI
were **not run**. This standalone finite research package adds no hook to those
paths. The focused checks above exercise its actual changed circuits, while
physical/compiler integration is explicitly outside its claim. No historical
receipt is represented as a fresh full replay.

## Refreshed source and overlap check

Original/fixed contribution base:
`f567884aeb8851b6e794af1184119a3bfbe1e631`.
During verification, upstream main advanced to
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`. The eight-file change concerns the
review batch and integration receipt; the selected certificate and current
status are unchanged. All four consumed input hashes were rechecked directly
from this fetched Git tree and match [SOURCE-PINS.json](SOURCE-PINS.json).
The new bounded-review policy was read; this package does not mark any pending
work reviewed or incorporated.

The submission refresh inspected **707 open PRs through #917**, including titles
and exact heads. Relevant new arrivals:

| PR | Inspected head | Distinction |
| --- | --- | --- |
| #917, Ross Richardson | `085c32a25e2a09b029fa816195b97fa93d6f0788` | Changes historical CK frame-zero compensation with two-sided bases. This result changes nonzero-frame helper runs; no code or claimed saving is composed. |
| #916, Stephen Shore | `1f0cd934f83ddf2f14f20275ecca072c5b85a7b9` | Admits #883's selected-X4 precondition lowering. This package does not implement or claim that integration. |
| #860, AmazedBot | `72899c888af7e171f8aba4d5c66f4b31a5719eba` | Signed coefficient-work reuse and admission for historical CK. Here the original coefficient lowering and work clearing remain. |
| #750, Sagar Thakrar | `b6d6934092c063ab2575ebee00f48bbc7b1c9d82` | Moves a cleanup scale and changes coefficients. Here macro order and unsigned coefficient preparation remain. |
| #807, David Awad | `b1a5c533a22c2665600102d872f6a84e0664a70d` | Restored helper-basis changes to frame-zero compensation. |
| #816, @dd-hemant | `133735a2cc2319c12ba5d786214b2217e083e7da` | Restored target forest in frame-zero compensation. |
| #882, @mightyOil | `e698981e0ffa680b6c5896dace1609025b97ad70` | Bounded within-macro JP8 synthesis. |
| #883, @mightyOil | `b31a870a3842b37f6ab97767c506ce91783632a2` | Selected-X4 two-register precondition fusion. |

The live pinned-issues query remained empty. The claim is therefore local;
no separate reservation issue was opened. Original predecessor credits and
licenses are retained. The result is a completed finite circuit contribution,
with an unchanged recurrence profile and no new kappa or global optimum claim.

## Final handoff

Submitted as [PR919](https://github.com/CrocSwap/integer-mult-bounds/pull/919).
A minimal export of exact implementation commit
`39b702f14f4ff74b87868257e5358e489e1dfe5c` (12 package files and four pinned
inputs, no Git checkout or cached artifacts) passed both `check.py` and all
package tests. The following commit only adds this handoff and updates the local
claim with the result link; executable code and both receipts are identical.
The immediate pre-submit refresh also saw #918's unrelated carry-grade modulus
audit (`df86cd10f78693061a0a545153d7d6f65dd62c4e`). No pinned sprint issue appeared.

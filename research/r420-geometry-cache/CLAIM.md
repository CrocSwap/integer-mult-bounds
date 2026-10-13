# Verification-engineering claim: seed 91

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`, freshly fetched main.
OS randomness `secrets.randbelow(100)` returned **91**, selecting verification
engineering. This is a second, independent contribution by @mtpsl with
substantial OpenAI Codex assistance; it does not depend on PR691.

Three narrow candidates:

0. Accelerate exact moment intervals. PR667/672 already address this area.
1. Cache repeated validated E8 geometry in PR543's mutation verifier.
2. Replace the repeated Fraction row reductions in one E8 frame initializer.

Choose `91 mod 3 = 1`: a bounded in-process geometry cache, preserving the
original arithmetic and all per-word checks. The exact geometry/header input
must be part of the key; no persisted cache or unchecked old certificate.
Expected deliverable: an opt-in adapter, same-input A/B benchmark, exact receipt
comparison and cache invalidation/aliasing controls. No frontier change.

Baseline observation: the original nine-negative/one-positive mutation suite,
including its initial valid word, took 8.120 seconds locally. The experiment
will rerun this same suite through each implementation and compare receipts.
Stop after one implementation and bounded targeted verification. Expected finish:
2026-10-13 12:55 Asia/Singapore; reserve the last quarter for verification/handoff.

No pinned coordination issue exists (GitHub pinnedIssues query returned empty).
Open issues contain only the unrelated Discussions request #650. PRs checked
through #700. The review ledger marks PR452 (older PR358 prefix/arithmetic
adapters) unreviewed; it is not a dependency. PR662 concerns complex Clifford
helpers, not this E8 label/frame audit. PR661's frame-search negative result
does not concern verifier performance. PR667/672 address interval arithmetic.
The selected PR626 certificate, its actual PR543 supplier and review, and the
repository contribution instructions remain as established at the recorded base.

Result: **completed tooling improvement**, submitted as
[PR709](https://github.com/CrocSwap/integer-mult-bounds/pull/709).
The same original mutation suite takes 8.239 s uncached and 1.273 s cached
(6.47x) in the recorded local pair. Complete diagnostics match byte for byte;
receipts, all ten original controls and twenty supplemental checks agree.
The adapter is optional, bounded and source-pinned. No existing verifier,
selected construction or upstream file changes; no new kappa.

The pre-submission metadata refresh reached #704 with no overlapping PR543
geometry-cache task. Main still equals the recorded base. Evidence, source pins,
reproduction command, dependency argument and limits are in this package.
This is the single result update to the local claim; no coordination thread
was available.

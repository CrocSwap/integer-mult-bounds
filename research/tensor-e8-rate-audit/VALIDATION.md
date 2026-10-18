# Validation and limits

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Audited source: PR647 at `956bb581e7f97328e1b53baa5aca3d2490f2f607`.
Execution date: 2026-10-13 UTC, macOS arm64.

The deterministic exact receipt covers all integer architecture depths 1–66;
there is no randomized search, unfinished search region or inferred impossibility.
Assignment seed 66 selects the last depth. The written proof covers the stated
profile algebraically for all positive depths, subject to the scope in PROOF.md.

Completed local checks:

- Exact receipt on Python 3.9.6, 3.11.16 and 3.13.16; isolated optimized
  acceptance checked on 3.11 and 3.13.
- Five tests: published depth-one/two histograms; independently implemented
  Decimal log checks at 120 digits; direct nonlinear moments at 250 digits
  for depths 1,2,3,6,16,66; nine cost/geometry controls; malformed depth and
  corrupted-receipt rejection, including optimized Python. Decimal checks
  are diagnostics, not the basis of the rational mathematical certificate.
- All five source-file SHA256 and Git blob IDs in SOURCE.json match the
  fetched immutable PR647 head.
- PR647's complete original `verify.py --check` was freshly replayed in an
  isolated archive checkout and returned `ALL_EXACT_CHECKS_PASSED`.
  This reuses the predecessor's implementation and does not count as an
  independent general-depth proof.
- The selected-record integrity check passed. The selected certificate and
  all `upstream/` content are unchanged. Whitespace and patch-scope checks pass.

Receipt SHA256:
`8114160ebe85b5d09520eb1e1c340d56e5cc874c2949e923cb86d30b75d6dcff`.

The source replay can be repeated without checking out another branch:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 956bb581e7f97328e1b53baa5aca3d2490f2f607
mkdir -p /tmp/tensor-e8-pr647-replay
git archive 956bb581e7f97328e1b53baa5aca3d2490f2f607 research/e8-paid-copy-ram-20261013 | tar -x -C /tmp/tensor-e8-pr647-replay
python3 -B /tmp/tensor-e8-pr647-replay/research/e8-paid-copy-ram-20261013/verify.py --check
```

No full repository suite pass is claimed. The earlier contribution's full
`make verify` attempt stopped at the unchanged selected bit supplier because
this machine lacks `boost/multiprecision/cpp_int.hpp`. That expensive suite
was not repeated for this isolated research package. A new path-scoped CI
workflow checks only this package; remote status is reported separately.

Before submission, 501 open PRs through #681 were inspected for overlap;
PR647's source head was unchanged and had no comments. No pinned coordination
issue existed. The local claim has one result update with the published branch
link. Credit and substantial AI assistance are disclosed in NOTICE.md.

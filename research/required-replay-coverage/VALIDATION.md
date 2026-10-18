# Validation

Windows CPython 3.11.9, base f567884aeb8851b6e794af1184119a3bfbe1e631.

Completed:

- Full archived PR799 reachability matrix: 112 altered-evidence cases accepted
  by the original complete binding; all 118 mutations rejected by enforcement.
  Pristine selected and supported historical replays accepted.
- Actual public old-binding CLI witness, new-CLI rejection, and refusal of
  incomplete ancestor reuse before any producer launches.
- Three contract/version/path tests and six existing binding tests pass.
  Existing PR799 tests now use ordinary copies to avoid Windows symlink
  privilege requirements; no mathematical expectation changed.
- Minimal offline relocation in a path with spaces passes under isolated
  optimized Python. Source drift and unsupported contract versions are rejected.
  Real archived evidence exercises final publication: missing native phase
  evidence cannot leave a newly published public RESULT.json.
- Fresh PR799 X4 native reconstruction, all 95 cold-end controls, native ledgers,
  independent local replay, residual wrappers, all 2949 phase edges, global
  owner/invoice/assembly and both independent local and price stages pass.
  This uses a complete, source-bound archived PR741 ancestor, explicitly recorded
  as reused. It does not freshly reconstruct that bit/SW4 ancestor.
- Final current coverage and publication functions rechecked that real fresh
  output. The cold run began with the prior direct-output wrapper layout;
  publication was later hardened to nest historical output under replay/.
  Mathematical check code, selected scripts and worker commands are unchanged;
  final publication is separately tested on actual evidence.
- Selected-record integrity passes with original source inventory and proof
  supplements. Both Makefile recipes resolve to the enforced entrypoint.

FRESH-REPLAY.json retains source/version IDs, complete native/top-level stages,
their measured durations and the final composition binding. EXPECTED.json is
the deterministic omission-matrix receipt. Timing is diagnostic, not a proof.

The first omission-matrix run reached the public CLI check and failed because
the historical PR799 script does not support isolated Python imports. Its CLI
invocation was corrected to ordinary assertion-enabled Python. The corrected
full matrix passes; the new entrypoint independently supports isolated checking.

`make verify` completed with a failure in the unchanged historical
`tests/test_recycled_bit_integration.py`: eleven optimized-entrypoint subprocess
checks exceeded their ten-second timeout under Ubuntu WSL on this checkout.
The preceding long historical producer checks passed, including full fallback
and both suppliers at kappa 0.000472154791. The aggregate stopped at
`verify-recycled-bit`, so no repository-wide or hosted-CI pass is claimed.
This contribution does not modify that test or its producer scripts.
All validation above concerns the verification gate and finite selected replay,
not the inherited all-size/compiler/hosting/analytic multiplication theorem.

Final overlap refresh found PR847 at 72b8406b96ea2e0f37bb5143f594e12d4817c92a.
Its basic integration is credited. This package adds versioned source contracts,
current-wrapper reachability, PR799 execution/result evidence checks and a fresh
native/global replay. PR851 changes bit bridge-control identities and is not
consumed; its selected-proof-hash change is not included here.

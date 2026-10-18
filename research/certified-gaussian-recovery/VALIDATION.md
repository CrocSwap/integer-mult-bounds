# Validation record

Executed locally on macOS arm64 with CPython 3.12.14, standard library only.
Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; priority revision 4.

The registered command passed both complete normal and optimized replays:

```text
python3.12 scripts/research_package.py --package research/certified-gaussian-recovery
PASS_CERTIFIED_GAUSSIAN_RECOVERY products=289 input_bits_max=14592 uniform_error<2^-49 RECEIPT_MATCH
PASS_CERTIFIED_GAUSSIAN_RECOVERY products=289 input_bits_max=14592 uniform_error<2^-49 RECEIPT_MATCH
PASS_REGISTERED_RESEARCH_PACKAGE research/certified-gaussian-recovery outcome=completed
```

`-I -O -B` also reproduced the exact receipt from a standalone copy containing
only this package and its three live pinned text inputs, with files read-only
and directories read/execute-only. No Git repository, network, external Python
package or predecessor executable was needed for that direct replay. The generic
repository runner separately validated the Git source pins and package metadata.
Appending a fault marker to one copied pinned source was rejected before imports
with `pinned source drift`; its original bytes were restored before the read-only
positive replay.

The individual multiplication command in README produced
`0xb00ea4e242d2080` with exactly 64 output bits. The source contains no float
literals or Python `assert` statements; numerical checks use explicit exceptions
and remain active under optimization. `git diff --check` passed for the staged
package. The old selected cold replay and unrelated historical suites were not
run, because no selected input or production verifier changed.

The final live overlap refresh at 2026-10-15 04:47:59 UTC covered 527 open PRs,
1,022 Discussion records and 1,538 local records, with complete remote
pagination and no warnings. It found no matching integrated Gaussian numerical
implementation. Closed work was covered through local notes and the ledger;
arbitrary code diffs and nested files were not exhaustively searched. The
relevant PR2234, PR2287 and PR2298 heads were unchanged on a separate live check
at 04:48 UTC. Canonical main remained the scientific base above.

The local finite certificate and written proof do not constitute a formal proof
of the asymptotic multiplier. No hosted-CI result or independent human review
is claimed by this record.

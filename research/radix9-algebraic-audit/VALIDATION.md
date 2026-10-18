# Validation and handoff scope

Local environment: Windows 10 build 26200 as reported by Python;
CPython 3.10.9, MSC v.1934, 64-bit AMD64. No third-party Python packages.

The following checks passed:

1. Normal exact replay and isolated optimized replay (`-B -I -O`). The
   deterministic receipt records all 54 coefficient enclosures, 48 inverse
   and 48 recurrence identities, 27 conjugation identities, both submitted
   factor certificates, 15 rejected mathematical controls, two valid factor
   reorderings and two valid conjugated factor certificates.
2. Eight focused tests cover invalid primitive embeddings, nested algebraic
   root enclosures, rejection of mere interval overlap, upward dyadic bounds,
   source/factor corruption, escaping manifest paths, offline relocation into
   a path containing spaces, output overwrite protection and forged receipts.
3. All four unchanged vendored files match both SHA256 values and the Git
   blob identities returned by GitHub for the pinned PR628 file list.
4. `python -X utf8 -B scripts/verify_selected_result.py` passed: selected
   kappa, finite certificate, original source inventory and proof supplements.
5. Staged whitespace validation (`git diff --cached --check`) passed.

The final exact coefficient/root-rectangle data were added to the receipt
without changing any earlier result: removing those additional certificate
fields reproduces the preceding JSON object exactly.

This is a new, isolated audit package. It changes neither a production
generator nor the selected construction. The full regenerating `make verify`,
supplier cold replay, PR628 execution/phase/dirty suites, Linux execution,
proof-assistant checks and independent human review were not run or claimed.
The added scoped workflow is configured for Python 3.11 and 3.14; local
validation does not establish its remote CI result.

The publication metadata refresh at 2026-10-13 06:07:46 UTC covered arrivals
through PR810. Main was `66849e1475c930fd7732b1a0067ffee7e1e95f60`;
PR628 was open at `0768f97d06c623b8211e651543c66135796b62bf`.
PR796's new prime-power valuation audit was inspected and credited in
`NOTICE.md`. It concerns p-adic valuations, not the complex interval and
factor-residual interface investigated here. No competing radix-9 complex
enclosure audit was identified in the inspected metadata. PR803's
degree-controlled inverse norm and PR804's integral-divisibility valuation
checks were also inspected and credited; neither is a dependency.

At the final submission refresh (2026-10-13 06:14:25 UTC, through PR811),
main had advanced to `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`, selecting
#741 with #589 on #555 at conditional `kappa=0.001661202643272239`.
PR628 remained unchanged. The selected-record integrity check reported above
was run on this audit's original base, not on that subsequent integration.
This standalone audit retains the original base and source pins.

At the initial patch handoff, submission access was checked through Git's credential manager and the
available browser session. Neither had a signed-in GitHub account, and the
GitHub connector was not installed. A clean patch and prepared PR description
were provided. Connection and publication are a subsequent step; a GitHub PR
or CI result is not implied by the local checks above.

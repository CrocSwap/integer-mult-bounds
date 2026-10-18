# Audit: reversal costs in the physical ripple counter

For the existing literal width-w ripple counter, N primitive calls in K
maximal constant-direction runs cost at most

    4N + 2(w-1)K                     (w >= 1).

If H of the runs contain a wrap, the sharper bound is
`4N+2(w-2)K+2H`. With no wraps it is `4N+2(w-2)K`.
Width zero costs exactly 2N. Both positive-width per-run coefficients are
sharp, witnessed by alternating single-call runs. An exact signed-potential
identity records every reversal and wrap; see [the proof](PROOF.md).

This is a **research note / adversarial mathematical audit**, not a new
counter algorithm or kappa claim. The existing Lean theorem
`CounterArithmetic.total_steps_bound` correctly assumes a fixed direction.
The contribution extends its accounting contract and supplies concrete
counterexamples to removing that assumption, even if all calls avoid wrap.
No defect in the selected construction is established.

## Reproduce

From the repository root, with Python 3.10 or newer and no dependencies:

```sh
python3 -I -B -O research/counter-reversal-audit/verify.py
```

Expected:

```text
PASS_COUNTER_REVERSAL_AUDIT schedules=130305 literal_executions=16376 controls=10
```

The command checks SHA256 and Git blob identities of six source files,
recomputes every field of [EXPECTED.json](EXPECTED.json), and rejects a
receipt mismatch. `--write /tmp/counter-reversal.json` writes a fresh receipt
without altering the committed one. All failures use explicit exceptions,
so optimized Python does not disable them.

Additional fault-injection checks:

```sh
python3 -I -B -O research/counter-reversal-audit/test_audit.py
```

Expected: six tests pass. These inject omitted head-return steps, a missing
wrap flag, an incorrect endpoint and source drift, and check the empty and
zero-width boundaries. The source-drift test runs a separate optimized Python
process against an isolated source copy.

## Completed coverage and independence

* A new single-cell tape interpreter implements the pinned transition table,
  including separators, returned heads and first completion. It does not use
  carry length to execute a call. All words of widths 0 through 10, both
  directions, and four exterior patterns give 16,376 executions. Arithmetic
  modulo 2^w and an integer trailing-bit calculation independently check
  each resulting word, flag and literal instruction count.
* The resulting physical transition table supplies every initial word of
  widths 0 through 7 and every direction string of lengths 0 through 8:
  130,305 schedules. Every schedule checks the exact identity and both
  bounds. A SHA256 commits to the ordered finite replay stream.
* A deterministic `random.Random(67)` replay adds 256 longer schedules of
  257 calls at widths 0 through 10. This is additional sampled coverage,
  not exhaustive coverage of that larger domain.
* Ten explicit false-claim controls cover omitted/signed reversal terms,
  wrap credits, sharpness, the fixed-direction hypothesis, initial width
  charge, and nonzero cost of zero-width calls.

The stopping rule is completion of these fixed domains, not a search for a
better exponent. The simulator independently implements execution but uses
the published transition table as its specification. Its source binding is
by immutable hashes and manual correspondence, not a verified Lean parser.
No Lean kernel rebuild or formalization of the new bound is claimed. The
universal proof is written separately from this finite evidence.

## Pins, scope and credit

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The counter package was published by **rfu08** in
`2d970ab3ca0271cfb2b609dc9aae1b7073b7774d`.
[SOURCES.json](SOURCES.json) records exact source hashes and Git objects.
The selected record at the base is #799, conditional
`kappa=1661634653669567/10^18`, following #741 with #589 on #555.
Its X4 construction and maintainer review were read to establish that status;
they are not dependencies of the new counter inequality.

[CLAIM.json](CLAIM.json) records assignment seed 67, three candidate tasks,
selection and coordination checks. No pinned or other sprint issue existed,
so the claim is local. PR #565 concerns physical counter copying; this audit
addresses direction-dependent counting costs and does not import #565.
Previously published counter README/review already identify the fixed-direction
limitation; the new evidence is the exact correction, sharper sharp run bounds,
nonwrapping obstruction and independently executable finite checks.

The charge is for completed primitive calls only. Initialization, mode
restart/dispatch, payload work, copies, reset/restoration and recursive
scheduler composition remain separate obligations. Resets must be charged
and split the state sequence. No full tape routing, multiplication theorem,
compiler/hosting realization or analytic transfer is established here.
Existing sources, selected certificates and `upstream/` are unchanged.

Contribution by **Kairos Ess (@Kairos-Ess)**, with substantial **OpenAI Codex**
assistance in derivation, implementation, verification and writing. No separate
human or delegated-agent review is claimed. Credit rfu08 for the existing
physical counter and formal fixed-direction accounting, and the repository's
original manuscript authors for the elementary scan argument. New files are
Apache-2.0 under the repository license; predecessor notices remain intact.

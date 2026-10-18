# Complex-supplier claim, seed 36

- Contributor: @24kHandsome1201, with substantial OpenAI Codex assistance.
- Assignment: OS-random seed **36**, drawn 2026-10-13 at 04:52:45 UTC.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Track: complex supplier. Seed parity selects the selected CK provider.
- Scope: contiguous scalar additions with an unchanged source, a common frame,
  non-unit dyadic coefficients, and a common odd numerator part. Reuse the
  coefficient-work stream by halving/doubling between different magnitudes.
- Method: exhaustive scan of both pinned CK event streams, preserving event
  order and every non-scalar boundary. Compare full primitive costs before
  implementation, then check arbitrary-input maps and prefix bounds exactly.
- Deliverable: a finite circuit result, executable verifier, pinned sources,
  complete run census, negative controls, proof and attribution. No new kappa.
- Planned finish: 2026-10-13 05:35 UTC, including final verification/handoff.

## Task selection and overlap

Three candidates were considered: (1) variable-coefficient work reuse,
(2) raw coordinate-factory resynthesis, (3) fixed-frame CK cleanup fusion.
Candidates 2 and 3 overlap #681 and #719. Candidate 1 extends the common-
magnitude reuse investigated in #722 to varying powers of two, on CK and
in both orientations. The selected runs must contain a genuinely changing
magnitude with a cheaper scale transition; equal-only runs are excluded.

The initial scan covered 544 open PRs through #725. The review ledger and
selected #626 construction/review were inspected. #696 changes the single-
macro primitive lowering, #723 changes JP8 numerator preparation, and #698
concerns B-frame optimality. None of those patches is imported here. Savings
will be counted directly against the selected program, with a separate
constant-magnitude-only comparator; no unverified additive savings claim.

There was no pinned sprint coordination issue. The only open issue found was
#650 requesting Discussions, so the claim is recorded here and no reservation
issue/comment is posted. Work is bounded to this one provider and mechanism.

The full finite domain is scanned, with no sampled search or solver timeout.
Source code and proofs are produced by one Codex agent; no independent human
or delegated-agent review is claimed.

## Result update

743 varying runs pass exact replay: 13,770 forward and 67,146 backward
real-component primitives saved. The incremental savings beyond constant-
magnitude sharing on the same blocks are 6,012 and 12,596. The 280 backward
runs occur in zero-frame preconditioning. All old prefix envelopes match.

The next overlap refresh reached #751 and found concurrent #739's JP8
forward-cleanup rescaling. The README/NOTICE credit its mechanism. This CK
contribution adds a distinct provider/phase domain and independently produced
716+9 full-program column evidence plus 11,610 local basis checks. No general
priority or combined-savings claim is made. See VALIDATION.md for submission
status and the final refresh.

The final pre-submission metadata refresh reached #767 and found #755's
equal-magnitude JP8 reuse in both orientations. README/NOTICE credit its
backward-phase coverage. This package's narrower contribution is separately
verified CK varying-magnitude reuse; no phase-priority claim is made.

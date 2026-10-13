# Bit supplier claim, seed 02

Claimed by Ross Richardson (@RossRichardson), with substantial OpenAI Codex
assistance, on 2026-10-13 at 11:29 UTC (22:29 Melbourne).

- Assignment: OS randomness, `python3 -c 'import secrets; print(secrets.randbelow(100))'`
  returned **2**, bit-supplier track.
- Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Selected certificate: PR799/PR589, conditional kappa
  `1661634653669567/10^18`; no new kappa is proposed.
- Object: PR589's tuned R439 phase-B block index 2, frame 519,
  `B[163:205]`, on twelve existing source registers.
- Method: split at `B[182]`, preserving the two exact integer-linear factors;
  exhaust destination-once positive-addition schedules for each factor.
  Verify the full dirty-input F2 map, literal reverse cleanup, frame paths,
  native ADD counts and positive prefix bounds.
- Deliverable: a checked shorter finite circuit or a scoped negative result,
  reproducible search, exact certificate and mutation controls.
- Finish target: 2026-10-13 12:09 UTC (23:09 Melbourne), reserving the final
  quarter for verification and handoff.

Three narrow candidates considered:

1. Frame 519 two-factor scheduling (chosen by seed 02 as block index 2).
   No specific construction claim found. PR891's whole-block single-write
   obstruction does not cover this two-factor search.
2. Frame 522 fixed-factor scheduling: another unclaimed block, but not chosen
   because the seed selects block 2.
3. Historical R480 quad 2: distinct from PR823's quad 1, but farther from the
   selected source than the chosen object.

Overlap: inspected open PRs 891, 873, 848 and 844 and refreshed the full open
PR inventory. Neighboring frame constructions 506/507/508/509/520/521/523 and
phase-A mini-nodes are distinct objects. Related methods and independent
evidence will be credited. No pending implementation is imported.

GitHub returned no pinned issues; the only open issue was #650 (Discussions).
Therefore the claim is recorded here rather than in a new reservation issue.

## Result update

Completed: [the checked frame-519 circuit](README.md) saves twenty complete
local ADDs (42 to 32 forward block gates, plus literal reverse cleanup),
with exact fixed-factor class minima 16+16. The reverse positive bound drops
to 1,031,082, the payload stays 93 bits, and the paid profile stays unchanged.
All local and native checks and controls pass; no new kappa is claimed.
See the [exact certificate](CERTIFICATE.json),
[native certificate](NATIVE-CERTIFICATE.json) and [executed validation](VALIDATION.md).
Final refresh found PR904's one-ADD `B[200:204]` replacement inside this
block. Our ten-ADD whole-block replacement and exact 16+16 class minima add
distinct coverage and evidence; [the overlap and attribution](README.md)
are recorded explicitly. No combined saving is claimed.

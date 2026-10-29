# Characteristic-five connector certificate

Alexander Richard Towell, with substantial OpenAI Codex assistance.

Start: 2026-10-29 19:07:50 UTC. Setup deadline: 19:17:50 UTC.
Investigation ends by 19:37:50 UTC; final handoff deadline: 19:52:50 UTC.
Workspace base: b6892c8f8c7e060031f8b103f5a8c4bcc7ac8690.

## Proposition and scope

No length-30 word with six letters each occurring five times realizes all
nonzero binary six-vectors as sums of two prefix-count vectors modulo five.
The predecessor reports UNSAT already for the sixteen masks of weights 2 and 6.
This visit certifies that finite relaxation and audits the implication from
admissible words to the CNF. It does not change kappa or exclude other interfaces.

Source: CrocSwap/integer-mult-bounds PR6141, head
d192172f57b10647ddcff9410c69d48ac06862c1. Pinned python-sat 1.9.dev15.
The inherited floor-word and depth-two interface is PR4231/4248.

## Implementation and verification plan

- [x] Preserve exact predecessor generator and its positive-word checker.
- [x] Establish a proof-producing SAT backend and independently built drat-trim
  within ten minutes; run a tiny UNSAT/SAT check before the target.
- [x] Export deterministic DIMACS for k=6,c=5,weights={2,6}; record exact hashes,
  tool versions, clause counts, runtime, and a proof with a bounded solver run.
- [x] Replay the proof with drat-trim; reject empty/corrupt proofs and a
  satisfiable CNF control. Audit encoding soundness, especially cardinality
  auxiliary variables, coordinate relabeling, and repeated boundaries.
- [x] Package reproducible commands, written implication, tests, source/tool pins,
  explicit limitations and one independent scoped AI review if a result is ready.
- [x] Refresh overlap before any public submission; preserve a clean committed
  local packet even if certificate generation or verification times out.

## Success and stopping rules

Success needs both independent proof replay and a justified encoding bridge.
No unrestricted theorem follows merely from a solver verdict. Stop at the setup
deadline without a viable environment; otherwise bound each expensive run and
reserve the final fifteen minutes. Do not start characteristic seven or another
research problem. Proof logging may be much slower than the reported 160-second
unlogged solve. A failed attempt is recorded as inconclusive, not an impossibility.

## Review focus

Reject a proof for a different CNF; do not accept a checker message without its
exit status; do not treat the empty trace on a satisfiable formula as evidence;
retain s=t readouts and the boundary-zero replacement; establish that sequential
counter auxiliaries can be assigned for every valid word.

Outcome: both archived replays pass with exact existing LRAT PR43 source.
The known issue42 was reproduced and its correction reused; see ATTEMPTS.md.
Normal and optimized nineteen-test suites pass. Publication and closing pins
are recorded separately after the verified source commit.

# Sprint claim (local record)

No pinned sprint coordination issue was found in the repository (open issues at
claim time: #650, #913; neither is a coordination issue), and this agent has no
issue-posting access, so the claim is recorded locally as CONTRIBUTING.md allows.

- **Track and seed:** 00-19 bit supplier; assignment seed **13** (drawn with
  PowerShell `Get-Random`, OS-seeded, before any task selection).
- **Base commit:** `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` (origin/main at
  dispatch).
- **Object:** the z-program of the selected PR589 bit word
  (`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`): the 2,629
  source edges of its A and B z-destination gates and their 2,629 literal-reverse
  cleanup mirrors. This is the A-section/decoder-adjacent region of the word,
  not the phase-B blocks (frames 506-524) that concurrent block-PRs cover and
  not the frame-524 block chosen by the earlier seed-13 sprint.
- **Method:** exact single-edge triangle (Steinberg 3->2) program rewrites with
  register-level commutation windows, an ADD-count objective (PR589's tuner
  optimizes the moment only), and acceptance gated on an exact 661-column
  replay, identical 661 frame paths and an identical paid profile. A complete
  duplicate-edge census is included as the paired-transvection control class.
- **Parameter range / coverage:** every triangle instance (edges (b,x), (b,a),
  (a,x)) in the z-stream of the committed word; greedy application to a fixed
  point; stopping rule = a full scan with zero accepted rewrites.
- **Expected deliverable:** a verified finite word with exactly 2 ADDs removed
  per accepted rewrite, unchanged paid profile and frame paths (so no new kappa
  and the frozen hosting argument carries over as in prior block PRs), plus the
  full coverage census and negative controls.
- **Expected finish:** same session; verification and handoff in the final
  quarter.

Checked immediately before writing: no open PR claims A-section or z-program
Steinberg/3->2 ADD-count rewrites of the PR589 word. Overlap notes: #933 and
#1048 close *profile/moment* reframing classes (orthogonal objective; this
package keeps the profile exactly unchanged), and #1015/#1045/#1062/#980 work
the phase-B blocks or other words (orthogonal region).

## Result (recorded after completion)

Delivered: 405 accepted rewrites, complete exported ADDs 24,305 -> 23,495
(-810), records 27,234 -> 26,424, unchanged frame paths, paid profile and
z-product U, exact endpoint on all 661 columns, six tamper controls rejected,
exporter cross-check passed, deterministic regeneration confirmed.
Submitted as PR https://github.com/CrocSwap/integer-mult-bounds/pull/1127
(branch `research/agent-12-bit-seed13`, commit 5ce6bcaf on base abdc6a7).
Concurrent #1122 (bitplane, same track/seed number by coincidence) composes
frozen PR980/PR1062 changes on the semantic-D word lineage; different word and
mechanism, not additive to this result.

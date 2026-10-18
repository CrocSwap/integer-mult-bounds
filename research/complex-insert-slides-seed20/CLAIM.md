# Sprint claim — agent-06

No pinned sprint coordination issue exists in the repository (checked
2026-10-13; the only open issue is #650), so the claim is recorded here.

- **Track and seed:** 20–39 complex supplier; assignment seed 20 (fresh
  OS-random draw, `RandomNumberGenerator`, 2026-10-13).
- **Base commit:** `f567884aeb8851b6e794af1184119a3bfbe1e631`
  (origin/main). Branch `research/agent-06-complex-seed20`.
- **Object:** SW4's eight r2h compensation pre-reads on the pinned promoted
  P6k4 complex word (content sha256 `0390ec65dc4d47df1887aabdc2ec5b6ddea3cfc8e65582873fdfeba81d100073`),
  the complex word of the selected frontier ancestry
  (`research/complex-sw4-frame8`, PR741 checkpoint).
- **Question:** SW4 inserts each compensating pre-read `add(t,h,-c)` at one
  fixed position ("right after h's last existing pre-read"). Can any other
  placement of those eight pre-reads inside their exactness window (anywhere
  before the helper's copy gate, where `h = E_h`) lower the complex cost?
- **Method:** deterministic complete enumeration of all single slides, all
  pair slides, and all same-position tie-order swaps, up to positional
  equivalence (positions between consecutive gates touching the moved target
  or helper are identical). Every candidate is checked for the exact B-end
  state (mod p) and by the inherited frame refit/profile checks, and priced by
  the exact complex endpoint functional of the pinned moment engine.
- **Expected deliverable:** a scoped negative result with exact coverage
  counts, or a priced insertion schedule; in both cases a reproducible
  package with controls.
- **Expected finish:** 2026-10-13 (same session).

## Candidates considered (three, per the sprint brief)

1. **Chosen: insertion-slide census (this claim).** Named as uncovered by
   #775's scope list ("alternative insertion positions"), untouched by #815
   (frame-optimal for the *fixed* gate sequence) and #864 (frame reassignment
   of a fixed program), and disjoint from #876 (full pair/triple read-set
   exchanges) and seed 28's frame duals.
2. **Tail/early-cleanup membership changes on the selected X4 complex word.**
   Not chosen: every candidate needs a global owner/hosting repricing to
   value honestly, which does not fit a bounded session.
3. **Larger-group coupled partial read exchanges beyond #775's connected
   triples.** Not chosen: #775 and #876 already cover the main mass of this
   space and a second coverage sweep there would duplicate their method.

## Result (2026-10-13)

PR: https://github.com/CrocSwap/integer-mult-bounds/pull/910

The complete census (1,432 configurations: 56 singles, 1,372 pairs, 4
same-position tie-order swaps) finds **0 improving placements**: all 1,060
legal configurations have exactly the pinned paid profile
`{1:2548, 2:342, 3:438, 4:186, 5:56, 8:8}`, so the complex endpoint is
pinned at `0.0016634287545401745`; the 372 refused configurations are
frame-cap violations and all 1,432 preserve the exact B-end state. Scoped
negative result; the "alternative insertion positions" gap in #775's scope
list is now covered for singles, pairs and tie orders. Reproduce with
`python3 -B research/complex-insert-slides-seed20/verify.py`
(`PASS_INSERT_SLIDES_SEED20 singles=56 pairs=1372 swaps=4 legal=1060 improving=0 best_root=0.001663428754540`).

## Overlap statement

Concurrent work acknowledged and not duplicated: #775 (coupled partial read
exchanges on P6k4), #876 (full pair/triple exchanges; also the source of the
byte-identical vendored input word, content-pinned by the SW4 recipe),
#815 (LP/CP-SAT frame optimality of the fixed sequences), #864 (exact frame
duals for the selected X4 word). This claim changes gate *positions*, which
none of their scopes include.

# (G) does not imply (D) even for the full live family (no new κ)

**Status: exact finite counterexample to a proposed shortcut, plus scoped search evidence. No κ claim, no
construction, and no change to any proved rigidity result.**

[PR1650](https://github.com/CrocSwap/integer-mult-bounds/pull/1650) (head `d960f8a2`) checks
[PR1560](https://github.com/CrocSwap/integer-mult-bounds/pull/1560)'s frame-incidence criterion on every P105
unit. Its open question 1 asks whether a pivot frame that passes the counting conditions (W), nonempty blocks
and (G) always passes the rank condition (D), when the family is **all** live frames. If so, the P105 replay could
drop every rank computation. Two earlier counterexamples (PR1650's `control.g-without-d` and navinor's
[PR1649](https://github.com/CrocSwap/integer-mult-bounds/pull/1649)) use *sub-families* of the live frames, so they
leave the full-family question open.

## Result

**The implication fails for full live families once eight lines are deleted from P112.** `verify.py` checks two
exact fixtures. Fixture 1:

- Deleted set X = (3, 4, 8, 9, 107, 108, 117, 118), live set P112 \ X (104 lines, a P104 live set). Pivot frame
  F = (19, 25, 37, 47, 67, 82, 94, 115). All 784 live frames are used.
- Nonempty blocks, (W) and (G) hold.
- (D) fails at pivot k = 2. The incidence matrix of the live frames on I_2 (52 lines) has exact rank 44 over Q,
  one short of 52 − 7 = 45. The seven vectors h_2l are independent and lie in its kernel, as #1560 requires.
- An integer certificate needs no elimination: x = +1 on lines {30, 31, 40, 41}, −1 on {2, 5, 7, 10}. Every live
  frame is orthogonal to x, and x is outside the span of the h_2l.
- **Why it happens.** Every one of the 2025 E8 frames meets the two coordinate-half D4 subsystems equally:
  Da (the 12 lines supported on coordinates 0–3) and Db (coordinates 4–7). The intersection counts are (0,0),
  (1,1), (2,2) or (4,4). FRAME0 deletes 4 lines from each. X deletes 4 more from each, which leaves exactly the 4
  lines of each that are odd to F[2]. So x = 1(Da live) − 1(Db live) is orthogonal to every live frame. It is
  supported on I_2, and it is not a combination of the h_2l.
- **Locally minimal.** Restoring any one of the eight deleted lines makes the same pivot pass all four conditions.
  Each restored live set has 816 live frames.
- This unit is still rigid through other pivots. Running PR1650's criterion at every live frame (`unit()` in
  `search/allframes.py`; unregistered, reproduced independently by the Codex review): 674 pass all four
  conditions, 96 pass (W), blocks and (G) but fail (D), 4 fail (G) and 10 fail (W).

Fixture 2, X = (13, 18, 22, 27, 34, 35, 36, 37) with pivot (17, 25, 38, 52, 61, 75, 98, 116), has the same
pattern at k = 7: rank 44 on 52 lines. Its certificate is +1 on {111, 112, 113, 114} and −1 on {12, 19, 21, 28}.
These come from a non-coordinate pair of orthogonal 12-line systems, each containing 4 FRAME0 lines. `verify.py`
checks those properties and the frame identity; that the pair is an image of the coordinate halves under the FRAME0
stabiliser comes from `search/mech.py` and is not re-checked.

So the conditions in PR1650's question cannot replace (D) in general. Whether they can on P105 to P111
(|X| ≤ 7) is still open; the evidence below found no counterexample there.

## Search evidence (unregistered)

The scripts in `search/` import PR1650's `verify.py` (head `d960f8a2`), whose criterion is the one verified
above. Set `PR1650_PACKAGE` to that package's directory. Wall times are on a shared 10-core macOS host
(load 15–30).

| Search | Domain | Outcome |
|---|---|---|
| `walk.py --n 5000` (seeds 0–4999) | fix a random pivot F; delete random non-pivot lines one at a time, skipping any that break (W) or blocks at F; full criterion after each step | 176 walks reach a (G)-pass/(D)-fail step, first at 23–41 deletions. The first failure is usually (G). |
| `minimize.py` on those 176 | restore deleted lines greedily while the verdict stays (D)-fail | locally minimal sizes 8 (20 sets), 10 (48), 11–28 (the rest); **none below 8** |
| `mech.py` | all 7 D4⊕D4 splits that contain FRAME0 as 4+4 (closure of the coordinate splits under the stabiliser generators), all 1260 pivots disjoint from FRAME0, all k; X = the live split lines even to F[k] | sizes 4, 6, 8, 10. **(D) fails only at |X| = 8** (32256 cases). Every |X| = 4, 6 or 10 case passes or fails blocks. |
| `allframes.py random --size s --sample 100` | random X of size 8, 9 and 10 (seeds 8, 9, 10), every live frame | 189952 frames: none fails (G) or (D); only (W) fails |
| `allframes.py p107` | every live frame of all 1614 P107 units (1807 s wall, 8 processes) | 1393377 frames: 1386438 pass all four, 6936 fail (W), 3 fail blocks; **none fails (G) or (D)** |

The first two rows also give the fixtures: walk seeds 1023 and 1759 minimize to fixtures 1 and 2 (pivot indices
1765 and 1670 in PR1650's frame order).

## Reproduce

```sh
python3 -I -B research/full-family-g-without-d/verify.py        # about 3 s, standard library
python3 scripts/research_package.py --package research/full-family-g-without-d --check-only
python3.12 scripts/research_package.py --package research/full-family-g-without-d
```

Expected last line: `PASS_FULL_FAMILY_G_WITHOUT_D fixtures=2: ...`. `-O` is refused.

## Scope and limits

- The counterexamples are at |X| = 8, below P105. Nothing proved in PR1616 or PR1650 is affected, since those
  verify (D) explicitly. The P104 units are not claimed non-rigid; fixture 1's unit has 674 passing pivots.
- "(W) and blocks imply (G)" also fails for full families: the same unit has 4 frames that pass (W) and blocks but
  fail (G).
- No search covered every pivot of every P106 or P105 unit; see the open questions.
- #1560's Theorem 1 and Corollary 2 are cited, not re-derived. Ranks in the restore controls are mod-p lower bounds
  matched by the h_kl kernel upper bound, as in PR1650. The (D) failures are exact over Q.

## Open next questions

1. **Does the shortcut hold for |X| ≤ 7 (P105 to P111)?**
   - *Why it matters.* If it does, the P105 replay could drop the rank computations that take nearly all of its
     1200 s budget.
   - *First step.* Run an every-frame census on the 19295 P106 units (about 40 CPU-hours with PR1650's criterion at the P107 rate of 9 CPU-s per unit),
     then on a P105 sample. Or prove that a balanced pair of line sets inside I_k needs eight deletions.
   - *Blocker.* Compute, and no candidate lemma. The D4 mechanism needs exactly eight, and no mechanism with fewer
     appeared in the searches above.
2. **Classify the balanced line pairs.**
   - *Why it matters.* Fixture 1's kernel vector comes from the frame identity |Φ ∩ Da| = |Φ ∩ Db|. If every rank
     drop has this form, an exact counting test could replace (D) after all.
   - *First step.* Express the kernel vectors of the size-10 and size-11 minimized sets from `minimize.py` in
     sparse form, and check whether each is a difference of D4 indicators.
   - *Blocker.* None. Not started.

## Credit

- **an664 / Andrey Mas (PR1560):** the criterion and its conditions.
- **PR1650 / PR1616 (JosieElliston):** the implementation whose open question this answers. `verify.py` re-types
  its E8 model and condition tests.
- **navinor / Aaron Wang (PR1649):** the P107 sub-family counterexample and the full-family boundary question.
- **burntout76 / Brett Halligan (PR1212), themilkman216 (PR968), DreamingOfClouds (PR717):** the E-graph model
  and the floor this line verifies.

Prepared by JosieElliston with substantial assistance from Claude Opus 5.5 (Anthropic) via Claude Code, covering
the search, verifier and write-up. Apache-2.0.

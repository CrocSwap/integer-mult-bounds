# One shared call at three directions: which two-term parts can be finished, which removed

**No new κ.** A small negative result, checked by computer in exact arithmetic, in the frame game at 3 address
bits. Two arrays share one call. For one array's part of that call's output I ask two things: can one more call
finish it, and can the other array's last call have it removed? Among the two-term parts tested (two kinds, the
coefficients in the table) none is both. Nothing new is excluded: my earlier note (#4628) already proves
s ≥ 14W/5 there in Lean for the engine game, which excludes a 2 in 5. With one spare address bit no bound I know
excludes it, and there I only sampled 100 cases.

Jacob Sussman, 16 November 2026. Labels: **checked by computer** (an exact, finite check that `verify.py`
reruns), **argued by hand** (a written argument that no person has checked), **local only** (work of mine that is
not public and not in this package), **open** (not known).

## 1. What this is

At three directions the plain way costs 3 calls per array, so 6 calls for two arrays. Two arrays in 5 calls
("2 in 5") would save 1.66e-1 (a saving in the paid calls of one unit, not a κ). The arrangement studied here
gives each array one call of its own, then one call on a mix of the two arrays, then one more call each. The
simplest way for the shared call to pay off asks two things of each array's part of its output. That array's last
call must be able to **finish** the part into a single third-level term. The other array's last call, which reads
the same output, must be able to have the part **removed** from its own result. The table tests both for two-term
parts (sections 3 and 4 define the words). Each row has 10,752 cases.

| part | coefficient c | plain in disguise | tested | finishable | removable | both |
|---|---|---|---|---|---|---|
| kind A | 1 | 769 | 9,983 | 128 | 639 | **0** |
| kind A | −1 | 769 | 9,983 | 0 | 767 | **0** |
| kind A | 2 | 769 | 9,983 | 767 | 0 | **0** |
| kind A | 1/2 | 769 | 9,983 | 767 | 0 | **0** |
| kind B | 1 | 768 | 9,984 | 0 | 128 | **0** |
| kind B | −1 | 768 | 9,984 | 0 | 128 | **0** |
| kind B | 2 | 768 | 9,984 | 0 | 0 | **0** |

Status: checked by computer, in exact rational arithmetic. "Finishable" means by the last call alone. A free step
after that call finishes more parts, none of them removable (section 5). For kind A one rule fits every tested
case (section 5); I have no proof of it. The conflict between the two jobs was met before (section 2), and the
table is a result about the cases it lists, not about all programs (section 7).

## 2. What was known, and what this adds

- **The shape.** eumemic's negative results (#288) closed two arrays in five calls at block 3 in one normal form
  and left the general case open. Jose Manuel (#2108) proved that such a circuit needs at least four "mixing
  blocks" (their term). My note (#4628) excluded 2 in 5 at block 3 in the engine game.
- **The conflict was met before, on examples.** In October 2026 a thread on the hub ran into both halves of it,
  on a five-call preparation built on lee-phys's two-image prefix (#4688) after Yiyang's phase repair (#4710).
  The prefix is invertible with the combination U + 2V and has a kernel with U + V. JoyboyBrian showed that with
  the invertible coefficient no change of the fresh input's free feed repairs the preparation (#4751), and that
  with coefficient 1 an exact free decoder leaves no contamination from the fresh owner but only a partial
  channel (#4797), whose rank Nick Petalas (#4825) and Dugongue (#4885) then found. Reading these as one conflict
  is my reading, not a statement of those notes, and they keep every phase (the engine game). My repository
  argues the same conflict by hand for a symmetric 2 in 7 at block 4 (a filter 1 + a·u that must be invertible
  while a = ±1 is forced), and ran the arrangement of section 1 at the excluded shapes 2 in 5 and 2 in 6 as a
  negative control.
- **The same finite geometry is on the hub.** Dugongue's native ports (#4743) include a census of it: the group
  of order 10,752 that keeps the raw frame, the 14 frames next to it, and their split 1 + 1 + 12 under a
  stabiliser of order 768. That note uses this "symplectic quotient" as a search coordinate system and says that
  alone it omits phases. zxv's note on cache reuse (#5283) defines frames the same way. The frame game is that
  quotient.
- **Added here** (checked by computer): the table for the two kinds of two-term part of section 4 at 3 address
  bits, over all 10,752 free elements, and a rule with a coefficient that describes kind A.
- **Nearby.** Nick Petalas's open note (#7551) proves a cut ceiling on the same graph. Dugongue's atlas (#5803)
  and the five-array shared port of Chris R (#4856) and JoyboyBrian (#5491) study other shared calls. The one
  unit claimed at three directions (#4813, 5 in 14) was withdrawn by its author on 23 October 2026; its folder on
  main still shows the original text, and this note says nothing on 5 in 14.

## 3. The game, in plain words

- **The engine game** is that of my note #4628, which defines array, call, free steps, width, unit, "W in s" and
  the plain way. An array holds 2^m complex numbers, addressed by m address bits; a paid call applies OpenAI's
  2-point kernel along one direction; shifts, phases, address maps and rational mixing of arrays are free. For a
  target of k directions the plain way costs k calls per array, and a unit with W arrays and s calls saves
  ln(kW/s)/ln k. Block m means m address bits and a target of all m directions.
- **A spare address bit.** An address has four bits and the target applies only three of the four directions. The
  program may use the fourth bit. My repository calls this a rank-3 target with a spare row.
- **Term, frame, level.** An array's content is a sum of terms. Each term is one input passed through one fixed
  product of steps, times a number. A term's frame is where it stands up to free steps. The frames are the
  Lagrangian subspaces of F_2^(2m), 135 of them at m = 3. Two frames are adjacent when they meet in dimension
  m − 1. This is the dual polar graph (DSp(2m, 2) in eumemic's #288, the binary symplectic dual-polar graph in
  Nick Petalas's #7551, the frame graph in my repository). A term's level is the distance of its frame from the
  raw frame, where every input starts. A finished target of k directions is at level k.
- **Frame game.** The same game with the Pauli part (bit flips, sign flips, the scalar i) dropped. A term is then
  an element of the symplectic group Sp(2m, 2), acting on labels (x, z) in F_2^m × F_2^m. The free elements are
  those that keep the raw frame L = {x = 0}; there are 10,752 at m = 3. A paid call is a transvection
  t_u(v) = v + ⟨v, u⟩u with u outside L; there are 56 at m = 3. The frame of a term g is g⁻¹(L). Products act
  from right to left: in t_w·γ·D0 the call D0 is applied first.

## 4. The question

Take one input. Its raw term is 1, and its first call D0 gives the term D0, at level 1. The shared call t_w then
acts on an array in which this input has D0 and one more term. Its part of the shared output is

- **kind A:** y = t_w·(1 + c·γ)·D0, when the extra term going in is a free image of the first-call term;
- **kind B:** y = t_w·(D0 + c·γ), when the extra term going in is a free image of the raw input.

Here γ is a free element, c is a rational number, and a free image of a term is a free element applied to it on
the left. M = t_w·D0 is the plain middle term, at level 2, and E is the other term of y. A "free combination" is
a sum of rational multiples of free elements, applied on the left. If the first call reads the raw input alone,
these are all the two-term parts with a level-2 term, up to a scalar, a free step on the left and symmetry, and
one first call and one shared call are enough (argued by hand). The docstring of `symmetries` in `verify.py` has
the map; `--part symmetry` checks its counts, a second shared call with the same table, and 368 cases of the map.

- **Finishable (by the call alone):** for some call t that raises M to level 3, the term t·M is a free
  combination of 1, D0 and y, plus t applied to a free combination of 1, D0 and y. Free steps may prepare the
  call's input and may add earlier arrays to its output. None is applied to the output itself (see section 5).
- **Removable:** for some call t that could be the other array's last call, t·y is a free combination of 1, D0
  and y, plus t applied to free combinations of 1 and D0 and to free images p·y of the part, with p a free
  element other than 1. A call that reads the shared output can then have this input's part cancelled from its
  result. A call could be the other array's last call when t·t_w is at level 2, which holds for 48 of the 56
  calls: only then can it raise that array's middle term to level 3 (argued by hand).
- **Plain in disguise:** y has one term or none, or E is a free image of 1 or of D0. These cases are set aside.

## 5. The table and the rule

**Kind A.** Compare the frames of the two terms M and E. The rule fits every tested case; it is not proved.

| frames of M and E | cases | finishable by the call alone | removable |
|---|---|---|---|
| the same: E = g·M with g free, so y = (1 + c·g)·M | 767 | exactly when 1 + c·g is invertible | exactly when it is not |
| adjacent | 768 | never | never |
| further apart | 8,448 | never | never |

"Invertible" means that another free combination undoes it. For g of order n the test is (−c)^n ≠ 1. With c = 1
the 128 cases with g of order 3 are finishable, and the 639 with g of order 2, 4 or 6 are removable. So on one
frame the part is either undone and finished like the plain term, or killed by a free step before any call reads
it (argued by hand); in the second case every one of the 52 calls tried removes it. The rule matches all 9,983
tested cases for each of c = 1, −1, 2 and 1/2 (checked by computer). I did not run other c. Two pieces are
standard: an invertible multiple of M is finished like M, and 1 + c·g is invertible exactly when (−c)^n ≠ 1.

Two things that the columns leave out (checked by computer):

- **Adjacent frames, and calls that cannot be a last call.** Let the removing call be any call that does not
  simply undo the shared call. Then the 768 adjacent-frame parts are removable too when c = ±1, which gives 1,407
  parts for c = 1 and 1,535 for c = −1. Each of them is removed by the same four calls, those with t·t_w at
  level 1, and none of the four can be anybody's last call.
- **A free step after the last call.** For a part with frames further apart, a call t that raises M to level 3
  may put both terms on one frame: t·E = h·t·M with h free. Then t·y = (1 + c·h)·t·M, and when 1 + c·h is
  invertible a free step applied to the call's output gives t·M alone. This finishes 128 more parts for c = 1 (h
  of order 3), 512 for c = 2 and for c = 1/2, and none for c = −1 (`--part poststep`). None of them is removable.
  An AI reviewer's own program found no other part that such a step finishes, and none that is then both. That
  program, and its argument that the list is complete, are local only.

**Kind B.** No part is finishable by the call alone, for c = 1, −1 and 2. For c = 1 and for c = −1 the same 128
parts are removable, and for c = 2 none is. The 128 are exactly the parts for which some call carries M onto the
frame of E and E onto the frame of M (checked by computer on all 9,984 cases; no proof). All of them sit among
the 1,536 parts whose two terms are on adjacent frames. In kind A the same test picks out exactly the 768
adjacent-frame parts.

**One spare address bit: a sample only.** With 4 address bits and the same target there are 20,643,840 free
elements, and I did not run them all. On a seeded sample of 100 kind A parts with c = 1 (20 on the same frame
with g of even order, 20 with g of odd order, 20 on adjacent frames, 40 further apart) the rule is right on every
case and none is both (checked by computer). The sample is drawn by random walks, not uniformly. It is no proof.

## 6. How to re-check

Run `python3 -B research/complex-m3-shared-call-finish-or-remove/verify.py --part controls`, then the same with
`main`, `poststep`, `symmetry`, `coefficients` and `spare`. Standard library only; no file is read or written.
With Python 3.12 on an Apple M4 the six parts take about 3, 38, 4, 42, 85 and 22 seconds and under 30 MB each,
and each ends with a line that starts `PASS_COMPLEX_M3_SHARED_CALL_`. The program checks with assert statements
and refuses to run under `-O`. `VERIFY.json` says what each part checks, the controls included. `--part full`,
which is not listed there, runs every case one at a time with no symmetry reduction, in about 4 minutes (or in
four quarters, `--quarter 0` to `--quarter 3`), and gives the same table.

## 7. Limits of this work

- **The frame game only.** My repository argues by hand that every engine unit gives a frame-game program with
  the same calls, and that every frame-game program completes to an engine unit (stated there for targets of all
  m directions). I have not turned this table into a statement about engine-game parts, where two terms that
  differ by a Pauli are different terms.
- **Two terms, one input at a time, one arrangement.** A part with three or more terms is not covered. The first
  call reads the raw input alone: a first call on a free combination (1 + c·a)·x of the raw input x gives a third
  kind of part, M + c·M·a, which is not in the table. The other array's part of the shared output is ignored,
  and each last call is treated on its own. A program that cancels what one last call leaves over against the
  output of the other is not covered. Nor is a shared first or last call, or two shared calls.
- **A finite check, not a theorem about all programs.** Complete at 3 address bits and sampled at 4, for the
  coefficients in the table only. With a free step after the last call, the list of finished parts is complete
  only by a reviewer's local program, and kind B was not run that way here. The table is a result about the
  cases it lists.
- **Fixed widths are not studied.** Terms are treated as formal. alephnan's threshold T(3) = 10 (#6714) says from
  which width distinct three-qubit Clifford terms are independent.
- **No person has checked this.**

## Open next questions

1. **Is there a 2 in 5 at three directions with one spare address bit (a saving of 1.66e-1)?** In the engine game
   it is the smallest shape at three directions (fewest arrays, fewest calls) that no bound I know excludes. My
   repository has listed it as open since 20 October 2026: the best lower bound there is 2.4883 calls per array
   (checked by computer, by one family of programs), and a 2 in 5 uses 2.5. I know of no search of this exact
   case, and I have no evidence either way. First step: the same arrangement at 4 address bits with every
   coefficient left free and the two last outputs read together, starting with the parts for which something
   happened here. Blocked by nothing but size: 20,643,840 free elements before symmetry.
2. **Is the kind A rule a theorem at every number of address bits?** A proof by hand would replace the sample at
   4 bits. First step: show that a part whose two terms sit on different frames is never finishable by the call
   alone. Blocked by nothing.
3. **Why are exactly those 128 kind B parts removable?** First step: prove that a call which carries M onto the
   frame of E and E onto the frame of M removes the part when c = ±1. Blocked by nothing.

## How this was found (a remark on method, not evidence; local only)

The table came out of nine runs in which AI agents carried ideas for sharing work into this game, eight of them
from other fields (the pull request names the fields and their originators). None gave a program that beats the
plain way at three directions, and six arrived separately at the arrangement of section 1. An earlier run had
given three totals (10,752 cases, 128 finishable, 1,407 removable under the wider test of section 5) and no rule.
Before looking at which cases were removable, the AI agent I work with wrote its guess for the rule in a dated
file, with a confidence of 75 %, and the comparison matched case by case. That afternoon it wrote eight such
guesses, all about this one table; seven were right, one of them on a sample only. Review by other AI agents then
asked two things that no guess had asked: could the removing call be a last call at all, and may a free step
follow the last call? Both changed the table. A guess written down first tested the agent's sense of the answer,
not whether the question was the right one. Only a file time dates the guess files. The nearest thing I found on
the hub is zxv's frozen forecast (#5283).

## AI assistance and credit

Substantial AI assistance: I did this work with the help of AI agents (Anthropic's Claude). The programs, the
searches, the arguments and the text were written by the agents under my direction. Two AI reviewers rebuilt the
counts of an earlier form of this table from the definitions with their own programs, and between them found the
two corrections of section 5; `verify.py` then reproduced the corrected counts (local only: the reviewers'
programs are not in this package). No independent human review of this package is claimed.

Credit on the hub: eumemic (#288); Jose Manuel (#2108); lee-phys (#4688); Yiyang (#4710); Dugongue (#4743, #4885
and #5803); JoyboyBrian (#4751, #4797, #5491); Nick Petalas (#4825, #7551); Chris R (#4856); alephnan (#6714);
zxv (#5283). OpenAI for the cost model, the call and its 2-point kernel. Apache-2.0.

## Sources

`SOURCES.json` has the hub base commit (`e54523517d`, main, 10 November 2026) and its pins. #288 was closed
without merge; its text is on main at `research/abelian-cayley-metric-scope/sources/pr288-README.md`. #7551 is
open and is cited at its head `9aec48e750`, not pinned. My repository is
https://github.com/jacobalansussman/wht-power-saving-lean at commit `0788bc6568` (3 November 2026):
`research/frame-packing-two-arrays/` (the frame game in "Words used here" and, for its symplectic form, in
`proofs/frame-game-sandwich.md`; engine units and frame-game programs; the negative control),
`research/moonshot-block4-block5/` (the 2 in 7 dilemma) and `research/block-bounds-and-new-rules/`, section 4.2
(spare rows, the 2.4883 lower bound, the open case; its table of open cases says "4 spare rows", meaning 4 rows
in all, one of them spare). Nothing is copied from another repository: `verify.py` rebuilds the table each run.

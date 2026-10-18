# Reframing does not legalize two-writer helper-star absorption

**Scoped interface obstruction under the full reframing escape class; no new
kappa.** The selected result, the selected bit supplier and `upstream/` are
unchanged; the bit side does not bind.

On the pinned 11,500-ADD PR1062 R439 word, omit one terminal helper-star
restoration `a ^= b` and toggle one donor in each of two existing phase-A
writes of `a` before its first read. Adam Gall's
[PR #1913](https://github.com/CrocSwap/integer-mult-bounds/pull/1913) found all
314 exact arbitrary-dirty completions of this class (52 with one fewer scalar
ADD) and rejected every one **at the unchanged gate frames**, explicitly leaving
changed gate frames and itineraries open. This package closes that escape for
the useful class: with gate frames free to change (arbitrary monotone
reframing, including shrinking below the original frames), **all 52
scalar-saving completions are still inadmissible**, each with an exact rational
leakage witness: a dirty target's forced carried span strictly exceeds its
pinned rank-7 `t`-perp final frame. Of the 262 cost-increasing completions, 260
are excluded the same way; the 2 survivors cost one ADD more than the source
word. Thus no scalar-saving completion can be legalized by reframing. This
does not exclude a better recursive moment from larger joins on a survivor;
that separate optimization remains open below.

## The forced-carry closure

The law is the pinned eumemic `xcheck_p.py` Part F nested-frame law: every
register starts at its start frame (sources at their own line, targets and
helpers at frame 0); before each gate every operand climbs to the gate's frame,
nested with a strict increase of dimension; final frames are pinned (sources
and helpers at the full frame, target `t` at `t`-perp, rank seven).

**Lemma (least forced frame assignment).** Fix any scalar edit of the word
(gate contents in `D,A,B,C` order; start and final frames unchanged). Process
the gates in order and set each gate frame to the span union of the current
frames of its touched registers, starting from the fixed start frames. Call the
result the *forced-carry closure*.

1. The closure is the componentwise least legal frame assignment: every legal
   reframing's register currents contain the closure's register currents at
   every point, by induction over the gates (a gate frame must contain all its
   operands' current frames).
2. If the closure reaches a final step where a register's forced carried span
   is not contained in its pinned final frame, then **no** reframing is legal:
   the offending direction sits in every reframing's carried span, which must
   end inside the same final frame.
3. If the closure is final-clean, the closure itself is an explicit legal
   reframing.

So the closure decides reframing-admissibility exactly, and its witnesses are
domain-free: they do not depend on any search over frame choices. Shrinking
gate frames below their original values is granted, which is the most favorable
reading of PR #1913's open question; the exclusion a fortiori holds in
grow-only or source-label-determined frame models.

## Domain and result

The domain is re-derived independently here and matches PR #1913 exactly:
236 terminal star edges, 414 eligible writer pairs, 549 first donors per pair
(227,286 trials, unique exact second donor), 314 exact completions.

| quantity | count |
|---|---:|
| exact arbitrary-dirty completions | 314 |
| completions with one fewer scalar ADD | 52 |
| completions with one more scalar ADD | 262 |
| legal at fixed gate frames (PR #1913) | 0 |
| scalar-saving completions legal under arbitrary monotone reframing | **0 / 52** |
| all completions excluded under reframing | 312 / 314 |
| closure-legal completions (both cost +1 ADD) | 2 |

Every completion's exact 661-column arbitrary-dirty boundary is replayed in
both orientations through the literal COPY/ERASE stream and passes (the scalar
criterion of PR #1913 is satisfied; the obstruction is purely geometric). The
witnesses all have the same shape: the added donor's forced join at the edited
gate spreads through later gates to a dirty target in 111–221, whose pinned
`t`-perp final frame has rank seven and cannot contain the leaked direction
(rank becomes eight). Examples (register, leaked labels, rank final, rank
joined):

| omitted restoration | toggles | witness |
|---|---|---|
| `231 ^= 459` | A[9] adds `109`; A[527] removes `459` | target 111 leaks `109`: 7 -> 8 |
| `234 ^= 241` | A[12] adds `9`; A[247] removes `241` | target 112 leaks `9`: 7 -> 8 |
| `506 ^= 374` | A[288] removes `374`; A[1033] adds `69` | target 116 leaks `30,46,54`: 7 -> 8 |
| `482 ^= 540` | A[786] removes `540`; A[787] adds `417` | target 145 leaks `5`: 7 -> 8 |

The third row is the instructive one: it moves Sagar Thakrar's known legal
single-writer absorption (`506 ^= 374` absorbed by A[288]) onto the *other*
writer. The one-writer move is legal; splitting the same compensation across
two writers forces the join into a rank-7 final and dies.

All 314 rows with complete witnesses are in
[CERTIFICATE.json](CERTIFICATE.json).

The two closure-legal completions share the omitted restoration `444 ^= 470`
and *add* rather than remove: donor `77` at A[1993] and donor `470` at A[1994]
(respectively A[2038]), both toggles being insertions. Their forced joins
spread but leak outside no pinned final, and the closure's scatter frames for
the nine retained totals equal the pinned rank-7 copy frames. They cost
**+1 ADD** (11,501 versus 11,500), and their least legal reframing's paid
histogram is `{1: 1494, 2: 1308, 3: 46, 4: 45, 5: 103, 6: 10, 7: 18}` (rank
mass 5,129, 3,024 children versus the source word's 2,920): more children at
smaller rank, so a worse moment bill at every `0 < p < 1` by concavity. They
are interface evidence that the closure is not vacuous, not savings.

## Boundary contract and paid profile

The acceptance gate asks for a full boundary contract and paid profile, not
scalar counts alone.

- **Boundary.** All 314 completions and the positive fixture pass the exact
  661-column arbitrary-dirty boundary in both orientations through the literal
  COPY/ERASE stream: every source holds `e_s`, every target holds
  `e_{y_t} + e_{x_t}`, every helper holds `e_h`.
- **Paid profile.** No excluded completion has a legal frame assignment, so
  there is no paid histogram to bill; billing an excluded completion is refused
  by the verifier. The two closure-legal completions are billed above. The
  pinned source word's complete profile is
  `{1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}`, rank mass **5,129**,
  with ADDs 11,500 and positive bounds F = 25,717, B = 5,911,840 (strict
  104/192-bit inequalities pass).
- **The one legal saving (predecessor's).** Sagar Thakrar / PR #1868's
  single-writer absorption `506 ^= 374` with A[288] donors `[374] -> [69]`
  passes both closures, saves one ADD (11,499) and keeps the paid profile
  identical. It is reproduced here only as a positive fixture; the saving is
  PR #1868's, not new.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -I -O -B research/r439-two-writer-reframing/verify.py
python3.12 -I -O -B research/r439-two-writer-reframing/test_verify.py
python3.12 scripts/research_package.py --package research/r439-two-writer-reframing
```

Expected marker:

```text
PASS_R439_TWO_WRITER_REFRAMING pairs=414 trials=227286 exact=314 saving=52 saving_excluded=52 reframing_excluded=312 legal=2 columns=661 controls=10 no_new_kappa
```

Default replay is read-only and compares every certificate field;
`--write` regenerates `CERTIFICATE.json`. Both pinned inputs are checked by
SHA-256; no predecessor executable is imported. Ten controls: baseline
legality and pinned profile, domain counts, all-314 boundary replays, the 312
witnessed reframing exclusions, the PR #1868 positive fixture, a removal-only
edit that is geometrically legal but boundary-rejecting (separating the two
checks), a wrong-substitute boundary rejection, refusal to bill an excluded
completion, source-corruption rejection and a star-domain mutation rejection.

## Scope and limits

- **Class.** Two writers, one donor toggle per writer, one omitted terminal
  star restoration, on the pinned PR1062 word. Multi-donor sets per writer
  (PR #1937's linear system) are not replayed under free frames here; the
  closure decides that class too and is left as the recorded next question.
  Post-read propagation and compensation, changed scalars, rebuilt A/B/C and
  other words are outside this scope, as in PR #1913.
- **Claim type.** A finite exact exclusion with machine-checked witnesses plus
  a decision lemma, not a theorem about arbitrary words and not a supplier
  admission. No new kappa, no changed selected record.
- **Not run.** Native 5/9/11-stage C++/Boost replay, hosted emission/invoice,
  all-size compiler, precision/tape, analytic transfer, Lean. Physical
  realization of any reframing is not claimed; the exclusion is at the word
  level of the inherited nested-frame law.
- **The lemma's model.** Gate frames are free rational frames with pinned
  starts and finals and the strict nested-climb law. Models with frame descent,
  reset, clean allocation, free role permutation or new transport are outside,
  as in the predecessor packages.

## Open next questions

1. **Multi-donor splits at free frames.** Does the forced-carry closure also
   exclude PR #1937's two-writer multi-donor splits once gate frames may
   change, or does a dual-witness-free closure yield a priced legal
   reframing? *First step:* replay its five solved same-path edges and its
   dual-witness targets through `closure_walk`. *Why it matters:* it decides
   the free-frame version of the only surviving split-restoration class.
   *Blocker:* none technical; bounded extension of this verifier.
2. **Cheapest legal reframing.** When a closure is legal, is its paid profile
   minimal? Larger joins can merge rank increments and lower the moment bill.
   *First step:* on the PR #1868 fixture, enumerate coalescing joins and
   compare paid histograms. *Blocker:* an optimization over legal reframings,
   unneeded for the excluded domain here.

## Credit and disclosure

- **Adam Gall / [PR #1913](https://github.com/CrocSwap/integer-mult-bounds/pull/1913):**
  the complete two-writer single-donor domain and its fixed-frame exclusion;
  its stated open question (changed gate frames/itineraries) is the object of
  this package.
- **Aaron Wang / [PR #1937](https://github.com/CrocSwap/integer-mult-bounds/pull/1937):**
  the complete fixed-gate multi-donor linear system; its fixed-gate premise is
  the changed one here.
- **Sagar Thakrar / [PR #1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868):**
  the twisted helper contract H2-tw/H4-tw/K-tw, the single-writer absorption
  (positive fixture, whose one-ADD saving is his), and the multi-gate-split
  question.
- **woklerx / [PR #1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194):**
  the semantic-D replacement contract H2-sem; **Arham Tahir / PR #1311, #1580,
  #1592:** its application and terminal-restoration obstructions.
- **Word lineage:** Sagar Thakrar / PR #1062 (the pinned word), Sricharan
  Vagvala / PR #967 (helper stars), Gareth Davidson / PR #915/#926/#1122,
  Ross Richardson / PR #923, Aaron Wang / PR #1015, DreamingOfClouds / PR #589,
  eumemic / PR #555/#543 and `xcheck_p.py`, Zhihao Chen / PR #425.
- **Pair-collision check:** discussions 1317 and 1166 through 2026-10-15
  07:52Z and `scripts/find_overlap.py` on the refined terms (612 open PRs,
  1138 discussion records, complete pagination) found no competing claim on
  reframed two-writer absorption.

Prepared by **Aaron Wang** with substantial AI assistance from opencode; no
independent human review or proof-assistant verification is claimed. New
material is Apache-2.0; pinned inputs keep their original notices.

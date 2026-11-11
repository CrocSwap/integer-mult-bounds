# Consecutive halves miss the five-map g=13, q=8 paired star

**Proof, under a stated hypothesis.** In the paired-star contract, if the
two full calls of every stage are adjacent, then a successful word needs at
least `ceil(g/2)` thin maps. The full projectors need not commute, the field
may be any characteristic-2 field, and the thin maps may have any rank.

At g = 13 that bound is 7. Five thin maps are impossible inside this
schedule, including five maps of rank q = 8. The same count shows that five
adjacent-halves maps are also too few at g = 31. A word that places any
call between the two halves of a stage is outside the hypothesis and remains
open at both profiles.

The predecessor commuting theorem already gave this count when all full
projectors commute. Commutation forces the off-diagonal block B to zero.
The argument in `PROOF.md` keeps a legal nonzero B and drops commutation,
and it requires the halves to be adjacent in exchange. The sharp word from
`research/coupled31-chronology/COMMUTING.md` still meets the count for every
legal B.

Selected κ stays `781451/250000000`. This is a schedule obstruction, not a
supplier and not a change to the selected frontier.

## Replay

From the repository root, with Python 3.12:

```sh
python3 -B scripts/research_package.py --package research/paired-star-g13-q8-five-map
```

The registered command reruns `verify.py`. The receipt is
`PASS_PAIRED_STAR_G13_Q8_CONSECUTIVE`. The checks raise on failure, so
`python3 -O -B` does not strip them. No third-party packages are required.

The g ≤ 5 endpoint grids are complete polynomial checks: each stage variable
has degree at most 2, and the three values `{2,4,8}` separate that degree.
The g = 13 evaluation uses two field points as an interpreter check against
the Laurent formula. The general identity is the written argument.

## Scope

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, canonical CrocSwap
`main`. Card `joint-query-controller`, scope refined to the unconstructed
g = 13, q = 8 profile in discussion #5593 and in the open questions of
PR #5747. The actual result is the consecutive-halves case of that profile.

Overlap used for this package:

- PR #5747, merged, is the contract, the rank floor, and the commuting
  map-count. Its open question asks for a noncommuting word at g = 13,
  q = 8 and at g = 31, q = 26.
- Open PR #6922 is the F_2 three-leaf one-thin census. It leaves both
  larger profiles open.
- Open PR #6940 is the F_2 three-leaf two-map rank bound. It also leaves
  both larger profiles open and says the three-leaf result does not lift.

Those three-leaf statements fix g = 3, block size 2, and entries in F_2.
They are not a proof at g = 13 or q = 8. This package does not extend them
by a failed search. GitHub search is not a full-text proof that no other
note mentions the same schedule hypothesis.

This is one checked lower bound. It does not open another construction
round, and it does not admit a supplier. The family expansion gate is
unchanged.

## Open next questions

- Does an interleaved word meet the g = 13, q = 8 endpoint with five
  rank-q thin maps when full projectors need not commute? The smallest
  useful step is one explicit pattern that separates at least one stage's
  halves, the constant thin maps forced by setting every D_j = 1, and a
  two-point check of the normalized coefficient before any native bill.
  The consecutive-halves theorem does not apply to that pattern, and no
  such word is supplied here.
- The interleaved g = 31, q = 26 profile is a different question. The
  adjacent-halves corollary covers only that subcase. It is not
  investigated here.
- A uniform proof that one thin map fails at g = 3 for every q, as opposed
  to the F_2 block-size-2 census in PR #6922, would say whether the
  smallest interleaved escape exists. That census does not lift.

Native transport, the physical bill, and κ stay out of scope even if an
interleaved algebraic word is found.

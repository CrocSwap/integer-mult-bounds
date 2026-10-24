# No further owned-helper relation subspace after #5421 (BIT) and #5383 (complex)

**Negative result; no new κ and no new BIT saving.**

[PR #5421](https://github.com/CrocSwap/integer-mult-bounds/pull/5421) (Ali Romman) owns nine helper
relations on the reverse PR589 BIT word. Each relation zeroes one COPY job (rank 7) and one rank-1 move,
and costs one rank-8 helper target. Its README says that a further BIT gain needs a new relation space.
[PR #5428](https://github.com/CrocSwap/integer-mult-bounds/pull/5428) (target 6) proposes systematic
relation-space selection for the same purpose.

This package answers the question exactly for that word. Any number of additional relations, in any
combination, removes at most 7.5 units of paid rank mass per relation dimension. A dimension costs one
rank-8 target. Every relation subspace therefore loses at least `8^t - 7.5 = 0.4424` raw moment per
local call at `C = 0.00347207`. The bound holds for every `C < 0.031`.

## Model

The model is #5421's. Replay the source records in reverse over GF(2) with 661 entry symbols. A paid job
is a MOVE of rank `r > 0` or a COPY entrance (rank 7). A relation subspace `V` consists of entry forms
supported on full-entrance fields, with helper pivots. A job becomes free exactly when the binary row of
its moved value lies in `V`. The raw moment changes per local call by

```text
sum over removed jobs of r^t  -  8^t dim V,      t = 1 - C,
```

and the controller multiplies this by its eighteen full calls. The certificate ignores the frame and pivot
conditions, so it bounds legal subspaces as well.

## Certificate

Let `E'` be the multiset of job rows, with each row repeated `rank` times, and let `w(V)` be the paid mass
with rows in `V`. By the matroid union theorem, if `m` copies of `E'` split into `p` linearly independent
sets, then `m w(V) <= p dim V` for every subspace `V`. Edmonds' augmenting paths make the split exact.
A row in a tight subspace (`w = 8 dim`) is one for which an extra copy cannot be inserted.

| Check | Result |
|---|---|
| Source paid jobs / jobs with a legal row | 2,920 / 2,384 (1,773 distinct rows) |
| Source word, `E'` into 8 sets | splits, so `max_V (w - 8 dim) = 0` |
| Source word, tight subspaces | exactly nine, each COPY H7 + MOVE H1: the #5421 relations |
| Modulo those nine, `E'` into 8 sets | splits; no tight row, so `w(V) < 8 dim V` |
| Modulo those nine, `2E'` into 15 sets | splits, so `w(V) <= 7.5 dim V` for all `V` |
| Control: source `2E'` into 15 sets | fails, as required |
| Control: extra rank-1 job on a COPY row | breaks the 8-split, as required |

Since `r^t <= r` for `r >= 1`, the moment change is at most `(7.5 - 8^t) dim V < 0`.
[RESULT.json](RESULT.json) holds the rebuilt numbers.

## Part 2: the complex word

The binding complex side uses Cao Yifan's #4610 word with the eight owned relations of
[PR #5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383) (Ali Romman), carried through #5392,
#5398 and the selected #5413 caller. The #5413 caller adds 144 paid and 144 target rank-8 jobs, which
cancel rank by rank. [complex.py](complex.py) replays the backward word exactly over Q with warp words.
The model is #5377/#5383's: 326 cold helpers carry rank-9 targets. A climb is freed when its row lies
in V. A centre job is freed when its row minus an earlier same-frame snapshot lies in V.

| Check | Result |
|---|---|
| Backward paid profile | `{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}` |
| Candidates | 163 pure-cold climb rows, 56 centre snapshot options |
| #5383's eight relations | free all eight centres and exactly eight rank-1 zero-site climbs |
| Remaining climb rows modulo them | 155 rows, linearly independent over Q, rank mass at most 3 |

Because the remaining rows are independent, any further subspace V contains at most `dim V` of them.
It frees at most `3 dim V` of paid mass, against `9^t dim V = 8.9403 dim V` of lost targets. Every
extension of #5383's relations therefore loses at least 5.94 raw moment per local call at the
selected `C = 0.003027288235`. [RESULT-COMPLEX.json](RESULT-COMPLEX.json) holds the rebuild. The result
does not cover a relation set that omits #5383's eight relations. Snapshot options are alternatives for
one centre, so they are not single matroid elements. The centre-exchange cap of
[owned-relation-exhaustion](../owned-relation-exhaustion/README.md) already limits that family, and all
eight centres are already used.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/bit-relation-subspaces
python3.12 -I -B research/bit-relation-subspaces/verify.py
python3.12 -I -B research/bit-relation-subspaces/complex.py
python3.12 -I -B research/bit-relation-subspaces/test_verify.py
```

The verifier uses only the standard library and finishes in about half a minute. It prints
`PASS_BIT_RELATION_SUBSPACES_NO_FURTHER_GAIN_AFTER_5421`. Part 2 prints
`PASS_COMPLEX_RELATION_SUBSPACES_NO_FURTHER_GAIN_AFTER_5383` in a few seconds. The controls print
`PASS_BIT_RELATION_SUBSPACES_CONTROLS`.

## Scope

The result fixes the PR589 operation order, helper inventory and job set. It does not cover a changed
chronology, a different BIT word or new helpers. Snapshot replacement in the style of PR #5377 applies
only to owned fields. On this word the only owned paid jobs are the nine COPY jobs, which #5421 already
removes. The nine relations come from the source word itself, so #5421 is not a live input.

## Open next questions

- Does a changed chronological order or a different BIT word admit a relation subspace of density
  above `8^t`? First run the same 8- and 15-part splits on its job rows. No frozen changed BIT word with an
  admitted invoice is available yet.
- Can a complex relation set that omits #5383's eight relations beat them? First enumerate one
  snapshot option per centre and run the same independence test on each choice.

## Credit

DreamingOfClouds (PR #589) and eumemic (PR #555) supplied the source word and port construction.
Cao Yifan supplied the #4610 word. Ali Romman's PR #5421, PR #5377 and PR #5383 supplied the owned-helper relation method that this package
generalises. zxv's PR #5428 named relation-space selection as a target. Prepared by Mark (Matarener)
with substantial Claude Code assistance. New work is Apache-2.0.

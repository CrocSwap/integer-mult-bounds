# Shared length two cannot write the S3 transposition

**Scoped written proof with exact finite corroboration. No new kappa.**
The selected record is unchanged.

## Result

In the paid S3 alphabet of
[#4351](../s3-diagonal-rank-screen/README.md), with labels
`s = (1 2)` and `t = (2 3)` and cost equal to reduced generator length, no
shared word of total cost at most **two** writes the transposition
`(1 3)` on any register. This holds for every number of scratch registers.

The proof is the word-metric inequality: a register receives a product of a
subsequence of the paid letters, so its reduced length is at most the total
paid cost. Since `(1 3)` has length three, cost two cannot produce it. The
bound is sharp: the coordinate word `s, t, s` has cost three and writes
`(1 3)`, and the shared four-call word

```text
(s, {0,1}), (t, {0}), (s, {0}), (s, {1})
```

writes `(1 3)` on register 0 and restores register 1 at total cost four.

This answers the open question in #4351: a scratch register does not lower the
length-three floor for `(1 3)`. It does not show that every register model is
exhausted.

## Model and scope

A paid shared call is a pair `(g, M)`: one alphabet element `g` written to
every register in the nonempty mask `M`, charged `ell(g)`. A register's
induced element is the ordered product over the calls that write it. This is
the natural shared-letter model for the #4351 alphabet.

The result is conditional on that cost model. If one paid call may write
*different* alphabet elements to different registers at a single unit cost,
then the induced element is no longer a subsequence product of the charged
letters and the norm bound does not apply. That alternative model is not
addressed here.

No native source generation, hosting, precision, transfer to the selected
rational-frame supplier, new kappa, register-model escape or complete
multiplication theorem is claimed. The selected frontier and its five
assumptions are unchanged.

## Evidence

The standalone verifier imports no predecessor executable and reads no
predecessor file. It rebuilds the S3 multiplication table, inverses and the
reduced length table, checks subadditivity on all 36 ordered pairs, and
enumerates every cost-at-most-two shared word on two and on three registers:
272 words and 768 register evaluations. No induced element is `(1 3)`. The
cost-three attainment, the shared cost-four scratch restoration and two
length-two mutation controls are asserted separately.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/s3-shared-length2-transposition-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -I -W error -B research/s3-shared-length2-transposition-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/s3-shared-length2-transposition-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/s3-shared-length2-transposition-floor --check-source-history
```

Any CPython 3.12 with the standard library can replace the interpreter path.
Expected marker: `PASS_S3_SHARED_LENGTH2_TRANSPOSITION_FLOOR`. The run writes
no files; its receipt hashes the present package files.

## Open next questions

1. **Does a different shared-call cost model break the norm bound?** If one
   paid call can carry different alphabet elements on different registers for
   one unit, the induced element is not a subsequence product. First step:
   state that model's exact cost and enumerate its cost-two calls. Blocked by:
   the cost is undefined in #4351, so no lower bound can be claimed for it.
2. **Can the same norm obstruction be combined with a target screen at length
   three or more?** A cost-three word attains `(1 3)`, so the question becomes
   whether a shared schedule can attain a whole diagonal target below the sum
   of coordinate costs. First step: pin one target and count shared letters
   against its representation rank. Blocked by: no native conversion or
   supplier instance is supplied by #4351 or this package.

## Credit and overlap

This contribution was produced by Nick Petalas. Riquelme Soares (@hevlyo), PR #4351, supplies the paid S3 alphabet, the
two-dimensional representation, the diagonal target screen and the scratch
question answered here. The reduced word norm, its subadditivity and the
length table of S3 are classical. The finite checks and the proof are new.
Predecessor verifiers, censuses and representation screens were cited rather
than replayed. Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.

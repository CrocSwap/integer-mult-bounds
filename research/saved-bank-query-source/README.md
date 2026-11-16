# One saved bank other than response2 autonomizes the query-4 row

**Scoped identity and finite census; no new κ.** On the published
two-edge feed of
[research/coded-active-feedback](../coded-active-feedback/README.md),
save the pair-0 X bank at the `bridge_query2` snapshot and add
`I - C1 Q C1` times that bank into the final-query argument. The
second operator stays `C1 Q^2` on `response2`. No call is added. The
four-input row after query 4 is autonomous.

In this formal algebra the operator is the unique element that does
this for the named bank. It has two monomials, and each cancels one y0
term and one x1 term. Among the other 28 banks recorded before that argument, no
algebra element works. [PROOF.md](PROOF.md) gives the schedule
identity, the monomial charge, and the census. The selected frontier
is unchanged.

## Result

The autonomous row at this checkpoint is `[A, 0, X1, 0]`, where
`A = D1 Q^{-1}` and `X1 = Q^{-1} C3 D1 D3`. The published row, with
`F2 = C1 Q^2` and no extra source, is `[A, B, X1 + E, 0]`. Here

```text
B = Q^{-1} C1 Q (I - Q) D1
E = (Q^{-1} C1 Q C1 - Q^{-1}) D1.
```

The named bank is the replay label `bridge_query2:0`:

```text
S = [0, -C1 Q D1, D1, 0].
```

`bridge_minus` deletes the `D1` on `x1`, so the copy is taken at this
snapshot. The one operator is `P = I - C1 Q C1`. The replay with
`C3 X + C1 Q^2 response2 + P S` as the final-query argument equals
`[A, 0, X1, 0]` on the pre-suffix row.

The two monomials, after the query's `Q^{-1}`, contribute

```text
I:           y0 = -Q^{-1} C1 Q D1,    x1 = Q^{-1} D1
-C1 Q C1:    y0 = Q^{-1} C1 Q^2 D1,   x1 = -Q^{-1} C1 Q C1 D1.
```

Their sum is `[0, -B, -E, 0]`. Either monomial alone leaves a term of
`B` and a term of `E`. The field ledger for one circuit that emits both,
under the predecessor's published units, is 2016 scalar ADDs, 560
monomial passes, 32 mode CLEARs, 112 COPYs, and 224 extra fields. It is
an upper bound for that circuit, not a tape proof.

The 29 legal sources are the recorded observations before `response4`,
excluding `response2`. Nineteen have a zero y0 or x1 column. Six have a
unit x0 or y1 column, which forces the operator to vanish. Three labels
are the same pair-0 Y bank; its unique candidate clears `B` and `E` and
writes a nonzero x0 correction. Only `bridge_query2:0` works. The nine
later observations are not inputs of this argument, and the same lemmas
reject them.

The scalar suffix does not produce the four uncoded target banks. This
row witness is not a caller.

## Evidence class

The row identity is a proof in the predecessor's formal algebra. The
list of 29 legal banks is an exhaustive finite census: the domain is
the replay's observation list, the enumeration is the ordered labels in
[verify.py](verify.py), and every bank is settled by a zero column or by
the inverse of a one-term column. There is no operator search. A further
physical relation can make a rejected residual zero; that quotient is
outside the census. The positive equality descends to every quotient.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/saved-bank-query-source --check-only
python3 -B scripts/research_package.py --package research/saved-bank-query-source
```

Direct replay:

```sh
python3 -I -W error -B research/saved-bank-query-source/verify.py
python3 -I -O -W error -B research/saved-bank-query-source/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. Allow a few seconds. No network, native build, or full
multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks whether one changed caller removes real work. This package
does not change the query demand and does not price a new caller. It
answers the second open question of
[research/active-feedback-outside-edge](../active-feedback-outside-edge/README.md),
merged PR #6961. The two-edge bill of `F1 = Q`, `F2 = C1 Q` is not this
package. The x1 block of an owner-indexed fresh image is not this
package.

Base commit: `17469fff78c22941280f04d39dc5a1faee09c840`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue and selected record are
provenance. The selected conditional result remains
`781451/250000000`. `search.py` and `gauge.py` are live inputs.

Overlap at this base covered the local note inventory and a live search
of open upstream PR titles. The matching note is the predecessor
package above, where this question is still open. No open upstream PR
title states this saved-bank insertion. PR #7033 is the owner-indexed
x1 block. The declared alternating-decoder lock and the owner-indexed
y0 map read banks after the suffix; they do not insert an operator into
the final-query argument.

## Open next questions

After this insertion, which coefficients of the four final banks does
the unchanged scalar suffix clear? The autonomous statement stops at
`query4:3`, and none of the four final banks is the uncoded target. The
first step is to compare those four banks in this replay with the
uncoded targets, before adding a call or a second saved source. No
tape or outer bill is priced here.

Does one named relation outside `Q^4 = C1^2 = C3^2 = I` and the
inherited `D` conjugation make `bridge_minus:0` succeed? That live bank
has a zero x1 column in this algebra, which is why the saved copy is
required. The first step is to impose that one relation and recompute
`P S` for this same operator. The positive identity on
`bridge_query2:0` is not reopened by a quotient.

## Credit

The schedule, algebra, and published feed are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code, and the passive ceiling packaged by Chris R /
Clear1nsight. The gauge engine remains
`research/coded-native-caller/gauge.py`. The question is open question 2
of `research/active-feedback-outside-edge` (merged PR #6961). The
declared-family lock and the owner-indexed y0 map are neighboring
results and are not redone. New work is the named bank, the operator
`I - C1 Q C1`, the two-monomial charge, and the census of the other
recorded banks.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.

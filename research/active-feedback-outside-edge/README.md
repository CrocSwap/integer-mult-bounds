# One outside feedback edge leaves the four-input row coupled

**Scoped row test; no new κ.** The named edge is the second feedback
operator `C1 Q` in the published two-edge feed of
[research/coded-active-feedback](../coded-active-feedback/README.md). The
first operator stays the published identity. This edge is outside the
8,281-policy family, because every nonzero second-edge policy ends in
`Q^2`. No call is added. The four-input row after query 4 is not
autonomous.

Holding either published operator fixed, no element of the predecessor's
algebra on the other edge makes that row autonomous. The obstruction is
that one-edge hypothesis. It is not an unrestricted impossibility: the
pair `F1 = Q` and `F2 = C1 Q`, both outside the family, does make the same
row autonomous. That pair changes two edges. Its other final banks are not
the four uncoded targets.

## Result

The autonomous row at this checkpoint is `[A, 0, X1, 0]`, where
`A = D1 Q^{-1}` and `X1 = Q^{-1} C3 D1 D3` is the no-feedback third
coefficient. [PROOF.md](PROOF.md) gives the schedule identity, the unique
second edge that restores `A`, and the opposite-correction obstruction for
the first edge.

The named replay is

```text
x0 = Q^{-1} C1 Q^{-1} C1 D1
y0 = Q^{-1} C1 D1 - Q^{-1} C1 Q D1
x1 = Q^{-1} D1 - Q^{-1} C1 Q^{-1} C1 D1 + X1
y1 = 0.
```

Its first coefficient is not `A`, and its second coefficient is nonzero.
The published edge `C1 Q^2` remains the only second-edge element that
restores `A`, and that edge keeps a nonzero second coefficient. Omitting
the second edge leaves the first coefficient at zero.

The two-edge boundary witness equals `[A, 0, X1, 0]` on this row and on
the final image of that bank. It is recorded so the one-edge failure is
not read as a statement about every feedback change. It does not equal the
four final target banks.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/active-feedback-outside-edge --check-only
python3 -B scripts/research_package.py --package research/active-feedback-outside-edge
```

Direct replay:

```sh
python3 -I -W error -B research/active-feedback-outside-edge/verify.py
python3 -I -O -W error -B research/active-feedback-outside-edge/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. Allow a few seconds. No network, native build, or full
multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks whether one changed caller removes real work. This package does
not change the query demand and does not price a new caller. It takes the
second open question of the declared-family coupling note on fork draft
PR 152, which is the remainder of handoff
[discussion comment 19138525](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138525)
after `research/coded-active-feedback` restored the missing coefficient.
The first open question of that note, an owner-indexed map on intact
endpoint banks, is not this package.

Base commit: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue and selected record are
provenance. The selected conditional result remains
`781451/250000000`. `search.py` and `gauge.py` are live inputs.

Overlap at this base covered the open upstream PR snapshot and discussion
snapshot, plus local notes. The matching active-feedback note is the
predecessor package above. No open upstream PR title states this named
edge. The declared alternating-decoder lock is a different object: it
does not change a feedback operator.

## Open next questions

What is the ordinary bill of the two-edge witness `F1 = Q`, `F2 = C1 Q`,
and which of its final banks can be cleared by scalar operations already
present in this schedule? The row witness is not a caller. The first step
is to compare those two monomials with the published `I` and `C1 Q^2` on
the same owned banks, then read final banks 0 and 3 from this replay,
before adding a call. An owner-indexed map that keeps every endpoint bank
intact is a different question and is not taken here.

Does one feedback source other than the saved response, still with no new
call, make this same row autonomous while the published second operator
stays `C1 Q^2`? The first step is to name that saved bank and the one
operator added into the existing final-query argument. Nothing here
supplies that source.

## Credit

The schedule, algebra, and 8,281-policy family are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code, and the passive ceiling packaged by Chris R /
Clear1nsight. The gauge engine remains the inherited
`research/coded-native-caller/gauge.py`. The declared-family decoder lock
that left this edge question is fork draft PR 152. New work is the named
`C1 Q` row, the one-edge identities, and the two-edge boundary witness.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.

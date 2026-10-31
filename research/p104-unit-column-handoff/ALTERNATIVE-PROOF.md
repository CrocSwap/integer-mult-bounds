# A lower-allowance alternative with four extra ADDs

## Exact result

For the same source, dual pairs, pivot and cut as [PROOF.md](PROOF.md), a second
explicit schedule uses seven source ADDs and six cut ADDs. Their allowances
are 72 and 64. Including both inverses gives **26 ADDs and allowance 272**.
The gate-minimum schedule remains **22 ADDs and allowance 280**. Neither
schedule dominates the other in both event count and weighted allowance;
no claim that these exhaust the Pareto frontier or minimize allowance is made.

The complete alternative word has 25,166 events and scalar allowance 217,700.
The original word has 25,140 events and allowance 217,428; #6297's schedule has
25,280 events and allowance 218,564. Thus the alternative saves 114 events and
864 allowance units relative to #6297. Its paid histogram, rank 9 → rank 5 +
rank 4 split, arbitrary-input endpoint and eight owned lifetimes are identical
to the gate-minimum candidate. **No new κ.**

## Two commuting half shears

Write `p=596`, and retain the actual row `a` and either actual column `b` from
the main proof. Let

`S1 = I + (1/2)e_594 e_592^T`,

`S2 = I + (1/2)e_594 e_593^T`, and `S=S2 S1`.

The two nilpotent off-diagonal matrices multiply to zero in either order.
Consequently the shears commute, fix `e_p`, and their inverses negate their
coefficients. Since `a_592=a_593=5/16` and `a_594=5/8`,

`a' = a S^-1 = (5/8)e_594^T + (3/8)e_p^T`.

Both actual columns have `b_592=-1` and `b_593=1`, so the two changes to
coordinate 594 cancel and `b'=S b=b`. Their pivot coordinate stays one.
The unit-column lemma supplies `R'` with `a'R'=e_p^T` and `R'e_p=b'`.
Set `R=S^-1 R'`. Then `aR=e_p^T` and `Re_p=b`, exactly as required.
Every operand is an existing support role in the required common frame;
all coefficients in the forward and inverse programs satisfy the caller cap.
The complete handoff follows from the same rank-one surgery argument in the
main proof, independently checked on the full constructed word.

The source operations, in execution order, are:

| Destination | Source | Coefficient |
|---:|---:|---:|
| 596 | 594 | -5/8 |
| 188 | 596 | -1 |
| 592 | 596 | -1 |
| 593 | 596 | 1 |
| 594 | 596 | 1 |
| 594 | 593 | -1/2 |
| 594 | 592 | -1/2 |

All use frame 3. The cut program omits the row involving role 188 and uses
frame 1053. The inverses reverse the operation order and negate coefficients.
The first ADD costs 20, each unit ADD costs 8, and each half ADD costs 10:
source `20+4*8+2*10=72`; cut `20+3*8+2*10=64`. All four boundaries cost
`2*(72+64)=272`. The support-activation lower bound in the main proof is
unchanged: this alternative deliberately uses one extra ADD in each forward
completion, and therefore does not contradict the six-/five-ADD minimum.

## Reproduction and independent scope

The registered package command runs both the gate-minimum and alternative
checks in normal and optimized Python. For this alternative alone:

```sh
python3 -I -W error -B research/p104-unit-column-handoff/alternative.py
```

Expected: `PASS_P104_ALLOWANCE_ALTERNATIVE inserted_events=26 inserted_allowance=272 word_controls=28`.
`ALTERNATIVE.json` records both exact programs, full primary/independent
invoices, source and implementation hashes, and the constructed word digest.
The default command is read-only; `--write` explicitly regenerates the receipt
and `--emit-word /absolute/external/path.json` exports the word.

The lead proposed the two-half-shear mechanism. Worker A checked its dense
rational boundary matrices, constructed the full word with the source-pinned
predecessor, and replayed every formal coefficient. Worker D independently
derived the cancellations and tariff. Its existing integer-dyadic replay and
binary-frame checker are reused without changing their arithmetic or source
bytes. The separately authored `weighted_review.py` wrapper changes only the expected fixture inventory
and repeats all original boundary, ownership and target checks. The valid
alternative must pass that wrapper before any negative control is counted.
Its analytic review is retained in [WEIGHTED-REVIEW.md](WEIGHTED-REVIEW.md).
All 26 single inserted-event omissions and two chart/growth faults reject in
the primary replay. Ten independent semantic faults must reject for semantic
reasons, before the fixture inventory check.

`GATE-MINIMUM-RESULT.json` preserves the original published receipt verbatim.
The updated `RESULT.json` has the same mathematical fields; only hashes of
the revised package documentation and manifest change. The alternative
verifier authenticates the historical receipt and checks this exact equality
after removing those metadata hashes. Historical validation is not silently
transferred to the new source: amended checks are recorded in VALIDATION.md.

## Limits and next question

This is a second local schedule, not a weighted-circuit optimum or a new
supplier. No native, caller, compiler, precision/tape or outer obligation is
discharged. All five selected framework assumptions remain. The next bounded
question is whether either allowance 280 can improve while retaining the
sharp 22-ADD total, or allowance 272 can improve when additional ADDs are
permitted. A weighted lower bound would be needed to certify either optimum.
No further coefficient or preconditioner search is part of this package.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Credit
#6297, Ali Romman's #5611/#5602 compiler and tariff, and all predecessor names
retained in the main README. Independent means separate derivations and
implementations, not independent human or proof-kernel acceptance. Apache-2.0.

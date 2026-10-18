# Dyadic admission of QQ16 unread minors

This is a scoped scalar-admission result submitted for review, not a supplier
or a new kappa.

The unread basis used by [PR2443](https://github.com/CrocSwap/integer-mult-bounds/pull/2443),
`H0=[1,2,3,4,5,6,8,12]`, has determinant `-32` and a dyadic inverse. It passes the
check below. However, replacing just unread port 2 by port 25 gives a rationally
invertible minor with determinant `-80` and inverse entry `1/10`. That read set
cannot support a finite dyadic-linear decoder for all original inputs under the
same two-cut observations, even when access and retention are free.

This does not contradict PR2443. Its specific basis is dyadic, its theorem is
rational, and it does not claim native execution. The new contribution is the
explicit alternative-set obstruction and a complete local census, useful before
optimizing which ports to leave unread.

## Domain and result

Use the actual integer `8 x 112` query matrix R and ordinary set U96 from the
retained [QQ16 packet](../joint-query/README.md). For an unread set H of size eight,
consider exact inversion of

```text
w = R_H D_(2,H) x1_H,
x1_H = D_(2,H)^(-1) R_H^(-1) w.
```

The order is the one in PR2443. Each port's cover map must be undone after scalar
inversion. No commutation of the different port maps is assumed.

Let `D=Z[1/2]`. An integer square matrix is invertible over D if and only if its
determinant is a unit of D, namely a signed power of two. Sufficiency follows
from the adjugate formula. Necessity follows by taking determinants of a left
inverse. Thus nonsingularity alone is insufficient for dyadic scalar admission.
The same odd-factor obstruction holds with Gaussian-dyadic coefficients.

The exact census includes every unread set at exchange distance at most two
from H0. No random sampling is used.

| Distance | Sets | Singular | Dyadic-unit determinant | Nonzero odd-factor determinant |
| --- | ---: | ---: | ---: | ---: |
| 0 | 1 | 0 | 1 | 0 |
| 1 | 704 | 185 | 485 | 34 |
| 2 | 107184 | 46180 | 58537 | 2467 |
| Total | 107889 | 46365 | 59023 | 2501 |

The nonzero absolute determinants are `16,32,48,64,80,96`. The odd-factor values
are `48,80,96`. [RESULT.json](RESULT.json) contains every histogram, both complete
inverses and the counterexample. This is not a census of all eight-subsets of U96.
A unit determinant admits the scalar inverse, not a native read or a favorable bill.

## A counterexample for the complete two-cut decoder

The observation contract is exactly PR2443's. Retain `x1_A/T`, `y1_A/T` after
complete F0, read `x1_(U\H)` there, and retain `y2_A` and `C=x2_U` immediately
after B1. There is no intervening modification. No `y2_U` or additional original
input is observed. Here A and T are the retained selected sets.

Use this order for the alternative unread ports and integer vector:

```text
H = [1,25,3,4,5,6,8,12],
z = [1,2,1,1,1,1,3,-2].
```

Exact multiplication gives `R_H z=10 e_1`, where centre coordinates are zero-indexed.
Set all owner and payload values constant, so every cover map acts as the identity.
Writing `P_A=R_A^T/4` and `q=10 e_1`, initialize

```text
x_U = iota_H z,  x_A = -P_A q,  x_T = 0,
y_U = 0,        y_A =  P_A q,  y_T = 0.
```

These are valid dyadic inputs, including the selected dirt. Since `R_A P_A=I`,
the first forward query is zero. The conserved F0 equations give

```text
x1_U = y1_U = iota_H z,
x1_A = x1_T = y1_A = y1_T = 0.
```

At B1, its future logger gives `y2_A=P_A q` and its ordinary target subtraction
gives `C=0`. All 88 read coordinates vanish. Hence all allowed observations are
zero except `y2_A=(5/2) R_A^T e_1`. Every observed coordinate belongs to the ideal
`5D`, but the required original `x_1` equals 1.

A finite D-linear circuit preserves `5D`. Therefore no such circuit can decode
all original inputs from these observations. The argument also covers finite
Gaussian-dyadic linear operations and owner permutations. The ideal `5D[i]` is
proper, as reduction modulo five with `i -> 2` maps 1 to 1 and five to zero. Extra dirty workspace or affine constants do not help a linear
implementation: compare the displayed input with the zero input using identical
workspace and subtract the two executions. The observation difference stays in
the ideal while the required output difference is 1.

A frame change is covered only if its coefficients are separately shown to lie
in the proved ring. Normalized Clifford coefficients such as `1/sqrt(2)` are
outside `D[i]` and are not covered here. No binding of the complete native gate
alphabet to this ring is supplied, and no claim that all native operations are
Gaussian-dyadic is made.

This is not an information-loss witness over Q. The rational inverse exists,
and its row 0, column 1 entry is `1/10`. Nor is it an obstruction to restoring
only the selected original inputs. In this displayed family those selected
inputs are already determined dyadically by `y2_A`. The claim concerns complete
input recovery, as in PR2443, under the fixed observations and coefficient ring.
Nonlinear exact integer division, odd-denominator gates, new observations or a
changed first pair are outside the result.

## Reproduce

Python 3.12 or later, standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-dyadic-unread-minors
python3.12 -I -O -B research/qq16-dyadic-unread-minors/verify.py
```

The registered replay checks source pins and runs:

- `verify.py`, using the one-/two-column determinant lemma, exact Fraction
  elimination, two inverse orders and the constant-owner two-cut witness;
- `oracle.py`, importing no primary verifier or pending PR code, using direct
  fraction-free elimination on all 107889 matrices and adjugate cofactors for
  both inverses;
- `test_verify.py`, checking optimized replay, a Git-free source export and
  rejection of source corruption, receipt type corruption, a missing receipt
  and an altered histogram.

The six mathematical controls include a singular minor, a wrong inverse sign,
an odd denominator, treating every nonzero determinant as a dyadic unit, a
changed modular vector and a duplicate unread port. Default replay writes no
artifacts. `verify.py --emit` explicitly emits a new complete receipt to stdout.

[SOURCES.json](SOURCES.json) pins retained main inputs at
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Pending PRs are attribution and
contract context, not runtime dependencies. Native replay, chronological
retention, child hosting, precision, tape, all-size admission and the complete
supplier invoice are not established. The separate retained QQ16 local replay
was run as a baseline, not as verification of a new native decoder.

## Engineering limits

All loops have fixed finite domains: matrix dimension at most eight, 112 ports,
and 107889 streamed candidates. Python uses dynamic allocation and arbitrary-size
integers. This is a managed-runtime deviation from fixed steady-state allocation.
The exact hash-bound source, fixed matrix sizes and streamed census bound live
state; no list of all candidates is retained. Parser sizes are checked before
hashing/decompression. Functions stay below 60 physical lines. Direct and
optimized replays, warning-enabled tests and a second determinant algorithm are
the available interpreted-code checks. A future broader domain must add explicit
input bounds and recheck resource limits rather than reuse this bounded receipt.

## Open next questions

Can a dyadic-unit unread basis reduce a complete native decoder's cost? First
for a dyadic-linear implementation, filter candidate read sets by the determinant
gate, then compare actual endpoint frames and the full read, chart-map, retention
and cleanup invoice. The blocker
is physical access and sustainable retention, not nonsingularity. The original
PR2443 basis already passes the dyadic check. No broader search is justified by
this finite census alone. [TASK.json](TASK.json) records the structured handoff.

## Credit

Gareth Davidson's PR2432 supplies the unread-column criterion and H0, pinned at
`cbede349fc764aa38379aa533befe3215916cfcd`. starship-s's PR2443 supplies the
arbitrary-input rational decoder and explicit two-cut contract, pinned at
`545c05e17243c962b112b91e7f84b4c1a41de7b8`. thakrarsagar's PR2470,
`1b2eee3bf1ec67e68c0b0fa7f47c7b2a66febe56`, is the separate retention census.
None is adopted as a supplier or represented as independently reviewed here.

Ali Romman and the retained QQ16 contributors supply the matrix, selected
sections, conserved maps and cover semantics. Adam Gall, commdata2338,
kyzer1023 and the coordinate-read predecessors retain their information-bound
credit. Rohan Arun, Jeremy Kothe, DreamingOfClouds and the earlier supplier and
compiler lineage retain their attribution through the unchanged
[QQ16 notice](../joint-query/NOTICE.md). No predecessor executable is imported or
vendored. New work is Apache-2.0. No independent human or proof-assistant review
is claimed.

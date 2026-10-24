# Original-J correction ranks and reciprocal reader cuts

This additive annex retains two completed results about reciprocal
responses. The first classifies the correction ranks for extensions of
the original clean response `J`. It includes the native implementation
of its coordinate rank-four split. The second identifies three exact
reader cuts for the later signed-metric response `E=P R`. These are
different response families. The annex does not combine them into a
controller or improve the complete kappa calculation.

## Original-J correction rank

The [root proof](frozen/root/RECIPROCAL-CENTRE-RANK-20261018.md) and its
[independent review](frozen/lanes/independent-review-20261017/reciprocal-centre-rank-review-20261018/REVIEW.md)
use the actual eight-row matrix `R`, with `K=R^T/4` and `RK=14I_8`:

```text
J = I_112-KR,     E = J+KMR,     G = J+KNR.
EG = I  iff  12I-13(M+N)+14MN = 0.
```

For dyadic scalar matrices `M,N`, reciprocity forces both correction
ranks to be eight. Over the rationals, the minimum rank sum is eight.
All equality cases are

```text
M = (12/13)P,     N = (12/13)(I-P),     P^2=P.
```

The projection need not be orthogonal. The proof derives `MN=NM` from
reciprocity; it does not assume commutation. It also proves that if one
correction has no denominator divisible by 13, its reciprocal partner
has full rank eight. A rank-four/rank-four split therefore requires a
13-denominator on both sides.

This theorem measures the two specified correction terms. It is not a
query or native-cost lower bound for arbitrary implementations of the
full response. For example, `M=N=I` gives `E=G=I`, although both specified
corrections have rank eight. The later `E=P R` family in the
parent package is outside this original-J extension theorem.

The independent scalar check covers all 256 coordinate projections,
nine pairs on all 112 input columns in both inverse orders, and
noncommuting and incorrect-weight controls. The written argument proves
the universal rank bound and all equality cases.

## Literal coordinate rank-four words

The [native proof](frozen/lanes/reciprocal-centre-20261018/RECIPROCAL-CENTRE-NATIVE.md)
and [independent word review](frozen/lanes/independent-review-20261017/reciprocal-native-review-20261018/REVIEW.md)
cover `P=diag(1,1,1,1,0,0,0,0)`. They retain four original rank-eight
centre calls per word. Both responses, both orientations, and both
historical providers give eight local words.

| Per local word | Dyadic real primitives | Real /13 scans | Native children | Native rank mass |
| --- | ---: | ---: | ---: | ---: |
| Forward E or G | 165,594 | 16 | 3,511 | 5,105 |
| Backward E or G | 165,618 | 16 | 3,511 | 5,105 |

The scans are separate from the dyadic bill. These are local component
counts, not a complete bit-machine supplier price. Every word has 23,500
events. The fresh reverse-column check covers all 640 arbitrary inputs,
all 408 logical helper returns, all 91 private-buffer returns, frames,
source bindings, and the division queries. `C0` ends at zero at I.
`C1` through `C7` retain their arbitrary input values at I. Requiring all
eight owned outputs to be zero needs seven extra CLEARs, or 14 primitives.

The scalar maps are `(x,y,h)->(x,y+T x,h)` and
`(x,y,h)->(x-T^T y,y,h)`. The backward map uses the transpose of its own
response. The reciprocal is the other response. After the common FULL
output is removed, the physical matrices remain ordered:

```text
C_F(T) = [[q,0],[q T q,q]],
C_B(T) = [[q,-T^T],[0,q]].
```

Thus `EG=I` in one scalar chart does not cancel the physical port-line
operators. The new centre occurrences are bound to exact recipes from
the retained 3,036-class native phase review. This replay does not repeat
that earlier phase sweep or re-emit the native program.

Each completed pre-division query has no new 13-denominator. The local
word adds at most one 13-denominator level at its operation boundaries.
The [conditional grid proof](frozen/lanes/independent-review-20261017/reciprocal-centre-rank-review-20261018/ODD-GRID-COMPOSITION.md)
requires exact dyadic endpoints for completed recursive children, root
conversion of every numeric field, and a separate binary and magnitude
guard. The individual rational E and G words are not completed dyadic
recursive providers. The grid check includes signed scans at widths
1 through 14, five nested trees, and failed-premise controls.

## Reader cuts for the later signed-metric response

The [source-cut proof](frozen/lanes/native-escape-20261017/reciprocal-reader-cuts-20261020/SOURCE-CUTS.md)
and [independent review](frozen/lanes/native-escape-20261017/owner-review/reciprocal-source-cut-review-20261020/REVIEW.md)
use the later 112-port model `E=P R`, `R=I+U ell`, and `ell U=-2I_16`.
Here `R` is a reflection, not the eight-row matrix above. Physical `P`
is a dyadic scalar matrix, not a monomial field permutation.

Put `t=y+R0 x` and `w=x-(P0^-1 R1 P0)t`. Under the pinned F/B/F native
contracts and the literal D25 entry and exit views, the exact records are:

| Cut | Current source | Ordered reader | Returned frame |
| --- | --- | --- | --- |
| After raw F0, before post-P0 | X | `c0=ell0 x` | `F9` |
| Before pre-P1 and raw B1 | Y | `c1=ell1 P0 t` | `F9 q_anchor` |
| After raw F2, before post-P2 | X | `c2=ell2 P1 P0 w` | `F25` |

The middle record is a hole record, not FULL. The ordered P factors are
already in the current source values. No old-chart read is needed at
these cuts. This does not supply an accumulator in the required frame.

Each conditional reader requires 16 separate typed accumulators and
applies 136 signed complex ADDs, at 1,088 inherited real scalar units.
Three formations cost 3,264 units if those accumulators are supplied.
The operation preserves the source and adds to each accumulator's
arbitrary baseline. It does not create a clean query from a dirty one.
The row one-norm is at most 11 at every local prefix, and this is attained.
There is no new coefficient denominator or source-line native transform.

The independent check reconstructs the model, verifies the ordered
formulas, checks 1,792 complete Z4 phase identities, and checks all 128
source and accumulator columns. The producer additionally checks all
656 local columns. The binding check compares 272 formation and 272
immediate inverse instructions. An immediate inverse needs an unchanged
source; it is not a later erase for the complete controller.

These reader costs exclude record supply, a zero baseline, accumulator
views, preparation, transport, leases, a recursive host, and final
restoration. The native contract remains a pinned premise. No reader
native-event replay or complete native invoice is claimed here.

## Reproduction

Use Python 3.11 or later, the standard library, at least 3 GiB free space,
and a new output directory. From the repository root:

```sh
python3 -I -B research/reciprocal-native-responses/annexes/original-j-rank-readers/replay.py --out /tmp/original-j-rank-readers
```

Expected final line:

```text
PASS_ORIGINAL_J_RANK_READERS_ANNEX
```

The [runner](replay.py) executes six unchanged checkers in normal Python
and with `-O`, one process at a time. It checks every frozen source before
and after execution. It writes logs, all compared results, and
`REPLAY.json` to the output directory. The retained
[publication replay](evidence/REPLAY.json) records the fresh relocated run.

Results without source paths must match exact bytes. For the reader
payload and its receipt, the runner first binds the raw decompressed
payload to its recorded raw hash. It then canonicalizes complete JSON,
changes only the four declared source-path strings, and uses the canonical
payload hash in the canonical receipt. Source-manifest JSON has only its
absolute keys changed to campaign-relative keys. Every other field is
compared. Gzip headers are not mathematical equality tests.

[SOURCES.json](SOURCES.json) records the 73 unchanged campaign files.
The package contains the full input closure for this runner. It does not
claim a complete runtime closure for the older producer and phase-sweep
scripts retained as source evidence. Historical freeze text remains
unchanged. Final package integrity is recorded in
[ANNEX-MANIFEST.json](ANNEX-MANIFEST.json).

## Open next questions

The original-J pair still needs an ordered controller with legal chart
transitions, restored arbitrary fields, a completed dyadic recursive
endpoint, and a full hosting, precision, and cost proof. The source-cut
result still needs safe typed records, their baseline contract, retention,
transport, and late erase. This annex does not solve these obligations.

The publication context is main commit
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, whose selected result names
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470).
The annex preserves historical source pins and proves no transfer to that
construction. [NOTICE.md](NOTICE.md) gives source credit, license terms,
and the AI-assistance disclosure.

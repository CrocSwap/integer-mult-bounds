# A one-helper-hyperplane recipient-stock screen

## Model and physical specialization

In the literal graph, ports 222 through 629 are 408 separate helper owners. Exactly 391 of them start in chart 0 and end in chart 1; both dimensions are respectively zero and eight. The other 17 have rank four. Each of the 391 fields is an independent public field, and each has the same endpoint operation. For any nonzero helper-only binary form `h`, an invertible XOR basis can make `h` one of these helper coordinates. Set that coordinate to zero and retain the other 390. The common endpoint action respects this basis change. At the raw rank-moment level this omits one rank-eight target, a debit of `8^t` in productive mass. Entry/exit recoding and owner setup would also need to be charged in a complete construction.

Work with the frozen normalized circuit. At each original MOVE `j`, let `f_j` be its whole-field binary input form, let `c_j` be its receiving chart, and let `S_c(j)` be the span of **all** values that were present at chart `c` strictly before `j`. Initial public owners count at time −1. The screen generously retains every past snapshot regardless of owner retirement and grants unlimited same-chart copies and XORs. The recovered payload can then be inserted at the original arrival time precisely when

`f_j ∈ S_{c_j}(j) + span(h)`.

All later old MOVE inputs and clocks are fixed. All eligible deletions may be applied simultaneously: at each replaced occurrence, reproduce exactly the old normalized arrival, so induction preserves every subsequent original normalized field. A new cocharted receiving `ADD` is allowed. A retimed delivery or a surviving paid operation whose sender or payload changes is not covered. This formal upper bound does not need to prove that its historical snapshots, ownership, or erasures are physically free.

The zero-based clock convention is the array index in `strong-bit.json.gz`; the screen checks all labels and the original 630 symbolic return forms. At each clock the implementation records full forms after the instruction, so the recipient stock for a MOVE does not include its own arrival. This enforces the original arrival time before any subsequent read.

## Exact affine cosets

Let `H` be the 391-dimensional helper-only space. At a recipient chart and clock write `K = S ∩ H`. The possible constraints for one MOVE are `H ∩ (f + S)`, either empty or an affine coset `h₀ + K`. The verifier maintains Gaussian bases over `F₂`, projecting every prior stock form to the coordinates outside `H`. A projected dependence yields a full form in `K`; retaining all such kernel rows computes the complete intersection. A projected reduction of `f` either fails or produces one exact representative `h₀`. The checker also confirms `h₀ ∉ K`: no original MOVE is already recoverable from recipient stock for unrestricted inputs.

Among 2,803 MOVEs, exactly 768 have nonempty helper-only cosets. Of these, 391 end at chart 1. In time order their kernels have dimensions 0 through 390, are nested, and each successive kernel contains the previous `h₀`. The 391 representatives are independent. Consequently their affine cosets are disjoint and partition every nonzero vector of `H`: the last nonzero coefficient of `h` in that basis gives its unique chart-1 deletion.

Each of the remaining 377 cosets has kernel dimension at most three. Fully expanding them gives 549 points, with no repeated point. Every one of those points has exactly one additional chart-1 deletion; every other nonzero `h` has no additional deletion. The checked rank multiset of the 549 two-deletion cases is:

| Deleted ranks | Number of helper hyperplanes |
| --- | ---: |
| `{1,1}` | 394 |
| `{1,2}` | 152 |
| `{1,4}` | 2 |
| `{2,2}` | 1 |

The best possible raw saving is therefore `1 + 4^t`: it also dominates `2·2^t`, since their difference is `(2^t − 1)^2`. The function `8^t − 4^t` increases for positive `t`. At `t = 2/3` it equals `4 − 4^(2/3) > 1`, since `16 < 27`. Hence `8^t > 1 + 4^t` for all `t > 2/3`. Further bank and replay costs cannot make the optimistic estimate more favorable.

## The rank-four endpoint classes

The remaining 17 helpers have rank four. They form ten classes with exactly equal start and end chart identifiers: three singleton classes and seven two-helper classes. Exhausting nonzero XORs inside each class therefore tests 17 singleton constraints and seven two-helper constraints. Under the same historical-recipient-stock model, every singleton can delete exactly two MOVEs of ranks `{1,2}`. Of the seven pair XORs, six can delete one rank-two MOVE and one can delete one rank-one MOVE. Simultaneous deletions use the same induction as above. None of these cases requires the rank-eight affine-flag argument; the verifier checks every one directly.

Every such change loses one rank-four target and saves at most `1 + 2^t`. For `t ≥ 3/4`, put `z = 2^t`. Then `z > 5/3` because `(5/3)^4 < 8`, and `z² − z − 1 > 1/9`. Thus `4^t > 1 + 2^t`. Together with the rank-eight result, the screen covers every one-dimensional constraint contained within an exact equal-endpoint helper class for `3/4 ≤ t ≤ 1`.

## A live-owner control at helper 625

Set helper 625 to zero, preserving all other arbitrary inputs. Replace instructions 6909–6911 by `INIT 2220` directly in chart 507. This removes the rank-four MOVE 6911; its payload was zero. Replace 10568–10570 by `INIT 3006` in chart 1 followed by cocharted ADDs from the live registers `2976, 2977, 2979, 2987, 2988, 2989, 3004`. This removes the rank-one MOVE 10570. At the end of each three-instruction window the new and old complete register maps, chart labels and whole-field forms agree. The first later uses of owners 2220 and 3006 are at clocks 6937 and 29573. The replay verifies that all seven donor owners are live in chart 1 at the replacement, that all 630 outputs agree, and that the original 3,433 private CLEAR instructions are retained without an extra owner. Seven new ADDs replace two old ADDs. The real `{1,4}` saving still does not pay for losing the rank-eight helper.

## Scope

This is a finite, exact whole-field screen for the pinned one-local-call normalized word and a single omitted dimension within one exact co-endpoint helper class. It is not a proof about XORs mixing endpoint classes or ranks, arbitrary helper constraints in tensor powers, changing paid source fields, inserting or retiming new paid contacts, different physical graphs, or an end-to-end κ gain. The verifier does not independently reconstruct the rational projectors or prove the complete physical supplier and outer application; those are inherited from the specifically pinned source. The source hash, normalized trace, coset computation, exhaustive flag argument, direct rank-four tests, named live-owner control and corruption rejection are independently replayable here.

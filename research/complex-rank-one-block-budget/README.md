# Sharp integer block budgets for the selected complex rank-one payload

**Cost-alphabet screening result; no physical decoder or new κ.** At block rank at most 16,
at least **363 of the selected word's 2,412 rank-one children per call** must be reblocked
to pass the optimistic primitive-saving target below. Reblocking all 2,412 permits at most
**10 additional integer rank units** of paid work. In particular, one additional rank-16
call already fails. Charging one extra rank-one call per nontrivial output block erases
every block's saving for every allowed rank 2..51 at this target and below.

This supplies a concrete gathering/restoration budget for the revision-3 rank-shape card.
It adds partial integer thresholds and additional-work pricing to Douglas Colkitt's
retained all-mass ideal lever calculations. A decoder that passes these necessary cost
conditions still needs its actual chronological frame and dirty-state realization.

## Model and results

The pinned selected local profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`,
with rank mass 5,586. Keep every non-rank-one child, the 64-per-call centre charge,
width 73, 896 live families per nine-stage replica, and old idle mass 1,646 per call.
For a chosen `k` in 0..2412, replace `k` unit-rank payload calls by integer ranks in
`1..B`, preserving mass `k`, where `B` ranges from 2 to 51. All compatibility and
scheduling restrictions are optimistically removed. Idle work is fractionally packed
at rank 51. Additional copies, gathering or restoration are paid **on top** of this
payload and idle bill; they receive no old idle credit.

The exact target is `a*=35491136290869/20000000000000000`, or about 0.001774556815:
21/20 times the baseline's certified *upper* primitive-ceiling bracket
`1690054109089/10^15`. Acceptance here is a strict relaxation moment below one at
`a*`. Thus a passing relaxation has more than 5% primitive-ceiling headroom relative
to that upper bracket. This is not a 5% κ improvement or a realized supplier.
The selected bit budget would already bind a full construction at this complex target.

| Maximum block rank B | Minimum replaced k | Maximum extra rank-one calls after replacing all 2412 |
|---:|---:|---:|
| 2 | 1440 | 1 |
| 4 | 722 | 4 |
| 8 | 482 | 7 |
| 16 | 363 | 10 |
| 32 | 291 | 12 |
| 51 | 255 | 14 |

The full 50-cap table, adjacent strict signs and exact rational intervals are in
[RESULT.json](RESULT.json). For B=16, the first passing partition is 22 rank-16
blocks plus one rank-11 block. Its remaining budget is less than 0.004311 of a
rank-one call, so it cannot pay even one additional rank unit. Full replacement
is 150 rank-16 blocks plus one rank-12 block. Its maximal same-rank overhead bills
are 10 rank-one, 5 rank-two, 2 rank-four, or 1 rank-eight call; these are alternatives,
not simultaneous allowances. Any integer-rank overhead of mass at least 11 fails.

Even putting all rank-one payload at the largest allowed block rank 51 gives a
relaxation moment above **1.01133** at `a=1/99`. So changes to the rank-one payload
alone cannot meet that planning target under this model. The predecessor already
excludes 1/99 even after deleting all rank-one costs; this reblocking check is a
corroborating, mass-preserving boundary, not a new exclusion of that target.

## Proof of optimality and the block tax

Write `q=1-a`, with `0<q<1`, and `c(r)=(r/73)^q`. Concavity gives a decreasing
increment `c(x+1)-c(x)`. For two ranks `1<=x<=y<B`, transferring one unit from
the smaller to the larger decreases total cost (remove the smaller at zero).
Iterate until at most one non-full rank remains. Hence the minimum at total
integer payload mass `k` is attained uniquely by `floor(k/B)` blocks of rank B
and, when nonzero, a block of rank `k mod B`. This is optimal in the relaxed cost
alphabet; no existence of a physical block decoder is inferred.

With `P(k,B)` the resulting complete local profile, the lower moment is

`F(k,B,a) = [sum_r P(k,B)_r c(r) + (1646/51)c(51)] / (896/9)`.

Its value is nonincreasing in `k`: a partial block's next marginal cost is at
most `c(1)`, and starting a new singleton leaves the bill unchanged. This
justifies bisection over all `k=0..2412`. Both engines prove strict rejection
at `k_min-1` and strict acceptance at `k_min`; this proves the threshold for
every partition, not merely the partitions visited by bisection.

An additional profile `J` contributes `sum_r J_r c(r)/(896/9)` to F. For a
same-rank overhead call, solve this strict inequality and certify the adjacent
integer counts. For arbitrary integer overhead mass, the same concavity lemma
minimizes its cost by full rank-51 blocks plus a remainder. In the full B=16
case, one rank-10 overhead call passes and one rank-11 fails; monotonicity of
the optimal overhead cost excludes every mass at least 11.

For one rank-r payload block, the saving in rank-one call units is `r-r^(1-a)`.
Every r=2..51 has certified saving below one at a*. The largest is at r=51,
below 0.354602. This expression increases with a, so the inequality holds
for every `0<=a<=a*`. Paying one extra rank-one call per nontrivial block
therefore makes each block strictly more expensive than its original singles.
This proof applies to any partition or replacement count. It is conditional
on that overhead tariff; the package does not prove a compiler must incur it.

## Arithmetic and verification

The retained `ceiling.py` uses atanh/logarithm and exponential Taylor intervals.
The separately implemented check in `verify.py` uses no logarithm or exponential
code: for `z=1-r/73` and `q=1-a`, expand
`(1-z)^q=1-sum_{n>=1} t_n`, where `t_1=q*z` and
`t_(n+1)=t_n*z*(n-q)/(n+1)`. All terms are positive, and every successive ratio
is less than z. After a partial sum, the remaining tail is at most
`t_(n+1)/(1-z)`. Integer interval arithmetic rounds outward at 160 bits and
stops with tail at most 2^-90. Both methods certify the baseline bracket,
all thresholds, all overhead decisions, and all 50 block-tax inequalities.

Replay also compares 10,274 complete integer-partition fixtures at two rational
savings and runs eight domain/mathematical controls. A deliberately incorrect
invoice which subtracts extra work from old idle mass gives a false pass at
the first rejected rank-one overhead count; the correct additional bill rejects
it. `test_package.py` checks source drift/inventory omission, numeric and bool/int receipt drift,
an incorrect arithmetic oracle, all 72 square-root oracle bounds by exact squaring,
and optimized replay in a read-only minimal
source relocation. These checks support the written proof; they are not a
formalization or independent human review.

## Reproduce

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 scripts/research_package.py --package research/complex-rank-one-block-budget
```

Expected markers: `PASS_COMPLEX_RANK_ONE_BLOCK_BUDGET` and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. The direct checker
supports `-I -O -B`; `verify.py --write` regenerates RESULT.json. Source inputs
are pinned by Git blob and SHA256 in [SOURCES.json](SOURCES.json); generic replay
also checks historical task/selected-record provenance. [VERIFY.json](VERIFY.json)
declares all four live inputs. Recorded environments and unrun checks are in
[ENVIRONMENT.json](ENVIRONMENT.json).

## Limits

This is an exact cost-alphabet relaxation and a conditional per-block tariff
obstruction. It supplies no decoder identity, support realization, physical
gathering, dirty-state restoration construction, actual frame grouping,
compiler/controller admission, hosting or new outer witness. Changed coverage,
centre sharing, other local children, ranks above 51, different widths or
templates, cross-call amortization and changed outer guards require their own
model. Full selected cold replay, native execution, precision/tape obligations,
Lean, hosted CI and independent human review were not supplied. The selected
record, frozen sources and upstream inputs are unchanged.

## Open next questions

- Can a concrete rank-16 decoder meet this narrow gathering/restoration budget?
  Pin one chronological climb group and exhibit its dirty-state identity and
  complete additional paid profile. The blocker is physical realization; the
  arithmetic alphabet alone supplies no free batching contract.
- Can changed rank-two/rank-three delivery or centre sharing add enough budget
  for 1/99? Derive one replacement local profile and its applicable coverage
  law, then include every additional cost before screening. The blocker is the
  missing new supplier interface, rather than an unexplored packing seed.

Structured questions and the changed scope declaration are in [TASK.json](TASK.json).

## Credit

Started from current main `adc34159e0d6dc3dd2af2bdba3f5ca7376ef957e`, chooser nonce
`3ab0bbddb657f850e7894cfc57f8d29e`, priority revision 3. The scope changed from
physical decoder synthesis to its optimistic screening experiment. Coordination:
[Discussion1596](https://github.com/CrocSwap/integer-mult-bounds/discussions/1596).

Credit Douglas Colkitt / #1240 for the selected local-word ceiling, profile and
ideal lever model; Sagar Thakrar / #1012 for the coverage law; Rohan Arun / #1094
and #1042, Jeremy Kothe's mutable-leaver/packing lineage, Hao Yan / FanPUYen's
controller, Josie Elliston's owner audit, and the retained construction sources
named in the selected review. #1264 surveys pending packing ceilings; #1334
prices ideal bit-side levers. Neither partial integer reblocking nor its extra
work tariff is inferred from those different scopes. Existing Apache-2.0 source
notices are retained; no third-party package is copied.

Prepared by Arham Tahir with substantial OpenAI Codex assistance in the research,
proof, both arithmetic implementations, tests and documentation. No subagents.
New material is Apache-2.0.

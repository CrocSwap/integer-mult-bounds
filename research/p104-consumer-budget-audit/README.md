# Conditional complete-cost screen for the pinned P104 consumers

**The stated uniform five-forward/four-dual consumer cannot reach the selected
saving with either PR2712 or PR2725's pinned dual profile.** This remains true
after granting every call its full persistent endpoint progress, forgiving
416 integer rank units per dual in the most favorable way allowed below,
and placing every remaining paid coverage unit in a fictitious rank-73 child.
Every finite number of fully paid auxiliary banks preserves the rejection.

This is a conditional budget obstruction for two fixed local profiles and one
coverage contract. It supplies no global owner construction and makes no
unrestricted claim about P104. The local endpoint identities remain valid.
The selected frontier is unchanged.

Jose Manuel (`jmbarrancoml`) first stated the PR2712 consumer-budget finding in
[Discussion 2619, comment 18955566](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619#discussioncomment-18955566).
This package independently audits its coverage and credit hypotheses, binds
the actual predecessor evidence, and also checks the separate PR2725 word.
The PR2712 calculation and original stopping insight remain credited to that
comment. [PR2729](https://github.com/CrocSwap/integer-mult-bounds/pull/2729)
separately prices local endpoint-fusion headroom; its local gains do not supply
a complete consumer invoice.

The final overlap check also found Nick Petalas's
[local-only claim to extend the PR2712 screen to all positive pair counts](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619#discussioncomment-18956430).
This package stays at four pairs, adds the independent source/applicability
audit and PR2725 case, and exhibits why unrestricted same-mass resynthesis
falls outside the proof. It does not claim the all-pair extension.

## Exact inputs and the consumer being tested

Scientific base: canonical main
`65e840f55428829ecc75d7c21006cc13ce1268c8`, priority revision 5. The three
scientific inputs are pinned independently:

| Role | Public source and exact head | Positive-child profile, ordered H1 through H8 | Rank mass |
| --- | --- | --- | ---: |
| Forward F | [PR2458](https://github.com/CrocSwap/integer-mult-bounds/pull/2458), `3170afd2fc13a990bfe28f5ab6421bcda4ffd0f6` | `(1216,74,86,104,48,42,68,8)` | 3070 |
| Dual D2712 | [PR2712](https://github.com/CrocSwap/integer-mult-bounds/pull/2712), `afa5d6649460dcdb93489babd74f0ee9d01a4911` | `(1498,60,74,92,58,56,92,8)` | 3542 |
| Dual D2725 | [PR2725](https://github.com/CrocSwap/integer-mult-bounds/pull/2725), `71d24b655c2fdddc063b9aaf285e8425ce197499` | `(1502,58,74,93,57,56,91,9)` | 3542 |

The verifier reconstructs the forward program from the native core and the
pinned insertion circuit, then recounts every transport. Its profile agrees
with the sum of the retained native-core and added profiles
in [PR2458's receipt](https://github.com/CrocSwap/integer-mult-bounds/blob/3170afd2fc13a990bfe28f5ab6421bcda4ffd0f6/research/p104-two-target-native/RESULT.json).
The dual profiles appear in [PR2712's proof](https://github.com/CrocSwap/integer-mult-bounds/blob/afa5d6649460dcdb93489babd74f0ee9d01a4911/research/p104-shared-chart-retiming/PROOF.md#L116-L134)
and [PR2725's README](https://github.com/CrocSwap/integer-mult-bounds/blob/71d24b655c2fdddc063b9aaf285e8425ce197499/research/p104-dual-add-retiming/README.md).
These are alternative words. Their separate retimings are not combined here.

All three have 104 source fields, 104 target fields and 150 arbitrary dirty
helpers. The partial forward correction fixes two rows; the other 102 retain
the inherited Gram/2 contract. PR2458 retains eight **owned live-copy discard**
lifetimes; its per-edge adjoints do not prove a whole backward program.
The two dual words instead inherit eight **zero-initialized, exactly zero-erased**
private lifetimes from the physical-dual lineage. These different private
contracts are retained explicitly, and neither gives persistent endpoint
coverage. See [PR2458's contract](https://github.com/CrocSwap/integer-mult-bounds/blob/3170afd2fc13a990bfe28f5ab6421bcda4ffd0f6/research/p104-two-target-native/README.md#L17-L54)
and [PR2712's boundary statement](https://github.com/CrocSwap/integer-mult-bounds/blob/afa5d6649460dcdb93489babd74f0ee9d01a4911/research/p104-shared-chart-retiming/PROOF.md#L9-L18).

The consumer fixes width `m=73`, `W=832` original live data families, five
forward calls and four calls of one of the dual words. These are the proposed
four-pair, nine-stage P104 substitution: `s=2p+1`, `m=8s+1`,
`W=(s-1)*104`, at `p=4`. The substitution and its coverage premise are
explicitly conditional in
[the terminal-correction floor](../p104-terminal-correction-floor/README.md#completed-optimistic-bill-and-why-idle-mass-is-not-a-credit).
That package points to Dominik Scholz's retained paired-chain model and Sagar
Thakrar's PR1012 coverage law. It does not admit a P104 owner embedding.

## Coverage and allowed changes

The theorem has the following hypotheses.

1. Each of the 832 original live data families has one unpaid coordinate.
   Any `B >= 0` auxiliary banks are fully paid: each adds 73 required paid
   coverage units and one family to the moment denominator. Width stays 73.
2. Credit every one of the nine calls with all
   `P = 104*8 + 104*8 + 150*9 = 3014` persistent endpoint units. This is a
   favorable coverage allowance, even if an actual ownership schedule cannot
   realize it. Private lifetimes give no additional persistent credit.
3. Outside the inherited local children, the remaining paid coverage has rank
   mass at least
   `I + 73*B`, where `I = 72*832 - 9*3014 = 32778`.
   This remaining mass may be carried by correction, helper-progress,
   residual or idle children collectively. It need not be idle mass alone.
4. The inherited local decomposition is fixed, except that each dual may
   decrease its original child ranks by nonnegative integers with total
   decrease at most 416. A child may disappear when its rank reaches zero.
   The forward profiles are fixed. There is no additional resynthesis,
   fusion, coarsening or repartition of inherited local children.
5. Every remaining positive recursive child has integer rank at most 73.
   The actual retained halving guard is stricter; relaxing it to 73 favors
   the candidate. All other omitted cost terms are nonnegative.

Hypothesis 3 is the precise coverage interface being audited. It prevents a
double charge when a correction itself supplies part of the remaining
progress: that child's rank belongs to the remaining bill once. Granting the
102 missing corrections and physical obligations free means ignoring their
additional nonnegative overhead while retaining this coverage requirement.
If a completion supplies progress `P_new` at added rank mass `A_new`, the
usual accounting `P_new <= A_new` allows it to replace that much idle coverage
without lowering this bound. A changed coverage law or an operation giving
unpaid progress requires a new invoice.

The 3014 credit is deliberately retained even after the hypothetical endpoint
deletions. No physical realization of that combination is asserted. Using a
larger progress credit or an extra unpaid coordinate is outside the theorem.
Fully paid banks may repack the remaining coverage, but may not alter the
fixed local profiles. The hypothesis is about finite `B`; it supplies no
positive margin uniform as `B` tends to infinity.

## Proof of the favorable lower bound

Let the primitive saving satisfy `0 <= a < 1` and put `p=1-a`. A child of rank
`r` contributes `(r/73)^p` before division by the family count. For
`0 < p < 1`, integer `0 <= delta <= r`, subadditivity gives

```
r^p - (r-delta)^p <= delta^p <= delta.
```

Thus deleting one unit of rank from an existing child saves at most the cost
of one H1 child. Subtracting 416 H1 children per dual is at least as favorable
as every allowed rank-deletion pattern, without needing to locate 416
removable endpoint children. The comparison extends to `a=0` by equality.
This proof does not cover coarsening: `H1+H1 -> H2` saves moment at zero rank
deletion and is expressly outside hypothesis 4.

For every other child with `0 < r <= 73`,
`(r/73)^(1-a) >= r/73`. Consequently its cost is at least its rank mass divided
by 73. This grants all remaining coverage fractional rank-73 packing,
including all fully paid bank coverage. No chronology, ownership or integer
packing restriction can lower this relaxed bill.

With the actual unmodified profiles and no banks, the zero-saving bound is

```
M(0) >= [5*3070 + 4*3542 + 32778] / (73*832) = 599/584 > 1.
```

After the stronger forgiveness of `4*416 = 1664` H1 children, the two
nine-call profiles are:

| Dual choice | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | Rank mass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D2712 | 10408 | 610 | 726 | 888 | 472 | 434 | 708 | 72 | 27854 |
| D2725 | 10424 | 602 | 726 | 892 | 468 | 434 | 704 | 76 | 27854 |

At `a=0`, adding the remaining coverage gives the optimistic value
`(27854+32778)/(73*832) = 583/584`. At positive saving the small inherited
children consume this apparent slack. Write a rank-r contribution as

```
(r/73)^(1-a) = (r/73) * exp(a*log(73/r)).
```

Use `log(73)>4`, `log(73/r)>2` for `2<=r<=8`, and `exp(x)>=1+x`.
For `a>0`, the fixed-profile numerator has strict linear lower slopes

```
L2712 = 4*10408 + 2*(27854-10408) = 76524,
L2725 = 4*10424 + 2*(27854-10424) = 76556.
```

Therefore, including any finite number of fully paid banks,

```
M_B(a) > 1 + (L*a - 104) / [73*(832+B)].
```

The selected record has
`kappa = 836330098538459/500000000000000000`. At `a=kappa`, both numerators
`L*kappa-104` are positive. For example, for D2712 the no-bank lower bound is

```
7594999831115139259129 / 7592000000000000000000 > 1.
```

The D2725 slope is larger, so it also fails. Every finite fully paid bank adds
73 to coverage and capacity; the displayed positive numerator survives with
the enlarged denominator. Concavity is used only to favor the remaining
coverage packing, not to coarsen the inherited children.

The selected `kappa` is the multiplication exponent saving, not the selected
complex primitive saving. The retained balanced transfer requires
`kappa < a/(1+a)` and hence `a > kappa`; see
[the fixed-word ceiling](../complex-local-word-ceiling/ceiling.py).
The displayed bound increases with `a`. Failure already at the smaller test
value `a=kappa` therefore excludes reaching the selected target under this
consumer contract. The actual retained seven-step transfer is more demanding.

## Why the fixed-profile hypothesis matters

An abstract same-mass histogram can pass this optimistic screen after
replacing the inherited decomposition. Reprice each forward mass 3070 as
`341 H9 + H1`, and each already-forgiven dual mass 3126 as
`347 H9 + 3 H1`. The nine calls then have profile
`3093 H9 + 17 H1`, still of mass 27854. This is an arithmetic witness, not a
constructed word, legal transport coarsening, or supplier.

For `0 <= a <= 1/580`, use `log(73/9)<17/8`, `log(73)<9/2` and
`exp(x)<=1/(1-x)` for `0<=x<1`. The same rank-73 relaxation for the remaining
32778 units now has the rational upper bound

```
M(a) <= [27837*(4640/4623) + 17*(1160/1151) + 32778] / 60736 < 1.
```

Both verifiers check finite rational log certificates and the final upper
bound `53862115339/53863448288 < 1`, using different logarithm proofs. This
witness demonstrates why rank mass alone, or the phrase
“416 rank units forgiven” without the deletion restriction, cannot justify
an obstruction to unrestricted resynthesis. It supplies no construction
realizing the new histogram.

## Scope and stopping decision

This screen grants more than a realizable consumer has established. It leaves
actual chronological owners, the 150-helper embedding, descending-edge
admission, private lifecycle realization, scalar/address and monomial work,
precision, rounded erasure, all-size lowering, and the remaining identity-row
corrections unresolved. Those missing obligations cannot rescue the fixed
profile while hypotheses 1-5 hold.

Stop owner construction aimed at beating the selected target with these exact
five-forward/four-dual profiles and coverage credits. A local identity or a
storage inventory transfer is still useful on its stated scope, but is not
evidence for expanding this particular consumer route.

## Open next questions

The useful reopening question is concrete: can a changed local profile,
coverage law or consumer pass its own favorable complete-cost screen? A first
step is a source-bound candidate bill that changes one declared premise and
includes its cost, before building its owners. Additional joint retiming or
coarsening needs an actual combined word and new profile; an extra unpaid
coordinate needs a replacement coverage theorem; a different call count or
width needs its own consumer derivation. Passing a relaxation would justify
that next admission experiment, not certify a supplier.

## Reproduce and evidence limits

Validation commands and exact retained-source checks are recorded in
[VERIFY.json](VERIFY.json), [SOURCES.json](SOURCES.json) and the verifier receipt.
With Python 3.10 or later and no third-party dependencies, run from the
repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-consumer-budget-audit
```

The registered commands run under isolated, optimized Python (`-I -O -B`).
The primary checker reconstructs profiles, boundary credits and exact rational
cost bounds. A separately written checker reconstructs all three scalar maps
on 358 arbitrary input fields, compares 256,328 inverse-transpose coefficients,
and checks dirty-helper restoration, frames and the distinct private lifetimes.
It imports no primary or predecessor executable code. Its six semantic controls
exercise stale frames, dirty COPY destinations, lost coefficients, undercharged
transports, lost dirty compensation and failed private cleanup. Artifact
controls also exercise source drift, typed receipt drift and Git-free replay.

This audit checks a conditional cost implication and pinned local profiles.
It does not rerun the complete native correctness proofs of its predecessors
or construct a global supplier. No selected-frontier, human-review or
proof-assistant claim is made.

## Credit

Credit Jose Manuel's Discussion 2619 calculation first; Ross Richardson's
PR2458 native binding and PR2445 two-target word; ywz65's PR2712 and physical-dual
lineage; commdata2338's PR2662 endpoint work; and PR2725's independent X90/N90
retiming. Retain the full predecessor attribution in those pinned packages,
including Chafik Boukhalfa's native channel, Rohan Arun's scalar/frame channel,
Adam Gall's schedule and the E8/native-interpreter ancestry. Credit the
terminal-correction-floor, paired-chain and packing-ceiling authors for the
conditional coverage framework and PR2729 for the separate local-cost context.
Prepared by Vasek (`flyingviper`) with substantial OpenAI Codex assistance,
including independent agent audits. New material is Apache-2.0; predecessor
licenses and notices remain in force.

## Maintainer integration: historical benchmark

The selected record used in this calculation is preserved byte-for-byte as
`inputs/SELECTED-AT-BASE.json`. Both engines authenticate it against the
original SHA-256 and Git blob in `SOURCES.json`; that original provenance
is retained. The live selected record and historical catalogue are not runtime
inputs. The assembly, scientific inputs and complete numerical receipt are
unchanged. The benchmark remains historical if the selected frontier changes.

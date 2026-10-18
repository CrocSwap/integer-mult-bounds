# Exact attainment of the joint rank-seven packing cap at T740

Ten interleaved copies of Nick Petalas's [PR3018](https://github.com/CrocSwap/integer-mult-bounds/pull/3018)
allocation admit a 550-row exchange journal that exactly attains the fixed-word
fractional packing cap of Marius-Paul Dumitrean's
[PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979).
The complete complex moment endpoint increases from
`[0.0017290342130642563095108, 0.0017290342130642563095109]` to
`[0.0017290357648755161814440, 0.0017290357648755161814441]`.
The gain is in `[1.5518112598719331e-9, 1.5518112598719333e-9]`, closing the
entire remaining fractional packing gap for these words and this bin model.

This is a finite chronological allocation and complete moment result. It is
not supplier admission, an outer multiplication exponent, or a change to the
selected frontier. In particular, Jeremy Kothe's PR3015 restore edit and its
PR3021 composition have a stronger conditional headline; this package closes
the remaining packing question for the underlying inventory. It does not
silently compose their changed words or reuse their release receipts.

Concurrent [PR3022](https://github.com/CrocSwap/integer-mult-bounds/pull/3022),
head `553dc9d8fc8c1489aa2b0378331a0de4b5e9b44e`, reports a T148 endpoint
near `0.0017290353460708282`, closing about 73% of the same gap. This
construction closes the gap exactly and proves the replica-divisibility
condition, at a larger physical stock. Its T148 admission follow-up is active;
this package does not duplicate or validate that release.

The scientific inputs are PR2979 at
`be191346391661f4d35fc0d1508d0a6029572576` and PR3018 at
`ca7113157d7c959fdfa9d7cd17ef92d3877070d0`. The checkout starts from canonical
main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
[SOURCES.json](SOURCES.json) binds live inputs; [RETAINED.json](RETAINED.json)
binds the two byte-identical PR3018 artifacts retained here. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18980473)
and [task record](TASK.json) describe live overlap and the scope change.

## Literal construction and complete bill

For every original row `(t,h,o,c,p,z)` and copy `j` in `0..9`, define

```text
row index = j*271728 + original row index
new row   = (10*t+j, h, o+74*j, c, p, z)
new call  = (original stage, original replica+74*j)
```

Copy the original provider dispatch. Every original source interval `(lo,hi]`
lifts to `(10*lo+j,10*hi+j]`, with `lo=-1` remaining `-1`.
For an unchanged row, both its call and its owner have the same copy index.
The lift therefore preserves chronology, widths, masks, prefixes and same-call
physical-family exclusions. Different copies use disjoint owner families.
There are 6,660 calls, 2,717,280 helper roles and 1,491,840 bins.

[EXCHANGE.json](EXCHANGE.json) then changes 550 rows with exact preimages.
Only 335 change destination; 215 change offsets during compaction. It touches
195 bins and 333 call times. The net bin-pattern histogram change reduces to the following
45-bin identity. A superscript is
written as repetition to avoid an implicit width charge.

```text
old                                   new
20 [4,8,9,9,9,9]@48                   17 [9,9,9,9,9]@48
10 [9,9]@32                           3 []@48
15 [9,9,9]@32                         20 [4,9,9,9]@32
                                      5 [8,8,8,8]@32
```

Capacity counts and every helper-width count agree. Fifty individual bins change pattern. Cancelling five `[9,9,9]@32`
patterns on both sides gives the displayed identity. The other 145 affected
bins relay roles without changing their patterns. The exact idle delta is

`20 H1 + 17 H3 - 15 H5 - 10 H14 + 3 H48`, where `Hr(b)=r*(73/r)^b`.

The resulting idle histogram is
`{1:173160, 3:49617, 5:17205, 48:281903}`. Including every local child,
the complete profile is

```text
{1:16456860, 2:4701960, 3:1594737, 4:719280,
 5:137085, 8:53280, 48:281903}.
```

Its rank mass is `48,165,120 = 740*65,088`. Physical stock is
`663,040 + 408 + 8 + 91 + 2 = 663,549`. The 91 private buffers are charged
once, as in the source contract. The retained owner engine's historical
`live+490` diagnostic omits 19 of those buffers; this package checks and
reports the actual `live+509` equation. This is a stock count under the
inherited model, not a physical execution or movement proof.

## Why this is the cap, and why T740

[cap_proof.py](cap_proof.py) independently enumerates all 2,551 feasible
patterns for capacities 8, 16, 32 and 48 and widths 4 through 9. It verifies
the source basis with rational inversion, proves its complete root bracket,
and checks reduced costs over the entire bracket. Twelve patterns have
identically zero reduced cost; the other 2,539 are strictly positive.
The logarithm/exponential enclosures are the authenticated source `root.py`,
so the arithmetic kernel is retained, not independently reimplemented here.
The new literal idle histogram equals 740 times the verified primal basis's
idle histogram. Thus its complete moment is the optimum's moment as an
identity in `b`, not merely a rounded root comparison.

There is also an exact integrality obstruction. On each tight pattern, put

`q = -3*[cap=8] - 6*[cap=16] - 12*[cap=32] + n6 + 2*n7 + 3*n8 + 4*n9`.

This equals 20 for `[9,9,9,9,9]@48` and zero for all other tight patterns.
Summing the capacity and width constraints gives

`20*N_[9,9,9,9,9]@48 = 1341*T`.

Strict reduced costs force every exact-cap allocation to use only tight
patterns. Since `gcd(1341,20)=1`, exact-cap integral patterns require `20|T`.
The displayed primal basis is integral whenever `20|T`. Among multiples of
74, T740 is therefore the first possible replica count. This does not
exclude nonmultiples of 74 or different words, bins, split-helper models,
physical contracts or costing rules. The journal supplies the missing
chronological sufficiency specifically at T740.

For a common unchanged background bill, the exchange improves the moment
for every `0<b<=1/100`. Factor its delta as `73^b*f(b)`, with

`f(b)=20+51*3^(-b)-75*5^(-b)-140*14^(-b)+144*48^(-b)`.

Here `f(0)=0`. The rational atanh-series bounds in `prove_exchange_sign`
certify `log(3)` in `(1.09,1.10)`, `log(5)<1.61`, `log(14)<2.64`, and
`log(48)` in `(3.85,3.90)`. Using `exp(-x)>=1-x` gives throughout the interval

`f'(b) <= 75*1.61 + 140*2.64 - 51*1.09*0.989 - 144*3.85*0.961`
`= -9740691/100000 < 0`.

Thus the strict improvement is independent of the local-profile background
when its widths, chronology and other charges are unchanged. That conditional
identity does not validate any other word or its supplier admission.

## Reproduction and verification boundaries

Python 3.12 and the standard library suffice. From the repository root:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/rank7-cap740
```

Use `python3.12` directly if available. The registered check authenticates
inputs, replays PR3018's preimage-bound journal and checks its T74 geometry,
constructs the implicit T740 rows and applies the new journal. An independent
differential implementation checks every affected bin and all 408 helpers at
every affected call. The unchanged retained owner engine separately streams
all 2,717,280 actual rows, checking complete role identities, every source
window, physical-family collision, capacity, mask, compact prefix and the
whole paid profile. No solver or Git history is needed for the verifier itself.
The generic metadata checker retains its own provenance requirements.

[RESULT.json](RESULT.json) is deterministic. The tests exercise actual lift
and journal behavior, illegal windows/capacities/family collisions, omitted
moves, stale/duplicate edits, cap/primal corruptions and omitted paid rank.
The optimized replay keeps all checks enabled. A separate internal read-only
review reconstructs the journal and all changed-bin/call checks without
importing `lift.py`; no independent human or formal-kernel review is claimed.

Discovery used bounded deterministic same-width relay searches. Early
one-step placements failed and were discarded; the final search found the
retained witness in 135 seconds. [decisions.tsv](decisions.tsv) records the
attempts. Search failures imply no infeasibility claim.

## Open next questions

1. Run a fresh source-bound native/admission/modern-outer release on this T740
   construction, including caller, movement, storage, precision/prefix/tape,
   and all-size/compiler obligations. Start with `lift.chronology` and
   `lift.Rows`, materialize the actual owner artifacts, and supply the complete
   profile above. The old T74 receipts do not bind this larger construction.
2. Bind the same allocation to PR3015's exact R1 words, whose widths are reported
   unchanged, and rederive their complete cap and release. The sign theorem is
   useful evidence, but does not prove source compatibility or composed
   admission. PR3021 is the credited starting point. These are targeted
   admission/composition tasks; further packing search inside this certified
   fixed-word relaxation cannot improve its optimum.

## Credit and implementation choices

Nick Petalas contributes this larger-replica construction, sparse journal,
cap-attainment/divisibility proof and new differential verification.
PR3018's journal and geometry checker are retained byte-identically, with their
original notices. Marius-Paul Dumitrean owns PR2979's words, cap and original
allocation. Credit Mason Hale, Jeremy Kothe, Jeremy Diviney, Yiyang Lu, Tekalign,
Ross Richardson, Dugongue, icekylinx, themilkman216 and the retained source,
geometry, native and owner lineage. Apache-2.0. Substantial automated
assistance was used; no independent human review is claimed.

Build the Lever led to a compact replayable journal rather than a solver-only
receipt. Prove It Works required the complete streaming owner check alongside
the differential check. Power of Ten led to explicit finite bounds, checks
active under optimization, local state and functions at most 60 lines.
Python managed allocation is a scoped deviation from fixed allocation; live
state is bounded by 740 replicas, 6,660 calls, 2,717,280 streamed roles,
1,491,840 bins and at most 2,000 journal edits. The three dynamic source modules
are authenticated before execution and run with bounded inputs. The retained
checker owns its existing implementation choices. Warnings are errors and
Ruff correctness/import/bugbear/modernization checks cover new code. No shared
runner, selected artifact or frozen predecessor is changed.

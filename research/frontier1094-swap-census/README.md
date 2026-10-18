# Selected PR1094: no improving two-role whole-helper swap

On the selected PR1094 owner map, **no unordered swap of two whole helpers
between distinct owner bins can strictly reduce the idle moment**, for any real
`0 < a < 1`, with call times, helper widths, actual source-event windows and the
local paid word fixed. Source and destination slices may compact to preserve
their occupied prefixes.

This is a complete finite census of the two-role swap move class — the first
move class the one-role census
([frontier1094-single-relocation](../frontier1094-single-relocation)) lists
among its non-exclusions — with a short exact comparison proof. It is not a
global packing optimum, a new supplier, or a new kappa.

## Result and evidence

The input is main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, with PR1094's
selected owner map at audited head
`0fc329d0bec93ca7cd288eaea1295172e8789810`. The exact inputs and pins are in
[SOURCES.json](SOURCES.json); [TASK.json](TASK.json) records the refined
`selected-packing` card; [TASK-CARD.md](TASK-CARD.md) is the pre-computation
card. The [coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18920710)
records this scope.

The reproducible certificate [CERTIFICATE.json](CERTIFICATE.json) contains the
baseline owner recount (inherited PR1091 audit), all 87 role-class rows, every
one of the 1,150 capacity-feasible improving pairs with both landing checks,
the positive fixture and eleven inherited owner mutation controls.

| Unordered role pairs | Count |
| --- | ---: |
| Same-bin swaps (no-ops) | 88,345 |
| Capacity-infeasible (one new remainder would be negative) | 1,570,734,429 |
| Strictly lower idle moment for every `0<a<1` | 1,150 |
| Identical idle moment for every `0<a<1` | 816,035,605 |
| Strictly higher idle moment for every `0<a<1` | 1,893,111 |
| Total `C(69120, 2)` | 2,388,752,640 |

All 1,150 capacity-feasible improving pairs fail the **strict source-event
window** rule already (`lo < position < hi` on both landings). The
active-pair and per-call family rules are never reached, so the obstruction
holds with those two restrictions relaxed. No legal strictly improving swap
exists in this class.

The 1,150 improving pairs come from five role classes (`(remainder, width)`
of the role's own bin; the map's 32,256 bins have remainders
`{0:24730, 1:2276, 3:377, 7:7, 48:4866}` and the 4,866 rank-48 bins are empty):

| Own-bin class A | Own-bin class B | Distinct-bin pairs | Why improving |
| --- | --- | ---: | --- |
| `(1, 7)` | `(3, 4)` | 377 | remainders `3+1 -> 4+0` |
| `(1, 7)` | `(7, 8)` | 1 | remainders `7+1 -> 8+0` |
| `(3, 9)` | `(7, 4)` | 754 | remainders `7+3 -> 8+2` |
| `(7, 4)` | `(7, 9)` | 12 | remainders `7+7 -> 12+2` |
| `(7, 8)` | `(7, 9)` | 6 | remainders `7+7 -> 8+6` |

In particular no swap touching a zero-remainder bin can ever improve, and the
4,866 empty rank-48 bins (the domain of one-role relocations) are outside this
class entirely.

## Exact comparison, uniform in a

A swap exchanges two roles of widths `w1, w2` between bins with free ranks
`x1, x2`, moving net rank `d = w1 - w2`: the pair goes from `(x1, x2)` to
`(x1+d, x2-d)`, which is feasible exactly when both new entries are
nonnegative. With `p = 1-a` in `(0, 1)`, the changed moment contribution is
`x1^p + x2^p` versus `(x1+d)^p + (x2-d)^p` at fixed sum.

For fixed sum `S`, `t^p + (S-t)^p` is strictly decreasing as the larger entry
increases above `S/2`, by strict concavity; continuity covers zero entries.
Hence the sign is: **strictly improving iff the new maximum exceeds the old
one**, strictly worsening iff it is smaller, neutral iff the multiset of
remainders is unchanged. This is an exact integer comparison for every real
`0 < a < 1`, with no floating-point exponent ordering; the test suite
cross-checks it against exact two-square-root comparison at `a = 1/2` on the
3,472 feasible integer quadruples of its grid.

Completeness is an exact accounting identity: 87 role-class rows partition all
`C(69120, 2)` unordered pairs into the five categories above (88,345 same-bin
pairs are counted once, across class boundaries too), and the materialized
improving list has exactly the analytic count of 1,150.

## Positive fixture and controls

A negative result needs a checker that can find a gain. A real legal swap
(roles `(5,4,139)` and `(7,14,296)`, remainders `1+7 -> 2+6`, strictly
worsening) is applied in memory; the inherited owner audit accepts the changed
map with its recounted idle histogram, and the census on that map reports the
same pair as a **legal strictly improving swap** (its inverse). Swapping back
restores every bin remainder and the audit passes again. This map is a control,
not an admitted physical construction or a modification of the frozen input.

The thirteen test groups cover the exact radical oracle, a toy brute-force
pair enumeration, the pair-aware family rule (a same-call swap is a bijection
and must not read as a collision; a cross-call collision is caught even with
the window muted), strict window endpoints, certificate tampering, a suppressed
candidate, and source-drift rejection.

## Packing cap and realized fraction (acceptance gate)

The pinned calculator ([complex-local-word-ceiling](../complex-local-word-ceiling/ceiling.py),
called as `ceiling(local, 73, 896, 9, 64)` on the audited per-call local
profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`) gives the packing ceiling
`a < 0.001690054109089`, i.e. `kappa < 0.001687202645` when the complex side
binds — **+0.87%** over the selected kappa `0.001672660197076918`. This census
realizes **0** of that headroom: no legal swap improves the idle moment at all,
so the realized fraction of the cap is `0.0`. The linear `a < D/E` supplier
diagnostic does not apply to a fixed-word repacking; the packing ceiling is the
applicable budget.

## Scope and what is not claimed

* The local paid profile, 144 complete calls, helper widths, source-event
  windows, the bit supplier and inherited fixed extra charges are held fixed.
* The census covers unordered **two-role** swaps between distinct bins only.
  It does not exclude neutral paths (816 million capacity-neutral pairs) that
  could reposition a helper before a later improving move, three-or-more-role
  cycles, multi-role slice repacking within a bin, different call orders,
  changed local words, helper splitting, or idle-axis transfers (see
  [selected1094-idle-reassignment](../selected1094-idle-reassignment)).
* It is a finite census, not an impossibility theorem for any architecture.
  No new kappa, supplier admission, hosted invoice, cold replay or
  multiplication-theorem obligation is discharged. The selected record is
  unchanged.

## Reproduce

Python 3.12+ and the standard library suffice. From the repository root:

```sh
python3 -I -O -B research/frontier1094-swap-census/verify.py
python3 -I -O -B research/frontier1094-swap-census/test_verify.py
python3.12 -B scripts/research_package.py --package research/frontier1094-swap-census
```

Expected primary status (about 30 s):

```text
PASS_PR1094_SWAP_CENSUS_OBSTRUCTION pairs=2388752640 possible_gains=1150 legal_gains=0 positive_control=natural_legal_worsening_swap no_new_kappa
```

Default verification regenerates the entire certificate in memory and compares
every byte with `CERTIFICATE.json`; it does not modify repository artifacts.
`verify.py --write <new-path>` writes a fresh certificate to a new path.

## Open next questions

1. **Neutral-then-improving two-step moves.** The census counts 816,035,605
   capacity-neutral pairs; a legal neutral swap can change which windows bind
   and unlock a later improving swap. First step: filter the neutral pairs by
   the same landing rules, apply each legal one, and enumerate the newly
   possible improving pairs on the changed map, with a canonical ordered pair
   of swaps. Blocker: the legal-neutral set must be enumerated with the
   pair-aware family rule before the second move can be counted; no two-step
   coverage or admission is claimed here.
2. **Three-role cyclic transfers.** A 3-cycle among three bins preserves total
   rank and can spread remainders where every 2-swap is blocked. First step:
   derive the majorization sign rule for a cyclic transfer `(x1,x2,x3) ->
   (x1+d1, x2+d2, x3+d3)` with `sum d_i = 0` and count capacity-feasible
   improving triples by role class. Blocker: triple materialization is three
   orders of magnitude larger than this census and needs the same window join
   to be designed first.

## Credit and disclosure

Selected construction and owner map: Rohan Arun
([PR1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)) and its
retained construction lineage. Owner geometry, baseline audit and the eleven
mutation controls: Josie Elliston
([PR1091](https://github.com/CrocSwap/integer-mult-bounds/pull/1091),
`research/t16-owner-audit-seed67`), reused and credited, not reimplemented.
One-role relocation census and its concavity comparison method:
`research/frontier1094-single-relocation` (prepared for @Arham-Tahir64).
Packing ceiling calculator: Douglas Colkitt's
[PR1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240)
lineage. Prepared by **Aaron Wang** with help from opencode. Apache-2.0.

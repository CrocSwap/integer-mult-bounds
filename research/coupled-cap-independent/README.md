# Independent audit of the coupled-carrier packing cap

PR3148's new 145-row allocation exchange passes a separately implemented
finite audit. All **2,717,280 helper roles** satisfy their actual source
windows, physical-family exclusions, capacity limits and compact-prefix
charges. An independent square-root interval method certifies the complete
moment and all **2,551 packing patterns**. No discrepancy was found.

This corroborates a reported allocation improvement of approximately
`1.4052734766776475e-9` over PR3143. It adds no construction or larger exponent.
It does not admit either pending candidate or change the selected frontier.
The attempted remaining packing improvement stops here: the fixed-inventory
relaxation is attained, conditional on the supplied local profile and widths.

Scientific base is canonical main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
Audited source is [PR3148][3148] at
`f2927a4b8afcf0701a6b945e14f30de1d94f5176`.
[The claim and result thread][thread] records coordination.

## What is checked independently

`geometry.py` imports no predecessor implementation. It finds each pending
interval's previous touch by scanning the literal source-event prefix
backwards, then builds windows from the actual lifted call times. It traverses
roles in time-major order rather than the producer's copy-major order.
Fixed-capacity occupancy arrays check every bin, including untouched and empty
bins. Per-call sets enforce physical-family exclusion even when two different
child indices refer to the same physical family.

The audit authenticates the 145 literal preimages, fixes each call/helper
identity and reconstructs the ten-copy replacements. It checks the baseline
T74 fill separately. The observed idle delta is

```
{1:+20, 3:+21, 5:-25, 39:-10, 48:+9}
```

The complete idle bill is `{1:173160, 3:48951, 5:13875, 48:282569}`.
Adding 6,660 supplied local bills gives

```
{1:16376940, 2:4821840, 3:1567431, 4:679320,
 5:147075, 8:53280, 48:282569}
```

Its rank mass is exactly `65088*740`. The fixed stock count, including all
91 private cleanup buffers, is `896*740+408+8+91+2 = 663549`.
This last identity is a recount, not a physical storage implementation or
independent prefix/stock-reserve audit.

### Different exact arithmetic

The predecessor uses logarithm and exponential series. `arithmetic.py` uses
only rational arithmetic, integer square roots and directed integer rounding.
It imports neither that engine nor the predecessor's lift, owner or dual code.

Set `D=2^256`. Starting with an enclosing integer interval for `x=73/r`,
replace endpoints by `floor(sqrt(D*L))` and `ceil(sqrt(D*U))` 160 times.
After step j, division by D encloses `x^(1/2^j)`. Round an exponent b down
and up to the grid `2^-160`; multiply the selected root factors with outward
rounding. Because `x>=1`, these products enclose `x^b`. Exact powering tests
check both directions at dyadic and non-dyadic exponents.

The resulting enclosure proves strict moment inequalities at

```
0.0017297774946785970118869
0.0017297774946785970118870
```

for `M(b)=sum_r n_r*r*(73/r)^b/(73*896*740)`. These are the predecessor's
existing endpoints, not extra digits proposed as new coverage. The checker
also derives a strict baseline root enclosure from the literal T74 bill and
bounds the actual allocation-only root gain independently of either headline.
`RESULT.json` contains those exact margins and comparisons.

### Complete packing certificate

The checker independently enumerates every multiset of widths
`4,5,6,7,8,9` fitting capacities `8,16,32,48`. It checks the submitted
nonnegative ten-column primal against the capacity counts and all six width
counts. It solves the transposed basis equations with four formal idle-cost
symbols, then bounds every reduced cost throughout the root interval.

There are 12 exactly tight patterns and 2,539 strictly positive patterns.
Every bin in the actual allocation is tight, and its aggregate idle profile
is exactly 740 times the primal optimum. Thus its moment attains the packing
relaxation. At the root, every other packing in this model costs at least one;
monotonicity rules out a higher fixed-word moment endpoint.

On every tight pattern the checked linear functional
`(-3,-6,-12,0,0,0,1,2,3,4)` on capacity/width counts is zero except on
`48:[9,9,9,9,9]`, where it is 20. Summing gives
`20*N_(48:[9,9,9,9,9]) = 1323*T`, so `20` must divide T.
This is necessary pattern integrality, not a chronological lower bound of
740 replicas. These cap and residue statements are PR3148's claims,
independently corroborated here rather than claimed as new theorems.

## Reproduce

Python 3.12 or later, standard library only:

```sh
# Full branch history supplies the generic metadata checker's provenance.
python3.12 -B scripts/research_package.py --package research/coupled-cap-independent

# Direct finite replay requires no Git, network, solver or native dependency.
python3.12 -I -O -Werror -B research/coupled-cap-independent/verify.py
python3.12 -I -O -Werror -B research/coupled-cap-independent/test_verify.py
```

The primary marker is
`PASS_INDEPENDENT_COUPLED_CAP roles=2717280 patterns=2551 tight=12`.
`verify.py --emit` regenerates the complete receipt to stdout without writing
files. Normal execution compares every receipt field. All live inputs are
SHA256-authenticated before parsing; the generic metadata checker additionally
binds their exact Git blobs, including the five byte-identical vendored inputs.
Those pins resolve to snapshot ancestor `d30f1c5bbae0a3cd0205c8376d76ae8a5dba8fd0`,
so a full-history checkout need not separately fetch an unmerged PR head.
`vendor/ORIGINS.json` retains the original upstream head, paths, identical Git
blob identities and SHA256 hashes. All five snapshots were compared directly
with that fetched upstream commit before the snapshot commit. Only data, not
predecessor Python, is vendored.

Fourteen behavioral groups cover exact powers, rounding and domain errors,
pattern completeness, wrong primal counts/inventory, dropped nonlinear costs,
chronological access, capacity, same-call collisions, overlap, unpaid holes,
stale/duplicate/missing journal entries, changed role identities, inherited
profile binding, duplicate JSON keys, the actual optimized full CLI and a
Git-free read-only source export with a source-corruption rejection.

## Limits and next decision

The ordered width arrays and per-call local profile are explicit inherited
inputs, not newly derived from scalar/native operators. This audit does not
check PR3133's word algebra, native phase or residual-adapter interpretation,
its full physical/prefix/outer release, the bit supplier, or all-size and
analytic obligations. It does not use stored PASS receipts as substitutes
for the independently executed allocation and pattern checks.

The family decision is to stop packing search for these fixed inputs, retain
this independent finite evidence, and leave supplier admission to its separate
review. A changed word, inventory, capacity model or consumer needs a new bill.

## Open next questions

Can a different legal chronology attain the same cap with fewer replicas?
The divisibility certificate permits T20, while the supplied construction uses
T740 and 663,549 physical families. Start with explicit T20 source windows and
an integral tight-pattern assignment. Reject any source-window or same-call
family conflict before synthesis. No alternate chronology is constructed here;
its physical/prefix/outer costs and inherited word admission remain blockers.

A separate useful task is native/physical review of the pinned candidate.
Begin with PR3148's full reproduction instructions and its explicit retained
cache scope. This package deliberately does not launch that heavy replay.

## Sources and credit

Nick Petalas. Apache-2.0. Substantial automated assistance was used in analysis,
implementation, local review and writing. No independent human or proof-kernel
review is claimed.

Credit Jeremy Diviney/PR3148 for the new exchange and integration; dcharb78/PR3133
for the changed inventory, fill and cap; Gonzalo Mier/PR3143 for the precise
comparison; Nick Petalas/PR3024/3030 for the lift and earlier cap/integration
method; Marius-Paul Dumitrean/PR2979 and the retained relaxation lineage;
Tekalign for the predecessor chronological owner check; Arham Tahir/PR3136 for
the separate local carrier-fold audit; Hiroki Kumazaki for the failed old-journal
transport test in #3145. Retain Jeremy Kothe, Mason Hale, Yiyang Lu, Dugongue,
icekylinx and the earlier supplier lineage. Original notices and credit are
retained verbatim under `vendor/`. Exact scientific pins are in `SOURCES.json`.

Build the Lever changed the deliverable to a replayable independent checker.
Prove It Works required all literal roles and a different arithmetic method,
not another call to the retained checker.

Power of Ten inspection covers the four new Python files. Functions are below
60 lines. Loops are bounded by the authenticated input sizes, 2,717,280 roles,
1,491,840 bins, 2,551 patterns, ten equations or 160 root steps. Checks use
explicit exceptions and remain enabled under `-O`. Test subprocesses have a
120-second timeout. Rule 3 has a managed-runtime deviation for Python objects;
JSON inputs are capped at 2 MB compressed and 32 MB decompressed, occupancy
arrays are fixed before replay, and per-call sets hold at most 408 integers.
There is no predecessor-code loading or generated executable code. Warnings as
errors and repository Ruff diagnostics cover the new files. A resident or
untrusted-input service would require a separate fixed-capacity JSON boundary.

[3148]: https://github.com/CrocSwap/integer-mult-bounds/pull/3148
[thread]: https://github.com/CrocSwap/integer-mult-bounds/discussions/3145#discussioncomment-18996207

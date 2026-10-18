# Jointly restored target shears in the X4 compensation panel

**Finite complex-supplier circuit result; no new kappa.** Two noncommuting
target shears improve a source-bound PR799 X4 compensation pair by **256 real
primitives beyond its best zero/one-shear choice** in the declared menu.
All four preparation/restoration macros and every coefficient primitive are
charged. The local positive prefix bounds grow; whole-supplier admission is
not claimed.

The targets are 121 and 173. Set `a=-1`, `b=1/2`. Execute
`y0 += a*y1`, then `y1 += b*y0`, replace the two coefficient rows by their
transformed rows, then undo the second shear and the first shear in that order.
The 216 helper sources are arbitrary. No helper is changed in the forward
orientation, and the reused coefficient-work register is cleared after each
nonzero scalar macro, including its final use.

| Pair bill | One real component | Both components |
|---|---:|---:|
| Unmodified pair | 648 | 1296 |
| Best identity/one-shear choice in the menu | 484 | 968 |
| New jointly restored two-shear choice | 356 | 712 |
| Additional saving over best one-shear | 128 | 256 |

The saving against the unmodified pair is 584 real primitives. The prior
one-shear saving receives its own comparison row; it is not new here.
Forward and inverse-transpose local circuits have the same primitive bill.

## Reproduce

Python 3.10+ and its standard library, from the repository root:

```sh
python -I -B research/x4-two-shear-seed31/verify.py
python -I -B research/x4-two-shear-seed31/crosscheck.py
python -I -B research/x4-two-shear-seed31/test_package.py
```

Expected:

```text
PASS_X4_TWO_SHEAR candidates=447552 improving=1456 extra_real_saving=256 no_new_kappa
PASS_X4_TWO_SHEAR_INDEPENDENT candidates=447552 columns=219 controls=8 no_new_kappa
PASS_X4_TWO_SHEAR_PACKAGE controls=8 inventory=exact source_snapshot=frozen
```

`verify.py` reconstructs every census field and checks `EXPECTED.json`.
`crosscheck.py` imports no producer or predecessor implementation: Fraction
matrices and explicitly emitted original binary-Horner primitives reproduce
the full cost histogram and every pair's cost floors. It also executes the
winning forward and inverse-transpose circuits as exact sparse linear maps
on all **219 independent columns**: two dirty targets, 216 dirty helpers and
one arbitrary incoming work value. Eight mathematical mutations are rejected.
Both checkers were AI-written; no independent human review is claimed.

The search is complete for all 6,216 unordered target pairs, both chronological
shear directions, and `a,b in {-2,-1,-1/2,1/2,1,2}`: 447,552 candidates.
The identity and all twelve one-shear alternatives are separately priced for
each pair. There are 1,456 strict two-shear improvements on 396 distinct pairs.
The largest additional saving is 128 per real component, with the first
deterministic witness shown above. No timeout, heuristic pruning, global
matching, overlapping-pair composition or unrestricted optimality is claimed.
Seed 31 selects the complex track and the prespecified small half-integer
coefficient region; every pair and both directions are covered.

## Scope and precision

The old emitter's binary-Horner lowering is retained. PR696 copy/unit lowering,
signed digits and joint multi-source Horner are different cost models; their
savings are not combined here. This is a historical PR799 X4 panel, not the
current U8/T37 selected supplier. Native frame/phase replay, full supplier
reconstruction, global invoice/admission, hosted CI, `make verify`, selected
cold replay and Lean were not run. No working GCC/Boost toolchain is available
in the execution environment; no installation was attempted.

For unit input envelopes the exact local maximum row-L1 bound changes from
24 to 28 forward, and remains 2 inverse-transpose. The independently propagated
cancellation-free local maxima grow **24 to 57** and **2 to 5**, respectively.
These are local measurements, not a claimed bound for arbitrary incoming
nonuniform envelopes or for the complete program. Additional global precision
and adapter pricing remain obligations before supplier adoption.

The local construction adds no helper, persistent copy, source mutation,
nonzero-frame transition or recursive child. Its matrix identity preserves
the compensation map on arbitrary inputs, so untouched target rows can remain
unchanged. This fact alone does not discharge realization, whole-call hosting,
uniform compilation, precision/tape, analytic-transfer or bit-interface
assumptions of the multiplication theorem.

## Current state, sources and credit

Exact base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
The frozen `BASE-SELECTED.json` records the reviewed PR942 T37 conditional
kappa `1661960547713947/10^18`. Its review and actual assembly are read as
context; the selected pointer and all predecessor packages are unchanged.
`SOURCES.json` pins the exact source inventory. Archives are hashed exactly;
text hashes normalize CRLF to LF. The replay depends on this frozen snapshot,
not on future changes to the repository's selected pointer.

This extends the class explicitly excluded in **ToikY's PR909** single-shear
all-exponent result: two consecutive shears followed by joint restoration.
Credit **Sricharan Vagvala's PR749** restored rational target pairs and
**ToikY's PR901** X4 signed-unit census for the preceding mechanism. No novelty
is claimed for matrix conjugation or Horner arithmetic.

**Ross Richardson's PR937/947** concern constant-row shears of historical
rank-h center gather/scatter factorizations; their basis change is not executed
on dirty center registers. Here two paid, noncommuting shears execute on dirty
X4 compensation targets. These are different matrices and boundary contracts.
PR975 multi-source Horner, PR981 root traversal, PR984 JP8 scale deferral and
PR990 private native BIT queries are distinct concurrent work; no additive
savings or integration with them is assumed. See `OVERLAP.json`.

The X4 source is **Jeremy Kothe's PR799**, on **Chafik Boukhalfa's PR741** and
**icekylinx's** gauge44/scalar-emitter lineage. Credit the retained construction,
owner, phase, compiler and hosting contributors, including DreamingOfClouds,
Dugongue, Dominik Scholz, jon314159, Rohan Arun and eumemic. Original source
notices and `upstream/` remain unchanged.

Prepared for **@woklerx with substantial OpenAI Codex assistance** in research,
implementation, mathematical reasoning, verification and writing. New files
are Apache-2.0 under the repository license.

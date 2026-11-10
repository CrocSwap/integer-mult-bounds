# Exact coarse-output error with a refined dirty helper

For one explicitly stated four-call rounded-reader ABI, refining only the
helper does not remove coarse destination rounding. With M=2^b, integral
source |x|<=B and helper lift coefficient a, the exact worst error is

```text
ceil(|3a-M| B/M) coarse output cells;
minimum over every integral a = ceil(B/M).
```

A nearest integer a=(M+1)//3 attains the minimum; it need not be unique.
For1<=B<=M the optimum is exactly one coarse cell. The source and destination
grids stay fixed, the helper is arbitrarily dirty, and its original value is
restored. [PROOF.md](PROOF.md) states and proves the complete all-parameter
contract, including b=0, negative inputs, half ties and the inverse reader.

The reader is O(H)=floor(3H/M+1/2), ties toward positive infinity. Its inverse
SUBTRACTS THE SAME O(H); independently rounding a negative real increment
is a different ABI at half ties. Co-refining the output, delayed rounding,
nonlinear preparation and direct source delivery are separate contracts.
This is not a lower bound for all algorithms or arbitrary rounded backends.

## Added value and predecessor boundary

This is a quantitative source/interface corollary for the fixed-grid question
released by Nick Petalas [PR6666](https://github.com/CrocSwap/integer-mult-bounds/pull/6666).
Ali Romman [PR1135](https://github.com/CrocSwap/integer-mult-bounds/pull/1135)
already gives the identical four-call endpoint, generic same-grid barrier,
residue response, safe translations and charged escapes.6666 already gives
exact-dyadic/co-refined approximation and the odd-scalar coefficient error.
The addition is this precise fixed-coarse-output error/minimax law, not a
new generic rounding obstruction, commutator or dyadic approximation theorem.
The full credit and source licenses are in [NOTICE](NOTICE).

## Exact bounded evidence and reproduction

CASES.json freezes b0..8; B in{0,1,2,3,7,16,31}; seven coefficients
floor(M/3)+offset with offset−3..3; every H in0..M−1 and x in−B..B.
Initial destination−2 is dirty; the written identity covers every destination.
The441 rows involve454279 parameter visits, including repeated smaller
source ranges. Retained complete signed histograms, extrema and witnesses
are compared after separate blind first seals. A finite coefficient-window
optimizer list is labeled window-only; the proof establishes the global
minimum VALUE. [VALIDATION.md](VALIDATION.md) records actual checks and limits.

Use CPython3.12 standard library from the repository root:

```sh
python3.12 -I -W error -B research/coarse-output-dirty-reader-minimax/verify.py
python3.12 -I -W error -B -O research/coarse-output-dirty-reader-minimax/verify.py
python3.12 -I -W error -B research/coarse-output-dirty-reader-minimax/oracle.py --check-primary research/coarse-output-dirty-reader-minimax/RESULT.json
python3.12 -I -W error -B -O research/coarse-output-dirty-reader-minimax/oracle.py --check-primary research/coarse-output-dirty-reader-minimax/RESULT.json
python3.12 -B scripts/research_package.py --package research/coarse-output-dirty-reader-minimax
python3.12 -B scripts/check_research_commit.py --package research/coarse-output-dirty-reader-minimax --check-source-history --check-modes
```

VERIFY.json registers four240-second commands. The implementations are
separate; no predecessor executable is imported or run. Four verbatim inert
proof/README inputs authenticate through SOURCE-PINS.json. All runtime inputs
are package-local. Normal acceptance recomputes retained receipts with explicit
checks active under optimization. Optional first/emit modes are development
commands, separate from read-only registered replay.

## Coordination and limits

Canonical main7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority8, selected6030;
selected binding-only orientation passed. The unchanged guidance checkpoint,
635open PR bodies with full pagination/refresh, targeted all-state searches,
source feedback and fresh rendered Hub preceded the
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19381560).
Coverage is non-atomic; arbitrary diffs, all closed/hidden work and every
Discussion reply remain unknown. Card formal-interface-lemma explicitly
changes to this written quantitative corollary, without Lean or selected
assumption closure. The actual6678 rounded-prefix backend question was saved
as a separate unclaimed alternative.

Two reader calls and two integer lifts are an abstract inventory, not a
complete paid bill. Incoming helper width and |a|B fine-cell displacement,
intermediate output widths, coefficient synthesis/delivery, inverse reader
availability, source promises/conversions and consumer tolerance remain
open. No actual P104 caller, productive-target gain, native implementation,
physical speedup, supplier admission, new kappa or frontier change follows.
All five selected assumptions, precision/stock/storage/tape/compiler and
recursive/outer obligations retain their status. No selected scientific
replay, Lean, Docker or paid computation was performed.

ToikY with substantial OpenAI Codex assistance and separate AI primary/oracle
and review. No independent human or proof-kernel acceptance is claimed.

## Open next questions

1. Can a complete actual consumer accept this coarse error or fund a changed
   output/reader contract? First pin incoming widths, grids, tolerance and
   every coefficient/conversion/restoration cost. No funded consumer or
   complete native invoice is supplied here.
2. What error/cost law follows from a caller-backed alternative tie policy or
   rounding schedule? First bind one actual alternative and its literal
   inverse before testing. No alternative's implementation price is known;
   this proof must not be transferred to nearest-even by analogy.

## Verifier constraints

The finite parameter set and source objects are frozen before execution.
Managed Python integer/Fraction/container allocation is a Power of Ten rule3
deviation; declared finite dimensions bound arithmetic objects. Explicit
exception guards remain active under-O. Strict JSON tree handling and Python
callable dispatch are documented managed-language deviations from C rules;
there are no external scientific imports, generated code, network calls or
scientific subprocesses. VALIDATION.md reports actual function sizes, modes,
resource observations and any control limitations.

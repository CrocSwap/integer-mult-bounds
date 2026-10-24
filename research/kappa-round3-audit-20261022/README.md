# Independent finite audit of the joint helper/map witness

TL;DR: the independently implemented patch, arbitrary-input operator and
complete-invoice checks pass for the frozen round-three word. Five semantic
corruption controls and eleven controls against the actual Lean-wrapper input
checks reject. This is an independent AI audit, not independent human review
or a formal proof of the full multiplication theorem.

Prepared by Cao Yifan with substantial OpenAI Codex assistance; Apache-2.0.
Credit the audited PR4610 lineage and the new joint helper/map construction,
including Cinna Davis, Dugongue, zxv and Jacob Alan Sussman's retained sources.
Pierre-Loic Doulcet's separate PR4626 helper edit is not this witness.

## Audited input and implementation separation

The admitted word is
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, with decompressed
canonical SHA-256
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.

`audit.py` imports no construction, optimizer, native verifier or pricing
module. It uses its own standard-library implementation of exact binary
point-set spans, native-map actions, guarded patch reconstruction, frame-state
walk, Fraction-valued sparse free-word operator replay, scalar allowance and
controller invoice assembly. It reconstructs every complete payload field from
the frozen PR4610 predecessor plus the guarded patch.

The direct logical replay starts with all 632 persistent input columns and an
independent owned-entry column. It checks the entire chronological word in
both orientations, including all arbitrary helper inputs. Every helper's
logical endpoint is its own identity column, and the actual entrance/exit
frames supply its productive physical transform. Only owned C0 is erasable;
its arbitrary entry column and scratch value vanish at return. This avoids
mistaking arbitrary borrowed inputs for zero storage.

## Results

The complete local paid census is
`{1:2201,2:412,3:510,4:127,5:40,8:8}`. The productive census remains
`{4:28,7:7,8:47,9:326}` across all 408 independent helpers. Paid rank mass is
5327; paid call count is 3298. Independent primitive accounting gives the real
scalar allowances 158120 forward and 158168 backward. All 4429 frame bases,
main interfaces, helper exits and port maps are inherited exactly.

Direct assembly from the retained controller's physical event and diagonal
lists uses 18 full calls, 15 query shears and 15 idle events. It matches both
complete arithmetic dictionaries: 64,404 paid calls, 10,928 productive fields
and rank-mass surplus 752. No query, idle, diagonal or center bill is dropped.

The audit verifies that phase-receipt provenance names this exact word and the
actual current verifier/source-manifest hashes. Its class sets exactly cover
all 20 changed bare native maps, all 180 actual warp classes, all 105 new paid
pairs and all 26 changed arbitrary-helper interfaces. Each helper receipt is
bound to the actual role, entrance, exit and rank. Absolute phases themselves
are a separately checked proof boundary; this script does not independently
reimplement their Clifford decoder.

The five independent semantic controls alter a changed helper entrance, paid
rank, scalar coefficient, borrowed erasure or invertible native G. All reject.
`AUDIT.json` records exact input/source hashes, coverage and rejection reasons.

## Lean-wrapper adversarial controls

`wrapper_controls.py` invokes the actual round-three `replay.bindings` and
numerical-literal parser, first on the valid inputs and again after all tests.
It substitutes receipt mutations only in memory and puts a temporary modified
Lean literal only in this audit directory. It never changes a frozen receipt,
construction, verifier or proof source.

The eleven controls reject stale native/phase payload hashes, stale native/phase
verifier hashes, stale phase source manifest, duplicate helper coverage,
duplicate warp or paid class with unchanged list length, a wrong helper phase
input, an altered native paid coefficient and an altered literal Lean paid
coefficient. The tested wrapper SHA-256 is
`b61400bf215832d91f6b6cf04eeab2f8298f6b10a08a0fbd6bc837d1753a69a0`.
`WRAPPER-CONTROLS.json` records the authentic successful baseline and all
rejection messages. These are parser/binding controls; they do not invoke Lean
or substitute for the root task's actual kernel compilation.

The audit identified missing native/phase receipt provenance checks in the
initial wrapper. Those were added before the recorded control run. It also
requested exact phase class sets and actual helper pair/rank bindings instead
of coverage counts alone; these controls exercise the resulting checks.

## Reproduce

From the repository root with the configured global Python 3.14 executable:

```
C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe -B research/kappa-round3-audit-20261022/audit.py
C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe -B research/kappa-round3-audit-20261022/wrapper_controls.py
```

No virtual environment or external Python package is needed. The audit takes
about four seconds and wrapper controls about 42 seconds on the recorded host;
times are diagnostic metadata. Regeneration changes timing fields and hashes
of these audit receipts, not the frozen mathematical inputs.

## Open next questions

* The all-size lifting, helper normalization/adapter, precision, storage/tape,
  compiler transfer, analytic decomposition and recovery obligations remain
  those explicitly retained by the construction. Resolve one actual contract
  if seeking a stronger theorem claim.
* The independent phase check here authenticates and matches the coverage of
  the supplied exact receipts. A separate phase implementation or expanded
  all-column frame-conjugated operator check would strengthen that boundary.
* Any future changed witness must invalidate these hashes and rerun the exact
  patch, operator, census and complete-invoice audit before reusing its result.

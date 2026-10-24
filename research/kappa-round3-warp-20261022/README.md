# Joint helper entrances and native maps

TL;DR: the new local paid profile is
`{1:2201,2:412,3:510,4:127,5:40,8:8}`, with the same productive helper census
`{4:28,7:7,8:47,9:326}` as PR4610. Compared with PR4610, four copies of two
rank-four jobs become rank-three plus rank-five jobs. Strict concavity improves
the paid moment at every real exponent between zero and one. The full p16 price
and Lean proof are supplied in the companion round-three package.

All 408 helper inputs remain arbitrary and independent. The new witness changes
26 helper entrances, 316 scalar contact frames, 20 warp frame pairs and 20 native
G maps. It preserves all main input/output interfaces, every scalar opcode,
coefficient and chronological order, all owned-center jobs, and all helper exits.
All 4,429 frame registry entries are byte-for-byte inherited from PR4610.

Both retained exact interpreters pass all 632 arbitrary-input columns in both
orientations. Exact Clifford admission passes all 20 changed native G operators
on 512 columns with absolute phase, all 180 actual warp classes, 105 new paid
frame pairs, and all 26 changed helper boundaries, in both orientations.
The native scalar allowances remain 158120 forward and 158168 backward.

## Reproduce the mathematical witness

From the repository root, using Python 3.14 and only its standard library:

```sh
python3.14 -B research/kappa-round3-warp-20261022/regenerate.py
python3.14 -B research/kappa-round3-warp-20261022/verify_candidate.py
python3.14 -B research/kappa-round3-warp-20261022/phase_check.py
```

`ACTUAL-WORD.json.gz` is the admitted witness. Its decompressed canonical SHA256
is `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
`PATCH.json` reconstructs every byte of it from the exact frozen PR4610 word.
The patch guards each old boundary/contact before changing it. No discovery
solver is used by these checks. `SOURCES.json` pins inherited sources and phase
evidence, with predecessor attribution retained.

The source-local Windows interpreter for this run is
`C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe`.
No virtual environment was created or activated.

## Discovery and bounded unsuccessful searches

The discovery scripts use SciPy 1.18.1 and NumPy 2.5.4, installed in ignored
`.deps/` using the global interpreter. Admission does not use either package.

1. `line_free_milp.py --operator all --seconds 180` frees all 72 late native map
   contacts, preserving the twelve operators' additional prelude line maps.
   Its 977794 variables and 202730 constraints yield the unchanged old invoice.
2. `helper_line_milp.py --operator all --seconds 180` also frees all 408 helper
   entrances, optimizing the complete paid-minus-productive moment. Its
   1636247 variables and 308777 constraints discover the positive witness.
3. `both_boundary_milp.py --operator all --seconds 180` additionally frees every
   helper exit. Its 2000950 variables and 385938 constraints yield the same new
   paid/helper profile. This separate output is not the frozen witness.

Every enumerated quotient interval in these runs has dimension at most five;
the interval enumerator does not truncate those domains. HiGHS reports floating
finite-model optimality. That report is discovery evidence and is not an exact
ceiling or an impossibility proof for other circuits, words, or interfaces.
Scripts that discover a positive candidate can overwrite their discovery
outputs; the separately frozen actual word and guarded patch remain authoritative.

During this round Pierre-Loic Doulcet's public PR4626 was found independently
proposing a helper621 two-chart change on PR4610, at source head
`c665f908fc991aa558ea8a8cd33e9ad26f97a22d`. Its result is credited and is not
claimed as new here. `combine_621.py` checks the direct combination with the new
joint-map witness. That particular combination worsens the moment; the saved
negative invoice screen does not rule out jointly redesigned combinations.

## Scope, credit and open next questions

These are finite exact circuit/census/phase certificates and scoped Lean
obligations. The full integer-multiplication theorem retains the repository's
analytic decomposition, native supplier, allowed owned-storage erasure,
whole-job normalizers, finite-template closure, precision, prime-avoidance and
exact-recovery assumptions. No measured runtime speedup or independent review
is claimed.

The new lever is to change helper input charts and native maps together. Freeing
only native maps leaves the old invoice unchanged in the tested model. The
helper credit couples interface choices to the paid contact graph; every helper
is charged and credited using its actual entrance and exit.

Open next questions:

- Free the twelve prelude line contracts jointly with late map contacts. A first
  step is an exact simultaneous two-subspace map test. Shared G consistency and
  arbitrary-input semantic replay are the admission blockers.
- Change scalar chronological order or the owned-center walk, then replay the
  whole word. Current solver domains preserve both, so their reported optimum
  does not constrain these directions.
- Prove an exact finite-model dual bound if a ceiling is needed. Floating solver
  status alone supplies no such certificate.

Credit the PR4610 predecessor by Cao Yifan, Cinna Davis's PR4470 native supplier
and cumulative sources, Dugongue's transported warp-frame lemma, zxv's native
and compiler work, Jacob Alan Sussman's mixed-target recursion, and Pierre-Loic
Doulcet's separate PR4626 contribution. Prepared by **Cao Yifan**, with
substantial OpenAI Codex assistance. Apache-2.0.

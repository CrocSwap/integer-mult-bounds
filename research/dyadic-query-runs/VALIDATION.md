# Validation and limits

Executed on macOS arm64 on **2026-10-14 AEDT**, with CPython **3.14.6** and
**3.9.6**. The program and mathematical certificate are identical across
interpreters. No Linux, hosted-CI or proof-assistant result is claimed.

## Focused checks

The normal 3.14.6 run generated the complete receipt. Isolated optimized
execution verified it unchanged on both interpreters:

```sh
python3 -I -O -B research/dyadic-query-runs/verify.py
/usr/bin/python3 -I -O -B research/dyadic-query-runs/verify.py
python3 -I -O -B research/dyadic-query-runs/test_package.py
```

- All **63** declared nonempty index sets pass literal forward/inverse
  Laurent replay, the independently reconstructed graph-component bound
  and both complete native invoices. Their fused query counts total **496**
  versus **576** for the separate-pair baseline. These are finite census
  totals, not an asymptotic or runtime measure.
- All **14** signed native query lowerings pass **84 rational** and **756
  modular** basis columns, literal inverse checks and ordered/unit admission.
  Modular checks use 3, 5, 7, 9, 15, 25, 27, 49 and 81; modulus 15 is an
  additional non-prime-power odd-ring control.
- **228,956** native address comparisons cover the complete six-field
  domains modulo 3 and 5. Each is lifted over all four configurations of
  two physically intervening binary spectator fields. The VALUE replay
  includes three arbitrary dirty roles, **252 forward** and **252 inverse**
  executions. Its complete deterministic output digest is in EVIDENCE.json.
- The independent finite shortest-walk traversal exhausts **15,616 states**
  and **156,672 directed edges**, with position restricted to `[-32,32]` and
  dyadic steps at most 64. All **15** nonempty subsets of indices 0 through
  3 match the theorem. This finite traversal is not the unbounded proof.
- **15** obligation-specific rejection controls and **two positive scope
  controls** distinguish wrong endpoints, invalid operations, unpaid work,
  legal nonoptimal words, nondyadic shortcuts and small-modulus cancellation.
- The package test passes standalone relocation in a path with spaces,
  byte-exact certificate/evidence regeneration and **eight on-disk faults**.
  It checks the expected failure reason, not just a nonzero exit code.
- Every retained source's SHA256 and Git blob digest agrees. All seven
  transitive original source files also match their fetched original Git
  objects at the commits recorded in `vendor/pr840-SOURCES.json`.

The explicit stopping rule was completion of the declared certificate and
bounded-walk domains; neither used adaptive search. The assignment seed 55
selects the five-index example and deterministic dirty inputs. The universal
query optimum is the written argument in PROOF.md, not an extrapolation of
this finite evidence or a machine-checked theorem.

## Repository context

Exact development base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.

```sh
make selected-record-check
python3 -B -m unittest discover -s tests -p 'test_selected_result.py'
git diff --check
```

The selected-record check and all **five** existing selected-result tests pass.
The selected certificate still records PR890 at
`1661957774647029/1000000000000000000`. Only this new research directory is
added; existing sources, `upstream/` and the selected frontier are unchanged.

Publication refresh reached main
`007664306fff84fbb1c9a1b4053b69f439764034`: its eighteen-contribution batch
does not change the selected record. The refreshed queue contains 700 open
PRs through #947; the closest dependency PR840 remains at the exact consumed
head. Its current discussion has no review or comment introducing a changed
contract. PUBLICATION-CONTEXT.json records the overlap scope and heads.
The immediate pre-submission refresh checked 40 recent open PRs through #950
and again found no pinned coordination issue. The complete optimized replay
and selected-record/five-test checks pass at mathematical commit
`282eff4d60bacfe1d0018bc08b22a2e1bf8d5928`. The subsequent claim/publication
update changes documentation and context metadata only.

The required root `make verify` was launched once in an untouched archive of
the exact base, so unrelated regeneration cannot enter this contribution.
Six historical groups completed: community, producers, partial-gauge,
three-stage-cover, paired-cube and recycled-bit. The recycled-bit replay also
passed its three tests. The run was deliberately terminated during the next
entrance-bank group (exit 143) after a direct check of the later mandatory
`make gen4-bank-verify` target established its missing dependency:

```
ModuleNotFoundError: No module named 'sympy'
make: *** [gen4-bank-verify] Error 1
```

That direct gate exited 2. Its selected-record prerequisite passed. The
interpreter also lacks NumPy/SciPy, but no further missing-dependency failure
is inferred. The root suite is **incomplete**, not passed; no dependency
installation or further repository-wide replay was attempted. The standalone
contribution requires only the standard library and its complete checks pass.

## Remaining obligations

No selected-supplier cold replay is claimed, because no selected construction
is changed. No physical selected-supplier integration, common-label compiler,
new frame/owner invoice, bit-precision theorem, all-size tape implementation,
outer analytic improvement or measured runtime is established. The actual
ordinary child and ordered affine stream implementations remain inherited
contracts. Coefficient-dependent work is kept explicit in the recurrence.

# Validation receipt

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Local Linux x86_64, 2026-10-13 UTC. No remote CI or human review is claimed.
New code, deterministic evidence, pins, proof and controls are confined to this
package; no existing generator, supplier, certificate or `upstream/` file changes.

The bounded experiment completed at 04:48 UTC. Dedicated verification and
handoff began at 04:52 UTC, ahead of the originally reserved 05:08 start within
the 40-minute session budget. The claim records assignment seed 23, the initial
screen and the complete stopping rule. Final concurrency review found #722 and
#723; their distinct scopes and #723's concurrent signed-digit result are
explicitly credited. This was an overlap clarification, not an additional
uncompleted investigation.

## Executed checks

| Check | Result |
| --- | --- |
| `python3 -B research/complex-prefix-bounded-dyadic/verify.py`, CPython 3.15.0 | PASS; 4 full primitive replays, 716 native + 9 private formal columns each |
| `/usr/bin/python3.14 -I -O -B research/complex-prefix-bounded-dyadic/verify.py`, CPython 3.14.7 | Same deterministic certificate; PASS |
| CPython 3.12.14, `-I -O -B` with the same verifier | Same deterministic certificate; PASS |
| `ast.parse(..., feature_version=(3,11))` for every package Python file | PASS syntax; Python 3.11 runtime was not run |
| Exact dense three-input replay of all 686 coefficient types | Both pinned PR696 and replacement endpoints/prefix bounds pass |
| Separate forward digit-graph Dijkstra | All 8,256 target/bound pairs for bounds 1 through 128 agree with the backward recurrence |
| Twelve mathematical/alias controls | Every control rejected; overshoot and cost controls check their precise rejection reasons |
| `python3 -B research/complex-prefix-bounded-dyadic/test_package.py` | PASS relocation, gzip-container variation, read-only behavior and four corruption/algorithm controls |
| `make selected-record-check` | PASS selected record, exact κ, original source inventory and proof supplement |
| Package JSON parsing and staged whitespace check | PASS |

The relocated check copies only this package and its 12 pinned repository
inputs, into a temporary path containing spaces. It changes gzip compression
and header time without changing the decompressed payload; reproduction still
passes. Mutations to a pinned source, the vendored PR696 file, the savings
receipt and the doubled-intermediate guard all fail. File snapshots before
and after each verifier invocation agree. No mutation touches the real checkout.

The complete coefficient census records all 686 types and multiplicities; no
sample or timeout is represented as complete coverage. The independent graph
check covers small finite bounds; the written recurrence proof supplies the
restricted-class argument for the larger selected numerators. Full scalar
replay is finite exact rational evidence, not a formal proof of an asymptotic
integer-multiplication theorem.

## Checks intentionally outside this unchanged-supplier scope

No full `make verify`, selected cold rebuild, global invoice/admission replay,
phase/Clifford regeneration, Linux remote CI or Lean build was run. The selected
word, geometry, interfaces and artifacts were not edited. This package checks
an explicit scalar substitution against retained selected outputs, binding
them to the selected SPEC; it does not regenerate their construction. Production
integration of a changed emitter would require the appropriate cold and global
replays and refreshed literal primitive receipts.

All uniform compiler, common-label/mutable-basis, hosting, precision/tape,
recovery, analytic-transfer and bit-supplier obligations remain inherited.

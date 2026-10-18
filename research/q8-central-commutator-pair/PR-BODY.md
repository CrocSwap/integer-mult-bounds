# PR: Quaternion alphabet: central commutator pairs still cost their direct bill (no new kappa)

## Scope

Track `bit-mechanisms`, task card `bit-new-register-model` (scope key `7f5f4426ef796683c485`,
chooser OS nonce `73aa3cb4cec915ba6c0a1125abe1e410`, priority revision 3), scope **refined**
to the card's allowed variation "a specified nonabelian operation family", instantiated as
the quaternion group `Q8`. Exact base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`;
selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

The scoped three-register obstruction (`research/bit-three-register-lower-bound`) and the
dihedral predecessor (`research/bit-dihedral-commutator`,
https://github.com/CrocSwap/integer-mult-bounds/pull/1443) both fix their address group and
state that other address groups are not excluded. This package changes exactly that one
hypothesis: address group `Q8 = {+-1, +-i, +-j, +-k}` instead of `M_3(Q)` / `UT3(F2) = D8`.
The commutator arithmetic differs: `z = xyxy = x^2 = y^2 = -1` is a paid-label square, so
the direct bill is 4 rather than the dihedral 8.

Model: formal `F2[Q8]`, paid labels `x = i`, `y = j` only, paid factors
`D_N(g) = I + ([g]+1)N` with `N = u v^T`, `v^T u = 1`, over `r` scalar registers (6 N / 12
generators at r = 2, 28 N / 56 at r = 3), free scalar `GL_r(F2)` mixing normalized by
augmentation (predecessor's argument; its finite GL-conjugation closure step is rechecked),
arbitrary dirty register inputs, every call charged, no free address maps, no COPY/ERASE, no
clean ancilla. Acceptance is equality in every coefficient of the full group algebra.

## Result

| endpoint | direct bill | exact minimum |
|---|---:|---:|
| r = 2: `diag([z],[z])`, `z = xyxy = x^2 = y^2` | 4 | **4** |
| r = 2: `diag([xy],[yx])` (noncommuting pair, both orderings) | 4 | **4** |
| r = 3: `diag([z],[z],[e])` with one restored dirty register | 4 | **4** |

Scoped negative: no cross-register sharing compression exists in this alphabet. Complete BFS
layer expansion to depth 3 (layers `1,12,110,936` at r = 2 and `1,56,2324,89574` at r = 3,
ball SHA-256 digests in `CERTIFICATE.json`) excludes every word of length at most 3; the
direct four-call word attains 4. Unlike the dihedral generators the Q8 factors are not
involutions (`D_N(x)^2 = D_N(x^2) = D_N(z)` is checked for all generators), so no split
argument is needed.

## Evidence and reproduction

Package: `research/q8-central-commutator-pair/`. Registered replay passes:

```sh
python3.12 scripts/research_package.py --package research/q8-central-commutator-pair
# PASS_REGISTERED_RESEARCH_PACKAGE research/q8-central-commutator-pair outcome=completed
python -I -O -B research/q8-central-commutator-pair/verify.py
# PASS_Q8_CENTRAL_COMMUTATOR diag_z_z_r2:4 diag_xy_yx_r2:4 diag_z_z_e_r3:4
#   r2_layers=[1, 12, 110, 936] r3_layers=[1, 56, 2324, 89574] no_new_kappa
```

The verifier recomputes everything from scratch (stdlib only) and checks: Q8 group laws
exhaustively plus agreement of two independent quaternion multiplications; rank-one
idempotent counts 6 / 28 and idempotence; `D_N(g)^2 = D_N(g^2)`; `GL_2(F2)` (order 6) and
`GL_3(F2)` (order 168) conjugation closure of the generator sets; complete BFS layer sizes
and ball digests; engine A (bitmask convolution) and engine B (independent frozenset formal
matrices with Hamilton 4-tuple multiplication) agree on every witness and direct word;
omission controls (every single-call deletion of each direct word misses, 12 controls);
known-distance controls (`I` at 0, `diag([x],[e])` at 1, `diag([z],[e])` at 2); mutated-target
failure control; certificate equality. `scripts/research_package.py --check-only` reports
`PASS_PACKAGE_METADATA_AND_PINS`. The `tests/test_research_*.py` suite passes (42 tests OK,
2 skipped).

## Limitations (stated, not checked)

No kappa, supplier, moment or frontier change is claimed; the bit side does not bind and no
physical invoice, native replay, hosting, precision or analytic obligation is invoked. The
result is exact only for this alphabet (labels `x, y`, these endpoints, r in {2,3}): a failed
search is a result about the searched domain, not an impossibility theorem. Not a
proof-assistant verification. The free-mixing augmentation normalization is inherited from
the predecessors; only its finite closure step is rechecked here.

## Overlap

Refreshed `scripts/find_overlap.py` with the concrete object terms (2026-10-14T10:53Z,
complete pagination): no `Q8` object in open PRs, discussions or local packages besides
this one. Deliberately distinct from the `F2[GL2(F2)]` coordinate-CNOT/SWAP line (order-six
group, isomorphic to `S3`), the `UT3/D8` commutator line (closed at `4k` for all registers;
third dirty register closed negatively), and the `S4`/`S5`/`AGL2`/`GL3` target searches of
2026-10-14. Coordination claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18921583.

## Credit

Prepared by **Aaron Wang**, with help from opencode (substantial AI assistance disclosed; no
independent human review). Apache-2.0. Model, normalization and presentation follow
woklerx's `research/bit-dihedral-commutator`
(https://github.com/CrocSwap/integer-mult-bounds/pull/1443), which explicitly leaves other
address groups open. Scalar-idempotent register model: eumemic's PR 288 section 1.2; the
register-model lineage credits Ali Romman (https://github.com/CrocSwap/integer-mult-bounds/pull/468),
Gareth Davidson (https://github.com/CrocSwap/integer-mult-bounds/pull/1333) and the pinned
three-register note (`research/bit-three-register-lower-bound`). Frozen sources and
`upstream/` are unchanged.

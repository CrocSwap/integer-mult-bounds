# Minimal joint-output connector charge

**Scoped connector-alphabet experiment; no new κ or supplier claim.** This
refines `connector-alphabet-change` to the smallest nonzero instance of one
output-side operation: two distinct output maps are applied to the same
connector in one joint readout record. The existing pair-source operation is
already treated in [PR #2056](../connector-pair-source-path-seed2cdb/README.md),
so this package checks the complementary output direction.

## Exact interface change

The fixed alphabet permits a single-target readout
`A_i: y_i += A_i z`. This experiment adds exactly one family

```text
J_ik: (y_i, y_k) += (A_i z, A_k z),    i != k
```

`J_ik` reads the one connector `z`, adds into two distinct output rows, leaves
`z` and all sources unchanged, restores its private scratch and tape heads, and
does not inspect either old target. Both maps are arbitrary fixed
`F_2`-linear maps. The operation is a **one-record premise change**: it must
account for both coefficient/map evaluations, both target updates, connector
routing, scratch restoration and head returns. Nothing in this package claims
that a real supplier currently implements that fused record.

## Smallest dirty-state construction

Use one source `x`, one arbitrarily dirty connector `z`, and two arbitrarily
dirty targets `y_i,y_k`. Let `B` be the source map and let the requested outputs
be `A_i Bx` and `A_k Bx`. Compare these schedules:

```text
single-target alphabet:  B, A_i, A_k, B, A_i, A_k
joint-output alphabet:   J_ik, B, J_ik, B
```

Write `s = Bx` and let the initial connector be any `z0`. In the first
schedule, each target receives `A_r(z0+s) + A_r(z0) = A_r(s)`. In the second,
each receives `A_r(z0) + A_r(z0+s) = A_r(s)`. Both schedules leave `z=z0`;
neither changes `x`. This uses only additivity over `F_2`; no invertibility,
commutation, clean-row assumption or observation of intermediate outputs is
needed. The instance is minimal for this operation: one source gives a
nonzero requested term, and two distinct targets are required to exercise
`J_ik`.

## Complete cost

Let `c_B`, `c_i`, and `c_k` be the complete map-evaluation costs per additive
call, excluding root dispatch. They include the source/coefficient access,
arithmetic, target update, scratch restoration and head return. Let `D` be the
cost of one root record. Charge a joint readout as

```text
cost(J_ik) = c_i + c_k + D + phi,
```

where `phi >= 0` is any extra shared-routing, fusion, storage or restoration
overhead not already counted in those two complete map costs or the one root
record. This explicitly pays for both `A` maps and targets.

| Schedule | Map evaluations | Root records | Complete bill |
|---|---|---:|---|
| Original alphabet | `2 c_B + 2 c_i + 2 c_k` | 6 | `2 c_B + 2 c_i + 2 c_k + 6D` |
| With `J_ik` | `2 c_B + 2 c_i + 2 c_k` | 4 | `2 c_B + 2 c_i + 2 c_k + 4D + 2phi` |

Therefore `C_joint - C_single = 2(phi-D)`. The joint operation is favorable
exactly when `phi < D`; at `phi = D` it ties, and above that it loses. If `J`
is implemented by invoking two ordinary root-level `A` calls, that pays the
second dispatch (`phi = D`) and yields no saving. A true one-record
implementation with no extra fusion surcharge would save `2D`, but remains an
unproved implementation obligation. No leaf-map work is removed in this
minimal instance.

## Verification

```sh
python3 -I -B research/joint-output-connector-minimal-charge-247794/verify.py
```

The standard-library checker enumerates all `16^3 * 4^4 = 1,048,576`
combinations of two-dimensional `F_2` maps `B,A_i,A_k` and arbitrary data
`x,z,y_i,y_k`. It checks both the output identity and connector restoration.
Three faulty schedules (missing one output update, missing the first dirty
cancellation readout, or missing final connector restoration) must fail. It
also checks the exact symbolic cost delta at `phi/D` values 0, 1 and 2. The
finite enumeration is a verifier check; the dimension-independent claim above
follows from the displayed linear identity.

Registered replay and source pins:

```sh
python3 scripts/research_package.py --package research/joint-output-connector-minimal-charge-247794 --check-only
python3.12 scripts/research_package.py --package research/joint-output-connector-minimal-charge-247794
```

The package is pinned to base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`,
priority revision 6. The selected record remains
`κ = 836330098538459/500000000000000000`; this experiment changes no selected
source, supplier, or frontier. It does not establish a real `J_ik` compiler,
an optimized caller, a reduced recursive interface tariff, or a new
multiplication bound.

## Overlap and credit

The current five-source scope map distinguishes fixed single-output calls,
pair-source calls and connector frames. Its pair-source predecessor already
accounts for two source accesses and arbitrary dirty replay. The live PR #3779
at intake concerns overlapping six-window gate counts and source restoration;
it does not change this one-source/two-target alphabet definition. The offline
overlap search found no direct joint-output match, and current handoff comments
were checked for the same operation. Open PR #3604 (head
`7156bb98f78b7492002010e8729d59fe38b92e60`) is adjacent: it co-delivers
specialized P112 tetrad products to a fused port and a source-side dirty
correction, and leaves the native schedule and full scalar tariff open. This
package does not re-audit that factorization; `J_ik` is the generic operation
that applies two arbitrary `A` maps to two targets from the same connector, and
the cost calculation deliberately grants no shared-product leaf discount.
These checks are not proof of novelty.

Credit Adam Gall and the contributors to the fixed-alphabet tariff and
pair-source connector results; this note does not supersede or restate their
theorems. Prepared by OpenAI Codex with substantial assistance. Apache-2.0.

## Open next questions

Can a caller-bound stacked map realize `J_ik` with all common-label, input
routing, output ownership, scratch and head costs included, at an overhead
`phi < D`? The next step is to instantiate one real supplier port and compare
its measured complete bill with the threshold above. Without such a caller and
tariff, do not extend this construction or infer a supplier improvement.

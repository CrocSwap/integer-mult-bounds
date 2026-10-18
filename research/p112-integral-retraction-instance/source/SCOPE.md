# Exact proposition, source connection, and remaining obligations

## 1. Acceptance boundary

The new Lean files are a **SOURCE ONLY / NOT YET KERNEL CHECKED** candidate.
They contain actual proof bodies, including a closed numerical certificate
term, but successful elaboration and kernel checking have not been observed by
the producer. No success follows merely from supplying these files. The
operator must compile every positive unit without errors/warnings, inspect the
complete axiom census, and run the intended failure control within the caps.

The request reports the predecessor's successful exact-toolchain local replay.
The delivered dependency is the requested published 48,758-byte version, not a
silently modified source. Its existing status/attribution text and all 159 axiom
queries are retained. Its report about a predecessor replay does not apply to
`P112Cert.certificate` or any other newly supplied declaration.

## 2. Canonical numerical object

`P112.json` is the complete supplied subobject for
`/units/P112/gluing_lattice_certificate`. Its canonical bytes and hash are checked
before generation. The four matrices have exactly 288/104/33/104 rows and
104/33/104/288 columns, respectively. Their stored entry counts are
1,152/195/66/111. Every source row and every within-row entry keeps its position.

Each emitted entry is `(⟨column, by decide⟩, (coefficient : Int))`. Thus columns
have explicit bounds proofs; the converter does not rely on Fin numeral wrap-
around. The source validator rejects out-of-range columns, duplicates, unsorted
columns, zero stored coefficients, Boolean-as-integer values, duplicate JSON
keys, missing/extra schema fields, wrong dimensions, or a nonpinned byte stream.

Balanced selectors `M_entries`, `P_entries`, `Q_entries`, `W_entries` dispatch on
the original zero-based row index. For every valid index the corresponding leaf
is the original literal row. A source-converter check enumerates those paths;
exact regeneration checks the full tree text, not just its leaf comments.
An independent inverse literal parser reconstructs all sparse rows and every
metadata field from the emitted constants, and compares the full resulting
object with the input. The reconstructed canonical JSON also has the original
13,183-byte hash. `BINDING.tsv` separately records every scalar and container
node. These checks deliberately include metadata that is not needed for the
three algebraic identities.

The metadata constants `anchors`, `basePairRepresentatives`, `coordinateLabels`,
`freeParameters`, `parameterClassCount`, `gPoints`, and `rankMetadata` preserve
source values; their presence asserts no geometric correctness. In particular,
`rankMetadata := 71` is just an integer copied from JSON, **not** a theorem about
rank. No rank operation, rank API, or numeric-rank proposition is defined here.

The full 1,019,927-byte saved certificate was not supplied as a separate file to
this producer and was not rehashed here. Its full-certificate digest and the
operator's extraction history are retained as reported provenance only.

## 3. Small sound adapter, not a replacement matrix product

All universal algebra comes from the unmodified PR1497 namespace:

```lean
abbrev Row (n : Nat) := Fin n → Int
abbrev Mat (m n : Nat) := Fin m → Fin n → Int
```

The delivered matrices are actual objects of these types, not arrays that only
look like them. `Sparse.row` is the finite list's ordinary integer linear
combination of the dependency's coordinate basis rows. For each column its
meaning is formally exposed by `P112Cert.Sparse.row_apply`:

```text
row xs j = xs.foldr (fun e s => (if j = e.1 then e.2 else 0) + s) 0.
```

The pinned lists have distinct columns, so this is their ordinary sparse
interpretation: the listed coefficient at its column and zero when absent.
No source entry is dropped, cancelled, sorted, or simplified by the converter.

`Sparse.eval xs B` only sums `coefficient * B row column` over the short list.
It is connected to the exact imported recursive finite sum by the proved
function equality

```lean
P112Cert.Sparse.rowMul_row
  (xs : List (Fin n × Int)) (B : PR1497.Mat n d) :
  PR1497.rowMul (P112Cert.Sparse.row xs) B = P112Cert.Sparse.eval xs B
```

The proof is structural induction on the list. The empty case uses the
inherited `Rows.rowMul_zero_left`. The successor case uses the inherited
`Rows.rowMul_add` and `Rows.rowMul_basis`, and the small derived scalar-linearity
lemma `Sparse.rowMul_scale`. That lemma is derived from the already proved
`Rows.rowHom`/`Hom.map_zsmul` and `Rows.row_zsmul`, not from an assumed scalar
preservation field. Thus the dense finite sum is avoided computationally, not
redefined or postulated away.

The only other new generic helper is `Sparse.allFinAdd`, a short wrapper around
core `Fin.addCases`. It assembles two proved finite index ranges; it makes no
matrix or group assumption. The new helper file has two definitions and four
theorems, with a query for every one. There is no new sparse-matrix algebra
library, custom evaluator, proof macro, or general algebra-law structure.

## 4. Complete finite proof obligations

The staged sources provide these complete row families:

| Family | Named row theorems | Columns in each row | Scalar obligations |
|---|---:|---:|---:|
| `mp_row_000` through `mp_row_287` | 288 | 33 | 9,504 |
| `qp_row_000` through `qp_row_032` | 33 | 33 | 1,089 |
| `residual_row_000` through `residual_row_103` | 104 | 104 | 10,816 |

Each theorem invokes ordinary `decide` on a closed proposition
quantified over the entire indicated `Fin` column range. Its proof must still
be checked by the operator's kernel run. A Python calculation
is not passed as a proof. There are no Boolean-checker soundness assumptions,
precomputed theorem receipts, or certificates accepted by unchecked evaluation.
The intended 21,409 scalar obligations are not replaced by sampled cells.

In `P112Certificate.lean`, core `Fin.forall_fin_one` and the proved
`Sparse.allFinAdd` assemble the row proofs using a balanced tree. Each leaf's
finite index reduces to its original numeric row. This yields
`mp_sparse_all`, `qp_sparse_all`, and `residual_sparse_all` over every row index.
Function extensionality plus `Sparse.rowMul_row` then proves the actual imported
matrix identities `P112Cert.mp`, `P112Cert.qp`, and `P112Cert.residual`.

The final declaration is a closed proof term:

```lean
theorem P112Cert.certificate :
    PR1497.MatrixIdentities P112Cert.M P112Cert.P P112Cert.Q P112Cert.W
```

Its proof is exactly the structure assembled from those three proved fields.
No `h : MatrixIdentities ...` binder occurs in the claimed finite result.
Neither lattice/kernel equality nor reconstruction is postulated or added as a
field, and no smaller matrix fixture is substituted for the P112 data.

## 5. Existing bridge conclusions bound to these constants

`P112Consequences.lean` instantiates only inherited results. The significant
interfaces are listed below; their exact names, locations, and declaration
kinds are in `DECLARATIONS.tsv`.

`P112Cert.lattice_eq_kernel` states, for every `v : Row 104`, that the **image**
`∃ z : Row 288, rowMul z M = v` is equivalent to `rowMul v P = 0`.
`P112Cert.phi_surjective` gives a preimage for every `Row 33` parameter vector.
`P112Cert.lattice_saturated` keeps the explicit nonzero-integer-multiple premise
and uses the inherited integral torsion-freeness proof.

`P112Cert.quotientIso` is an `AddIso` between the inherited actual image-
difference quotient group and `rowGroup 33`. `quotient_relation` exposes that
`v - w` is an integer row image, rather than defining the quotient by the desired
kernel conclusion. The forward-on-representative and inverse-on-parameter
lemmas identify the maps as `[v] ↦ vP` and `z ↦ [zQ]`. Both left and right inverse
equations are instantiated. The definition is an inherited proved isomorphism,
not a new assumed isomorphism field.

The monomial declarations quantify over arbitrary `D : Type u` and an explicit
ordinary `PR1497.CommGroup D`. `reconstruction`, `reconstruct_coordinate`, and
`unique_parameterization` also retain

```lean
hx : PR1497.MonomialBridge.Relations G P112Cert.M x
```

which literally means that **each of the 288 relation-row monomials equals
`G.one`**. They do not assume annihilation of the entire span: that bridge is
already proved in the inherited source. `converse_relations` and
`parameters_recover` apply to arbitrary 33-tuples of parameters. The inherited
`residual_relations_formula` is instantiated with the actual W coefficients,
without assuming that relation-row values are one. These declarations still
refer to actual finite products and signed powers, not arbitrary characters
with reconstruction built into their laws.

Nothing here constructs nonzero field elements, a units group, field coercions,
or a Laurent-scheme interpretation. The existence of a lawful group or the
geometric truth of the individual relation hypotheses is not inferred merely
from the numerical integer identities.

## 6. Bounded kernel strategy and what a timeout means

The candidate deliberately avoids a single dense decision procedure. In the
four dense products there are 4,573,608 scalar multiplication summands. The
proved left-row adapter reduces the corresponding listed coefficient terms to
72,018, before accounting for right-row lookup. That is a source-specific
arithmetic work comparison, **not a measured speedup or runtime guarantee**.

Balanced dispatch has depth at most 9 for M, 7 for P/W, and 6 for Q. Balanced
proof assembly likewise has depth at most 9/6/7. One decision handles only one
complete row of at most 104 columns. A compilation unit contains at most 16
MP/QP row theorems or 8 residual row theorems. The unchanged dependency is
compiled first, followed by the adapter/data, 34 row-stage files, certificate,
consequences, and damaged-certificate proofs.

Every new unit sets `maxRecDepth 4096` and `maxHeartbeats 1000000`; neither is
zero. The external runner caps each process at 120 seconds and the complete
successor at 600 seconds, excluding only the unchanged dependency stage. The
total includes preflight and acceptance bookkeeping. The runner terminates the
process group on timeout, records the exact stopped unit, and never retries
with raised limits. On an operator interruption it also stops the child process.

No authoring-runtime Lean executable was found or executed. Whether these
proof scripts elaborate and fit the resource budget is therefore the remaining
empirical obligation. If a stage times out, already accepted row theorems may
be reported as partial finite obligations, but the full certificate or final
applications must not be called kernel checked. An elaboration error must be
repaired in the new files, not by altering the accepted dependency or assuming
the failed identity. There is no assertion that an unexecuted timing cap was met.

## 7. Genuine mathematical negative control

The original sparse row W[5] is exactly `[[0,1]]`. The control changes it to
`[[0,-1]]` and retains every other row. In ordinary integer matrices:

```text
(I_104 - PQ)[5,0] = 1
(W_bad M)[5,0]    = -1.
```

`P112Cert.Damaged.residual_entry` and `damaged_product_entry` contain Lean proof
bodies for these statements through the same sound adapter. `not_residual`
uses the entry discrepancy to contradict the whole residual identity, and
`no_certificate` refutes `MatrixIdentities M P Q W_bad`. No malformed type or
missing-file premise is involved. MP and QP are unaffected because M/P/Q are
not changed.

The separate compile-fail fixture imports these positive proofs and attempts
the false residual-entry equality. After rewriting, ordinary `decide` must
reject `1 = -1`. Acceptance requires exactly that diagnostic, exit code 1, no
output `.olean`, and no unrelated diagnostics. The Python producer independently
observed four differing residual cells: (5,0), (5,1), (5,4), (5,5). The **Lean**
positive/negative controls were not run by the producer.

The request identifies PR1497 `verify.py` lines 605–607 as a W-corruption-control
precedent. The exact `(5,0)` sign flip and proof here are source-specific new
control code, not a claim to have inspected or duplicated the old control's
precise mutation.

## 8. Trust, axiom census, and omissions

All source-named declarations are enumerated: 477 new queries and 159 unchanged
inherited queries. There are no manually declared private auxiliaries. Compiler-
generated eliminators/recursors, if any, are covered transitively by the parent
queries; no fresh proof axiom is inserted. Ordinary `decide` is used without
native or unchecked execution options. The source guard and Python parser are
supplementary checks, not a substitute for source audit or the Lean kernel.

The replay accepts only the allowed foundational set `propext`, `Quot.sound`,
and `Classical.choice`, and requires a complete census after a successful fresh
compilation. No observed new axiom list is asserted in this delivery. Failed
elaboration followed by printed axiom messages is categorically not acceptance.

Excluded: E8 roots and geometric generator correctness; class completeness,
coverage, anchors' geometric roles, source-relation geometric validity; actual
field/Units adapters and nonzero-element premises; numeric rank; P120; zero
exclusion; local Lemma 5; decoder K; helper reduction; paid invoices; kappa;
full multiplication/analytic/hosting/precision/tape theorems; frontier changes.
This work does not establish novelty, terminate another study, or post any
external update. It is a finite source-binding successor to existing work.

## 9. Sources and credit

The mathematical/finite source pins and full lineage are recorded in
`PROVENANCE.json`. The requested PR1610/PR1497 repository contents were supplied
in the prompt; no claim of fetching their full audit or saved certificate is
made. During development, only official Lean source at the exact required
commit was consulted online for the core finite-index and ordinary decision
interfaces:

- https://raw.githubusercontent.com/leanprover/lean4/d024af099ca4bf2c86f649261ebf59565dc8c622/src/Init/Data/Fin/Basic.lean
- https://raw.githubusercontent.com/leanprover/lean4/d024af099ca4bf2c86f649261ebf59565dc8c622/src/Init/Data/Fin/Lemmas.lean
- https://raw.githubusercontent.com/leanprover/lean4/d024af099ca4bf2c86f649261ebf59565dc8c622/src/Lean/Elab/Tactic/Decide.lean

The existing `check_axioms.py` parser was retained from the actual earlier
repair archive, with fresh tests and strict compiler-status gates in `replay.py`.
The new converter, inverse parser, adapter, balanced proof assembly, staged
Lean declarations, final applications, and mathematical corruption proof are
new deliverables. Their proof/source assistance is attributed to GPT-6 Pro
through ChatGPT using the operator-selected label, not a more-specific backend
claim. Andrey Mas and the prior PR1497/PR1610 audit/bridge, Codex coordination/
auditing/replay, and PR1212/PR717/PR968 lineage are credited separately. This is
not independent human verification. Apache-2.0.

# PR4610 scalar-order contract and changed phase-interface research

The scalar-order comment is addressed by [COMMENT-ASSESSMENT.md](COMMENT-ASSESSMENT.md).
Matarener reports bounded no-gain evidence with native warp frames fixed. The
old word received exact MILP and plateau experiments; the current `1eb8da6cf`
word received the K-through-8 window screen. This package does not rerun that
family or infer a global optimum from it.

**Complete result:** every one-edge phase defect in the declared fixed graph is
unprofitable. The full scan covers all 34,638 graph edges by exact proof
dependency reduction and 2,008 full-system deletions. All 100 helper-changing
cases are single-helper boundary pre/postprocessing, including their entire
phase spaces. A fresh Lean module proves the conditional all-rank cost lemma.
This supplies no new construction improvement or kappa.

New work tests changed phase interfaces beyond the unchanged-rank, frozen-owned
boundary conditions of [Cinna Davis's PR4665](https://github.com/CrocSwap/integer-mult-bounds/pull/4665),
using [Dugongue's PR4654 symmetric-form grammar](https://github.com/CrocSwap/integer-mult-bounds/pull/4654).
No phase construction or higher kappa has been admitted here. Exact source
copies and API provenance are in `SOURCES.json`; upstream bytes, including
their original line endings, are preserved and checked against Git blob IDs.

## Owned-center relaxation

The actual eight owned centers have chart dimensions 8 to 0. Their phase-form
intersection is zero, so changing the source form alone does not increase their
relative Fourier rank. Clearing a zero numerical field is compatible with any
linear address gauge. This motivates testing the source COPY gauges with the
owned-contact freeze removed, while retaining main and explicit adapter
boundaries and all unchanged paid/warp ranks.

`owned_phase_probe.py` imports PR4665's exact graph and forms implementation.
It changes exactly one AST-local boundary predicate and verifies that every
node, frame, edge, shared G action, and helper identity remains identical.
The relaxed frozen set is a subset of the original set. Explicit adapter and
main freezes still apply when an owned contact coincides with one of them.

Result: 196 formerly owned-only frozen contacts are released, mostly of
dimension zero. There are 311,072 form coordinates and 559,088 nontrivial
homogeneous equations. Exact equality substitution discharges every equation.
The only 288 unconstrained coordinates occur at eight isolated rank-eight
clear nodes with no incident graph edge. Every productive helper phase
difference is still forced zero. Thus this optimistic owned relaxation supplies
no productive phase gain at unchanged paid/warp ranks. This extends the boundary
test; it does not establish a universal phase obstruction.

## Explicitly paid defects

The next gate permits the complete compatibility block of one physical edge
to change while keeping all other edge ranks fixed. Such an edge may be a
previously positive-rank paid climb, a formerly rank-zero chart transition, or
a formerly monomial warp. Its extra rank must be charged. A candidate is a
node-dependent collection of symmetric forms, not a fixed ambient form shared
at every contact.

`exact_defect_probe.py` first records an explicit dependency DAG proving every
old helper coefficient query zero. Removing an edge absent from every such
proof cannot change any helper query. This safely reduces the 34,638 physical
edges to 2,008 candidate blocks. For each candidate, the complete exact system
is reconstructed with only that block removed, equality substitution is closed,
and any residual system is Gaussian-eliminated over F2.

For a feasible direction the checker reconstructs a primal kernel, substitutes
its emitted representative into every retained original equation, and computes
the exact relative form ranks at every helper and the changed physical edge.
It also enumerates every rank-one defect matrix in the relevant kernel image,
allowing its induced node forms to vary by actual transport. Kernel basis
representatives supplement this rank-one enumeration. This is not exhaustive
optimization over all higher-rank combinations.

The original pair-only rollback relaxation (`one_defect_probe.py`) was too
weak: omitting higher-arity equations left every edge potentially useful. That
screen is retained as negative methodological evidence, not a useful bound or
feasibility certificate.

The completed scan found 100 helper-changing edge blocks: 50 entrance and
50 exit cases. Every one is an originally rank-zero edge at the corresponding
helper boundary. All 1,908 other proof-relevant deletions leave every helper
phase query forced zero; edges outside the 2,008 candidates are excluded by
their explicit unaffected zero proofs. No positive-rank paid edge or native
warp can supply helper phase gain when it is the sole allowed defect.

For all 100 feasible cases, `materialize_forms.py` examines **every** surviving
coordinate, independently of the sampled candidate selection. No residual
equations remain. Apart from isolated clear gauges, the whole kernel is confined
to exactly one helper entrance or exit node. This is a complete linear-space
support statement, not an inference from testing basis vectors. There are
41 affected H8 helpers, seven H7 helpers and two H4 helpers, each with an entrance
and exit edge. Other helper intersections are zero and cannot gain phase rank.

Let `h>0` be the boundary form's rank. Its formerly rank-zero physical edge now
costs `h^t`. The helper's extra rank `d` is the rank of that form restricted to
its entrance space, so `0<=d<=h`. For its old rank `g>0` and `0<t<1`,

```
(g+d)^t-g^t <= (g+h)^t-g^t < h^t.
```

Thus **every rank**, including unsearched higher-rank combinations, is
unprofitable throughout this one-edge family. Pure isolated clear gauges change
no helper and supply no reward. This conclusion follows from exact whole-kernel
support plus the general inequality; it does not promote the rank-one trial
enumeration to an exhaustive search of all forms.

The 100 emitted representatives are also evaluated independently by
`verify_forms.py`. It uses separate coordinate enumeration and binary matrix
elimination, and reuses no equality solver. All graph edges, fixed boundaries,
and helper form ranks match. Omitting the phase, mispricing the paid rank and
inflating helper gain are rejected. Their literal forms are in
`FORMS-WITNESSES.json`; every representative raises one helper H4/H7/H8 by one
and pays a rank-one job. The least-negative tested local surplus is approximately
`-0.0075365324171` (H4 to H5), before multiplying by 18.

`invoice.py` rebuilds every emitted candidate's full local and whole-controller
target/paid profiles, retaining all 18 local invocations and every unchanged
controller charge. It evaluates the moment difference with the independent
rational interval engine at the current tested exponent. The invoice assumes
the emitted form ranks and is not a native endpoint or absolute-phase proof.
All 100 complete invoices are strictly negative at the tested exponent.

`Preprocessing.lean` freshly proves strict real-power subadditivity, the
conditional one-helper inequality, and its positive-multiplicity version,
using four axiom reports. Its proof factors powers with a negative exponent;
it is distinct from the parent's independent strict-concavity proof. Only the
analytic implication is Lean-verified. Python graph extraction, finite kernel
classification, rank formulas and native semantics are not thereby formalized.

## Controls, reproduction, and proof boundary

`controls.py` checks 896 proof dependencies against exact Gaussian
edge-deletion counterfactuals (the receipt records the final count). It shuffles
equations before substitution, checks a decisive higher-arity dependency and
corrupts a temporary copy of an actual pinned source; the actual probe's source
authentication rejects it. Temporary files are confined to `.scratch`.

From the checkout root, using the global Python 3.14 executable and assertions
enabled:

The fast frozen evidence check is `check_bundle.py`. The following commands
recompute the research; the full exact scan took about 15 minutes here.
Timing fields and fresh Lean metadata may differ on replay. After deliberately
recomputing coherent receipts, `check_bundle.py --write-manifest` explicitly
refreshes their aggregate hashes; the default mode verifies the existing freeze.

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/owned_phase_probe.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/exact_defect_probe.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/materialize_forms.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/verify_forms.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/invoice.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/controls.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/verify_lean.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-scalar-contract-20261022/check_bundle.py --write-manifest
```

A profitable rank witness would still require all-column arbitrary-input native
replay, literal absolute phases, whole-job helper normalizers, and the complete
compiler/outer transfer. Tensoring the columnwise phase schedule cannot be
replaced by one uncharged global Pauli phase. No such admission or Lean
multiplication theorem is asserted by these phase-system calculations.

The scope remains fixed subspaces, scalar chronology, logical G maps, main and
explicit adapter boundaries, with all owned-contact phases optimistically
released. A profitable phase schedule must change at least two physical edge
ranks in this model, or escape another listed condition. The result does not
rule out joint paid defects, changed native maps/subspaces/scalar words,
different main or adapter contracts, or a new recursive controller.

Prepared by Cao Yifan with substantial OpenAI Codex assistance, Apache-2.0.
Credit Matarener's commuting-window experiments; Dugongue's source-aware phase
grammar and paid cut model; Cinna Davis's exact rigidity implementation and
supplier/controller lineage; the PR4610 native word; zxv, Jacob Alan Sussman,
and the retained E8, scalar, Clifford, native, precision, and compiler authors.
Classical symmetric forms, exact binary elimination, and dependency DAGs are
not claimed as new mathematics.

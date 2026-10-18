# Exact tariff for a bipartite commutator grid

**Exact abstract construction and lower bound; no new `kappa`.** In the
class-two group `H(m,n)` with generators `x_i` and `y_j`, let each selected
edge `(i,j)` carry `p_ij` distinct dirty target roles for the central
commutator `z_ij=x_i y_j x_i y_j`. Among paid factors
`I+([g]+[1])N`, for the listed generators and arbitrary rank-one binary
matrices `N`, the exact minimum is `4 Σ p_ij` for every finite number of
dirty registers. The direct edgewise word attains this bill; the proof shows
that no labels can be shared across the bipartite incidence pattern to reduce
it. The first cyclic case `K2,2` has four distinct outputs and exact cost 16.

The object extends the shared-middle rank-nullity pattern of the three-label
UT4 path result to a complete bipartite commutator incidence model. One
`UT3(F2)` quotient per active edge and its contragredient expose each edge
target. For each generator, the disjoint
incident target spaces force matching column and row span dimensions; one
rank-nullity inequality per generator sums to `4 Σ p_ij`. The complete
parameterized proof is in [PROOF.md](PROOF.md).

## Cost and limits

The local tariff counts every rank-one factor occurrence in the direct word.
The model permits arbitrary free scalar
`GL_r(F2)` mixing and normalizes it by augmentation; it has arbitrary dirty
register inputs and no free address maps, clean roles, COPY, or ERASE. These
are formal group-algebra calls only. Source access, physical frame changes,
hosting, copying, restoration, precision, interfaces, supplier realization,
and recursive-moment charges have no representation here. The exact local
minimum is therefore not a supplier improvement or a selected-`kappa`
change.

The pinned research baseline returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
and identifies the complex supplier as currently binding. That is a source
binding/arithmetic check only; this package does not replay or modify the
selected supplier.

The verifier constructs the 256-element `H(2,2)` multiplication table,
checks each of four edge quotients and its dual on all 256-squared group-pair
inputs, verifies the
16-call `K2,2` word in the full formal algebra, checks a weighted six-target
instance, rejects each one-call omission, and rejects a changed edge label.
It does not search for words: the all-finite-graph lower bound comes from the
written quotient/rank-nullity proof.

## Reproduce

From repository root, using Python 3.12 and the standard library:

```sh
python3 scripts/research_package.py --package research/heisenberg-commutator-incidence-seedb054 --check-only
python3.12 scripts/research_package.py --package research/heisenberg-commutator-incidence-seedb054
```

Direct local check, also using only the standard library:

```sh
python3 -I -B research/heisenberg-commutator-incidence-seedb054/verify.py
```

Expected result:

```text
PASS_HEISENBERG_BIPARTITE_COMMUTATOR group=256 edge_quotient_pairs=262144 K22_targets=4 calls=16 omission_controls=16 dirty_spectator=preserved weighted_targets=6 calls=24 wrong_label=rejected
```

The assigned base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Exact
predecessor file hashes and historical catalogue/selected provenance are in
[SOURCES.json](SOURCES.json); the required replay inputs are declared in
[VERIFY.json](VERIFY.json). The fresh complete overlap snapshot and nearby
claims are in [OVERLAP.json](OVERLAP.json). The scope claim was posted at
[Discussion #1167, comment #18938788](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18938788).

## Open next questions

Can one of these abstract central-commutator words be embedded in a concrete
bit supplier with a complete favorable source, frame, copy, hosting,
restoration, precision, and interface bill? A feasible first step is to map
one `H(2,2)` label operation to a pinned supplier boundary and charge every
role transition. The blocker is that no such implementation or recursive
profile is supplied here.

## Attribution

The normalized register model and the preceding shared-middle UT4 tariff are
credited to their cited authors and [merged UT4 mixed-root package](../ut4-mixed-root-tariffs/README.md).
The new statement is the bipartite graph incidence tariff, with `K2,2` as its
first cyclic case. Prepared by OpenAI Codex with substantial GPT-6 assistance
in selection, derivation, exact implementation, verification, and writing;
no independent human review or proof-kernel verification is claimed.
Apache-2.0.

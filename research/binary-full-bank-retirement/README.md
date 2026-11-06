# Full-bank and changed-history bounds for binary retirement

**No new κ.** This package proves structural limits on fragmenting the binary supplier's paid idles. It enlarges #6726's auxiliary-projector obstruction, prices the actual cost of central-dependent bases, and excludes several redesigned histories. These are scoped mathematical results, not a global optimum or supplier admission.

## Results

- [PROOF.md](PROOF.md) excludes ordinary full-bank retirement at the completed-left-child cut, at arbitrary coupled width and with arbitrary auxiliary prefix K, including singular or S-dependent K. Ordinary input/output/cut bases may mix all four banks.
- A basis and its restoration require at least one new rank-one thin query per retired channel, including mixed L/SL prefixes. Each fragment earns less than one query. An exact two-channel escape attains the query-count floor with one forward and one inverse query; counting only the forward direction would be wrong.
- [HEADER-SATURATION.md](HEADER-SATURATION.md) extends the obstruction to changed histories with the original three-query header, positive unit-exponent body factors and atomic native query/body stages. Determinants force rank saturation. Single fragments and mixed two-fragment gains cannot pay the necessary fourth query. Its coupled three-block extension is an algebraic carrier bound, with no automatic added-block price inference.
- [INTERLEAVED-TWO-MODULES.md](INTERLEAVED-TWO-MODULES.md) separately excludes a single fragment obtained by arbitrarily interleaving the original six queries of two modules with four independent body symbols.

[QUARTIC-BODY.md](QUARTIC-BODY.md) separately replaces formal body differentiation by finite-character rank and determinant bounds, under explicit joint-character and per-channel-tariff assumptions. Extra positive fourth-power cycles cost at least four body applications and cannot fund at most two scalar fragments.

Two equal-orientation fragments under a general changed history remain a distinct economic question: their gain can exceed one at very asymmetric ranks. A deliberate counterexample guards that boundary. The fixed-prefix theorem still prices its own full restoration cost.

## Provenance and novelty

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Selected #6030 remains conditional κ = 0.003125804. Exact predecessor #6726: `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`, especially `frozen/RESEARCH-NOTES.md`, `frozen/internal_prefix_lemma.py` and `frozen/two-fragment/caller.py`.

The predecessor treated ordinary auxiliary idle projections. The new results permit full-bank bases and arbitrary K, prove the mixed-prefix query debt, and address redesigned headers and interleavings. `SOURCES.json` binds the canonical provenance and retained live inputs; `ORIGINS.json` preserves original paths and hashes. No predecessor implementation is imported.

## Reproduce

CPython 3.12, standard library, from repository root:

```sh
python3 -B scripts/research_package.py --package research/binary-full-bank-retirement
```

Expected: the reverse-interpolation, mixed-prefix, three-query-saturation and interleaved-module and finite-character-body PASS markers, followed by `PASS_REGISTERED_RESEARCH_PACKAGE`. The exact reverse oracle checks every five-/six-input coefficient, fresh handoffs and query counts using a faithful formal S action and a checked interpolation degree bound. Word/source mutations, 17,391 finite-field rank fixtures, four-field/three-width header fixtures, exact price enclosures and explicit scope counterexamples support the written proofs. Normal and optimized executions are recorded in `VALIDATION.json`.

Universal quantifiers come from the proofs, not finite searches. Separate AI reviews are preserved; no independent human or formal-kernel acceptance is claimed.

## Scope

Ordinary controls are F-valued and S-independent. Width results use one common S; multiplying by 104 means independent per-port application, not arbitrary mixing of distinct physical S_q. General operator-valued controls, body-dependent ordinary operations, changed headers/exponents, negative body calls and noninvertible erasure outside the complete matrix model require new analysis. Atomic native query/body adjacency is explicit.

## Open next questions

Can a complete four-query changed history profitably realize two equal-orientation fragments? Can larger interleaved module systems evade the stated header obstructions? Can a legal physical control outside the F-valued model improve the fully charged interface? Each requires an exact arbitrary-input word and complete accounting before any κ claim. Structured questions are in `TASK.json`.

No native all-column, owned-erasure, compiler, precision/tape or analytic-recovery assumption is discharged. No selected cold-replay or full-history-preflight PASS is claimed. The paying root fragments in #6726 use another geometry and are not contradicted.

## Credit

Jerry Chen / **@CubeJerry**, with substantial **OpenAI Codex assistance** and separate mathematical verification. Credit Cinna Davis, Ali Romman (#6348/#6398), thu-nmrc (#6716), zxv (#6726), and the complete preserved lineage. New work is Apache-2.0; predecessor license and notice remain in `frozen/`.

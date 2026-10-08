# Certified hybrid matrix multiplication

Author: Alejandro Zarzuelo Urdiales. This personal project is separate from the Chandra, Sakana and Robert contest projects.

The actual core qualification comprises nine byte-pinned Lean sources and 35 unique selected endpoints, all with only `propext`, `Classical.choice` and `Quot.sound`. The concrete theorem `PersonalMatrix.Concrete16.certified_2208` proves the explicit 16×16 algorithm correct over every commutative unital ring in which 2 is invertible, with exactly 2,208 scheduled scalar product gates. The concrete dependency closure has eight sources; `DAGRefinement` is the separate ninth general synthesis interface.

This counts scheduled variable-product slots, excluding additions, fixed coefficient scalings, transposes and data movement. It is an upper bound on variable multiplication complexity, not a bilinear tensor-rank, optimality, floating-point accuracy or hardware-speed assertion. The 46-gate leaf allows linear forms mixing both input banks. Generic composition and matrix-valued DAG refinement use explicit normal correctness hypotheses for the original components; the concrete 48×46 instance discharges them with actual coefficient and leaf proofs.

The rank-48 outer is the known Dumas–Pernet–Sedoglavic construction, extracted from the pinned reference `spicylemonade/faster_16x16` commit `7743ee6848ed876615012c4edb3bc46a1f870afd`. The division-free paired-inner leaf is the known Rosowski construction, distinguished from the Waksman division-by-two presentation. The general transpose/DAG interface credits the stable-involution precedent. No new outer algorithm or exponent is claimed.

## Reproduction

Use Lean 4.33.1. In `lean/`, the exact nine-package lock pins Mathlib to `0df444a360eaa60ab8c11dca51a86af692955474`. Fetch the pinned dependencies and their official cache with the usual Lake/Mathlib setup; no binaries or runtime libraries are shipped here. Then run `python check_selected_axioms.py`. It hashes the nine sources, compiles them sequentially with `-j1`, and runs `SelectedAxiomAudit.lean`, requiring exactly 35 selected names and only the standard axiom allowlist. Fresh reproduction output is written under a new dated directory; historical evidence is retained.

`evidence/` contains exact actual compiler text and sanitized module-specific projections. Private raw invocation receipts and compiled artifacts remain outside the public payload, bound by SHA-256. Original generic receipt prose is preserved privately; the public module scope table supplies the accurate interpretation of each actual declaration. The checker/audit are prepared reproduction tools; their future invocation is not represented as an already completed fresh audit.

The core does not certify the 486×441 / 81×81 instance, universal all-even/all-odd leaf existence in this coefficient model, all-order fringes, or the later integer-only output-division extension. Those are separate scopes.

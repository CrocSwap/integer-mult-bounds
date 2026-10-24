# QQ16 source-handle adoption frontend (partial)

This package implements the finite-schema metadata updates of the literal PR4167 adoption transaction and PR4790 engine/external-cache replacement. A fresh tuple is required at each source tuple-construction assignment: replacing pointers in an old tuple in place can erase an actual Tape alias and incorrectly pass inventory. Stable occupied record addresses preserve object identity; a paid finite mark/sweep reuses only unreachable addresses. Numerical non-Tape leaf values can be omitted without changing ordered Tape DFS.

The [proof and complete mutation coverage table](PROOF.md) give the precise representation contract and separate initialization, update, inventory projection/DFS, collection and disposal tariffs. `F_adopt(L,N,V)` is a partial metadata charge in the finite source-schema capacity L, transaction count N and projection count V. It is **not** PR4986's complete missing F(K): source constructor/schema generation, Context/recipe/Ordinary mutators and physical marker/body actions are still unimplemented or separately charged. No matched caller-cost comparison, supplier admission or new kappa is claimed.

## Evidence

[verify.py](verify.py) extracts and executes the original `adopt_return` from the pinned nested PR4167 archive, uses the unchanged PR4790 `ReturnProtocol`, and compares each step to [frontend.py](frontend.py). It runs 16 transactions across producer/service callers and bank/private targets, four transactions with opaque `10**100000`, and one retained-old-tuple alias rejection. Both the real source inventory and the predecessor finite kernel reject the latter. Numeric value changes preserve the whole result and invoice. Cyclic owner references, shared tuple identity, cached sequence order, repeated address reclamation and marker preconditions are exercised.

This is a source-mutator calibration on an explicit role schema with a marker-only Tape oracle. It does not run the entire physical controller. The pre-input fixture compiler uses explicit known class schemas and a host identity table solely as an independent test oracle; it is not advertised as a physical constructor compiler. PR5034's K=67783, 2327-Tape, 49-validation/36-exchange two-generation case remains predecessor evidence and was not rerun. Its later Ordinary.finish `[{},{}]` cut is not covered by this implementation.

Exact inputs and historical provenance are recorded in [SOURCES.json](SOURCES.json); [RESULT.json](RESULT.json) is the deterministic bounded receipt. Scope, stopping conditions and inherited obligations are in [TASK.json](TASK.json). All new guards use explicit exceptions and remain active under optimized Python.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/qq16-source-handle-adoption --check-only
python3.12 -B scripts/research_package.py --package research/qq16-source-handle-adoption
```

Only Python 3.12 and the standard library are required. The registered commands run normal and optimized replay. No full native controller, production O73, Lean, Docker or payload census is part of this package.

## Open next questions

1. Bind one actual Context/Program replacement constructor to the finite schema, including its Count view and retirement. This would extend source mutation coverage; begin with the exact retained `restore_context`, whose previous graph-shape test is not a frontend. Its real constructor/lifetime/refinement proof is the blocker.
2. Derive the closed schema's transient capacity L from actual compiler parameters and the PR5034 return-cut K. Begin by enumerating stored omitted references and the six fresh tuple records used by adoption. Source-constructor completeness and non-adoption intermediate liveness remain blockers; a return-cut cap alone does not price those phases.

## Credit and test value

Chris R/Clear1nsight owns the retained adoption and QQ16 caller source; Tekalign's finite-role idea, Jose Manuel's original Machine, Mihir Srivastava's return obligations, ywz65 and the physical/control predecessors retain their attribution. JoyboyBrian's PR4790/4986/5034 provide the source inventory, conditional finite kernel and graph-cap lineage. New implementation, proof and checks: JoyboyBrian, with substantial OpenAI Codex assistance, Apache-2.0.

The checks protect observable ordered ownership and rejection, not source formatting. A credible regression is an in-place tuple rewrite, stale external sequence, or lost `parking.roles` update. Prior observer/cap tests start from a host-generated graph and cannot validate this new store update. The oracle calls real retained functions on an explicitly reduced schema without adding production test hooks; physical Tape actions are deliberately outside its claim.

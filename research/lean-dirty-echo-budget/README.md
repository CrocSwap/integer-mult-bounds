# Lean proof of the reserved-scratch echo bound

**Scoped formalization / independent verification; no new κ.**
Lean 4.21.0 checks the all-size resource theorem from
[PR784](https://github.com/CrocSwap/integer-mult-bounds/pull/784), including
feasibility, the matching construction family, and the exact minimum of
**2,304 uniform leaf calls for 50 factors and six reserved scratch arrays**.
The new evidence is a kernel-checked proof, with an explicit formal grammar
and a bounded connection to the predecessor's executable schedules.

Let `n` count factors, `N` count complete leaf calls, and `s` be an available
dirty-array budget. At a node of arity `k>=2`, the parent reserves `k-1`
arrays throughout every child call. Children sequentially reuse a disjoint
deeper pool. Each endpoint child runs twice, and every interior child four
times. Leaves have unit price. Under exactly this grammar, Lean proves:

```text
feasible(n,s) iff 1 <= n <= 2^s
N + 4^s >= 2^(s+1) n
min N = 2^(s+1) n - 4^s, if s>=2 and 3*2^(s-2) <= n <= 2^s
```

The main proof is [EchoBudget.lean](EchoBudget.lean). It uses only Lean core
and bundled `Std`, without Mathlib. [MODEL.md](MODEL.md) explains the formal
definition, proof, and trust boundary. The bound and construction were already
proved on paper by Alexander Schwartzman; this package does not claim a new
call-count improvement.

## Reproduce

Install the official [Lean 4.21.0 release](https://github.com/leanprover/lean4/releases/tag/v4.21.0)
or select `leanprover/lean4:v4.21.0` with an existing Elan installation. Run
from the repository root with Python 3.12+:

```sh
python3 -B -I research/lean-dirty-echo-budget/verify.py --lean /path/to/lean-4.21.0/bin/lean
```

Expected final line:

```text
PASS: 8 universal statements; 5474 constructor proofs; 5440 ordered trees; 36 equality cases; 9 negative controls; exact 50/6 minimum 2304
```

The proof alone is also reproducible, from this directory:

```sh
lean -DwarningAsError=true EchoBudget.lean
```

The complete verifier hashes every consumed predecessor file before import,
reconstructs [EXPECTED.json](EXPECTED.json), and compares all receipt fields.
It compiles in a temporary directory and works without Git, network access,
Mathlib, or writes inside this package. `--write /new/receipt.json` creates a
new receipt and refuses to overwrite. `--emit-cases /new/ModelCases.lean`
saves the generated constructor proofs for inspection, also exclusively.
The normal command runs the negative controls as well as positive checks.

## What is checked

- The eight audited universal statements cover capacity, additive and
  subtractive call bounds, exact feasibility, attainment, sharpness, the
  50/6 minimum, and exclusion of a 59-factor/five-array reserved-pool tree.
  The last item distinguishes the different connector-reuse contract in
  [PR822](https://github.com/CrocSwap/integer-mult-bounds/pull/822).
- Independent ordered-composition enumeration covers **all 5,440 ordered
  trees through eight factors**, including every allowed arity. Source
  `Plan` fields are matched to independently computed profiles and to Lean
  constructor proofs that follow the actual tree, using proven weakening
  when a child has spare capacity.
- **36 optimizer outputs** cover the full equality band for budgets 2..6.
  Their actual source-produced costs receive Lean proofs of global
  minimality within `Fits`. Extra subtrees bring the constructor-proof
  count to **5,474**. Python also checks each emitted forward/inverse word,
  every factor multiplicity, the complete leaf-call count, and the maximum
  scratch address for all 5,476 finite cases.
- Axiom audits reach every constructor proof and every finite optimality
  proof through balanced conjunctions. Only Lean's standard `propext`,
  `Classical.choice`, and `Quot.sound` are admitted. There is no `sorry`,
  custom axiom, or `native_decide` escape in the accepted proof.
- Six compiler controls alter an endpoint price, interior price, parent
  reservation, the 50-factor minimum, the equality interval, or a
  source-derived resource profile. Three audit controls inject disallowed
  axioms. All nine must fail validation.

The finite domain is fixed, not a search for a stronger frontier. Its stopping
rule and random assignment **83** are recorded in [CLAIM.json](CLAIM.json).
Execution details and package controls are in [VALIDATION.md](VALIDATION.md).

## Scope and credit

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. Subject: PR784 at
`548e42022b37a300f8bf745e848c38baccbce056`. Six consumed source/license files
are vendored verbatim, with SHA256 and Git blob pins in
[SOURCES.json](SOURCES.json). The source documentation is retained in its
original scope. The selected #799 κ remains `1661634653669567/10^18`.

The formal grammar counts completed uniform-price calls and simultaneous
reserved scratch. It does not formalize Python execution, operator products,
nonlinear restoration, rounded errors, coefficient preparation, weighted
leaf prices, preprocessing time, the physical tape/ownership interface, or
the full multiplication theorem. Those obligations and costs remain in the
predecessor's separate local interface. Connector reuse and clean-root
checkpoints admit different schedules and are outside this grammar. The
equality interval is sufficient; no maximality or uniqueness is claimed.

Credit **Alexander Schwartzman (@AlexS-scale)** for PR784's theorem and
executable source, **androolloyd** for PR673's multiway echo, and
**Koroffstrogov** for PR758's all-arity optimizer. Related contributions
include Sagar Thakrar's PR730 ordered binary/ternary optimization and Ali
Romman's PR744 strict-ternary census. Original notices preserve the earlier
PR628/621 lineage. See [NOTICE.md](NOTICE.md).

Prepared for **Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance**. One AI agent developed this proof and verification package;
no independent human review is claimed. Apache-2.0.

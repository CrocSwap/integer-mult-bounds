# Selected BIT caller: fixed roles, parked banks and finite returns

I implement fixed-role recursive control for the all-size p=1 caller in
[David Arias's PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753).
I compile its fixed source schedule to macroinstructions and execute them with
one active frame, permanent stream roles, two numerical banks and one parking
stack. I serialize the parent return label and state before child descent;
I retain no parent generator or per-child tape bank. Under the pinned caller's
input and root-coupling hypotheses, I prove an O_q(V_root)+F_q physical reserve
and retain its O_q(V(n+w)) local toll. See [PROOF.md](PROOF.md).

The executable contribution includes:

* A finite instruction emitter and dispatch loop, with canonical result commits,
  protected child handoff/return ports and complete root workspace erasure.
* A fixed scratch pool with explicit leases, stale-access rejection and guards
  against physical Tape or Arena allocation during execution.
* Complete generated-controller replays on 9216 recursive GL2(F2) addresses and
  31104 four-family GL2(F3) addresses. The latter checks 96 private COPY endpoints
  before cancelling XORs and both intermediate family sweeps.
* Actual selected adapter/child coefficients and typed CALL/RETURN checks, plus
  the earlier Frame integration, 1500 nested checkpoints and residual cursors.

I execute the reduced source programs through the generated controller, with the
source recursive Invocation constructor disabled. Production uses the unchanged
selected coefficient implementation; the reduced fixtures use their declared
small grammars. I have not materialized the astronomical selected GL64 instruction
word or expanded the retained primitive blocks into one complete microtransition
table. I support the parametric claim with the source-level refinement proof;
finite replays do not establish a formal verification of the full theorem.

I retain p=1, the stronger H2 primitive obligations and the outer borrowing
wrapper boundary. I make no exponent improvement or supplier-admission claim.
I leave the selected frontier unchanged.

## Reproduce

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/selected-bit-physical-caller
```

The registered suites authenticate the complete frozen source inventory and
its transitive repository inputs before execution. They cover the generated
recursive and four-family controllers, selected-source junction and ownership
controls, and normal/optimized Frame and continuation checks.
See [VALIDATION.md](VALIDATION.md) for scope, commands and observations.

## Attribution and overlap

Jose Manuel (`jmbarrancoml`) contributed this lowering and integration, with
substantial OpenAI Codex assistance in mathematics, code and verification. I
claim no independent human or proof-assistant review.

David Arias supplied the all-size logical caller, stock/endpoint induction,
linear-sign repair and complete logical reserve in PR2753. I reuse my numerical
codec from [PR2769](https://github.com/CrocSwap/integer-mult-bounds/pull/2769).
ywz65 supplied the finite two-tape parking controller in
[PR2635](https://github.com/CrocSwap/integer-mult-bounds/pull/2635).
[SNAPSHOTS.json](SNAPSHOTS.json) pins the 97 unchanged exported files and their
original Git paths. Those exports retain predecessor notices, including the
earlier routing, directory, residual-lifetime and selected-source work.

I coordinated this scope in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18958887).
The numerical lifetime audits in PR2781/2796/2801, the ordered-shear machine in
PR2776 and the separately claimed outer wrapper address complementary boundaries.
I do not incorporate their pending claims as proof dependencies.

I corrected the earlier continuation checker's parent-identity omission after
[starship-s's audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18960884).
I now validate each boundary against its expected parent before deterministic
signature projection, test wrong parents on both comparison paths, and reject
wrong parent/source bindings at the generated controller's call gate.

## Open next questions

* Replace the retained O(wV) route/leaf routines with the required H2 primitives.
  Price the actual source-bound coefficient and movement paths; the present
  physical lowering retains the p=1 baseline.
* Join the physical reserve with the outer stock wrapper. Coordinate with its
  active author and track all padding, restoration and preparation charges.
* Audit the compiler and primitive specialization independently. Start with
  the opcode/source correspondence, lease-end annotations and CALL invariants;
  a complete expanded transition table or proof-assistant refinement remains open.

The structured scope, overlap checkpoint and next steps appear in
[TASK.json](TASK.json). This contribution follows the repository's Apache-2.0
license and preserves the frozen sources' notices.

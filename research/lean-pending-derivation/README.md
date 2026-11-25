# PR540's pending ranges, derived in Lean

**Lean companion to [#540](https://github.com/CrocSwap/integer-mult-bounds/pull/540), stacked on its head
`acc1917034d10f464271ab115fda314fd4eee7a3`. No new κ. No PR540 file is changed.**

PR540's `PhysicalSourceConnection.pendingTag` supplies the pending coordinates of the selected
invocation (stage 2, replica 0, pair 0) by hand: `[15,22)` for idle child 1 and `[1,29)` for child 2.
Lean checked only that they contain the target masks. [#1228](https://github.com/CrocSwap/integer-mult-bounds/pull/1228)
derived them in Python. This package moves that derivation into Lean 4.21 and binds it to PR540's
actual definition.

## What is proved

From the literal PR442 schedule and route blocks (`PendingScheduleData.lean`), `PendingDerivation.lean` defines:

- **Levels:** `L₋₁ = {0}` and `L_ℓ = [0,8) ∪ E₁ ∪ … ∪ E_ℓ`, with `E_s` the exterior axes of the
  stage-s route.
- **Pending axes:** `pendingAxes idx = L_target \ L_source`, ascending.
- **Windows:** the stages strictly after the pair's last local or bridge touch.

The following are proved by `decide`, using only `propext` and `Quot.sound` (or no axioms):

| Theorem | Statement |
|---|---|
| `idle_ranks_and_nesting` | All 10 idle events: levels nest and `|pendingAxes idx| = rank` |
| `pending_child1`, `pending_child2` | `pendingAxes 1 = [15..21]`, `pendingAxes 2 = [1..28]` |
| `hosted_windows` | For all 16 tags: stage 2 is in the child's window, the host pair is not pair 0, and `offset+width ≤ |pending|` |
| `target_derived` | For all tags and axes, `targetMask t i` is the `[offset, offset+width)` slice of the derived pending axes |
| `PendingBinding.pendingTag_derived` | PR540's `pendingTag t i = derivedPendingTag t i` for all tags and axes |
| `PendingBinding.pending_eq_derived` | `PhysicalSourceConnection.pending = derivedPending` |
| `PendingBinding.selected_invocation_completion_derived` | PR540's completion theorem, stated with the derived mask |

As a result, the hand-written ranges and the extractor's hard-coded bases 15 and 1 are no longer
unchecked premises. Both are equal to schedule-derived definitions inside Lean.

Six mutations each fail because `decide` refutes the mutated statement:

- L₋₁ empty;
- L₋₁ set to the whole local block;
- exterior blocks off by one stage;
- the first two exterior blocks swapped;
- child 1 advanced before the selected call;
- child 1 claimed on the previous block.

## Remaining trust boundary

- **Literal data.** `PendingScheduleData.lean` is a Python extraction from the pinned template and
  geometry, the same boundary as PR540's other literal data. `generate_pending_schedule.py --check`
  regenerates it byte for byte.
- **Level model.** The model is a definition. Its agreement with the PR386 frames (in particular
  L₋₁ = span(q) in the `B_port ⊕ I₅₆` chart) is not proved here. The checks above pin it down only
  through ranks, nesting and the extracted target masks.
- **Axis order.** The ascending axis order within a child is the offset convention shared with
  PR540's extractor.
- **Scope.** One invocation only. No cover sweep, cost, all-size or κ claim.

## Reproduce

```sh
cd research/lean-multi-host-source && lake exe cache get Mathlib.Data.Matrix.Mul \
  Mathlib.Algebra.BigOperators.Fin Mathlib.Tactic.FieldSimp Mathlib.Tactic.Ring Mathlib.Tactic.NormNum
lake build PhysicalSourceConnection          # PR540's own build; 3.5 min measured with the Mathlib cache
cd ../.. && python3 research/lean-pending-derivation/verify.py
```

Building the three new modules takes seconds, and the controls about 15 s. `verify.py` runs the
generator check, compiles the modules against PR540's build through `lake env`, audits the axioms
of all seven theorems and runs the controls.

## Open next questions

- **Can the level model be proved from the PR386 frames?** Proving `L_ℓ` from the route identity
  ρ_(s,q): (P_q, E_s) → (I₈, E_(s−1)) and PR540's port charts would remove the last modelling
  premise. A first step is to state the route identity for port 0 over PR540's `Address` type. The
  blocker is that the geometry's rational route matrices are not yet Lean data.
- **Does this generalise to a second invocation?** `PendingDerivation` is parametric in the tag's
  child. A second selected call needs its own ownership literals from PR540's extractor.

## Credit

The Lean formalization, ownership literals and identification of this gap are cheesegrader's #540.
The construction and hosting rule are #434/#442, and the bit geometry is PR386. The Python
predecessor is #1228. Prepared by Douglas Colkitt with substantial Claude (Anthropic) assistance.
Apache-2.0.

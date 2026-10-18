# Deriving PR540's pending ranges from PR442's schedule

**Independent source-binding check for an open Lean PR. No new κ; the selected record is unchanged.**

[PR540](https://github.com/CrocSwap/integer-mult-bounds/pull/540) (cheesegrader, head
`acc1917034d10f464271ab115fda314fd4eee7a3`) formalizes one literal PR442 bit invocation (stage 2,
replica 0, pair 0, forward). Its `PhysicalSourceConnection.pendingTag` supplies the pending
coordinates by hand: child 1 owns axes `[15,22)` and child 2 owns `[1,29)`. Its README states that
"Neither Lean nor the source-extraction check binds these ranges to the source schedule." Lean's
`tag_pending_contains` only shows that the ranges *contain* the hosted target masks. The extractor
`generate_ownership_data.py` hard-codes the bases 15 and 1. The
[handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166) lists this as a next task.

## Result

`verify.py` derives both ranges from PR442's hosted bit template and PR434's geometry. It is
standard-library code that imports nothing from PR434, PR442 or PR540. **Both ranges are exactly the
derived pending sets.**

| Child (template `idx`) | Pair | Level advance | Window stages | Derived pending axes | PR540 range | Hosted width used by the stage-2 call |
|---|---:|---|---|---|---|---:|
| 1 | 1 | 1 → 2 | {2} | `[15,22)` = exterior block E₂ | `[15,22)` | 7 of 7 |
| 2 | 2 | −1 → 3 | {0,1,2,3} | `[1,29)` = q⊥ ⊕ E₁ ⊕ E₂ ⊕ E₃ | `[1,29)` | 28 of 28 |

The derivation has five steps.

1. **Binding.** The hosted template's uncompressed SHA256 equals `bit_template_sha256` in PR442's
   [`EXPECTED.json`](../idle-axis-hosting/EXPECTED.json) on main. The geometry's hash equals the
   template's `geometry_sha256`. The two vendored inputs in `inputs/` are byte-identical to PR540's
   `research/lean-multi-host-source/inputs/` files with the same names.
2. **Coordinates.** All 120 ports' stage-s routes give one common exterior block layout:
   E_s = `[8+7(s−1), 8+7s)`. The blocks partition axes 8..63. For every port, `[q/2 | A_q]` is
   checked to be an exactly orthogonal 8×8 matrix. This is the `B_port ⊕ I₅₆` chart in which axis 0
   is span(q) and axes 1..7 are q⊥.
3. **Levels.** The level model follows PR386's geometry (ρ_(s,q) sends (P_q, E_s) to (I₈, E_(s−1))):
   L₋₁ = span(q) = {0} and L_ℓ = Q⁸ ⊕ E₁ ⊕ … ⊕ E_ℓ = `[0, 8+7ℓ)` in chart axes. The rank of every
   idle event in the schedule (all 10, including the rank-0 terminal child) equals dim L_b − dim L_a.
4. **Windows.** The windows are recomputed from the schedule with the PR442 rule: local invocations
   strictly after the last local or bridge touch of the pair. Stage 2 lies in both windows, and the
   host pairs differ from the active pair 0.
5. **Routes.** Each of the 747 hosted routes `(child, off, w)` of the selected call maps to
   `pending[off:off+w]`. This equals PR540's `base+off .. base+off+w` for every route. Each
   PR540 range equals the full derived pending set, not just a superset of its targets.

Six mutations are rejected:

- child 1 placed on the previous level's block `[8,15)`;
- child 2 shifted to include the q axis;
- the two children's ranges swapped;
- L₋₁ = {} (rank mismatch);
- a route offset moved past the pending rank;
- stage 2 removed from child 1's window.

## Limits

- This is a Python derivation, not a kernel proof. It closes the stated gap as **external evidence**.
  Moving the derivation into Lean remains open.
- The idle ranks fix only the *dimensions* of the level spaces. Identifying L₋₁ with span(q), rather
  than another line, uses PR386's route identity, which this package does not re-prove. A wrong
  choice of line would break the q⊥ chart; that chart is checked.
- Within one child, PR442 requires only disjoint width-w subsets of its pending set. The ascending
  axis order that maps `off` to axes is the shared convention of PR540's extractor and this check;
  the source does not fix it.
- Only the selected invocation is checked. This says nothing about other calls, the cover sweep,
  costs or κ.

## Reproduce

```sh
python3 -I -B research/pr540-pending-range-derivation/verify.py   # ~0.5 s, prints PASS_…
python3 scripts/research_package.py --package research/pr540-pending-range-derivation
```

`verify.py --write` regenerates `RESULT.json`. Without that flag, the script requires the existing file to
match byte for byte.

## Open next questions

- **Can `pendingTag` be defined from the schedule inside Lean?** This would turn the hand-supplied
  ranges into a theorem. A first step is to encode the 10 idle events and the level map
  `L_ℓ = [0, 8+7ℓ)`, then prove `pendingTag t = L_b \ L_a` by `decide`. The blocker is that the
  level model must be stated as a definition and linked to the route identities in Lean.
- **Does the same derivation hold for a second selected call?** That would test whether the
  convention generalises before PR540 is extended. A first step is to run `derive` with another
  `SELECTED` (for example, stage 3 on pair 1, whose children have different windows). This is not
  blocked, but it is outside this session.

## Credit

The construction and hosting rule are PR434/PR442 (`research/e8-early-reset-kernel`,
`research/idle-axis-hosting`). The bit geometry is PR386. The Lean formalization and the
identification of this gap are cheesegrader's PR540. Prepared by Douglas Colkitt with substantial
Claude (Anthropic) assistance. Apache-2.0.

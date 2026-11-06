# Two terminal guards can be omitted from a compact-switch cover

The arbitrary-source compact-switch macro admits a sufficient guard product
with **3r−1 translations**, rather than the conservative **3r+1** of Nick
Petalas's [PR6231](https://github.com/CrocSwap/integer-mult-bounds/pull/6231).
The final source-control digit and the highest target window can both be
unrestricted. For one target this leaves only the temporary-control guard,
so two translations suffice. No translation of data or source transport is
needed in that one-target case.

[PROOF.md](PROOF.md) proves the endpoint for every admitted radix, window
width and target count, and proves the minimum menu size for the revised
product predicate. The bound allows arbitrary coordinate constants in each
entry. It does not lower-bound menus exploiting the full raw agreement set.
For B=2^G>=4, sufficient menu parameters are q=3r−1<=B and
q(B−2)<=2^m. Sources may read windows and exterior data, but omit all active
targets and both borrowed controls. Inactive high control digits are dirty
and restored. Complete-field modular wrap is permitted.

The terminal source carry is already understood in John-Michael Smith's
PR763 for a different fixed-bit caller. Hanson Sun's seed73 two-pass guard audit, following PR1219, also
leaves the highest window unguarded for its fixed-bit source. Both
cancellation mechanisms are predecessor facts. The new result composes
them with arbitrary target-omitting functions and specializes the optimal
translation-cover theorem to the resulting predicate. Interior source carries and nonterminal window spills remain
possible failures. The coordinate-adversary method and source-conjugation
interface are credited to PR6231.

This is a scoped algebraic proof with finite corroboration. The connection
to the documented bottleneck is an alternate logical CRT switch interface,
under the analytic-recovery track. The card's original selected-assumption
audit has explicitly changed scope. None of the five selected assumptions
is discharged, and no new κ or runtime saving is claimed. The complete cost
of translation, selection, controlled execution, shuttles and cleanup is
unknown. A physical implementation campaign needs that bill first.

## Evidence and reproduction

Python 3.10+ standard library, from the repository root:

```sh
python3 -B research/terminal-carry-guard-cover/verify.py
python3 -O -B research/terminal-carry-guard-cover/verify.py
python3 -B scripts/research_package.py --package research/terminal-carry-guard-cover
```

Direct checks used CPython 3.10.12; registered normal/optimized replay used
CPython 3.12.9, both on Linux x86_64.
The verifier recomputes and compares [RESULT.json](RESULT.json). It imports
no predecessor executable. Evidence covers:

- 65,536 complete one-target endpoints, every Boolean function of the
  three-bit window and every low control/target/window value.
- 6,144 deterministic sampled multi-field endpoints with saturated terminal
  source digits, dirty high controls and cross-window/exterior sources.
- A separate 6,144 guarded executions with a guaranteed outgoing source carry
  wrapping at the complete control boundary. Highest windows are unrestricted.
- Exact compressed product-cover checks for four geometries with r=1,1,2,3,
  including failure of the one-entry-short diagonal menu; 416 arbitrary-menu
  adversary fixtures corroborate the general written lower bound.
- Five negative controls for interior source carry, temporary saturation,
  nonterminal window spill, target-reading sources and missing source
  transport. An explicit positive control wraps both complete data and source
  fields in the same execution.

The sampled checks and product histograms are not full multi-target address
enumerations. Normal and optimized Python retain every check through explicit
exceptions. No Lean, Docker, selected cold replay or predecessor suite was run.
The stopping rule is this first verified interface refinement; no larger
construction or search is part of the result.

## Freshness and overlap

Canonical main was fetched repeatedly during this session at
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected #6030
at κ=781451/250000000. The selected baseline passed. Picker nonce
`930100c482c571e578d56c96d62de0a7` selected the adversarial-audit track; the
chosen suggestion is `uniform-transfer-audit`.

Live start-here, handoffs, active discussions and open PRs were checked before
the picker. Cached overlap snapshots at 2026-11-06 20:17–20:19 UTC covered
761 open PRs, 6,882 discussion records and all 8,917 tracked local notes.
Targeted guard-cover searches found PR6231 and its completed handoff, which
this package extends through a changed predicate. No competing matching claim
was found; bounded overlap searches do not prove novelty. Prior PR6811 is a
separate tooling task and supplies no scientific input here.

[SOURCES.json](SOURCES.json) pins predecessor text and original assignment.
[TASK.json](TASK.json) records the scope change and remaining questions.
No frozen predecessor file or selected record is modified.

## Open next questions

1. Can the two-phase one-target interface beat repair after every physical
   cost is included? First price independent t-digit translation, selection,
   conditional macro execution, dirty shuttles and cleanup. A logical cover
   alone cannot settle this; those costs are unknown.
2. Can source-dependent agreement reduce the menu further? Begin with an
   actual raw-word agreement set and an endpoint-preserving selector.
   The present lower bound concerns only the relaxed product predicate.

## Credit

Prepared for Benny Zhao / zhaobenny with substantial OpenAI Codex assistance
in the mathematics, implementation and writing. No independent human or
formal-kernel review is claimed. Apache-2.0.

Nick Petalas supplies PR6231's conservative cover and logical conjugation.
John-Michael Smith supplies PR763's carry/repair audit. Hanson Sun supplies
the seed73 two-pass guard audit and PR1219's one-pass boundary, including
the unguarded highest window. Unpaidmoon supplies
PR4321's live-digit sharp guard. Cinna Davis supplies PR4100's CRT caller;
Hiroki KUMAZAKI / PR4169 and Ryanson Jonathan / PR4329 supply the retained
arbitrary-source and target-free-window interfaces. Douglas Colkitt and the
ordinary/CRT predecessor lineage retain their credit and original notices.

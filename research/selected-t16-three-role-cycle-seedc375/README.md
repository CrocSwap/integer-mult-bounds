# Selected T16 same-call three-role cycle census

**Status: scoped negative result; no new κ.** On the selected PR1094 T16 owner map, every capacity-feasible same-invocation cycle of three whole-helper roles either leaves the idle-rank histogram unchanged or strictly raises the selected complex moment. Cross-call cycles and longer exchange sequences remain open.

## Object and move

The source is the selected map in `research/complex-t16-rare-pattern-exchanges/data/`: 144 calls, 480 helper roles per call, 32,256 pending-child/port groups, and 69,120 whole-role placements. The package pins the accepted assembly/profile, source manifest, task catalogue, both exact moment engines, unchanged bit supplier and fixed-word packing ceiling. Seed, exact base, claim, priority revision and selected-record hash are in `TASK.json` and `RESULT.json`.

At a single call, let three distinct occupied owner groups A, B and C have idle slacks `(rA,rB,rC)`. If their current roles have widths `(x,y,z)`, rotate them `A→B`, `B→C`, `C→A`. The new slacks are

```text
(rA + x - z, rB + y - x, rC + z - y).
```

The same three groups remain occupied in that call, so the per-call physical-family set is preserved. Each group is already eligible at that call, and the exact nonnegative new slacks are the aggregate-capacity test. Reassigning consecutive offsets within each group compacts its hosted intervals without changing helper widths, call times, copies, frames, local paid ranks, precision or restoration work. The only possible cost change is the exact complex moment of the resulting idle-rank profile.

## Exact result

The verifier compresses role triples by their actual `(idle slack, outgoing width)` types, separately within every selected call. Multiplicity checks ensure repeated types still represent three distinct occupied groups. It exhausts:

- 49,408 ordered supported type patterns;
- 4,417 patterns with nonnegative post-cycle slacks;
- 255 distinct ordered transfer states;
- 35 distinct old/new positive-rank histogram transitions.

At the selected complex endpoint, the pinned Mercator and base-two engines certify 19 exact histogram ties and 16 strictly more expensive transitions. **There are no strictly cheaper same-call cycles.** The smallest strict increase is for histogram `1:2, 7:1 → 1:1, 2:1, 6:1`; its exact interval endpoints are in `RESULT.json` and a source witness is included there. A synthetic arithmetic control `0,3,3` with widths `9,8,9` gives `0,2,4` and strictly lowers both engine prices, checking the sign convention independently of the selected map.

The selected complex endpoint is `67018507072324140917/40000000000000000000000`; the unchanged bit endpoint is `1733427039589844234749/10^24`, including its retained bad-residue surcharge. Both exact engines reproduce each supplier's endpoint and reject the next `10^-24` tick. The complex side still binds. No feasible cycle in this domain raises its endpoint, so the domain realizes **0%** of the fixed-word packing headroom. The selected-word relaxation remains `a < 1690054109089/10^15`, hence `κ < 1690054109089/1001690054109089` (decimal `0.0016872026453254019`).

## Open next questions

This is not a global packing optimum or an impossibility result for owner changes. It excludes cross-call cycles, paths into a free group, longer owner permutations, changed local words and alternative templates. PR #1790 identifies three-role cycles as the next question after its two-role census; this contribution closes only its same-call permutation subdomain on the selected PR1094 map. PR #1154 gives a positive three-owner cycle in the different PR1117 route, with a different local word and slack pattern; it does not census this map. The next finite step is an exact window/family join for cross-call cycles, starting with the seven rank-7 groups and requiring each target family to be free or vacated by another selected move at that call.

## Reproduce

From the repository root:

```sh
python3 -B research/selected-t16-three-role-cycle-seedc375/verify.py
python3 -B research/selected-t16-three-role-cycle-seedc375/test_verify.py
python3 scripts/research_package.py --package research/selected-t16-three-role-cycle-seedc375 --check-only
python3 scripts/research_package.py --package research/selected-t16-three-role-cycle-seedc375
```

Expected census: `49,408 / 4,417 / 255 / 35`, then `19` ties, `16` increases, and `0` decreases. The controls include a known improving algebra fixture, an over-capacity rejection, and a feasible selected-map cycle whose exact price increases. `research_package.py` checks source blobs against the pinned base before replay.

## Credit

The selected owner map and rare-pattern packing are Rohan Arun's PR #1094, retaining the PR #1087, PR #1018/#987 and Hao Yan PR #858 controller lineage. This package uses those frozen sources without changing the owner map or upstream data. The selected construction's other suppliers and assumptions remain as stated in the pinned review. Prepared by Codex with substantial OpenAI Codex assistance; new material is Apache-2.0.

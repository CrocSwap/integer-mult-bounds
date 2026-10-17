# T740 idle-axis reassignment: exact transfer census and CP-SAT screen

**Scoped negative result; no new κ or admitted supplier.** PR #3184 claims a conditional κ of `0.001730189061233850760095…` from redistributing idle rank-48 axes. PR #3187 gives an exact physical-operator counterexample to its first committed star move. This package extends that check to every eligible one-axis transfer and paired transfer on the four rank-48 children, independently replays PR3184's actual replica-0/port-0 star, and tests a relaxed CP-SAT assignment optimum.

## Result

Using the authenticated PR3148 T740 fill (`SHA256 8f4d6965…e00`), we checked all 112 port recipes for owner replica zero. A single-axis candidate moves one residual axis from one of children 8, 10, 12 or 13 to another, and must be orthogonal to every original destination axis, including hosted axes. A paired candidate moves the same axis on both streams of child pair `(8,10)` to both streams of `(12,13)`, or in reverse, under the same destination rule.

The exact eight-stream replay found:

- **21,504** eligible single-axis transfers; all 21,504 change the physical operator at the moved axis character (**192 per port**).
- **2,688** eligible forward paired transfers and **2,688** reverse paired transfers; all 5,376 change the operator (**24 per port in each direction**).
- A 147-mode baseline control passes for port 0, and the zero-character identity passes for all ports. The complete fill journal and payload authenticate, and a mutated journal preimage is rejected.

For a concrete single-axis witness, port 0 moves axis 7 from child 8 to child 12. The baseline and overlay differ in three matrix entries; `(1,1)` changes from `[0,-1]` to `[1,0]`. `RESULT.json` contains the full before/after matrices and per-port counts for both witness types.

Within the paired-transfer family, eligible axes are pairwise orthogonal: each source residual basis is orthonormal, and forward candidates are orthogonal to the full reverse destination basis. At the character equal to any one selected axis, every other moved phase is inactive, so any simultaneous nonempty set of those paired transfers retains a one-transfer counterexample.

The same isolation argument covers every **same-centre star** among children 8, 10, 12 and 13 in the audited owner-replica-0 recipes. PR3184 chooses distinct moved axes from one orthonormal donor basis; each leaf must already be orthogonal to its incoming axes. At the character equal to any moved axis, all the other moved phases are inactive, so the star's operator equals that single-axis overlay. Since the exact census rejects every eligible single-axis overlay, no nonempty star in this class preserves the operator.

We also replayed PR3184's pinned `replica=0, port=0` star from commit `6faefe1`: child 10 sends axes `[16,32,64]` to child 12 and `[128,256,4096]` to child 13, giving ranks `[48,42,51,51]` on children `(8,10,12,13)`. At character 16, the full star replay equals its isolated `10→12` single move and differs from baseline in three matrix entries. `RESULT.json` stores the full matrices. This independently reproduces the physical mismatch and explains why changing the other five axes in that star cannot repair it.

## OR-Tools assignment search

To test whether cycles could evade those one- and two-axis screens, `ortools_screen.py` models each port's 192 residual-axis tokens as an assignment to children 8, 10, 12 and 13. It preserves the token multiset, fixed hosted axes and pairwise GF(2) orthogonality, and caps each resulting child rank at 51. CP-SAT minimizes the local moment surrogate `Σ r^(1-a)` at `a = 0.00167546`, then minimizes the number of moved tokens. The exact eight-stream replay screens each port's minimum-move optimum at the 73 unit characters, the moved axes, their pairwise XORs and 72 adjacent-pair characters; it stops at the first mismatch.

All 112 port models were optimal. Each found the same best rank profile `[51,51,51,39]` from `[48,48,48,48]`, with 12 moved tokens. For those four rank terms, the surrogate falls by `0.0019571899` (about `1.026×10⁻⁵` relative). Every nominated assignment changes the exact operator at its first tested mismatch, on character `1`, `2` or `32`. The strongest structural profile is therefore not an admissible κ improvement. This search tests one minimum-move representative per port; it does not rule out another assignment with the same profile that preserves the operator. No full provider moment, κ or supplier admission is claimed.

To reproduce the optional artifact, use Python 3.10.12 with OR-Tools 9.11.4210 and run `python3.10 -B research/idle-star-paired-axis-census/ortools_screen.py > research/idle-star-paired-axis-census/ORTOOLS-RESULT.json`. The registered exact-replay package does not depend on OR-Tools. `ORTOOLS-RESULT.json` records the solver candidates and their first exact replay counterexamples.

The exact census and star-isolation argument cover owner replica zero and the same-centre star class only; multi-donor cycles can combine nonorthogonal moved axes, and other child/time pairs and nonzero replicas remain open. The CP-SAT result supplies the best rank-profile candidate for its stated four-child assignment relaxation, but only one minimum-move assignment at that profile is replayed per port. Neither experiment claims a general obstruction. The selected record and frontier are unchanged.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/idle-star-paired-axis-census --check-only
python3.12 scripts/research_package.py --package research/idle-star-paired-axis-census
```

The verifier independently implements the exact eight-stream Gaussian-integer replay. Live main inputs are pinned in `SOURCES.json`; the retained fill, journal and provider table are checked against the SHA256 and Git-blob IDs recorded from PR3148. PR3184's complete star-move artifact is retained and pinned to its exact head for the added witness. The original PR3133 notice and credits are retained under `vendor/`.

## Open next questions

See the structured tasks in [TASK.json](TASK.json). The remaining question within this slice is whether a multi-donor cycle with nonorthogonal moved axes can preserve the complete operator; first charge its maximum possible profile change against the full supplier bill. A different child/time pair needs its own insertion-to-insertion intertwiner and source-bound replay.

## Credit

Gonzalo Mier’s [PR #1252](https://github.com/CrocSwap/integer-mult-bounds/pull/1252) already gives a commuting three-axis exchange for selected #1094 children. Nick Petalas’s [PR #3187](https://github.com/CrocSwap/integer-mult-bounds/pull/3187) supplies the physical-stream criterion and first exact counterexample to the current PR3184 move. The T740 fill and 145-row exchange journal are from Jeremy Diviney’s [PR #3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148); the underlying fill/provider notice and credits are retained unchanged from PR3133 in `vendor/`. The challenged profile claim is Rohan Arun’s [PR #3184](https://github.com/CrocSwap/integer-mult-bounds/pull/3184). Recipe, template, plan and dispatch retain their PR2979/selected-supplier lineage. This package adds an independently written exact replay, a source-bound transfer census and an optional OR-Tools candidate search. Prepared by OpenAI Codex with substantial AI assistance; no independent human or proof-assistant review is claimed. New work is Apache-2.0.

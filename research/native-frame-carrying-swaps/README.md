# Frame-carrying weighted swaps in the native round-three word

This package constructs 534 direct weighted field swaps per orientation from consecutive three-ADD words. Of these, 43 enter with unequal frames. It preserves both specified normalized shears on all 632 independent inputs, including all 408 arbitrary helper inputs, final frames and the cleared owned cell. The recursive paid profile remains `{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}` in each orientation. **No improved κ is established.**

## Sufficient algebraic identity and construction

Let d and s be distinct fields over the rationals and a be nonzero. Chronologically execute d ← d + a s, s ← s − d/a, d ← d + a s. Substitution gives the intermediate pair (d₀ + a s₀, −d₀/a), then the final pair (a s₀, −d₀/a). Thus a direct field exchange followed by these two scalar multipliers has exactly the same linear map for every input, including arbitrary dirty helper values. No assumption of zero operands is used.

If the input frame assignments are (f, g), the exchange carries them to (g, f). Scalar multiplication commutes with the linear frame transforms, so it can be performed in each carried frame. Unlike three scalar contacts at one shared frame, the exchange itself requires no common containing frame. This assertion concerns the abstract field interface: it is not a free physical tape operation.

`construct(program)` removes inherited climb events, recognizes exactly these consecutive rational three-ADD patterns, and carries the frames through each swap. At every retained contact or native warp it inserts the required strictly nested transport; it restores every terminal frame. The verifier rejects a construction if any required transport is not nested. Hence this is a sufficient source-specific construction, not a claim that arbitrary programs can be transformed without extra cost.

The replay proceeds chronologically, enforcing frame equality at each scalar contact and native-warp boundary. A direct swap simultaneously exchanges the two sparse independent-input rows and their frame labels, with exact rational multipliers. Composition of the local identities proves normalized endpoint equality; the executable replay checks every row against both the original word and the specified forward/backward shear. Paid center and climb ranks are counted explicitly. The symbolic native operators and their physical correctness remain inherited source premises.

## Reproduction

Python 3.12, standard library only; Linux and Windows paths are resolved relative to this file.

```sh
python3.12 -I -B research/native-frame-carrying-swaps/verify.py
python3.12 -I -O -B research/native-frame-carrying-swaps/verify.py
python3.12 -B scripts/research_package.py --package research/native-frame-carrying-swaps
python3.12 -B scripts/check_research_commit.py --package research/native-frame-carrying-swaps
```

Default verification is read-only and compares fresh results with RESULT.json. `--write` explicitly regenerates that receipt. The `construct` function returns the full rewritten program for downstream experiments; no unpublished optimizer is needed. Sign mutation must fail endpoint comparison; omitting unequal frame carry must fail chronological frame validation. Normal and optimized interpreters enforce explicit exceptions, not assertions.

The constructor and its chronological replay are separately written but share retained row primitives with the baseline interpreter. This is not a second independent physical interpreter. No fresh Lean/kernel audit, full multiplier replay, hosted CI or human review is claimed. No physical tape-pass saving, scalar cost saving, higher κ or selected-frontier update follows from the unchanged recursive profile. Physical exchange, scale and subsequent transport costs still need a complete implementation and accounting.

## Scope and overlap

The three-transvection signed exchange identity is classical. The contribution is its explicit frame-carrying realization on the pinned current native word, with source-bound all-input replay and a reusable changed optimization representation. It does not replace the involutive-dual result in PR #4948 or claim a new caller. PR #4950 discusses coordinate swaps in a different BIT group-algebra model; our operation exchanges whole owner fields and carries their representation labels. No exhaustive novelty claim is made. Prior-session overlap coverage through PR #4955 was targeted; Discussion coverage remains incomplete. At release canonical main was refreshed to b91956876e5b4122fd89179f1b57557ff8378f15; relevant guidance, catalogue and selected record were unchanged from the campaign base.

## Open next questions

Can a joint frame/scalar schedule exploit the changed representation to reduce the complete paid bill? Begin with `construct(program)` output and price every transport and physical field movement. This matters because removing forced shared-frame contacts opens feasible representations but the present one has exactly the old paid profile. The blocker is a favorable complete budget, not endpoint correctness. See TASK.json for the structured obligation; bounded unsuccessful searches are not an impossibility proof.

## Attribution

Cao Yifan supplied the round-three native source beyond PR #4610. Cinna Davis supplied the retained scalar/helper and selected-result lineage, including PRs #4440 and #4470. Dugongue supplied the transported-frame and retained replay work, including PRs #4935 and #4948. The native/compiler lineage retains zxv and the mixed-target lineage retains Jacob Alan Sussman, together with all source authors listed in NOTICE. RETAINED-SOURCE.md records the exact predecessor. Existing local transvection lemmas motivated the algebraic representation; they were not newly kernel-checked or required as external dependencies. Prepared by Dugongue with substantial OpenAI Codex assistance, solo. Apache-2.0; inherited notices retained.

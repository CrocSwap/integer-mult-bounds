# Common code through moving Gaussian stages

**Changed local interface and a rejected direct controller substitution; no new κ.**

An explicit coordinate transport makes the center-free producer's physical
owner code identical at every stage. The price is a moving Gaussian stage
`E_s=P_s D_0`, 224 additional main-field coordinate permutations per FULL,
and eight extra anchor axes. Distinct-stage products retain exactly eight
Gaussian axes per stage after a specified output permutation. The inherited
controller's commutation condition nevertheless fails. This package preserves
the construction and identifies that next algebraic obligation.

The [proof](PROOF.md) first excludes a common code for **any** stage-local
monomial normalizers with the specified distinct port-line images. Its proof
uses support intersection, not exhaustive normalizer enumeration. It then
constructs global intertwiners `K'_i,s=P_s K_i,0`, proves their common-code
and arbitrary-input F/B endpoints, and derives the exact noncommuting stage
word formula. All 5,824 actual nonzero owner blocks disagree between two
stage-local codes but agree under the global transport, including signed
phases. The preserved Gaussian ranks do not admit the new jobs or price
spectator completion.

The decisive gate is `[C_0,E_s Q]=0 iff [C_0,P_s]=0`. The latter fails on
all 5,824 nonzero blocks in the source fixture. A direct reuse of PR4933's
local gauge is therefore rejected. This does not exclude another caller,
a recursively coded family, or transport that changes the boundary contract.
No complete moment is asserted; unknown costs remain unknown.

Reproduce with CPython 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/common-code-moving-stages
python3.12 -I -O -B research/common-code-moving-stages/verify.py
```

The replay authenticates all live source hashes, checks the 112 normalizers,
57,344 exact phase congruences, all 5,824 nonzero code blocks, both normalizer
inverse orders and all 1,956 distinct ordered words on six fresh stages.
A separate address-array calculation over F_65537 checks the word formula
on two deterministic vectors per word, using the actual one-axis Gaussian
coefficients. This corroborates the written all-width proof; a finite vector
check alone is not that proof. Equal-line/same-stage positive controls,
noncommuting-order and repeated-stage rank controls retain the scope boundary.
The normal and optimized registered commands are read-only. RESULT.json is
regenerated only by the explicit authoring option `--write-result`.

Canonical base is `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`, priority revision 7;
selected conditional κ remains 0.00302015. SOURCES.json pins the exact source
bytes; TASK.json retains the changed-card decision, overlap coverage and next
questions. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19142768)
was claimed before the checks. No native-word regeneration, complete
controller/compiler/BIT/outer replay, Lean proof, independent human review
or selected-frontier change is claimed.

## Open next questions

1. Can the transported F/B endpoints be consumed by a changed caller without
   assuming `[C_0,E_s Q]=0`? Start with one complete arbitrary-input pair and
   its actual thin queries; charge every added oracle call and both returns.
   Stop if the negative bank still requires an unpriced Q-conjugated code.
2. Can an anchor be recycled with a proved boundary and unchanged target rank?
   Start with one actual source target word and all its spectator labels.
   The new eight-axis anchor and its completion costs currently remain open.
3. If a caller survives, derive its complete completed moment, rounding,
   movement and compiler invoice before another construction search. The
   preserved 8k target rank alone grants no recursive saving.

Credit Dillon/PR4933 for physical signed normalizers and the coded ABI;
Dugongue/mdumitrean/PR4929 for the center-free producer and code;
Cayden Burkart/PR4940 and JoyboyBrian/PR4936 for the caller and physical-pair
question; Cao Yifan/PR4610; Cinna Davis/PR4694/4698/4470; zxv;
Jacob Alan Sussman; and the full inherited native/compiler/precision lineage.
Their archived mathematics is retained as a source premise. New work by
Cinna Davis, with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. No global novelty claim for coordinate transport is intended.

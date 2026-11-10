# Three signed frames, old profile (1,1,0,2)

**Scoped character proof. No new κ and no word.**

In the PR2085/2112 model, the seven-call count profile

```
(a,b,p,q,r,s,t) = (1,1,0,2,1,1,1)
```

admits no word. The determinant equation is `R+S+T = I+2P`, with matrix `[[2,1],[1,2]]` and coefficient vector `(1,1,2)`. Every rational solution by three nonzero symmetric rank-one matrices admits an AB or PQ character that detects two calls and four targets. The selected record stays κ = `781451/250000000`. The argument is written in [PROOF.md](PROOF.md).

## Scope and evidence

This is one named profile from the seven-call census in [discussion comment 19377345](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377345): old counts `(1,1,0,2)` with added multiplicities `(1,1,1)`. It is one of the twelve profiles listed there with 24 positive-dimensional spaces. It is not `(1,1,1,1)`, `(0,2,1,1)`, or `(2,0,1,1)`.

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers one profile left open by the `(2,0,1,1)` exclusion.

Evidence class: **proof**, for this profile and these hypotheses only. Lemma 4 is an exhaustive check of its 32 residue classes. Lemma 5 is the three primitive classes modulo 2. The scale bracket, the axis numerator, the axis rearrangement, and the Cramer determinant are polynomial identities, expanded in full by `verify.py`. The single-line box and the axis-reduction box are finite corroborations. The five fixtures are witnesses of the character, not a census of solutions. No step is a heuristic search offered as a nonexistence proof.

The rational solution tested with this residual's bilinear form is `A+B+2P`. Its unshifted PQ character detects two calls and four targets. The same character covers every other rational solution.

The inherited inequality "detected calls ≥ detected targets" is not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run. The orientation command `scripts/research_selected_baseline.py` was not run in this session.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Priority revision 8 on this main still quotes an older selected decimal; the frontier value used here is the selected record, not that sentence. Full Git history is needed to resolve the pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/three-signed-q-twice --check-only
python3 scripts/research_package.py --package research/three-signed-q-twice
```

The direct check is `python3 -I -W error -B research/three-signed-q-twice/verify.py`.

## Open next questions

Which of the other seventeen three-frame count profiles survive the same test? A useful first step is to read one tuple that discussion comment 19377345 already prints, other than `(1,1,1,1)`, `(0,2,1,1)`, `(2,0,1,1)`, and `(1,1,0,2)`, write that tuple's own determinant residual, and test one rational rank-one solution with the bilinear form of that residual. The sign-flipped tuple `(1,1,2,0)/(1,1,1)` has residual `[[2,-1],[-1,2]]` and is not settled here. The form `2 x1 y1 - x1 y2 - x2 y1 + 2 x2 y2` belongs to `[[2,1],[1,2]]` and does not transfer. No uniform reduction among the remaining profiles is supplied.

Four or more added signed rank-one frames are outside this three-summand character and are not a next question of this package.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and first-order inequality are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR #6190. The census is Nick Petalas's discussion comment 19377345. The released all-old-once handoff is comment 19377832. The `(0,2,1,1)` and `(2,0,1,1)` exclusions are unpaidmoon PRs #7013 and #7035. Those three profiles are not redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

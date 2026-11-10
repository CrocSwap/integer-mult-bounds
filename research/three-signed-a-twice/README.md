# Three signed frames, old profile (2,0,1,1)

**Scoped character proof. No new κ and no word.**

In the PR2085/2112 model, the seven-call count profile

```
(a,b,p,q,r,s,t) = (2,0,1,1,1,1,1)
```

admits no word. The determinant equation is `R+S+T = A+3B = diag(1,3)`. Every rational solution by three nonzero symmetric rank-one matrices admits an AB or PQ character that detects two calls and four targets. The selected record stays κ = `781451/250000000`. The argument is written in [PROOF.md](PROOF.md).

## Scope and evidence

This is the named sibling of the `(0,2,1,1)/(1,1,1)` exclusion: old counts `(2,0,1,1)` with added multiplicities `(1,1,1)`. The census is [discussion comment 19377345](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377345). The question was left open by [PR #7013](https://github.com/CrocSwap/integer-mult-bounds/pull/7013) and its finding, [discussion comment 19507678](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507678). It is not the settled all-old-once profile `(1,1,1,1)/(1,1,1)`, and it does not redo `(0,2,1,1)`.

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers one profile left open by the `(0,2,1,1)` character proof. That proof itself followed the all-old-once exclusion of the three-frame question in [research/bit-two-signed-frame-floor](../bit-two-signed-frame-floor). No further construction round is opened.

Evidence class: **proof**, for this profile and these hypotheses only. The scale bracket, the Cramer determinant, and the axis rearrangement are polynomial identities, expanded in full by `verify.py`. Lemma 4 is an exhaustive check of its 32 residue classes. The single-line box is a finite corroboration of Lemma 3 on coordinates and denominators at most 12. The axis-reduction box checks the collapsed scale formulas for `u1 = 0` on primitive coordinates at most 8. Neither box is the proof. The five fixtures are witnesses of the character, not a census of solutions. One of them is the rational solution `2B+P+Q`. No step is a heuristic search offered as a nonexistence proof.

The bilinear form is `3 x1 y1 + x2 y2`. The constants 3, 6, and 12 used for `3A+B` in the `(0,2,1,1)` argument do not appear here unchanged: the axis equation is `(α-2l) v1^2 (αβ-γ^2 - 6α k) = 2 α^2 k v2^2`, and the Cramer matrix carries 6 on the first coordinate of the new form and 2 on the second. A failure control solves one triple with the old form and checks that the sum is `diag(3,1)`, not `diag(1,3)`.

The inherited inequality "detected calls ≥ detected targets" is not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run. The orientation command `scripts/research_selected_baseline.py` was not run in this session.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Priority revision 8 on this main still quotes an older selected decimal; the frontier value used here is the selected record `781451/250000000`, not that sentence. Full Git history is needed to resolve the pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/three-signed-a-twice --check-only
python3.12 scripts/research_package.py --package research/three-signed-a-twice
```

The direct check is `python3 -I -W error -B research/three-signed-a-twice/verify.py`.

## Open next questions

Which of the other eighteen three-frame count profiles survive the same AB/PQ test? A useful first step is to read one tuple that [discussion comment 19377345](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377345) already prints, other than `(1,1,1,1)`, `(0,2,1,1)`, and `(2,0,1,1)`, write that tuple's own determinant residual, and test one rational rank-one solution with the bilinear form of that residual. This package does not name another tuple. The forms `3 x1 y1 + x2 y2` and `x1 y1 + 3 x2 y2` are special to `diag(1,3)` and `diag(3,1)`.

Four or more added signed rank-one frames are outside this three-summand character and are not a next question of this package.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and first-order inequality are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR #6190. The census and the released all-old-once handoff are Nick Petalas's discussion comments 19377345 and 19377832. The `(0,2,1,1)` exclusion and the question answered here are unpaidmoon PR #7013. The all-old-once profile was character-excluded separately and is not redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

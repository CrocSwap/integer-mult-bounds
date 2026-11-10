# Three signed frames, old profile (0,2,1,1)

**Scoped character proof. No new κ and no word.**

In the PR2085/2112 model, the seven-call count profile

```
(a,b,p,q,r,s,t) = (0,2,1,1,1,1,1)
```

admits no word. The determinant equation is `R+S+T = 3A+B = diag(3,1)`. Every rational solution by three nonzero symmetric rank-one matrices admits an AB or PQ character that detects two calls and four targets. The selected record stays κ = `781451/250000000`. The argument is written in [PROOF.md](PROOF.md).

## Scope and evidence

This is one named profile from the seven-call census in [discussion comment 19377345](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377345): old counts `(0,2,1,1)` with added multiplicities `(1,1,1)`. It is one of the twelve profiles listed there with 24 positive-dimensional spaces. It is not the settled all-old-once profile `(1,1,1,1)/(1,1,1)`.

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers one profile left open by the all-old-once character proof, which itself answered the three-frame question in [research/bit-two-signed-frame-floor](../bit-two-signed-frame-floor).

Evidence class: **proof**, for this profile and these hypotheses only. Lemma 4 is an exhaustive check of its 32 residue classes. The scale bracket and the Cramer determinant are polynomial identities, expanded in full by `verify.py`. The single-line box in the verifier is a finite corroboration of Lemma 3 on coordinates and denominators at most 12; the written coprimality argument covers every primitive vector. The five fixtures are witnesses of the character, not a census of solutions. No step is a heuristic search offered as a nonexistence proof.

The inherited inequality "detected calls ≥ detected targets" is not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run. The orientation command `scripts/research_selected_baseline.py` was not run in this session.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Priority revision 8 on this main still quotes an older selected decimal; the frontier value used here is the selected record, not that sentence. Full Git history is needed to resolve the pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/three-signed-b-twice --check-only
python3.12 scripts/research_package.py --package research/three-signed-b-twice
```

The direct check is `python3 -I -W error -B research/three-signed-b-twice/verify.py`.

## Open next questions

Which of the other nineteen three-frame count profiles survive the same test? A useful first step is the named sibling `(2,0,1,1)/(1,1,1)`, whose residual is `diag(1,3)` rather than `diag(3,1)`. The bilinear form and the constants 3, 6, and 12 in this proof are special to `3A+B`.

Can four or more added signed rank-one frames lower the eight-call minimum? This three-summand character does not apply. A useful first step is four primitive directions and the shortest determinant equation that uses each new label once.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and first-order inequality are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR #6190. The census and the released all-old-once handoff are Nick Petalas's discussion comments 19377345 and 19377832. The all-old-once profile was character-excluded separately and is not redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

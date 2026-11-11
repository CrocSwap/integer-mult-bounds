# Six-call orbit O5 is character-excluded

**Scoped character proof. No new κ and no word.**

In the PR2085/2112 model, the four six-call profiles of orbit O5 are character-excluded. Under the cited determinant and character premises they admit no word. The representative is `(0,1,1,1)/(1,1,1)`, with residual `diag(3,2)`. The proof is written for the coordinate swap `(1,0,1,1)`, residual `diag(2,3)`, and the quadratic form `3 x1^2 + 2 x2^2`. Section 8 of [PROOF.md](PROOF.md) carries the exclusion to the named profile and to `(1,1,0,1)` and `(1,1,1,0)`. The selected record stays κ = `363005817/100000000000`.

## Scope and evidence

This is open question 1 of [PR #7128](https://github.com/CrocSwap/integer-mult-bounds/pull/7128). That note shows that all 1870 box triples of the representative are character-excluded, and asks for a proof. The first step it names is the parity-image argument of [PR #7035](https://github.com/CrocSwap/integer-mult-bounds/pull/7035) with `3 x1^2 + 2 x2^2` in place of `3 x1^2 + x2^2`. The blocker it names is real: `diag(3,2)` has determinant 6, and the strict 2-adic gap does not survive.

Evidence class: **proof**, for these four profiles and the cited determinant and character premises only. The bracket, the doubled-matrix identities, the Cramer determinant, and the axis rearrangement are exact polynomial expansions in `verify.py`. Lemma 5 is an exhaustive check of its 32 residue classes. The direction-type enumeration checks that the written case list covers every triple. Two explicit decompositions show that a pair can have parity image containing `(1,1)`; each still has another pair whose character detects two calls and four targets. The single-line box and the axis-scale box are finite corroborations, not the proof.

The literal conclusion of #7035, that no pair carries `(1,1)`, is false for this residual. The odd-`k` axis equation has both sides of valuation 2, and the witness with directions `(0,1)`, `(-5,3)`, `(-3,5)` realizes that subcase. Exclusion uses the remaining diagonal-diagonal pair.

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers one orbit left open by #7128. No further construction round is opened.

The forms `3 x1 y1 + x2 y2` and `2 x1 y1 + 3 x2 y2` are failure controls. The first solves `diag(1,3)`. The second solves the named residual `diag(3,2)` directly and is not the form used in Sections 4 through 7; the named residual is reached by the coordinate swap `t`.

The inherited premises (P1) and (P2) are not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Priority revision 8 on this main still quotes an older selected decimal; the frontier value used here is the selected record `363005817/100000000000`. Full Git history is needed to resolve the pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/o5-six-call-character-exclusion --check-only
python3.12 scripts/research_package.py --package research/o5-six-call-character-exclusion
```

The direct check is `python3 -I -W error -B research/o5-six-call-character-exclusion/verify.py`.

## Open next questions

1. Does every decomposition of `(2,1,1,0)/(1,1,1)` fail a character or fail target support? PR #7128 gives a decomposition that passes every character. The character test of this package cannot close that orbit.
2. The same question for `(0,1,1,1)/(1,1,2)`. Its witness in #7128 passes every character and fails target support.

Four or more added frames are a different equation and are not a next question of this package.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and first-order inequality are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR #6190. The census is Nick Petalas's discussion comment 19377345. Orbit O5, the question answered here, and the maps `s`, `t`, and `h` are his PR #7128. The parity-image method is unpaidmoon's PR #7035, following #7013 and the all-old-once exclusion. The redone axis split, the safe-pair argument, and the checker are new.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

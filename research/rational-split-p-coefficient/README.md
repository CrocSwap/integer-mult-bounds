# Rational splittings of 2I fail the length-6 character count

**Scoped impossibility proof. No new κ and no word.**

Fix old call `B` and frozen frames `A`, `P`, and `Q`. For every rational rank-one splitting `X + (2I-X) = 2I`, the six labels `A, B, P, Q, X, 2I-X` meet target support, and both the `P`-coefficient and the `AB`-coefficient extend. Each detects two calls and four targets, so the six labels are not a word. The argument is [PROOF.md](PROOF.md).

The displayed point asked for by PR #7067 is `t=2`: frames `(-2/5, 4/5, 8/5)` and `(12/5, 6/5, -8/5)`. There the multiplier is `5`. Every integer lift of either character, not only `5c` and `5(a+b)`, gives the same count. Each family has `125` residue classes and `25` integral ones, an exhaustive parity census. Inside the lattice `Z^3 + ZX`, no rank-one matrix has character `(1,1)`, and any word that stays in the lattice and uses all six labels has at least ten calls. A single extra label cannot restore the determinant sum, so length 7 is impossible even outside the lattice.

Selected κ stays `363005817/100000000000`. This package does not change the selected frontier and does not lower or raise the eight-call minimum. The ordinary eight-call word does not contain the splitting frames.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers the rational-splitting question left open by unpaidmoon PR #7067. The predecessor classified length-6 support and showed that the integral pairs `{2A,2B}` and `{2P,2Q}` fail the `P`-coefficient test. The open count was the same test on the displayed `t=2` frames.

Evidence classes, kept apart:

1. **Proof.** For every primitive direction, the odd multiplier `m = |u|^2 / gcd(|u|^2, 4)` makes `m c` and `m(a+b)` integer characters on the splitting lattice. Both detect two calls and four targets. Every other lift is even on the splitting. No rank-one matrix in the lattice has character `(1,1)`, so a lattice word that uses all six labels has at least ten calls.
2. **Exhaustive finite census of one denominator.** At `t=2`, all `125` residue classes of each character family are integral only when the value on both frames is even. Period steps of `5` change those values by even integers, so the residues cover every integer lift.
3. **Finite control, not a census of directions.** The closed forms are evaluated on all `1440` primitive vectors with coordinates in `[-24, 24]`.

The support census of #7067, the five-call theorem of #7024, the six-frame classification of #7076, the length-5 four-frame theorem of #7083, and the two-old equation of #7100 are not redone. Passing a character count is not how a word is established here: the count fails.

The determinant identity, the torsion-free reading of the address group, and the character inequality are inherited from `research/bit-two-signed-frame-floor/PROOF.md`, Section 1. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Full Git history is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/rational-split-p-coefficient --check-only
python3.12 scripts/research_package.py --package research/rational-split-p-coefficient
```

The direct check is `python3 -I -W error -B research/rational-split-p-coefficient/verify.py`.

## Open next questions

Is there a rank-one matrix `Y` outside the `t=2` lattice for which every `AB` lift and every `P`-coefficient lift integral on the displayed frames detects `Y`? A cancelling pair `Y, -Y` would then meet both inequalities at length 8. Length 6 and length 7 cannot contain all six labels. The half projector `P/2` is a negative example: the lift `a+3b` misses it and still detects two calls against four targets. The smallest next matrix is `(0,0,1/3)`. No such search is included here. A matrix that survives the lifts would still not be a word: support and the product remain.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant identity and the character inequality are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR6190. The `AB` and `PQ` shapes are the three-frame argument of `research/three-signed-old-once`. The integral `P`-coefficient count is the language of `research/four-signed-once-parity`. The length-6 support shape, the displayed `t=2` frames, and the open question are unpaidmoon PR #7067, head `e6aac77f79560add2c47c761d9defff96934d88d`. None of those theorems is redone.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

## Workflow feedback (optional)

https://github.com/CrocSwap/integer-mult-bounds/discussions/1200

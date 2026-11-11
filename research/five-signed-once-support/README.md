# Five once-each signed frames and the five-call equation

**Exhaustive finite support census, plus one parity-image witness. No new κ and no word.**

The shortest determinant equation that uses five new labels once each is `R+S+T+U+V = 4I`: five paid calls and no old call. In the PR2085/2112 model that equation admits no word. Lemma 1 of [PROOF.md](PROOF.md) limits a target-carrying subset to size 2 or 3, and every one of the 116280 ordered 4-tuples of such subsets fails the rank-one cone. The argument and the census counts are in [PROOF.md](PROOF.md).

The same sum has one explicit rational solution on five pairwise nonparallel primitive directions whose parity image is all of `F2^2`. The three-frame test, which needs that image to miss `(1,1)`, does not apply to every five-frame solution. The witness is still excluded by the support census and by a direct character count on that one solution. It is one solution, not a census, and it is not a word.

The selected record stays κ = `781451/250000000`. Six or more added frames, and five added frames together with an old call, stay open. This census does not lower the eight-call minimum.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and takes the five-frame question left open by the four-call note, discussion comment 19507121, which itself follows the three-frame note. It does not redo the four-call theorem, the three-frame character, or a four-frame equation with an old call.

Evidence classes, kept apart:

1. **Exhaustive finite census, and therefore a scoped proof of support failure.** The domain is the 116280 ordered 4-tuples of distinct weight-2 and weight-3 subsets. Of them, 71040 have invertible incidence matrices and a unique rational solution off the determinant cone, 44520 are inconsistent, and 720 are consistent of rank 4 with one frame frozen at `±2I`, `±(A-B)`, or `±(P-Q)`. No tuple meets the rank-one hypothesis. The determinant identities `det H = 1/2` and `det(4I-H) = 17/2` are checked exactly, and one invertible determinant is reduced by hand to `-2`. This is not a heuristic search and not a sample of directions.
2. **Explicit witness, not a census.** Directions `(-1,1)`, `(0,1)`, `(1,0)`, `(1,1)`, `(1,3)` at scales `1`, `-1`, `3`, `-1/2`, `1/2` sum to `4I`, and three declared integer combinations realize parity images `(1,0)`, `(0,1)`, and `(1,1)`. No AB or PQ form kills all five frames.
3. **Direct count on that one witness.** The `P`-coefficient modulo 2 detects two calls and four targets. The inherited inequality is not reproved. The witness's nonempty subset sums miss every target; that list checks the witness and is not the census.

The determinant identity and the subset-sum necessity are inherited from `research/bit-two-signed-frame-floor` and are not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Full Git history is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/five-signed-once-support --check-only
python3.12 scripts/research_package.py --package research/five-signed-once-support
```

The direct check is `python3 -I -W error -B research/five-signed-once-support/verify.py`.

## Open next questions

Can six added signed rank-one frames, each used once and with no old call, meet target support for `F1+...+F6 = 4I`? A six-call word would still lower the eight-call minimum, and this census uses exactly five columns. A useful first step is to rewrite the size lemma: the complement of a four-element subset is now a pair, so sizes 2, 3, and 4 all remain possible, and then to test one six-direction solution. No such census is supplied here.

Can five added frames plus one old call meet support at length 6? Lemma 1 uses the residual `4I`. A useful first step is one old projector `E` and the equation `R+S+T+U+V = 4I-E`, then the subset-size test on that residual. No such solution is supplied here.

A full parity image does not by itself survive every character: the witness above is still excluded by a character that detects only two of the five frames.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and the subset-sum necessity are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR6190. That floor stopped at two added frames. The three-frame all-old-once character is the package `research/three-signed-old-once`. The four-call support proof and the open five-frame question are the package `research/four-signed-once-parity`, merged as PR6952, discussion comment 19507121. Neither is redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

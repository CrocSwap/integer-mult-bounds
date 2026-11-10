# Five rank-one frames plus one old call, at length 6

**Support classification, plus an integral character obstruction. No new κ and no word.**

Fix one old projector `E` in `{A,B,P,Q}`. Five nonzero symmetric rational rank-one matrices sum to `4I-E` and meet all four targets as subset sums if and only if three of them are the other three old projectors and the other two split `2I`. The argument is [PROOF.md](PROOF.md).

The integral splittings are exactly `{2A,2B}` and `{2P,2Q}`. Each integral solution then detects two calls and four targets under the `P`-coefficient modulo 2, so it is not a word. One pairwise nonparallel splitting, at chart parameter `t=2`, is a support witness only. The selected record stays κ = `781451/250000000`. This classification does not lower the eight-call minimum.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers the length-6 question left open by the five-call census, discussion comment 19514165 on PR #7024. The equation is `R+S+T+U+V=4I-E`. It does not redo the five-call residual `4I`, the four-call theorem, a four-frame equation with an old call, or six added frames with no old call.

Evidence classes, kept apart:

1. **Proof of the construction and of the splitting identity.** For each projector `E`, the three complementary projectors plus any rank-one splitting of `2I` meet support. The identity `Q(2I-X)-Q(X)=4(2-tr X)` classifies those splittings. The integral points are the two pairs above, read off the discriminant `4-c^2`.
2. **Exhaustive finite census, and therefore the converse.** Lemma 1 leaves subset sizes 2, 3, and 4: 230300 unordered 4-tuples. Of them, 22370 duplicate an `E`-bit row and contradict the twelve target differences; 2450 have rank 3 and an inconsistent left kernel; 3840 have a full-support kernel and fail the trace test `2,3,4 ≠ 7`; 27840 freeze one frame and do not meet the cone; 53400 freeze three frames, of which only 240 are consistent and on the cone, and those 240 are the construction. The other 120400 tuples are invertible and off the cone. One invertible determinant is the known value `-2`.
3. **Explicit witnesses, not a word.** `A,P,Q,2A,2B` with old call `B`, and the `t=2` frames `(-2/5,4/5,8/5)` and `(12/5,6/5,-8/5)` on directions `(1,2)` and `(2,-1)`. The integral witness fails the inherited character count. The non-integral witness is support only.

The determinant identity, the subset-sum necessity, and the character inequality are inherited from `research/bit-two-signed-frame-floor` and are not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Full Git history is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/five-signed-one-old --check-only
python3.12 scripts/research_package.py --package research/five-signed-one-old
```

The direct check is `python3 -I -W error -B research/five-signed-one-old/verify.py`. It takes about 90 seconds.

## Open next questions

Can one rational splitting of `2I` make this length-6 support solution into a word? A word would lower the eight-call minimum. The integral pairs already fail the `P`-coefficient test. A useful first step is the same count on the displayed `t=2` frames. Passing it would still not be a word: support is necessary, not sufficient.

Six added frames with no old call, and four added frames plus an old call, are different equations and are not answered here.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant, the subset-sum necessity, and the character inequality are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR6190. The three-frame all-old-once character is `research/three-signed-old-once`. The four-call support proof is `research/four-signed-once-parity`, merged as PR #6952. The five-call census and this open question are PR #7024, discussion comment 19514165. None of those theorems is redone. Discussion #2091 studies one fixed fifth address and is not this residual equation.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

# Four rank-one frames plus one old call

**Support proof for one length-5 profile. No new κ and no word.**

Four nonzero symmetric rational rank-one matrices and one old projector `E ∈ {A,B,P,Q}` do not meet target support for

```
R + S + T + U = 4I - E.
```

In the PR2085/2112 model that is the length-5 profile with four added frames, each used once, and exactly one old call. The profile admits no word. The argument is written in [PROOF.md](PROOF.md).

The selected record stays κ = `781451/250000000`. Lengths 6 and 7, with two or three old calls, stay open. Five or more added frames stay the separate question in [research/four-signed-once-parity](../four-signed-once-parity).

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and takes the one-old-call question left open by the four-call note, discussion comment 19507121. It does not redo that four-call proof, the three-frame character, or another three-frame census profile.

Evidence classes, kept apart:

1. **Proof.** Lemmas 1–7 exclude target support for every rational solution of `R+S+T+U = 4I-E` by four nonzero symmetric rank-one matrices and one old projector. Subset size, parity, the tree list, and the two 4-cycle framesets are the whole case split. The determinant identities `det H = 1/2` and `det(4I-H) = 17/2` are checked exactly.
2. **Exhaustive finite census of the same carrying assignments.** For each of the four projectors, all `80640` choices of four distinct pairs, target bijections, and direct-or-complement bits are solved by exact integer elimination. Each projector has 576 consistent systems, all of them 4-cycles through `E`, and none of those solutions is rank one. This is not a search over directions or scales.
3. **Two declared solutions of the sum, not a census.** For `E=A`, directions `(1,0),(0,1),(1,1),(1,2)` at scales `4,2,-2,1` sum to `4I-A`, and no nonempty subset of the five labels is a target. For `E=P`, directions `(1,0),(0,1),(1,1),(1,-1)` at scales `1,1,1,3/2` sum to `4I-P`. Exactly two targets, `A+P` and `B+P`, occur as pairs, and the other two targets do not occur at all. A pair test on one solution is not the theorem.

The determinant identity and the subset-sum necessity are inherited from `research/bit-two-signed-frame-floor` and are not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Full Git history is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/four-signed-one-old --check-only
python3.12 scripts/research_package.py --package research/four-signed-one-old
```

The direct check is `python3 -I -W error -B research/four-signed-one-old/verify.py`.

## Open next questions

Can four added signed rank-one frames plus two old calls meet support at length 6? A word at length 6 would still be shorter than the eight-call minimum. The first step is two old projectors `E,F`, the equation `R+S+T+U = 4I-E-F`, and one rational rank-one solution's subset scan. The five-label case split does not apply: a sixth label changes the allowed subset sizes.

Can the same four frames plus three old calls meet support at length 7? That is the shortest remaining profile in the question left by the four-call note. The first step is three old projectors and `R+S+T+U = 4I-E-F-G`. Seven labels are a different graph, so neither the length-5 cycle list nor a failed length-6 search would settle it.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and the subset-sum necessity are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR6190. The four-call once-each support proof is `research/four-signed-once-parity`, PR #6952, discussion comment 19507121, and is not redone here. The three-frame all-old-once character and the `(0,2,1,1)` profile are neighboring results and are not reused as lemmas.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

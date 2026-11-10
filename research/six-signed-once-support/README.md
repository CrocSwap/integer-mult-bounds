# Six once-each signed frames

**Support is attained. No word, and no new κ.**

The shortest determinant equation in six new labels, each used once and with no old call, is `F1+...+F6 = 4I`. Target support is possible: the addresses `A,P,B,Q,2A,2B` are nonzero and rank one, sum to `4I`, and realize the four targets as pair sums. The same holds for every rational rank-one splitting of the remaining `2I` after `{A,B,P,Q}`.

None of those solutions is a word. The character `a+b mod 2` detects two calls and all four targets. The argument that this is the entire support locus is an exhaustive census of the 230,300 subset systems, written in [PROOF.md](PROOF.md). The selected record stays κ = `781451/250000000`.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers the six-frame question left open by the five-frame note, discussion comment 19514165. It is a scoped local result on that handoff. It does not open another construction round, and it does not redo the four-frame or five-frame support proofs.

Evidence classes, kept apart:

1. **Exhaustive finite census, hence a proof of the support classification.** Lemma 1 limits subset size to 2, 3, or 4, so there are 50 subsets and 230,300 unordered 4-tuples. Column relabeling gives 658 orbits. Outside two orbits, all 15,776 other assignment systems are linearly inconsistent or have a degree-1 Nullstellensatz certificate of 1, re-expanded by the verifier. The four-cycle orbit is exactly `{A,B,P,Q}` plus a trace-2 rank-one splitting of `2I`. The four-triple orbit has no real point.
2. **Hand character obstruction on that locus.** Every rational member of the family is killed by `χ_AB`, extended by zero on the padding. The inequality is inherited and not reproved. The hypotheses are six once-each rank-one frames, no old call, and residual `4I`.
3. **Explicit support witness, not a word.** `A,P,B,Q,2A,2B` meets support and has character counts 2 and 2. A witness is only a witness of support.

The five-frame domain of 116,280 tuples does not carry over. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Full Git history is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/six-signed-once-support --check-only
python3.12 scripts/research_package.py --package research/six-signed-once-support
```

The direct check is `python3 -I -W error -B research/six-signed-once-support/verify.py`. It reruns the orbit census and the certificate expansions. On this machine that takes about 35 seconds.

## Open next questions

Can five added signed rank-one frames plus one old call meet support at length 6? The six-frame census uses the residual `4I`. One old call replaces that residual, so neither the size cut nor the character count applies. A useful first step is one old projector `E` and the equation on five new frames summing to `4I-E`.

Can seven or more added frames, or six frames plus an old call, lower the eight-call minimum? Both change the number of free addresses or the residual. No such equation is solved here.

A support solution is not a word. On the locus above, the character obstruction is complete for six once-each frames with no old call.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and the subset-sum necessity are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR6190. The four-frame support proof is merged PR #6952, discussion comment 19507121. The five-frame support proof, whose open question this answers, is open PR #7024, discussion comment 19514165. The three-frame all-old-once character is `research/three-signed-old-once` and is not redone.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

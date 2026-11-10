# Four once-each signed frames and the four-call equation

**Support proof, plus one parity-image witness. No new κ and no word.**

The shortest determinant equation that uses four new labels once each is `R+S+T+U = 4I`: four paid calls and no old call. In the PR2085/2112 model that equation admits no word. Every target would have to be a sum of two of the four rank-one frames, and all 15 ways of choosing four pairs contradict the rank-one hypothesis. The argument is written in [PROOF.md](PROOF.md).

The same equation has one explicit rational solution whose parity image is all of `F2^2`. The three-frame test, which needs that image to miss `(1,1)`, does not apply to every four-frame solution. The witness is still excluded by a direct character count (two calls against four targets) and by the support proof. It is one solution, not a census, and it is not a word.

The selected record stays κ = `781451/250000000`. Lengths 5, 6, and 7, and five or more added frames, stay open.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and takes the four-frame question left open by the all-old-once three-frame note, discussion comment 19493126, which itself follows comment 19377832. It does not redo that three-frame proof and it does not take another three-frame census profile.

Evidence classes, kept apart:

1. **Proof.** Lemma 1 and Theorem 2 exclude target support for every rational solution of `R+S+T+U = 4I` by four nonzero symmetric rank-one matrices. The 15 pair graphs are the entire case split. The determinant identities `det H = 1/2`, `det(4I-H) = 17/2`, and `det(-H/2) = 1/8` are checked exactly.
2. **Explicit witness, not a census.** Directions `(0,1)`, `(1,-1)`, `(1,1)`, `(1,2)` at scales `-3`, `5/2`, `1/2`, `1` sum to `4I`, and `R`, `S`, and `S+U` realize parity images `(1,0)`, `(0,1)`, and `(1,1)`. No AB or PQ form kills all four frames.
3. **Direct count on that one witness.** The `P`-coefficient modulo 2 detects two calls and four targets. The inherited inequality is not reproved. The witness's fifteen nonempty subset sums miss every target; that list checks the witness and is not Theorem 2.

The determinant identity and the subset-sum necessity are inherited from `research/bit-two-signed-frame-floor` and are not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Full Git history is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/four-signed-once-parity --check-only
python3.12 scripts/research_package.py --package research/four-signed-once-parity
```

The direct check is `python3 -I -W error -B research/four-signed-once-parity/verify.py`.

## Open next questions

Can four added signed rank-one frames plus one, two, or three old calls meet support at length 5, 6, or 7? Theorem 2 uses exactly four calls. A useful first step is one old projector `E` and the equation `R+S+T+U = 4I-E`, then the same pair test on one rational solution. No such solution is supplied here.

Can five or more added signed rank-one frames lower the eight-call minimum? The four-call support proof and the three-frame character both stop at the number of frames they assume. A useful first step is five primitive directions and the shortest determinant equation that uses each new label once.

A full parity image does not by itself survive every character: the witness above is still excluded by a character that detects only two of the four frames.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and the subset-sum necessity are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR6190. That floor stopped at two added frames. The three-frame all-old-once character is the fork package `research/three-signed-old-once`, discussion comment 19493126, and is not redone here. The concrete handoff is discussion comment 19377832.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

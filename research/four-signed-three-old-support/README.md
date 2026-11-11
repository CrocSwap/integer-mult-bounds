# Three old calls meet length-7 support

**Explicit support witness. No new κ and no word.**

Four nonzero symmetric rational rank-one matrices and three distinct old
projectors can meet target support for

```
R + S + T + U = 4I - E - F - G.
```

The seven labels `A`, `B`, `P`, `Q`, `(1/2)A`, `(3/2)A`, and `2B` sum to `4I`.
Each target is exactly one of the pairs `A+P`, `A+Q`, `B+P`, and `B+Q`.
Designating any three of the four projectors as the old calls leaves the
omitted projector and the three scaled frames as added frames. Added frames
may equal a standard projector; that is the permission already stated for the
length-5 equation. The argument is written in [PROOF.md](PROOF.md).

The same seven labels fail the inherited odd-`c` count: `P` and `Q` are the
only labels with odd `c`, while all four targets have odd `c`. Under that
inherited inequality the witness is excluded as a word. The inequality is not
reproved. Selected κ stays `363005817/100000000000`.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The
card asks for a larger or nonabelian native alphabet. This package stays in
the abelian symmetric 2-by-2 model and takes the three-old length-7 question
left open by the two-old support witness, PR #7100, which itself follows the
one-old support proof, PR #7083. It does not redo either result, and it does
not take the length-6 four-odd-`c` question.

Evidence classes, kept apart:

1. **Explicit witness.** The seven matrices are the standard `uu^T` frames at
   the scales in [PROOF.md](PROOF.md). They are positive semidefinite, rank
   one, and distinct. They sum to `4I` because `(1/2)A + (3/2)A = 2A` and the
   six labels `A, B, P, Q, 2A, 2B` sum to `4I`. Every old triple is checked,
   not only one orbit representative.
2. **Carrier case split for that one solution.** The `c`-coordinate of a
   subset lies in `{-1,0,1}`, and the axis subsets with coefficient `0` or `1`
   are unique. Each target is exactly the declared projector pair. The
   verifier also sums all 127 nonempty subsets. That finite scan exhausts the
   subsets of this one set. It is not a census of solutions of the equation.
3. **Odd-c count on that same solution.** Two calls, four targets. Every
   label has integer `c`, including the two half-integer axis frames. The
   inherited inequality is not reproved. Dropping `Q` removes `A+Q` and `B+Q`
   and keeps `A+P` and `B+P`. Shifting `(3/2)A` by `A` breaks the sum.
   Adjoining `(1/2)A` to the six-label set moves the sum off `4I`.

The determinant identity and the subset-sum necessity are inherited from
`research/bit-two-signed-frame-floor` and are not reproved. Predecessor
replays, Lean, Docker, and the selected-result cold replay were not run.
No search over directions or scales is claimed, successful or otherwise.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance. Full Git history
is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/four-signed-three-old-support --check-only
python3.12 scripts/research_package.py --package research/four-signed-three-old-support
```

The direct check is `python3 -I -W error -B research/four-signed-three-old-support/verify.py`.

## Open next questions

Does any other solution of `R+S+T+U = 4I-E-F-G` meet support and also have at
least four labels of odd `c`? This witness has two, so the inherited count
excludes it as a word and leaves a different solution untouched. A word at
length 7 would be shorter than the eight-call minimum. The first step is one
other solution with four odd-`c` labels, then the same carrier scan.

The same odd-`c` question for the length-6 equation `R+S+T+U = 4I-E-F` stays
with PR #7100. This package does not take it.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant
and the subset-sum necessity are the PR2910 package as recorded in apoursh's
two-signed-frame floor, PR #6190. The four-call once-each support proof is
`research/four-signed-once-parity`, PR #6952. The one-old length-5 support
proof is PR #7083. The two-old length-6 witness, whose open question asks for
this three-old scan, is PR #7100. None of those results is redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review. New work is Apache-2.0.

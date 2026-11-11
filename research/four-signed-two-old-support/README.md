# Two old calls meet length-6 support

**Explicit support witness. No new κ and no word.**

Four nonzero symmetric rational rank-one matrices and two distinct old
projectors can meet target support for

```
R + S + T + U = 4I - E - F.
```

The six labels `A`, `B`, `P`, `Q`, `2A`, and `2B` sum to `4I`. Each target
is one of the pairs `A+P`, `A+Q`, `B+P`, and `B+Q`. Designating any two of
the four projectors as the old calls leaves the other four labels as added
frames. Added frames may equal old projectors; that is the permission already
stated for the length-5 equation. The argument is written in [PROOF.md](PROOF.md).

The same six labels fail the inherited odd-`c` count: `P` and `Q` are the
only labels with odd `c`, while all four targets have odd `c`. Under that
inherited inequality the witness is not a word. The inequality is not
reproved. Selected κ stays `781451/250000000`.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The
card asks for a larger or nonabelian native alphabet. This package stays in
the abelian symmetric 2-by-2 model and takes the two-old length-6 question
left open by the one-old support proof, PR #7083, which itself follows the
four-call note `research/four-signed-once-parity`. It does not redo either
proof, and it does not take another three-frame census profile.

Evidence classes, kept apart:

1. **Explicit witness.** The six matrices are the standard `uu^T` frames at
   the scales in [PROOF.md](PROOF.md). They are nonzero, rank one, and sum
   to `4I` because `P+Q = A+B = I`. Every old pair is checked, not only one
   orbit representative.
2. **Subset scan of that one solution.** All 63 nonempty subsets are summed.
   Each target occurs, and on this solution it occurs only as the declared
   projector pair. This is not a census of solutions.
3. **Odd-c count on that same solution.** Two calls, four targets. The
   inherited inequality is not reproved. Dropping `Q` removes `A+Q` and
   `B+Q` and keeps `A+P` and `B+P`. Shifting `2A` by `A` breaks the sum.

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
python3 scripts/research_package.py --package research/four-signed-two-old-support --check-only
python3.12 scripts/research_package.py --package research/four-signed-two-old-support
```

The direct check is `python3 -I -W error -B research/four-signed-two-old-support/verify.py`.

## Open next questions

Does any other solution of `R+S+T+U = 4I-E-F` meet support and also have at
least four labels of odd `c`? This witness has two, so the inherited count
excludes it and does not exclude a different solution. A word at length 6
would be shorter than the eight-call minimum. The first step is one other
integral solution with four odd-`c` labels, then the same subset scan.

Can four added frames plus three old calls meet support at length 7? The
six-label witness has no seventh matrix. The first step is three distinct
projectors and `R+S+T+U = 4I-E-F-G`, then one rational solution's subset scan.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant
and the subset-sum necessity are the PR2910 package as recorded in apoursh's
two-signed-frame floor, PR6190. The four-call once-each support proof is
`research/four-signed-once-parity`, PR #6952. The one-old length-5 support
proof, whose open question asks for this two-old scan, is PR #7083. Neither
proof is redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review. New work is Apache-2.0.

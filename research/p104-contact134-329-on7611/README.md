# One common-contact rechart on PR #7611

**Conditional κ = 0.003652740309**, more than **3.16496849e-7 above
PR #7611's certified raw upper bound**. All six required checks completed
against the frozen source: five in the original guarded run, and the unfinished
signed stage in one separately approved guarded completion. The first signed
380-second timeout and earlier #7610 stops remain preserved. See
[VALIDATION.md](VALIDATION.md), [RESULT.json](RESULT.json) and `evidence/`.

The contribution changes five occurrence-bound records involving public fields
134 and 329. Their common scalar contact moves from chart 618 to chart 373.
Four incident paid ranks `(3,1,1,4)` become `(2,0,2,5)`, with the zero leg
omitted. Across the actual 17-call signed caller,

`delta P = {1:-34, 2:+34, 3:-17, 4:-17, 5:+17}`, `delta T = {}`.

The candidate has 110,264 paid positions, 22,461 productive positions and rank
surplus 1,424. The comparison source has 110,281 paid positions. The scalar
opcode/operand/coefficient stream, external endpoints and ordered owned
chronology are preserved. No additional paid MOVE or owned lifetime is used.

## Sources and overlap

The branch starts at canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. Main selects
PR #7000. This contribution requests review of a pending conditional successor;
it does not alter that selection.

| Retained source | Inspected head | Role |
|---|---|---|
| [#7605](https://github.com/CrocSwap/integer-mult-bounds/pull/7605) | `e1d2756eecf03e146338239fee81772a99ba8d4c` | Complete application, two pricing engines and full source closure |
| [#7608](https://github.com/CrocSwap/integer-mult-bounds/pull/7608) | `24b082992cf2d7774bc3567540cc36ff58755334` | Hosted902 edit and inherited CLEAR44 condition |
| [#7611](https://github.com/CrocSwap/integer-mult-bounds/pull/7611) | `bbdbc8aea2f4fd94a927f6d8c438372c0c69ae6c` | Exact immediate word and complete comparison invoice |

All 166 retained files are byte-preserved and authenticated by the pinned
`data/retained-hashes.json`; `SOURCE-VERSIONS.json` also records their Git blob
identities; `SOURCE-ORIGINS.json` maps each subtree to its exact hosted source. The constructor checks the complete #7605 -> #7608 -> #7611 edit
lineage before applying the new five edits. The original tar source dependency
is included, so replay does not depend on another contributor's unmerged Git
objects or a local source cache.

The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19624227)
identifies this exact contact. Open PRs through #7611, related all-state text
queries and live Discussions 7111/1166/5645 were checked. Numeric GitHub searches
returned unrelated historical PR numbers and do not establish literal-text
novelty. Sparse, unpublished and non-atomic coverage remain limits. The ongoing
dual scan, network compiler and R3TILE scopes were excluded.

The old #7546 rechart trial and archive #7582 remain closed. The new token-settled
source supplies an explicit funded assignment that was absent from that trial.
The #7481 fixed-contact exclusion is not transferred to the changed scalar word.

## Reproduction

Use Python 3.12 with assertions enabled and the standard library:

```sh
python3 -B scripts/research_package.py --package research/p104-contact134-329-on7611
```

The generic hook above runs the four construction, physical, exact-row and
invoice-pricing commands, with a total declared cap of 270 seconds. Full
qualification also requires both dedicated application commands below, listed
in `APPLICATION-REPLAY.json`. Their per-command limits are 550 and 595 seconds;
run them in a dedicated Python 3.12 environment with 2 GiB, one CPU, no swap and
a 1,200-second job limit. This separates the longer application replay from the
generic hook's 1,200-second sum-of-timeouts limit; passing the generic hook alone
is not the full application result.

```sh
python3 -I -B research/p104-contact134-329-on7611/application.py \
  --stage native --work .contact134329-native-ff380ae0
python3 -I -B research/p104-contact134-329-on7611/application.py \
  --stage signed --work .contact134329-signed-ff380ae0 \
  --native-result .contact134329-native-ff380ae0/producer54/validation_native/NATIVE-RESULT.json \
  --native-adapters .contact134329-native-ff380ae0/CONTACT-ADAPTERS.json
```

These commands write the two named work directories in the repository working
directory. Start in a fresh checkout, or preserve earlier work directories under
different names. The launcher refuses to overwrite an existing directory.
Signed execution requires the fresh native result and matching counted adapter
ledger; the retained #7605 receipt is rejected. The original signed380-second
allocation timed out during its catalogue sweep; its evidence is preserved and
the user separately approved one unchanged-source signed-only completion.

For direct execution, `application.py --stage native --work ABSOLUTE_NEW_DIR`
produces the native receipt. Pass its `producer54/validation_native/NATIVE-RESULT.json`
and `CONTACT-ADAPTERS.json` to `--stage signed` in a different new work directory.
The immutable package can therefore be replayed from a writable external work
area without writing into the retained source.

The standalone `physical.py` checks six specified chart quotients on all 512
forward and 512 adjoint columns. The application checks all 66 affected pairs
with 18 signed Pauli generators and an exact basis-zero phase column in each
direction; six of those pairs additionally receive dense 512-column checks in
each direction. Complete qualification remains pending.

## Scope and limitations

The five framework assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. Relative to #7611, all 74
CLEAR contents must agree exactly. Relative to #7605, the sole inherited
change is ordinal44, owned1557 at chart595: its ideal row is now
`{451:-1,1495:1}` rather than
`{451:-1,902:-3/2,985:-3/2,1495:1}`. The paid whole-private-extent reset service
and its actual allocation, return chronology and numerical applicability remain
conditional. The rechart adds no erasure-content condition of its own.

All-column finite checks and author-side AI reviews do not establish a formal
proof-kernel theorem or independent human acceptance. The fixed-invoice ceiling
concerns this complete invoice, with the unchanged caller and framework; it is
not an optimum over other words, stock or callers.

## Open next questions

Independent substantive review should reproduce all six checks (the four registered commands plus both dedicated application commands) and inspect
the five literals, phase-bearing quotients, CLEAR44 binding and fresh
native-to-signed receipt chain. `TASK.json` states the first step and blockers.
No follow-on research region is reserved by this package.

## Credit

The new nomination came from the authorized GPT-6.1-Terra-high source audit.
Construction, source review, implementation and verification were prepared for
Clear1nsight with substantial OpenAI Codex and verified ChatGPT Pro assistance.
Twenty scoped Terra-high agents assisted source and feasibility work, followed
by disjoint implementation and author-side review assignments.

Ali Romman contributed #7605 and its complete application; DreamingOfClouds
contributed #7601/#7607/#7608/#7609/#7611; SYLforge contributed #7603; Hao Yan
contributed #7604; ToikY contributed #7546/#7544; Rohan Arun contributed the
#7113 caller and #7122/#7124 rechart methods. Clear1nsight, dillona, CubeJerry
and all nested source authors retain their credit and notices. Classical linear
conjugation and strict concavity are used in this particular new instance.
Apache-2.0; see LICENSE and NOTICE.

Historical #7610 remains credited as the preceding main46 contribution; #7611 supersedes that word.

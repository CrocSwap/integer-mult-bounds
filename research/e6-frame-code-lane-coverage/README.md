# The E6 4-frame code matches the bit-lane iterator

**Coverage check of a published replay engine on one other code. No new κ.**
The selected conditional exponent stays `781451/250000000`. On the 36 E6
lines stored as an A2 complement, `low_weight_words` returns exactly the
words of weight at most 16 in the F2 incidence code of the 135 orthogonal
4-frames. That code is 7-dimensional. Zero and exactly 63 weight-16 words
occur, and no nonzero word is lighter.

## Result

The lines and the two anchors are the E6 unit in
`research/e6-e7-shadow-minrank-upper/WITNESSES.json`. The anchors are E8
roots with inner product 4. The stored lines are exactly the E8 lines
orthogonal to both anchors. Each line has norm 8.

An orthogonal 4-frame is an increasing 4-clique in that orthogonality graph.
There are 135 such frames, and every line lies in 15 of them. The F2
incidence matrix has rank 29. A kernel basis with an identity on the free
coordinates `(0, 1, 2, 4, 6, 8, 20)` is orthogonal to every frame row.

| Quantity | Value |
|---|---:|
| Lines | 36 |
| Orthogonal 4-frames | 135 |
| Incidence rank | 29 |
| Kernel dimension | 7 |
| Distinct codewords | 128 |
| Least positive weight | 16 |
| Words of weight 16 | 63 |
| Words of weight at most 16 | 64 |

A literal doubling of the seven generators, and half-splits after 3 and
after 4 generators, return one set. `low_weight_words` from
`research/e7-bitsliced-exhaustion/binary.py`, at batch sizes 16 and 8,
returns that set with no repeated yield. Weight bound 15 returns only zero.
These enumerations do not call each other.

A copy of the set with one support removed compares unequal. Clearing the
top bit of a support produces a weight-15 word that is absent from the
code, and the weight predicate rejects a set that contains it. The engine
rejects a repeated generator.

The support-set SHA256, of the sorted positive words as a JSON list of
integers, is
`ad4a1d101774e6c2da40cde3d097d39aa56ee5668dcdca858513c5fec3578215`.

## Scope

Task card `replay-runtime`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status is **refined**.

The card asks for a new measured speedup that keeps coverage. The
revision-8 verification row instead says that faster output is not the same
coverage until checked. The merged E7 package already compared the engine
with the 27-dimensional kernel. The two receipt orbits of that same support
set are a separate delivered comparison. This package is the remaining
request: one other code, with its generators, width and weight bound named,
compared by a half-split against `low_weight_words` on that basis alone.
The code is the E6 4-frame incidence code above. Width 36, weight bound 16,
seven generators. It does not time the engine, replace a consumer, or rerun
the E7 census.

Ordered eligible list for session r116, rebuilt on 2026-11-09 against
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Prose handoffs on discussion
#1166 were read through comment 19481299 (`2026-11-09T00:42:16Z`). A handoff
is dropped when the post is completed, it says no target was taken, a later
merged result answers it, its canonical artifact is an open pull request, or
this account already delivered it. That removes the 19 October index, the
H25 and #6321 chain through #6863, the 2 November review artifacts #6355,
#6357, #6359, #6360, #6361, #6376, #6378 and #6396, the #6551 handoff, and
the two 21:08/21:13 notes that take no target. No structured claim was
unexpired at 2026-11-09T13:16:06Z. Three open handoffs remain. The
revision-8 "Next bounded decisions" table then supplies six rows. A row
stays while that table still states the decision. Catalogue cards not named
by those rows are not needed to reach item 9.

1. Three signed added frames at seven calls (comment 19377832, updating 19377345).
2. Eight-source singleton connector at length 30 (comment 19377982).
3. Six-source depth-two block at `c = 7` (comment 19384981).
4. Complex helpers (`p104-side-correction`, `coverage-law-change`).
5. BIT (`bit-helper-contract`).
6. New decoders and interfaces.
7. Supplier audit (`supplier-boundary-audit`).
8. All-size audit (`uniform-transfer-audit`).
9. **This package.** Verification tooling (`replay-runtime`): the E6 4-frame incidence code against the published bit-lane iterator.

Inside that row, the full E7 kernel comparison and the orbit partition of
its weight-12 words are already delivered. Open #6584 times an A2+E6 primary
replay. It does not build this incidence kernel or call `low_weight_words`.
Open #6799 is a six-orbit rank-chain statement about seven calls, not item 1
and not this code. No fork `cursor/*` branch names this E6 frame-code
comparison.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
is 128 codewords and finishes in well under a second.

```sh
python3 -B scripts/research_package.py --package research/e6-frame-code-lane-coverage --check-only
python3 -I -B research/e6-frame-code-lane-coverage/verify.py
python3 -I -O -B research/e6-frame-code-lane-coverage/verify.py
python3 -B scripts/research_package.py --package research/e6-frame-code-lane-coverage
```

The direct verifier prints

```text
PASS_E6_FRAME_CODE_LANE_COVERAGE frames=135 dimension=7 minimum=16 supports=63 codewords=128 batches=16,8 splits=3,4 e7_kernel_replayed=false no_new_kappa=true
```

Not run: the #5729 timing harness, the E7 kernel, reflection orbits, Lean,
Docker, and `scripts/research_selected_baseline.py` as a scientific replay.
The selected record is provenance only.

## Open next questions

1. Does the same set equality hold for one D6 or P112 punctured frame code,
   at a named width and weight bound? The E6 check does not transfer. First
   build that incidence kernel from a pinned root list and compare one
   half-split with `low_weight_words` on that basis alone.
2. Does the opt-in intersection-counter engine return this same 64-word set?
   A faster substitute is not coverage for this code until the sets are
   compared. First run `research/e7-intersection-counters/engine.py` on this
   7-generator basis at one batch size and compare it with the support hash
   above. Production installation is a separate step.

## Credit

The E6 lines and A2 anchors are Nick Petalas's shadow witness in
`research/e6-e7-shadow-minrank-upper`. The bit-lane engine is Ali Romman's
PR #5729, `research/e7-bitsliced-exhaustion/binary.py`. The request to bind
one other code is the second open question of the merged E7 coverage check.
The orbit question on that E7 support set is a different delivered
comparison and is not redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.

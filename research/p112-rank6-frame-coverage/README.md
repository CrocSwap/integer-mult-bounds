# P112 rank-six star trims: sharp frame-demand copy bill 60

**Scoped structural result and exact census. No masked decoder, supplier or new kappa.**

The exact C/N support theorem in David Arias's PR1236 has copy floor 64 and
excludes further support trims. Cinna Davis's PR1323 showed that a first copy
saving from an original cost-seven atom needs at least 20 support deletions.
This contribution asks what frame coverage survives that saving, including
arbitrary simultaneous trims of both factors, on the same fixed P112 model.

## Result

Every rank-six descendant of an original cost-seven atom meets at most **1,120
of the 1,260 live frames**. A rank-factorization argument reduces all arbitrary
joint cuts to maximal one-axis functional zero sets. Both checkers agree across
all **7,616 tagged parents and 967,232 maximal slices**, not just the minimum
deletion witnesses of PR1323.

| Maximum hits after arbitrary joint rank-six trimming | Tagged parents |
|---:|---:|
| 1,080 | 5,824 |
| 1,120 | 1,792 |

The averaged copy bound is only `10080*6/1120 = 54`. Simultaneous frame demands
give the stronger, sharp **integer relaxation optimum 60**: nine terms are
excluded by the inherited nine-root obstruction, while `COVERING.json` supplies
ten cost-six support pairs meeting every frame at least eight times. The exact
hit counts are 8 on 376 frames, 9 on 648, and 10 on 236.

This ten-term frame witness leaves **21 diagonals uncovered**. It therefore
cannot be a masked decoder, regardless of coefficients. That concrete failure
is a negative control and shows why the relaxation's value must not be promoted
to a construction. A 120-second search adding diagonal coverage found no
feasible incumbent; it did not exhaust that search or prove infeasibility.

The [proof](PROOF.md) gives the all-cuts reduction, the inherited ten-term
obstruction, the exact relaxation definition and the limits. In particular,
original rank-eight/nine parents, descendants of rank five or lower, mixtures
with other cost classes, different punctures and shared-copy pricing are outside
this optimization. Other term classes may have different frame efficiencies.

## Reproduce

From the repository root, standard-library Python:

```sh
python3 -I -O -B research/p112-rank6-frame-coverage/verify.py
python3 -I -O -B research/p112-rank6-frame-coverage/independent.py
```

Expected markers:

```text
PASS_P112_RANK6_FRAME_COVERAGE atoms=7616 slices=967232 max_hits=1120 average_floor=54 cover_bill=60
PASS_INDEPENDENT_P112_RANK6_COVERAGE atoms=7616 slices=967232 max_hits=1120 cover_bill=60
```

`generated/COVERAGE.jsonl` stores one record per tagged parent:
`[left_tag, right_tag, maximum_row_hits, attaining_cut_hex, attaining_cut_size,
maximizer_count, all_127_cut_hit_digest]`. Each digest encodes sorted nonzero
cuts as `hex_cut`, tab, decimal hits, newline. Bit positions refer to original
root IDs 0 through 119. Transposed parent records supply column maxima.
`generated/CERTIFICATE.json` records the full distributions and a maximum-hit
witness. The explicit writer option refuses existing output directories.

The separate implementation imports no primary or predecessor program. It uses
Weyl reflections, row-coordinate duals and set-based frame enumeration. Both
engines belong to this contribution; independent human review is not claimed.

Eight tests cover all 4,096 binary 3-by-4 matrices and 524,160 joint restrictions,
the rank-factorization domination lemma, exact frame receipts, the uncovered
diagonal obstruction, deliberately false copy/frame witnesses, source and table
corruption, overwrite refusal and optimized relocation. Finite regressions test
the implementations; the written argument supplies the arbitrary-cut scope.

The optional `search_cover.py` proposes witnesses with NumPy 2.5.3 and SciPy
1.18.1, as used in the recorded run. Its exhaustive candidate generation yields
5,376 distinct maximum-hit frame patterns. Assignment seed 20 forces sorted
pattern index 20. It chooses ten distinct patterns and has a 120-second solver
limit. `SEARCH.json` records the feasible first run; `DIAGONAL-SEARCH.json`
records the single bounded refinement without a feasible incumbent. Solver
arithmetic is not part of acceptance: both standard-library engines check the
fixed witness exactly.
The refinement keeps one first-enumerated support representative per frame
pattern. Other representatives with the same frame hits may have different
diagonal coverage, so the refinement does not exhaust even the maximum-hit
support dictionary.

```sh
OPENBLAS_NUM_THREADS=1 python3 -B research/p112-rank6-frame-coverage/search_cover.py --output /tmp/new-frame-search.json
```

The search may return a different witness or hit its time limit; neither outcome
changes the committed exact certificate. Add `--diagonal` to reproduce the
stronger searched constraint. Output paths must be new.

## Open next questions

Can rank-six support cuts participate in an exact masked identity below cost
64 once diagonal and orthogonal-entry equations are imposed? A feasible first
step is a support-level relaxation adding diagonal coverage and stronger
per-frame rank constraints across the **full** slice dictionary. The recorded
search used only maximum-hit patterns and did not decide even its restricted
diagonal-cover problem. A favorable support relaxation would still require
exact coefficients, helpers, source access, frame changes, restoration, hosting
and a complete recursive cost recurrence. The current frame-only certificate
does not supply any of these obligations.

## Provenance and credit

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Fresh OS assignment seed **20**,
complex supplier track. Coordination: [discussion 1330](https://github.com/CrocSwap/integer-mult-bounds/discussions/1330).
Exact commits, Git blobs and archive hashes are in `SOURCES.json`; source archives
and their original notice are unchanged.

Navinor (@navinor), PR1226 at `8b10989e4e45f0f9ce41004d7898a21a32f87e11`,
supplies the P112 model and root-star census. David Arias (@DavidAriasC), PR1236
at `ee8437bd9879272094e20c024cd34a53c4e84cd8`, supplies the original sharp cost64
theorem and nine-root obstruction; Hanson Sun (@bbMisk), PR1242 at
`7f31a561787864f26eb2242ef35179d07223accf`, independently corroborates it and
identifies further trims as open. Cinna Davis, PR1323 at
`c1144855242a56ffc1090be2f075f977d123d947`, supplies the first-erasure result and
ordered model. PR717 by DreamingOfClouds and retained PR968 geometry are credited
in the frozen notice. None of these pending packages is silently adopted as
the selected frontier.

New work by **Cinna Davis (@1337isnot1337)** with substantial **OpenAI Codex
assistance** in proof analysis, code, experiments, checks and writing.
Apache-2.0; `LICENSE` and the predecessor notice are retained.

# Validation record

Environment: Windows 11 x64, Python 3.12.14 (`python3.12.exe`), no
third-party packages. All commands from the repository root at base commit
`f567884aeb8851b6e794af1184119a3bfbe1e631`, run with `-I -B`.

## Commands and outcomes

1. `python3 -I -B research/r439-bsection-survey/search.py`
   Prints the ten per-block results (frames 506..524, minima 24/30/39,
   five donor-supply witnesses, two global infeasibilities) and
   `spliced frames: [506, 523] forward gates saved: 8 -> full word ADDs
   24289`. Regenerates `CANDIDATES.json` and `CERTIFICATE.json`; both files
   were byte-identical (SHA-256) across repeated runs.

2. `python3 -I -B research/r439-bsection-survey/verify.py`
   Exit 0, wall time 87.5 s, prints `"status": "PASS_R439_BSECTION_SURVEY"`
   with columns 661, survey all ten frames, spliced `[506, 523]`, bills
   `adds 24305 -> 24289`, forward positive bound 49,347 (equal), composed
   reverse positive bound `1,113,070 -> 1,090,494`, payload 93 bits,
   rank mass 5,129, identical frame paths for all 661 registers, H1-H5
   hypotheses and conclusions all true, and 12 rejected negative controls.

3. Receipt red test: `EXPECTED.json` tampered (block 523 minimum set to 40);
   the same command failed with `Reject: survey receipts differ` in 85.7 s,
   exit 1. Receipts restored from backup; the green run above followed.

## Checks recomputed by `verify.py`

- Source pins (base commit and three consumed files) and certificate schema.
- Per block: binding (frame, slice, registers, original bill), forward
  integer map by independent column propagation.
- Class minima and infeasibilities by a backward Bellman recursion over
  realized-register subsets with its own iterative-deepening donor
  enumeration (written independently of `search.py`; the two agreed on all
  ten blocks).
- Donor-supply infeasibility certificates by direct recounting of fitting
  donors and their column totals.
- Spliced blocks: forward map equality, reverse maps (entrywise comparison
  recorded per block), exhaustive Boolean truth tables (1,024 inputs at frame
  506, 4,096 at frame 523).
- Whole word: splice lengths, unrelated fields unchanged, literal cleanup
  reversal (H4), register frame paths (nesting-legal and identical to the
  original on all 661 registers), exact F2 endpoint on all 661 dirty-input
  columns before and after.
- Pinned `xcheck_p.py` interface check: H1-H5 hypotheses and all four
  conclusions hold on the spliced word.
- Paid profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` and rank
  mass 5,129 recomputed from frame paths and retained copy ranks.
- Pinned `export_records.py` bills on both words: ADD/copys/erasure counts,
  non-ADD event inventory, forward and reverse positive bounds by exact
  record replay, payload bits against the unchanged 104-bit cap.

## Negative controls (all rejected)

`mutated_candidate_source_506`, `unpaid_gate_506`,
`mutated_candidate_source_523`, `unpaid_gate_523`,
`inverted_domination_506`, `forged_domination_523`, `omitted_cleanup`,
`missing_gate_with_matching_cleanup`, `illegal_frame_descent`,
`stale_cleanup_literal_H4` (positive semantic control, rejected only by the
literal H4 guard), `wrong_slice_binding`, `forged_supply_witness`.

## Defects found by these checks during development

1. The backward donor recursion subtracted value-minus-goal instead of
   goal-minus-value, silently reporting infeasible for multi-donor rows.
   Caught by the cross-implementation disagreement with the forward DP
   (block 506), then fixed; both implementations now agree on all ten blocks.
2. The word builder spliced replacements left to right, so the 26 -> 24
   change at `B[102:128)` shifted block 523's indices by two and spliced the
   wrong gates. Caught by the whole-word F2 endpoint check at register 112.
3. The first mutation control changed a gate's source to its existing source
   (a no-op) and was correctly reported as "negative control accepted".
   Fixed to mutate to a distinct wire.

Each defect was observed as a failure before the fix; the final green run
above is after all three.

## Not run

C++ native legality and 5/9/11-stage replays, hosted invoice, global
assembly, selected cold replay (`make frontier799-verify`), `make verify`,
Lean builds and remote CI. Forward-map equality plus the recomputed exported
bills carry the cost claims; an independent native replay remains to confirm
them, as in the neighboring block PRs.

# Cold restoration of FULL-cleanup helpers on the T74 PR2322 words: single-gate conversions are legal but save nothing

**Research note (constructive screen with a scoped negative); no κ claim.** This follows up
[PR2429](https://github.com/CrocSwap/integer-mult-bounds/pull/2429), which found that 355 FULL-cleanup helpers of the
[PR2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322) words pay 525 rank units per call of end-of-call
restoration climbs. PR2429 priced the ideal of cold-restoring all of them at +10.8% of the LP ceiling. Here I
test whether the existing cold-restoration contract can realize any of it. That contract is the PR2226 / PR601
lineage: restore the helper inside the word at a partial frame, and let a private zero buffer stand in for it in
the FULL cleanup.

| step | method | result (both providers) |
|---|---|---|
| 1. single-gate screen | in the inverse-reverse cleanup, look for helpers whose restoration is one write `h −= c·s` that depends on no earlier cleanup gate, so it can move to the end of the forward word, and where joining h's frame with the source's frame saves a dimension | **8 of 355**: 559, 561, 569, 571, 576, 577, 578, 579, each with end climb 3. They sit next to the existing cold-restored 572–575 and 580–583. |
| 2. construction + exact replay | build each converted word on the pattern of the existing restore sections: restore the helper, **clear its input from every reader** (X registers included) with `r −= a·h`, set `helper_final`, and make the cleanup buffer-free. Then run the vendored PR2315 exact replay (ℚ⟨F⟩, forward and dual, arbitrary dirty inputs) and the frame check. | **all 8 converted words are legal, and all 8 save nothing.** Clearing the readers forces the restore frame to contain each reader's frame (dimensions 6 to 8), so the joined frame is FULL for every candidate. The unmodified words replay as a control. |
| 3. time-resolved frame heuristic (known proof gap) | after h's last use, estimate the restored frame from the cheapest holder of each variable of h's accumulated content | computed histogram {0:60, 1:216, 2:15, 3:64}, totaling 438 of 525 end-climb dimensions; the floating-point LP estimate is **+8.86%**, not a proved upper bound |

**Reading.** The cheapest move, one commuting restoring gate with reader clearing, is legal for 8 helpers but
saves **nothing**. The reason is frames, not the contract: every reader of the restored input must be cleared
through a gate that reads h, so h's final frame contains every reader's frame, and for all 8 that join is FULL.

Step 3 is an exploratory heuristic with a known gap: h's old content could be moved out and its variable
supplied by another holder. The author reports additional reviewer span checks, including a tentative
54-of-525 estimate, but those checks are not reproduced by this registered package. Neither that report
nor agreement on some cases repairs the missing general argument. The printed `frame_bound` fields are
historical heuristic labels; they are not certified bounds.

For the eight screened single-gate conversions, reader clearing joins the frame to FULL and leaves zero
saving. A useful different realization must avoid or otherwise pay for that obstruction; this experiment
does not exclude every possible restoration mechanism.

## Reproduce

From the repository root, standard library only:

```sh
python3 -I -B research/t74-cold-restoration-screen/restoration_screen.py --fetch    # ~25 s
```

`--fetch` fetches `refs/pull/2322/head` (002304ef) if absent. The words are blob-pinned. The vendored tools are
this author's PR2387 `fill_check80.py` / `ceiling_lp.py` / iteration-3 `price_check.py`, and PR2315's
`words_check.py`, all pinned.

Expected final line:
`PASS_T74_COLD_RESTORATION_SCREEN single_gate=8 legal=8 saving=0 frame_bound=438/525 frame_bound_gain=+8.86% no_new_kappa`

All results were run on CPython 3.14.4; the registered Python 3.12 replay was not run locally.

## Scope and limits

- **Construction.** It follows the existing restore-section pattern and was corrected after adversarial review;
  a first attempt omitted reader clearing. "Saving 0" holds for these 8 single-gate moves: their readers' frames
  join to FULL.
- **Step-3 estimate.** It has a known proof gap and is not accepted as an upper bound. The reported
  reviewer span check is not included in the registered replay. The unchanged-forward-word premise
  and post-last-use warps need explicit treatment in a replacement proof.
- **Prices.** They are floating-point LP estimates on the fixed bin stock, without certified
  enclosures; a numerical price attached to an unproved heuristic is not a mathematical ceiling.

## Open next questions

- **Low-frame readers.** Are there helpers whose input readers all sit at low frames, so that a multi-gate
  restoration with reader clearing joins below FULL? First step: make the reviewer's span-based bound rigorous,
  including warps after the last use, and rank helpers by their reader-frame join.
- **Earlier restoration.** Can restoration be placed earlier in B, before the readers' frames grow? First step:
  for the 8 single-gate candidates, compute the reader-frame join at each helper's last use instead of at the
  end of the forward word.
- **The rest of the T74 line.** The words of PR2435 and PR2374 share PR2322's scalar word and cleanup. PR2435's
  change is frame-only (PR2446). Rerunning this screen on PR2435's frames is the natural check.

## Credits and licence

- PR2322 (Vlado Vojdanovski): the words.
- PR2226 (Cinna Davis): exact cold restoration and private zero buffers.
- PR601 / PR615 / PR617 / PR676 (Jeremy Kothe), PR604 (DreamingOfClouds) and PR608 (higherbeing): cold and
  hyperplane-ended helpers.
- PR2269 / PR2312 / PR2374 / PR2435 (Jeremy Kothe): the T74 line.
- PR2429 / PR2402 / PR2387 / PR2315 (this author): the earlier tools, vendored with pins.

Prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5).

An adversarial AI reviewer corrected the step-2 construction, which was missing reader clearing and had a
leaking buffer. It also identified the frame obstruction and flagged the gap in the step-3 argument. No
independent human review is claimed. Apache-2.0.

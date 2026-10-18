# R439: phase-B block programs on the helper-star D, and the guard headroom they free

**Finite bit-circuit construction; no new κ.** The selected result, the selected bit supplier and
`upstream/` are unchanged; the bit side does not bind.

The incorporated helper-star word (PR967, `research/r439-helper-stars-seed19`) rebuilt only D and kept
PR589's phase-B blocks. The shortest recorded block programs were built on the 24k-ADD PR589 word and
were explicitly left uncomposed with the D-substitution line (PR1015; batch-952 review). This package
composes them and prices one consequence:

| complete local word | ADDs | D ADDs | F | B | local / nine-stage bits (caps 104 / 192) |
|---|---:|---:|---:|---:|---|
| helper stars (main) | 11,783 | 5,563 | 72,847 | 10,394,084 | 102 / **192** |
| + ten spliced phase-B blocks | **11,515** | 5,563 | 24,625 | 5,846,566 | 95 / 181 |
| + same seed-19 star pass rerun | **11,500** | 5,548 | 25,717 | 5,911,840 | 95 / 182 |
| pair control (degree one, rerun) | 11,715 | 5,763 | 24,563 | 5,892,602 | 95 / 181 |

1. **Composition (−268).** Nine PR1015 multi-write programs and the incorporated PR923 frame-520
   program replace the ten phase-B blocks: 388 → 254 gates, with C rebuilt by the literal-cleanup
   rule. Every replacement has the original F2 block map (all 2^n inputs). Every replacement also
   has an equal integer transfer and a smaller reverse transfer. D is byte-identical to the
   helper-star word.
2. **Freed guard (−15 more).** The helper-star word sits at bit-length 192 under the 2^192
   nine-stage cap. Its seed-19 greedy pass rejected 24 nominees on that guard. With the spliced
   blocks, both positive bounds fall (F 72,847 → 24,625). The **unchanged** builder
   (`research/r439-helper-stars-seed19/build.py`, called as a library) is rerun on the same PR915
   parent with the same blocks spliced. That pass makes 0 guard rejections and admits 236 edges
   instead of 221, giving D 5,563 → 5,548.

For both words, PR589's A, scatter, copied totals, register frame paths, nine COPY/ERASE pairs and paid
profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` (rank mass 5,129) are unchanged. The pinned
owner checker gives the same H1–H5 pattern as the incorporated helper-star word. Only the two flags
that line already carries are false: syntactic `H2_D_frame0_targets_from_helpers` and `K_equals_D`.

## Reproduce

```sh
python3 -I -B research/r439-bsection-stars-seed01/verify.py
python3 -I -O -B research/r439-bsection-stars-seed01/verify.py
```

Expected (about 20 s each, standard library only):

```text
PASS_R439_BSECTION_STARS blocks=10 gates=388->254 ADDs=11783->11515->11500 guard_rejections=24->0 columns=661 controls=8 no_new_kappa
```

The verifier does the following:

* rebuilds all three payloads and both search receipts deterministically and compares them byte-wise;
* replays all 661 formal columns through the literal COPY/ERASE stream in both directions for four
  words (helper star, composition, candidate, pair control);
* checks the D dirty boundary against PR589;
* runs the pinned `xcheck_p.py` owner checker;
* recomputes the paid profile from frame paths and copy ranks;
* bills the pinned `export_records.py` records, whose bounds equal the literal-stream bounds here;
* checks both precision guards;
* confirms that the original search still gives 11,783 with 24 rejections;
* rejects eight controls, listed below.

| control | rejected by |
|---|---|
| mutated block source | F2 block map |
| dropped block gate | F2 block map |
| block gate at frame zero | illegal frame move |
| stale (pre-splice) cleanup | literal-cleanup rule; it is F2-exact but costs more ADDs |
| omitted cleanup gate | boundary |
| the 236-edge D without the spliced blocks | nine-stage guard |
| omitted star restoration | D boundary |
| 105-bit local bound | local guard |

The sixth control is the key one: the extra stars are admissible only because of the composition.

## Scope and what is not claimed

* **No κ change.** The bit supplier does not bind, and this word is not proposed as the selected
  supplier. Hosted invoice, supplier binding and outer assembly were not run.
* **Native replay not run.** The 5/9/11-stage C++/Boost replay was not run here because Boost
  headers were unavailable. Exact F2 endpoints, frame paths, exporter records and the owner checker
  were run.
* **No optimality claim.** The block programs are best-found results of their searches, not minima.
  The star pass is one deterministic greedy pass.
* **Not composed.** Open single-step D edits on the 11,783 word (#1040: −3; #1047: −14) were not
  tested on top of this word. Neither was the separate PR941/#1045 helper-matching line.

## Credit and disclosure

The block programs are by Aaron Wang (PR1015, open; `inputs/PR1015-CANDIDATE.json` is copied unchanged
from head `7588c797`) and Ross Richardson (PR923, frame 520, incorporated). The helper-star builder and
D are from PR967 (`research/r439-helper-stars-seed19`, prepared for @theon199). That work generalizes
Gareth Davidson's PR926 pairs on the PR915 target basis. The underlying word comes from DreamingOfClouds'
PR589 on eumemic's PR555, and the checkers come from the retained supplier lineage. Track 00–19 (bit
supplier), OS-random seed **1**, base `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

Prepared by Sagar Thakrar with substantial assistance from Anthropic Claude (Claude Code). Apache-2.0.

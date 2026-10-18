# One relocation or Steinberg rewrite plus exact reframing cannot raise PR589's bit c

**Status: scoped negative result (exhaustive finite search with exact certification). No new κ, no new supplier.**

The selected #799 assembly is complex-bound (bit lower 0.001733427…, complex lower 0.001664400…, κ = 0.001661634…),
so no bit-side change alone can move κ. This package settles a bit-side question that open
[PR886](https://github.com/CrocSwap/integer-mult-bounds/pull/886) leaves open. PR886 proves PR589's word frame-optimal
with the gate order fixed and concludes that further headroom on this word "must come from gate-order or structural
moves". Here the gate order changes by one relocation or two interacting relocations, or the gates change by one
Steinberg 3→2 rewrite, and every frame is then re-optimized exactly.

## Statement

Let W be PR589's tuned punctured R439 word (`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, the
selected bit supplier), with nine-stage c = `1733427039589844234749/10^24`. Allow one of the following moves:

- **summand relocation**: take one source s out of a phase-A or phase-B gate `t += {…, s, …}`, make it its own gate
  `t += s`, and insert it at any index reachable by crossing only gates it commutes with. For a single-source gate,
  the whole gate moves. The two indices next to its own remainder are the **in-place splits** of a multi-source gate.
- **gate relocation**: move a whole multi-source gate the same way.
- **cross-scatter relocation**: continue either move across the scatter into the other phase. This is allowed when the
  moved gate commutes with the scatter: it writes neither a target nor a retained total, and reads no target. That
  keeps H1–H5 syntactically: A still writes only z registers, and the new B gate writes z from z.

Two XOR gates commute iff neither writes a register the other reads. Then give **every** phase-A/phase-B gate any
closed frame, from the catalogue or not, such that all register frame chains nest. D, start and final frames are
unchanged. The nine retained totals keep their COPY frames, so COPY ranks stay 7 and the decoder constant stays 63.
Targets stay at frame 0 until the scatter. C is the literal reverse of the z-destination gates at the full frame (H4).

**Result (exhaustive over this class):** no relocation, under any frame assignment, gives a paid local profile with
c above W's. Of the 10,886 relocation classes:

| outcome | summand/A | gate/A | summand/B | gate/B | across scatter A→B | B→A | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| no legal frame assignment | 1,807 | 22 | 837 | 56 | 71 | 12 | 2,805 |
| optimum = W's exact profile | 4,925 | 0 | 2,886 | 0 | 153 | 4 | 7,968 |
| optimum strictly worse (c certified below) | 47 | 1 | 65 | 0 | 0 | 0 | 113 |
| **optimum better** | **0** | **0** | **0** | **0** | **0** | **0** | **0** |

The classes cover all **1,442,430** individual insertion indices: 1,323,506 within a phase and 118,924 across the
scatter. Every class whose optimum differs from W's has one of 17 distinct profiles. For each, exact rational moment
bounds at W's published lower endpoint show that the nine-stage moment exceeds 1, so its c is strictly smaller
(smallest certified excess 1.44×10⁻⁷). The worse profiles are rearrangements of climbs such as {2,5}→{3,4} or
4→1+3. Every illegal class fails in the forward least-frame pass. In 853 of them a retained total's last phase-A gate
already needs more than its COPY hyperplane. In 1,952 a target's forced frame passes its final hyperplane. Least
frames are lower bounds for every legal assignment, so no framing can rescue these.

**Steinberg 3→2 rewrites (PR548's mechanism, re-run greedily by PR589's tuner):** over F2,
`b: bt^=bs ; e: et^=bt` equals `e ; b ; (et^=bs)`, and `b ; e: bs^=es` equals `e ; b ; (bt^=es)`. So a triple
b, e, c whose members can be brought together through commuting gates collapses to `e ; b`. PR589's word has 659
such triples among single-source gates: A 519 (16 case 1, 503 case 2) and B 140 (19, 121). Every rewritten word
passes an exact F2 replay of D, A, scatter, B and the rebuilt C on all columns. Every exact optimum, computed by both
implementations, is **PR589's exact profile**: 659 neutral, none better, none worse.

**Depth-two extension (interacting pairs):** each of the 8,081 legal first moves m1 is applied, then every relocation
m2 of the changed word, including across the scatter, is enumerated on that word. m2 must come out of a gate that
touches a register of m1's moved operands or of m1's remainder gate. This gives **891,589 pairs**, 685,524 of them
legal. 663,741 legal pairs reproduce W's exact profile. The other 21,783 have one of 58 distinct profiles, each
certified exactly to have c below W's. **None is better.** The class covers "neutral move, then improving move" chains
on a common register, and contains PR589's own two-move path on PR555's word (see Controls). Pairs whose moves share no
register are not covered.

**Implications.** Under exact reframing, PR589's word is a local optimum of the paid profile for single relocations
(including in-place splits and cross-scatter moves), for interacting pairs of relocations, and for single Steinberg
3→2 rewrites. On this word, further bit headroom has to come from outside these classes:

- longer or non-interacting reorderings;
- changes to the op multiset (new or removed helpers, resynthesis);
- different COPY frames or decoder;
- the hosting remainder.

ADD-count constructions that preserve every register's frame path leave the paid profile unchanged by construction.
None of this can move κ until a complex supplier exceeds the bit side (now 0.0017334 vs 0.0016644).

## Relation to earlier work

- **PR589** (DreamingOfClouds; the selected bit supplier; tuner from PR541/548 by Dugongue and PR542 by rohanarun)
  relocates one elementary op and applies Steinberg 3→2 rewrites greedily, choosing frames locally with all other
  frames held fixed. It reached a fixed point after two moves and claims no optimality. Both of its move types are
  covered here, plus in-place splits, whole-gate and cross-scatter moves, with all frames re-optimized exactly after
  the move.
- **PR886** (SethBurkart123, open) is the exact frame-only optimum at the fixed order. Its class relaxes C beyond H4.
  This package keeps H4 and the COPY frames fixed, and reproduces its fixed-order conclusion on the A/B gates
  (149 free gates in 125 components here, versus 159 in 133 with C relaxed there).
- **PR711** (thakrarsagar, open; adjacent A swaps) and **PR661** (yuj1r0, open; phase-B frames at fixed order) treat
  the older R420 word, not the selected R439 word. Here the moves are not restricted to adjacent swaps.
- The R439 native ADD-count constructions target scalar additions, not the paid profile, so they are orthogonal to
  this question. They include phase-A mini-nodes (PR728, PR792), phase-B blocks (PR873, PR880, PR891, PR906 and
  others) and D compensation (PR915); those checked here (PR728, PR792, PR880, PR906) state that every frame path is
  preserved.

## Method

`reframe.py` computes the exact optimum over all frame assignments for a given gate order:

1. **Bounds.** Forward least frames `lo_g` are the closure of the operands' current least frames. A retained total's
   last phase-A gate is set to its COPY frame, because that gate fixes the frame the scatter reads. Backward greatest
   frames `hi_g` are the intersection of the operands' next upper bounds, with targets bounded by 0 before the scatter
   and COPY frames pinned. By induction along each register chain, every legal assignment has `lo_g ⊆ f_g ⊆ hi_g`, and
   the all-least assignment nests. If some `lo_g ⊄ hi_g`, or a least chain exceeds a final or COPY frame, no
   assignment exists.
2. **Components.** Gates with `lo_g = hi_g` are forced. Free gates interact only through register chains, and a forced
   gate between two free gates on a register fixes the frame there. The components of "consecutive free gates on a
   register" are therefore independent in both legality and cost (as in PR886).
3. **Enumeration.** Each component is enumerated over every closed frame between its bounds, built by closure from
   `lo_g`. Rank uses exact `Fraction` elimination.
4. **Objective.** At z = c the moment Σ n_d·d/(mW)·(m/d)^z is linear in the profile, the rank mass is invariant
   (5,129), and the moment increases in z. So a profile raises c only if Σ n_d·d·(64/d)^c decreases. Ties are
   compared as integer profiles, and every distinct non-base profile is then certified exactly (`certify.py`, using
   the repository's rational moment engine with the inherited fallback term and PR589's idle remainder).

D (all at frame 0 with operands at frame 0) and C (all at the full frame, every C operand ending at the full frame)
cannot add a climb beyond the last one to the final frame. `reframe.Word` asserts both facts, and the independent
implementation keeps D and C explicitly.

**Slot equivalence.** Moving a gate only changes the gate sequences of its own operand registers, plus its phase for
a cross-scatter move. Inserting at index q changes them only through the number of operand-touching gates before q,
so one index per slot represents every index in it. `search.py` walks from the original index and records one index
each time it crosses a gate that touches the moved operands, or the scatter. `independent_check.py` instead enumerates
all 1,442,430 indices and groups them by prefix counts. Both give the same 6,802 + 3,844 within-phase and 224 + 16
cross-scatter classes.

## Controls

- **Positive control (depth one).** On PR555's untuned word, the same search finds exactly five improving
  relocations. They are PR589's hoist (summand 470 out of `A[1993]`, placed before its remainder; the best single
  move) and PR589's sink (summand 469 out of `A[1994]`, placed after base gate 2028). The other three are a later
  placement of summand 470 (after gate 2036) and the in-place splits of both gates.
- **Positive control (depth two).** From the hoist, the best interacting second move found by the pair search is
  PR589's sink. The pair reaches exactly PR589's published local profile
  `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`; from the sink, the best second move is the hoist.
- **Explicit word.** `export.py` writes PR555 + hoist + sink with its optimal frames. PR589's `wlib.replay` checks the
  exact F2 endpoint on all 661 columns and nesting, and returns that profile. The unchanged independent checker
  `code/xcheck_p.py` accepts it: E8 labels, COPY ranks 7×9 at the punctured hyperplanes, H1–H5 and U/J/K/C⁻¹.
- **Steinberg detection control.** Under exact reframing, every inverse expansion `e ; b → b ; e ; c` of this word is
  itself neutral, so this control tests detection rather than a gain. Phase A is expanded once (seeded choice, with c
  moved to its farthest commuting slot). The 3→2 search on the expanded word lists the cancelling triple, and its
  rewrite gives back PR589's phase A gate for gate.
- **Negative controls.** Swapping an op with an adjacent gate that reads its destination (non-commuting) breaks the
  exact F2 endpoint. Lowering a gate frame below its forced bound makes the chains fail to nest.
- **Independent implementation** (`independent_check.py`, no shared code): frozenset frames, fraction-free integer
  span tests, D and C kept explicitly, enumeration of every insertion index, and coarser any-shared-register groups.
  On PR589's word it reproduces the class count (10,886 from 1,442,430 indices) and the outcome multiset of every
  moved summand or gate, with **0 mismatches** (7,968 identical, 113 worse, 2,805 illegal). It also agrees on all 659
  Steinberg optima. A seeded sample (seed 14) of 2,000 interacting pairs, rebuilt by its own move builder, agrees on
  every pair: 1,476 identical, 43 other, 481 illegal.

## Reproduce

Standard library only (no numpy, no compiler). From the repository root:

```sh
python3 -B research/bit589-transport-reframe/verify.py /fresh/output/dir
```

Expected last line (5 min 34 s with `--jobs 10` on a 12-thread Linux machine; peak parent RSS 52 MB):

```text
PASS_BIT589_TRANSPORT_REFRAME classes=10886 legal=8081 improving=0 control_rediscovered=2 independent_mismatches=0 certified=17 steinberg=659 pair_sample_agree=2000 no_new_kappa
```

The optional depth-two replay adds `--pairs`, which reruns the pair positive control, all 891,589 interacting pairs
and their exact certification (30 min 34 s with `--jobs 10`):

```text
PASS_BIT589_TRANSPORT_REFRAME classes=10886 legal=8081 improving=0 control_rediscovered=2 independent_mismatches=0 certified=17 steinberg=659 pair_sample_agree=2000 pairs=685524 no_new_kappa
```

Each step prints `ok <name>` after comparing its output with `EXPECTED.json`, and any difference stops the replay with
`FAIL`. Validated on Fedora Linux 44 (x86_64): the default replay passes under CPython 3.14.8 (forkserver workers)
and CPython 3.12.15 (fork workers), and the `--pairs` replay passes under CPython 3.14.8. No macOS or Windows run and
no remote CI are claimed.

`EXPECTED.json` freezes every count and profile. Individual entry points: `search.py WORD C [--detail]`,
`pairs.py WORD C`, `steinberg.py WORD C [--independent|--control]`, `independent_check.py WORD PRIMARY_DETAIL`,
`pair_sample_check.py WORD C N SEED`, `certify.py PROFILES`, `export.py WORD C OUT MOVES`.

## Scope and non-claims

- **Exhaustive only within the stated classes.** They are:
  - one relocation within A, within B or across the scatter;
  - interacting pairs of such relocations;
  - one Steinberg 3→2 rewrite of single-source gates;

  each followed by arbitrary frames. Not covered:
  - longer reorderings and non-interacting pairs;
  - Steinberg rewrites combined with relocations or with each other, rewrites involving multi-source gates, and
    other changes of the op multiset (pruning, new helpers, resynthesis);
  - changes to D, C, COPY frames, the decoder or the hosting (the idle remainder is about 13% of the bit moment);
  - other words.

  Absence of a candidate in this class is not an impossibility theorem for the bit supplier.
- The cost model is PR589's paid local profile priced by its `fastc` identity, c = certify(288·local + REM, 64,
  28416), with the idle remainder REM held at PR589's value, as PR589's own moves did. It is not a rerun of the C++
  hosting pipeline, which needs a compiler and Boost. A move that keeps the local profile could in principle change
  the frozen hosting selection; that is outside this model. With no improving candidate there is no new word to host.
- All inherited assumptions of PR555/PR589 and of the selected #799 review remain: all-size compiler,
  mutable-source realization, whole-call hosting, precision/tape and analytic hypotheses. This is not a Lean proof
  and does not formalize the multiplication theorem.
- The selected record, the PR589 package and `upstream/` are unchanged. Only this directory is added.

## Pins

| item | value |
|---|---|
| base commit | `f567884aeb8851b6e794af1184119a3bfbe1e631` |
| PR589 word (selected bit supplier; PR589 head `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`) | sha256 `e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`, content `5642fd0e…eba0b` (= PR589 `EXPECTED.json`) |
| PR555 word (positive control) | sha256 `1bc3c53d4baf4927c6a00c339ea3975516471a48074d4d97c6addaded2a4d858`, content `d0df3c89…5cbe3` |
| moment engine | sha256 `81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482` (= selected assembly input pin) |
| interface checker `code/xcheck_p.py` | sha256 `af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e` |
| compared open PRs | PR886 `881f72ec596a5c6d7aba801153792292ecc39737`, PR711 `ebd567a22d26fadc1c8292b5c57056fb52331266` |

## Attribution

Contributor: Ian Libânio (GitHub `ianlibanio`). Assignment seed **14** (OS randomness), bit-supplier track. No pinned
coordination issue existed, so the claim is local in `CLAIM.json`. The search, checkers, certification and this note
were prepared with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code). Apache-2.0.

Built on:

- eumemic's PR543/PR555 word, its `xcheck_p.py` and the R420 interface lemma;
- DreamingOfClouds' PR545/PR510/PR589 word, `wlib.py`, `fastc.py` and remainder identity;
- the transport and Steinberg 3→2 mechanisms of Dugongue's PR541/PR548 and rohanarun's PR542;
- SethBurkart123's PR886 bounds-and-components method;
- the R420 analogues of thakrarsagar (PR711) and yuj1r0 (PR661).

# Late-compensated helper entrances on the R439 bit word: a scoped census

**Scoped negative result with one open survivor. No construction and no new κ.**

- Track: 00–19 (bit supplier), assignment seed 9, drawn with the OS CSPRNG via Python `secrets`.
- Card: `bit-helper-contract`, with the scope **refined** in [TASK.json](TASK.json).
- Base: `0b1cccf8`. The selected record frontier1094 is complex-bound and is unchanged.

## The question

The inherited H2/K interface requires every helper to start at frame 0, so that a frame-0 prefix D can supply all dirt compensation (N = K).

An **entrance** lets one helper start at a nonzero frame E instead: a pivot p, plus the gauge q ^= p on a support c. This changes the response by ρ = Kc, so the targets in T = supp ρ need extra compensation.

What merged work settles and what it leaves open:
- #1179 found the kernel entrance 444+470, which has T = ∅.
- #1253 proved that this is the only kernel entrance among the common-frame entrances of all 366 closure classes.
- #1128 (PROOF §4) leaves "compensation moved after A" open.
- #1179 states that its condition K e_J = 0 is "not a statement about arbitrary later compensation".

This package **narrows** that open case. It looks at compensation **after the scatter**, with A and the scatter fixed and one entrance at a time.
- Inputs: every support of #1253's closure (4,954 supports from 5,548 (V, c) pairs) plus 5,212 enumerated source-donor entrances, of which 5,059 have a legal entrance frame.
- Words: the selected PR589 word and the four merged star words (#1062, #1122, #1188, #1208).
- Outcome: the case reduces to one open triple.

The broader case of #1128 §4, compensation after A but before the scatter, is not covered.

## The test

For each target t, W_t is the **dirt-only space**: the helper parts of every F2 combination, with zero source part, of the values t could legally read after the scatter. A support c is admitted only if every t ∈ T has some u ∈ W_t with u·c = 1. Otherwise it is **rejected**.

The test is run in three classes:

| Class | What t may read | What a REJECT proves |
|---|---|---|
| **LC-fav** | any register whose frame at the scatter cut lies in t's final frame t⊥, plus the nine COPY snapshots | Rejection for the **whole class** of post-scatter programs with monotone frames under the stated premises ([PROOF.md](PROOF.md)). This is the necessary test. |
| **A6** | B ++ C unchanged, plus inserted target reads with a carrier check and read-only relays | Rejection for A6, which is contained in LC-fav. |
| **A6R** | A6 plus storage relays (a target that received reads may be read later); relay restoration is ignored | Nothing: A6R is an over-approximation, used only to show that a survivor is *not* excluded. |

The carrier check requires the reading register and the register being read to both fit inside the gate's frame.

The scout's prototype class (`strict_proto`) is kept for traceability only. It has no carrier check, so it is not physical, and on these words it gives the same results as LC-fav.

## Results ([RESULT.json](RESULT.json); identical on all five words)

| | LC-fav | A6 |
|---|---|---|
| Supports admitted | 2: 444+470 (T = ∅, #1179's kernel pair) and **444+470+578** (\|T\| = 8) | 1: 444+470 (T = ∅) |
| Single helpers | 0 / 439 | 0 / 439 |
| New pairs | 0 / 1,569 | 0 / 1,569 |
| Source donors (5,212 enumerated, 5,059 placeable) | 0 kernel, 0 late | 0 kernel, 0 late |
| Linear relaxation (366 classes) | one nonzero class (frame 79's line), kernel {444+470, 578}, 84 rows kept | one nonzero class, kernel {444+470}, 94 rows kept |
| max dim W_t | 5 | 4 |
| K incidences covered | 98 / 18,085 | 47 / 18,085 |

**Apart from the kernel pair:**
- No late-compensated entrance exists in A6.
- In the sound LC-fav class, only the triple **444+470+578** survives. Its targets are 113, 118, 150, 153, 192, 197, 214 and 219.

**The triple is OPEN.**
- A6 covers only 150 and 197.
- A6R covers all 8.
- A6R restricted to relays inside T covers 150, 153, 192 and 197.

So, within A6R (B ++ C fixed, insertion-only target reads), covering all 8 targets needs storage relays outside T, which must later be restored. LC-fav also allows a rewritten B or C and fresh restored registers, which A6R does not model. That remains open (open question 1).

**Why so little survives.** Every W_t is a *coordinate* subspace, spanned by at most 5 unit vectors e_j (at most 4 in A6). A target can therefore compensate a support only where the support meets that small set of helpers. Only 98 of the 18,085 nonzero K incidences (47 in A6) fall inside these sets.

## Two engines

**Engine 1** ([census.py](census.py)) computes:
- the raw replay, K, the first contacts and the closure L;
- W_t in every class;
- the parity census of every support;
- the per-class linear relaxation, with a check that it contains every admitted support;
- the source donors and A6R.

**Engine 2** ([engine2.py](engine2.py)) shares no code with engine 1. It uses:
- a set-valued replay;
- rational-annihilator geometry, which also checks that every frame is closed, so that label inclusion equals rational containment;
- a closure that also equals #1253's `CERTIFICATE.json`;
- a kernel method for LC-fav and per-pair change points for A6.

It agrees with engine 1 on K, the closure, every W_t (LC-fav and A6) and every **support verdict**. The source-donor census, the relaxation, the scout class and A6R are computed by engine 1 alone.

## Controls

Recorded in RESULT.json; [test_package.py](test_package.py) has 20 tests.

- **A realisable late entrance, on a synthetic word.**
  - `W_syn` is PR589 with target 150's compensation of helper 470 moved after the scatter: three B reads into 150 (149 at frame 0, then 149 and 470 at frame 323), with 470 dropped from D's row 150.
  - On `W_syn` the census admits 444+470 as a *late* entrance (T = {150}) in LC-fav and A6.
  - The built witness passes the merged `wlib.replay`:
    - start[444] = 79, with the shear at the head of A and its inverse at the end of C;
    - three post-scatter reads into 150;
    - D′ = PR589's D without 444, i.e. `W_syn`'s D minus 444 with 470 restored at row 150.
  - Without its late reads, the witness fails replay at register 150.
  - Its late reads undo `W_syn`'s own moved compensation, so after B it carries the same values as #1179's prefix entrance on PR589. It is a check that an admission can be realised, not a new construction.
  - `W_syn` with D left unedited also fails at 150.
  - Both words are rebuilt in code and checked by canonical sha256.
- **Mutations that flip verdicts.**
  - Flipping one K bit rejects 444+470.
  - Letting register 77 be read at FULL admits the triple in A6.
  - Emptying target 150's reads rejects the triple.
- **Binding.** A flipped word byte is rejected by its digest, and so is a wrong pin.
- **Structure.** All frames are closed, and a frame with a dropped label is detected. Reads during C reduce to reads at the end of B: C is entirely at FULL and touches no target.
- **Sanity checks of the census itself** (true by construction):
  - with every unit vector added to every W_t, all supports are admitted;
  - the kernel pair (T = ∅) is admitted;
  - clearing K's column 578 admits 578.

## Scope

**Covered.** For each single common-frame entrance on these five words, with A and the scatter fixed, no pre-scatter wires, and the endpoint required on all 661 columns:
- the LC-fav REJECTs hold for the whole post-scatter class;
- the A6 REJECTs hold for insertion-only compensation.

**Not covered:**
- a changed A;
- targets leaving frame 0 before the scatter;
- a new COPY, or scatter changes beyond added snapshot terms;
- gauge shears after A or at several frames;
- source-dependent basis changes other than the donor shear;
- several simultaneous entrances;
- recursive interfaces and hosting.

**No κ.** The bit side does not bind. An entrance would at most save the pivot's first climb (−H1), which width-8 hosting cancels with +H1 (#1179, #1253).

## Reproduce

```sh
python3 -I -B research/r439-late-entrance-census-seed09/verify.py          # about 3 min; PASS_R439_LATE_ENTRANCE_CENSUS
python3 -I -B -m unittest discover -s research/r439-late-entrance-census-seed09 -p test_package.py
python3 scripts/research_package.py --package research/r439-late-entrance-census-seed09 --check-only
python3.12 scripts/research_package.py --package research/r439-late-entrance-census-seed09
```

- `--no-a6r` skips the A6R runs and stops before RESULT.json is checked.
- Requirements: standard-library Python 3.10 or later.
- Tested on Python 3.12.15 and 3.14.8 (macOS 26.5, arm64).

## Open next questions

1. **Can the triple 444+470+578 be realised in LC-fav?** It is the only support that survives the sound test.
   - Why it matters: at the cut, helper 470 carries s_470 + x₇₇ at frame 79. Within A6R its 8 targets can be covered only through relays outside T. A rewritten B in which the targets read 470 and source 77 directly is not excluded.
   - First step: record which reads A6R uses for each target, build a candidate word (relays first, then a rewritten B reading 77 directly), and test it with `wlib.replay` and #1179's literal stream checks.
   - Blocked by: restoring the relay targets, or a legal rewritten B.
2. **Do simultaneous entrances admit late compensation where single ones do not?**
   - Why it matters: this census is one entrance at a time. The joint test requires (K_t·c_i)_i ∈ {(u·c_i)_i : u ∈ W_t} for every t.
   - First step: run the joint test over pairs of disjoint supports in the same class V.
   - Blocked by: none.
3. **Does a different scatter enlarge W_t enough to admit a late single entrance?**
   - Why it matters: the coordinate W_t of at most 5 helpers is a property of this scatter. Adding snapshot terms is already inside the class and changes nothing.
   - First step: move one retained total to another helper and recompute W_t.
   - Blocked by: pricing the changed COPY with #1128 §5's argument.

## Relation to earlier work and credit

- **#1128** (aliromman): the width-seven boundary obstruction. This package narrows the case its PROOF §4 names. Lemma 1 is its §1 dependency-path argument, and Lemma 2 is the dual of its §2 erasure invariant.
- **#1179** (adamgall): the kernel pair 444+470. Its literal stream checks are proposed for a future witness of the triple; they are not run here.
- **#1253** (mightyOil): the all-support common-frame kernel entrances and the closure L. Its certificate is reproduced here.
- **#1194** (woklerx) and **#1311** (Arham-Tahir64): the semantic-D contract.
- **The star words:** #1062 (thakrarsagar), #1122 and #1188 (bitplane) and #1208 (ToikY). Their helper-star D comes from #967 (theon199), built on #915/#926 (bitplane).
- **The R439 word and its checker:** eumemic (#543/#555), including the scatter and `xcheck_p.py`. DreamingOfClouds (#589) supplied the two A-section transports and `wlib.py`.
- **The helper-470/source-77 boundary** behind the survivor: #1043 (aliromman, open), #1079 (bbMisk / Hanson Sun) and #1256 (RossRichardson).
- **Kernel-entrance precedents:** #254 (Dugongue) and #382 (chafreaky).
- **Different mechanisms:** open #1810 (RossRichardson; dirty workspace on B) and open #1580/#1592 (Arham-Tahir64; terminal star compensation).

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via Claude Code.
- Parallel read-only scout and judge subagents selected the question.
- Reader subagents and a synthesizer audited the scout's criterion. They found the triple the scout had missed and the missing carrier check in the scout's strict class, and they specified the classes.
- The engines, the proof note and the controls were then written fresh.
- A post-PR adversarial review corrected the witness description, the scope of the open triple, the citations and the controls (second commit).

No claim was posted to Discussions. New material is Apache-2.0.

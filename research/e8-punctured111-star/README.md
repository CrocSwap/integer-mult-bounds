# Punctured star bit unit: 111 ports, nine rank-7 totals, R = 489

**Bit c = 0.00165947204563779652541, +4.54% over the live bit c of PR #510.** κ is another matter: composed with #535's
complex b, κ = 0.001587467473762886 is **complex-bound, +0.16% over #535**. The bit word raises the cap on any future complex
gain; it does not move κ by more than that today.

This package ships one E8 bit word and the parameterisation of PR #493's hosted-audit chain that prices it. The word is
PR #493's quad skeleton with 9 of the 120 labelled E8 lines punctured (neither source nor target), so it has **v = 111 live
ports**. The nine retained decoder totals are nine *pseudo-target* helpers, one per punctured line, each of frame rank 7, so the
decoder constant is **cst = 9 x 7 = 63** (PR #493 / #503: 9 x 8 = 72). The result is **R = 489** helpers (480 skeleton helpers
+ 9 totals). The chain (emit, independent audit, exact price, outer assembly) is #493's, with every hard-coded
120 / 72 / 9600 / 489 derived from the word.

| quantity | value |
|---|---|
| bit c, eleven stages, eight pooled replicas, every residual whole and hosted (10^-24 grid; #472's pipeline as #493 runs it) | `165947204563779652541/100000000000000000000000` = **0.00165947204563779652541** |
| live bit c: PR #510's R480 word at nine stages (the bit supplier of #535) | 0.001587447106092548137108 (**+4.5372%**) |
| same pipeline on PR #503's R480 word (v = 120), reproduced by `verify.py` | 0.001574753352953808650916 (+5.3798%) |
| pricing harness `code/price/pricex.py` (independent local-histogram replay + the same hosting programme + `moment.certify`) | equal to all 24 digits, same profile |
| κ with #535's complex b = `1589991533606044174031/10^24` | **`793733736881443/500000000000000000` = 0.001587467473762886**, complex-bound; #535 publishes 0.001584931111785787 (bit-bound at the live bit c) |
| robustness: c under a stricter hosting (one helper per family copy per stage), `code/price/price458.py` | >= 0.001651282591289915996071 (at most 0.49% lower; still +4.02% over the live bit c); κ unchanged |

#535's complex b (0.00158999) is 4.37% below this unit's c, so κ is complex-bound and rises +0.1600%
(0.001584931111785787 -> 0.001587467473762886). The remaining 4.37% of bit headroom pays only against a future complex b above
1.59e-3. The κ line is computed by the same outer code that reproduces #535's published κ from #510's bit c (step 9, control).

## What the unit is

* Word: `data/bitE8mut-v111-r489.json.gz`, format `bitE8/1+mut` (PR #493), `v = 111`, `R = 489`, `ports_geom` = the 111 live
  labels as indices into the 120-line system, `punctured` = **[39, 52, 57, 71, 76, 78, 103, 109, 114]** (footprint (1^9): one
  punctured line in each of nine 4-frames; none of lines 0..7, so the frame-zero residual basis 2e_0..2e_7 is made of live
  labels and PR #493's residual-isometry check applies unchanged). `verify.py` rebuilds it byte for byte from PR #493's frozen
  plan with `code/word/gen_punct.py`.
* Skeleton: #493's, verbatim, restricted to the live lines. Every helper register is kept; the carriers of punctured lines stay as
  junk wires (18). The phase-A total for a punctured line y_j is a fresh helper that reads exactly what the removed target would
  read (the two quad outputs and the Q delivery at D6[Hy], then its two needers at y_j-perp): its x-part is z_{y_j} restricted to
  the live lines, its frame has rank 7, and it is issued at the end of phase A, so no reader needs an extra climb. Hosting the
  totals on dead registers (as #503 does for rank 8) fails here: a rank-7 total can only combine dead registers whose frames lie
  inside y_j-perp, and none has a frame in D6[Hy].
* Frames are the live line sets of the closed 120-line frames; their ranks are recomputed by every checker from the word's own
  `lines`.
* Choice of P: of 414 sampled punctures (W1's search), 304 reach R = 489 and 110 need 1-3 Q-node junk wires (R = 490-492); among the
  R = 489 words c varies slightly (1.659350e-3 to 1.659472e-3, 8 distinct local histograms). The shipped word has the highest c
  found (reached by 145 of the 414). A different representative of footprint (3,3,1,1,1), P = [16,22,32,43,54,70,76,90,103],
  builds R = 491 and c = 1.656230e-3; it is not this word. No claim is made that 489 is a floor for other skeletons.

## What was parameterised (`code/adapt.py`)

`adapt.py` writes adapted copies of nine parent files by 55 exact string edits (each anchor must occur exactly the listed number
of times, as in #503). The parent tree is never modified. Nothing is read from the environment; the one configuration
(`code/punct_cfg.py`) is derived from the word (v, R, live labels, the totals map) and, in scripts that never see the word, from
the exported records.

| file | constant (parent) | now |
|---|---|---|
| `emit.py` | `(h, v, form) == (8, 120, ...)` | v from the word; configuration checked against the word |
| | COPY rank `== 8` | `0 < rank <= 8`; the sum over the nine totals is the CST and must equal the word's totals map (63) |
| | `72` (local mass identity, rank-mass deficit, deficit field) | CST |
| | replica stride `1200` (3x) | `2 K v` |
| `audit.py` | `V, R = 120, 489`, `DATA = 9600`, physical `9609`, deficit `3264`, `72`, `len(ports) == 120`, helper offset `240`, stride `1200` (2x), `geometry_routes = 1320` | V, R from the records (`n = 2V + R`); CST from the audit's own replay of the records' COPY ranks; `DATA = 2 K V T` |
| `local_audit.py` | `969`, `729`, `240` (2x), `R489` status string, the word path | `2V + n`, `n`, `2V`, `R%d`, the word given to `adapt.py` (as #503 does) |
| `assemble.py` | `V = 120`, `72`, suppliers file | `V` from the bit's GLOBAL.json; the deficit from the audit (it must fit nine copy ranks); optional suppliers argument |
| `host_select.py` | `V = 120` | `V = word['v']` |
| nine-/eleven-stage `geometry.py` | all 120 ports emitted; `240`, `120`, `1080`, `1320` | only the live ports, re-indexed 0..v-1; counts from `len(LIVE)` |
| `chk/checkword.py` | `len(lines) == v == 120` | `100 <= v <= 120`, plus: every label is one of the 120 E8 root lines (the lines of #493's word, which #370's checker accepts); norm 2, pairwise \|ip\| <= 1, rank 8 still checked; `relax.py` is the parent's, unchanged |
| `mutate_records.py` | "COPY with a cheaper rank" sets the rank to the literal 7 | `rank - 1` (a literal 7 is the true rank of a rank-7 total) |

Unchanged and already general: the C++ checkers (`-DVPORTS=v -DRHELP=R -DNCOPY=9`, `HDIM = 8`; their COPY check is
`z == dim(frame)`), the residual-isometry check (`validate_isometries`, stock call), `export_records.py`, `stage_cohort.py`,
`gram_frames.py`, `interface.py`, `mutate_mut.py`, `mutate_records_mut.py`, the moment engines, the row bound, and the outer
assembly (it sees only c, b and the bit's charged coefficient bits). The cited complex b enters as a bare rational; there is
**no port count on the complex side of the assembly**, so the bit v = 111 is not tied to the complex word's own v.

## Checks (`verify.py`)

0. This package's `MANIFEST.json` and #493's `MANIFEST.sha256`.
P. (full mode) #493's `verify.sh`, unchanged.
1. The word rebuilt from #493's plan is byte-identical; the configuration (v, R, totals map, CST = 63).
2. Independent checker (#370's, `v <= 120` and the E8-membership check, relaxed for mutable sources by #493's `relax.py`): exact F2
   replay of all 2v + R columns, frame nesting, Gram, price; `interface.py` (#425's hypotheses); the word-level mutants.
3. Official cohort checkers at (v, R): legality (NCOPY = 9), five-stage columns (payload 91 bits < 104), eleven-stage columns
   (24/24 omitted-bridge controls), KPAIRS = 2 regression, record mutants.
4. Exact Gram on all 636 frames.
5. Geometry (live labels), #442 hosting programme (rediscovers `data/hosting-v111-r489.json`), emit, independent audit (22 template
   mutations), assembly (47 strict inequalities and controls) with #535's complex b.
6. `pricex.py` agrees with the hosted-audit c to all 24 digits; hosting-stacking statistics; `price458.py` (stricter hosting).
7. **Regression**: PR #503's R480 word through the stock chain (parent `emit.py` / `assemble.py`, #503's `audit.py` /
   `local_audit.py`) and through the adapted chain: `GLOBAL.json`, `GLOBAL-TEMPLATE.json.gz`, `AUDIT.json`, `RESULT.json` are
   byte-identical (GEOMETRY.json stores its own run time and is shared), equal to #503's EXPECTED (c, profile, emitted-program
   sha256, κ for three suppliers).
8. **Mutation controls** (`code/mutants.py`, 8): dropped gate, wrong frame, payload overflow (legal and F2-correct; refused only by
   `columns_h`), cell collision (#442 rule), a helper hosted on the family the call acts on, a cheaper profile claim, v tied to 112
   (the cited complex word's port count), the stock #493 emitter on the 111-port word. M4a tests same-cell collisions only; it is
   not a test of #458's one-helper-per-family rule (see Scope).
9. Composition with #535's complex b, and the control that reproduces #535's published κ from #510's bit c with the same code.

## Rank-mass identity for v < 120

The chain asserts `M * live - mass = T (2 K v - L cst)` (here M = 78, T = 8, K = 5, L = 11, live = 2 K v T). It is a telescoping
identity, valid for any v:

* locally, sources climb rank 1 to 8, targets 0 to 7 and helpers 0 to 8, so the local mass is `8 R + cst + 14 v`;
* at eleven stages the idle ranks sum to 308 per family (2 v families), and the 88 R hosted helper climbs of width 8 are paid out
  of that idle rank, so the global mass is `T (11 (8 R + cst + 14 v) + 616 v - 88 R) = T (11 cst + 770 v)`;
* with `M * live = 780 v T` the difference is `T (10 v - 11 cst)`.

For v = 111 and cst = 63 this is 8 x 417 = 3336 (v = 120, cst = 72: 3264). The same shape, `D = h ((s-1) v - s cst)`, is the one
PR #523 uses for its punctured complex word; emit and audit check the identity numerically on the emitted program.

## Scope and what is not claimed

* The word is checked as a `bitE8/1` word with 111 labels (norm 2, pairwise |ip| <= 1, rank 8, labels in the 120-line E8 system);
  that a 111-port unit with cst = 63 is an admissible bit supplier for the outer assembly rests on the same hypotheses as v = 120.
  Everything #493 and #472 assume (all-size compiler, common-label/mutable-basis interface, whole-call hosting) is assumed
  unchanged. This package makes no unconditional claim.
* **Hosting rule.** The hosting is the pooled whole-residual programme of #442 / #472 / #493 (`hosting_core.solve`, eight replicas
  pooled, `2 v T` copies per idle child): every helper residual is hosted whole on an idle data family, at disjoint cells. It does
  **not** satisfy #458's literal rule that an entering helper is the only owner of its physical family in an invocation: in 82 of
  the 88 calls several helpers of that call sit on one family (at most 7), at disjoint offsets. This is inherited: PR #503's
  accepted emitted program does the same in 80 of 88 calls (reproduced by step 7). `verify.py` prints both counts. Under the stricter
  rule "one helper per family copy per stage" (which implies #458's per-invocation rule) the unit still prices at
  c >= 0.001651282591289915996071 (at most 0.49% lower, +4.02% over the live bit c); κ is complex-bound and unchanged.
* Payload margin: 91 bits against 104. Stage count: the unit is feasible only at eleven (and thirteen) stages; the nine-stage
  hosting wall is R <= 4 v = 444.
* The pricing harness and the hosted emit/audit share `hosting_core`; their agreement at v = 111 checks the adapted emitter and
  audit against an independent local-histogram replay, not the hosting programme itself.

## Credit

PR #493 (eumemic) is the skeleton, the word family and the chain; #503 (DreamingOfClouds) the dead-total variant and the
`adapt.py` pattern; #523 (icekylinx) the puncture pattern on the complex side (ports removed, copy ranks lowered, D recomputed);
#472 (chafreaky), #442 (DaysSky), #445, #386, #370 (Dylan Crow), #381, #315 the pipeline and checkers; #510 the live bit c; #535
(icekylinx) the cited complex b; the independent audit of this package supplied `code/price/price458.py`. Prepared by
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Maintainer portability correction (2026-10-12)

The R480 regression may rediscover a different HiGHS optimum. The maintainer
replay checks exact integer feasibility, capacities, idle windows, helper
coverage and the residual histogram for both nominations using the already
reviewed #503 comparison. Both physical pipelines still consume the same
frozen allocation and must reproduce the unchanged physical audit and bill.
This replaces only equality with the solver's historical tie choice.

The stricter-hosting pricing diagnostic also checks all rounded integer stock
and stage-demand equalities exactly. Its rate is an auxiliary allocation and
moment calculation; no separate physical emission under that stricter rule
is supplied. The selected construction retains the disclosed pooled-cell
hosting contract.

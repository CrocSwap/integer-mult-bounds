# The complex supplier at p = 10: explicit numbered programs at h = 20

**Claim.** Compile the source-assisted complex word of PR #184/#194 at cube size p = 10 (h = 2p = 20, v = 8·C(10, 3)
= 960 ports) instead of p = 11, with the query modules of `modules/` (triple module p = 10, pair module n = 9,
all-but-one module n = 8) and the frozen layers of `layers/` (carrier arcs, PR #200's descended operation frames,
reuse pairs of PR #193's or PR #233's recipe, kernel pairs). Each of the six words is one explicit program in Jacob
Sussman's certificate format gcert/1 with the star scatter, accepted by his reference checker `gx.check1` and his
Python mirror of the two Lean checks `gxcore.py` (jacobalansussman/wht-power-saving-lean, `tools/gx/`, commit
`f010392c`; both vendored unchanged in `gx/`). In the bridged five-stage word B₂ written out at h = 20 (m = 5h = 100,
W = 4v + R, idle climbs e₃₈, e₁₉, e₄₂, e₄) the exact rational bounds certify:

- **centre-sharing set, PR #233's maximum-weight pairs: a = 7795/10⁷** (8,375 registers, R = 6,455, W = 10,295;
  7796/10⁷ rejected); with PR #193's pairs 7747/10⁷;
- **PR #304's recipe on the annealed set, PR #233's pairs: a = 7737/10⁷** (8,435 registers, R = 6,515, W = 10,355;
  7738/10⁷ rejected); with PR #193's pairs 7689/10⁷;
- same-recipe control (PR #168 v4's modules cut to p = 10): 7375/10⁷ and 7322/10⁷.

Each claim holds with and without the five-stage packages' 10⁻¹⁶ fallback envelope, and the fallback-inclusive coarse
savings on the 10⁻¹⁸ grid are certified by two independent engines (§2, step 12). No new κ by itself: on the open
frontier the bit side (PR #320, 7.69199e-4, cited) lies below PR #315's p = 11 complex supplier (7727/10⁷) and below
both prices here; a κ package that adopts this supplier would see the complex cap rise from 7.727e-4 to 7.796e-4
(whether it may is §5's open point).

## 1. Inputs

- **Modules** (`modules/`). JSON files in the formats of PR #168's sources, read by the rebuilt tree's own loaders,
  which check the module contracts at p = 10: in the pair module every root sums exactly the inputs disjoint from its
  pair, in the all-but-one module every root sums all inputs but one, in the triple module every root J sums the
  inputs I disjoint from J, and every addition joins disjoint supports. The centre-sharing pair module has a 37th
  root, the sum of all 36 inputs; `centre46.load_pmod46` checks the 36 pair roots and the full sum. All are zero
  restrictions of p = 11 module files (PR #168 v4's or PR #304's), the non-control ones then annealed at p = 10; the
  search is not part of the proof. The three control files are re-derived by `verify.py` (§3).
- **Frozen layer** (`layers/<set>/`): `matching-arcs.json`, `physical-frames.json` (the operations whose frame differs
  from the closure frame, in the canonical form of `source_aligned_local_v4.py`), `physical-pairs-{parity,mw}.json`
  (reuse pairs [donor, recipient, deadline]) and `kernel-pairs-{parity,mw}.json` (two kernel pairs on the control's
  parity layer, none elsewhere). `discovery/make_layer_p.py` is how they were found; `verify.py` only checks them.
- **The word builder** (`aligned_word_p.py`). It is PR #304's `aligned_word.py`, i.e. `source_aligned_local_v4.py`
  of PR #202 (Avi Eisenberg, PR #193/#194) with its four discovery steps replaced by inputs, with three changes:
  the cube size is a parameter (`Graph(p)`, modules at p, p − 1, p − 2); `--centre46` builds the centre-sharing graph
  (`centre46.finish_centre46`: the star centre S(2i + e) is the pair module's 37th root instead of a separate sum,
  which is what PR #315's 10-line `Graph.finish` patch does); and when `select()` chooses gauges that the script then
  drops, the record's gauge ledger is corrected to the kept gauges (§5). Everything else (local configuration, merge
  f8:00111100, `compile_closure`, `select`, phase-one prefix, forward closure with future-cap clipping and local-pair
  checks, gauge filtering, target histogram, `paired_cube_physical.physical()`, the encoding of the seven output
  files) is the script's.

## 2. Chain of checks (each of the six words)

1. **Module contracts**: `triple_module_from`, `pair_module_from` (or `load_pmod46`), `all_but_one_from` at p = 10.
2. **Arcs**: `compile_closure` (PR #162, DaysSky) accepts the frozen arcs (one donor per use, a donor carries one of
   its own operands, acyclic generalized dependency graph, every value span inside its backward-intersection frame,
   exact positive-rank ledger with mass h·R + loss) and keeps them unchanged; `select` chooses the gauges.
3. **Frames**: the script's forward closure, run with every frozen frame as the preferred frame, returns every frozen
   frame unchanged; the frozen list is the script's canonical list of moved frames.
4. **Pairs**: every pair is an edge of the script's candidate graph, one pair per donor and per recipient, and the
   list is a fixed point of the script's last-late-control reordering. `paircheck.py` then re-checks the pairs from
   the written word alone (kinds, one-to-one, every gauge paired, early and late chronology, donor frame inside the
   gauge, no pair erasable by PR #184's source-donor purification) and rejects five mutations, each for the condition
   it breaks.
5. **Physical checks** (`scripts/paired_cube_physical.py`, PR #168 lineage): nested role chains, pair legality and
   read chronology, the exact spliced recount, and a randomized numeric replay of the aliased signed word mod 2⁶¹ − 1
   with random dirty scratch; `verify.py` recomputes this profile in-process and requires it to equal the file.
6. **Admission** (PR #200's complete complex checker `complex/physical.py`, Chafik Boukhalfa): exact signed scalar
   pairs, full backward and gauge intersections, the positive-rank ledger recounted against the record, descended
   frames, nested chains, aliases and target read chronology, the exact adjoint with a formal coefficient bound,
   every formal source, target and dirty column; the early-read and missing-read mutations are rejected.
7. **Flow and exact lift** (PR #184, icekylinx): `complex_frame_flow.py --witness --purify-source-donors
   --recycle-kernels` with the frozen kernel pairs, then `exact_complex_flow_lift.py`.
8. **Contract** (PR #194's `contract_v4.py`, as PR #233 runs it).
9. **Program** (PR #256's `gcert_emit.py`, unchanged) and **reference checks** on the emitted program: `gx.check1`
   (E0/E1 labels, E2 the scatter cut, E3/E4 gate shapes, E5 the exact scalar identity, E6 the price data
   N = R·h + 2v(h − 1) + cst) and Sussman's `gxcore.py` mirror (its block histogram equals the program's).
10. **Ledger**: 3(x + y + s + c) + 2v·e₂ of the program's block histogram equals the flow's child histogram.
11. **Star scatter** (`normalize_scatter.py`): all six programs are emitted in star form (every retained-total unit
    is +1), so nothing is re-signed; `gx.check1` and `gxcore` accept the committed program again, and both reject it
    with one scalar sign flipped (E5).
12. **Price** at h = 20: H₅ = 5·H_inv + 2v(e₃₈ + e₁₉ + e₄₂ + e₄), m = 100, W = 4v + R; W·m − |H₅| = 4v − 5·cst = 2,040
    (cst = h(h − 2) = 360). (a) The moment Σ n_r (r/m)^{1−a} is below W at the claimed a by PR #225's exact upper
    bound (PR #304's convention), and also with the fallback envelope added (32·m²·Σn rank-one calls at weight
    10⁻¹⁶); at a + 10⁻⁷ PR #225's bound fails and source527's exact lower bound of the normalized moment exceeds 1.
    (b) The coarse saving b: the largest 10⁻¹⁸ grid point at which the normalized moment with the fallback is below 1,
    certified by `scripts/source527/moment.py` (with its `bad` envelope) and by `base_two_moment.py` (the envelope as a
    separate rank-one term), the next 10⁻¹⁸ point excluded by both; the same without the fallback is recorded; a ≤ b.
13. **Reproduction**: the six programs equal the committed `certificates/` byte for byte (uncompressed JSON), and
    every number above equals `certificate/expected.json`.

## 3. Anchors

- **(a)** `aligned_word_p.py` at its default p = 11, given PR #168 v4's modules and the source-aligned word's own arcs,
  frames and pairs, reproduces the seven output files of `source_aligned_local_v4.py` byte for byte.
- **(b)** PR #194's word through this package's chain (at p = 11) gives PR #256's certificate of that word (same
  sha256 of the canonical JSON) and the block histogram of Sussman's published certificate of #193 in every class and
  rank; the generic idle-rank formula gives PR #304's (42, 21, 46, 4) there.
- **(c)** The control modules are `module_cut.min_cut` of PR #168 v4's three module files in the rebuilt tree (the
  fewest-additions single-point zero restriction), byte for byte.
- **(d)** PR #315's patch `references/centre46_graph.diff` applied to the rebuilt `scripts/paired_cube/graph.py`
  builds, on the centre-sharing modules, the same graph as `centre46.finish_centre46` in every field but the status
  string, and leaves the graph of the 36-root pair module unchanged.
- There is no external histogram for any p = 10 word: nothing else compiles this word at p = 10. The control passes
  the same chain and is the like-for-like baseline; the exploratory runs that first produced these programs (with a
  script version of the same recipe) gave the same programs.

## 4. Results

| word | R | registers | blocks | N | W | certified a | rejected | coarse b with fallback (/10¹⁸) |
|---|---|---|---|---|---|---|---|---|
| control, parity pairs | 7,121 | 9,041 | 49,631 | 179,260 | 10,961 | 7322/10⁷ | 7323/10⁷ | 732209244332069 |
| control, mw pairs | 7,125 | 9,045 | 49,282 | 179,340 | 10,965 | 7375/10⁷ | 7376/10⁷ | 737511222939316 |
| PR #304 recipe, parity pairs | 6,515 | 8,435 | 48,602 | 167,140 | 10,355 | 7689/10⁷ | 7690/10⁷ | 768912365785154 |
| PR #304 recipe, mw pairs | 6,515 | 8,435 | 48,299 | 167,140 | 10,355 | 7737/10⁷ | 7738/10⁷ | 773718577669358 |
| centre-sharing, parity pairs | 6,455 | 8,375 | 48,278 | 165,940 | 10,295 | 7747/10⁷ | 7748/10⁷ | 774746506241368 |
| centre-sharing, mw pairs | 6,455 | 8,375 | 47,979 | 165,940 | 10,295 | 7795/10⁷ | 7796/10⁷ | 779597612622781 |

Every program has m = 100, deficit 2,040, cst = 360, scalar denominators 2 (x, slots) and 6 (y), and the star scatter
as emitted. The fallback lowers the coarse saving by about 3·10⁻¹² (`certificate/expected.json`). Gains on the
certified grid points: annealed over control +4.91% (mw, 362/7375) and +5.01% (parity); centre-sharing over control
+5.69% and +5.80%; PR #304's recipe at p = 10 over PR #304 at p = 11 (7635 and 7586/10⁷) +1.34% and +1.36%; the
centre-sharing word over PR #315's p = 11 centre-sharing program (7727/10⁷) +0.88%. The centre-sharing set has no
control of its own: against the PR #304-recipe set (7795 vs 7737, +0.75%) it changes both the graph (the centre
patch) and the pair module (`pmod46_pc1_p10.json` vs `pmod_p3_p10.json`, different parents), so that gain is not
the patch's alone.

## 5. What is not claimed

- **No Lean build in this package.** `verify.py` checks the programs with Sussman's Python reference checker and his
  Python mirror of the Lean checks. Separately, both mw programs were compiled with his unchanged generator and
  kernel-checked locally (`wht_main_block_B2Gcc95x`, 1 − 7795973/10¹⁰; `wht_main_block_B2Gcp37x`,
  1 − 7737183/10¹⁰; `tools/Compare.lean` passed; axioms propext, Classical.choice, Quot.sound; see README). The
  official comparator was not run, and the Lean files are not part of this package.
- **The five-stage layout at h = 20.** The ledger H₅ = 5·H_inv + 2v(e_{2h−2} + e_{h−1} + e_{2h+2} + e₄), m = 5h,
  W = 4v + R is applied at h = 20 as the generic formula. PR #304 applied it at h = 22 only (as did every Lean run of a
  complex program), and at R values other than #193's; that it holds verbatim here is the generic B₂ statement of
  Sussman's repository (`bankPrice h`), not something this package re-proves.
- **The fallback envelope** (10⁻¹⁶, 32·m² rank-one calls per paid child) is the five-stage packages' inherited
  assumption, here evaluated at m = 100; it is not a new m = 5h admission.
- **What a κ package must change to adopt these programs.** The outer assembly uses only the two coarse savings,
  and the two suppliers' widths already differ in PR #315 (bit m = 100, complex m = 110). But PR #315's package
  (and PR #296's, from which its complex checks come) pins the p = 11 complex program in five places, which must be
  generalized or re-pinned before a p = 10 program can be used:
  - `code/complex_labels.py`, `code/complex_scalars.py` and `code/complex_splice.py` hard-code h = 22, v = 1,320 and
    22 centres;
  - `portable_complex.py` asserts (110, 9036, 22, 14316) and pins R, N and the reference histograms;
  - `math_check.complex_supplier()` asserts m = 110, W = 14,316, the histogram totals (351,820 calls, 1,571,680
    rank mass) and the literal b.

  The programs here are in the star form those checks read. This package does not make those changes.
- **Record correction.** On the control's cut modules `select()` chooses 8 gauges of ranks 14 and 13 that the
  script drops; `aligned_word_p.py` removes their births from the record so that PR #200's checker can recount it.
  The correction is checked, not trusted: the checker recounts the ledger from the word. The programs do not read
  the corrected fields (`physical()` reads other record fields, none of the three corrected ones).
- **Discovery is numerical.** Floating-point scores chose the modules, frames and pairs; every choice is a frozen input
  that the chain checks exactly. The annealing effort is asymmetric (about 1.5 h at p = 10 against the p = 11
  anneals of PR #168 and PR #304), so the p = 10 prices are not a bound on what p = 10 modules can reach. Cutting
  PR #304's p = 11 modules straight to p = 10 gives only 7235/10⁷, so the gain over p = 11 comes from re-annealing at
  p = 10, not from the cut.

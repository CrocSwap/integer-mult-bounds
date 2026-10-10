# Re-annealed complex modules: a stronger complex supplier as explicit numbered programs

**Claim.** Replace the three query modules of the source-assisted complex word of PR #184/#194 (PR #168 v4's pair
module, n = 10; all-but-one module, n = 9; disjoint-triple module, p = 11) by the re-annealed modules of `modules/`,
and compile the word with the frozen layer of `layers/cmod/` (carrier arcs, PR #200's descended operation frames,
PR #233's maximum-weight reuse pairs, no kernel reuse). The result is one explicit program in Jacob Sussman's
certificate format gcert/1, 11,800 numbered registers (1,320 sources x, 1,320 targets y, 9,160 slots) with the star
scatter, accepted by his reference checker `gx.check1` and by his Python mirror of the two Lean checks `gxcore.py`
(jacobalansussman/wht-power-saving-lean, `tools/gx/`, commit `f010392c`; both vendored unchanged in `gx/`). In the
bridged five-stage word of that repository (m = 5h = 110, W = 4v + R = 14,440) it is certified at saving
a = 7635/10⁷ with exact rational bounds (7636/10⁷ rejected), against 7547/10⁷ for PR #233's word (PR #256). With PR
#193's parity-avoiding pairs instead: 7586/10⁷. The same recipe on PR #168 v4's own modules (`layers/pr168-v4/`, the
control) gives 7522/10⁷ and 7469/10⁷. No new κ by itself: on the frontier of PR #299 the bit supplier (7.50462e-4)
lies below PR #233's complex price and below both re-annealed prices, so the bit side still binds; the complex cap
rises from 7.547e-4 to 7.635e-4.

## 1. Inputs

- **Modules** (`modules/`). Three JSON files in the formats of PR #168's sources, read by the rebuilt tree's own
  loaders, which check the module contracts: in the pair module every root sums exactly the inputs disjoint from its
  pair, in the all-but-one module every root sums all inputs but one, in the triple module every root J sums the
  inputs I disjoint from J, and every addition joins disjoint supports. They were found by simulated annealing from
  PR #168 v4's modules against the exact compile ledger of the aligned word; the search is not part of the proof.
- **Frozen layer** (`layers/<set>/`): `matching-arcs.json` (carrier arcs), `physical-frames.json` (the operations
  whose frame differs from the closure frame, in the canonical form of `source_aligned_local_v4.py`),
  `physical-pairs-{parity,mw}.json` (reuse pairs [donor, recipient, deadline] of the two recipes),
  `kernel-pairs-{parity,mw}.json` (empty: the flow reuses no kernel on any of the four words). `discovery/make_layer.py`
  is how they were found; `verify.py` only checks them.
- **The word builder** (`aligned_word.py`). It is `source_aligned_local_v4.py` of PR #202 (Avi Eisenberg, PR
  #193/#194) with its four discovery steps replaced by inputs: the module files (hard-coded there), the arcs (mapped
  there from PR #168's matching), the preferred frames (inherited there from PR #168's layer) and the pairs (its own
  `--pairs` option). The local configuration, `Graph.finish`, the merge f8:00111100, `compile_closure`, `select`, the
  phase-one prefix, the forward closure with its future-cap clipping and local-pair checks, gauge filtering, the
  target histogram, `paired_cube_physical.physical()` and the encoding of the seven output files are the script's.

## 2. Chain of checks (each of the four words)

1. **Module contracts**: `triple_module_from`, `pair_module_from`, `all_but_one_from` of the rebuilt tree.
2. **Arcs**: `compile_closure` (PR #162, DaysSky) accepts the frozen arcs (one donor per use, a donor carries one of
   its own operands, acyclic generalized dependency graph, every value span inside its backward-intersection frame,
   exact positive-rank ledger with mass h·R + loss) and keeps them unchanged; `select` chooses the gauges.
3. **Frames**: the script's forward closure, run with every frozen frame as the preferred frame, returns every frozen
   frame unchanged: each contains its value span and both predecessor frames, lies inside its exact future cap,
   every local operation has its minimal frame, every local pair its span, every root role ends inside its root
   frame. The frozen list is the script's canonical list of moved frames.
4. **Pairs**: every pair is an edge of the script's candidate graph (donor ungauged and not a root, its last frame
   inside the recipient's gauge frame, its last operation before the recipient's first, deadline as the script
   assigns it), one pair per donor and per recipient, and the list is a fixed point of the script's last-late-control
   reordering. `paircheck.py` then re-checks the pairs from the written word alone (kinds, one-to-one, every gauge
   paired, early and late chronology, donor frame inside the gauge, no pair erasable by PR #184's source-donor
   purification) and rejects five mutations, each for the condition it breaks: a late recipient given an unused
   donor still alive at its read; an unused donor with legal timing whose last frame lies outside the gauge (rejected
   for frame containment alone); a duplicated pair; an unpaired gauge; an unused donor with legal timing whose last
   frame is parity-erasable (rejected for erasability alone).
5. **Physical checks** (`scripts/paired_cube_physical.py`, eumemic; PR #124/#131/#143 lineage): nested role chains,
   pair legality and read chronology, the exact spliced recount, and a randomized numeric replay of the aliased
   signed word mod 2⁶¹ − 1 with random dirty scratch, for two seeds; omitting a read, reading early and flipping a
   coefficient are rejected. `verify.py` recomputes this profile in-process for the admission and requires it to
   equal the file. (The exact identity of the whole program is step 9's E5.)
6. **Admission** (PR #200's complete complex checker `complex/physical.py`, Chafik Boukhalfa, as PR #233 admits its
   layer): all descended frames, nested chains, aliases and target read chronology, the exact adjoint with a
   formal coefficient bound, every formal source, target and dirty column under both shear signs; the early-read and
   missing-read mutations are rejected.
7. **Flow and exact lift** (PR #184, icekylinx): `complex_frame_flow.py --witness --purify-source-donors
   --recycle-kernels` with the frozen kernel pairs, then `exact_complex_flow_lift.py`: exact rational local
   invertible completions at every node, monotone flow, zero-fresh kernel reuse DAG, dyadic coefficients.
8. **Contract** (PR #194's `contract_v4.py`, as PR #233 runs it): fresh columns equal the identity, centres in phase
   one, target cap reads in phase two, nested target chains, source controls before the original K, the integer
   histogram recount.
9. **Program** (PR #256's `gcert_emit.py`, unchanged) and **reference check** (`gx.check1`): E0/E1 labels (every
   register's frames are nested reduced-echelon subspaces of F₂^h, every gate at one frame), E2 the scatter cut
   (retained totals at their frames, targets untouched; in star form also exactly h = 22 totals, which in table form
   only the emitter's own assertion checks), E3/E4 gate shapes, E5 the exact scalar identity (every target receives
   exactly its source, every source is restored), E6 the price data N = R·h + 2v(h − 1) + cst.
10. **Ledger**: 3(x + y + s + c) + 2v·e₂ of the program's block histogram equals the flow's child histogram.
11. **Star scatter** (`normalize_scatter.py`): where the emitter wrote a scatter table, every column must be the star
    column times one unit ±1; the registers of the totals with unit −1 are re-signed over the whole program (every
    coefficient on an edge with exactly one endpoint in such a register changes sign) and the star rule is written.
    The result must differ from the emitted program only in coefficient signs, the scatter and the name; `gx.check1`
    accepts it again (same denominators, coefficient bounds and frame steps) and Sussman's `gxcore.py` mirror of the
    two Lean checks accepts it with the same block histogram. This is the committed program.
12. **Price**: in Sussman's bridged five-stage word the ledger is H₅ = 5·H_inv + 2v(e₄₂ + e₂₁ + e₄₆ + e₄) per cover
    vertex (PR #250's statement for PR #234/#209's layout), m = 110, W = 4v + R. The moment Σ n_r (r/m)^{1−a} is
    below W at the claimed a and not at a + 10⁻⁷, with the exact upper bounds of `scripts/moment.py` (PR #225).
13. **Reproduction**: the four programs equal the committed `certificates/` byte for byte (uncompressed JSON), and
    every number above equals `certificate/expected.json`.

## 3. Anchors

- `aligned_word.py`, given PR #168 v4's modules and the source-aligned word's own arcs, frames and pairs, reproduces
  the seven output files of `source_aligned_local_v4.py` (four cache files, physical frames and pairs, the sinks
  certificate) byte for byte. The builder is the upstream script wherever the upstream script decides.
- PR #194's word (the aligned word's arcs and frames, PR #194's frozen pairs and kernel pairs) run through this
  package's chain gives PR #256's certificate of that word (same sha256 of the canonical JSON) and the block
  histogram of Sussman's published certificate of #193 in every class and rank (N = 262,944). The flow, lift,
  emitter and checker used for the new words are therefore the ones whose output on PR #194's word matches, class
  by class, his independent rebuild of #193.
- The control has no external histogram of its own: no other package compiles PR #168 v4's modules with this
  recipe. It passes the same chain as the result and serves as the like-for-like baseline. On PR #168's modules the
  recipe is weaker than PR #168's inherited layer (7469 vs 7474.547 per 10⁷ with PR #193's pairs, 7522 vs 7547 with
  PR #233's: −0.07% and −0.33%), so the gain of the modules is measured against the control.

## 4. Results

| word | R | registers | frames | gates | blocks | N | five-stage W | certified a | rejected |
|---|---|---|---|---|---|---|---|---|---|
| control, parity pairs | 9,412 | 12,052 | 18,338 | 51,221 | 70,295 | 262,944 | 14,692 | 7469/10⁷ | 7470/10⁷ |
| control, mw pairs | 9,412 | 12,052 | 18,338 | 52,587 | 69,827 | 262,944 | 14,692 | 7522/10⁷ | 7523/10⁷ |
| re-annealed, parity pairs | 9,160 | 11,800 | 18,018 | 50,859 | 69,384 | 257,400 | 14,440 | 7586/10⁷ | 7587/10⁷ |
| re-annealed, mw pairs | 9,160 | 11,800 | 18,018 | 51,909 | 68,942 | 257,400 | 14,440 | 7635/10⁷ | 7636/10⁷ |

Every program has scalar denominators 2 (x, slots) and 6 (y) and cst = 440; no kernel is reused and no source
control is erased in any of the four flows. The control programs come out of the emitter with the star rule (1/3
inside, −1/6 outside), as PR #256's do, and are committed as emitted. In the two re-annealed programs a scaling by −1
in the exact lift's completion leaves the retained totals of coordinates 20 and 21 in registers 5778 and 6318 with
unit −1 (`gcert_emit.py` keeps units as in Sussman's `gxconv.py`), so the emitter writes the scatter as a table.
Step 11 re-signs those two registers (50 coefficients) and writes the star rule, the only form that the five-stage
packages' complex code reads (`complex_labels.py` and its neighbours); both forms pass `gx.check1`.

Gains of the modules on the certified grid points: +1.57% (parity pairs, 117/7469) and +1.50% (mw pairs, 113/7522;
+1.51% on the numerical roots 7.63588e-4 and 7.52265e-4); against PR #233's word in the same layout (7547/10⁷):
+1.17% (88/7547); against the circuit of #193 (7474547/10¹⁰): +2.15%. The exact moment bounds and margins are in
`certificate/expected.json`.

## 5. What is not claimed

- **No Lean build.** The programs are checked by Sussman's Python reference checker `gx.check1` and his Python
  mirror of the Lean checks `gxcore.py`, not by the Lean kernel. His repository checks the program of #193 in Lean;
  the same generators should apply to these files, but no kernel build is part of this package, and `refcheck.py`
  and `gxdry.py` were not run on them.
- **Scatter normalization.** The committed re-annealed programs are the emitted ones with two registers re-signed
  (step 11). The re-signing is checked, not trusted: both the emitted and the committed program pass `gx.check1`,
  the committed one also `gxcore.py`, and the price reads only the block histogram, which does not change.
- **The five-stage layout at R ≠ 9,412.** The ledger formula H₅ = 5·H_inv + 2v(e₄₂ + e₂₁ + e₄₆ + e₄) with
  W = 4v + R was stated for the bridged layout of the word of #193 (R = 9,412). Here it is applied to words with R =
  9,160, as the bit-side packages apply their layout at several R values: in the formula the bridge terms do not
  involve R, and R enters only through W and the invocation ledger. That the bridged layout holds verbatim at this R
  is left to the five-stage authors to confirm.
- **No new κ by itself.** On the current frontier, PR #299 (chafreaky; cited, not checked here: κ =
  7.49899215319498e-4), the bit supplier (coarse) is 7.50462e-4, 0.57% below the complex price of PR #233's word
  (7.54736e-4) and below both re-annealed prices (7586/10⁷ and 7635/10⁷). This package raises the complex cap from
  7.547e-4 to 7.635e-4 (+1.17%).
- **Discovery is numerical.** Floating-point scores chose the modules, the frames and the pairs; none of them is
  trusted: every choice is a frozen input that the chain above checks exactly.
- **Not packaged.** A centre-sharing variant, in which the pair module also supplies the star centre as a 46th root
  (about +2.7% over the same-recipe control on the numerical five-stage root, exploratory), needs a change to
  `Graph.finish` in PR #202's tree; it is left as a follow-up.

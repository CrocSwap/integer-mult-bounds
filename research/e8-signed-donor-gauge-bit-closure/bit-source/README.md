κ = 8.75481145306751e-4

# An E8 bit word: the bit supplier on the E8 label family

This package gives a conditional finite construction with **κ = 875481145306751/10¹⁸ ≈ 8.75481145306751·10⁻⁴**. That is:

- +9.29 % over PR #352 (8.01083628465007e-4);
- +8.54 % over the best p = 10 package we had verified (8.06611444687371e-4).

Until now every bit word has been a paired-cube word: transversal triples of point-pairs, with the form G = I − J/9 on
Q^h. This package replaces it with a bit word on the **E8 label family**: the 120 root lines of E8 in Q⁸. Jacob
Sussman introduced the E8 family for the complex side (#352).

| side | supplier | coarse saving |
| --- | --- | ---: |
| bit (new) | E8 bit word `bitE8-r865` (h = 8, v = 120, R = 865, m = 40, 9 centres) | c = 452036410121261/(5·10¹⁷) ≈ **9.04072820242522·10⁻⁴** |
| complex | Sussman's E8 unit `gcert1-e8-r783`, PR #352's checks unchanged | b = 876248285600677/10¹⁸ ≈ 8.76248285600677·10⁻⁴ |

The bit coarse saving is +12.0 % over the previous bit root (8.0726e-4) and 3.2 % above the complex supplier, so **the
complex side binds again**. κ is the complex-bound assembly of PR #315's `outer.assembly`: all 47 constraints hold, the
complex leaf cap itself is rejected, and the adjacent 10⁻¹⁸ grid point is rejected.

## The construction

**Labels and form.** The 120 root lines of E8 in Construction-A coordinates (from the [8,4,4] Hamming code) are:
- the 8 frame lines 2eᵢ;
- 112 codeword lines: ±1 on a weight-4 codeword, with a sign pattern taken modulo ±.

The form is ⟨x,y⟩ = x·y/2. It is positive definite, so **every frame is nondegenerate**. Data role S starts at its line
and ends at the full frame. Target t ends at its cap t^⊥, which has dimension 7.

**Decoder.** There are 9 retained totals at the full frame:
- T₀ = Σ x;
- Tᵢ = Σ over S with B(aᵢ, S) = 1 of x_S, for an F₂-basis a₁…a₈ of E8/2E8, where B is the symplectic form ⟨·,·⟩ mod 2.

y_t reads T₀ and the Tᵢ with (t̄)ᵢ = 1. This gives x_t + Σ_{S ⊥ t} x_S over F₂. The junk of t is the 63 lines of the E7
in t^⊥, all inside the cap.
- Copy loss L = 72, so the deficit is 4v − 5L = 120, as in Sussman's complex unit.
- 9 centres are necessary. With a neighbour 8-clique fixed to the standard basis, which loses no generality, CP-SAT
  proves that no rank-8 F₂ decoder exists. It finds a rank-9 decoder in 5 s (`code/bit/independent/centres_sat.py`).

**Side network.** This is the design `ham2` (`code/bit/producer/ham2.py`).
- Notation for a codeword target t:
  - t lies in block c, and c̄ is the complementary block;
  - Q is the π-coset of t: the 4 mutually orthogonal lines of c that contain t;
  - d is the partner of t in Q, and {a, b} = Q − {t, d}.
- y_t climbs C_c̄ (dim 4) → K_p (dim 5) → C_c̄ ⊕ ⟨a,b⟩ (dim 6) → t^⊥ (dim 7). Along the way it reads:
  - E(D4(c̄)): 12 lines, shared by 12 targets;
  - M(p): 8 lines;
  - N = M(p′) + x_a + x_b: shared with d;
  - two tops M+M over the cross planes ⟨a,d⟩ and ⟨b,d⟩, with the single line d folded into one of them.
- How the sums are built:
  - each M is a sum of two L's (L = 4 lines spanning an A3), and each L is a sum of two pairs;
  - frame targets read along coordinate subspaces;
  - all sums are built before the scatter;
  - dirt is compensated at frame 0, and cleanup happens at the full frame.
- A local search over pairings, fold sides, level-5 choices, frame-target choices and L splits gave R = 865, i.e. 7.2
  helpers per pair. `code/bit/producer/fullword.py params-r865.json` regenerates the shipped word byte-for-byte in
  JSON content.

The local word's five-stage histogram is {1:10380, 2:4710, 3:2240, 4:2330, 5:1540, 6:10, 7:240, 8:90, 14:240, 18:240}.
W = 4v + R = 1345, m = 5h = 40, deficit 120, and the largest child is 18 < m/2.

## Verify

    bash verify.sh /fresh/dir      # about 2.5 minutes; Python 3.11+ with numpy, mpmath, sympy; g++ (C++17) with Boost

Optional: ortools, for step 7b. The final line is:

    PASS conditional kappa = 875481145306751/1000000000000000000 = 0.000875481145306751 (complex-bound; ...)

`VERIFY-LOG.txt` is a clean run.

| step | what is checked | generalization and regression |
| --- | --- | --- |
| 0 | `MANIFEST.sha256` | — |
| 1 | The word is regenerated from the producer parameters and must equal the shipped word. The PR249 records (`MOVE/ADD/COPY/ERASE`, B/A frame bases) are exported and their hashes compared. | new exporter |
| 2 | **Independent checker** (`independent/checkword.py`, no code shared with the producer): exact rational nesting, one common frame per gate, y at frame 0 at the scatter, start and final frames (y ends at label^⊥), the **exact F₂ identity on all 2v + R = 1105 columns** with arbitrary helper dirt, Gram determinants, histogram and moment root. 6 mutants are rejected. | new |
| 3 | **PR #266 official cohort legality and five-stage formal columns** with h = 8 and **NCOPY = 9**: 14,603 common-frame ADDs, rank mass 8,672, 9 COPY/ERASE, all 1345 global columns over the five stages with bridges, prefix bill 60 bits < 104. 6 record-level mutants are rejected, including the unchanged word under the original copy count h. | `-DNCOPY` defaults to `HDIM`. Built without it, on the PR #325 p10b word, the generalized sources give a **byte-identical** legality receipt and an identical columns receipt (wall-clock aside) to the unmodified PR #346/#352 sources. |
| 4 | Exact nondegeneracy under the **E8 Gram** (positive definite; all leading minors > 0) and **PR #315's prime-witness rule** on all 944 frames. The only prime is 2, so any odd address prime works. | `--gram triple9` is PR #346's formula verbatim. It reproduces `prime_new.py` on the p10b word (12,885 frames, 97 bits, primes {2, 3, 11}). |
| 5 | **PR234 five-stage geometry** for all 120 ports, with W(E8) reflection words (≤ 2 reflections) as port isometries. Checked: routes involutive; the stage boundary chain; eight idle boundary pairs with gap ranks (14,14,7,7,18,18,4,4) = (2h−2, h−1, 2h+2, 4); the D_I D_P identity; the five-window completion for the entrance census {σ = 0: 865 helpers}; a duplicated window is rejected. | The original's coordinate permutation π is the isometry g, with g⁻¹ in place of πᵀ. On paired-cube labels at h = 20 the generalized routes equal the original literal ρ. |
| 6 | **Banks**: residual census {8: 865} tiles exactly into 173 width-40 banks of five blocks (1 replica). | `tile_g.py` with h, replicas as arguments. Its output is byte-identical to `tile_check.py` on p10b. |
| 7 | **Retained totals**: 9 > h = 8, admitted explicitly; see below. | — |
| 8 | Complex supplier: PR #352's `certify_complex.py`, unchanged. This covers gx.check1, gxcore, labels, scalar words, splice, precision guard, Lean regeneration of `wht_main_block_B2Ge8x`, Sussman's stand-alone replay, and the exact b. | vendored |
| 9 | **Bit coarse saving and outer assembly**: PR #315's two moment engines, the 10⁻¹⁶ fallback, the adjacent grid point excluded, and the 47 constraints. | `certify_bit_g.py` takes h and T as arguments. With h = 20, T = 12 it gives receipt fields identical to the original `certify_bit.py` on p10b. |
| 10 | **Finite bill at m = 40**. Values are read from this run's receipts: unit additions 14,603, rows 742 and 6,308, stock 1345, K = 27,347,440. Results: coefficient 1,916,288,151,501 (41 bits) < 2⁸⁰; q-power bound q¹⁶⁰¹ (row constant d + 1 = 1601); payload 60 bits < 104; δ_τ > 0; ordinary bootstrap chain. All 120 port routes are exact elementary programs with power-of-two denominators. | The original finite bill line for line, with NCOPY in place of h for copies and temporaries, and the route template generalized to the port isometry. On agent G's p = 10 loans receipts it reproduces the coefficient 24,463,942,022,302,301, the moment gaps, the chain and the route program hash. |
| 11 | Secondary: the PR #363 numbers (next section). | `bridged.py` vendored from #363 |

## Retained totals: 9 at h = 8 (admitted)

The paired-cube layouts have h centres, and both PR #266 checkers pinned the copy count to h. #352 likewise bounds
retained totals by the h reserved centre slots. The E8 bit word needs 9 (step 7b). In this package:
- copies are sequential complete temporary streams, one COPY window at a time, and the legality checker enforces that
  lifecycle;
- the finite bill charges NCOPY = 9 copied-centre temporaries and 5·9 copy/erase episodes per replica;
- the deficit 4v − 5L uses the actual L = 72.

What the count changes is physical stock by one temporary slot, not the price. That is the admission: "≤ h" is a
layout pin of the paired-cube words, not a requirement of the construction.

## PR #363 (seven-stage) — secondary, conditional

PR #363 (DaysSky) prices Sussman's unit in a seven-stage bridged word B₃ at b₃ = 932783231884153/10¹⁸. Its conditions
are m = 63 ≤ 72, max child 31 < 31.5, and rows 12,064 < 20,161. #363 notes it has no Lean proof of B₃, and its exchange
identity is checked at the abstraction of the `Net.lean` header. `outer.assembly` reads only (a, b) and the generic
bridge, so b₃ is usable on the same terms as #352's b, conditional on #363's own obligations. Step 11 gives:

| bit layout | complex | κ |
| --- | --- | --- |
| five-stage (this package) | #352 five-stage b | **8.75481145306751e-4** (complex-bound; the claim of this package) |
| five-stage (this package) | #363 seven-stage b₃ | 9.032562102114e-4 (bit-bound) |
| seven-stage B₃ (estimate: no bit construction yet) | #363 b₃ | 9.319139565121e-4 (complex-bound) |

The B₃ row prices this word's local histogram with #363's idle climbs at h = 8 (m = 56, W = 1585, deficit 216). That
gives c = 9.68198e-4. B₄ gives 9.57e-4. Using it would need a seven-stage analogue of PR234's bit construction (banks,
bridges, source owners), which does not exist.

## Open obligations

- **Inherited from the bit supplier, unchanged:**
  - the all-size weighted compiler and common ancestor chart;
  - restored rows (the external row coefficient 20161 is as in #315/#352; the additive row constants 9909 + 252 are
    inherited);
  - tape routing, prime supply, precision/recovery and the analytic transfer.
- **New, written here but not formally proved:**
  - that PR234's five-stage bank construction carries over to a positive-definite non-paired-cube label family with
    rational, non-permutation port isometries. Step 5 checks every port's matrices exactly; the source527 lowering
    program itself is not re-run;
  - that 9 retained totals at h = 8 are admissible, as argued in the section on retained totals above.
- **Not run on this word:** the source527 scalar program's signed integer decoder (the word is F₂ throughout; the
  checks over F₂ are exact).
- **Complex side:** #352's obligations, unchanged.
- This is a conditional finite construction, not a formal verification of the multiplication theorem.

## Credits

- **E8 label family and the complex unit**: Jacob Sussman (wht-power-saving-lean, `gcert1-e8-r783`, the Lean theorem
  `wht_main_block_B2Ge8x`, gx/gxcore, generators and replay).
- **Complex checks, generalized to any retained-total count**: DaysSky (#352), on the #346/#315/#256/#233/#202/#200/#194/#184
  lineage.
- **Seven-stage bridged layout and `bridged.py`**: DaysSky (#363), used only in the secondary step.
- **Bit-side checkers and engines generalized here**:
  - PR #266's official cohort checkers;
  - LJH-217's #346 ports;
  - PR #315's moment engines, outer assembly and finite bill (DreamingOfClouds);
  - the source527 lineage (eumemic; PR #200 Chafik Boukhalfa's physical rules);
  - PR234's five-stage architecture (hcg890 / Henry Grant, on Jacob Sussman's five-stage layout);
  - Evan McKinney's completed banks.
- **The E8 bit word, its producer, the independent checker, and the generalizations and regressions**: Dylan Crow, with
  Anthropic Claude assistance.

See `NOTICE.md`, `NOTICE-PR352.md`, `NOTICE-PR363.md`, `PR-STATEMENT.md` and `HANDOFF.md`.

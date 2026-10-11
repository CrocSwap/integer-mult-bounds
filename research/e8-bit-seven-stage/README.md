κ = 9.3191395651209e-4

# The E8 bit word and the E8 complex unit in the seven-stage bridged word

This package gives a conditional finite construction with **κ = 93191395651209/10¹⁷ ≈ 9.3191395651209·10⁻⁴**:

- +6.45 % over PR #370 (8.75481145306751e-4), whose E8 bit word it uses;
- +3.17 % over that bit word in five stages with PR #363's seven-stage complex unit (9.03256e-4, the number PR #370
  reports but does not claim).

Both suppliers run in the **seven-stage bridged word B₃**. That is PR #363's generalization of Jacob Sussman's
bridged five-stage word B₂ from two bank pairs to three:

| side | supplier | layout | coarse saving |
| --- | --- | --- | ---: |
| bit | PR #370's E8 bit word `bitE8-r865` (h = 8, v = 120, R = 865, 9 centres), unchanged | B₃: m = 56, W = 1,585, D = 216 | c = 968197503705007/10¹⁸ ≈ **9.68197503705007·10⁻⁴** |
| complex | Sussman's E8 unit `gcert1-e8-r783`, unchanged (PR #363) | B₃: m = 63, W = 1,503, D = 216 | b = 932783231884153/10¹⁸ ≈ 9.32783231884153·10⁻⁴ |

The bit coarse saving is +7.09 % over the same word in five stages (9.04073e-4) and 3.8 % above the complex supplier, so
**the complex side binds**. κ is the complex-bound assembly of PR #315's `outer.assembly`: all 47 constraints hold,
the complex leaf cap itself is rejected, and the adjacent 10⁻¹⁸ grid point is rejected.

## The layout

PR #370's bit word uses the five-stage bridged word: two bank pairs per class, five invocations, three layers of twin
bridges, then the terminal exchange. In B_K (PR #363, `code/complex/code/bridged.py`) pair p borrows its first forward
invocation from pair p − 1 in the same way:

    stage 0, 1, 2      pair 1: forward, backward, forward
    stage 2p-1, 2p     pair p: backward, forward                      (p = 2..K)
    after stage 2p-3   X(p-1) += Xp,  Yp -= Y(p-1)
    after stage 2p-2   Yp += Y(p-1),  X(p-1) -= Xp
    at the end         Y(p-1) -= Yp,  Xp += X(p-1)                    (p = K..2)

So K pairs are exchanged by 2K + 1 invocations on H ⊕ 2K·H, with m = (2K+1)h, W = 2Kv + R and D = 2Kv − (2K+1)·L for copy
loss L per invocation. With L = 72, both E8 units have D = 120 in five stages and D = 216 in seven. One invocation of
the bit word is unchanged. Only the word around it changes:

- **Idle climbs of the bit word in B₃** (h = 8): pair 1 [34], pair 2 [14, 7, 20], pair 3 [28, 7, 6]. The two climbs
  above m/2 are split at explicit intermediate frames, 34 → 27 + 7 and 28 → 27 + 1. The largest paid child is then
  27, and 2 · 27 < 56 satisfies the half-shrink guard.
- **Banks.** Every helper starts at frame 0, so all 865 residuals have width 8. Width-56 banks hold 7 of them, and 7 ∤ 865,
  so the bank tiling uses **T = 7 literal replicas**: 865 exact width-56 banks. The moment arithmetic is invariant
  under this normalization.

## What is checked (`bash research/e8-bit-seven-stage/verify.sh <fresh dir>`, about 4 min)

Every step of PR #370's verification runs, and so does the B₃ version of each stage-dependent step. Each new checker is a
K-parameterized copy of a PR #370 checker. At K = 2 it reproduces that checker's receipt, and `verify.sh` compares the
two.

0. **Manifest and provenance.** 142 files have the git blob ids of PR #370 at `b7fe9cd`, and 6 those of PR #363 at
   `9df55da` (`SOURCE-pr370.json`, `SOURCE-pr363.json`).
1. **The word** (PR #370) is regenerated from its producer parameters, and the PR249 records are exported.
2. **One invocation** (PR #370): the independent all-column checker and its 6 word-level controls.
3. **Legality and formal columns.** Legality of one invocation uses PR #266's checker (NCOPY = 9).
   `columns_k.cpp -DKPAIRS=3` is PR #370's all-column F₂ check of the whole bridged word, extended to seven stages:
   - all 1,585 physical columns, dirty helpers included, through 7 invocations, 12 twin bridges and the terminal
     exchange;
   - all 12 omitted-bridge controls rejected;
   - PR #370's 6 record-level controls rejected.

   At K = 2 the receipt equals `columns_h`'s. On the PR #325 p10b word it equals PR #346's unmodified checker.
4. **Exact nondegeneracy** under the E8 Gram, and prime witnesses, on every frame (PR #370; the only prime is 2).
5. **PR234's route and idle geometry**, on all 120 ports, with W(E8) reflection words as port isometries.
   `geometry_k.py 3` uses 7 blocks:
   - routes involutive, 6 stage boundaries chained;
   - every idle climb a commuting nested pair whose gap rank equals `bridged.py`'s;
   - the two splits at dyadic intermediate frames Q = b − D, where D is a sum of orthogonal E8 root projectors, so
     the prime set stays {2};
   - the 7-window entrance completion exact, and a duplicated window rejected.

   At K = 2 it gives PR #370's idle ranks (14, 14, 7, 7, 18, 18, 4, 4).
6. **Banks.** `tile_k.py`: an exact zero-padding width-56 tiling with 7 replicas. At K = 2 it is byte-identical to
   `tile_g.py`.
7. **Copied centres.** 9 retained totals at the full frame. This is PR #370's admission, and it is charged as NCOPY = 9
   per invocation everywhere.
8. **Complex supplier** (PR #363, `certify_b3.py`):
   - the B₂ regression reproduces PR #352's pins and b;
   - at B₃, PR #352's portable checks at m = 63: rows 12,064 < 20,161, induction gap 63·B, max child 31;
   - Sussman's Lean data regenerated byte for byte, and his replay accepts;
   - b₃ = 932783231884153/10¹⁸.
9. **Bit coarse saving and outer assembly.** `certify_bit_k.py 3 8 7` takes the one-level histogram
   7 × (one invocation) + 240 × (B₃ idle blocks), with W = 7 · 1,585, m = 56 and deficit 7 · 216. It uses PR #315's
   two engines with the 10⁻¹⁶ fallback, and rejects the adjacent grid point. The outer assembly gives 47 positive
   constraints and κ.

   At K = 2, T = 1 the receipt fields equal PR #370's (κ = 8.75481145306751e-4).
10. **Finite bill at m = 56** (`finite_k.py`). The original formulas with the stage counts of B₃:
    - 7 invocations' additions plus 12v bridge additions;
    - route families 2·7·(2v + R) + 6v;
    - 7·NCOPY·T copy/erase episodes;
    - the selector bill 2·7·T·(…).

    The coefficient is 57,685,376,070,645 (46 bits) < 2⁸⁰, with q-power bound q³¹³⁷. All 120 port routes are exact
    elementary programs with denominators {1, 2, 4}. At K = 2 the bill is byte-identical to PR #370's, and the p = 10
    regression reproduces the original coefficient.

## Open obligations

- **No Lean proof of the bridged word B₃**, on either side. Sussman's `bridge2_certificate` covers B₂. Here B₃ rests on:
  - the all-column F₂ check of the whole seven-stage bit word (step 3);
  - PR234's exact rational geometry on 7 blocks (step 5);
  - PR #363's coordinate-frame check and exchange identity for the complex side.
- **Everything PR #370 admits**, unchanged:
  - the 9 retained totals at h = 8, a layout pin of the paired-cube words;
  - PR234's bank construction for a non-paired-cube family, checked on the exact matrices and not re-proved;
  - the inherited bit-supplier interfaces.
- **Everything PR #363 / #352 / #346 / #315 admit on the complex side:**
  - the complex symbolic correctness;
  - the precision/recovery and row interfaces, including the additive row constants;
  - the analytic transfer.
- The finite bill takes PR #370's formulas with the counts of seven stages (above). Its proof text is PR #370's and the
  source527/p10 lineage's, not re-derived here.
- This is a conditional finite construction, not a formal verification of the multiplication theorem.

## Credits

- **Dylan Crow (utcorvusvolat-dotcom), PR #370:** the E8 bit word, its producer, its independent checker, and the
  generalized bit-side checkers this package extends.
- **Jacob Sussman:** the E8 family and the E8 complex unit; the bridged five-stage word and its geometry, which B₃
  generalizes.
- **PR #363 (DaysSky):** B_K and the seven-stage complex unit.
- **PR #352 / #346 / #315 / #266 / source527 / PR234 lineage:** see `NOTICE.md` and `NOTICE-PR352.md`.

Prepared by DaysSky, assisted with Claude.

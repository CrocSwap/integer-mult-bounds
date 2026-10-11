κ = 9.95656966441037e-4

# The E8 bit word in the nine-stage bridged word, with PR #377's nine-stage E8 complex component

This package gives a conditional finite construction with **κ = 995656966441037/10¹⁸ ≈ 9.95656966441037·10⁻⁴**, which
is above 2⁻¹⁰ = 9.765625·10⁻⁴:

- +2.94 % over #380 (9.67261003170394e-4), which pairs PR #377's complex component with the seven-stage bit word;
- +4.34 % over #375 (9.5424356568133e-4).

| side | supplier | layout | coarse saving |
| --- | --- | --- | ---: |
| bit | PR #370's E8 bit word `bitE8-r865` (h = 8, v = 120, R = 865, 9 centres), unchanged | **B₄**: nine stages, m = 72, idle climbs unsplit (max child 50, halving degree 2) | c = 249162322049641/(25·10¹⁶) ≈ **9.96649288198564·10⁻⁴** |
| complex | PR #377's compressed nine-stage E8 component (Sussman's unit), vendored unchanged | m = 73, banks, halving degree 2 | b = 999240641319551/10¹⁸ ≈ 9.99240641319551·10⁻⁴ |

The bit side binds. κ is the bit-bound assembly of PR #315's `outer.assembly`: all 47 constraints hold, and the
adjacent 10⁻¹⁸ grid point is rejected.

## The bit side: B₄, unsplit

PR #373 put the bit word in the bridged word B_K of PR #363 with K = 3. Its K-parameterized checkers run here at K = 4:
four bank pairs per class and nine invocations, with m = 9·8 = 72 and W = 8v + R = 1,825. The deficit is
8v − 9·72 = 312 per unit.

As in PR #375 for the complex side, the idle climbs are **not split** below m/2. The B₄ idle climbs of the bit word
are:

    [50] | [14, 7, 36] | [28, 7, 22] | [42, 7, 8]

The largest child is 50 of 72, and 72² = 5184 > 2·50² = 5000, so the halving degree is two. Split below m/2, B₄
would price at 9.5702·10⁻⁴. Unsplit B₃ gives 9.9123·10⁻⁴.

**Banks.** 9 stages × 865 helper residuals of width 8 tile width-72 banks with 9 residuals each. Since 865 ≡ 1 (mod
9), this takes **T = 9 literal replicas**, and gives 865 exact banks.

## What is checked (`bash research/e8-nine-stage-kappa/verify.sh <fresh dir>`)

Steps 1–2 and 4 are PR #370's. Steps 3, 5, 6, 9 and 10 run PR #373's K-parameterized checkers at K = 4. Each of
those also runs at K = 2 and is compared with PR #370's receipt.

0. **Manifest and provenance** (`SOURCE-pr*.json`, git blob ids): files from PR #370, #363, #373, #375 and #377.
1. **The word** is regenerated from its producer parameters, and the PR249 records are exported.
2. **One invocation**: the independent all-column checker and its 6 controls.
3. **Legality and formal columns.** `columns_k.cpp -DKPAIRS=4` runs the all-column F₂ check of the whole bridged word:
   - all 1,825 physical columns, dirty helpers included, through 9 invocations, 18 twin bridges and the terminal
     exchange;
   - all 18 omitted-bridge controls rejected;
   - PR #370's 6 record-level controls rejected.
4. **Nondegeneracy.** Exact E8-Gram nondegeneracy and prime witnesses, with prime set {2}.
5. **PR234 route and idle geometry** (`geometry_k.py 4 … unsplit`), on all 120 ports with W(E8) reflection words:
   - 9 blocks, routes involutive, 8 stage boundaries chained;
   - every idle climb a commuting nested pair whose gap rank equals `bridged.py`'s;
   - the 9-window entrance completion exact;
   - largest child 50, halving degree 2.
6. **Banks** (`tile_k.py`): an exact width-72 tiling with 9 replicas.
7. **Copied centres.** 9 retained totals at the full frame (PR #370's admission), charged as NCOPY = 9 per invocation.
8. **Complex component.** PR #377's own `verify.py` runs unchanged on its vendored, manifest-pinned package. It checks
   the Clifford frames, transitions and adapters, the data and cover phases, the global template and two moment engines.
   It gives b = 999240641319551/10¹⁸.
9. **Bit coarse saving and outer assembly** (`certify_bit_k.py 4 8 9 … unsplit`):
   - the one-level histogram is 9 × (one invocation) + 240 × (B₄ idle blocks, unsplit);
   - W = 9 · 1,825, m = 72;
   - two engines with the 10⁻¹⁶ fallback, and the adjacent grid point rejected;
   - the outer assembly with PR #377's b: 47 positive constraints and κ.
10. **Finite bill at m = 72** (`finite_k.py`):
    - 9 invocations' additions plus 18v bridge additions;
    - route families 2·9·(2v + R) + 8v;
    - 9·NCOPY·T copy/erase episodes, and the selector bill 2·9·T·(…);
    - halving degree 2, so the internal row coefficient is 2·(72² + 1) = 10,370;
    - coefficient 2⁴⁸ < 2⁸⁰, q-power bound q⁵¹⁸⁵.

    At K = 2 the bill is byte-identical to PR #370's.

## Halving degree two on the bit side

The bit finite bill (`finite_k.py`) now computes the least halving degree t with mᵗ > 2·(max child)ᵗ. At t = 1 it is
the original bill; otherwise it charges the internal borrowed-row reserve t·(d + 1).

This is PR234's treatment: "The proper child ratio 5/6 requires halving degree four. The one-level weighted recurrence
is retained; its histogram is not multiplied by four"
(`research/five-stage-source527-banks/UPSTREAM-PR234-PROOF.md`). PR #375 and PR #377 use degree two on the complex
side. The external complex row coefficient 20,161 of the outer assembly is unchanged.

## Open obligations

- **No Lean proof of the bridged word B₄** on the bit side. Here B₄ rests on:
  - the all-column F₂ check of the whole nine-stage word (step 3);
  - PR234's exact rational geometry on 9 blocks (step 5).
- **Halving degree two on the bit side.** The inherited bit finite bill states degree one. Here its internal row term
  is charged at degree two, as in PR234's degree-four precedent.
- **Everything PR #370 admits:**
  - 9 retained totals at h = 8;
  - PR234's banks for a non-paired-cube family;
  - the inherited bit-supplier interfaces.
- **Everything PR #377 admits for the complex component:** the local E8 theorem, the Clifford/compiler, common-grid,
  row and analytic interfaces.
- **The finite bill** takes PR #370's formulas with the stage counts of B₄ (PR #373's generalization).
- This is a conditional finite construction, not a formal verification of the multiplication theorem.

## Credits

- **Dylan Crow (utcorvusvolat-dotcom), PR #370:** the E8 bit word, its producer and independent checker, and the
  generalized bit-side checkers.
- **Zhihao Chen (jacklightChen), PR #377:** the compressed nine-stage E8 complex component, vendored unchanged with its
  verifier.
- **Jacob Sussman:** the E8 family and the E8 complex unit, and the bridged five-stage word.
- **PR #363 / #373 / #375 (DaysSky):** B_K, the K-parameterized bit-side checkers, and halving degree two.
- **PR #380 (rohanarun):** first paired PR #377's component with an E8 bit word.
- **PR #352 / #346 / #315 / #266 / source527 / PR234 lineage:** see `NOTICE.md` and `NOTICE-PR352.md`.

Prepared by DaysSky, assisted with Claude.

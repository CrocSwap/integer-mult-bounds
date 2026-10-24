κ = 1128983115440183/10¹⁸ (conditional; bit-bound) with PR #433's complex supplier

# An E8 bit word with 740 helpers: dead helper slots reused through F₂ relations

This package is a bit-side supplier: an E8 bit word in PR #370's format (h = 8, v = 120, 9 retained totals) with **R = 740 helpers**. For comparison, #370 has 865, #376 has 822, #426 has 767 and #433 has 758. In the compressed nine-stage layout of PR #386 (m = 64), which #425, #431 and #433 use, its coarse saving is

**c = 282564789736676592463/(2.5·10²³) ≈ 1.130259158946706·10⁻³**

on PR #433's 10⁻²⁴ grid. On #386's 10⁻¹⁸ grid it is 565129579473353/(5·10¹⁷).

PR #433 (icekylinx) pairs its split-centre complex supplier, b = 1183986549206329/10¹⁸ ≈ 1.183987·10⁻³, with a 758-helper bit word, c = 1.122122700265139·10⁻³. #433's bit side binds, at κ = 1.120864952258278·10⁻³. With this word in place of R758, through #433's own bit engine, finite invoice and six-level tail:

**κ = 1128983115440183/10¹⁸ ≈ 1.128983115440183·10⁻³**, bit-bound, **+0.7243 % over #433**.

The bit c is +0.7251 % over #433's R758. As controls, the same code reproduces #433's bit c from #433's stated R758 profile, and #433's κ from #433's (c, b), exactly. The complex side still has 4.75 % of headroom over this c.

## Bit coarse savings

| bit word | R | compressed nine-stage (#386 layout, m = 64) | B₄ unsplit (#381 layout, m = 72) | B₃ unsplit (m = 56) |
| --- | ---: | ---: | ---: | ---: |
| PR #370 (`bitE8-r865`) | 865 | **1057833103534317/10¹⁸** (= #386, #425, #431) | **249162322049641/(2.5·10¹⁷)** (= #381) | 9.912261·10⁻⁴ |
| PR #376 (R822) | 822 | 1084538480613107/10¹⁸ | **255384852701747/(2.5·10¹⁷)** (= #390 … #424) | **8128527708459/(8·10¹⁵)** (= #376, #389 baseline) |
| PR #417 (R822 + shared-donor kernel) | 822 | — (entrance residuals do not fill #386's rank-8 slots) | **1044063934627389/10¹⁸** (= #417) | 1.037508·10⁻³ |
| PR #426 (R767, clean-reset reuse) | 767 | 1116714040089377/10¹⁸ | 1.051689·10⁻³ | **104575879789097/10¹⁷** (= #426) |
| PR #433 (R758: #426 + source-basis totals) | 758 | **561061350132569610283/(5·10²³)** (= #433, 10⁻²⁴ grid) | — | — |
| **this word** | **740** | **282564789736676592463/(2.5·10²³) ≈ 1.130259·10⁻³** | **1064525457834209/10¹⁸ ≈ 1.064525·10⁻³** | **1058066102700151/10¹⁸ ≈ 1.058066·10⁻³** |

Compressed nine-stage values are on #386's 10⁻¹⁸ grid, except #433's and this word's, which are on #433's 10⁻²⁴ grid. On the 10⁻¹⁸ grid this word is 565129579473353/(5·10¹⁷).

Bold entries in the control rows are the values the cited PRs publish. `verify.sh` reproduces each exactly with the same code that prices this word. Most come from the PR's own word. #433's R758 value comes from the R758 profile stated in #433, because the package does not ship that word. The other entries are computed here and are not published by those PRs.

This word compared with the best published bit c in each layout:

| layout | best published bit c | this word |
| --- | --- | ---: |
| compressed nine-stage | #433's R758 | +0.725 % |
| B₄ | #417 | +1.960 % |
| B₃ | #426 | +1.177 % |

Against #426's R767 word priced in the same layouts, this word is +1.213 % (compressed nine-stage) and +1.221 % (B₄). The five-stage saving (PR #370's independent checker) is 9.63227·10⁻⁴.

## κ with cited complex suppliers

| complex supplier (cited, not rebuilt) | layout and tail | b | κ with this word | κ as published |
| --- | --- | ---: | ---: | ---: |
| **PR #433 (icekylinx)** | compressed nine-stage; #433's tail | 1183986549206329/10¹⁸ | **1128983115440183/10¹⁸** (bit-bound) | 560432476129139/(5·10¹⁷) (bit-bound, R758) |
| PR #431 (rohanarun, draft) | compressed nine-stage; #386's tail | 529046848168159/(5·10¹⁷) | 1056975315151441/10¹⁸ (complex-bound) | 1056715272872389/10¹⁸ at db4f465 (bit-bound, #370 word); 1056975315151441/10¹⁸ at 71c5988 (with #376's retimed bit word) |
| PR #425 (jacklightChen) | compressed nine-stage; #386's tail | 52455248902029/(5·10¹⁶) | 524002754014103/(5·10¹⁷) | same |
| PR #386 (#377's component) | compressed nine-stage; #386's tail | 999240641319551/10¹⁸ | 998243154231047/10¹⁸ | same |
| PR #424 (chafreaky) | B₄; #392's refined tail | 254887067002137341481/(2.5·10²³) | 1018509848057013/10¹⁸ | same |
| PR #410, #409, #407 | B₄; #392's refined tail | as cited by #417 | as published | same |

All κ values are on the 10⁻¹⁸ grid and satisfy PR #315's 47 strict outer inequalities. The next grid point is rejected. The three tails:

- **#433's tail** (`compose433.py`, ported from #433's `bit_price.py` and `combined.py`):
  - c is the 10⁻²⁴-grid lower endpoint of PR #315's `certify`, with the 10⁻¹⁶ bad-branch allowance, and is checked by the second engine;
  - η = β = 10⁻¹⁸, seed min(c, (1 − β)b) − 10⁻²⁴, six bootstrap levels;
  - zero η, zero β and unit β are rejected as well;
  - the finite invoice charges the prefix at the next multiple of 64 bits: here 123 bits, charged 128.
- **#386's tail** (#386, #425, #431): three bootstrap steps, η = 10⁻¹², β = 10⁻⁹. The seed is strictly below (1 − β) times both suppliers (#431's policy).
- **B₄:** #392's refined tail, as reimplemented in PR #417's `bootstrap.refine`.

With #431's complex supplier the complex side binds. Every bit word above #431's b gives that κ, including #376's and #426's words in this layout. #431's later head uses #376's retimed word. The PR #370 word reproduces #431's κ at db4f465, and #425's and #386's κ, exactly.

## The word

1. **PR #370's producer, unchanged, with new parameters.** `data/params/params-r740.json` differs from #370's `params-r865.json` in 67 of 520 entries. It was found by a local search with the reuse pass in the objective (`discovery/`). The producer gives a word with R = 863.
2. **Elimination reuse** (`code/reuse/reuse.py`).
   - A helper is dead after its last gate in phases A and B. It still holds a leftover x-content: an F₂ sum of source lines, at its last frame.
   - Before a later helper is born at frame F, the pass looks for an F₂ relation content(r₀) = Σ_{q∈S} content(q) among dead slots whose frames lie inside F. It emits r₀ += S at the join G of their frames (G ⊆ F). r₀ then holds no x-content and hosts the new helper.
   - The relation is found by Gaussian elimination over F₂. The cheapest relation with |S| ≤ 3 replaces it when one exists, scored by the extra climbing of r₀ and of the eliminators.
   - The 9 retained totals take dead slots too. The slot's leftover x-lines are read from the sources at the full frame.
   - The dirt compensation D and the cleanup C are rebuilt as in #370's `fullword.py`.
   - **114 helper slots and 9 totals are reused: R 863 → 740.**
   - **Prior and concurrent work.**
     - #376 reused helper lifetimes by aliasing: 43 reuses.
     - #426 (ai-nanachi, posted first) uses the same mechanism as this pass. It zeroes a retired helper's x-content with exact two- or three-parent "clean resets" before reusing the slot, rebuilds D and C, and keeps the totals protected. It makes 55 resets on #376's R822 word (R767).
     - This pass was developed independently. It differs in four ways: it searches every dead slot inside the birth frame by elimination, uses cost-scored relations with up to three eliminators, puts the totals on dead slots as well, and starts from a re-parameterised #370 producer word (R863).
   - **#433's source-basis trick does not apply here.** The trick computes the nine retained sums in source rows, which removes #426's nine dedicated total helpers (R767 → 758). In this word the totals already sit on slots of earlier helpers, and no helper is born after them, so the trick would remove no register.
3. **Retiming** (`code/reuse/retime.py`, the idea of #389). Each gate moves to its lowest or highest legal frame when that lowers Σ r ln(64/r) over its registers' adjacent steps: 37 gate moves.

All search choices use integer costs computed with Python's correctly rounded `decimal` logarithm, so the word is the same on every platform. One invocation's local histogram is {1: 2355, 2: 884, 3: 489, 4: 425, 5: 62, 8: 9}: 4,224 blocks, of which 9 are copies. Gates D/A/B/C: 120/1873/472/1873; 944 frames.

## Verify

    BOOST_INCLUDE=/usr/include bash research/e8-bit-elimination-reuse/verify.sh /fresh/output/dir
    bash research/e8-bit-elimination-reuse/verify.sh --quick /fresh/output/dir

Requirements: Python 3.11+ with numpy, mpmath and sympy (`requirements.txt`); a C++17 compiler (`CXX`); Boost headers (`BOOST_INCLUDE`). `--quick` skips the regressions on #370's word, the comparison words in the compressed nine-stage layout, and the B₃ rows. The workflow `.github/workflows/e8-bit-elimination-reuse.yml` runs both modes on Python 3.12 and 3.14.

0. **Manifest and provenance.** `MANIFEST.sha256`. The git blob id of all 52 vendored files is checked against `SOURCE-pr*.json`: #370, #376, #381, #386, #417, #425, #426, #431 and #433.
1. **The word from pinned inputs.**
   - Control: #370's producer regenerates #370's word from its own parameters.
   - `regen.py` rebuilds this word from our parameters (producer → reuse → retiming). It must equal the shipped word, and the reuse ledger must match.
   - #376's R822 word is rebuilt from #370's word and #376's two witnesses with #417's `apply376.py`, as a control word.
2. **One invocation, exact.**
   - #370's independent checker: the 120 E8 root lines; nested frames; common gate frames; F₂ on all 980 columns, dirty helpers included; Gram determinants on 935 used frames (prime 2 only); the five-stage root.
   - #370's 6 word-level controls, rejected.
   - 6 elimination-reuse controls, rejected by the same checker: drop an elimination gate, drop one eliminator, drop one x-line read of a total's undo, lower an elimination below an eliminator's frame, remove all 123 elimination gates, move a total's undo gate to frame 0.
3. **Official checkers.**
   - PR #266's cohort legality, as generalised in #370 (NCOPY = 9): 19,527 records, 15,294 common-frame ADDs.
   - Five-stage formal columns: 1,220 columns, prefix payload 64 bits < 104.
   - #381's B₄ formal columns: all 1,700 physical columns over F₂ through 9 invocations, 18 twin bridges and the terminal exchange. All 18 omitted-bridge controls are rejected.
   - #370's 6 record-level controls are rejected, including the unmodified copy count NCOPY = 8.
4. **Nondegeneracy.** `gram_frames.py`: all 944 frames positive definite under the E8 form. Prime witnesses are valid; the only prime is 2.
5. **Retained totals.** 9 COPY/ERASE episodes at the full frame (rank 8).
6. **Compressed nine-stage layout (#386).**
   - #386's `geometry.py`, unchanged: 120 port routes, 1,080 route checks, at most 77 route factors with denominators {1, 2, 4}, and the bank slots. It is bound to this word by the equality of the 120 label vectors.
   - `global_word_g.py`, our generalisation of #386's `global_word.py`:
     - both reflected local streams replay all 980 columns;
     - the scalar replay over 9 stages covers 7,620 independent columns;
     - 72 local invocations, 1,405,944 emitted events and 53,280 bank assignments (6,660 banks of 8 whole rank-8 slots, no padding);
     - live stock 64v + 9R = 14,340;
     - deficit 2,496 = 8(8v − 9·72);
     - max child 42 of 64, so two-level halving;
     - prefix bound 2¹⁸·776⁵·17,724⁴ of 123 bits, under #386's 192-bit allowance.
   - `audit_g.py`: 944 exact rational projectors and 3,263 nested pairs. #386's 8 template mutations are rejected.
   - `cited.py`: each cited complex b, and that PR's own κ, must equal the fields of the PR's receipt. The receipts are #386's `COMBINED.json`, #425's `FINAL.json` and #431's `VALIDATION-LOCAL.json`, vendored and pinned by blob id.
   - `certify_g.py`: both PR #315 engines with the 10⁻¹⁶ fallback admit c and reject c + 10⁻¹⁸. The finite coefficient has 123 bits; the two-level coefficient has 282 bits, below 2⁵¹²; the row coefficient is 18,355 < 20,161. κ is then computed with each cited complex b.
   - `compose433.py`: PR #433's bit engine, finite invoice and six-level tail, ported from #433's `bit_price.py` and `combined.py`.
     - Controls: #433's stated R758 profile prices to #433's bit c, and #433's (c, b) gives #433's κ. Both are bound to #433's `CERTIFICATE.json`, which is vendored and pinned.
     - Then this word's c, invoice and κ with #433's complex b: next grid point, zero η, zero β and unit β are rejected.
   - **Regression:** on #370's word the same three scripts reproduce #386's `GLOBAL.json`, `AUDIT.json` and the bit, finite and κ fields of `COMBINED.json`, field for field. They also reproduce #425's and #431's κ.
   - **Comparison:** the same chain prices #376's word (rebuilt in step 1) and #426's word in this layout. Each gives the same κ with #431, since each has c > b.
7. **B₄ (#381's layout, unsplit).**
   - #381's `geometry_k.py` on this word: PR234 routes on 9 blocks, idle gap ranks equal to `bridged.py`, the 9-window entrance completion, max child 50 (halving degree 2).
   - `tile_k.py`: 740 banks of 9 rank-8 residuals with T = 9 replicas.
   - `certify_bit_k.py` prices this word and the #370, #376 and #417 controls.
   - `receipts_k.py` and `finite_k.py`: the finite bill at m = 72. The coefficient has 48 bits, below 2⁸⁰; the payload prefix is 64 bits; the internal row coefficient is 10,370.
   - `kappa_b4.py` computes κ with the cited B₄ suppliers.
   - **Regression:** `columns_k` at K = 2 gives the five-stage `columns_h` receipt.
8. **B₃ (informational).** Formal columns at K = 3 (1,460 columns), banks with T = 7, and prices with the #376 and #426 controls.
9. **Summary** against `EXPECTED.json`.

Locally, the C++ checkers were built against a 128-bit, overflow-checked stand-in for `boost::multiprecision::cpp_int`, because the preparing machine has no Boost. CI compiles them against libboost-dev.

## Retained assumptions and open obligations

- **Everything PR #370 admits:**
  - 9 retained totals at h = 8;
  - PR234's banks for a non-paired-cube family;
  - the inherited all-size weighted bit compiler, prime/tape/precision and analytic interfaces.
- **The compressed nine-stage layout is PR #386's:**
  - its window, bank and route arguments (PROOF.txt there);
  - two-level halving (max child 42 of 64);
  - its finite charges.
  Our scripts check this word against those arguments' finite conditions; they add no new argument.
- **B₄ is PR #381's:** halving degree two on the bit side (#375, #381); no Lean proof of B_K.
- **The complex suppliers are cited by pinned reference and not rebuilt:**
  - the headline κ depends on #433's split-centre complex supplier (its PROOF.md), which builds on #425's written scalar-interface extension;
  - #433's complex b, its six-level tail (#392's refined form, η = β = 10⁻¹⁸) and all its obligations remain #433's.
  - #431 (a draft) and the other cited suppliers are listed only for comparison.
- **#433's bit finite charge is adopted for the headline:** the prefix is charged at the next multiple of 64 bits (here 123 bits, charged 128, inside #386's 192-bit allowance), and the two-level coefficient is below 2⁵¹² (here 282 bits).
- This is a conditional finite construction, not a formal verification of the multiplication theorem. No Lean proof is claimed.
- **Not measured:** stacking #417's shared-donor kernel on this word. It applies to B_K banks. It does not apply to #386's whole-block banks, whose slots need rank-8 residuals.

## Credits

- **Dylan Crow (utcorvusvolat-dotcom), PR #370:** the E8 bit word format, the producer whose output we reuse, the independent checker and the generalised official checkers.
- **applecrusher, PR #376:** helper-lifetime reuse, which the elimination reuse generalises.
- **ai-nanachi:**
  - PR #389: the frame-retiming idea;
  - PR #426: clean-reset reuse, the same slot-reuse mechanism, published first (developed independently here), and its R767 word as a comparison.
- **icekylinx, PR #433:**
  - the split-centre complex supplier that the headline κ uses;
  - its bit engine, finite invoice and six-level tail, ported here;
  - the R758 comparison.
- **DaysSky:**
  - PR #381: the B₄ layout and checkers;
  - PR #375: halving degree two;
  - PR #363: B_K and `bridged.py`.
- **Zhihao Chen (jacklightChen):**
  - PR #386: the compressed nine-stage bit layout and its checkers, generalised here;
  - PR #425: the mutable-basis complex word.
- **Chafik Boukhalfa (chafreaky), PR #417:** the B₄ pricing tail port, the #376 rebuild and the kernel-word control.
- **Rohan Arun (rohanarun):**
  - PR #431: a cited complex supplier and the two-supplier seed policy;
  - PR #392: the refined pricing tail.
- **Jacob Sussman:** the E8 family and the bridged word.
- **PR #266 and PR #315 (DreamingOfClouds) lineage:** the official checkers, the moment engines and the outer assembly.

Prepared by eumemic with substantial Anthropic Claude assistance. Apache-2.0 (`LICENSE`); see `NOTICE.md`.

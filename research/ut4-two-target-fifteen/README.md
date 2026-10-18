# No fifteen-call two-target UT4 word on two roles

**Exhaustive finite negative result in one explicit alphabet. No new κ; the selected record is unchanged.**

[CrocSwap/integer-mult-bounds#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662) (@ToikY, head
`01cc02b164ecc4f9d84df3f56a1fe65b88daf390`) defines the alphabet and proves at least 14 calls for two central
targets. [CrocSwap/integer-mult-bounds#1690](https://github.com/CrocSwap/integer-mult-bounds/pull/1690) (Aaron Wang /
@navinor, head `dfd15686309d26eb98740942c4e84cddeafae7d8`) excludes 14 calls on two roles. Its first open next question
asks whether 15 is attainable. This package answers it:

> With r = w = 2, no word of 15 paid factors `I+([g]+1)xy^T` (g in {a,b,c}, x, y nonzero in F2^2) equals
> `I+([z]+1)I_2`. No such word reaches even the degree-three quotient endpoint.

**Consequence for every r (conditional on written lemmas).** [CrocSwap/integer-mult-bounds#1680](https://github.com/CrocSwap/integer-mult-bounds/pull/1680)
(@ToikY, head `a281330e84e64ad357e35b338796c96144a345ce`) proves that every two-target word of at most 15 calls on any
finite r ≥ 2 roles compresses to a word on two roles, with no label count increased. #1662 excludes 13 or fewer calls,
#1690 excludes 14 on two roles, and this package excludes 15. So **two central targets need exactly 16 calls for every
finite r ≥ 2**, and the direct word `(abcb)^2` on each target is optimal. Sharing across the two targets saves nothing at
unit tariff. This rests on #1662's count bound and #1680's compression lemma. Both are written arguments. I checked them
line by line in this session (section "Written premises") but did not formalize them.

## Model

Exactly #1662's model, as used by #1690: formal group algebra F2[UT4(F2)], a = I+E12, b = I+E23, c = I+E34,
z = I+E14. Every paid factor counts once; scalar GL2(F2) mixing is free and normalized away; there is no COPY, ERASE or
clean workspace. With r = 2 there are nine couplings `xy^T` per label.

#1662's bound (n_a, n_c ≥ 2w = 4 and n_b ≥ 3w = 6) leaves three label-count splits for 15 calls: (5,6,4), (4,6,5) and
(4,7,4). The verifier searches all three. (5,6,4) and (4,6,5) are related by the automorphism ψ(g) = J g^{-T} J of
UT4(F2), which swaps a and c and fixes b and z (`test_package.py` checks this on all 4,096 pairs), so searching both is
redundant. It is kept as a cheap control.

## Method

The pipeline is #1690's, generalized; `pr1690_search.py` is #1690's `search.py`, vendored byte for byte, and
`verify.py` checks its SHA-256. It supplies the group algebra, the quotient Q, the profile, key and expansion formulas,
and both endpoint checks. `fifteen.py` adds:

1. **Unequal a/c counts.** Separate a-prefix and c-suffix profile sets (133,561 profiles for five couplings in six
   middle gaps, 39,355 for four couplings in seven).
2. **Seven middle calls.** The cross-key masks have seven bits, so `fifteen.py` has its own 7-bit `key_cross` and
   solution table. #1690's parity table covers six bits only. A first run without that fix crashed rather than
   returning a wrong answer.
3. **A trie side screen.** The a- and c-side coefficients (ab, ba, aba, bab and the mirror) are accumulated along a trie of
   profiles rather than per profile. Middle sequences are processed in parallel with `multiprocessing`, merged in a
   fixed order. Standard library only.

Every surviving profile pair is expanded into all concrete words: per-gap coupling tuples, then every a/c interleaving
inside each gap. Each word is checked against the full degree-three quotient endpoint and, separately, the full formal
endpoint in `M_2(F2[UT4(F2)])`.

| Split | Canonical middles | Profiles a / c | Side passes a / c | Key pairs | Profile pairs | Words | Q pass | Formal pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| (4,6,4) (= #1690) | 5,582 | 20,791 / 20,791 | 3,383,566 / 3,383,566 | 184 | 208 | 3,248 | 0 | 0 |
| (5,6,4) | 5,582 | 133,561 / 20,791 | 9,815,222 / 3,383,566 | 340 | 1,252 | 114,960 | 0 | 0 |
| (4,6,5) | 5,582 | 20,791 / 133,561 | 3,383,566 / 9,815,222 | 340 | 1,252 | 114,960 | 0 | 0 |
| (4,7,4) | 49,686 | 39,355 / 39,355 | 47,271,678 / 47,271,678 | 3,944 | 5,952 | 64,680 | 0 | 0 |

The (4,6,4) row is a regression control. The generalized driver reproduces every stage count #1690 records.

## Written premises (checked by reading, not formalized)

The every-r statement uses two written arguments. I re-derived each step:

- **Count bound (#1662).** The first-order coefficient gives `X_g Y_g = 0`, so `n_g ≥ u_g + v_g`. The four
  degree-three target coefficients abc, cba, bac (BAC+BCA) and acb (ACB+CAB) force each of the six spans to contain
  the target span, so every rank is at least w. For the middle label, `XY = UY = XV = 0` and `UV = P`, from the
  B, AB, BC and ABC coefficients. So P factors through `ker X / im Y`, which gives `n_b ≥ w + u_b + v_b`. Together these
  give n_a, n_c ≥ 2w and n_b ≥ 3w.
- **Compression (#1680).** Summing gives `L ≥ 7w`. At L ≤ 7w + 1 at most one span exceeds w, so all row spans or all
  column spans equal the target span. Every factor is then block triangular with one common orientation. The
  active-corner projection is multiplicative on that block-triangular ring, even with noncommutative entries. Zero
  projected couplings are dropped, so length and label counts do not increase. At w = 2, L = 15 = 7w + 1, so the lemma
  applies to 15-call words. A compressed word may be shorter, which #1662 (≤ 13) and #1690 (14) cover.

I found no gap. This is one reader's check, not an independent formalization.

## Evidence and controls

- `verify.py` (standard library; 243 s wall and about 30 CPU-minutes on a 10-core Apple M-series machine, Python 3.12;
  `--workers N` to change, `--part small|large` to split as in `VERIFY.json`):
  - the vendored #1690 module's hash;
  - the quotient homomorphism on all 4,096 pairs;
  - GL2(F2) orbit coverage of all zero-sum middle sequences of length 6 and 7;
  - the direct 16-call positive control;
  - the exact #1690 (4,6,4) regression;
  - all three 15-call splits against the counts in `EXPECTED.json`, with no formal solution.
- `test_package.py`:
  - the trie screen equals a brute-force screen with #1690's formulas, for every split;
  - the 7-bit `key_cross` equals the direct cross coefficients;
  - indexed key pairing equals brute-force pairing on 7-bit keys;
  - planted-word completeness: for random words of each split, with the word's own screen values, its profiles
    pass the screen under their keys, the key pairing emits that pair, and the expansion regenerates the word;
  - the ψ automorphism;
  - the r = 1 driver control.

## Scope and limits

- The search covers r = 2 only. Extending it to every r uses #1680's written lemma, and the count split uses #1662's
  written bound. Neither is formalized.
- The search reuses #1690's formulas and expansion code. A systematic error shared with #1690 would affect both
  results. The regression, brute-force screen and planted-word tests guard against this but are not an independent
  reimplementation.
- Unit tariff only. A weighted tariff can make a word longer than 15 calls cheaper, and nothing here covers that.
- No rational-frame identity, physical compiler, supplier profile or κ change. No proof-assistant or human review.
- The registered `--part large` replay took 149 s wall and 21 CPU-minutes here (`--part small`: 86 s, 9 CPU-minutes). It fits its 600 s timeout only on 4 or more cores of comparable speed.

## Reproduce

From the repository root, Python 3.10+ (registered replay uses 3.12):

```sh
python3 -B research/ut4-two-target-fifteen/verify.py        # PASS_UT4_TWO_TARGET_R2_NO_15
python3 -B research/ut4-two-target-fifteen/test_package.py
python3 scripts/research_package.py --package research/ut4-two-target-fifteen --check-only
```

## Open next questions

1. **Three or more targets.** Is `8w` optimal for every w, or does sharing start at w = 3? Why it matters: two targets
   now show no sharing at unit tariff, and the lower bound `7w + [w=1]` still leaves a gap of w. First step: at w = 3,
   #1680's compression applies only to L ≤ 22 while the gap is 21..24. So first decide 21 and 22 on three roles. Blocker:
   the profile pipeline has 49 couplings per label at r = 3, and the middle has at least 9 calls. It needs a new
   symmetry reduction (GL3(F2) has order 168) or a quotient-level meet-in-the-middle.
2. **Weighted tariffs.** For which price ratios β/(α+γ) can a word longer than 16 calls beat `(abcb)^2` per target?
   Why it matters: #1662 prices labels separately, and the separate-label bound `n_b ≥ 3w` is below the direct word's
   `4w`. First step: decide whether any two-target word has n_b = 6 or 7, at any length. Blocker: #1680's compression
   needs L ≤ 15, so long words on extra roles are not covered.

See [TASK.json](TASK.json) for the structured form.

## Credit

The model, count bound and question are @ToikY's (#1662). The workspace compression is @ToikY's (#1680). The profile
and key pipeline and the 14-call exclusion are Aaron Wang / @navinor's (#1690); its search module is vendored
unchanged. That lineage builds on steph4n-gh (#1573), Arham Tahir (#1589) and Hanson Sun / @bbMisk (#1607).

Josie Elliston's donated session; substantial AI assistance from Claude Code in implementation, checking and writing.
No independent human review. Apache-2.0.

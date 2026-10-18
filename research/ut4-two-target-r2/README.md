# No fourteen-call two-target UT4 word on two roles

**Exhaustive finite negative result in one explicit alphabet. No new κ; the selected record is unchanged.**

[CrocSwap/integer-mult-bounds#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662) (@ToikY, head
`01cc02b164ecc4f9d84df3f56a1fe65b88daf390`) proves that two central targets need at least 14 paid calls
in its `F2[UT4(F2)]` alphabet, and the direct word `(abcb)^2` per target uses 16. Its open next question
asks whether 14 is attainable. This package answers it for words with **no extra roles**:

> With r = w = 2, no word of 14 paid factors `I+([g]+1)xy^T` (g in {a,b,c}, x, y nonzero in F2^2)
> equals `I+([z]+1)I_2`. No such word even reaches the degree-three quotient endpoint.

**With CrocSwap/integer-mult-bounds#1680, this covers every workspace size.** @ToikY's concurrent
[CrocSwap/integer-mult-bounds#1680](https://github.com/CrocSwap/integer-mult-bounds/pull/1680) (head
`a281330e84e64ad357e35b338796c96144a345ce`) proves in writing that every 14- or 15-call two-target word with
any finite r ≥ 2 compresses to a word on exactly two roles. Factors are dropped, never added, and
CrocSwap/integer-mult-bounds#1662 excludes 13 calls or fewer. Together the two give: **two central targets need at least 15 calls
for every finite r**, so the tariff interval is 15..16. That corollary is conditional on CrocSwap/integer-mult-bounds#1680's written
lemma, which this package does not re-derive or audit.

## Model and what is relied on

The alphabet, target and counting rules are CrocSwap/integer-mult-bounds#1662's: every factor is counted, scalar mixing is free, and
there is no COPY, ERASE or clean workspace. With r = 2 there are nine couplings `xy^T` per letter.
CrocSwap/integer-mult-bounds#1662's written theorem (`n_a, n_c ≥ 2w`, `n_b ≥ 3w`) forces the counts (4,6,4) on a 14-call word. That
theorem is cited, not re-derived here. Everything else is checked in this package.

## Method

Let `Q = F2<a,b,c>/(a², b², c², ac−ca, degree ≥ 4)`, the quotient CrocSwap/integer-mult-bounds#1662 uses. `verify.py` independently
checks that `g ↦ 1+g` extends to a multiplicative map `UT4(F2) → Q` on all 4,096 pairs, with
`z ↦ 1+abc+acb+bac+cba`. Every coefficient of the target's image in `M_2(Q)` is therefore a necessary
condition.

1. **Middle sequences.** These are the six b-couplings with zero sum (33,489 sequences). Conjugation by
   GL2(F2) fixes the target, so only the 5,582 conjugation-minimal ones are searched; their orbits are
   checked to cover all 33,489.
2. **Profiles.** Write `P_j` for the sum of a-couplings before the j-th b-call and `Q_j` for the sum of
   c-couplings after it. With zero a- and c-totals, the a/b-only coefficients
   `ab = Σ P_j N_j`, `ba = Σ N_j P_j`, `aba = Σ P_j N_j P_j` and
   `bab = Σ_{j<k} N_j (P_j+P_k) N_k` depend only on the profile. The same formula gives the c/b-only
   coefficients for `Q`. There are 20,791 realisable profiles of four couplings.
3. **Keys.** The cross coefficients are `abc = Σ u_j(P) w_j(Q)^T` and `cba = Σ u_j(Q) w_j(P)^T`, with
   `u_j = P_j x_j` and `w_j = P_jᵀ y_j`. So profiles are grouped by these vectors, and pairs are found by
   solving the linear `abc = I` condition for the partner's masks.
4. **Expansion.** Every surviving profile pair is expanded into all concrete words: per-gap coupling tuples
   and every a/c interleaving within a gap. Each word is checked against the full `Q` endpoint and,
   separately, the full formal endpoint in `M_2(F2[UT4(F2)])`.

| Stage | Count |
|---|---:|
| Canonical middle sequences | 5,582 |
| Profiles passing the one-sided screen (summed) | 3,383,566 |
| Key pairs / profile pairs with `abc = cba = I` | 184 / 208 |
| Concrete words expanded | 3,248 |
| Words passing the `Q` endpoint | 0 |
| Words passing the formal endpoint | 0 |

## Evidence and controls

- `verify.py` (about 3 min, standard library) checks the homomorphism and orbit coverage. It also checks
  that CrocSwap/integer-mult-bounds#1662's direct 16-call word passes both endpoints while each of its 16 one-call omissions fails.
  It then replays the search and compares every stage count with the table above.
- `test_package.py` (13 tests, 1–2 min):
  - Random words, 6,000 of them, check the profile formulas against direct `Q` products.
  - Random keys check indexed pairing against brute-force pairing.
  - The CrocSwap/integer-mult-bounds#1662 failed 12-call trial is rejected.
  - A planted-word completeness test: for random (4,6,4) words, the enumeration rerun with that word's
    own screen values regenerates the word.
  - The slow reference driver finds `(abcb)^2` at r = w = 1, and finds nothing with counts (2,3,2).
- Six mutations of the formulas and target (operand order, the `bab` sum, cross order, quotient
  reduction, left versus right multiplication, the central target) are each caught by the tests.

## Scope and limits

- The search itself covers only r = 2. The transfer to r ≥ 3 is CrocSwap/integer-mult-bounds#1680's written compression lemma, not
  a computation here.
- The count split relies on CrocSwap/integer-mult-bounds#1662's written lower bound.
- This is a finite exhaustive search over one explicit alphabet. It establishes no rational-frame identity,
  physical compiler, supplier profile or κ change. No proof-assistant or independent human review.

## Reproduce

From the repository root, Python 3.10+ (registered replay uses 3.12):

```sh
python3 -B research/ut4-two-target-r2/verify.py        # PASS_UT4_TWO_TARGET_R2_NO_14
python3 -B research/ut4-two-target-r2/test_package.py
python3 scripts/research_package.py --package research/ut4-two-target-r2 --check-only
```

## Open next questions

1. **Is 15 attainable at r = 2?** By CrocSwap/integer-mult-bounds#1680 this decides the exact two-target cost for every r: 15 if a
   witness exists, otherwise the direct 16-call word is optimal. A first step is to run this pipeline on
   the splits (5,6,4), (4,7,4) and (4,6,5) allowed by CrocSwap/integer-mult-bounds#1662's bound. The blocker is that `fast_search`
   is specialised to (4,6,4); it needs unequal a/c counts (separate profile sets and tables) and seven
   middle calls (9⁷ sequences before symmetry).
2. **Independent check of CrocSwap/integer-mult-bounds#1680's compression lemma.** The every-r corollary rests on it. A first step
   is to run this package's formal checker on CrocSwap/integer-mult-bounds#1680's compression fixtures. The blocker is that the
   lemma is a written argument; finite fixtures corroborate it but cannot replace a proof review.

See [TASK.json](TASK.json) for the structured form.

## Credit

The question, model and lower bound are @ToikY's
([CrocSwap/integer-mult-bounds#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662)), building on steph4n-gh
([CrocSwap/integer-mult-bounds#1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573)), Arham Tahir
([CrocSwap/integer-mult-bounds#1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589)) and Hanson Sun / @bbMisk
([CrocSwap/integer-mult-bounds#1607](https://github.com/CrocSwap/integer-mult-bounds/pull/1607)). The workspace compression that
extends the result to every r is @ToikY's
([CrocSwap/integer-mult-bounds#1680](https://github.com/CrocSwap/integer-mult-bounds/pull/1680)). No predecessor code is imported.

Prepared by Aaron Wang / navinor, with help from Claude Code. Apache-2.0.

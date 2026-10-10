# Kernel families at the early cut, shared donors, and the two retimings, composed

**Claim.** On PR #249's bit word (commit `96495746`), PR #259's multi-cut kernel condensation extended to 890 pivot
families (entrance rank 1,719) and retimed by PR #263's 25 descent gates and PR #270's 29 plateau blocks is a legal
word of the same model with literal bank stock 866,550 and κ = 711482139228173/10¹⁸ = 7.11482139228173·10⁻⁴, checked
by PR #259's seven native checkers, the two retiming stages' own audits, and PR #259's exact pricer, under the retained
public all-size hypotheses of PR #249/#254/#259.

## 1. The mechanism (PR #254/#259, unchanged)

A dirty helper j untouched before a cut (initial frame ZERO, final frame FULL, no write, copy or non-initial read
before the cut) acts on the targets only through its initial zero-frame compensation reads, so its *complete target
response* R_j ∈ F₂^1760 is a column of the prefix's target map. Helpers a, b with R_a = R_b and a nondegenerate common
entrance subspace E inside both first required frames admit the rewrite: a (the pivot) starts at E and its initial
reads are deleted; b (the donor) moves ZERO → E at the cut and absorbs a there (Q = I + e_b e_aᵀ); the old word
resumes from E; Q⁻¹ is paid at the full frame; the omitted response R_a·a and the induced change R_b·a cancel. PR #259
generalises this to several simultaneous zero-response directions at four cuts and admits any entrance through an
exact chart audit (B⁻¹(I − σ)B diagonal, factor count ≤ 548, intermediates below 2⁸⁰).

## 2. The families added

Cut 676,559 is the last initial compensation read (records 0..676,559 are the 676,560 initial reads; the first MOVE
follows). Among the 14,286 clean helpers live there, the responses form 985 twin classes of size two and 24 of size
nine. Three rounds, each admitted by the φ ledger (with the deficit pinned at 35,200 per replica the coarse exponent is
driven by Σ r·n·ln(120/r), φ(r) = r·ln(120/r); a pair with first ranks (r_a, r_b) and e = 1 changes it by
φ(r_a − 1) − φ(r_a) + φ(1) + φ(r_b − 1) − φ(r_b): −2.02 for (2, 2), −0.97 for (3, 3)):

1. `union-early-cut`: 333 twin pairs disjoint from all 1,194 helpers of PR #259's families (319 with first frames
   (2, 2) on lines u = eᵢ − eⱼ — norm 2, cleared Gram 9·uᵀu − (Σu)² = 18, excluded primes {2, 3} as for the ±1-four
   lines of PR #254, which PR #254's `norm == 4` rule excluded and PR #259's generic audit admits — and 14 pairs
   (3, 5), (3, 3), (3, 6) with ±1-four lines), two dropped for the mod-3 rule.
2. `headroom-2`: every response class of any size at twelve cuts from 676,559 to 727,593, pairs and XOR triples
   R_c = R_a ⊕ R_b; 32 more disjoint net-positive families, all at 676,559 (28 (3, 3), two (3, 6), one (3, 5) with e = 1,
   one (3, 5) on its full two-dimensional nondegenerate intersection); nothing at any later cut; no net-positive triple
   (a partner costs φ(1) + φ(r − 1) − φ(r) > 0).
3. `shared-donor`: PR #259's transform only requires pivots to be unique and never donors; a partner may serve several
   families, being moved to each family's entrance in increasing dimension at its cut, so a shared donor is legal when
   its entrances form a nested chain and its own first use is after every cut it serves. For every current donor d and
   every clean untouched helper p with R_p = R_d, the entrance is d's existing subspace when it lies inside F_p (the
   lift already paid) or a nondegenerate line inside E_d ∩ F_p; greedy by gain, dissolving a plain pair when a
   shared-donor alternative is strictly better and its donor serves no other family: 54 shared-donor families (51 on
   the donor's existing entrance, 3 on nested lines; pivot ranks 49 × 3, 5 × 5), 26 pairs dissolved (11 of round 1, 15 of
   PR #259's at 680,080 and 700,582, whose helpers re-enter as pivots or donors of better families), including all 24
   reuse pairs and the two e = 2 planes of PR #270.

Total: 890 families (PR #259's remaining 503 + 387 added), entrance rank 1,719 ≡ 0 mod 3, 1,903 helpers, 96 shared
donors; 60,520 initial reads removed, 2,286 gates paid.

## 3. The two retimings

PR #263 (rohanarun) reassigns the frames of 25 internal ADD gates found by local descent on the concave paid-rank
objective Σ r·ln(120/r); its selection binds gates by ADD ordinal, scalar content and old basis and is gated by the
input transcript's sha256. PR #270 (utcorvusvolat-dotcom) ships the rebinding (full scalar-core alignment: every
ADD/COPY/ERASE event outside the kernel categories must be identical) together with its own stage, 29 connected
plateau blocks of 57 ADDs retimed jointly, with audits of the operand source spans and of all added frames. Both
selections rebind to this transcript (the core events are identical; 18 of the 25 descent gates touch registers that
are helpers here, and every self-check of the stage still passes, so disjointness from the pivots was sufficient, not
necessary). Histogram deltas: descent {2: −2, 4: +24, 5: −48, 6: +25, 11: −1, 13: +2, 17: −1} (one call removed);
plateau {1: +15, 2: −26, 3: +19, 4: −7, 5: −3, 6: +21, 7: −24, 8: +8, 9: −14, 10: −2, 11: +13, 12: −4, 13: +4} (calls
and mass unchanged).

## 4. What is checked (receipts in `expected/`)

| stage | receipt |
|---|---|
| `cohort-transform` (all-column F₂ replay) | 890 pivots, entrance rank 1,719, 60,520 initial reads removed, 2,286 gates, raw mass 434,177 → 432,458; omitted-Q and omitted-Q⁻¹ controls fail nontrivially |
| `descent_retiming` → `plateau_retiming` | sha gates cohort d073aeb4… → descent 43a73a44… → final 4f6ffc1d… (828,136 records); spans and frame-table audits PASS |
| `cohort-legality-independent` | 1,903 helpers, 0 source-owner and 0 donor intersections, 24 COPY/ERASE windows, all final frames |
| `cohort-prefix-independent` | 890 cohorts, 4 cuts, 1,566,400 target-kernel equalities |
| `cohort-bank-review` | literal stock 866,550 (saved 2,865), 919 exact charts (at most 262 factors), 3,317,400 assignments, selector 626,937,131,600 |
| `cohort-five-stage-columns` | 23,627 columns, payload 98 bits |
| `cohort-price` | coarse 142397741344279/(2·10¹⁷), W 173,310, 3,970,400 calls, mass 20,762,000, deficit 35,200, 47/47 constraints, adjacent grid rejected, pinned-baseline regression exact |
| `cohort-finite-invoice` | PASS, deficit 176,000, cutoffs positive |

Control: PR #259's own selection through the same transform reproduces its κ exactly, and the stable-sorted PR #259
word is byte for byte the input PR #263's selection is bound to (sha 1ae06b18…), whose descent output is the input of
PR #270's plateau selection (80af525c…).

Platform matters (so that one package verifies on Linux/g++ and macOS/clang alike): `code/cohort-transform.cpp` uses
`std::stable_sort` on the gauge order (the tie order of `std::sort` differs between libstdc++ and libc++ and changed the
transcript's sha256); `verify.py` drops `containment_pairs_checked` (a memo-cache miss counter) from the compared
receipt fields and normalizes both sides. Nothing else of PR #259's code changes; `discovery/README.md` lists the diff.

## 5. Not claimed, not composed

No Lean certificate; the public all-size interfaces of PR #249 are retained as hypotheses. Not composed here:
eumemic's target-prefix compression (PR #268; PR #273 composes it with #269, PR #272 with collective kernels) and
evmckinney9's cleanup sandwiches (PR #271); 492 twin candidates whose donor's entrance is not inside the new pivot's
first frame and multi-donor relations R_p = R_d₁ ⊕ R_d₂ were not searched.

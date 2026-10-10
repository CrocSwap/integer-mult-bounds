# The early cut carries 365 more response-kernel families

**Claim.** On PR #249's bit word (commit `96495746`), PR #259's multi-cut kernel condensation extended by 365
twin-pair rewrites at its earliest cut (record 676,559) is a legal word of the same model with literal bank stock
866,565 and κ = 44463833535321/(625·10¹⁴) = 7.11421336565136·10⁻⁴, checked by PR #259's seven native checkers
and priced by its exact pricer, under the retained public all-size hypotheses of PR #249/#254/#259.

## 1. The mechanism (PR #254/#259, unchanged)

A dirty helper j that is untouched before a cut (initial frame ZERO, final frame FULL, no write, copy or
non-initial read before the cut) acts on the targets only through its initial zero-frame compensation reads, so
its *complete target response* R_j ∈ F₂^1760 is the column of the prefix's target map. Two such helpers a, b with
R_a = R_b and a common nondegenerate rank-one line E inside both first required frames admit the rewrite of PR
#254: a starts at E (its initial reads are deleted), b moves ZERO → E at the cut and absorbs a there (Q = I +
e_b e_aᵀ), the old word resumes from E (the first moves of a and b become E → F_a, E → F_b), and Q⁻¹ is paid at
the full frame; the omitted response R_a·a and the induced change R_b·a cancel. PR #259 generalises this to
several simultaneous zero-response directions at four cuts and admits any entrance line through an exact chart
audit (B⁻¹(I − σ)B diagonal, factor count ≤ 548, intermediates below 2⁸⁰).

## 2. What is added

At the earliest of PR #259's four cuts, record 676,559 (the last initial compensation read; records 0..676,559
are the 676,560 initial reads, and the first MOVE follows), 14,286 clean helpers are live. Their responses form
985 twin classes of size two and 24 of size nine. Of the 985 pairs, 747 have a nonzero nondegenerate common
line; 335 are disjoint from all 1,194 helpers of PR #259's 518 families (319 with first frames (2, 2), 8 with
(3, 5), 7 with (3, 3), 1 with (3, 6)); 333 are kept (the two of smallest gain dropped so that the total entrance
rank 1,344 + 333 = 1,677 is ≡ 0 mod 3, which PR #259's transform requires at 40 replicas). Their lines are
u = eᵢ − eⱼ (norm 2; cleared Gram 9·uᵀu − (Σu)² = 18, so the excluded primes are {2, 3}, as for the ±1-four lines
with Gram 36) for the (2, 2) pairs and ±1-four lines for the others. Each is a pair with e = 1, exactly PR
#254's shape; they enter `inputs/candidates.json.gz` in PR #259's schema (`pivot`, `partners`, `roles`,
`basis`, `dim = 1`, `E_dimension = 1`, `cut = 676559`, `first_frames`, `kind`, `round = "union-early-cut"`)
after PR #259's 518 items, which are unchanged.

Second round. Among the 12,427 clean helpers not used by the 851 families, the response classes at twelve cuts from
676,559 to 727,593 (every class of any size, pairs and XOR triples R_c = R_a ⊕ R_b, entrance a nondegenerate line or
the full intersection when its Gram is nondegenerate) contain 64 net-positive pair candidates and no net-positive
triple (a partner costs φ(1) + φ(r − 1) − φ(r) > 0, so only the pivot gains); a greedy packing by gain keeps 32
disjoint families, all at cut 676,559: 28 pairs (3, 3) with e = 1, two (3, 6), one (3, 5) with e = 1 and one (3, 5)
entering on its full two-dimensional intersection (e = 2), entrance rank 33, so the total 1,710 is ≡ 0 mod 3 with
no drop (`round = "headroom-2"`). The later cuts add nothing: at 680,080 and 700,582 the candidate set is the same,
from 705,000 on it shrinks to nothing. After these 32 no net-positive pair or triple remains among unused helpers at
any cut, so this lever is exhausted on this word under the φ ledger.

Why they pay: with the deficit pinned at 35,200 per replica (120·W − mass is invariant under the rewrite, because
the pivot's residual 24 → 23 shrinks the bank capacity by exactly the mass saved), the coarse exponent is driven by
the log-weighted mass Σ r·n·ln(120/r); a pair with first ranks (r_a, r_b) and e = 1 changes it by
φ(r_a − 1) − φ(r_a) + φ(1) + φ(r_b − 1) − φ(r_b), φ(r) = r·ln(120/r): −2.02 for (2, 2), −0.97 for (3, 3), and
PR #259's exact pricer confirms the sign and the size on the whole selection.

## 3. What is checked (PR #259's checkers, unchanged; receipts in `expected/`)

| checker | receipt |
|---|---|
| `cohort-transform` (all-column F₂ replay) | 883 pivots, entrance rank 1,710, 59,192 initial reads removed, 2,272 gates, raw mass 434,177 → 432,467, 829,444 records; omitted-Q control 37,450 wrong columns, omitted-Q⁻¹ control 1,084 |
| `cohort-legality-independent` | 1,924 selected helpers, 0 source-owner and 0 donor intersections, 729,703 common-frame ADDs, 99,693 nested MOVEs, 24 COPY/ERASE windows, all final frames |
| `cohort-prefix-independent` | 4 cuts, 1,554,080 target-kernel equalities, 37,042,593 non-target identity bits |
| `cohort-bank-review` | literal stock 866,565 (saved 2,850), residual families 23: 733, 22: 42 and 24: 13,404 (others unchanged), 3,317,400 assignments, 883 exact charts (at most 200 factors), selector 626,937,137,600 |
| `cohort-five-stage-columns` | 23,627 columns, payload 98 bits |
| `cohort-price` | coarse 711927817449537/10¹⁸, W 173,313, 3,971,440 calls, mass 20,762,360, deficit 35,200, 47/47 constraints, adjacent grid rejected, pinned-baseline regression exact |
| `cohort-finite-invoice` | coefficient 56 bits, deficit 176,000, cutoffs positive |

Control: PR #259's own selection through the same pipeline reproduces its κ exactly and six of its seven
receipts byte for byte; the seventh differs only in `containment_pairs_checked`, a memo-cache miss counter of
the legality checker that depends on the compiler's evaluation order and not on what is checked (PR #259's
expected value 82,347 against 82,344 with Apple clang).

Two platform matters, so that the same package verifies on Linux/g++ (the workflow) and on macOS/clang:
`code/cohort-transform.cpp` orders the gauges by frame dimension with `std::sort`, whose order among equal
dimensions differs between libstdc++ and libc++, so the emitted transcript (and its sha256 in `RESULT.json`)
differed between the two; this package's copy uses `std::stable_sort` there (one token; the gates of equal-dimension
gauges keep their selection order, every checker is unchanged). And `verify.py` adds `containment_pairs_checked`
to the platform-dependent fields its `normalize` already drops (`seconds`, `local_scalar_stream`) and applies
`normalize` to the committed receipt as well as to the fresh one (two lines). Nothing else of PR #259's code
changes; `discovery/` lists the diff.

## 4. Not claimed

No Lean certificate; the public all-size compiler, chart, routing, prime-supply, precision and analytic interfaces
of PR #249 are retained as hypotheses, as in PR #254/#259. The 4 pairs whose twin is a PR #259 helper have no
other twin at any cut; PR #263's 25 frame retimings do not apply verbatim (18 of their registers are among the
helpers used here, and their selection is bound to #259's transcript), and were not re-derived.

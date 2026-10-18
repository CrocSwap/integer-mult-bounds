# Actual T185 attainment of the current fixed-packing optimum

The actual five-copy relay has complete paid profile

    {1: 4029300, 2: 1068930, 3: 458874, 4: 213120,
     5: 65490, 8: 13320, 48: 66896}.

The independent review checks every one of its 679,320 helper roles in 1,665 calls, reconstructs its source-event windows, recounts the full profile, and certifies its exact moment above the full PR #2857 rational. Separately, an exact primal/dual certificate proves that this actual profile attains the fractional packing minimum for the fixed current word, inventory and bin capacities throughout the moment-root interval below. This is not a global optimality statement about integer multiplication or alternative native words.

## 1. Universal strict improvement of the actual relay

Let H_r = r^p for any 0 < p < 1. Relative to five source copies, the actual profile change is

    H_48 − H_3 − 5 H_9 < 0.

Indeed, 48 = 3 + 9 + 9 + 9 + 9 + 9. Divide these six positive parts by 48 to obtain positive numbers t_i < 1 with sum 1. Since t_i^p > t_i, their p-th powers sum to more than 1. Multiplying by 48^p proves the inequality. The live stock and normalization per source copy are unchanged. Thus the normalized paid moment decreases strictly for every exponent in this interval, independently of a displayed decimal approximation.

The allocation worker's actual ten whole-role moves consist of five replicated width 9 vacancy relays, followed by moving five actual width 9 roles out of one capacity 48 donor. Five capacity 16 bins that each held width 7 become full [7, 9] bins; the capacity 48 donor becomes empty. This converts the six old idle ranks [3, 9, 9, 9, 9, 9] into [48]. This explanation does not replace the literal checks: all source windows, family exclusions, disjoint masks and prefixes are recounted by `review_current.py`.

## 2. Precisely fixed packing model

For any positive replica count T, assume the unchanged source geometry and current native providers. Per replica the bin counts are

| Capacity c | 8 | 16 | 32 | 48 |
|---|---:|---:|---:|---:|
| B_c | 672 | 448 | 448 | 448 |

The current ordered native inventory has widths {4: 26, 5: 2, 7: 62, 8: 84, 9: 234}. There are nine calls per replica. The local paid profile is

    2394 H_1 + 642 H_2 + 266 H_3 + 128 H_4 + 26 H_5 + 8 H_8.

A bin pattern is a capacity c and a vector u = (u_4, u_5, u_7, u_8, u_9) of nonnegative integers with Σ_w w u_w ≤ c. Its remainder is r = c − Σ_w w u_w. Put H_0 = 0. There are exactly 1,163 such patterns over these four capacities.

For each pattern let x_(c,u) ≥ 0 be its fractional multiplicity. The constraints are

    Σ_u x_(c,u) = T B_c,
    Σ_(c,u) u_w x_(c,u) = 9 T I_w,

where I_w is the width inventory above. The objective is the sum of idle costs Σ_(c,u) H_r x_(c,u); add the fixed native paid cost separately. This relaxation allows more assignments than a chronological literal allocation. It therefore gives a valid lower bound for every actual allocation with these inventories, for every positive integer T whose enclosing source geometry and finite admission are admissible. It does not prove that every T satisfies the enclosing finite invoice, nor that every fractional solution has a literal realization.

## 3. Exact rational primal

The following bin multiplicities are per replica. A tuple lists the widths in the bin; an empty tuple leaves the entire bin idle.

| Capacity | Widths | Multiplicity | Remainder |
|---:|---|---:|---:|
| 8 | (8) | 672 | 0 |
| 16 | (7, 9) | 448 | 0 |
| 32 | (9, 9, 9) | 120 | 5 |
| 32 | (8, 8, 8, 8) | 21 | 0 |
| 32 | (7, 7, 9, 9) | 55 | 0 |
| 32 | (5, 9, 9, 9) | 18 | 0 |
| 32 | (4, 9, 9, 9) | 234 | 1 |
| 48 | () | 1808/5 | 48 |
| 48 | (9, 9, 9, 9, 9) | 432/5 | 3 |

Adding these rows gives every bin-count and helper-count constraint exactly over the rationals. Its idle objective is

    234 H_1 + (432/5) H_3 + 120 H_5 + (1808/5) H_48.

Adding the nine native call costs gives the complete per-replica profile

    H* = 21780 H_1 + 5778 H_2 + (12402/5) H_3
         + 1152 H_4 + 354 H_5 + 72 H_8 + (1808/5) H_48.

The actual T185 profile is exactly 185 times this profile, entry by entry. This is checked directly from the complete candidate file; no idealized replacement is made in the release.

## 4. Symbolic dual and weak duality

Set

    q = (H_3 − H_48)/5,     C = H_5 − 3q.

Use capacity prices

    λ_8 = C/4,   λ_16 = C/2,   λ_32 = C,   λ_48 = H_48,

and helper prices

    μ_4 = H_1 − H_5,   μ_5 = −H_5,
    μ_7 = −C/2 − q,    μ_8 = −C/4,    μ_9 = q.

Prices are unrestricted real numbers because the primal inventory constraints are equalities. For each of the 1,163 patterns the required inequality is

    λ_c + Σ_w u_w μ_w ≤ H_(c − Σ_w w u_w).

`profile_lp_certificate.py` verifies every one of these inequalities with exact symbolic coefficients and outward integer power intervals, uniformly throughout the root bracket in Section 5. Eleven inequalities are symbolically exact equalities. Every other inequality has a strictly positive lower slack. `lp-final-01/PATTERNS.json` records every pattern, its exact symbolic slack and its directed interval. A forged capacity price is explicitly rejected.

Why does this prove optimality? Multiply each inequality by its nonnegative primal multiplicity and sum. The two sets of inventory equalities give

    idle cost ≥ T [Σ_c B_c λ_c + 9 Σ_w I_w μ_w].

This is weak duality, proved directly without a solver. Substituting the displayed prices makes the bracket exactly the rational primal idle objective from Section 3; the code checks this as an identity of coefficients of H_1, H_3, H_5 and H_48. Thus the rational primal is optimal in the full fractional model. The actual T185 allocation has its objective value, so it attains that minimum despite the additional chronological restrictions. For any other admissible T the same scaled dual is a lower bound; integral attainment at that T is not assumed.

## 5. Uniform root bracket and exact arithmetic

The optimal normalized moment is

    Φ(p) = H*(p) / (896 × 73^p).

With α = 1 − p, each positive term (r/73)^(1−α) increases strictly with α because 0 < r < 73. Hence Φ(1−α) is continuous and strictly increasing. Directed arithmetic gives opposite strict signs at

    α_low  = 0.001720100805416885927944,
    α_high = 0.001720100805416885927945.

The unique moment root lies strictly between these rationals. The dual is feasible uniformly across this entire interval: for each integer r its lower power bound is evaluated at α_high and its upper bound at α_low, using monotonicity. Symbolic zero slacks are recognized as identities; positive and negative coefficients of every other slack select the appropriate outward endpoints. Consequently this is a locally uniform optimum certificate, not merely a floating comparison at a nominated exponent.

All power bounds use only integer arithmetic and Fraction. Write n = 2^k a with 1 ≤ a < 2 and z = (a−1)/(a+1), so 0 ≤ z ≤ 1/3. Integrating the geometric series for 2/(1−z²) gives

    log a = 2 Σ_(j≥0) z^(2j+1)/(2j+1).

After J terms the positive tail is at most 9 z^(2J+1)/(4(2J+1)). The code encloses the sum and powers by outward dyadic recurrences. It computes log 2 in the same way, then log n. For t = α log n in [0, 1/2], the positive Taylor series for exp(t) has remaining tail at most twice its next term. Outward reciprocal arithmetic yields n^(1−α) = n/exp(t). The scale is 2^512. No solver or floating transcendental is trusted in either the moment signs or the dual inequalities.

The enclosing target is α_low − 10^−46 − 10^−70. `REVIEW-FINAL.json` independently checks its moment and its exact rational superiority over PR #2857. This statement is conditional on the retained all-size compiler, native, hosting, precision/tape and analytic interfaces. Full admission, which retains payload 2048 and all denominator, mass and C0 guards, is a separate enclosing check.

## 6. Source and verification boundary

The actual staged words and T37 source are PR #2857 at `0b2e2537b368a0cade07ce3f71452ea018ebe394`, by Yiyang/Lyy-iiis with Codex assistance. It credits Jeremy Kothe's PR #2833 and Philippe Van Velzen's independent PR #2853 treatment of the same quartet. The vacancy-relay neighborhood overlaps Marius-Paul Dumitrean's PR #2856; no priority or previously-unused claim is made. The preserved PR #2855 atlas/mixed-fibre work is not silently inserted into this candidate. Earlier notices and licenses remain with the enclosing package.

The five-copy construction belongs to the allocation worker. This supplement supplies an independent owner/moment review and an exact fixed-model optimum certificate. Its arithmetic, source-event checks and LP dual are not new general mathematical identities. It asserts neither global optimality across dimensions or native circuits nor an unconditional integer multiplication theorem. No Lean process was used for this exact informal campaign.

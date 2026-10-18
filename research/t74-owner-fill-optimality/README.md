# Exact owner-fill optimality on the T74 handoff line: PR2374 is optimal; PR2435's fill leaves +5.8e-10

**Audit / independent check; no κ claim.** This package certifies the exact pattern-integer optimum of the
whole-helper owner fill for the two latest T74 claims and compares each claim's published fill with it.

- **[PR2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374)** (Jeremy Kothe) claims "an exact
  window-free-optimal owner fill" on [PR2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322)'s
  words.
  - **Confirmed and strengthened.** Every legal whole-helper owner fill of these words has
    **b ≤ κ₂₃₇₄ + 10⁻¹⁵**.
  - Its idle multiset `{1:21978, 3:8592, 5:2552, 32:1, 48:24560}` is the only one whose root exceeds
    κ₂₃₇₄ − 10⁻¹².
  - Owner-map work on the PR2322 words is therefore exactly exhausted. The earlier cap in
    [PR2402](https://github.com/CrocSwap/integer-mult-bounds/pull/2402) allowed up to 8.1e-10.
- **[PR2435](https://github.com/CrocSwap/integer-mult-bounds/pull/2435)** (Jeremy Kothe, κ = 0.0016985113437)
  raises 24 copy-buffer entrances and adds "an exact owner fill for the new inventory", with idle
  `{1:20824, 3:6695, 5:1, 48:25302}`.
  - **That fill is not the pattern optimum.** The unique pattern-integer optimum has idle
    **`{1:20822, 3:6694, 5:2, 48:25302}`**, with root **0.0016985119240, +5.80e-10 above PR2435's claimed κ**.
  - It moves two rank-1 remainders and one rank-3 remainder into one more rank-5 remainder. Its pattern
    counts are in the receipt; for example it uses two (32: 9,9,9) bins and 1,156 (48: 4,8,9,9,9,9) bins.
  - Every legal fill of the PR2435 words has b ≤ that root + 10⁻¹⁵.
  - Whether the optimum can be realized under PR2435's windows and family rules is **not** checked here.
    It is a concrete owner-level target worth up to +5.8e-10.

## Method (`owner_optimum.py`)

0. **Inputs.**
   - PR2322 words: profile and inventory recounted in PR2402.
   - PR2435 words: recounted for this audit with the PR2387 frame-climb rule from PR2435 head `324d7d35`
     (`BORROW-WORD-43base`, blob 7e382c2d; `BORROW-WORD-43extra`, blob 29fa1b3a). Both providers give
     profile {1:2359, 2:632, 3:330, 4:120, 5:38, 8:8} and inventory {4:33, 5:9, 7:62, 8:90, 9:240}, equal to
     the published report.
   - The idle multisets and κ values are as published in each PR body.
1. **The relaxation.** A legal fill places every helper role whole into one idle bin. The bins have ranks
   8/16/32/48 and counts 49,728 / 33,152 / 33,152 / 33,152. So the fill's idle remainders come from an
   integer pattern-count vector x ≥ 0 over the 1,163 width patterns, with the bin and width-inventory row
   sums fixed (PR2387 / PR2360 relaxation, after PR1129). Windows, families and ports are dropped. That
   makes this a relaxation of every legal fill, and the moment is linear in x.
2. **Root check.** The PR2322 local profile (recounted in PR2402) plus PR2374's idle multiset has its root
   certified within ±10⁻¹⁵ of the claimed κ, using 800-bit enclosures. Its rank mass equals 73·66304 − 23680.
3. **Exact dual.** At a₀ = κ₂₃₇₄ + 10⁻¹⁵, a float simplex dual is repaired to an exact rational dual. It is
   feasible against 800-bit lower enclosures of h(r) = (r/73)^(1−a₀) on all 1,163 patterns. Every integer
   x then satisfies

       66304·μₓ(a₀) ≥ L_loc + D + Σ_p rc_p xₚ,   rc_p ≥ 0 exact,

   and if Σ rc_p xₚ ≥ T := 66304 − L_loc − D, then bₓ ≤ a₀. Here T ≈ 1.5475e-4.
4. **Enumeration.** Every idle multiset of an integer x with Σ rc_p xₚ < T is covered exactly.
   - Nine basic columns form an invertible rational basis. Non-basic patterns with reduced cost at least T
     cannot appear. The eligible non-basic set varies by inventory and evaluation point.
   - The two degenerate columns have zero remainder and involve only zero-remainder basic columns.
     Their basis representations need not be integral: the PR2435 case includes halves.
   - Let D clear every denominator in these basis representations. Reduce each degenerate count modulo D.
     Basic counts change by integers only in zero-remainder columns, so integrality and the idle multiset
     are preserved. The verifier checks that the canonical zero-remainder basic counts are nonnegative
     for every enumerated heavy combination and residue. All other basic counts are unchanged. Thus
     every feasible original solution has a feasible enumerated representative.
   - The nondegenerate counts are bounded by their exact positive reduced costs and enumerated by a
     budget-pruned DFS. Basic variables are solved in exact rationals.
   - Integration review added the canonical-residue nonnegativity check and corrected the earlier
     integral-representation explanation. All search, exclusion and uniqueness controls still pass;
     the reported bounds and idle multisets are unchanged.
5. **Search, then exclusion.**
   - Search: at a = κ_claim, enumerate every integer solution that could beat the claim. A budget-pruned
     DFS is exact. Rank the distinct idle multisets by certified root.
   - Exclusion: at a₀ = (best root) + 10⁻¹⁵, zero integer survivors remain, so every fill has b ≤ a₀.
6. **Control at (best root) − 10⁻¹²:** the optimal fill must survive, and it does.
   - For PR2374 there are 25 survivors and for PR2435 there are 1,250. Each set is made of degenerate
     copies of one heavy part, and all carry the optimal idle multiset.
   - That gives the uniqueness statement.

An adversarial AI reviewer reviewed the PR2374 part (the PR2435 extension came later) and found it
**not refuted**. Using its own code
(Decimal at 90 digits), it:
- reproduced PR2374's root to 60 digits;
- confirmed with a Gomory group-relaxation shortest path that the only correction within the budget is one
  empty 32-bin;
- ran local search over more than 48,000 exchanges of up to 4 bins without finding any improvement.

Its runner-up fill, `{1:21978, 3:8591, 5:2553, 30:1, 48:24560}`, has a root 5.0e-10 below PR2374's. Its
two wording issues are fixed here: the nonnegativity argument for the degenerate sweep, and the
degenerate-copy count.

## Reproduce

From the repository root, standard library only. It needs no network, since all inputs are vendored and
pinned.

```sh
python3 -I -B research/t74-owner-fill-optimality/owner_optimum.py     # ~45 s
```

Expected final line:
`PASS_T74_OWNER_OPTIMUM pr2374:claim_is_optimum pr2435:optimum_gain=+5.803e-10 unique_within_1e-12 no_new_kappa`

All results were run on CPython 3.14.4; the registered Python 3.12 replay was not run locally.

## Scope and limits

- **What is not re-checked.** Realization of the fills (windows, families, ports, admission, outer) is not
  re-run, for either PR's fill or for the PR2435 pattern optimum. The bound covers every legal fill.
  Attaining PR2435's optimum needs a realized owner map.
- **What the statement covers.** It is about owner fills of the fixed PR2322 and PR2435 words, the 249/417
  dispatch and the unchanged PR2269 bin stock. Changed words, inventories or templates are outside it; see PR2402
  and PR2429 for those levers.
- **Exactness.** The enumeration is exact (integer and rational), with an exact dual and enclosures. The
  only floating-point step is the simplex that proposes the dual, and its repair is exact.

## Open next questions

- **Other inventories.** Do the same exact integer-optimality certificates hold for PR2312's and PR2269's
  inventories? That would show whether every recent owner-fill PR on the T74 line was already at the
  integer optimum. First step: run `owner_optimum.py` with their inventories and published idle
  multisets.
- **Recursive-interface levers.** Since packing on these words is exhausted, which word-level move is
  cheapest to realize? Candidates are a block-53 handoff (+4.3e-8, PR2402) and cold-restoring one
  end-climb-3 helper (+1.46e-6, PR2429). First step: attempt the PR601-style commutation test on the 64
  end-climb-3 helpers.

## Credits and licence

- PR2374 / PR2349 (Jeremy Kothe) and PR2363 (mason-hale): the audited fills.
- PR2322 (Vlado Vojdanovski): the words.
- PR2360 (Jeremy Diviney) and PR1129 (Ali Romman): the pattern-dual relaxation.
- PR2387 / PR2402 (this author): the LP and recount tools, vendored with pins.

Prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). An adversarial AI
reviewer was used; no independent human review is claimed. Apache-2.0.

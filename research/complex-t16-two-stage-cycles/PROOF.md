# Why the owner map is admissible and strictly cheaper

## Domain

This argument is the same as PR1407's (`research/astra-ultra-hosting-20261013/PROOF.md`
at `d8640f5b`). Relative to the selected PR1094 map, only the physical owner,
port and slice offset of whole helper roles change. The local gauge44 provider (480 whole helpers per call), the 144
complete calls and their order, orientations, source events, endpoint adapters,
global bridges and terminal corrections all stay fixed. `build.py` asserts that
every changed row keeps `stage`, `replica`, `time`, `helper` and `width`.

The bin `(o, c, p)` is owner replica `o`, idle child `c` and port `p`. Its
capacity is the rank of `c`. Its borrowing interval is the original idle
transition: after the owner's last source-event touch and before its idle
deadline, with all 144 bridges included. A placement of helper `h` of call `k`
into `(o, c, p)` is legal under four conditions:

1. **Capacity.** The widths assigned to the bin fit its rank, and the slices
   are a prefix `0..used-1`.
2. **Window.** The call position lies strictly inside the bin's interval.
3. **Family.** The physical family `o*F + (2*pair+side)*V + p` is used by no
   other helper of the same call.
4. **Integrity.** `copy = 112*o + p`, each helper appears once per call, and no
   helper is split.

The search (global class-level repack, ejection cycles, CP-SAT neighbourhood
re-assignments including the evacuation neighbourhood, class-level re-solves
with guided realisation, and the final min-diff re-assignment) only proposes a
final owner table. Intermediate states
are not executed; the controller only ever sees the final table. So it is
enough to check the final map, and this package checks it three independent
times:

- `build.py`'s own packing checker covers 1, 3 and 4 and the window
  membership of 2 against `PLAN.windows`.
- The seed67 auditor (Josie Elliston, PR1091) checks R1–R7, X1 and X2 and
  rejects its 11 mutations. `check.py` also confirms that every role lies
  strictly inside its window and that each helper appears once per call.
- The unchanged PR1087 strict verifier re-emits every affected chart. Its
  controller audit, finite invoice, independent T16 replay and 69 + 12 + 6 + 15
  rejecting controls all pass.

## All-input operator argument (inherited)

Inside one borrowed bin, the owner has no data touch between the interval's
opening event and its deadline. Each complete invocation applies its declared
data shear whatever the incoming helper values are. It also applies its
residual Clifford operator to the borrowed axes. Distinct slices partition the
bin's original `c` axes, and the exact Gaussian-dyadic factors commute. So at the
deadline the assigned slices together with the unused suffix act as the
original idle child. The owner's value is the original one whenever the
controller reads it. This is PR1407's argument, applied to a different legal
final assignment; it needs no new step. It inherits the common-label and
mutable-source realization assumptions; it does not prove them anew.

## Strict cost improvement

The paid recursive moment depends on the profile through a sum of per-residual
weights `H(r)` that are strictly concave in the rank `r` with `H(0) = 0`. In the
PR1407 and PR2077 arguments, `H(r) = r^p` with `0 < p < 1`. Rank mass
(1,041,408) and deficit (5,120) are unchanged. Against the selected PR1094 map,
the idle remainder profile changes by

```
{1:+116, 2:+8, 3:-270, 4:+1, 7:-2, 16:+1, 48:+14}
```

selected: `{1:2276, 3:377, 7:7, 48:4866}`; this map:
`{1:2392, 2:8, 3:107, 4:1, 7:5, 16:1, 48:4880}`. The residual totals are equal
(237,024 on both sides). Sorted in decreasing order and padded with zeros to
the common number of bins,

```
new: 48 x 4880, 16 x 1, 7 x 5, 4 x 1, 3 x 107, 2 x 8, 1 x 2392, 0 ...
old: 48 x 4866,         7 x 7,        3 x 377,        1 x 2276, 0 ...
```

The partial sums of the new vector are never below those of the old one.
They agree for the first 4,866 entries (all 48), the new vector leads from
entry 4,867 on (by 602 after 4,880 entries; the largest lead is 636, after
4,887 entries), and the old vector never catches up before both reach 237,024
(after 4,880 + 1 + 5 + 1 + 107 + 8 + 2,392 = 7,394 and
4,866 + 7 + 377 + 2,276 = 7,526 entries). So the new residual vector majorizes
the old one, strictly. In words: 270 residuals 3 and two residuals 7 are gone,
and their residual capacity (824) reappears as 14 more completely idle bins
(672), one residual 16, one residual 4, eight residuals 2 (16) and 116 more
residuals 1. `check.py` checks this mechanically: it sorts and pads both
audited idle vectors, asserts equal totals and that every partial sum of the
candidate vector is at least the selected one's, with strict inequality
somewhere, and records the result as `majorization` in `CHECK.json`;
`verify.py` requires it. By Karamata's inequality for strictly concave `H`,

```
4880 H(48) + H(16) + 5 H(7) + H(4) + 107 H(3) + 8 H(2) + 2392 H(1)
  < 4866 H(48) + 7 H(7) + 377 H(3) + 2276 H(1)
```

(for example 36,417.5 < 36,660.1 at `p = 1/2`). The complex moment strictly
decreases while rank mass and deficit are unchanged. (Version 3 of this package
did not have this property and relied on the exact engines alone.)

The sign argument gives the direction only. The value of κ comes from the
pinned exact engines (moment, base-two moment, outer) and the strict replay,
not from a hand computation. The native complex lower endpoint is
`1676419885861434425020/10^24` (selected: `1675462676808103522925/10^24`). The
bit lower endpoint is unchanged at `1733427039589844234749/10^24`. The complex
supplier is binding, so κ = `1673614205725695/10^18` = 0.001673614205725695.
With the conservative bit surcharge, κ = 0.001673614202872892. The unchanged
strict verifier's own moment engines and outer assembly reach the same κ, and
the PR1069 sweep independently certifies the endpoint, the deficit identity
`W - 64N`, halving, the PR589 bit record, and that κ equals both the record and
the title value. The search used the surrogate `Σ f ln f` over idle fragments
only to rank candidates; only the final profile matters for κ.

## A proved packing ceiling

This section bounds how far owner packing on this supplier can go, in two
quantities: the number of completely idle cap-48 bins and the search surrogate
`E = Σ_bins g(free)` with `g(f) = f ln f` (`g(f) = 0` for `f ≤ 1`). It does
**not** bound κ directly (see the end of the section). `ceiling_bound.py`
checks every step with exact integer arithmetic and the standard library only;
`verify.py` runs it.

**Instance.** The bins are the 288 (owner, idle child) windows of `PLAN.json`
times 112 ports: 32,256 bins with capacities 8, 16, 32 and 48 and counts
10,752, 7,168, 7,168 and 7,168. The helpers are the 69,120 rows of the owner
table (144 calls × 480), with widths 4, 5, 7, 8 and 9 and counts
144 × (56, 32, 30, 122, 240). `ceiling_bound.py` derives both counts from the
package data and asserts them. Total capacity minus total width is 237,024, the
idle total of every legal map.

**Relaxation.** A *packing* assigns each helper to one bin so that the widths
in each bin sum to at most its capacity. Every legal owner map is a packing;
windows, the family rule (R4) and call distinctness are dropped. So everything
below holds for every legal map on this supplier.

**Theorem 1 (empty cap-48 bins).** Let `a(w) = ⌊7w/9⌋`, which gives
3, 3, 5, 6, 7 for widths 4, 5, 7, 8, 9, and `A(c) = ⌊7c/9⌋`, which gives
6, 12, 24, 37 for capacities 8, 16, 32, 48. For every multiset of widths with
sum at most `c`, `Σ a(w) ≤ A(c)`, because `Σ a(w) ≤ 7 Σ w / 9 ≤ 7c/9` and the
left side is an integer. (`ceiling_bound.py` also checks all 1,163 width
patterns.) Define the slack of a bin as `A(c) − Σ a(w)` over its helpers. It is
non-negative, and the slacks of all bins sum to

```
Σ_bins A(c) − Σ_helpers a(w) = 587,776 − 406,944 = 180,832
```

for every packing. An empty cap-48 bin has slack 37, so
`37 · #(empty cap-48 bins) ≤ 180,832 = 37 · 4,887 + 13`: **at most 4,887 cap-48
bins can be empty.** The selected map has 4,866, this map 4,880.

**Theorem 3 (surrogate).** A bin with slack 0 has free capacity at most 1
(`9 A(c) ≤ 7(c − f)` gives `f ≤ (7c mod 9)/7 < 9/7`), so it contributes
`g = 0`. Let `H(s)` be the largest `g(free)` over bins (capacity and width
pattern) with slack `s`. Then `E ≤ Σ_bins H(s_b)` with `Σ s_b = 180,832`, so `E`
is at most the optimum of an unbounded knapsack: choose a multiset of slacks
summing to 180,832 and maximise the sum of `H`. The empty cap-48 bin (slack 37,
`g(48)`) has the best ratio. Every other bin has `g(free)/slack ≤ g(44)/34`
(a cap-48 bin holding one width-4 helper), and `g(44)/34 < g(48)/37`. Let `n`
be the number of empty cap-48 bins.

- For `n ≤ 4,874`, `E ≤ n g(48) + (g(44)/34)(180,832 − 37n)`. This is
  increasing in `n` and at `n = 4,874` it is below `4,887 g(48) + g(17)`.
- For `4,875 ≤ n ≤ 4,887`, an exact dynamic programme over the remaining slack
  (at most 457) gives the best value. It is attained at `n = 4,887` with
  remaining slack 13, which a single cap-48 bin with free 17 fills (widths
  9 + 9 + 9 + 4: weight 24, slack 13).

So **`E ≤ 4,887 g(48) + g(17) = 908,139.013`** for every legal map. All
comparisons are exact: `exp` of a sum of `g` values is a product of integers
`f^f`, so the checker compares integers. A float knapsack over the full slack
range is computed as a cross-check and agrees. This map has `E = 907,271.883`
(867.1 below the bound); the selected map has 905,526.558.

**Theorem 2 (LP dual; weaker, for reference).** With `λ = (36/37) ln 48`, the
weights `v(4) = v(5) = 4λ`, `v(7) = (20/3)λ`, `v(8) = 8λ`, `v(9) = (28/3)λ`,
`μ(c) = cλ` for `c < 48` and `μ(48) = 48 ln 48` satisfy
`g(free) ≤ μ(c) − Σ v(w)` for every pattern. The checker verifies this exactly
as `f^(qf) ≤ 48^p`. Summing gives `E ≤ (8,679,936/37) ln 48 = 908,156.136`,
17.1 above Theorem 3.

**Windows and R4 do not tighten it (solver-reported).** In the search session,
the class-level window LP and the window + aggregate-R4 IP (`search/winlp.py`)
reached the same aggregate optimum: CP-SAT found a class-level solution with
idle profile `{1:2431, 17:1, 48:4887}`, which attains Theorem 3. This is a
solver result on a relaxation; it is not checked here, and a class-level
solution need not be realisable on concrete bins.

**The 2,392 one-free bins are not waste.** All of this map's residual-1 bins
are cap-32 bins with the pattern 9 + 9 + 9 + 4. That pattern has slack 0 under
the 7/9 weights, so these bins cost nothing in Theorem 1. The bound-attaining
profile has 2,431 of them.

**What this does and does not bound.** Theorems 1 and 3 bound the number of
empty cap-48 bins and the surrogate `E`. They do not bound κ: κ depends on the
whole idle profile through the exact engines, and `E` is only approximately
linear in κ. As an indication only, pricing the bound-attaining idle multiset
`{1:2431, 17:1, 48:4887}` with the package's pinned engines (`check.py`, recorded
as `indicative_ceiling_price` in `CHECK.json`) gives κ 0.001674088611862992
(complex lower endpoint 0.0016768959, 9.82% of the complex endpoint gap). This
map is 4.744e-7 below that. Nothing here proves that no legal map prices
higher. That would need, for example, the bound-attaining multiset to majorize
every attainable idle vector, which is not shown.

## What is not claimed

There is no optimality claim: the κ search is a finite heuristic (global
repack plus LNS, including the evacuation neighbourhood, then class-level
re-solves with guided realisation) that was still finding gains when it was
stopped, and the min-diff step is a finite MIP/LNS whose
relocation count is not proven minimal over all maps with this profile. The
majorization argument shows only that this map is strictly cheaper than the
selected one; the packing ceiling above bounds the surrogate and the number of
empty cap-48 bins, not κ, and it is not known to be attainable. There is no
new supplier, interface or mechanism. There is no fresh cold rebuild of the
native ancestry, and no unconditional theorem. All PR1094 inherited
assumptions remain.

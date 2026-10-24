# Ordinary interchange threshold at the reservoir width

**Scoped exact computation with a written all-width argument. No new κ.**
The selected conditional exponent stays 60403/20000000. This does not
accept PR #4100.

## Result

BIT.md §4 runs the elementary digit-swap algorithm when `2k ≥ e` or the
body width is below 64. Here `e` is the q-ary field width, `q = 2^89 − 1`,
and `k` is the least integer with `q^k ≥ K(w)^{D(e)}`. Evaluated exactly,
this test gives:

1. **Exact threshold.** The elementary branch runs exactly for q-ary widths
   `e ≤ 311308`. Every width `e ≥ 311309` takes the recursive branch.
   In binary, an `h`-bit field reaches the recursive branch exactly when
   `h ≥ 27706412`.
2. **Every #4174 reservoir up to 2.77 · 10^9 bits is elementary.** Since
   `r_max = floor(L/(100G))`, `H = r_max G ≤ L/100`. A recursive H-bit
   interchange therefore needs `L ≥ 2770641200`. The production plan
   `p = 9240576`, `ell = 24` has `L = 1540096`, which is 1,799 times too
   short. Its `H = 15360` bits is 173 q-digits. The smallest layout with
   `L ≤ p` from #4938 (`p = 1310720`, `ell = 21`) has `H = 10752`, which
   is 121 q-digits. Both are elementary.
3. **What this means for #4938's question.** One ordinary H-bit interchange
   does fit `O(V H^{1−a} + V)`, because BIT.md's statement is uniform and
   its finitely many elementary widths are absorbed into the constant. On
   every elementary width, `E^{a2} < 2^{19 a2} < 2^{0.033}`, so the absorption
   costs at most that factor over the elementary constant. At the actual
   #4174 width, however, the factor `H^{−a}` is not realized. The callee does
   elementary swaps, so there is no width saving.

## Argument

Fix `w`. BIT.md takes `w = ceil(e^c)` with `c = 8667/5000000`, so
`w = 2` exactly for `2 ≤ e ≤ 2^{1/c}`, and `1/c > 576`. Width `e = 1` is
elementary trivially.

*Stock digits.* Write `β = 269241600 N` with `N = |GL_64(F_q)|`. The
verifier checks `q^4096 < β < q^4097` exactly. At `w = 2`,
`K^D = q^{4096D} β^D`, so `k = 4096 D + j(D)`, where `j(D)` is the least
`j` with `q^j ≥ β^D`. Then `4096 D < j(D) ≤ 4097 D`, and `k ≤ 8193 D`.
The verifier computes `j(D)` exactly for `D ≤ 20`. In particular
`k = 155654` at `D = 19`, so `2k = 311308`.

*Depth blocks.* The map `n ↦ 42 floor(n/64)` is nondecreasing, so `D` is
nondecreasing by induction. `D(e) = D` therefore holds exactly on the block
`[m_D, m_{D+1})`, with `m_1 = 64` and `m_{D+1} = 64 ceil(m_D/42)`. Since
`k` depends on `e` only through `D(e)` at fixed `w`, the elementary set in
each block is an initial segment, ending at `max(2k_D, k_D + 127)`.

*Below the D = 20 block.* The verifier checks every width
`2 ≤ e < m_20` against the literal test. The result is elementary exactly
for `e ≤ 311308`. That boundary lies inside the `D = 19` block.

*From D = 20 up to 2^576.* For each block start `m_D ≤ 2^576` with
`D ≥ 20`, the verifier checks `2 · 8193 D < m_D` and
`(m_D − 8193 D)/2 ≥ 64`. By the block property, each whole block is then
recursive. There are finitely many such blocks, and all of them are
checked.

*Beyond 2^576 (`w ≥ 3`).* Put `x = log2 e ≥ 576`. Then
`w ≤ e^c + 1 ≤ 2^{cx+1}`. Each depth step multiplies by at most `21/32`,
so `D ≤ 1 + 1.65 x`. Also `k ≤ (4096 w + 1) D + D`. Together these give
`2k < 2^{17 + cx + log2 x}`, and at `x = 576` the exponent is below
`575 < x − 1`. The gap `x − cx − log2 x` increases for `x ≥ 2`, so
`2k < e/2` for all larger `e`. The body width `(e − k)/w ≥ e/2^{cx+2}` is
far above 64. This range lies far outside any physical width and is
included only so that the threshold statement covers all `e`.

*Binary widths.* BIT.md embeds `2^h` into `q^E`, with `E` least such that
`q^E ≥ 2^h`. Then `E ≤ 311308` exactly when `2^h ≤ q^311308`. The bit
length of `q^311308` is 27706412, so the recursive branch starts at
`h = 27706412`.

*Both stages.* The test depends only on `e`, `w` and the fixed stock, and
not on the preceding saving `a`. The `a = 0 → a1` and `a1 → a2` wrappers
therefore share this threshold.

## Scope

Card `uniform-transfer-audit`, scope **refined** to the callee's branch at
the reservoir width (see `TASK.json`). This package follows BIT.md §4 as
written: the stock is `K(w)^{D(e)}` on the original radix width, and the
body width is `n = floor((e − k)/w)`.

The following are not covered: the constants `C` and `c_el` (BIT.md gives
neither), the three-field placement (#4174 proves it), the guard scan, the
sparse repair, and any statement about the complete CRT or multiplication
theorem. The threshold is a fact about the callee as written. A smaller
stock or a different wrapper test would move it.

Base: canonical main `cef4b52f2a59009865bf8eabde1be3f159063703`,
priority revision 7, fetched 2026-10-23T03:05Z. `find_overlap.py`, the PR
search for "interchange" and the handoff thread found no open claim on this
threshold. That is a search result, not a novelty proof. Claim:
[#1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19136868).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/crt-interchange-width-threshold/verify.py
python3.12 -B scripts/research_package.py --package research/crt-interchange-width-threshold
```

The direct command prints `PASS_CRT_INTERCHANGE_WIDTH_THRESHOLD` in about
20 seconds. Most of that time goes to the exact `β^D` comparisons. Changing
the q-ary boundary to 311309, the binary boundary to 27706411 or the
production q-width to 172 makes the verifier fail.

## Open next questions

1. **At what reservoir length does the composed CRT bill first beat the
   elementary-callee bill?** Below `L = 2770641200` every reservoir exchange
   is elementary. Any CRT-layer saving in that range has to come from some
   other source. *First step:* write the per-layer cost as `c_el V H`
   (elementary) and `C V H^{1−a2}` (recursive), then solve for the smallest
   #4174 layout at a stated ratio `C/c_el`. *Blocked by:* BIT.md states
   neither constant, so the answer is conditional on the stated ratio.

## Credit

Cinna Davis, PR #4100, for the CRT construction, BIT.md and its wrapper
test. Hiroki KUMAZAKI (@kumagi), PR #4174, for the constructor and the
production plan. JoyboyBrian, PR #4938, for the evaluator binding and the
open question. PR2195, PR2234, PR2753/2809, PR2899 and PR2915 for the
retained interchange assembly lineage credited in BIT.md.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review and no formal-kernel
acceptance are claimed.

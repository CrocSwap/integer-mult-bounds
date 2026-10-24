# The #4174 reservoir exchange against the ordinary-interchange bill

**Scoped counting proof, conditional on BIT.md's ordinary interchange as
stated. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

Pending PR #4938 asked whether one ordinary H-bit interchange of
`research/unconditional-batched-crt/CRT.md` §3–§4 fits its bill
`O(V H^{1-a} + V)` at the actual #4174 width `H = r_max G`. The callee is
BIT.md's machine. It "exchanges two complete equal e-bit binary address
fields, with arbitrary complete preceding, intervening and following
fields" in `O(V e^(1-a2))`, through a wrapper that falls back to
elementary q-digit swaps (`q = 2^89 - 1`) at small widths.

**Relation to #4942.** James Reed's PR #4942 (pending, head
`32fa3600a0e739d47dca98fdeb3abceda073f9f2`) was claimed a minute before this
package. It already evaluates BIT.md §4's wrapper branch at the reservoir
width: elementary exactly for q-ary `E <= 311308` (binary `h < 27706412`),
`D = 19`, `k = 155654`, `E = 121` at `H = 10752` and `E = 173` at
`H = 15360`. It also proves that every larger width is recursive. **#4942 is
the predecessor for parts (iii)–(iv) below.** This package recomputed them
independently and agrees; it claims no novelty for the threshold.

**New here:** parts (i)–(ii), the write-up of one `Plan.placement` as
ordinary calls and the count of placement and restoration calls with the
resulting 6x bill. Also new: the padding ranges (v) and the
`D`-independent bound of Remark 4.

[PROOF.md](PROOF.md) proves the following for every layout accepted by the
#4174 constructor, with `a = a2`.

| Part | Statement |
|---|---|
| (i) | One `Plan.placement` (three sources to front `u`, front `t`, back `b`) is three ordinary calls of width exactly `H`, in any order. Restoration is the same three calls. That is six calls per batch, and every dirty record is restored. |
| (ii) | Given BIT.md's theorem, these cost at most `6 C_BIT V H^{1-a} + 6 c_own V`, which is CRT.md's bill with multiplicity 6. |
| (iii) | *Recomputation of #4942.* BIT.md's wrapper runs at radix width `E = floor(H/89) + 1`. It is elementary for every `H < 27,706,412` and body at `H = 27,706,412` (`E = 311309`, `D = 19`, `k = 155654`). Since `H <= L/100`, every layout with `L < 2,770,641,200` runs all six calls, and all twelve §4 shuttles, on the elementary branch. |
| (iv) | *Agrees with #4942's `E^{a2} < 2^{0.033}`.* On that range `E <= H^{1-a}`, so the elementary stage alone meets the bill, with constant `C_0 q^2`. Also `H^{a} < 2^{1/20}`, so the `a2` saving is numerically absent. |
| (v) | The literal call pads the volume by `(q^E/2^H)^2`. This is in `(2^{33}, 2^{34})` at the minimal layout and `(2^{73}, 2^{74})` at production. |

At the minimal layout `p = 1310720`, `ell = 21`, `d = 2^16`, widths 20
(`G = 2688`, `r_max = 4`, `H = 10752`), we get `E = 121`, `w = 2`,
`D = 1` and `k = 8193`. Since `2k >= E`, every call is elementary. The
production layout `p = 9240576`, `ell = 24` (`H = 15360`) gives
`E = 173`, `D = 2`, `k = 16385`, also elementary. These values agree with
#4942. As an extra check of this package, the two layout results do not
depend on the exact `D`: any `D >= 1` makes `H <= 1,458,353` elementary.

**Answer.** Yes, the bill fits, with multiplicity 6. At these widths it
is met by BIT.md's elementary fallback, not by its body word, as #4942
also finds. The constant
includes a real padding factor of up to `2^{34}` (minimal) or `2^{74}`
(production) per call.

Not proved: BIT.md's theorem itself (used as stated; #4100 AUDIT.md
records that its physical suites are not all passing), the stage-0
constant and embedding on fixed tapes, the rest of the §4 gadget, and the
reading of `D(e)` at radix width `E`. Remark 4 of the proof covers the
last for both layouts.

## Evidence

[verify.py](verify.py) authenticates its four input pins and the quoted
source phrases. It then executes the #4174 allocator bytes it has just
authenticated, and checks the following:

- **A.** Two `Placement` fixtures with dirty payloads (4,096 and 16,384
  addresses). Three literal field-exchange calls realize `P` in all six
  orders, and the same three calls restore every record.
- **B.** All 131,072 minimal-layout plans (786,432 calls) and all 104,864
  production plans (629,184 calls). Each has three disjoint width-`H`
  pairs inside the reservoir, sources omitted by every dependency, and the
  `u`, `t`, `b` destinations.
- **C.** An independent recomputation of #4942's branch values: the exact bounds `1 - 2/q < N/q^4096 < 1` with `N = |GL_64(F_q)|`,
  the `j(D)` table, the wrapper branch at every `E <= 311309`, the radix
  lemma, and the `H*` and robust edges.
- **D, E.** The inequality `E <= H^{1-a}` and both padding ranges.
- **Controls.** Thirteen rejection controls: a dropped restoration call,
  a bit-reversing exchange, an overlapping source, the body branch one
  digit or one bit early, the stock without `269241600 N`, `D(173) = 1`,
  `N >= q^4096`, `j(D)` dropped, and both padding floors. Each must fail.

Ten source mutations of sharp claims (for example `E_MIN`, `H_MIN`, the
`j` table, the radix formula, the call count and the padding range) all
make the verifier fail. The finite checks corroborate the written proof;
they do not replace it.

## Scope

Card `uniform-transfer-audit`, scope **refined** to the reservoir
placement's ordinary-callee bill. Canonical main fetched 2026-10-23 at
`cef4b52f2a59009865bf8eabde1be3f159063703`, priority revision 7. Source
pins are in [SOURCES.json](SOURCES.json). This answers open question 1
of pending #4938 together with #4942, and the reservoir remainder of open
question 2 in #4377 and #4650.

**Overlap.** James Reed's CLAIM for #4942 (discussion #1166, comment
19136868) and this package's CLAIM (comment 19136883) crossed one minute
apart. #4942 covers the wrapper branch and states that the three-field
placement is not covered. This package therefore cites #4942 for the branch
and contributes the placement call count.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/crt-reservoir-interchange-bill --check-only
python3.12 -B scripts/research_package.py --package research/crt-reservoir-interchange-bill
```

The direct command `python3.12 -B research/crt-reservoir-interchange-bill/verify.py`
prints `PASS_CRT_RESERVOIR_INTERCHANGE_BILL` in about 8 seconds.

## Open next questions

The [structured list](TASK.json) has the same entries.

1. **Does a direct binary exchange of `H` single-bit swaps meet the same
   bill on fixed tapes without the `(q^E/2^H)^2` padding?**
   - *Why it matters:* at the actual widths the literal BIT.md call pays
     up to `2^{34}` (minimal) or `2^{74}` (production) extra volume per
     call, and the `a2` saving is absent anyway.
   - *First step:* write one bit swap at positions `i < j` as one fixed-tape
     pass with a bounded buffer, and count its tape actions per record.
   - *Blocked by:* nothing. It needs a tape model, not new mathematics.
2. **What is the stage-0 constant `C_0` of BIT.md's elementary q-digit
   swap?**
   - *Why it matters:* by (iii)–(iv) it is the whole callee constant at
     every CRT layout with `L < 2.77 × 10^9`.
   - *First step:* bound one q-digit transposition of two radix-q fields
     with intervening fields on a fixed tape inventory.
   - *Blocked by:* BIT.md does not state the elementary algorithm in
     detail.

## Credit

Cinna Davis, PR #4100, for the CRT construction, BIT.md's ordinary
interchange and its wrapper. Hiroki KUMAZAKI (@kumagi), PR #4174, for the
reservoir constructor, the disjoint-exchange geometry and the six-exchange
invoice. unpaidmoon, PRs #4377 and #4650, for the evaluator bills and the
open question 2 this continues. Nick Petalas, PR #4845, for the full-batch
arena bill.
James Reed (jwr404), PR #4942 (pending), for the wrapper-branch threshold
and the `E`/`k` values at both layouts, recomputed here. PR #4938
(JoyboyBrian, pending) for the layout binding and the question answered
here.

Prepared by JoyboyBrian with substantial Anthropic Claude (Claude Code,
Opus 5.5) assistance. Apache-2.0. No independent human review and no
formal-kernel acceptance are claimed.

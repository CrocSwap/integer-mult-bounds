# Crossover length for the recursive ordinary interchange in the CRT reservoir

**Scoped proof with exact computation, conditional on a stated constant
ratio. No new κ.** The selected conditional result is unchanged. This does not
accept PR #4100 or BIT.md's theorem.

## Question

PR #4942 (`research/crt-interchange-width-threshold`, James Reed) shows that
BIT.md §4 takes its recursive branch exactly from binary width
`H_b = 27706412`, so every #4174 reservoir with `L < 2770641200` is
elementary. Its open question 1 asks: at what reservoir length does the
recursive bill `C V H^(1-a2)` first beat the elementary bill `c_el V H`, for a
stated ratio `rho = C/c_el`? BIT.md fixes `c = 8667/5000000` and
`a2 = c(1-c^2)`, an exact rational.

## Result

Write `rho_c = H_b^a2`. Then:

1. **Crossover width.** For every `rho > 0`, the least reservoir width at which
   the recursive branch runs and its bill is strictly below the elementary bill
   is

   `H*(rho) = max(H_b, h(rho))`, where `h(rho)` is the least integer with `h^a2 > rho`.

   So `H*(rho) = H_b` exactly when `rho < rho_c`, and `H*(rho) = h(rho)`,
   about `rho^(1/a2) ≈ rho^576.9`, when `rho >= rho_c`.
2. **Critical ratio.** `rho_c = 1.030151098331576173576873168658...`
   (30 digits certified). At the branch threshold the `H^(-a2)` factor is
   worth only 3.02%. Any recursive constant more than 3.02% above the
   elementary constant moves the crossover beyond the branch threshold.
3. **Exact least length at the branch threshold.** Over every layout the #4174
   constructor accepts (power-of-two `d >= 51200`, `2 <= m <= ell` with
   `m = ceil(log2(p+2))`, widths `w_i in {ell-1, ell}`, `G = 64(ell+m)`,
   `r_max = floor(L/(100G))`, `H = r_max G`), the least `L` with
   `H >= H_b` is **`L = 2770643200`**. One witness is `d = 2^28`, `ell = 11`,
   `m = 2` (`p = 1` or `2`), `G = 832`, `r_max = 33301`, `H = 27706432`.
   This sharpens PR4942's lower bound `100 H_b = 2770641200` by 2000 and is
   the answer for every `rho < rho_c`.
4. **Ratio-bound examples.** The least lengths are exact for
   `rho = 1.031` (`H* = 44561394`, `L = 4456140800`) and
   `rho = 1.032` (`H* = 77956662`, `L = 7795667200`). For larger ratios the
   verifier certifies `H*` exactly and reports the lower bound `L >= 100 H*`:

   | rho | H* | bits of H* |
   |---|---|---|
   | 1.05 | 1675568503989 | 41 |
   | 1.1 | 757789515901820833519268 | 80 |
   | 1.5 | exact integer, not printed | 338 |
   | 2 | exact integer, not printed | 577 |
   | 4 | exact integer, not printed | 1154 |
   | 10 | exact integer, not printed | 1917 |

   With `rho = 2` a profitable recursive call needs a reservoir of more than
   `100 · 2^576` bits.

## Argument

Fix `rho > 0`. Below `H_b` the wrapper runs the elementary branch (PR4942,
used as stated), so no recursive bill applies. For `H >= H_b`,
`C V H^(1-a2) < c_el V H` is equivalent to `H^a2 > rho`, because `V, H > 0`.
The map `H ↦ H^a2` is strictly increasing, so the set of widths satisfying both
conditions is `{H >= max(H_b, h(rho))}`. Also `H_b^a2 > rho` exactly when
`rho < rho_c`, which gives the regime split.

For the length, `H = floor(L/(100G)) G` is nondecreasing in `L` at fixed
`(d, ell, m)`. At fixed `k = ell + m` (so `G = 64k`), the least `L` with
`H >= H*` is `t = 100 G ceil(H*/G)`, provided `t` lies in some
`[d(ell-1), d ell]` with admissible `ell in [ceil(k/2), k-2]` and `d = 2^s >= 2^16`.
Every integer in that interval is reachable by choosing how many widths equal
`ell`. If no admissible interval contains `t`, the least reachable value
above `t` is `d(ceil(k/2)-1)` for the smallest qualifying `d`. Since
`t >= 6400k`, the scan over `k` stops once `6400k` exceeds the best value
found. Every feasible `(s, ell, m)` is therefore covered.

## Evidence

`verify.py` uses only the standard library and checks these points:

- Two logarithm engines decide `h(rho)`. Engine 1 is a rigorous fixed-point
  interval logarithm (atanh series with directed rounding and an explicit tail
  bound), in integer arithmetic only. Engine 2 uses Python's correctly rounded
  `decimal` `ln`/`exp` to propose `h`. Engine 1 then certifies both
  `h^a2 > rho` and `(h-1)^a2 < rho`. An unresolved interval aborts.
- The 30-digit bracket of `rho_c` is certified by engine 1 at both endpoints.
  Just below `rho_c` the width is `H_b`, and just above it the width is `H_b+1`.
- The pruned layout search is compared with a complete brute scan over
  `(s, ell, m)` on five fixtures (`H = 10752, 15360, 27706, 100000, 123457`).
  The verifier also checks that the brute ranges are large enough for each
  fixture. Every reported witness is checked against the domain.
- Five rejection controls: `L-1` at the witness, `m = 1`, `d = 2^15`, a ratio
  just above `rho_c` at `H_b`, and a nonpositive ratio.
- The BIT.md constants and the four placement-domain phrases are read from the
  pinned inputs. A fresh `RESULT.json` is compared byte for byte.

The registered check runs in about 1.5 seconds.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3.12 -B research/crt-recursive-interchange-crossover/verify.py
python3.12 -B scripts/research_package.py --package research/crt-recursive-interchange-crossover
```

Expected:
`PASS_CRT_RECURSIVE_INTERCHANGE_CROSSOVER rho_c=1.030151098331576173576873168658 least_L_at_branch=2770643200 ...`

## Limitations

- Conditional on BIT.md's bill as stated and on PR4942's branch threshold. Both
  are cited, not re-proved. BIT.md gives neither `C` nor `c_el`.
- The comparison uses the per-layer bills only. It omits the 6x placement
  multiplicity and the `(q^E/2^H)^2` padding from PR4944. A common factor
  cancels, but padding that differs between branches would change `rho`.
- Exact least lengths are computed only when `H* <= 10^9`. Above that, only
  `L >= 100 H*` is reported.
- No statement about the complete CRT bill, supplier admission or any
  multiplication theorem.

## Open next questions

1. **What are `C` and `c_el`?** Once `rho` exceeds 1.0302, the crossover
   grows like `rho^577`. A definite ratio, including padding, decides whether
   any physical reservoir uses the recursive branch profitably. First step:
   bound `c_el` from the elementary q-digit swap and `C` from the body word at
   `w = 2`, `D = 19`. BIT.md states neither constant.
2. **Exact lengths for larger `H*`.** Replace the linear `k` scan with a
   divisor search near `64 ceil(H*/64)` under the `d >= 65536` constraint.
   That would give exact least lengths for `rho` in `(1.032, 1.05]` and beyond.

## Credit

Builds on James Reed's PR #4942 (branch threshold and the open question),
JoyboyBrian's PR #4944 (six-call reservoir bill and padding), Hiroki KUMAZAKI's
PR #4174 (constructor and layout domain) and Cinna Davis's PR #4100 (CRT
construction and BIT.md). The crossover analysis, critical ratio, layout
search and verifier were produced by Nick Petalas. Apache-2.0. Independent
human and formal proof-kernel review are unclaimed.

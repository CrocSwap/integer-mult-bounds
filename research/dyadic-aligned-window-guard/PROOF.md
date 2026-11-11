# Exact admission of dyadic aligned target windows

Produced by Nick Petalas. **Scoped proof with an exact finite check. No new κ,
no supplier admission, no change to the selected frontier.** Apache-2.0.

## 0. What is cited and what is new

CubeJerry's merged [PR #6972](https://github.com/CrocSwap/integer-mult-bounds/pull/6972)
(`research/core-production-nonempty`) supplies, and this document **cites without
replaying**:

* the source rule `q(j) = j + floor(e j / S + 1/2)`, `N = S + e`, with the other
  target coordinates identity holes;
* its Section 3: for an integer width `W >= 1`, the unchanged capped carve has a
  nonempty interior in a target window **iff** the longest selected run `M` of that
  window exceeds `6W`;
* its Section 4 guard (6): `S >= e(6W+1)` and `L >= 12W+2` give `M > 6W` in every
  ordinary window of length `L`, with one-unit adverse families for arbitrary
  integer windows. It leaves open whether a sharper guard exists for dyadic aligned
  sections (`N`, `L` powers of two, every window starting at a multiple of `L`).

New here: an exact classification of the dyadic aligned family, and the answer to
that question. A window with `M > 6W` is called **good**, otherwise **bad**.

**Hypothesis (G).** `S >= e(6W+1)`, equivalently `N >= e(6W+2)`. It implies
`S >= 7e >= 2e` and `floor(S/e) >= 6W+1`.

**Dyadic notation.** `N = 2^n`, `L = 2^l` with `0 <= l <= n`, aligned windows
`[kL, (k+1)L)`. Write `e = 2^j t` with `t` odd; then `j < n`, and put `g = 2^(n-j)`.

## 1. Holes and runs

**Lemma 1.** If `S >= 2e`, the unselected coordinates ("holes") are exactly
`H_c = ceil(S(2c-1)/(2e)) + c - 1 = floor(((2c-1)N + e - 1)/(2e))`, `1 <= c <= e`.
Consecutive holes differ by `floor(N/e)` or `ceil(N/e)`, so the selected cell between
two consecutive holes has length `floor(S/e)` or `ceil(S/e)`.

*Proof.* Put `phi(j) = floor(e j/S + 1/2)`. Then `phi(j) >= c` iff `j >= A_c :=
ceil(S(2c-1)/(2e))`, `phi(0) = 0`, and `phi` rises by at most 1 per step because
`e < S`. So `q` is strictly increasing with steps 1 or 2, and a step of 2 occurs
exactly into `j = A_c`, skipping `q(A_c - 1) + 1 = A_c + c - 1`. The index `A_e`
is at most `S - 1` iff `S >= 2e`, which gives `q(S-1) = N - 1`; with `q(0) = 0` there
are no holes before the first or after the last selected coordinate. This gives the
`e` holes `H_c = A_c + c - 1`. Since `2(c-1) = u - 1` for `u = 2c-1`,
`H_c = ceil((uS + e(u-1))/(2e)) = ceil((uN - e)/(2e)) = floor((uN + e - 1)/(2e))`.
Finally `A_(c+1) - A_c = ceil(x + S/e) - ceil(x) in {floor(S/e), ceil(S/e)}`. ∎

**Lemma 2.** Let a window of length `L` inside `[0,N)` contain `r` holes at offsets
`p_1 < ... < p_r`. If `r = 0` then `M = L`. Otherwise `M` is the largest of
`p_1`, `p_(i+1) - p_i - 1`, and `L - 1 - p_r`. Under (G): `r >= 2` implies
`M >= floor(S/e) >= 6W+1`; `r = 1` gives `M = max(p, L-1-p)`.

*Proof.* The selected coordinates of the window are its non-holes, and `M` is the
longest stretch between consecutive marks (window ends and holes). Two consecutive
holes enclose a whole cell of length at least `floor(S/e)` (Lemma 1). ∎

## 2. The single-hole band

**Theorem 1.** Assume (G) and a window of length `L >= 6W+1`. Let
`B = [L-1-6W, 6W]` (empty when `L >= 12W+2`). The window is bad iff it contains a hole
whose offset lies in `B`. If `L <= 6W`, every window is bad.

*Proof.* If `L <= 6W` then `M <= L <= 6W`. Let `L >= 6W+1`. If the window is bad then
`r = 0` is impossible (`M = L`), and `r >= 2` is impossible (Lemma 2), so `r = 1`, and
`max(p, L-1-p) <= 6W` says `p in B`. Conversely let a hole sit at offset `p in B`. A
second hole in the window would be at distance at least `floor(N/e) = floor(S/e)+1 >=
6W+2` from the first. Above it, its offset would be at least `(L-1-6W) + 6W + 2 = L+1`;
below it, at most `6W - (6W+2) = -2`. Both are outside the window, so `r = 1` and
`M = max(p, L-1-p) <= 6W`. ∎

**Corollary 1.** Under (G) and `L >= 6W+1`, all aligned windows of length `L` are good
iff no hole `H_c` satisfies `H_c mod L in B`. (Hole `H_c` lies in the aligned window
`k = floor(H_c / L)` at offset `H_c mod L`.) For `L >= 12W+2` the band is empty and every
aligned window is good, which is #6972's length condition for dyadic sections.

## 3. Periodicity of the hole pattern

**Lemma P.** For `e = 2^j t` with `t` odd and `N = 2^n`, put `g = N/2^j`. Then
`H_(c+t) = H_c + g` for `1 <= c <= e - t`. Under (G), `H_t < g`, so block
`[ig, (i+1)g)` contains exactly the `t` holes `H_(it+1), ..., H_((i+1)t)`, the same
pattern in every block.

*Proof.* With `u = 2c-1`, `N = 2^j g`, `e = 2^j t`:
`(uN + e - 1)/(2e) = (ug + t - 2^(-j))/(2t)`. For an integer `m` and `0 < d <= 1`,
`floor((m - d)/(2t)) = floor((m-1)/(2t))`, because no multiple of `2t` lies in
`(m-1, m)`. Hence `H_c = floor((ug + t - 1)/(2t))`. Replacing `u` by `u + 2t` (that is,
`c` by `c + t`) adds `g`. Also `H_t < g` iff `(2t-1)g + t - 1 < 2tg` iff `t - 1 < g`,
which holds because (G) gives `g >= t(6W+2)`. ∎

## 4. The classification

**Theorem 2.** Let `N = 2^n`, `1 <= e < N`, `e = 2^j t` with `t` odd, `L = 2^l` with
`0 <= l <= n`, `W >= 1`, and assume (G). All aligned windows of length `L` are good if
and only if

* **(I)** `l >= n - j + 1`; or
* **(II)** `l = n - j`, and (`t >= 3` or `L >= 12W+2`); or
* **(III)** `l <= n - j - 1`, and `(t+1) L > t (12W+3)`.

*Proof.* **(I)** `L >= 2g`: an aligned window is a union of `L/g >= 2` blocks, so it
holds at least `2t >= 2` holes and is good by Lemma 2.

**(II)** `L = g`: the aligned windows are the blocks. If `t >= 3` each holds at least
three holes: good. If `t = 1` each holds the single hole `H_1 = floor(g/2) = L/2` at
offset `L/2`, so `M = L/2`, good iff `L >= 12W+2`.

**(III)** `L` divides `g/2`, so the aligned windows split each block into `g/L >= 2`
windows, and the offsets of all holes modulo `L` are those of block 0:
`R = {H_c mod L : 1 <= c <= t}`. Write `g = 2Lm` with `m = 2^(n-j-l-1)` and `u = 2c-1`.
By Lemma P, `H_c = floor(Lmu/t + (t-1)/(2t))`. Writing `mu = tq + rho` with
`0 <= rho < t`, `H_c = Lq + floor(L rho/t + (t-1)/(2t))`, and for `t` odd
`floor(L rho/t + (t-1)/(2t))` is the nearest integer `nu(rho)` to `L rho/t`: with
`L rho = kt + s` it equals `k + [2s >= t+1]`, and `s = t/2` cannot occur. As `c` runs
over `1..t`, `u = 2c-1` runs over all residues modulo `t` (2 is a unit), hence so does
`rho = mu mod t` (`m` is a power of 2, a unit). Therefore
`R = { nu(rho) mod L : 0 <= rho < t }`.
Because `nu(t - rho) = L - nu(rho)` (no ties), `R` is symmetric under `r -> L - r`.

Now apply Corollary 1.

* `L <= 6W`: every window is bad, and the inequality `(t+1)L > t(12W+3)` fails, since
  `(t+1)L <= 6W(t+1) <= t(12W+3)`.
* `L >= 12W+2`: every window is good by Corollary 1. A power of two is even and `12W+2`
  is not a power of two for `W >= 1`, so `L >= 12W+4` and
  `(t+1)L >= (t+1)(12W+4) > t(12W+3)`.
* `6W+1 <= L <= 12W` (a power of two is not `12W+1`, which is odd, nor `6W+1`): put
  `nu_max = nu((t-1)/2)`, the largest `nu(rho)` with `rho <= (t-1)/2`; all of them are at
  most `L/2 <= 6W`. A lower-half residue `r = nu(rho)` lies in `B` iff `r >= L-1-6W`
  (its upper end `6W` is automatic). An upper-half residue `r = L - s`, `s = nu(rho)`
  with `1 <= s <= L/2`, lies in `B` iff `L-6W <= s <= 6W+1`, that is iff `s >= L-6W`,
  which implies `s >= L-1-6W`. Hence `R` meets `B` iff `nu_max >= L-1-6W`. Now
  `L - nu_max = D` := the nearest integer to `L(t+1)/(2t)`, so `R` meets `B` iff
  `D <= 6W+1`. All windows are therefore good iff `D >= 6W+2` iff
  `L(t+1)/(2t) > 6W + 3/2` (equality would force `t | L`, so `t = 1`, and then
  `L(t+1)/(2t) = L` is an integer) iff `(t+1)L > t(12W+3)`. ∎

**Corollary 2 (the guard for dyadic aligned windows).** Under (G): `L >= 12W+2` always
admits (so #6972's length condition holds on dyadic sections); for `e = 2^j` (`t = 1`)
with `l <= n-j-1`, `L >= 6W+2` is necessary and sufficient, half of the uniform length;
for `t >= 3` in case (III) the least admissible `L` is the least power of two with
`L > t(12W+3)/(t+1)`, which tends to `12W+3` as `t` grows. The odd part `t` of `e`
and `n - j` decide, not `S/e`.

## 5. The uniform length threshold cannot be lowered on dyadic sections

**Theorem 3.** For every `W >= 1` and every power of two `L <= 12W` there is a dyadic
instance satisfying (G) and `N - L >= W` in which every aligned window of length `L` is
bad. So no dyadic `L <= 12W` is admissible uniformly in `e`; the least admissible
dyadic length is the least power of two `>= 12W+2`, exactly the length condition of
#6972's guard.

*Proof.* If `L <= 6W`, any instance with (G) works (`M <= L <= 6W`), for example
`e = 1` and `N` a power of two with `N >= 6W+2`. A power of two is never `6W+1`. If
`6W+2 <= L <= 12W`, take `N = 8L`, `e = N/L = 8`: (G) holds because `L >= 6W+2`, and
`H_c = (2c-1)L/2` exactly, one hole at offset `L/2` in every window, so `M = L/2 <= 6W`
in all windows, with `N - L >= L >= W`. ∎ (This is case (II) with `t = 1`; the verifier
checks this family literally for `W <= 64`.)

**Remark (the two adverse families of #6972 are not dyadic).** The first has length
`L = 12W+1`, odd. The second has `N = 18W+5`, odd. In a dyadic instance `N` and `e(6W+2)`
are both even, so `S = e(6W+1) - 1` never occurs, and `S >= e(6W+1)` is the same as
`S >= e(6W+1) - 1`. Whether an aligned window can fail for a dyadic instance with
`floor(S/e) <= 6W` is not settled here (Open next questions).

## 6. What is not claimed

* The equivalence "interior nonempty iff `M > 6W`", the cap and width admissions, source
  accuracy, `N - L >= W` in applications, row gaps and every native, compiler or
  precision obligation are #6972's or remain open; none is touched.
* Everything here is under (G), i.e. `floor(S/e) >= 6W+1`. Instances with
  `floor(S/e) <= 6W` are outside; they are not shown to fail or to succeed.
* The proofs above are written by hand. The finite check (`verify.py`) corroborates them
  but is not a proof; no proof-kernel check was run and no independent human review is
  claimed.

# A 14-port Hall obstruction to rank-8 realisations of P104 (no κ)

**No new κ.** This package proves that, under a stated label pattern, the 104 ports of the #5561 word have no realisation of inner
dimension exactly `8k`, over any field. The obstruction is combinatorial: fourteen of the ports already have a Hall deficiency.

## Statement

**Hypothesis (complex label pattern).** Each port `T` carries a pair of `k × d` matrices `U_T, W_T` over a field `F` (`d` is the inner
dimension; `k >= 1` is the label dimension), and the pairing `B_ST = W_S U_T^T` (`k × k`) satisfies

* `B_ST = 0` for every pair `S != T` of ports with F2 dot product 0 (the "forced-zero" pairs, which are the E8-non-orthogonal pairs of
  the 104 ports; the ports are 9-bit odd-weight vectors and the rule is `popcount(p_S & p_T)` even);
* `B_TT` invertible for every port `T`.

`W != U` is allowed (asymmetric and Hermitian-type pairings are covered). The pattern is an assumption: it records how the pairing
of the labels of a complex-field construction is constrained at its frame contacts. It is not proved here for any word, and the
mask is not the one used for the real-valued completion in `research/p104-designer-toolkit-v2/P104-LEMMAS.md` (there the forced values are
on the pairs of F2 dot product 1).

**Theorem.** Under this hypothesis, for the ports of `research/p104-designer-toolkit-v2/words/5561.json.gz` (0-based indices), no
realisation has inner dimension `d = 8k`, over any field of any characteristic, for any `k >= 1`. For `k = 1`: the minimum rank is
at least 9 (`d = 8` is impossible, and `d < 8` is excluded by the 8-clique below).

**Scope.** Ranks `8k < d < 9k` (`k >= 2`) are *not* covered. Other masks are not covered. Nothing is priced.

## The obstruction

`K = {62, 63, 69, 74, 81, 86, 91, 99}` is a clique of the forced-zero graph (its clique number is 8, so `K` is maximal and no
9-clique exists). `O = {57, 67, 68, 95, 100, 101}`. Writing `A(T)` for the members of `K` that are *not* forced-zero to `T`:

| T | 57 | 67 | 68 | 95 | 100 | 101 |
|---|---|---|---|---|---|---|
| A(T) | {62, 91} | {63, 99} | {62, 99} | {62, 63} | {62, 69} | {63, 69} |

The union is `{62, 63, 69, 91, 99}` (five coordinates for six ports). Any two ports of `O` with a common coordinate are forced zero
and have exactly one common coordinate (11 such pairs). `check.py` verifies all of this from the ports.

## Proof

Let `d = 8k` and suppose a realisation exists.

1. **Gauge.** `K` is a forced-zero clique, so `B_KK` is block diagonal with invertible diagonal blocks and has rank `8k`. As
   `B_KK = W_K U_K^T` with `W_K, U_K` of size `8k × d = 8k × 8k`, both are invertible. Replace `U` by `U g`, `W` by `W h` with
   `g = U_K^{-1}` and `h = g^{-T}`; the pairing is unchanged and now `U_K = I`, `W_K = B_KK`. Multiplying the block rows of `W_k`
   (`k ∈ K`) on the left by `B_kk^{-1}` changes only block row `k` of `B` by an invertible left factor, which preserves every
   zero block and every invertible diagonal block. So `U_K = W_K = I`.
2. **Support.** Write `U_T = (U_T[c])_{c ∈ K}` and `W_T = (W_T[c])_{c ∈ K}` in `k × k` blocks. Then `B_{kT} = U_T[k]^T` and
   `B_{Tk} = W_T[k]`, so a forced-zero pair `(T, k)` gives `U_T[k] = W_T[k] = 0`: both are supported on `A(T)`.
3. **X Y^T is block diagonal.** Fix `c ∈ K` and let `O_c = {T ∈ O : c ∈ A(T)}`. Any two `S != T` in `O_c` are forced zero and share
   only the coordinate `c`, so `B_ST = W_S[c] U_T[c]^T = 0`. Let `X` be the stack of the `W_T[c]` and `Y` the stack of the `U_T[c]`
   over `T ∈ O_c` (each block `k × k`). Then `X Y^T` is block diagonal with diagonal blocks `W_T[c] U_T[c]^T`, and as a product through
   dimension `k` it has rank at most `k`. Hence, with `r_T(c) = rank(W_T[c] U_T[c]^T)`,
   `sum_{T ∈ O_c} r_T(c) <= k`.
4. **Rank sum.** `B_TT = sum_{c ∈ A(T)} W_T[c] U_T[c]^T` is invertible, and rank is subadditive, so `sum_c r_T(c) >= k`.
   Summing over the six ports and exchanging the sums:
   `6k <= sum_{c} sum_{T ∈ O_c} r_T(c) <= k · |{62, 63, 69, 91, 99}| = 5k`,
   a contradiction. `∎`

For `k = 1` the rank sum is the pigeonhole principle: each of the six ports needs a coordinate where both of its entries are non-zero, two ports
cannot use the same coordinate, and there are five coordinates.

## What `check.py` verifies (about 0.3 s, standard library)

* ports are 104 distinct odd-weight 9-bit vectors; the forced-zero graph has clique number 8 and `K` is a maximal clique;
* the `A(T)` table, the five coordinates, the 11 sharing pairs (all forced zero, one common coordinate each);
* `k = 1`, any field: no system of distinct representatives for `A(57), ..., A(101)`;
* `k = 1`, `F_2` and `F_3`: an exhaustive search of the gauge-fixed asymmetric 14-port system, with all `U_T, W_T` entries free on the
  eight coordinates (supports are derived from the mask, not assumed): zero solutions;
* a satisfiable control for the same search (port 101 left out), and a satisfiable symmetric dimension-9 realisation of the whole
  14-port mask (one extra coordinate lets the six ports have distinct active coordinates).

`retained/` holds the Singular inputs for the support-reduced `k = 1` system (`s_asymA*.sing`: rings `Z/2`, `Q`, `Z/3`, `Z/5`, `Z`) and
`expected-output.txt`: the standard basis is the unit ideal in each ring. They need Singular and are not run by `verify.sh`.

## Open next questions

1. **Change the label pattern.** Which mechanism forces the pairing to vanish on every zero-dot pair, and can a contact be routed
   through a paid helper so that one forced zero inside each Hall-deficient configuration is broken? Every rank-`8k` route has to do
   this for configurations like the 14 above.
2. **Ranks strictly between `8k` and `9k`** (`k >= 2`). The gauge needs `d = 8k`; with a free extra column the rank sum may or may not close.
3. **Other port systems.** Apply the same support argument (distinct representatives over a forced-zero clique) to other port sets.

See `TASK.json` for first steps and blockers. Credit: DreamingOfClouds.

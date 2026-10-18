# Local-count floor for the stage recipe

This note shows that the stage recipe of the nine-stage bit template uses the
fewest possible local invocations for its number of data pairs. The recipe is
in `global_k.py` (`recipe(K)`), from the PR #386/#436/#443/#463 lineage as
generalised by PR #510.

**Priority.** The bound is not new. The archived campaign report M states that
exchanging P bank pairs needs at least 2P+1 stages. Open PR #743 (Johnny
Franks) proves it uniformly with the potential `rank(A) + rank(D)` of the
diagonal blocks. That potential equals `2K − ν − μ'` below, so the two proofs
are the same argument. This independent formulation is kept because its four
invariants also drive the pruning of `recipe_search.py`. No priority is
claimed.

## Scalar model of a recipe

The template's own integer replay (`small()` in `global_k.py`) abstracts a
recipe to an integer matrix on `2K` banks. Bank `2p` is side 0 of pair `p`, and
bank `2p+1` is side 1. Order the coordinates as `V = V0 ⊕ V1`, where
`V0 = span(side 0 of every pair)` and `V1 = span(side 1 of every pair)`. Write
`L0 = V0 ⊕ 0` and `L1 = 0 ⊕ V1`. The events act as follows:

| event | effect | form |
|---|---|---|
| forward local on pair `p` | `side1_p += side0_p` | lower unipotent `[[I,0],[S,I]]`, `S = e_p e_pᵀ`, rank 1 |
| reverse local on pair `p` | `side0_p -= side1_p` | upper unipotent `[[I,T],[0,I]]`, `T = -e_p e_pᵀ`, rank 1 |
| bridge `(d,s,c)` | `side0_d += c side0_s`, `side1_s -= c side1_d` | block diagonal `diag(A, A⁻ᵀ)` |
| final exchange | `(side0_p, side1_p) -> (side1_p, -side0_p)` | block anti-diagonal `X` |

The template asserts that the whole recipe composes to the identity. Let `P` be
the product of all locals and bridges, so that `X P = I` (and bridges after the
last local are part of `P`). Then `P = X⁻¹` is block anti-diagonal:
`P(L0) = L1` and `P(L1) = L0`.

## Theorem

Work over any field. Let

`P = Λ_n τ_n Λ_{n-1} ... Λ_1 τ_1 Λ_0`,

where:

- every `Λ_i` maps `L0` to `L0` and `L1` to `L1`;
- every `τ_i` is lower (`[[I,0],[S_i,I]]`) or upper (`[[I,T_i],[0,I]]`), with
  `r_i = rank(τ_i - I)`.

The matrices `S_i` and `T_i` may be arbitrary; they need not be symmetric or
integral. If `P(L0) = L1` and `P(L1) = L0`, then

`Σ_i r_i ≥ 2K + 1`.

**Corollary.** Every local of the bit template has rank 1, and every bridge
sequence is block diagonal. So any recipe that ends in the exchange of all `K`
pairs needs at least `2K + 1` locals, which is `2K + 1` stages. `recipe(K)`
uses exactly `2K + 1`, so it is optimal in this respect. Equivalently, at
`L = 9` stages there are at most `K = 4` exchanged pairs. The rank-mass
deficit `T(2Kv - L·cst)` therefore cannot be raised by re-designing the stage
recipe in this model: at fixed `L`, `K` cannot increase, and at fixed `K`, `L`
cannot decrease.

## Proof

For a linear map `g`, define

- `μ(g) = dim(g L0 ∩ L0)` and `μ'(g) = dim(g L1 ∩ L0)`;
- `ν(g) = dim(g L0 ∩ L1)` and `ν'(g) = dim(g L1 ∩ L1)`.

At `g = I` these are `(μ, μ', ν, ν') = (K, 0, 0, K)`. At `g = P` they must be
`(0, K, K, 0)`. Build `P` from the right, one factor at a time.

**(a) Block-diagonal factors change nothing.** On the left, `Λ` preserves both
`L0` and `L1`, so `dim(ΛU ∩ L_j) = dim(Λ(U ∩ L_j)) = dim(U ∩ L_j)`. On the
right, `gΛL_j = gL_j`.

**(b) A lower factor fixes ν and ν'; an upper factor fixes μ and μ'.** A lower
`τ` maps `L1` onto itself, so `dim(τU ∩ L1) = dim(U ∩ τ⁻¹L1) = dim(U ∩ L1)`.
The same argument applies to an upper `τ` with `L0`.

**(c) A factor of rank r changes each quantity by at most r.** Let `U` and `W`
be subspaces and `x ∈ U ∩ W ∩ ker(τ - I)`. Then `x = τx ∈ τU ∩ W`, so
`dim(τU ∩ W) ≥ dim(U ∩ W) - r`. Applying the same bound to `τ⁻¹`, which also
has `rank(τ⁻¹ - I) = r`, gives the reverse inequality.

By (a)–(c), only lower factors move `μ` and `μ'`, and only upper factors move
`ν` and `ν'`. Each moves them by at most its rank. So `Σ_lower r_i ≥ K` and
`Σ_upper r_i ≥ K`.

Now look at the first factor `τ_1`; `Λ_0` does not matter by (a).

- **`τ_1` is lower.** It fixes `L1` pointwise, so `τ_1 Λ_0 L1 = L1` and
  `μ' = dim(L1 ∩ L0) = 0` stays 0. The later lower factors alone must raise
  `μ'` from 0 to `K`. Hence `Σ_lower r_i ≥ K + r_1 ≥ K + 1`.
- **`τ_1` is upper.** It fixes `L0` pointwise, so `ν` stays 0 after it, and
  symmetrically `Σ_upper r_i ≥ K + 1`.

In both cases `Σ r_i ≥ 2K + 1`. ∎

## Tightness and checks

- **Tightness.** `recipe(K)` attains the bound: `F_0` followed by
  `(R_j B+ F_j B−)` for `j = 0..K-1`, which is `2K + 1` rank-1 locals.
- **Brute force.** `floor_check.py` independently confirms `K = 1` and `K = 2`.
  For `K = 1` it uses vectors in `[-3,3]`; for `K = 2` it uses all primitive
  vectors in `[-2,2]²` and entries up to 50. No product of `2K` rank-1 shears is
  block anti-diagonal, while products of `2K + 1` shears are. This is a finite
  check of the bounded class only; the theorem above is the general statement.

## Scope

- **What the theorem covers.** The theorem is about the template's scalar
  abstraction: each local is a rank-1 shear on one pair. Its conclusion does
  not depend on the coefficients, on the field (it holds over F2, where the
  template also replays its columns), or on which block-diagonal maps sit
  between locals.
- **What it does not cover.** It does not cover templates in which a local
  acts on several pairs at once, or in which free data movement is
  off-block-diagonal, for example a cheap `side1 += side0` addition that is not
  a paid local. Nor does it cover architectures where the exchange is not
  required on every data pair.
- **Hosting, words and κ.** It says nothing about how idle children are
  hosted, which is the subject of the search in `README.md`. It says nothing
  about the local word either. It changes no κ.

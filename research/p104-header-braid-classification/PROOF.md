# Saturated headers, the sphere-braid relation and the Hurwitz classification: statements and proofs

No κ is claimed. Everything below is a statement about words of rank-one square-zero units, proved from the
definitions, plus exact checks in `verify.py` (section numbers are cited there). Where a published theorem is used
without proof, Section 8 says exactly what it states and where it was checked.

## 0. Conventions and hypotheses

`F` is a field with `char F != 2`; `n >= 2` is even and `N = n + 1`. A *unit* is `U = I - 2 x y` with `x` a column,
`y` a row and `y x = 0`. A word of units acts with the unit of index 0 first: `J = U_n ... U_0`.
`Gamma_ij = y_i x_j`.

* **Header** (saturated): `n+1` units on `F^n` with `J = -I`. This is the case `N - r = 1`, `r = n`, of the
  rank identity of #6832: `n+1` square-zero units whose product is the involution `-I`, the minimum allowed.
* **Normalised header**: `Gamma_ij = sgn(i - j)`.
* **Gauge**: `(x_t, y_t) -> (s_t x_t, y_t / s_t)` does not change `U_t`. Over `Z` the only gauge is `s = +-1`.
* **Path form** (hypotheses H): `q` is central with `q^2 = 1`; `t_i(q) = I + q a_i b_i`, `b_i a_i = 0`, `i = 0..n`;
  `M(q) = t_n(q) ... t_0(q)`; the projection `E` onto the `q`-even part satisfies `E(q) = 0`, so
  `E(M) = (M(1) + M(-1))/2`; ordinary (`q`-free, invertible) controls are absorbed into the units by conjugation;
  every diagonal control variable is specialised to `D = 1`; the target is `q`-odd, i.e. `E(M) = 0`, i.e.
  `M(-1) = -M(1)`. These four hypotheses (`q^2 = 1`, `E(q) = 0`, ordinary controls, `D = 1`) are the scope of
  everything stated for path form. They are not claimed for a central `q` of order 3, for non-central controls, or
  for non-uniform columns.
* `sgn(0) = 0`; `S_n` is the `n x n` matrix with entries `sgn(j - i)`.

## 1. Rank identity, normalisation, rigidity

**Lemma 1.1 (expansion).** For units `I - x_t y_t` (`t = 1..N`, index 1 first), `J = I - X K^{-1} Y`, where `X = [x_1 ... x_N]`,
`Y` has rows `y_t`, `K = I + (strictly lower part of Gamma)`, `Gamma = Y X`.
*Proof.* Induction on `N`. Write `K = [[K', 0], [g, 1]]` with `g = y_N X'`; then `K^{-1} = [[K'^{-1}, 0], [-g K'^{-1}, 1]]` and
`X K^{-1} Y = X' K'^{-1} Y' + x_N (y_N - g K'^{-1} Y')`, which is `I - (I - x_N y_N)(I - X' K'^{-1} Y')`. ∎

**Lemma 1.2 (rank one).** For a header (units `I - 2 x y`, so `x' = 2x` in Lemma 1.1; `Gamma' = 2 Gamma`), the matrix
`R = 2K' - Gamma' = 2I + Gamma'_< - Gamma'_>` has rank one.
*Proof.* `J = -I` gives `X' K'^{-1} Y = 2 I_n`. Put `A = K'^{-1} Y` (`N x n`) and `Omega = A X'`. Then `X' A = 2I` shows `A` is injective and
`X'` surjective, so `rank Omega = n`; and `Omega^2 = A (X' A) X' = 2 Omega`. As `char != 2`, `Omega` is diagonalisable with
eigenvalues `2` (multiplicity `n`) and `0` (multiplicity `N - n = 1`). Hence `rank(2I - Omega) = 1`, and
`2K' - Gamma' = K'(2I - Omega)`. ∎ (`verify.py` section 2 checks the rank on headers up to `n = 18` and the expansion on random words.)

**Proposition 1.3 (normal form).** Every header is gauge-equivalent over `F` to a normalised header.
*Proof.* `R = u v^T` with `u_i v_i = 2` (diagonal of `R`). `R_ij = Gamma'_ij = 2 Gamma_ij` for `i > j`, `R_ij = -2 Gamma_ij` for `i < j`. The gauge
`s_i = u_i` multiplies `Gamma_ij` by `u_j / u_i`, giving `Gamma_ij = u_j v_j / 2 = 1` for `i > j` and `-1` for `i < j`. ∎

**Theorem 1 (structure and rigidity).** Let `T = ((x_t, y_t))` be a normalised header on `F^n`.
(a) The `x_t` span `F^n` and so do the `y_t`; the only linear relation is `sum (-1)^t x_t = 0`, and likewise for `y`.
(b) There is a unique form `omega` with `y_t = omega(x_t, .)`; it is skew and `omega(x_i, x_j) = sgn(i - j)`. The vectors
`d_s = x_s - x_{s+1}` (`s = 0..n-1`) form a basis with `omega(d_s, d_{s+1}) = -1` and `omega(d_s, d_t) = 0` otherwise, so `omega`
is nondegenerate (the path `A_n`, determinant 1), and `Z{x_t} = Z{d_s}` is unimodular for `omega` when `T` is integral.
(c) (Rigidity) If `T'` is another normalised header on `F^n`, there is exactly one `g in GL_n(F)` with `g x_t = x'_t`
for all `t`, and then `y'_t = y_t g^{-1}`. In particular `g` is symplectic for the two forms.
*Proof.* (a) `X' K'^{-1} Y = 2I` gives `rank X = rank Y = n`. For every `i`, `sum_j (-1)^j sgn(i - j) = 0` (direct count: the sums over `j < i`
and `j > i` are both `[i odd]`), so `y_i (sum_j (-1)^j x_j) = 0` for all `i`; the `y_i` span the dual, hence `sum (-1)^j x_j = 0`; likewise for `y`.
As `rank X = n` and there are `n+1` vectors, this is the only relation. (b) `omega(x_i, x_j) := Gamma_ij` respects the relation in both arguments by
the same count, so it defines a bilinear form on `F^N / <alternating vector> = F^n`; it is skew. The values `omega(d_s, d_t)` follow from
`Gamma_ij = sgn(i - j)`: for `t > s+1` all four terms are `-1, +1, +1, -1`; for `t = s+1` they give `-1`; for `t = s` they give 0.
Unimodularity: the Gram matrix of `d` is the path, `det = 1`. (c) By (a) both tuples have the same unique relation, so the map `x_t -> x'_t` on the
basis `x_0..x_{n-1}` is well defined on all `x_t`. Then `y'_t g x_j = Gamma_tj = y_t x_j` on a spanning set gives `y'_t g = y_t`. ∎

(`verify.py` section 2 checks (a), (b) and the two relations up to `n = 18`; section 2 also computes `g` between the canonical header and the chain
roots `(3|3)`, `(1|5)`, `(2|2)` and the root of #6726 and checks `g x_t = x'_t`, `y'_t = y_t g^{-1}` on all `n+1` units. Control: after
inserting a unit and its inverse (five units, product still `-I`) two tuples on `F^2` have no common `g`, so exactly `n+1` units are needed.)

## 2. The sphere-braid relation on a chain of transvections

Let `V = Z^N` with basis `e_0..e_{N-1}`, `omega(e_i, e_{i+1}) = 1 = -omega(e_{i+1}, e_i)`, other pairs zero, and `tau_i(v) = v + omega(e_i, v) e_i`.
Put `s_k = e_0 + ... + e_k` and `rho = sum_k (-1)^k s_k`, so `rho_i = sum_{k >= i} (-1)^k`.

**Proposition 2 (palindromic relation).** For every `N >= 1`,
`P_N := tau_0 tau_1 ... tau_{N-1} tau_{N-1} ... tau_1 tau_0 = -I + 2 rho (e_0^*)` where `e_0^*(v) = v_0`.
Consequently, for `N` odd, `rho = e_0 + e_2 + ... + e_{N-1}` spans the radical of `omega`, `P_N = -I` on `V / rad`, and with `t_i = tau_i`,
`M(q) = t_{N-1}^q ... t_0^q`: **`M(-1) = -M(1)` on `V/rad`**. For `N` even `P_N != -I`.
*Proof.* Let `Q_k = tau_0 ... tau_k tau_k ... tau_0`, `g_k = tau_0 ... tau_{k-1}`. Then `Q_k = (g_k tau_k^2 g_k^{-1})(g_k g_k^{rev}) = T_{w_k}^2 Q_{k-1}` with
`T_w(v) = v + omega(w, v) w`, `w_k = g_k e_k`, because `g T_v g^{-1} = T_{g v}` for `g` preserving `omega`. Applying `tau_{k-1}, tau_{k-2}, ...` to `e_k`
adds `e_{k-1}`, then `e_{k-2}`, ..., so `w_k = s_k`. For `j < k`, `omega(s_j, s_k) = (j+1) - j = 1`. Hence `P_N = T_{s_{N-1}}^2 ... T_{s_0}^2` (`s_0` first).
Write `v = sum c_k s_k` (so `c_k = v_k - v_{k+1}`, `epsilon := sum c_k = v_0`); `omega(s_k, v) = sum_{j>k} c_j - sum_{j<k} c_j`. After steps `0..k-1` the coefficients at
`j < k` are final (`f_j`), the others are the original `c_j`; so `f_k = c_k + 2 (sum_{j>k} c_j - sum_{j<k} f_j)`. With `F_k = sum_{j<=k} f_j`, `C_k = sum_{j<=k} c_j`
this reads `F_k + C_k = 2 epsilon - (F_{k-1} + C_{k-1})`, so `F_k + C_k = 2 epsilon [k even]` and `f_k = -c_k + 2 (-1)^k epsilon`. That is `P_N v = -v + 2 epsilon rho`.
For `N` odd, `rho_i = [i even]`, and `omega(rho, e_j) = [j odd] - [j odd] = 0`, so `rho` is radical. For `N` even `rho = -sum_{i odd} e_i != 0` and `P_N e_0 = -e_0 + 2 rho != -e_0`.
Finally `P_N = -I` gives `t_{N-1} ... t_0 = -(t_0 ... t_{N-1})^{-1} = -t_{N-1}^{-1} ... t_0^{-1}`. ∎

`verify.py` section 1 checks `P_N = -I + 2 rho e_0^*` for `N = 1..40`, that `M(1) + M(-1)` takes values in the radical for odd `N`, that `P_N != -I` for even `N`, and four
altered words (a letter removed, an altered middle, inverse letters on one side) that are not `-I` modulo the radical.

**Reading as a braid relation.** With `n + 2 = N + 1` strands, the word `sigma_1 ... sigma_N sigma_N ... sigma_1` is the extra relation of the sphere braid group
(Fadell and Van Buskirk; see Section 8); the chain of `tau_i` is the symplectic (Burau at `t = -1`) representation of the braid group on `N + 1 = 2g + 2` strands
acting on `H_1` of the genus-`g` hyperelliptic cover (`N = 2g + 1`), where the hyperelliptic involution acts as `-I`. Proposition 2 is the matrix identity and does not use
that reading. The topological identification of the lift of this word with the involution is the Birman–Hilden picture; it is not needed here and was not re-derived.

## 3. The path theorem and existence

**Lemma 3.1 (telescoping).** For units `t_i(q) = I + q a_i b_i` with `b_i a_i = 0` and `A_i = t_n^{-1} ... t_{i+1}^{-1}` (`t^{-1} = t(-1)`):
`M(-1) M(1)^{-1} = (A_0 X_0 A_0^{-1}) (A_1 X_1 A_1^{-1}) ... (A_n X_n A_n^{-1})`, `X_i = I - 2 a_i b_i`.
*Proof.* `X_i = t_i^{-1} t_i^{-1}` because `b_i a_i = 0`, and `A_{i-1} = A_i t_i^{-1}`, so `A_i X_i A_i^{-1} = A_{i-1} t_i^{-1} A_i^{-1}`. The product telescopes to
`A_{-1} t_0^{-1} ... t_n^{-1} = M(-1) M(1)^{-1}` (`A_n = I`, `A_{-1} = M(-1)`, `t_0^{-1} ... t_n^{-1} = M(1)^{-1}`). ∎

**Theorem 2 (path theorem).** Assume H with `N = n + 1` units on `F^n`, `M(-1) = -M(1)`. Then, after a gauge `(a_i, b_i) -> (s_i a_i, b_i / s_i)` (which fixes every `t_i`),
the path Gram `Gamma^p_ij = b_i a_j` satisfies `Gamma^p_{i,i+1} = 1`, `Gamma^p_{i+1,i} = -1`, `Gamma^p_ij = 0` for `|i - j| >= 2`. In gauge-invariant form: `Gamma^p` is tridiagonal and
`Gamma^p_{i,i+1} Gamma^p_{i+1,i} = -1` for every `i`; no value other than `-1` occurs. Conversely, for every even `n` the chain of Proposition 2 (on `V/rad`, `a_i = e_i`
for `i < n`, `a_n = -(e_0 + e_2 + ... + e_{n-2})`, `b_i = omega(a_i, .)`) satisfies H with `N = n+1` and `M(-1) = -M(1)`. By Theorem 1(c) every path-form header is, up to `GL_n`, this one.
*Proof.* By Lemma 3.1 the star word `U_0 ... U_n`, `U_i = A_i X_i A_i^{-1} = I - 2 x_i y_i` (`x_i = A_i a_i`, `y_i = b_i A_i^{-1}`), equals `M(-1) M(1)^{-1} = -I`; listing the units from the last
one makes it a header, which by Proposition 1.3 is gauge-equivalent to a normalised one; in the index of `i` the normalised Gram reads `y_i x_j = +1` for `i < j` and `-1` for `i > j`. Gauge does not change `t_i, A_i`.
Now `y_i x_j = b_i A_i^{-1} A_j a_j`, and `A_i^{-1} A_j = t_{i+1} ... t_j` for `i < j`, `= t_i^{-1} ... t_{j+1}^{-1}` for `i > j`. Using `t_j a_j = a_j` and `b_i t_i^{-1} = b_i`, and expanding the products over increasing
(resp. decreasing) chains, with `U` and `L` the strict upper and lower parts of `Gamma^p`:
upper part of `(y_i x_j)` is `U + U^2 + ... = U (I - U)^{-1}`, lower part is `L - L^2 + ... = L (I + L)^{-1}`, diagonal `b_i a_i = 0`.
Let `Z` be the superdiagonal shift. The normalised values say `U(I-U)^{-1} = Z + Z^2 + ... = Z(I - Z)^{-1}`, so `U = Z(I-Z)^{-1} (I + Z(I-Z)^{-1})^{-1} = Z`; and `L(I+L)^{-1} = -Z^T(I - Z^T)^{-1}` gives `L = -Z^T`.
The converse is Proposition 2 with Lemma 3.1 and Proposition 1.3. ∎

`verify.py` section 3 checks: star-to-path (`a_i = t_{i-1}...t_0 x_i`, `b_i = y_i (t_{i-1}...t_0)^{-1}`) gives `b_i a_i = 0`, tridiagonal Gram with products `-1` and `M(-1) = -M(1)` for canonical headers `n = 2..10`,
chains `(3|3), (4|4), (5|3)` and the root of #6726; the converse for `N = 3, 5, 7, 9, 11` (star of the chain is a normalised header and agrees with the canonical header up to the `g` of Theorem 1);
**exhaustively, every one of the 160 triples of units on `F^2` with entries in `{-1, 0, 1}` and `M(-1) = -M(1)` has the stated Gram**; control: doubling one `b` gives `t = -2` and `M(-1) != -M(1)`.

*Hypotheses are used as follows.* `q^2 = 1` and `E(q) = 0` give `E(M) = (M(1) + M(-1))/2`; ordinary controls and `D = 1` let the units be written as `I + q a b` and the target as `M(-1) = -M(1)`; the count `N = n + 1` makes the rank identity an equality.
Without `N = n + 1` (rank deficiency `N - r >= 2`) the theorem is false in the form stated: the control in Section 1 shows non-rigid roots exist.

## 4. Hurwitz moves

For a normalised header `T` define, for `1 <= i+1 <= n`:
`mu_i^{+}`: `(x_i, x_{i+1}) -> (x_{i+1}, 2 x_{i+1} - x_i)`, the same for `y`;
`mu_i^{-}`: `(x_i, x_{i+1}) -> (2 x_i - x_{i+1}, x_i)`, the same for `y`.
These are the Hurwitz moves `(U_i, U_{i+1}) -> (U_{i+1}, U_{i+1} U_i U_{i+1}^{-1})` and `(U_i^{-1} U_{i+1} U_i, U_i)` written with the signs that keep the Gram normalised.

**Theorem 3 (Hurwitz action).** Let `T` be a normalised header, `d_i = x_i - x_{i+1}`, `g_i = I + d_i (y_i - y_{i+1})` (the transvection `v -> v + omega(d_i, v) d_i`).
(a) Each move gives a normalised header with the same `omega`, the same product `-I`, and `mu_i^{+} T = g_i T`, `mu_i^{-} T = g_i^{-1} T` (the linear action on every `x_t` and `y_t`).
(b) The `g_i` satisfy the braid relations, so `rho_T : B_N -> Sp(F^n, omega)`, `sigma_i -> g_i`, is a homomorphism (the Burau representation at `t = -1`, see Section 8), and for a word `w = (j_1, s_1) ... (j_m, s_m)` of moves,
`w T = rho_T(sigma_{j_1}^{s_1} ... sigma_{j_m}^{s_m}) T`. The orbit of `T` is `rho_T(B_N) T`.
(c) (Locality) Only the units at positions `i, i+1` change; they are supported in the union of the two old supports; the prefix products `U_k ... U_0` are unchanged for `k != i`.
(d) (Sector form is legal, path form is not.) Work in `F[q]/(q^2 - 1) = F x F` (values at `q = 1` and `q = -1`). A *sector unit* is `I + (q-1) x y`, with value `I` at `q = 1`
and `I - 2xy` at `q = -1`. Conjugating a sector unit by another sector unit has value `I` at `q = 1`, so it is again a sector unit with `q`-free square-zero vectors
`(U_{i+1} x_i, y_i U_{i+1}^{-1})`. A *path unit* is `t(q) = I + q a b`; the conjugate `t_{i+1}(q)^{-1} t_i(q) t_{i+1}(q)` has `q`-even part `Gamma^p_{i,i+1} a_i b_{i+1} - Gamma^p_{i+1,i} a_{i+1} b_i`,
nonzero for adjacent units of a path header (`Gamma^p_{i,i+1} Gamma^p_{i+1,i} = -1`, `a_i, a_{i+1}` independent), so it is no longer of the form `I + q (q-free rank one)`; units with `Gamma^p = 0` (non-adjacent) commute and move freely.
"Legal" here means: the moved word is again a product of the same kind of units with the same `M(q)`. It is a statement about this algebra only, not about any compiler, native supplier or caller.
*Proof.* (a) `g_i x_i = x_{i+1}` (as `omega(d_i, x_i) = -1`), `g_i x_{i+1} = x_{i+1} + omega(d_i, x_{i+1}) d_i = 2 x_{i+1} - x_i`, and for `t < i` or `t > i+1`, `omega(d_i, x_t) = Gamma_it - Gamma_{i+1,t} = 0`
because `sgn(i - t) = sgn(i + 1 - t)`. For `y` the same computation with `y_t = omega(x_t, .)`. The inverse move is `g_i^{-1}`. A transvection preserves `omega`, so `Gamma`, `J` and unit squares are preserved.
(b) `omega(d_i, d_{i+1}) = -1`, `omega(d_i, d_j) = 0` for `|i - j| >= 2` give the braid relations. After one move `x'_t = g_i x_t`, `y'_t = y_t g_i^{-1}` for all `t`, so `d'_j = g_i d_j` and the transvection of the new tuple is
`g'_j = I + g_i d_j (y_j - y_{j+1}) g_i^{-1} = g_i g_j g_i^{-1}`; the second move acts as `g'_j g_i T = g_i g_j T`; induct. (c) from (a); the pair `U_{i+1} U_i` is replaced by `(U_{i+1} U_i U_{i+1}^{-1}) U_{i+1}`, equal. (d) computation as stated. ∎

`verify.py` section 4 checks (a)-(c) for all `2n` moves of canonical headers `n = 2, 4, 6, 8` and chain `(3|3)`, the braid and far-commutation relations of the `g_i`, `5` random words per root as `rho_T`-products, the
sector computation for every `i`, the nonzero `q`-even part for every adjacent path pair and the vanishing for non-adjacent pairs.

**What (c) does and does not say about masks.** A *site mask* is any coordinate set containing the supports of `x_t` and `y_t`. By (c) only the masks at the two moved positions can change, and the new supports lie in the union of the two old ones.
The statement that a word of this kind with diagonal controls `D` has `M(D) = -prod Delta_k` exactly when each site idempotent commutes with its unit depends on how masks are defined in the surrounding word (constant bases, one variable per site).
That equivalence is not reproduced or claimed here.

## 5. Orbits in a fixed frame

A *frame* is the choice of the form `Omega` in coordinates; an *integral frame* is `Omega in M_n(Z)` with the header integral. If `T` is integral and `Omega` is integral on `Z^n`, then
`L = Z{x_t} = Z{d_s}` has `det(omega|_L) = 1`, while `det(omega|_L) = [Z^n : L]^2 det(omega|_{Z^n})`; so `L = Z^n` and `Omega` is unimodular.

**Theorem T (cited; Section 8).** For `n = 2g`, the standard map `rho : B_{2g+1} -> Sp_{2g}(Z)` (Burau at `t = -1`) restricts on the pure braid group to a surjection onto `Sp_{2g}(Z)[2]`, the level-2 congruence subgroup (Brendle–Margalit, Theorem 3.3;
the first statement of that theorem is attributed there to A'Campo).
By Theorem 1(c) the representation `rho_T` of Theorem 3 is conjugate in `GL_n(Z)` to the standard `rho` (the standard `rho(sigma_i)` is the transvection along a chain basis `c_i` with `c_i . c_{i+1} = +-1`; two chain bases with the same Gram
are carried to one another by a symplectic isomorphism, and `T_{-v} = T_v`).

**Theorem 4 (classification in a fixed frame).** Let `Omega` be an integral frame, `n` even, `Hdr(Omega)` the set of normalised integral headers with that `Omega` (nonempty whenever `Omega` is unimodular: such an `Omega` has a symplectic basis, and a change of basis carries the canonical header to it; `verify.py` does this for one frame other than `S_n`).
(a) `Sp(Omega)(Z)` acts simply transitively on `Hdr(Omega)` up to the global sign `-1` (rigidity plus integrality), commuting with the Hurwitz moves.
(b) `rho_T(B_N) = { g in Sp(Omega)(Z) : g mod 2 lies in S }`, where `S` is the group generated by the reductions of the `g_i` (they act on `{x_t mod 2}` as the transpositions `(i, i+1)`; `S_N -> S` is injective, because a normal subgroup of `S_N` in the kernel would contain a 3-cycle and so contain `A_N`, while the images of a transposition and of a 3-cycle are nontrivial). In particular `-I` lies in it (Proposition 2).
(c) Two tuples `T, T' in Hdr(Omega)` are in one Hurwitz orbit **iff the multisets `{x_t mod 2}` coincide** (the invariant `Omega` is part of the frame). The orbit is `rho_T(B_N) T` and has no other invariant.
(d) The number of orbits in `Hdr(Omega)` is `|Sp_n(F_2)| / (n+1)!`: 1, 6, 288, 130560 for `n = 2, 4, 6, 8` (`n = 2, 4, 6` enumerated; `n = 8` from the formula).
(e) Headers with different `Omega` are never connected by moves (Theorem 3(a)), although by Theorem 1(c) any two headers on `Z^n` with unimodular `Omega` differ by a change of frame.
*Proof.* (a) `T' = hT` with `h in GL_n(Q)` by Theorem 1(c); `h` maps `L = Z^n` onto itself because `x'_t in Z^n` span it, so `h in Sp(Omega)(Z)`; uniqueness up to `-I` as in Theorem 1(c) (`g x_t = +-x_t` for all `t` forces
a common sign through `Gamma_{01} = +-1`). (b) The moves are `x_i <-> x_{i+1}` modulo 2, so `rho_T(B_N)` reduces onto `S`; by Theorem T `rho_T(B_N) supseteq rho_T(PB_N) = Sp[2]`, the kernel of `Sp(Z) -> Sp(F_2)`; a subgroup that contains the kernel and maps onto `S` is the full preimage of `S`. (c) If the multisets agree, `h mod 2` permutes `x_t mod 2` (it maps `x_t` to `x'_t`, which are the `x_t` in some order), hence lies in `S`
(a spanning set determines an element of `Sp(F_2)`), so `h in rho_T(B_N)` by (b) and `T' = hT` is in the orbit; the converse is the reduction of a move. (d) Orbits are the cosets `h rho_T(B_N)`, in bijection with
`Sp_n(F_2)/S`, and the stabiliser of the multiset in `Sp_n(F_2)` is `S` (an element permuting the spanning set `{x_t mod 2}` is determined by the permutation). (e) from Theorem 3(a). ∎

*Cited input used:* only `rho(PB_{2g+1}) = Sp_{2g}(Z)[2]`. Nothing here depends on A'Campo's original paper beyond what Brendle–Margalit attribute to it.

`verify.py` section 5 checks consequences of Theorem T independently at small level, by breadth-first search over all moves on exact tuples of units reduced modulo `m` (states are the matrices `x y`, so every gauge is quotiented out):
size of the orbit of the canonical header: `n = 2`: mod 3 `12 = |Sp_2(3)|/2`, mod 4 `24 = 3! 2^3 / 2`, mod 8 `96 = 3! (|SL_2(Z/8)|/6)/4` (four scalars `s` with `s^2 = 1` fix every unit); `n = 4`: mod 3 `25920 = |Sp_4(3)|/2`, mod 4 `61440 = 5! 2^{10} / 2`.
(The factor `1/2`, resp. `1/4`, is the scalars `s` with `s^2 = 1`; without it the mod-4 count would be `122880`, a negative control.) It also enumerates the orbit of the mod-2 multiset under `Sp_n(F_2)` (generated by all transvections) and finds `1, 6, 288` classes, equal to `|Sp_n(F_2)|/(n+1)!`,
and checks that an explicit transvection of `Sp_4(Z)` (along `(1,1,1,0)`) carries the canonical header to a header with the same `Omega` and a different mod-2 multiset, i.e. to a different orbit in the same frame.
These checks do not prove Theorem T for `n >= 6`.

## 6. The arc law

Frame `Omega = S_n`, `x in Z_(2)^n` (rational numbers with odd denominator; `Z` is enough for the checks), `y = x^T S_n`, i.e. `y_f = sum_{g<f} x_g - sum_{g>f} x_g = 2 s_{<f} + x_f - s` with `s = sum x_g`, `s_{<f} = sum_{g<f} x_g`.
Let `M` be any set containing `supp(x) and supp(y)`, and `W = {g : x_g odd}`. Cyclic order: `S_n` rotated by one place equals `D S_n D` for the diagonal sign `D = diag(-1)` at the moved field, so the fields lie on a cycle up to signs.

**Theorem 5.** (a) If `|W|` is odd, `M` is all fields. (b) If `|W|` is even, there is `c in {0, 1}` such that every field outside `M` has `|W cap [0, f)| = c` modulo 2; i.e. `M` contains `W` and every field whose prefix parity is not `c`.
(c) If `W = {A, j}`, `M` contains one of the two cyclic arcs from `A` to `j` (inclusive).
*Proof.* For `f not in M`, `x_f = 0 = y_f`, so `2 s_{<f} = s`. (a) `s equiv |W| = 1 (mod 2)` contradicts `2 s_{<f} = s` in `Z_(2)`, so no field is outside `M`. (b) `s` is even; all gaps have the same `s_{<f} = s/2`,
whose parity is the parity of `|W cap [0, f)|` (even entries do not change parity); this is `c`. (c) With `A < j` the prefix parity is `0` for `f <= A`, `1` for `A < f <= j`, `0` for `f > j`. If `c = 0`, every `f` with parity 1 is in `M`, so
`[A+1, j] cup W`, i.e. the arc `[A, j]`; if `c = 1`, `M` contains `[0, A] cup [j, n-1]`, the arc from `j` through the wrap to `A`. ∎
**Both supports are needed.** If only `y` is supported in `M`, (c) can fail: `n = 4`, `x = (-2, 1, 0, -1)`, `y = (0, -1, 0, -1)`, `W = {1, 3}`, `supp y = {1, 3}` contains no arc from 1 to 3 (the true mask `{0, 1, 3}` does).
`verify.py` section 6 checks (a)-(c) for every `x` in `{-3..3}^4`, `{-2..2}^6`, `{-1,0,1,2}^8` (83,562 vectors, plus 3,120 unit checks on the literal roots and walks), the counterexample, and every unit of the chain roots `(3|3)`, `(9|9)`, the root of #6726 and of random Hurwitz walks of those roots in the frame `S_n`.

## 7. Literal relations

`verify.py` section 7 puts each root in the frame `S_n` by a signed relabeling of its fields (the relabeling is a frame change; it is not a Hurwitz move) and finds shortest Hurwitz words by growing breadth-first balls from both ends
(the length printed is exact: the balls of the radii below it are disjoint).
* Chains `(a|b)` with the same `n` (40 chains, `n = 4..12`, shapes `(odd|odd)`, `(even|even)`, `(odd|even)`) all have `Omega = S_n` and the same multiset `{A + f}, {A}, {all but A}` mod 2, so by Theorem 4(c) each pair is one orbit.
Shortest words: `(2|2) <-> (3|2)`: 2 letters; `(3|2) <-> (1|4)`: 4; `(3|3) <-> (5|1)`: 6; `(3|3) <-> (1|5)`: 6; `(5|5) <-> (7|3)`: 6.
* The root of #6726 (8 fields, 9 queries, site masks of sizes 2, 4, 4, 4, 4, 2) has `Omega` equal to `S_8` after any of eight signed relabelings of its fields (one per choice of the first field); exactly one of the eight (first field = field 0) has the chain invariants. The shortest Hurwitz word from chain `(3|3)` to it is **5 letters**: `(1,-1), (4,+1), (3,+1), (6,+1), (4,+1)` (position `i` is the move on units `i, i+1`). Distance 5 is exact.
This is a statement about one instance. No general statement that a retirement is a Hurwitz move is made.
* Frames matter: chain `(3|3)` in its own coordinates has 56 nonzero entries in `Omega`; a header on `Z^8` with `Omega` equal to four copies of `[[0,1],[-1,0]]` has 8. Moves preserve `Omega` (checked on 40 random moves each),
so the two never meet, though Theorem 1(c) relates them by a change of frame.
* Observation about the family: the closed form for the thin queries in `chain_root.py` of #6833 (commit `51f54e3c`) for shapes `(even|odd)` does not give a sign-Gram header in this transcription (`(2|1), (2|3), (4|1)` fail; `(3|1), (1|4), (2|2), (4|4), (9|9)` and all shapes used above pass). The shapes used in this package and in #6833 itself, `(9|9)`, are unaffected.

## 8. Citations: what was checked and what each says

1. **Fadell and Van Buskirk** (Duke Math. J. 29 (1962)): the sphere braid group is the braid group with the one extra relation `sigma_1 ... sigma_{N} sigma_{N} ... sigma_1 = 1`.
Checked: the nLab entry on spherical braid groups and Kaabi–Vershinin (arXiv:1202.3557) state this with that attribution (Zariski earlier). The original was not read.
2. **Birman–Hilden.** Checked in Margalit–Winarski, *The Birman–Hilden theory* (arXiv:1703.03448): for genus 2 `1 -> <iota> -> Mod(S_2) -> Mod(S_{0,6}) -> 1`; `SMod(S_g)/<iota> = LMod(S_{0,2g+2})`; `iota` acts as `-I` on `H_1`; `SMod(S_g^1) = B_{2g+1}` and `SMod(S_g^2) = B_{2g+2}`; the symplectic representation is Burau at `t = -1` (the integral Burau representation).
**That survey does not state the relation of Section 2, and says nothing about it.** What Birman–Hilden supplies is the interpretation; the relation comes from item 1. The identity used here is proved in Proposition 2.
3. **A'Campo**, *Tresses, monodromie et le groupe symplectique*, Comment. Math. Helv. 54 (1979), 318–327. I could not obtain the text. Secondary sources: the paper arXiv:1609.05673 ("Congruence subgroups of braid groups") cites it as [Theorem 1 (1)] for the surjectivity of the reduction of the symplectic representation of `B_n` modulo every prime `p`,
and Brendle–Margalit (The level four braid group, arXiv:1410.7416, Theorem 3.3) say that the first statement of their theorem is due to A'Campo. **The level-2 statement for the pure braid group, which Theorem 4 needs, is therefore cited to Brendle–Margalit, Theorem 3.3** (for odd `n = 2g+1`: `rho(PB_n) = Sp_{2g}(Z)[2]`), not to A'Campo directly.
Arnol'd (1968): `B_n[2] = PB_n`, as quoted in the same sources.
4. **Gambaudo–Ghys, Proposition 2.1**, quoted in arXiv:1609.05673 for "evaluate the Burau representation at `t = -1` to get a symplectic representation". Identification of `sigma_i` with the transvection along a chain basis: standard; used in Theorem 3(b) only through conjugacy classes of chain bases.
5. **Brendle–Margalit–Putman**, *Generators for the hyperelliptic Torelli group and the kernel of the Burau representation at t = -1*, Invent. Math. 200 (2015): context only (kernel of `rho`); not used.

## 9. Not covered

Order-3 (or other) central `q`; non-central controls; non-uniform columns; fields of characteristic 2; headers with more than `n+1` units (non-rigid); non-integral frames (`Omega` not integral on `Z^n`, or `x` not integral); `Z_(2)`-frames for Theorem 4; the equivalence of masks with commuting idempotents;
whether any of the Hurwitz-equivalent headers admits a complete invoice (nothing here prices a word); general optimality of any chain shape.

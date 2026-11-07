# Query-block bound: statements and proofs

No κ is claimed. Everything here is a statement about words of rank-one query units in an algebra with a
bimodule projection, plus exact checks (`verify.py`) on the literal #6726 header and on explicit models.
Section numbers are cited by `README.md` and `verify.py`.

## 0. Conventions

`F` is a field. A *unit* is a rank-one factor. For vectors `x_i, y_i` over `F`, `N` units give
`J = (I - x_N y_N^T) ... (I - x_1 y_1^T)`; the index `1` acts first. Put `tau_i = y_i^T x_i`,
`Gamma_ij = y_i^T x_j`, `K = I + (strictly lower part of Gamma)`. A unit is *square-zero* if `tau_i = 0`.

## 1. A rank identity

**Theorem 1.** Let `char F != 2`, let `J` be an involution (`J^2 = I`) and `r = rank(J - I)`. Then
`rank(2K - Gamma) = N - r`. Explicitly `2K - Gamma = 2I - diag(tau) + Gamma_< - Gamma_>`
(`Gamma_<`, `Gamma_>` the strictly lower and upper parts).

*Proof.* Expanding the product, only the entries `Gamma_ij` with `i > j` occur, and
`J = I - X K^{-1} Y` with `X = [x_1 ... x_N]`, `Y = [y_1 ... y_N]^T`, `Gamma = Y X`. Hence
`Pi = (I - J)/2 = (1/2) X K^{-1} Y` is the projection onto the `-1` eigenspace of `J`; it is an idempotent of rank `r`
(`char != 2`). Put `Omega = K^{-1} Y X`. Since `(X)(K^{-1}Y) = 2 Pi` satisfies `t(t-2) = 0`,
`Omega^2 (Omega - 2) = K^{-1} Y [(2Pi)(2Pi - 2)] X = 0`. So the eigenvalue `2` of `Omega` is semisimple, and its
algebraic multiplicity equals that of `2 Pi` (the nonzero spectra of `AB` and `BA` agree with multiplicity), namely `r`.
Therefore `rank(2I - Omega) = N - r`, and `2K - Gamma = K (2I - Omega)` with `K` invertible. ∎

**Corollary 1.1 (shortest words).** If `tau_i != 2` for some `i` then `N >= r + 1`: the diagonal entry
`2 - tau_i` of `2K - Gamma` is nonzero. For square-zero units this is the bound `N >= r + 1` for a product of rank-one
nilpotent involution factors. More generally, if `A` is a set of units with `Gamma_ij = Gamma_ji = 0` for all
distinct `i, j` in `A` and `tau_i != 2` on `A`, the submatrix of `2K - Gamma` on `A` is invertible diagonal, so
`N - r >= |A|`. These pairings are those of the units of `J` as written.

*Remarks.* (i) A product of unipotent units has determinant 1, so `r` is even when all `tau_i = 0`.
(ii) The bound `N = r + 1` is attained by the explicit three-unit word on two fields (`r = 2`) and by the nine
nilpotent queries of the #6726 eight-field root (`r = 8`, `J = -I`); both are checked in `verify.py`.
(iii) Theorem 1 does not use unipotence: reflections (`tau = 2`) are allowed; a single reflection has `N = r = 1`.
The involution hypothesis is needed (a single shear has `N - r = 0`, `rank = 1`; checked).

**Lemma 1.2 (relative word).** For `T_i(S) = I + S u_i v_i^T`, `tau_i = v_i^T u_i != +-1`,
`M(S) = T_N(S) ... T_1(S)`, one has `M(-1) M(1)^{-1} = (A_1 X_1 A_1^{-1}) ... (A_N X_N A_N^{-1})` with
`A_i = T_N(-1) ... T_{i+1}(-1)`, `X_i = T_i(-1) T_i(1)^{-1} = I - 2 u_i v_i^T / (1 + tau_i)`: a product of `N` units.
(Telescoping: `A_{i-1} = A_i T_i(-1)`.) Verified exactly on the Whitehead word in `verify.py`.
This is how Theorem 1 applies to words in which a formal central `Q` is replaced by the two values `+-1`
and the ordinary controls do not depend on the sign.

## 2. Projection setting

**Setting.** `A` is an associative unital `F`-algebra, `B` a unital subalgebra, `E : A -> B` an `F`-linear map with
`E|_B = id` and `E(b a b') = b E(a) b'` for `b, b' in B` (a `B`-bimodule projection), and `Q in A` with `E(Q) = 0`.
No commutation of `Q` with anything is assumed. Matrices over `A` are `n x n`; `E` acts entrywise.
A *query word* is `M = T_N ... T_1`, `T_i = I + u_i Q v_i`, with `u_i` a column in `B^n` and `v_i` a row in `B^n`.
Ordinary controls (invertible matrices over `B` between the queries) are absorbed: conjugating the `i`-th query by the
product of the controls before it replaces `u_i, v_i` and leaves an overall factor in `GL_n(B)` on the left.
Write `U = [u_1 ... u_N]`, `V` for the matrix with rows `v_i`, `G = V U in M_N(B)` (`G_ij = v_i u_j`).

**Proposition 2.1.** `M = I + U W V` with `W = sum_{k>=0} (Q G_<)^k Q`, where `G_<` is the strictly lower part of `G`.
`W_ii = Q` and `W_ij = 0` for `i < j`. With `F := E(W)`: `F` is a strictly lower triangular matrix over `B`, and
`E(M) = I + U F V` exactly.

*Proof.* Multiplying out, `M` is the sum over index chains `i_k > ... > i_1` of
`u_{i_k} Q v_{i_k} u_{i_{k-1}} Q v_{i_{k-1}} ... u_{i_1} Q v_{i_1}`
`= u_{i_k} [ Q G_{i_k i_{k-1}} Q ... G_{i_2 i_1} Q ] v_{i_1}`. The bracket is the `(i_k, i_1)` entry of
`(Q G_<)^{k-1} Q`. Summing over chains gives the formula. Since `U, V` have entries in `B`, bimodularity gives
`E(U W V) = U E(W) V`. The diagonal of `E(W)` is `E(Q) = 0`; entries above the diagonal vanish. ∎

**Theorem 2 (rank identity).** Suppose `M = O_1 diag(g_1, ..., g_n) O_2` with `O_1, O_2 in GL_n(B)`, `g_j in ker E`
for `j <= r` and `g_j = 1` for `j > r`. Let `rho : B -> M_d(F)` be a unital representation and apply it blockwise.
Then `rank rho(I + F G) = (N - r) d`.

*Proof.* `E(M) = O_1 diag(E(g_j)) O_2 = O_1 diag(0_r, 1_{n-r}) O_2`, so `rank rho(E(M)) = (n-r) d`. By Proposition 2.1,
`rho(E(M)) = I + rho(U) rho(F V)`, and `dim ker(I + XY) = dim ker(I + YX)` (Sylvester) gives
`dim ker(I_{Nd} + rho(F) rho(G)) = nd - (n-r)d = rd`. ∎

(For every query word, with no target, the same computation gives
`rank rho(I+FG) - Nd = rank rho(E(M)) - nd`; this is checked on random words in `Q[S_4]`, Section 3.)

**Lemma 3 (window).** Let `F, G in M_N(M_d(F))` in blocks, `F` strictly lower block triangular, and let
`A = {k+1, ..., k+w}` be consecutive indices with `G_ij = 0` for all `i, j in A` (diagonal included). Then
`rank(I + F G) >= w d`. The statement and proof are characteristic free.

*Proof.* Let `H = I + FG`; its block row `i` is `e_i + sum_{j<i} F_ij G_j`, where `G_j` is block row `j` of `G` and
`e_i` block row `i` of the identity. Let `T` be the row space of `H` together with block rows `1..k` of `G`;
`dim T <= rank H + kd`. For `i <= k`, `e_i = H_i - sum_{j<i} F_ij G_j in T`, so `T` contains `T_0 = span(e_1..e_k)`
of dimension `kd`. Let `pi` be the projection onto the columns of `A`; `pi(T_0) = 0`, so `dim pi(T) <= dim T - kd <= rank H`.
For `i in A`, `pi(H_i) = pi(e_i) + sum_{j<=k} F_ij pi(G_j) + sum_{j in A, j<i} F_ij pi(G_j)`, and the last sum
vanishes because `G_ij = 0` on `A x A`. Hence `pi(e_i) in pi(T)` for every `i in A`, and these span all `w d`
coordinates of `A`. So `w d <= dim pi(T) <= rank H`. ∎

**Corollary 4 (window bound).** In the Setting, if `M` has the form of Theorem 2 and `w` consecutive units have
pairwise zero pairing (`v_i u_j = 0` for all `i, j` in the window, including `i = j`), then `N - r >= w`,
i.e. `N >= r + w`. The window may sit anywhere in the word.
*Proof.* Theorem 2 gives `rank rho(I+FG) = (N-r)d`; Lemma 3 gives `>= wd`. ∎

Checks: the window lemma holds on 6000 random exact instances with attained equality; consecutiveness is necessary
(the Whitehead word has `N - r = 1` and two orthogonal square-zero units that are not consecutive) and so is the zero
pairing (consecutive header units of one copy pair nontrivially).

## 3. Two instances of the Setting

**3.1 Parity sector.** `A = F[q]/(q^4 - 1)`, `B = F[q^2]`, `E(a + q b) = a` for `a, b in B`, `Q = q^{-1} = q^3`.
`E` is `B`-linear and `E(Q) = 0`. Ordinary controls may depend on `q^2` (for instance the gates that multiply by
`(1+i s)/2 + (1-i s) q^2 / 2`). Here `B` is commutative and `E` is the even part; evaluating at `q` and `-q` gives
`E(M) = (M(q) + M(-q))/2`.

**3.2 Uniform single-qubit Clifford cosets.** Let `C = (1+i)/2 [[1,-i],[-i,1]]`, `S = diag(1,i)`, `X`, `Z`.
Modulo scalars they generate a group of 24 elements, and the eight monomial matrices form a subgroup `H`
(both checked exactly in `verify.py`; `C^2 = X`). For `f` columns put `g^{(f)} = g^{\otimes f}`; `Q = C^{(f)}`.
The products `g^{(f)} h^{(f)}` are nonzero scalar multiples of `(gh)^{(f)}`, so the span `A_f` of the 24 matrices
is an algebra, and `B_f` (span of the eight monomial powers) a subalgebra containing `X^{(f)} = Q^2`, the
monomial wrappers, `S^{(f)}`, and uniform Pauli gates.

*Independence.* The entries of `g^{(f)}` are the degree-`f` monomials in the four entries of `g`, so the rank of the 24
matrices is the rank of evaluating degree-`f` forms at 24 points of `P^3`. It is `4, 10, 20, 23, 24, 24, 24` for
`f = 1..7` (exact), and once it is 24 it stays 24: if `ell` is a linear form not vanishing at any of the points,
multiplying by `ell` maps degree-`f` forms onto prescribed values at degree `f+1`. So the 24 powers are independent
exactly for `f >= 5` (over a field of characteristic 0 containing `Q(i)`).

*Projection.* For `f >= 5` define `E_f` as the coordinate projection of `A_f` onto `B_f` along the 16 non-monomial
powers. Because `H` is a subgroup, `h g h'` lies in `H` iff `g` does (checked on all 1024 triples), and the scalar
factors do not matter, so `E_f` is a `B_f`-bimodule map; `E_f(Q) = 0` since `C notin H`. The ordinary controls
covered are therefore all uniform monomial gates and their `F`-linear combinations, including non-commuting ones
(`S^{(f)}`, uniform Pauli gates, `q^2`-dependent gates); controls that are uniform non-monomial Cliffords, or that act
on a proper subset of the columns, are not in `B_f` (Section 5).

**Control.** In the noncommutative model `A = Q[S_4]`, `B = Q[D_4]`, `Q` a 3-cycle (same Setting, untwisted), 30 random
words satisfy Proposition 2.1 and the Sylvester identity exactly; with ordinary entries chosen outside `B`, the identity
`E(M) = I + UFV` fails in 12 of 12 trials.

## 4. The #6726 header

Specialising every body variable to 1 (a homomorphism when the body variables are central and the controls depend
on them centrally), the retained 606-event caller of #6726 acts on 34 fields. In the sector model 3.1 the events are:
`ADD`, `SCALE`, `SWAP` (ordinary, `q`-free), `LAMBDA` (ordinary, `q^2`-dependent), `QUERY` and `LOCAL` (the shear
`row_dst += q^{-1} row_src`, i.e. the unit `I + Q e_dst e_src^T`), `IDLE`, `IDLE_ONE` (trivial). `verify.py` replays
the events exactly in `Q(i)` at `q = 1, -1, i, -i`, finds `diag(q^{d})` with 32 odd exponents `d` and two even ones
(so `r = 32` targets lie in `ker E` and two are 1), extracts the `N = 33` units with all ordinary controls absorbed,
checks that each is square-zero, forms `G` and `F = E(W)`, and checks in both sectors `q^2 = +-1`:

* `E(M) = O (I + U F V)` equals `(M(q) + M(-q))/2` from the independent replay;
* `rank(I + F G) = 1 = N - r`.

So the header attains `N - r = 1` per port. **Replication.** Take `w` copies of the header with zero pairing between
copies (`G`, `F` block diagonal), ordered unit-major (copies commute). Then `N = 33 w`, `r = 32 w`,
`rank(I + FG) = w = N - r`, and the `w` copies of any one unit form a window with zero pairing. Checked exactly for
`w = 3`. By Corollary 4, no word of the Setting with a width-`w` window of mutually orthogonal square-zero units and
`r = 32 w` targets in `ker E` has fewer than `r + w` units: the `w` header deficits `-1` cannot be shared.

**Hypothesis used for the caller (not derived here).** A native call of width `P` contributes `P` mutually orthogonal
square-zero units at each of its positions (one per port), all ports share the single central `Q`, and cross-port
controls are in `B`. Under that reading the bound is `N - r >= P`, attained by `P` independent ports.

## 5. Scope

Covered: words in the Setting; ordinary controls in `B` (Section 3 lists the controls for each instance); targets
`O_1 diag(g) O_2` with `g_j in ker E` or `1`; any window position; any characteristic for Lemma 3 and
Corollary 4; Theorem 1 for `char != 2`.

Not covered, and not claimed: controls that do not commute with the body variables (the specialisation to 1 is then
not an algebra homomorphism) and uniform non-monomial controls or controls on a subset of columns (not in `B`); a native
whose per-port central part is not a square-zero unit (a reflection or other non-square-zero central action pairs with
itself, Lemma 3 then does not apply); a recursive supply in which query units are themselves produced by a job of
the same kind; positive characteristic for the Clifford instance (independence of the 24 powers is shown over
characteristic 0); targets other than `1` and elements of `ker E`; half-width or column-split units (no statement made).
Nothing here prices a word, constructs a caller or discharges the five framework assumptions of the cited words.

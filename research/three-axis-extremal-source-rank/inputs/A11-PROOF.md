# Selected source phases force an all-order binary Stein-rank floor

## 1. Exact claim and source boundary

Let `g >= 1`, `N = 2^g`, and `R_N = 2 ceil((N+3)/5)`. On each axis `l`, let `s_l` be a distinct odd prime and `t_l` a power of two with `s_l < t_l < 2s_l`. Put `delta_l=t_l-s_l`, `rho_l=t_l/s_l`. Take one common positive integer `alpha` and `a=pi alpha^2`. The retained source defines

    q_j = floor(rho*j+1/2), beta_j = rho*j-q_j,
    G_jk = exp(-a[(rho*k-q_j)^2-beta_k^2]).                 (1)

See `inputs/BILATERAL-LDU.md`, Statement and section 4. Its finite period uses `0 <= j < s`; its periodic matrix `N_source=Pi(G)` sums aliases. We use only the displayed unrounded, alias-deleted coefficients on that finite index list. This is already the source's column-normalized Gaussian, not the earlier raw resampling matrix. No new phase or chirp similarity is applied. A *same cell* has constant `q_j-j`, as in `inputs/PHASE-CELLS.md`.

**Theorem.** Fix an even integer `2 <= r <= R_N`. Suppose on every axis

    b_l = s_l-1-delta_l-2r^2-r > 0.                        (2)

There are sets `I_l subset {0,...,s_l-2}` with at least `b_l` elements each such that every `i_l in I_l` has `q_(i_l+1)=q_(i_l)+1`. For every choice of one such index on each axis, let

    C = tensor_l G^(l)[{i_l,i_l+1},{i_l,i_l+1}].           (3)

For every simultaneous permutation `P` of its `N` vertices,

    rank E(P C P^T) >= r,  rank E(P C^-1 P^T) >= r,        (4)
    E(A) = A-Z A Z^T,

where `Z` is the ordinary lower one-step nilpotent shift. The selected indices precede and work for all vertex orders. Their count concerns distinct starting indices / centered phase residues beta_i, not distinct physical cells q_i-i. The inverse in (4) is the inverse of (3), not a section of a larger source inverse.

This pointwise theorem retains the actual same-cell phase/chirp coefficients and removes a generic-parameter premise at this selected interface. It does not cover arbitrary phases, scheduled capped interiors, larger sections, periodic aliases, rounded coefficients or the complete analytic-recovery caller. All five framework assumptions and the accepted multiplication bound remain unchanged.

## 2. Exact source-grid and pair identities

Suppress the axis subscript. The integer `n_j=s beta_j=tj-sq_j` runs bijectively through `[-(s-1)/2,(s-1)/2]` for `0 <= j < s`: these are the balanced residues of `delta*j` modulo `s`. There are no half-integer ties because `s` is odd. Also `0 <= q_j < t`, since `rho(s-1)+1/2=t-rho+1/2<t`.

A same-cell unit step has `n_(i+1)=n_i+delta`, so it occurs exactly when

    -(s-1)/2 <= n_i <= (s-1)/2-delta.                    (5)

Writing `n=n_i`, direct substitution into (1) gives

    G[{i,i+1},{i,i+1}] = [[1,U],[V,1]],
    U=exp(-a A/s), V=exp(-a B/s),                         (6)
    A=2t-s+2n=s+2n_(i+1), B=s-2n, A+B=2t.                (7)

For the upper-right entry, `t(i+1)-sq_i=n_(i+1)+s`; the difference of its square and `n_(i+1)^2`, divided by `s^2`, is `A/s`. The reverse entry gives `B/s`. Thus (6) is a literal coefficient identity with no discarded similarity.

Condition (5) is equivalent to an odd `A` with `2delta+1 <= A <= 2s-1`. The odd integers in `[1,2s-1]` lift all residues modulo odd `s` uniquely; exactly `delta` lie below `2delta+1`. Each admissible lift determines `n=(A-(2t-s))/2` and `i=delta^-1 n mod s`.

A nonzero residue also removes the terminal index: if admissible `i=s-1`, the next value has `n_s=0`; a unit step would give `n_i=-delta`, hence `A=s`, the zero residue. Thus every admissible nonzero residue yields a pair inside `[0,s)`, without a period wrap. Both `A,B` are positive and

    0 < U V = exp(-2at/s) < 1.                            (8)

Every selected factor and its tensor are therefore invertible, although generally nonsymmetric.

## 3. A positive fraction of indices separate all bounded exponents

Assume `2r<s`. Range over the nonzero residues of `A`; write `B=2t-A` modulo `s`. A collision in the map

    (u,v) -> u A + v B mod s,  0 <= u,v <= r,             (9)

has a nonzero integer difference pair `(d,e)` with `|d|,|e| <= r` and

    (d-e) A = -2t e mod s.                               (10)

If `d=e != 0`, this is impossible: `s` is odd, `t` is a power of two, and `0<|e|<s`. Otherwise `0<|d-e|<=2r<s`, so (10) forbids at most one residue of `A`. There are `(2r+1)^2-1=4r^2+4r` nonzero difference pairs. Excluding the `2r` nonzero diagonal pairs, and pairing `(d,e)` with `(-d,-e)`, leaves at most

    2r^2+r                                               (11)

forbidden residues. Distinct pairs can give the same residue, so this is an upper bound, not an exact count. The zero residue has already been excluded. At most `delta` further residues have an odd lift below `2delta+1`. Section 2 therefore gives at least `s-1-delta-2r^2-r` distinct admissible starting indices for which (9) is injective.

The theorem's positive condition (2) implies `2r<s` for `r>=2`, so no additional hypothesis is hidden here. This establishes the asserted sets `I_l`. Their cardinalities count indices, not distinct cells. Arbitrary valid same-cell indices need not pass (9).

## 4. An exact nonzero polynomial for every order

We use the published predecessor `arbitrary-order-binary-gaussian-rank`, commit `085b30f8e036f69421d5953d0993ac4974ec3f24`; its exact proof is retained as `inputs/A9-PROOF.md`. It proves that for every ordering of the binary vertices there is a translation matching whose ordinary Stein graph has an even-path principal minor of size at least `R_N`, with determinant coefficient `+1` or `-1` isolated at a monomial. More explicitly, deleting two adjacent vertices from each closed alternating component leaves even paths; the resulting weighted path matrix has a unique perfect matching and determinant `+1` or `-1`.

The trimming argument from `fine-prime-binary-core-rank`, published commit `da06a3d10e06870a0279e33dd5056ded8d7e7a38`, reduces that certificate to any even size `r <= R_N`: retain an even endpoint prefix from each path, choosing sizes that sum to `r`. Every chosen path retains its unique perfect matching. The isolated-coefficient argument still applies. This is a principal minor of the **full displacement** `E(H)`, not displacement after compressing `H` to a smaller grid.

Now form the formal directed tensor

    H(U,V) = tensor_l [[1,U_l],[V_l,1]].                  (12)

For each order `P`, use the same size-`r` principal index set as above and let `F_P(U,V)` be its determinant in `E(P H(U,V) P^T)`. Specializing `U_l=V_l=Q_l` gives the nonzero symmetric certificate. Hence `F_P` itself is a nonzero integer polynomial. Every entry is a difference of two squarefree monomials, so its degree in each individual `U_l` or `V_l` is at most `r`.

Fix any selected indices from section 3, and put

    S = product_l s_l,  z = exp(-pi alpha^2/S),
    U_l = z^(A_l S/s_l), V_l = z^(B_l S/s_l).             (13)

Different monomials of `F_P` have different integer exponents after (13). Indeed, equality of two total exponents, reduced modulo `s_l`, gives

    A_l(u_l-u'_l)+B_l(v_l-v'_l) = 0 mod s_l,

because `S/s_l` is a unit modulo `s_l` and all other axes contribute multiples of `s_l`. The injection (9) forces both exponents equal on every axis. Thus substitution yields a nonzero polynomial in `z`, with no cancellation between distinct original monomials.

The number `z` is transcendental by the Gelfond-Schneider theorem: take base `-1`, logarithm `i*pi`, and algebraic irrational exponent `i alpha^2/S`. The resulting value is exactly (13). The original source is A. Gelfond, *Sur le septieme probleme de Hilbert*, 1934, pp. 623-634, logarithm-ratio theorem on p. 628; see `SOURCES.md`. Consequently every substituted `F_P` is nonzero. This proves the forward half of (4).

The argument specializes each order's minor separately. It does **not** multiply all `N!` minors before applying the bounded-degree guard. There is no generic-real-parameter exception: the fixed selected source coefficients satisfy the result pointwise. There is also no numerical lower margin from this transcendence argument.

## 5. The inverse and the precise representation consequence

For any invertible matrix `A`, take the two Schur complements of

    M = [[A,Z],[Z^T,A^-1]].

They show `rank E(A)=rank E_rev(A^-1)`, where `E_rev(B)=B-Z^T B Z`. Applying the same identity to `A^-1`, and writing `J` for order reversal, gives

    rank E(A^-1) = rank E_rev(A) = rank E(J A J).          (14)

No symmetry or positive-definiteness is required. Section 2 proves invertibility of the selected tensor. Since reversal is another ordering, the already proved forward theorem gives the inverse half of (4).

If a matrix is represented as a sum of `k` ordinary lower/upper triangular Toeplitz products `L(u_j) U(v_j)`, each term has displacement `u_j v_j^T`, so `k >= rank E(A)`. Thus (4) forces at least `r` such terms in every order. A format materializing their two length-`N` generator vectors separately requires at least `2Nr` scalar slots. This is a lower bound for that specified dense representation, not a general lower bound on arithmetic time, implicit generator descriptions, separable circuits, memory reuse or integer multiplication. The bound for the inverse concerns `C^-1`, not a principal section of the inverse of the larger source operator.

## 6. An eventual fine-prime guard with a square-root-prime cap

The retained `inputs/FINE-PRIME-PADDING.md`, section 1, supplies distinct odd primes with `delta_l/s_l <= 1/p^2`, and section 2 supplies the common positive integer `alpha`. Assume the explicit finite guards `p>=3` and `s_l>=p^4`. Put

    r = min(R_N, 2 floor(sqrt(s_min)/4)).                 (15)

This is even, at least two, and satisfies `r<=sqrt(s_l)/2`. Hence

    b_l >= s_l-1-s_l/9-s_l/2-sqrt(s_l)/2
        >= s_l/3-1 > 0,                                (16)

where the second inequality uses `s_l>=81`, so `sqrt(s_l)/2<=s_l/18`. This proves the theorem with at least the stated number of good starting indices per axis. The fraction concerns each individual axis; no dimension-independent density of the Cartesian product is asserted.

The retained scale is `log s_l = Theta(p^(1-epsilon))` for fixed `0<epsilon<1`, so the finite guard is eventual and the cap in (15) is `exp(Theta(p^(1-epsilon)))`. When `R_N` is below this cap, the complete predecessor generic rank floor becomes pointwise at selected source phases. For larger groups the proved floor saturates at the square-root-prime scale; it is not a linear-in-`N` theorem in that regime. This improves the earlier discovery route, which used a restricted family `B=K A mod s` and supplied only a polynomial-in-`p` sufficient cap. The full-residue counting argument is the single recorded evidence-driven pivot.

The source phase-cell report also has older norm/precision parameter regimes. Only its exact cell/grid definitions are used here; none of those old quantitative bounds is imported into (15). Nor does the existence of a pair in the source grid imply that a currently scheduled capped tile uses that pair.

## 7. Paid exact selection and remaining cost boundary

A sequential selector can find one good index per axis using only integer arithmetic. Enumerate nonzero residues, lift each to its odd representative `A in [1,2s-1]`, and reject `A<2delta+1`. For each survivor enumerate all integer pairs `(d,e)` in `[-r,r]^2` except `(0,0)`; reject if `(d-e)A+2te` is divisible by `s`. A surviving `A` determines `n` and `i` by section 2. The positive count proves termination. No hash table, sort or unit-cost matrix lookup is needed.

Each candidate costs `O(r^2)` modular operations on `O(log s)`-bit integers. Since (2) gives `r^2<s`, all axes cost at most

    O(g s_max^2 poly(log s_max)) bit operations.          (17)

Schoolbook multiplication/division and extended Euclid suffice for this conservative bound. The nested scans use `O(log s_max)` local arithmetic scratch, plus the input and the chosen output indices, which cost `O(g log s_max)` bits. Enumerating or storing every good index would require its own output charge; that is not part of this selector. Under the retained prime scale and polynomial `g`, (17) is `exp(o(p))`. It is a standalone setup bill, not a complete caller's amortized cost.

The selector produces indices only. It does not produce Gaussian coefficients, generators, permutations, inverse entries or their bit representations. No random-access transport, precision restoration or coefficient construction has been made free. Even the specified dense generator format still pays at least `2Nr` scalar slots; additional scalar precision and all access/transport costs remain.

## 8. Limitations and verification meaning

The exact polynomial specialization supplies no lower bound on determinant magnitude. Rounding a sufficiently small nonzero displacement minor can change its rank. No `Cp`-bit robustness or actual production-error bound follows. Gelfond-Schneider is a classical theorem used with checked premises, not a numerical experiment.

The source statement is confined to the selected square, two-point, alias-deleted factors of (1), their tensor, and that tensor's inverse. Periodic alias sums, arbitrary source phases, larger/rectangular tiles, different row and column permutations, principal sections of a larger inverse, and full analytic recovery require separate arguments. No universal impossibility for faster structured algorithms is asserted.

The exact verifier authenticates retained source bytes, compares literal nearest-grid coefficient exponents with (7), checks local exponent boxes against a separate difference test, and checks selected directed determinant polynomials both before and after substitution. Negative controls cover phase cuts, finite endpoints, insufficient guards, noninjective exponent boxes, denominator collisions and inverse/section confusion. These bounded checks corroborate the universal proof; they do not replace it. Independent review is recorded separately. No new kappa is claimed and no selected certificate is changed.

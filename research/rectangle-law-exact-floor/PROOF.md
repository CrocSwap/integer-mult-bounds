# Proof: the exact floor of an odd rectangle of residual ranks

Scoped proof over every field of characteristic not 2. The finite checks in
`verify.py` corroborate it; they are not part of the proof.

## 0. Setting and statement

Fix a field K with 2 != 0, integers u, h >= 1, and signs s_dc, s_df, s_ec, s_ef in
{+1, -1} with product -1 (an *odd* rectangle). For A_d, A_e in K^{u x h} and
B_c, B_f in K^{h x u} put

    C_xy = s_xy I_u - A_x B_y            (x in {d, e}, y in {c, f}),
    r_xy = rank C_xy,   Sigma = r_dc + r_df + r_ec + r_ef.

This is the cell of Lemma 1 of PR #6935 (DreamingOfClouds, `research/p104-root-cut-laws`) with
stage size u and hub count h in place of rho = u = h = 2; there it is proved that
Sigma >= min(rho, 2) for square rho x rho matrices.

**Theorem 1.** The least value of Sigma over all A_x, B_y is

    f(u, h) = max(0, 2u - h, 3u - 2h, 4u - 4h).

Equivalently: f = 0 for h >= 2u; f = 2u - h for u <= h <= 2u; f = 3u - 2h for
u/2 <= h <= u; f = 4(u - h) for h <= u/2. In particular f(rho, rho) = rho. It satisfies
the duality f(u, h) = 4(u - h) + f(h, u).

Throughout, G = [[s_dc, s_df], [s_ec, s_ef]]. Because the product of the four signs is -1,
s_df s_ec = -s_dc s_ef, so

    det G = s_dc s_ef - s_df s_ec = 2 s_dc s_ef != 0.                      (1)

## 1. Lower bounds

**Lemma A (block rank).** Sigma >= 2u - h.

*Proof.* Put M = [A_d; A_e] in K^{2u x h} and N = [B_c  B_f] in K^{h x 2u}. The block matrix
MN has blocks A_x B_y. Let S = G (x) I_u (a 2u x 2u matrix, blocks s_xy I_u). By (1) S is
invertible. Then S - MN is the block matrix C = [[C_dc, C_df], [C_ec, C_ef]]. It is the sum of
four matrices, each zero outside one block and of rank r_xy, so rank C <= Sigma. Hence
2u = rank S <= rank(MN) + rank C <= h + Sigma. QED

**Lemma B (cell rank through the dual product).** For s != 0, A in K^{u x h}, B in K^{h x u},

    rank(s I_u - A B) = u - h + rank(s I_h - B A).

*Proof.* If (s I_u - AB)v = 0 then ABv = sv, so BA(Bv) = s(Bv); and Bv = 0 would force
sv = ABv = 0. So v -> Bv maps ker(s I_u - AB) injectively into ker(s I_h - BA). The map
w -> Aw does the same in the other direction. The kernels have a common dimension d, and the
ranks are u - d and h - d. QED

**Lemma C (dual block rank).** With D_xy = s_xy I_h - B_y A_x, the sum of the four ranks
rank D_xy is at least 2h - u.

*Proof.* Put M' = [A_d  A_e] in K^{u x 2h}, N' = [B_c; B_f] in K^{2h x u}. The block matrix
N'M' has blocks B_y A_x and rank at most u. S' = G^T (x) I_h is invertible by (1), and
S' - N'M' has the blocks D_xy (row block y, column block x). As in Lemma A,
2h = rank S' <= u + sum rank D_xy. QED

**Proof of the lower bound.** Lemma B on each cell gives
Sigma = 4(u - h) + sum rank D_xy. Lemma C then gives Sigma >= 4(u - h) + max(0, 2h - u)
>= max(4u - 4h, 3u - 2h). Lemma A gives Sigma >= 2u - h, and Sigma >= 0. QED

## 2. Attainment

**Lemma D (one perturbed block).** Let n >= 1 and let G'' = [[a, b], [c, e]] have entries +-1 and
product abce = -1. For 0 <= k <= n let Pi_k = diag(1^k, 0^(n-k)) and let X be G'' (x) I_n with
2a Pi_k subtracted from its top-left n x n block. Then rank X = 2n - k.

*Proof.* The bottom-right block e I_n is invertible. For a block matrix [[P, Q], [R, T]] with T
invertible, rank = rank T + rank(P - Q T^-1 R). Here the Schur complement is
(a I - 2a Pi_k) - b c e^-1 I = (a - bce) I - 2a Pi_k. From abce = -1 and a^2 = 1 we get
bce = -a, so a - bce = 2a, and the complement is 2a (I - Pi_k), of rank n - k because
2 != 0. So rank X = n + (n - k). QED

**Case h >= u.** Let k = max(0, 2u - h) <= u and let X be the matrix of Lemma D with n = u,
G'' = G. Then rank X = 2u - k <= h. Choose a rank factorisation X = MN with M of width exactly h
(pad with zero columns), and read A_d, A_e as the top and bottom u rows of M and B_c, B_f as the
left and right u columns of N. Then A_x B_y is the (x, y) block of X, and
C_xy = (S - X)_xy, which is zero except C_dc = 2 s_dc Pi_k. So Sigma = k = max(0, 2u - h)
= f(u, h), because for h >= u the term 2u - h dominates 3u - 2h and 4u - 4h.

**Case h < u.** Let k' = max(0, 2h - u) <= h and let X' be the matrix of Lemma D with n = h and
G'' = G^T = [[s_dc, s_ec], [s_df, s_ef]]. Then rank X' = 2h - k' <= u. Factor X' = N'M' with N'
of width exactly u, put B_c, B_f for the top and bottom h rows of N' and A_d, A_e for the left and
right h columns of M'. Then B_y A_x is the (y, x) block of X', so D_xy = (S' - X')_yx is zero
except D_dc = 2 s_dc Pi_k'. By Lemma B, Sigma = 4(u - h) + k' = 4(u - h) + max(0, 2h - u)
= max(4(u - h), 3u - 2h) = f(u, h), because for h < u the term 2u - h is dominated. QED

Rank factorisations exist over every field, and the only place 2 != 0 is used is Lemma D and (1),
so attainment holds over every field of characteristic not 2. `verify.py` builds the
factorisations explicitly over Q for 1 <= u, h <= 8 and all eight odd sign patterns.

## 3. Corollary: Theorem S for any stage size and hub count

Hypothesis (S_u) is hypothesis (S) of the source with u x u in place of 2 x 2: L = 18 stages of
u units each, Gamma_dc the u x u matrix of products y_u . x_v over all coordinates for stage d
before stage c, and sgn(d - c) Gamma_dc = Xi_d H_c with Xi_d, H_c invertible u x u for d != c.
Take any h hub coordinates; let Xi'_d (u x h) hold the y-entries of stage d at the hubs and
H'_c (h x u) the x-entries of stage c. The cell with the hubs removed is
s Xi_d H_c - Xi'_d H'_c = Xi_d (s I - A_d B_c) H_c with A_d = Xi_d^-1 Xi'_d and
B_c = H'_c H_c^-1, so R_dc = rank(s I - A_d B_c) with s = sgn(d - c), exactly as in the source.

**Corollary 2.** Under (S_u), for any h hubs and char K != 2,

    sum over d != c of R_dc >= 72 f(u, h).

*Proof.* Lemma 2 of the source gives 72 pairwise cell-disjoint rectangles in the 18 x 18
off-diagonal grid, each with odd sign product (`verify.py` recomputes the 72 rectangles, their
disjointness and their parity). Apply Theorem 1 to each. QED

At u = h = rho this is 72 rho. For rho = 2 it is the 144 of Theorem S. For two hubs and u >= 4
units it is 288 (u - 2).

## 4. Exactness at u = h, and the packing number

**Proposition 3.** For u = h = rho and L = 18 the least possible total over all A_d, B_c is
exactly 72 rho.

*Proof.* The lower bound is Corollary 2. For the upper bound take A_d = x_d I_rho and
B_c = y_c I_rho with x, y in {+1, -1}^18. The cell is (sgn(d - c) - x_d y_c) I_rho: zero if
x_d y_c = sgn(d - c), and 2 sgn(d - c) I_rho of rank rho otherwise. An exhaustive search over x
(2^18 choices, the best y per column) finds the least number of mismatching off-diagonal cells to
be 72 (finite certificate). The total is then 72 rho. QED

The same search gives ⌊(L - 1)^2 / 4⌋ mismatches for every L from 2 to 18 (finite computation;
no general-L proof is claimed). Since every odd rectangle forces at least f(1, 1) = 1 mismatch in
the scalar case, 72 is also the largest number of cell-disjoint odd rectangles in the L = 18 grid:
a larger packing would contradict the scalar solution with 72 mismatches. So the packing of Lemma 2
cannot be improved to a larger floor at u = h.

## 5. What is not claimed

* Nothing about whether any root with rho > 2 satisfies (S_u), about the hub rank law, Theorem H,
  the cut costs or any price. (S_u) is a matrix hypothesis here.
* For u != h the grid floor 72 f(u, h) is a lower bound only. It is vacuous where f = 0 (for
  example h >= 2u), and no matching total is claimed away from u = h.
* Characteristic 2 is excluded: for K = F_2 the matrix G is singular and the floor is 0 at
  (u, h) = (1, 1) and (2, 2) (checked exhaustively in `verify.py`).

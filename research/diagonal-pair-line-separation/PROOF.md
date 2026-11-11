# Proof of the line exclusion

## Setting

Let `F` be a field, `G` a group, `L` a label set, and `F[G]` the group algebra.
For a rank-one idempotent `N` in `M_2(F)` and `g in L`, a call is

    D_N(g) = (I - N) + [g] N.

Fix `N_1, ..., N_k` and labels `g_1, ..., g_k`. Expanding the product over the
`2^k` subsets `U` of positions gives the identity in `M_2(F[G])`

    P := D_{N_1}(g_1) ... D_{N_k}(g_k) = sum_U [g_U] P_U,                (1)

where `g_U` is the product of the labels at the positions of `U` in increasing
order, `P_U = product_{i in U} N_i` in increasing order, and `P_empty = I`.
Every matrix entry of `P` is an element of the commutative ring `F[G]`.

## Common image line

Suppose all `N_i` have the same image line, so `N_i = u v_i^T` for one nonzero
`u` and vectors `v_i`. Idempotence gives `v_i^T u = 1`:

    N_i N_i = u (v_i^T u) v_i^T = u v_i^T = N_i.

Hence for every `i, j`

    N_i N_j = u (v_i^T u) v_j^T = u v_j^T = N_j.                          (2)

By (2) and induction on the size of `U`, every nonempty `P_U` is `N_{max U}`:

    N_{i_1} N_{i_2} ... N_{i_r} = N_{i_r}   for i_1 < ... < i_r.

Substituting in (1), with `c_j := sum_{V subseteq {1..j-1}} [g_V]` and
`[g_U] = [g_{U without j}] [g_j]` for `U` with maximum `j`,

    P = I + sum_{j=1}^k c_j [g_j] N_j = I + u w^T,
    w^T := sum_j c_j [g_j] v_j^T.                                         (3)

Every entry of `u w^T` is `u_i` times an element of `F[G]`, and `u_i` lies in
the central subfield `F`. Therefore the determinant of `P - I` vanishes
identically in `F[G]`:

    det(P - I) = 0.                                                       (4)

## Common kernel line

Suppose all `N_i` share a kernel line, so `N_i = u_i v^T` for one nonzero `v`.
Idempotence gives `v^T u_i = 1`, hence `N_i N_j = u_i (v^T u_j) v^T = N_i`.
The same induction gives `P_U = N_{min U}`, and (1) becomes

    P = I + w v^T,   w := sum_j c'_j [g_j] u_j,

so (4) holds again.

A family with a single repeated projector is a special case of both paragraphs:
all its members share an image line and a kernel line.

## The determinant is not zero for a separated pair

Let `a != b` be elements of `G`. We show

    ([a] - 1)([b] - 1) != 0    in F[G]     for every field F.             (5)

The product is `[ab] - [a] - [b] + 1`. Its support is contained in
`{ab, a, b, e}` with integer coefficients `+1, -1, -1, +1` on the four basis
elements, where repeated elements are collected. Since `a != e`, `b != e` and
`a != b`, the only possible collisions are `ab = e`, `ab = a`, `ab = b`, and
`ab` distinct from all of them.

- `ab = a` forces `b = e`, excluded. `ab = b` forces `a = e`, excluded.
- `ab = e`: the coefficient of `e` is `+1 + 1 = 2` and the coefficients of `a`
  and `b` are `-1`. If `a != b` then `[e]`, `[a]`, `[b]` are distinct basis
  elements, so the product is nonzero because `2 != 0` or `a`, `b` are distinct
  from `e`. If `a = b` the case is excluded by hypothesis.
- Otherwise `ab`, `a`, `b`, `e` are four distinct basis elements and the
  coefficient of `ab` is `1 != 0`.

In every case some basis coefficient is nonzero in `F`, so (5) holds.

Now assume `P = diag([a],[b])`. Then `P - I = diag([a]-1, [b]-1)` and

    det(P - I) = ([a] - 1)([b] - 1).

By (5) this is nonzero whenever `a != b`, contradicting (4). This proves
Theorem 1: a common image line or a common kernel line can never produce a
diagonal pair with distinct targets, at any length, over any field and any
group.

## Corollary: line separation is necessary

Let `a != b` and suppose neither is a product of at most two labels. If a
product equals `diag([a],[b])`, Theorem 1 excludes every family with one image
line or one kernel line. Hence the projector list contains two projectors with
distinct image lines and two with distinct kernel lines. A repeated projector
family is excluded as well.

## Two calls never suffice

Let `P = D_{N_1}(g_1) ... D_{N_k}(g_k) = diag([a],[b])` with `k <= 2`.

*Normalisation.* For `S in GL_2(F)`, conjugating the whole product gives

    S P S^{-1} = D_{S N_1 S^{-1}}(g_1) ... D_{S N_k S^{-1}}(g_k),

and `S diag([a],[b]) S^{-1} = diag([a],[b])` because `[a]` and `[b]` are
central scalars. Rank-one idempotents are conjugate, so we may assume
`N_1 = E00`.

*Case `k <= 1`.* Then `P - I` is either `0` or `(1 + [g_1]) N_1`, which has
determinant zero, while `diag([a]-1, [b]-1)` has determinant
`([a]-1)([b]-1) != 0` by (5). Contradiction.

*Case `k = 2`.* Put `t_2 = 1 + [g_2]`, which is nonzero because the coefficient
of the identity basis element is `1`. With `N_1 = E00`,

    P = diag([g_1], 1) (I + t_2 N_2).

A product of two diagonal matrices is diagonal, and `diag([g_1], 1)` is
invertible in the total ring of fractions, so `Q := I + t_2 N_2` is diagonal.
Writing `N_2 = (p, q; r, s)`, the off-diagonal entries of `Q` are `t_2 q` and
`t_2 r`. Since `F[G]` is a free `F`-module and `t_2 != 0`, `t_2 q = 0` forces
`q = 0`, and similarly `r = 0`. So `N_2` is diagonal, hence `N_2` is `E00` or
`E11`.

Four possibilities remain, and each has a target that is the identity or a
single label:

    D_E00(g_1) D_E00(g_2) = diag([g_1 g_2], 1),
    D_E00(g_1) D_E11(g_2) = diag([g_1], [g_2]),
    D_E11(g_1) D_E00(g_2) = diag([g_2], [g_1]),
    D_E11(g_1) D_E11(g_2) = diag(1, [g_1 g_2]).

In each case `a` or `b` is `e` or a single label, so it is a product of at most
two labels, contradicting the hypothesis. This proves Theorem 2.

## What the verifier checks

`verify.py` reconstructs each field from its addition and multiplication, builds
the rank-one idempotent inventory directly from `N^2 = N` and `trace(N) = 1`, and
then checks by exact arithmetic:

- the inventories `q(q+1) = 6, 12, 20, 30` for `F2, F3, F4, F5`;
- every ordered pair in every image-line and kernel-line class satisfies (2) or
  its transpose (`24, 72, 160, 300` pairs);
- every nonempty subset product of every enumerated same-line tuple collapses to
  the last or first projector (`7,812 / 71,736 / 43,400 / 123,960` checks);
- the determinant of `P - I` vanishes for each such tuple, computed by exact
  expansion in the group algebra of the free abelian group on the positions
  (`372 / 2,904 / 3,400 / 9,360` tuples at the lengths shown in the run line);
- the two-call diagonal-forcing step: for every projector `N_2`, the product
  `D_E00(g_1) D_{N_2}(g_2)` is diagonal if and only if `N_2` is diagonal;
- the positive control `D_E00(x)^3 D_E11(y)^3 = diag([x^3],[y^3])`, whose
  determinant is nonzero with the four predicted coefficients, and the
  mixed-line control `D_E00(x) D_E11(y)` with a nonzero determinant.

The free abelian group is a commutative instance, which is what the rank
argument uses; the verifier is finite corroboration, not a proof kernel. It does
not enumerate tuples outside the same-line families and is not a census.

## Remaining proof obligations

- The general `F4`, `F5`, odd-characteristic and larger-width six-call floors
  remain open. Nothing here bounds tuples with two or more image lines.
- Theorem 2 is a written argument; only the diagonal-forcing step is machine
  checked.
- No native, compiler, supplier or kappa claim is made or implied.

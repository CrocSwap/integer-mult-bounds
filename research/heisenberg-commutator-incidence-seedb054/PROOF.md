# Bipartite commutator incidence tariff

## Theorem

Let `L` and `R` be finite index sets of sizes `m` and `n`, and let `E` be a
bipartite edge set in `L × R`. For each edge `e=(i,j)`, choose a nonnegative integer multiplicity
`p_e`, and put `P = sum_e p_e`. In the group algebra over `F2` of

```text
H(m,n) = { (u,v,Z) : u in F2^m, v in F2^n, Z in M_(m x n)(F2) }
(u,v,Z)(u',v',Z') = (u+u', v+v', Z+Z'+u(v')^T),
```

write `x_i=(e_i,0,0)`, `y_j=(0,e_j,0)` and `z_ij=(0,0,E_ij)`. Thus
`x_i y_j x_i y_j = z_ij`, and every `z_ij` is central. Let `r >= P`, assign
disjoint sets `S_e` of `p_e` register coordinates, and let `P_e` be the
diagonal projection onto `S_e`.

The target is the diagonal matrix which has `[z_ij]` on the coordinates in
`S_(i,j)` and the group-algebra identity on every other coordinate. A paid
factor is

```text
D_N(g) = I_r + ([g]+[1]) N,
g in {x_i : i in L} union {y_j : j in R},
N in M_r(F2), rank(N)=1.
```

Arbitrary scalar `GL_r(F2)` maps may be interspersed for free, but the final
target is expressed in the original coordinates. Each paid occurrence costs
one. Every finite `r`, including arbitrary restored dirty spectators, has exact minimum

```text
4 P.
```

The smallest cyclic incidence instance is `K_(2,2)` with one target for each
edge; it has four distinct central outputs and exact cost 16. The preceding
UT4 shared-middle result has a two-edge path incidence pattern. This result
extends that rank-nullity mechanism to arbitrary bipartite target graphs;
`K_(2,2)` is its first cyclic case.

## Attaining word and accounting

For each edge `e=(i,j)` and each `t in S_e`, use the four factors

```text
D_(E_tt)(x_i) D_(E_tt)(y_j) D_(E_tt)(x_i) D_(E_tt)(y_j).
```

At coordinate `t` these multiply to `[x_i y_j x_i y_j]=[z_ij]` and act as
identity at every other coordinate. Distinct diagonal supports do not
interact. This gives exactly `4 p_e` paid calls on edge `e`, or `4P` total;
every one of the four occurrences is charged. No scalar preparation, clean
role, COPY, ERASE, or auxiliary operation is used.

The call tariff is deliberately optimistic and complete only for this formal
alphabet. It does not price a physical source/copy/frame/hosting/restoration/
precision/interface implementation. Consequently it is not a selected
supplier bill and supplies no `kappa` change.

## Lower bound

Free scalar `GL_r(F2)` maps may be normalized away. Push them through the paid
factors by conjugation; a rank-one `N` remains rank one. Augmentation
`[g] -> 1` sends every paid factor and the target to identity, so the
remaining scalar map must itself be identity. It suffices to consider pure
words in the displayed paid factors.

Fix an active edge `(i,j)`. The map

```text
rho_ij(u,v,Z) = [[1, u_i, Z_ij], [0, 1, v_j], [0, 0, 1]]
```

is a group homomorphism to `UT3(F2)`: its top-right product term is exactly
`u_i v'_j`. It sends `x_i` to `I+E12`, `y_j` to `I+E23`, all other listed
generators to identity, and `z_kl` to `I+E13` exactly when `(k,l)=(i,j)`.
The contragredient `rho_ij^vee(g)=(rho_ij(g)^(-1))^T` is also a homomorphism;
it sends the same edge's central element to `I+E31`.

Write each occurrence of a label `g` as `N_s=a_s b_s^T`. Let `X_g` have
the `a_s` as columns and `Y_g` have the `b_s^T` as rows; their common inner
dimension is the number `n_g` of occurrences of `g`.

Under `rho_ij`, a factor labeled `x_i` contributes the block `E12 ⊗ N_s`,
and a factor labeled `y_j` contributes `E23 ⊗ N_s`. Comparing the `(1,2)`
block with the target forces `sum_(s:g_s=x_i) N_s=0`; similarly the `(2,3)`
block forces `sum_(s:g_s=y_j) N_s=0`. For any active vertex one of its
incident edges therefore gives

```text
X_g Y_g = 0,  rank(X_g) + rank(Y_g) <= n_g.             (1)
```

The `(1,3)` block of the natural representation is the ordered sum
`sum_(s<t, g_s=x_i, g_t=y_j) N_s N_t`, which must equal `P_(i,j)`.
Consequently `im(P_(i,j))` is contained in `im(X_(x_i))` and
`row(P_(i,j))` is contained in `row(Y_(y_j))`. The `(3,1)` block in the
contragredient representation gives the reverse ordered sum equal to the
same `P_(i,j)`. Hence `im(P_(i,j))` is also contained in `im(X_(y_j))`, and
its row space is contained in `row(Y_(x_i))`.

More explicitly, for every left vertex `i`, the disjoint target coordinate
sets on incident edges give

```text
rank(X_(x_i)) >= sum_(j:(i,j) in E) p_(i,j),
rank(Y_(x_i)) >= sum_(j:(i,j) in E) p_(i,j).
```

For every right vertex `j` the analogous two inequalities hold with the
column sum `sum_i p_(i,j)`. Equation (1) therefore implies

```text
n_(x_i) >= 2 sum_j p_(i,j),
n_(y_j) >= 2 sum_i p_(i,j).
```

Summing over all label vertices counts every edge multiplicity once at each
endpoint, so the number of paid factors is at least `2(2P)=4P`. Labels not
incident to a target edge only add nonnegative calls. The explicit word
attains the bound, proving exactness for every finite bipartite graph and all
finite dirty register counts.

The argument uses only necessary homomorphic images for its lower bound; the
upper word is separately checked in the full formal group algebra. No
finite-address test is used to infer the universal statement.

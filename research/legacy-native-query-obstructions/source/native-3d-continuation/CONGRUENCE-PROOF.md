# A bound from reduction modulo 4

## Exact statement

Let `O` be the ring of rational numbers with odd denominators. Let `G` be a subgroup of `GL_m(O)`. Suppose that each element of `G` is congruent to `I_m` modulo 2. Let `z = -I_m` belong to `G`.

For each query, let `N_i` be a binary rank-one idempotent in `Mat_r(F2)`. Let `g_i` belong to `G`, with `rank_Q(g_i - I_m) = 1`. Suppose that the exact native word has endpoint

`I_r + (z - 1) D`

in `Mat_r(F2[G])`, where `D` is a constant binary idempotent of rank `p`. Then the word has at least `p*m` queries.

This statement permits arbitrary dirty helpers when the endpoint restores every helper. It does not apply to initialized or discarded helpers. It does not assert that all rational query maps have a common basis with the stated congruence property.

## Proof

Use the ring `R = F2[e]/(e^2)`. For `g = I_m + 2 A`, define

`a(g) = A modulo 2`,

`rho(g) = I_m + e a(g)`.

The definition is valid because `A` has entries in `O`. Reduction of an odd denominator modulo 2 is valid. If `g = I + 2 A` and `h = I + 2 B`, then

`(g*h - I)/2 = A + B + 2 A B`.

Thus `a(g*h) = a(g) + a(h)`, and `rho(g*h) = rho(g) rho(h)`. Inverses are in the same congruence subgroup: reduction of `g` modulo 2 is `I`, and `g^-1 - I = -2 g^-1 A`. Therefore `rho` is a group representation. Extend it linearly to the group algebra over `F2`.

The matrix `A_i = (g_i - I)/2` has rational rank one. Every minor of size two is zero in `O`. The same minors are zero after reduction modulo 2. Therefore `rank_F2(a(g_i)) <= 1`.

The image of the native query is

`rho(H_Ni(g_i)) = I_rm + e (N_i tensor a(g_i))`.

Since `e^2 = 0`, the image of a word of `q` queries is

`I_rm + e sum_i (N_i tensor a(g_i))`.

For `z = -I_m`, we have `(z - I_m)/2 = -I_m`. Therefore `rho(z) = (1+e) I_m`. The stated endpoint maps to

`I_rm + e (D tensor I_m)`.

Equality gives

`sum_i (N_i tensor a(g_i)) = D tensor I_m`.

Each matrix on the left has rank at most one. The matrix on the right has rank `p*m`. Rank subadditivity gives `q >= p*m`.

## Use in the current lane

For three productive DATA roles and three ADDRESS coordinates, this bound is nine queries. The bound covers infinite congruence subgroups. In particular, it removes a nomination with coordinate flips, two equal integral reflections `R = I - 2 u v^T`, and three plane transvections whose entries are all congruent to `I` modulo 2.

A nomination with an odd transvection parameter, a half parameter, or a dense map with odd entries can fail the hypothesis. The bound must be checked in one common rational ADDRESS basis before it is used.

This proof is original work in this packet. It does not use a finite search or a classification of rational groups.

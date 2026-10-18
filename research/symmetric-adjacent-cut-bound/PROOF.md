# Symmetric groups with adjacent calls: the exact dirty-register bill

This is an all-parameter written proof in the formal operation model below.
The package's finite checks are corroborating executable evidence, not a
substitute for this proof or a formal-kernel verification. The result gives
no physical BIT supplier, recursive child profile, precision estimate, or
new multiplication exponent.

## The model and theorem

Fix an integer `n>=2`. Write `S_n` for permutations of `{1,...,n}`, with
composition `gh=g after h`, so `(gh)(a)=g(h(a))`. The coefficient ring is
the full, generally noncommutative group algebra

```
A = F2[S_n],     [g][h]=[gh],     1=[e].
```

The formal symbols `[g]` form an F2 basis: equality means equality of every
group coefficient, not equality in a chosen quotient representation.
Use column vectors of `R` registers, with `R>=W` finite. Matrix products
act rightmost first. Every register entrance is arbitrary; in particular,
no spectator is assumed to be zero. One may interpret the formal boundary
on arbitrary columns in `A^R`, where matrices multiply on the left.

The paid address labels are exactly the adjacent transpositions

```
s_i=(i,i+1),     1<=i<n.
```

One paid call, of cost one, is

```
D_N(s_i) = I_R + ([s_i]+1)N,
N=u v^T in M_R(F2),     v^T u=1.
```

Thus `N` ranges over every binary rank-one idempotent, not just coordinate
projectors. Scalar entries of `N` commute with group-algebra entries. Every
such call is invertible and is its own inverse: `[s_i]^2=1` gives
`([s_i]+1)^2=0` in characteristic two. Arbitrary scalar `GL_R(F2)` maps
are free and may occur anywhere. They mix register roles identically at
every address. No other free address maps, resets, erasures, COPY operations,
or clean allocations are included.

For prescribed `w_1,...,w_W in S_n`, the complete required boundary is

```
T = diag([w_1],...,[w_W],1,...,1) in M_R(A).          (1)
```

All spectators must be restored to their individual entrance values, and
every off-diagonal role coupling must vanish. Every paid call used for
preparation, computation, or restoration counts. There is no deferred or
uncharged inverse cleanup.

Define the ordinary inversion count

```
inv(w) = #{(a,b): 1<=a<b<=n and w(a)>w(b)}.
```

**Theorem.** The exact minimum number of paid calls realizing (1) is

```
L = sum_(j=1)^W inv(w_j).                           (2)
```

This holds for every finite `R>=W`, every permitted interleaving with free
scalar maps, and all binary rank-one idempotents. The attaining circuit
uses only coordinate projectors, no free scalar changes, and no extra
roles. Empty target lists have minimum zero; the `R=W=0` case is the
vacuous empty identity.

## Ordered pairs supply a subadditive cut rank

Let

```
Omega = {(a,b): 1<=a,b<=n, a!=b},
H = {(a,b): a<b},     K = {(a,b): a>b}.
```

Let `V=F2^Omega`, with basis `e_(a,b)`, and define permutation matrices by

```
P_w e_(a,b) = e_(w(a),w(b)).
```

The product convention gives `P_g P_h=P_(gh)`. This action therefore
extends linearly to an algebra homomorphism `rho:A -> End_F2(V)`.
Extend it entrywise to register matrices, acting on `F2^R tensor V`.
The cut separates all `R` copies of H from all `R` copies of K. For any
operator M on this represented space, put

```
q(M) = rank_F2 M[K,H],
```

where the block takes H-supported inputs to K-supported outputs and both
index sets include every scalar role.

For arbitrary operators U and V on the same space, block multiplication
gives

```
(UV)[K,H] = U[K,H] V[H,H] + U[K,K] V[K,H].
```

The rank of a sum is at most the sum of the ranks, and multiplying a
matrix on either side cannot increase its rank. Consequently

```
q(UV) <= q(U)+q(V).                                 (3)
```

This inequality needs neither invertibility nor commutativity. It can
therefore be iterated over a circuit in its actual chronological order.

A free scalar operation S is represented by `S tensor I_V`. It preserves
both address halves, so `q(S tensor I_V)=0`. A paid call is represented by

```
rho_R(D_N(s_i)) = I_(R*|Omega|) + N tensor (P_(s_i)+I_V).
```

The identity has no crossing block. The paid crossing block is thus

```
N tensor P_(s_i)[K,H].                              (4)
```

Exactly one increasing ordered pair crosses under `s_i`: `(i,i+1)` goes
to `(i+1,i)`. To verify completeness, if neither entry is i or i+1, both
entries are fixed. If only one entry is moved, its value changes by one
without passing the other entry, which is outside `{i,i+1}`. Its order
is unchanged. Hence `P_(s_i)[K,H]` has exactly one nonzero entry, of value
one. Formula (4) contains one copy of N and otherwise zero blocks, after
reordering rows and columns. Its rank is exactly `rank_F2 N=1`.

For general w, `P_w[K,H]` has a nonzero column exactly for each pair
`a<b` with `w(a)>w(b)`. These nonzero columns are distinct standard basis
vectors, because w permutes Omega bijectively. Therefore

```
rank_F2 P_w[K,H] = inv(w).                          (5)
```

The represented target (1) is diagonal in scalar roles. Its crossing
block is the direct sum of the crossing blocks for the `w_j`, followed
by zero blocks for the identity spectators. Ranks of direct sums add,
so (5) yields

```
q(rho_R(T)) = sum_j inv(w_j) = L.                    (6)
```

Any formal circuit equality with target T remains an equality after
applying `rho_R`. If the circuit has C paid calls, (3), the zero free-map
charges, and (4) imply `q(rho_R(T))<=C`. Equation (6) proves `C>=L`.
Every intermediate role, including arbitrary dirty spectators, is already
included in this inequality. No bound on R beyond finiteness was used.

## Free-map normalization is consistent with the complete endpoint

The cut argument handles interleaved scalar maps directly, so it needs
no normalization assumption. Nevertheless, the familiar normalization
of the predecessor register model remains valid here. For scalar S,

```
S D_N(s_i) S^-1 = D_(S N S^-1)(s_i).                (7)
```

Conjugation preserves binary rank, idempotence, and the class of allowed
N. Sliding free scalar maps to one end therefore leaves allowed paid
factors and a single scalar factor S_total.

Augmentation `epsilon:A -> F2`, defined by `epsilon([g])=1`, is an
algebra homomorphism even though A is noncommutative. Each paid factor
augments to `I_R`, and (1) also augments to `I_R`. Thus the product of
all free scalar maps, in its actual order, is `S_total=I_R`. This is not
permission to leave an arbitrary scalar output map or dirty coupling.
It confirms that the normalized and interleaved models have the same
complete formal endpoint contract.

## A formal attaining word, including chronological order

For a target role j, let `E_j` be its coordinate projector. For any
`g in S_n` abbreviate

```
T_j(g) = I_R + ([g]+1)E_j.
```

This is the diagonal matrix with `[g]` in coordinate j and 1 elsewhere.
Direct multiplication in the full formal algebra gives

```
T_j(g) T_j(h) = T_j(gh).                            (8)
```

The notation `T_j(g)` in (8) does not introduce a free or unit-cost
nonadjacent call. It is a convenient way to state the formal identity;
only `T_j(s_i)=D_(E_j)(s_i)` is an allowed paid primitive. Matrices
`T_j(g)` and `T_k(h)` commute for `j!=k`, even when g and h do not.

Here is a deterministic construction of a word of length `inv(w)`.
Start with the one-line list `w(1),...,w(n)`. Whenever an adjacent descent
`w(i)>w(i+1)` occurs, swap those two positions by right multiplication
by `s_i`; for determinism, one may choose the least such i at each step. The proof
works for any adjacent-descent order; the producer uses bubble-sort sweeps
and the independent checker reconstructs shortest paths by breadth-first search.
This decreases the inversion count by exactly one: the inversion of
the swapped pair disappears, while for each other position its total
number of inversions with the two swapped entries is unchanged. If no
adjacent descent remains, the list is increasing and hence equals
`1,...,n`. Thus this process makes exactly `ell=inv(w)` swaps. Calling
the successive transpositions `t_1,...,t_ell`, it gives

```
w t_1 ... t_ell = e,
w = t_ell ... t_1.                                 (9)
```

Execute the paid coordinate calls

```
D_(E_j)(t_1), ..., D_(E_j)(t_ell)
```

in that chronological order. Since column matrices act rightmost first,
their final product is `T_j(t_ell)...T_j(t_1)=T_j(w)` by (8)--(9).
Do this for each target role j. The role circuits commute, so concatenating
them gives precisely (1), with `sum_j inv(w_j)` paid calls.

This argument establishes equality in `M_R(A)`, without relying on the
ordered-pair representation. Each spectator is untouched at every step.
Every target receives its required formal permutation on its arbitrary
entrance value. There is no clean-workspace assumption, compensating
residual, or inverse word omitted from the price. Together with the
lower bound, this proves (2).

| Resource | Complete attaining formal circuit |
| --- | --- |
| Arbitrary-input target roles | W |
| Extra dirty roles needed | Zero; any present spectators remain untouched |
| Paid adjacent rank-one calls | `sum_j inv(w_j)` |
| Free scalar changes used | Zero |
| Clean inputs, COPYs, resets, erasures | None |
| Additional preparation or restoration calls | Zero; no unfinished endpoint work |
| Endpoint certificate | Full formal group-algebra equality (8)--(9) |
| Native address/compiler, hosting, and recursive cost | Not provided or asserted free |

## Boundaries and useful failure controls

**Represented equality is only a necessary condition.** For `n>=4`, let
`Omega_sum=sum_(g in S_n)[g]`, which is a nonzero element of A. For any
fixed input and output ordered pairs, exactly `(n-2)!` permutations carry
the first pair to the second. That number is even, so
`rho(Omega_sum)=0`. For `R>=2`, the formal matrix

```
B = I_R + Omega_sum E_(1,2)
```

is nonidentity and invertible, with `B^2=I_R`, but `rho_R(B)=I`.
It also augments to the identity. This is an explicit endpoint-checking
negative control, not a claim that B has a legal paid-word factorization.
It explains why the represented cut proves a lower bound while the
attaining endpoint is proved separately in the full formal algebra.
For n=2 or n=3 the ordered-pair action is regular, so this particular
kernel control applies only from n=4 onward.

**The adjacent alphabet is essential.** If a nonadjacent transposition
`(a,b)`, `a<b`, becomes a single unit-cost paid label, it crosses
`2(b-a)-1` pairs at this cut. For example, `(1,3)` has three inversions
but is one such expanded-alphabet call on a coordinate role. The present
one-crossing-per-call inequality would no longer be the appropriate
invoice. A changed alphabet requires its own charged bound.

**Rank-d extension uses a rank-d charge.** If arbitrary binary idempotents
of rank d are permitted, (4) has rank d. The same proof therefore shows
`sum_calls rank(N)>=L`. Charging each call its scalar rank gives the exact
minimum L, because the rank-one attaining construction is still allowed.
This is not an invocation-count result when higher-rank calls cost one:
`N=E_1+E_2` implements two identical adjacent targets in a single rank-two
invocation, whereas their inversion sum is two. It also is not a theorem
for nonlinear recursive rank prices such as `r^(1-a)`.

**Order, dirt, and omitted calls matter.** With the product convention
above, `s_1 s_2` is not `s_2 s_1` for n>=3; reversing a non-palindromic
attaining word can change its target. A word with any one paid call
omitted from the attaining circuit has fewer than L calls, so the lower
bound itself proves that it cannot satisfy the same full endpoint.
Checking only zero spectator values can miss an off-diagonal spectator
coupling. A formal matrix or faithful regular-action check must include
every spectator input column and every required restored output column.

## Scope and predecessor credit

The old three-register rational-frame model uses the abelian address
group `M_3(Q)` under addition and a different paid alphabet. Here that
address group is replaced by `S_n` with explicitly charged adjacent
transpositions. Rational frame entries have not been reduced modulo two.
The lower bound is for the new formal finite-group model stated above,
including all finite role counts, rather than an extension of a
three-register search by analogy.

Cinna Davis's pinned S4 studies are direct predecessors:

| PR | Pinned head |
| --- | --- |
| [1720](https://github.com/CrocSwap/integer-mult-bounds/pull/1720) | `edb4a289a5f32c8209140144e384dcd3fa8cbfd1` |
| [1734](https://github.com/CrocSwap/integer-mult-bounds/pull/1734) | `48855b620b23af3a7fe87d53bde05cd2211342c8` |
| [1749](https://github.com/CrocSwap/integer-mult-bounds/pull/1749) | `90405b9498e4abfdd7d0eececcf11c7e83c6d13b` |
| [1801](https://github.com/CrocSwap/integer-mult-bounds/pull/1801) | `4f734ba1dee6418bb151e3730b9bf50655bd0fde` |

For the locally retained PR1720 endpoint, `c=s_1 s_2 s_3` has one-line
form `(2,3,4,1)` and three inversions. Its two-target endpoint therefore
has minimum six for every `R>=2`. PR1720 already established its
three-role instance by complete formal enumeration; that instance is
credited rather than claimed anew. The present proof replaces the
finite parameter restrictions by a uniform cut argument. Listing the
other pinned studies is attribution, not a claim to rerun their finite
computations or a certificate of literature priority.

The subadditive cut-rank method is inherited from Adam Gall's
[PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941), head
`5938ce3e91bbb8b5c2227af7976d444b2fbac7d4`, and Ross Richardson's
[PR1966](https://github.com/CrocSwap/integer-mult-bounds/pull/1966), head
`691e6eb9417384d1820de4fdc167fc3e9797b75e`. Their finite-dihedral
representations and tariffs are not assumed to hold for symmetric
groups. The argument above proves the needed replacement: the ordered
distinct-pair action has one crossing per adjacent generator and exactly
`inv(w)` crossings per target.

The covered domain is all `n>=2`, all finite `R>=W`, every target tuple
in `S_n^W`, and the complete formal diagonal boundary (1), under the
specified gate alphabet and unit price. This establishes a written
universal obstruction and a matching formal construction. It is not a
formal-kernel theorem or an inference from finitely many checked n.

There is no integer lift or numerical approximation in this formal
F2-algebra argument. Physical interpretation requires separately
admitting and pricing the native address actions, scalar operations,
all frame/compiler and hosting work, restoration, precision/tape
behavior, and the full recursive child profile. Those obligations are
unresolved here and cannot be discharged by this formal optimum. Other
free address maps, nonlinear gates, partial endpoint contracts, clean
ancillas, or different call prices are outside the stated theorem.

Prepared by Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0.

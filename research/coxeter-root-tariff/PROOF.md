# Coxeter root cuts give exact tariffs with arbitrary dirty workspace

This is a written theorem for a formal group-algebra operation model. Its
finite executable examples corroborate particular identities and boundary
conditions; enumeration is not the justification for its infinite families.
The theorem supplies no physical BIT supplier, recursive moment, or change to
the selected integer-multiplication exponent.

## 1. Model and statement

Let `(W,S)` be a Coxeter system with a finite set S of simple generators. W
may be finite or infinite. Thus each `s in S` is an involution, and the group
has its Coxeter presentation. Work in the full algebra

```
A = F2[W],       [g][h]=[gh],       1=[e].
```

Every algebra element is a finite sum. Distinct group elements are distinct
formal basis vectors; equality in A means equality of every coefficient.
Use `r>=d>=0` scalar registers, each with an arbitrary entrance value. The
required complete endpoint is

```
T = diag([w_1],...,[w_d],1,...,1) in M_r(A).             (1)
```

Every spectator is restored to its own entrance value, and all off-diagonal
role couplings vanish. A paid call is

```
D_N(s) = I_r + ([s]+1)N,
s in S,       N in M_r(F2),       rank(N)=1,       N^2=N. (2)
```

Arbitrary scalar `GL_r(F2)` operations are free and may be interleaved.
Scalar entries commute with A. There are no other free address operations,
clean allocations, resets, discards, or uncharged preparation/restoration
calls. Matrix products act on columns, rightmost first. Since
`([s]+1)^2=0`, every call (2) is its own inverse.

Let Phi be the real root set of the standard geometric representation of
`(W,S)`, let `Phi+` be its positive roots, and put `Phi-=-Phi+`. These are real
geometric roots used as distinct labels. **They are not reduced modulo two.**
Write O for a W-orbit in Phi and `O(s)` for the orbit of the simple root
`alpha_s`. Assign each root orbit a positive real price `c_O`, and charge (2)
the price `c_O(s)`. There are at most `|S|` such orbits. Define

```
i_O(w) = |{alpha in O intersect Phi+ : w alpha in Phi-}|,
L_c(w) = sum_O c_O i_O(w).                              (3)
```

These counts are finite, including when W is infinite.

**Theorem.** In this model, for every finite r and every tuple in (1), the
exact minimum paid cost is

```
sum_(j=1)^d L_c(w_j).                                  (4)
```

More strongly, the number of calls whose simple generator belongs to orbit O
is at least `sum_j i_O(w_j)`, separately for every O. One coordinate-role
circuit attains all these inequalities simultaneously. In particular, with
all prices one, the exact call count is `sum_j ell_S(w_j)`.

The pricing hypothesis is equivalently that conjugate simple generators
have the same price. This permits different prices on different reflection
classes, for example the two classes in type B. It does **not** permit
arbitrary separate prices for the adjacent swaps of a symmetric group.

The vacuous `r=d=0` endpoint has cost zero. Below assume r is positive; the
case `d=0` follows by the same argument and the empty circuit.

## 2. Standard root facts used, and the weighted recurrence

We use three standard facts from the geometric representation of a Coxeter
system:

1. `Phi = Phi+ disjoint union Phi-`.
2. A simple s sends `alpha_s` to `-alpha_s` and permutes
   `Phi+ minus {alpha_s}`.
3. `Inv(w)={alpha in Phi+ : w alpha in Phi-}` has cardinality
   `ell_S(w)`. Also `w alpha_s` is negative exactly when
   `ell_S(ws)=ell_S(w)-1`.

These facts, including infinite Coxeter groups, are proved in Gert Heckman's
[Coxeter Groups, Section 4.2](https://www.math.ru.nl/~heckman/CoxeterGroups.pdf#page=71),
Theorem 4.11, Corollaries 4.12--4.13, and Theorem 4.14 (printed pages 71--73).
We use those root-theory results as cited mathematical input. The circuit
inequality and attaining formal construction are proved below.

Here is the needed refinement by root orbit. Choose a right descent s of
w, so `ell_S(ws)=ell_S(w)-1`. By facts 2--3,

```
Inv(w) = {alpha_s} disjoint union s Inv(ws).              (5)
```

Indeed `alpha_s` is inverted by w and is not inverted by ws. On every other
positive root, applying s is a bijection of the positive roots other than
`alpha_s`, and `w(s beta)=(ws)beta`. As s preserves each W-orbit, (5) gives

```
i_O(w) = i_O(ws) + 1[O=O(s)].                           (6)
```

Apply (6) repeatedly to the last letters of any reduced expression for w.
The number of letters in orbit O in that expression is exactly `i_O(w)`.
Its price is therefore `L_c(w)`. This proves the weighted reduced-word fact
needed here directly from the inversion recurrence; no additional theorem
about unequal-parameter Hecke algebras is assumed.

For completeness, the root-orbit pricing formulation agrees with reflection
conjugacy. The reflection associated to `alpha=w alpha_s` is `w s w^-1`.
Roots in one orbit therefore give conjugate reflections. Conversely,
suppose `h s h^-1=t` for simple s,t. In the geometric representation, the
image of `I-t` is the line through `alpha_t`, and also the line through
`h alpha_s`. The roots in the standard normalized representation have the
same nonzero norm, so `h alpha_s=+alpha_t` or `-alpha_t`. In the second case
composition with t changes the sign. Thus the simple roots are in one orbit.
Each orbit contains the negative of each of its roots, because the
associated reflection changes that root's sign.

## 3. Algebraic cut rank also works for infinitely many roots

For an orbit O, form the algebraic direct-sum vector space

```
V_O = direct_sum_(alpha in O) F2 e_alpha
    = V_O^+ direct_sum V_O^-,
```

where the two summands use positive and negative root labels respectively.
Every vector has finite support. Define the permutation representation
`P_w e_alpha=e_(w alpha)`. Since `P_g P_h=P_(gh)`, it extends linearly to
an algebra homomorphism `rho_O:A -> End_F2(V_O)` and entrywise to `M_r(A)`.
The represented register space is `F2^r tensor V_O`.

This is a permutation module on the set of real roots, not the geometric
reflection representation over a field of characteristic two. In
particular, `e_alpha` and `e_(-alpha)` are different basis vectors.

Let H contain all role copies of `V_O^+`, and K all role copies of `V_O^-`.
For a represented operator M, define

```
q_O(M) = rank_F2(M[K,H]).                              (7)
```

Here the block is an actual linear map between algebraic direct sums. For
any group element w its crossing block is a partial permutation with one
nonzero column for each root of `Inv(w) intersect O`. Those columns are
different standard basis vectors. Consequently

```
rank(P_w[K,H]) = i_O(w).                               (8)
```

It is finite by fact 3. Every entry of a formal matrix uses finitely many
group elements, and r is finite. A finite sum of finite-rank crossing maps
has finite rank. Thus (7) is finite for every formal matrix used here, even
if Phi is infinite. All maps and their compositions are defined on the
direct sum because images of basis vectors have finite support. No infinite
series, limits, bounded-operator topology, or finite truncation of Phi is
being used.

For two operators U,V, their two-by-two block multiplication gives

```
(UV)[K,H] = U[K,H] V[H,H] + U[K,K] V[K,H].              (9)
```

The image of a sum lies in the sum of the images. Composition cannot
increase finite rank: for `AB`, its image is contained in `image(A)` and
is a linear image of `image(B)`. Therefore (9) implies

```
q_O(UV) <= q_O(U)+q_O(V).                             (10)
```

The argument is the same finite-rank image inequality in finite and
infinite-dimensional spaces. It does not require invertibility or
commutativity. We apply it in the actual order of the circuit.

## 4. Every orbit has its own complete paid-call lower bound

A free scalar S acts as `S tensor I_(V_O)`. It preserves H and K, so its
crossing rank is zero. A paid factor (2) acts as

```
I + N tensor (P_s+I).
```

The identity part has zero crossing block. Fact 2 says that the crossing
block of `P_s` is zero if `alpha_s` is outside O, and otherwise has exactly
one nonzero entry, from `alpha_s` to `-alpha_s`. Hence the paid crossing
block is either zero or a single copy of N. In particular,

```
q_O(rho_O(D_N(s))) = 1[O=O(s)].                       (11)
```

The complete target (1) is diagonal in role space. Its crossing block is
the direct sum of those of the target permutations, followed by zero
spectator blocks. By (8),

```
q_O(rho_O(T)) = sum_j i_O(w_j).                        (12)
```

A formal endpoint equality remains an equality under each `rho_O`.
Iterating (10), inserting the zero free-map costs and (11), and applying
(12) proves the separate call-count lower bound for every O. Multiply
these inequalities by the positive `c_O` and sum to obtain (4) as a lower
bound. All arbitrary dirty roles are included in the ranks throughout;
there is no dependence on how many spectators were used.

This argument handles interleaved free scalar maps directly. Normalizing
them is also legitimate: `S D_N(s) S^-1 = D_(SNS^-1)(s)`, and conjugation
preserves the allowed projector class. After sliding scalar maps to one
end, augmentation `[g]->1` maps every paid gate and target to `I_r`, so
the final scalar residue must be the identity. No scalar residue or dirty
output coupling is waived by the model.

## 5. Attainment is in the full formal algebra

For role j write E_j for its coordinate projector, and put

```
T_j(g)=I_r+([g]+1)E_j.
```

This is a diagonal formal matrix, and direct multiplication shows
`T_j(g)T_j(h)=T_j(gh)`. For a reduced expression
`w_j=s_1...s_k`, the product

```
D_(E_j)(s_1)...D_(E_j)(s_k)=T_j(w_j)                  (13)
```

therefore holds coefficientwise in `M_r(A)`. To execute that product on
columns, apply the gates chronologically in the order `s_k,...,s_1`.
By (6), its number of orbit-O calls is `i_O(w_j)`.

Concatenating these circuits for distinct target roles gives (1), since
diagonal operations on different roles commute. It uses no spectator,
no scalar mixing, and no uncharged cleanup. Each spectator present is
untouched. Thus every orbitwise lower bound is attained, establishing the
exact cost claim and a true minimum for any positive real orbit prices.

The permutation representation is used only as a necessary lower-bound
test. Its possible kernel as an algebra representation is immaterial:
(13), not equality in a root representation, certifies the upper endpoint.
Even a faithful action of W on roots need not make the induced group
algebra representation faithful.

## 6. Explicit two-price corollary for signed permutations

Let `W=B_n` be the group of signed permutations, with `n>=1`. A group
element has one-line form `(w_1,...,w_n)`, where the absolute values are
`1,...,n`, and acts by `e_i -> sign(w_i)e_|w_i|`. The simple generators are

```
s_0: e_1 -> -e_1, fixing the other coordinates;
s_i: swap e_i and e_(i+1),              1<=i<n.
```

Price `s_0` at a>0 and every adjacent swap at b>0. Use the following
positive roots:

```
short: e_i                         (1<=i<=n),
long:  e_j-e_i and e_j+e_i          (1<=i<j<=n).
```

Their negatives complete the root set. A root is positive precisely when
its last nonzero coordinate is positive. The short and long roots are
separate invariant sets; for `n>=2` they are exactly the two root orbits.
Using roots with lengths one and square-root-two instead of normalized
roots merely rescales these two orbits. It preserves their permutations
and signs. The root of `s_0` is `e_1`, and that of `s_i` is
`e_(i+1)-e_i`.

For a signed list w define

```
neg(w) = #{i : w_i<0},
inv(w) = #{i<j : w_i>w_j},
nsp(w) = #{i<j : w_i+w_j<0},
```

with the usual integer order. Short positive roots sent negative are
exactly those with `w_i<0`, so their crossing count is `neg(w)`.
For each i<j, the image of `e_j-e_i` is negative exactly when `w_i>w_j`.
The image of `e_j+e_i` is negative exactly when `w_i+w_j<0`. These
equivalences follow by looking at the sign at the larger of
`|w_i|,|w_j|`, which are distinct. Thus the long crossing count is
`inv(w)+nsp(w)`.

The exact cost for an arbitrary tuple of signed-permutation targets, with
any finite number of dirty spectators, is consequently

```
sum_j [ a neg(w_j) + b (inv(w_j)+nsp(w_j)) ].           (14)
```

There is also a direct sorting proof of attainment, without the abstract
root facts. If the first entry is negative, negate it by right multiplying
by `s_0`. Otherwise, if there is an adjacent descent, swap its entries by
right multiplying by the corresponding `s_i`. If neither move is possible,
the list is positive and increasing, hence the identity.

Negating a negative first entry decreases neg by one and leaves
`inv+nsp` unchanged. To check the latter assertion, for x<0 and another
entry y, the combined pair contribution before the sign change is
`1[x>y]+1[x+y<0]`; afterwards it is
`1[-x>y]+1[-x+y<0]`. Writing x=-u with u>0, the two terms are merely
`1[y<-u]` and `1[y<u]` in opposite orders. The remaining pairs are fixed.
An adjacent descent swap leaves neg unchanged, decreases inv by one, and
leaves nsp unchanged, since nsp depends on unordered pairs of entries.
Thus every move decreases `neg+inv+nsp` by one. The process terminates,
using exactly `neg(w)` sign flips and `inv(w)+nsp(w)` swaps. Reversing the
list of right multipliers gives an expression for w: if the recorded
sorting moves are `t_1,...,t_k`, then `w t_1...t_k=e` and
`w=t_k...t_1`. Executing the coordinate calls chronologically as
`t_1,...,t_k` therefore gives the formal endpoint w, with the convention
of (13).

For example, the central sign reversal `(-1,-2,...,-n)` costs
`a n + b n(n-1)` on each target role. Unlike the type-A equal-price case,
the two coefficients remain independently sharp for every positive a,b.
The `n=1` case has no long roots and is simply `a neg(w)`.

## 7. Rank-priced extension and scope boundaries

**Arbitrary binary couplings, charged by rank.** Permit any
`N in M_r(F2)`, not necessarily an idempotent, and charge the gate
`I+([s]+1)N` the cost `c_O(s) rank(N)`. This gate is still an involution:
its square is I because the cross term vanishes in characteristic two and
`([s]+1)^2=0`. The crossing block in (11) now has rank `rank(N)`, so the
same proof establishes (4) exactly in this expanded model. The attaining
coordinate rank-one gates remain allowed. In particular, allowing
nilpotent rank-one scalar couplings at the same price cannot improve (4).

This is a rank tariff, not a higher-rank invocation theorem. If rank-two
gates cost one invocation, `N=E_1+E_2` realizes two identical simple targets
in one call. Nor does the theorem handle a concave price such as
`rank(N)^theta` for `0<theta<1`.

**Prices must respect root orbits.** In type A2 the two generators s,t are
conjugate and `sts=tst`. If their prices are a and b, the displayed costs
are `2a+b` and `a+2b`. When a differs from b there cannot be a
word-independent price assignment to their single root orbit that charges
both prescribed prices. The arbitrary-generator weighted problem is
outside (4). This observation does not claim that sharing is possible in
that changed model.

**Only simple generators have the stated one-root cost.** Adding an arbitrary
reflection or other group element as a unit-price primitive changes the
alphabet. Its crossing block can have several root crossings, so (11)
would no longer justify that unit price. For example in type A2, allowing
`sts` as one paid coordinate call realizes a length-three target in one
call of the expanded alphabet.

**The Coxeter presentation matters.** An arbitrary group generated by
involutions need not admit the root action used here. Nor can a root action
automatically descend through an additional group quotient: in the
infinite dihedral group `(st)^4` has length eight, whereas imposing
`(st)^4=e` makes that target the identity. The quotient must use its own
valid representation and generating-system hypotheses. In particular,
this proof does not settle the coordinate-CNOT alphabet in `GL_3(F2)`.

**The endpoint and field are part of the statement.** The claim is about
finite circuits over `F2[W]` with the exact arbitrary-input boundary (1).
The proof does not identify real roots modulo two, infer a formal endpoint
from a quotient test, give a physical realization of these address labels,
or extend a finite-address coincidence to the full group algebra. Extra
free address maps, changed preparation resources, and different endpoint
contracts require separate analysis. No transfer to the selected abelian
rational-frame supplier or complete multiplication theorem is asserted.

## 8. What this adds and what is inherited

The cut-rank inequality and its dirty-register application are inherited
from Adam Gall's [PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941),
Ross Richardson's [PR1966](https://github.com/CrocSwap/integer-mult-bounds/pull/1966),
and the retained
[symmetric adjacent-cut theorem](../symmetric-adjacent-cut-bound/PROOF.md)
([PR1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989)). The latter
already proves exact inversion-sum costs for all symmetric groups and
arbitrary restored dirty roles. We do not claim those cases as new.
The [infinite-dihedral result](../infinite-dihedral-register-bound/README.md)
([PR1911](https://github.com/CrocSwap/integer-mult-bounds/pull/1911)) and the
finite-dihedral results are also credited covered special cases.
In particular, the retained finite-dihedral theorem already closes the
arbitrary-workspace D16 question; stale earlier next-question text does not
make it new here. The arbitrary binary coupling/rank tariff in the infinite
dihedral case is also already given by
[ywz65's PR2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716),
head `74c96ae917fe16160db357c361058b3a6417a440`. Its special case is credited;
Section 7 applies the rank argument uniformly to the Coxeter root orbits.

The added statement is the uniform passage to every finite-rank Coxeter
system, including infinite groups, with a separate sharp bound for each
root orbit. This yields genuine arbitrary two-price tariffs for B_n and
other systems with multiple reflection classes. The proof makes the
infinite-dimensional step explicit and supplies a formal attaining word.
The optional rank-priced extension follows from the same block calculation.

Heckman's root theory is an external mathematical input, not a new theorem
of this package. The broader cut idea is elementary and no claim of
literature priority is made. Source pins and current overlap coverage
belong to this package's source/task metadata. Preparation and review used
substantial OpenAI assistance; finite checks and agent review are not
independent human review or proof-assistant verification.

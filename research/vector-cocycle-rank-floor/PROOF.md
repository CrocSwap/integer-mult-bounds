# A rectangular cocycle rank floor

## Formal boundary

Let F be a field, G a group, V an F-vector space of finite positive
dimension d, and R:G -> GL(V) a representation. Suppose c:G -> V is a
crossed homomorphism, with convention

```text
c(gh) = c(g) + R(g)c(h).
```

Use the full formal group algebra F[G]. A register word has r finite
scalar roles. Its paid factors are

```text
D_N(g) = I_r + ([g]-[1])N,
N = xy^T in M_r(F), y^T x = 1.
```

Every input is arbitrary. Any declared dirty role must have its required
full formal identity output, including all off-diagonal coefficients.
Constant GL_r(F) matrices may be interspersed at no formal paid-call cost.
No physical realization or price for those free matrices is asserted.

This is the rank-one idempotent register convention of Cinna Davis's
PR2116/2047/2248/2085 and Sagar Thakrar's PR4032. The new lemma uses a
vector-valued affine representation in place of a scalar twisted functional.
Nick Petalas's PR4898 supplies an earlier specific first-order instance;
neither that instance nor the predecessor results are replayed here.
Nick Petalas's PR6008 supplies the general full-operator representation
rank cut. The charge here uses a common rectangular block, whose per-call
rank is one even when the full operator defect has rank greater than one.
This is a changed invariant, rather than substitution of another group
into that full-operator cut.

## Theorem

For T in M_r(F[G]), define the rectangular matrix Delta_c(T) in
M_(rd,r)(F) by replacing entry `sum_g a_ij,g [g]` with the d-by-1 column
`sum_g a_ij,g c(g)`. If a register word equals T, then

```text
rank_F Delta_c(T) <= number of its paid calls with c(g) != 0.
```

The same statement holds with a call of projector rank k charged k units
when c(g) is nonzero. In the rank-one alphabet, for a full diagonal target
`diag([t_1],...,[t_w],1,...,1)`, the number of calls outside ker(c) is at
least `#{i : c(t_i) != 0}`. The bound is independent of the number of
restored dirty roles.

### Proof

The cocycle identity makes

```text
rho(g) = [ R(g)  c(g) ]
         [   0      1 ]
```

a group representation, so it extends linearly to an algebra map on
F[G]. Apply it entrywise and reorder the coordinates by putting all V
coordinates first and all final scalar coordinates last. The resulting
algebra map has the form

```text
rho_r(T) = [ A(T)  Delta_c(T) ]
           [   0    eps(T)   ],
```

where eps is entrywise augmentation. Therefore

```text
Delta_c(UW) = A(U) Delta_c(W) + Delta_c(U) eps(W).
rank Delta_c(UW) <= rank Delta_c(U) + rank Delta_c(W).
```

This uses only the rank inequalities for a sum and a product. In
particular no simultaneous diagonalization or scalar character is needed.

The cocycle identity at the identity gives c(1)=0. For a paid factor,

```text
Delta_c(D_N(g)) = N tensor c(g).
```

Its rank is one if c(g) is nonzero and zero otherwise. For the stated
higher-rank variant it is rank(N) if c(g) is nonzero. The factor is legal
and invertible since its inverse is D_N(g^-1), using N^2=N. Its upper
block is `(I-N) tensor I_d + N tensor R(g)` and its lower block is I_r.

A constant scalar matrix S has blocks S tensor I_d and S, with zero
rectangular block. It contributes no rank charge. Iterating the product
inequality proves the assertion even with interspersed free scalar mixing.

For the diagonal target, column i of Delta is c(t_i) supported in its own
V block. Distinct nonzero columns are independent because those blocks
are disjoint. Identity spectator outputs give zero columns and rows.
This proves the diagonal statement for every finite r. QED.

The bound is necessary, not sufficient. A nonidentity element in ker(c)
can have a nonidentity rho image with zero rectangular block. The full
formal endpoint, rather than this representation alone, remains the
correct acceptance condition for a construction.

## Normal p-subgroup extension

Let P be a finite p-group, H any group acting on P, and G=P semidirect H.
Let Phi(P)=P^p[P,P] be the Frattini subgroup. Then V=P/Phi(P) is a finite
Fp-vector space. H acts linearly on V because Phi(P) is characteristic.
For the unique expression g=ph, set

```text
R(ph) = action of h on V,
c(ph) = image of p in V.
```

Indeed `(ph)(qk) = p(hqh^-1)hk`, and taking the Frattini quotient gives
the crossed homomorphism identity. The theorem applies over Fp, or after
extending scalars to any field of characteristic p. Consequently every
diagonal target label with nonzero Frattini component forces one call
whose normal component also survives that quotient.

There is no hypothesis on the order or commutativity of H, and no
one-dimensional equivariant functional on V is required. This answers
the existence of a vector-valued rank floor in PR4032's Open next
question 2. It does not assert that every particular scalar-character
floor, equality classification or shortest-word theorem extends. Elements
of Phi(P), including central defects killed by that quotient, are not
detected. For a nonsplit extension an appropriate cocycle would need to
be supplied separately.

## A sharp family invisible to abelianization

Let p be any prime, d>=2, V=Fp^d and
`G = V semidirect SL_d(Fp)`, with the natural action. Write its elements
as (v,h), so multiplication is `(v,h)(w,k)=(v+hw,hk)`. The cocycle is
c(v,h)=v and the representation is R(v,h)=h.

Give every nonidentity group label unit paid-call price in the formal
rank-one alphabet. For any nonzero vectors v_1,...,v_w and every finite
r>=w, the full endpoint

```text
diag([(v_1,I)],...,[(v_w,I)],1,...,1)
```

has exact minimum w paid calls. The theorem gives the lower bound w,
including arbitrary restored dirty workspace and free scalar mixing.
The w coordinate projectors give the upper bound, with the exact full
formal endpoint and no cross-role entries.

Nevertheless every homomorphism from G to an abelian group kills all
translations. To prove this, for i!=j use h=I+E_ij in SL_d(Fp) and the
translation by e_j. With `[a,b]=aba^-1b^-1`, their commutator is the
translation by `(h-I)e_j=e_i`. All translations are products of these
basis translations. Thus V is contained in [G,G], and every abelian
quotient sends the whole target to identity. In particular ordinary
one-dimensional group characters cannot supply this nonzero target
defect. This statement does not exclude other representation-theoretic
lower bounds.

The finite example uses p=3,d=2. Its complement is nonabelian and has
order 24, divisible by 3. Thus the example actually exercises the
removed complement-order restriction. The written proof establishes the
family; finite checks are corroboration on this single group only.

Affine representations of cocycles, Frattini quotients, elementary
commutators and rank subadditivity are classical. No literature-wide
priority is claimed. The contribution here is their rectangular-block
register-word application and the stated scope extension of the
predecessor first-order method.

## Obligations outside this proof

These are formal algebraic call counts. Native address operators, scalar
basis conversion, permitted sources, ownership and erasure, chronology,
restoration costs, hosting, precision/tape, compiler closure, recursive
funding and the outer multiplication theorem are not provided. The
selected result and its five framework assumptions are unchanged. The
written proof has no claimed formal proof-kernel or independent human
acceptance.

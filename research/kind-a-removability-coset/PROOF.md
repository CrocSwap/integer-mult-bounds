# The complementary kind A removal criterion

Work in the formal group algebra Q[G], where `G=Sp(2m,2)`, `m>=3`.
Let L be the raw Lagrangian and `P=Stab_G(L)`. A free combination is
an element of Q[P] acting on the left. The frame of g is `g^-1 L`.
Its level is `ell(g)=m-dim(L intersection g^-1 L)`.
Products act from right to left. A paid call is a transvection whose
normal is outside L; each such call is an involution of level one.

Use Jacob Sussman's exact definition of removal from PR #7629.
Let D be the first call and W the shared call. Assume `ell(WD)=2`.
For `gamma in P` and a nonzero rational c, put

```text
M = WD,       E = W gamma D,       y = M+cE,
U = span_Q {p, pD, py : p in P},
U_without = span_Q {p, pD : p in P}
            + span_Q {py : p in P, p != 1}.
```

The removing call T is any paid call with `ell(TW)=2`. This is the
source's condition that T can be another array's last call. Removal
means `Ty in U + T U_without`. The occurrence with identity preparation
is excluded from `U_without`: otherwise removal is automatic and empty.
The other array's content is not part of this definition.

**Theorem.** For every such T, removal holds exactly when

```text
M and E have the same frame,       (-c)^ord(gamma) = 1.
```

The criterion is independent of the choice of admissible T. There is
no restriction on ambient width, the order of gamma, or spare bits.
The proof also permits plain or zero parts; these are set aside in the
source's nonplain table. For rational c the singularity condition means
`c=-1`, or `c=1` with even order. The coefficient c=0 is outside the claim.

This is the removal half of the source rule. PR #7649 already proves
the finishing half, with the opposite binomial test and its stated
extra-term and final-call hypotheses. No finite result from that source
is counted as new here.

## The level facts

The level is unchanged by multiplication on either side by P. The
Lagrangian distance `d(A,B)=m-dim(A intersection B)` is invariant under
the group and satisfies the triangle inequality. For example, the
intersection of `A intersection B` and `B intersection C` in B has
dimension at least `dim(A intersection B)+dim(B intersection C)-m`.
It lies in `A intersection C`. This proves the required inequality.
Consequently level is subadditive, and an inverse has the same level.
These are the only geometric facts needed below.

## Project onto the shared-call coset

Multiply the removal inclusion on the right by D. This is invertible.
Write `y0=W(1+c gamma)`. Multiply next on the left by T, which is its
own inverse. The resulting equivalent inclusion is

```text
y0 in T span_Q {p, pD, pW(1+c gamma) : p in P}
       + span_Q {p, pD : p in P}
       + span_Q {pW(1+c gamma) : p in P, p != 1}.
```

Project onto the formal coefficients whose indices lie in the right
coset WP. This coset is closed under right multiplication by gamma.
The following columns have zero projection:

- P misses WP, because their levels are zero and one.
- TP misses WP. An equality `Tp=Wh` would give `p=TWh`, whose level
  is `ell(TW)=2`, contrary to p in P.
- TPD misses WP. An equality `TpD=Wh` would give `TWh=pD`.
  The two sides have levels two and one.
- Every column `TpW(1+c gamma)` misses WP. If its first endpoint
  were Wh, then `pW=TWh` would have levels one and two. If its second
  endpoint were in WP, its first endpoint would also be in WP.

Let `H=P intersection W^-1 P W`. Index WP by h in P and write
`e_h=[Wh]`. The remaining binomial columns are

```text
b_h = e_h + c e_(h gamma),        h in H, h != 1.
```

This follows from `pW=Wh`, which is equivalent to `p=WhW^-1 in P`.
The omitted preparation p=1 is exactly h=1. PD singletons may survive
at h with `WhD in P`; retain them until the target support is examined.

## Distinct frames: the plain coefficient cannot be removed

The middle frames coincide exactly when
`EM^-1=W gamma W^-1` is in P, or equivalently gamma is in H.
Suppose gamma is not in H. No available binomial column touches e_1:
its start would need h=1, which is excluded, or its end would need
`h=gamma^-1`, which is not in H. A PD singleton at e_1 would require
`WD in P`, excluded by `ell(WD)=2`. The target `e_1+c e_gamma`
has coefficient one at e_1, since gamma is not the identity.
Thus removal is impossible, regardless of other PD singletons.

## Same frame: delete one cyclic column

Suppose gamma is in H and let n be its order. Restrict to the cycle
`{e_(gamma^j) : 0<=j<n}`. A binomial with a start outside the cycle
also has its end outside it. No PD singleton lies on this cycle:
`W gamma^j W^-1` is free, so `W gamma^j D` is a free left multiple
of WD and has level two. The only available columns on the cycle
are therefore `b_j=e_j+c e_(j+1)` for `1<=j<n`, with indices modulo n.
The target is b_0. The exact cyclic relation is

```text
sum_(j=0)^(n-1) (-c)^j b_j = (1-(-c)^n) e_0.
```

If `(-c)^n=1`, this relation expresses b_0 by the other columns.
Their actual preparations are `p_j=W gamma^j W^-1`, which are free
and nonidentity for `1<=j<n`. It is a relation between actual full
formal columns, so it proves sufficiency before projection. After
multiplication by T and D it removes Ty as required. For n=1 the
singular case is the zero part y=0 and needs no other columns.

If `(-c)^n!=1`, the full n-by-n cyclic binomial matrix is invertible.
Indeed the displayed geometric sum inverts `1+cz` modulo `z^n-1`
after division by `1-(-c)^n`. Its columns are independent. Hence b_0
cannot be in the span of the other n-1 columns. This proves necessity
and the theorem.

## Consequence and the necessary call restriction

For the nonraw kind A parts covered by PR #7649, finishing by a single
last call requires the same frame and `(-c)^n!=1`. Removal by any
admissible other last call requires the same frame and `(-c)^n=1`.
The two conditions cannot hold together. This proves that specific
finish/remove conflict with any number of spare address bits.
It does not exclude joint decoding of both outputs or general 2-in-5
programs. Post-call free processing is outside the finishing theorem.

The condition `ell(TW)=2` is essential. At m=3 take D and W with
normals e0 and e1, and take gamma with normal z1. Its middle frames
are distinct. With c=1, the four removing normals
`e1+z1`, `e1+z0+z1`, `e1+z1+z2`, `e1+z0+z1+z2` remove the part,
but every one has `ell(TW)=1`. These are boundary controls, not
valid other-array last calls. Retaining the identity preparation is
another invalid relaxation: it would make every target removable.

## Exact finite verification

The verifier constructs all 10752 elements of P at m=3 from every
invertible 3-by-3 binary A and every symmetric binary S:

```text
gamma = [[A, 0], [A^(-T) S, A^(-T)]].
```

The form is unique; invertibility and the symplectic identities imply
that S is symmetric. All generated basis pairings and uniqueness are
checked. For the fixed three coordinate calls, it builds the complete
literal sets P, PD, TP, TPD, PW and TPW. It then restricts their columns
to the target's exact right-gamma orbit and performs rational elimination.
Each two-term column stays in one such orbit, so this restriction decides
membership exactly. The computation retains PD singletons and every
paid column; it does not assume the theorem's projected zero statements.

All 43008 contracts for c in {1,-1,2,1/2} agree with the theorem.
After exclusion of the source's 769 plain cases, the removal counts are
639, 767, 0 and 0, as in the source's finite table. The 1407 singular
contracts also have their explicit deletion relation checked coefficient
by coefficient. A separate membership implementation, using free-element
tests instead of the materialized coset sets, checks 150 contracts at
four, five and six bits. Five controls cover the identity preparation,
a valid distinct-frame negative, an inadmissible call, a changed
coefficient and the zero-coefficient boundary. These checks corroborate
the written proof; they do not replace its arbitrary-width argument.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Credit Jacob Sussman for the definition, finite rule and question in
PR #7629, and Nick Petalas for the coset proof method and complementary
finishing theorem in PR #7649. No predecessor code was copied.
New work is Apache-2.0. Independent human and formal-kernel review,
Pauli phases, native realization and a full multiplication invoice
remain open. No new kappa or selected-assumption discharge is claimed.

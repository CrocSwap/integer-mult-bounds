# Exact kind B removal by an admissible call

Work in the formal group algebra Q[G], where `G=Sp(2m,2)`, `m>=3`.
Let L be the raw Lagrangian and `P=Stab_G(L)`. Free combinations act
on the left and lie in Q[P]. The frame of g is `g^-1 L`; its level is
`ell(g)=m-dim(L intersection g^-1 L)`. Products act right to left.
Paid calls are transvections with normals outside L. They are involutions
of level one. Two terms g,h have the same frame exactly when `g h^-1`
is in P. Thus a frame is a left coset Pg.

Use Jacob Sussman's removal definition from PR #7629. Let D be the
first call and W the shared call, with `ell(WD)=2`. For gamma in P
and nonzero rational c, a kind B part is

```text
M = WD,       E = W gamma,       y = M+cE.
```

Assume `E not in PD`. This excludes the source's plain-in-disguise
case, where E is a free image of the first-call term. The levels of
M and E are two and one, so their frames are different.
Let T be a paid call with `ell(TW)=2`. Define

```text
U = span_Q {p, pD, py : p in P},
U_without = span_Q {p, pD : p in P}
            + span_Q {py : p in P, p != 1}.
```

Removal means `Ty in U + T U_without`. The identity preparation is
excluded from `U_without`; otherwise every part would be removable.

**Theorem.** At every such width, removal by T holds if and only if

```text
TM in PE,       TE in PM,       c in {+1,-1}.
```

The first two conditions say that T exchanges the two frames. This
proves both directions of the kind B rule left open in PR #7629,
including its requested sufficiency statement. The theorem is about
one part and one removing call. It does not settle finishing, joint
decoding, post-call free processing, Pauli phases or a two-in-five unit.

## Why both exchange directions are necessary

Multiply the removal inclusion on the left by T. Because T is its
own inverse, the equivalent condition is

```text
y in T U + U_without.
```

The available columns are the singletons in `P, PD, TP, TPD`, the
binomials `py` with `p in P, p!=1`, and the binomials `Tpy` with p in P.
Neither target endpoint M nor E can occur in a singleton:

- M has level two, so it is outside P and PD.
- E has level one and is outside PD by the nonplain assumption.
- If TM were free, then `TW=(TM)D` would have level one, contrary
  to `ell(TW)=2`. Also `TMD=TW` is not free.
- `TE=TW gamma` has level two, so it is not free. If TED were free,
  then TE would be a free left multiple of D and have level one.

These statements exclude M and E from TP and TPD as well. The level
is invariant under left or right multiplication by P. The displayed
uses require only this invariance and the level of a call.

An old binomial py with p nonidentity cannot contain either endpoint:
matching its corresponding endpoint forces p=1, and matching the other
endpoint would put M and E on the same frame. In a paid binomial Tpy,
M cannot be its first endpoint and E cannot be its second endpoint,
because either equality would force `p=T`, which is not free.
The only remaining ways to cover the target endpoints are

```text
M = TpE  iff  TM E^-1 is in P,
E = TpM  iff  TE M^-1 is in P.
```

If either is absent, the corresponding target coefficient, one or c,
is nonzero while every available column has coefficient zero there.
This is an explicit linear obstruction. It proves both exchange
conditions are necessary, without any enumeration or assumption about
other columns.

## Exchange gives one even alternating cycle

Assume both exchange conditions. Put `a=E M^-1` and let n be its order.
The two conditions say `T a^-1` and Ta are in P. Therefore

```text
a^2 = (T a^-1)^-1 (T a) is in P.
```

But a is not in P because M and E have different frames. It follows
that n is even, and `a^j in P` exactly for even j. Also `T a^j in P`
exactly for odd j: for odd powers use Ta and powers of a squared;
for even powers membership would force T into P.

Let `delta=M^-1 E` and define `g_j=a^j M=M delta^j`, with indices
modulo n. These are distinct group elements. Every binomial column
has endpoints g and `g delta`, so no column with an endpoint outside
this right-delta orbit can meet it. Let `e_j=[g_j]` be its formal
coordinate vectors. The target is `b_0=e_0+c e_1`.

The available binomial columns on the cycle are precisely

```text
b_j = e_j+c e_(j+1),       1 <= j < n.
```

For even j, b_j is `p_j y` with `p_j=a^j in P`. Its j=0 occurrence
is the excluded identity preparation; all other even occurrences are
allowed. For odd j, b_j is `T p_j y` with `p_j=T a^j in P`, which
is an allowed column of TU.

There are no singleton columns anywhere on this cycle. For even j,
g_j is in PM; for odd j it is in PE. Both cosets miss P and PD by
level and the nonplain assumption. Moreover T sends these particular
cycle points to PE and PM respectively, because `T a^j` has the
opposite parity membership just proved. Hence they also miss TP and
TPD. This excludes every other way to repair the omitted column.

## The coefficient test and explicit removal

The exact cyclic identity is

```text
sum_(j=0)^(n-1) (-c)^j b_j = (1-(-c)^n) e_0.
```

If `(-c)^n!=1`, the full cyclic binomial matrix is invertible: the
geometric sum inverts `1+cz` modulo `z^n-1`. Its columns are independent,
so b_0 is not spanned by the other n-1 columns. Removal is impossible.
For nonzero rational c and even n, equality `(-c)^n=1` holds exactly
at c=+1 or c=-1.

At either of those coefficients, the identity expresses b_0 as minus
the weighted sum of the other columns. This is an identity in the full
group algebra, not only in the projection. The actual preparations are

```text
p_j = a^j       for even j, 0<j<n,
p_j = T a^j     for odd j,  0<j<n.
```

The even preparations are nonidentity because n is the order of a.
After multiplication by T, the even columns belong to `T U_without`
and the odd columns belong to U. They give an explicit expression for
Ty in the required space. No earlier singleton is needed. This proves
sufficiency and completes the theorem.

## Exact finite evidence

The independent checker uses binary row matrices. It enumerates all
10752 free elements at three bits from all invertible A and symmetric S:

```text
gamma = [[A,0],[A^(-T) S,A^(-T)]].
```

Every generated matrix is unique and satisfies the symplectic identity.
This parametrization is complete because the zero upper-right block
and the symplectic equations determine the lower-right block and force
`A^T C` to be symmetric. The 768 plain cases are excluded by the
literal test `E D in P`. It checks all 48 paid calls with `ell(TW)=2`.
Thus the domain contains 479232 part/call pairs.

For each pair, the checker first inspects every possible singleton,
old-binomial and paid-binomial incidence at both target endpoints.
For 478720 pairs at least one target coefficient is absent from all
columns. That certificate rejects all five nonzero coefficients tested.
For the remaining 512 pairs, it constructs the complete right-delta
cycle, retains every available column, and performs rational elimination
at c in {1,-1,2,1/2,-2/3}. The cycle lengths are two, four and eight,
with 128, 256 and 128 pairs. Explicit alternating relations are also
checked for every positive case. Only c=+1 and c=-1 work.

The domain covers 2396160 coefficient contracts. There are 128 distinct
removable parts at each of the two signs and zero at the other three
coefficients. The source already supplied the 128-part finite count for
c=+1 and c=-1; it is corroboration here, not the new result.

A second route runs full orbit-span checks on 150 wider cases at four,
five and six bits. It includes conjugation by a free transvection that
mixes a core coordinate with a spare coordinate, as well as padded
controls. It does not use the missing-endpoint shortcut. Five boundary
controls check one-sided exchange, the forbidden identity preparation,
a coefficient change, a missing cycle column and c=0. Two small exact
linear-system controls check the rational eliminator itself. The finite
checks support the written arbitrary-width proof.

## Attribution and limits

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Jacob Sussman defined kind B removal, supplied the finite rule and posed
the frame-exchange question in PR #7629. Nick Petalas's coset method in
PR #7649 and Ali Romman's kind A removal proof in PR #7677 are related
predecessors; they do not prove this alternating-frame theorem. The
row-matrix verifier was written for this package. No predecessor source
file is needed at run time. New work is Apache-2.0.

The mathematical model drops Pauli phases. Native operations, physical
layout, precision, restoration and the complete signed target/paid invoice
remain open. Free formal combinations are not a priced physical decoder.
No new kappa, supplier admission or selected-assumption discharge is
claimed. Independent human and formal-kernel review are unclaimed.

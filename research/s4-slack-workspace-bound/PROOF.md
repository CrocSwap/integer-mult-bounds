# Inversion slack bounds restored dirty workspace

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a written quantified proof, not a formal-kernel certificate.

## 1. Statement and exact model

Let R=A⊕S be a finite-dimensional binary scalar register space, with dim A=w.
In M_r(F2[S4]), let a normalized m-factor word have endpoint Q_A⊕I_S.
The active block Q_A may be any invertible formal block satisfying the word
premise; its augmentation is necessarily identity. Every paid factor is

    G_s(u,v)=I+([s]+[e])uv^T,   v^T u=1,

where s is one of (12),(23),(34). Scalars commute with group coefficients.
The entire formal endpoint is required for arbitrary inputs, including dirt.
Free scalar GL mixing is normalized by conjugation; augmentation forces its
remaining scalar endpoint to be identity, as in PR4765. Products are written
in matrix order; the rightmost written factor acts first on columns.

Use the ordered-pair permutation module V=R⊗U, where U has basis e_(a,b),
1≤a,b≤4 and a≠b. Put H=R⊗span{e_(a,b):a<b} and let K be its negative half.
For an invertible represented map P define

    φ(P)=rank(π_K P|_H)=d(H,P^(-1)H),
    d(X,Y)=dim X-dim(X∩Y)  for equal-dimensional X,Y.

Let L=φ(Q_A⊕I_S), and δ=m-L. The triangle inequality makes δ≥0.

**Theorem.** There is a single scalar basis change B=I_A⊕B_S, fixing the
original active coordinates, such that every conjugated paid factor is
supported on the original active roles and at most δ additional dirty roles.
Discarding the remaining identity block preserves every paid label, order,
rank-one idempotent and the full endpoint Q_A⊕I. Thus at most

    w + δ = w + m - L

total roles suffice. In particular all label counts and all prices depending
only on the labels are preserved. The assertion is a reduction of a given
word, not an existence claim or a shortest-word lower bound for a new target.

For diagonal permutation targets L is the sum of their inversion counts.
For a general active formal endpoint it is the represented crossing rank;
no faithfulness of the representation is assumed. The conclusion about the
paid factors themselves is in the full group algebra.

## 2. Quantitative one-step charge

Suppose P=Q_{A_0}⊕I_{S_0} for some current scalar decomposition R=A_0⊕S_0.
For a paid factor G=G_s(u,v), write u_S for the S_0 component of u and v_S
for the restriction of v to S_0. Define

    η(P,G)=1[u_S≠0]+1[v_S≠0].

We prove the stronger local estimate

    η(P,G) ≤ 1 + φ(PG) - φ(P).                         (1)

A simple generator crosses exactly α=e_(i,i+1) and β=e_(i+1,i), permuting
the other five positive roots among themselves. With H_other their span,

    Y:=GH=(R⊗H_other) ⊕ (ker(v)⊗α) ⊕ (span(u)⊗β).     (2)

Indeed R=ker(v)⊕span(u), and G is identity and s on these respective parts.
Thus d(H,Y)=1. Put X=H, Z=P^(-1)H and D=X∩Z. Since P fixes the current
spectators, Z has no negative spectator component, and S_0⊗α⊂D.
Invariance of Grassmann distance and G^2=I give

    φ(PG)=d(Y,Z),  φ(P)=d(X,Z),
    φ(PG)-φ(P)=dim D-dim(Y∩Z).                         (3)

On X let ℓ extract its α coefficient and apply v. From (2), Y∩X=ker ℓ.
If v_S≠0, ℓ is nonzero on S_0⊗α⊂D, so dim(D∩ker ℓ)=dim D-1.

There are four cases.

* u_S≠0 and v_S≠0: a vector in Y with nonzero β coefficient has nonzero
  negative spectator component u_S, so cannot lie in Z. Consequently
  Y∩Z=D∩ker ℓ, its dimension is dim D-1, and (3) equals +1. Both new
  components are charged: η=2=1+φ(PG)-φ(P).
* u_S≠0 and v_S=0: the same identity Y∩Z=D∩ker ℓ holds, so its dimension
  is at most dim D. The right side of (1) is at least one, as required.
* u_S=0 and v_S≠0: the intersection Y∩Z has a positive part D∩ker ℓ of
  dimension dim D-1. Its quotient by that part injects into Y/(Y∩X),
  whose dimension is one. Hence dim(Y∩Z)≤dim D, again proving (1).
* Both components vanish: η=0, and the distance triangle gives
  d(Y,Z)≥d(X,Z)-1, which is (1).

Thus a genuinely two-sided spectator coupling forces φ to rise by one in a
right peel. A one-sided coupling prevents φ from falling. These are local
statements for arbitrary invertible active blocks, not just diagonal targets.
When δ=0, (1) recovers the tight elimination step of PR4765.

## 3. Extending the active space with the charged dimensions

For a vector a∈S_0 and functional b on S_0 there is a decomposition

    S_0=U⊕S_1,   a∈U,   b|_{S_1}=0,
    dim U ≤ 1[a≠0]+1[b≠0].                            (4)

Here are explicit choices. If a=b=0, use U=0. If b=0 and a≠0, take
U=span(a) and any complement. If b≠0 and a=0, choose t with b(t)=1 and
use U=span(t), S_1=ker b. If b(a)=1, use U=span(a), S_1=ker b. Finally,
if a,b are nonzero with b(a)=0, choose t with b(t)=1 and complement span(a)
inside ker b; use U=span(a,t) and that complement for S_1. This proves (4)
over F2 without an orthogonality or nondegeneracy assumption on b(a).

Apply (4) to a=u_S, b=v_S. Set A_1=A_0⊕U. The factor G is supported on
A_1 and fixes S_1: u∈A_1 and v vanishes on S_1. The old P also preserves
A_1 and is identity on S_1, since it was identity on all S_0. Therefore PG
again has the exact full formal block form Q_{A_1}'⊕I_{S_1}. The active
space has grown by at most η(P,G), the quantity charged in (1).

## 4. Nested splittings and telescoping

Write T=G_1⋯G_m. Start with P_0=T and the original R=A_0⊕S_0=A⊕S.
At step j peel G_{m-j+1} on the right, so

    P_j=P_{j-1}G_{m-j+1},   P_m=I.

Apply sections 2 and 3 at every step. This constructs nested decompositions
A_j=A_{j-1}⊕U_j and S_{j-1}=U_j⊕S_j. Every peeled factor is supported on
its current A_j, and hence on the final A_m. Every residual P_j fixes S_j.
All U_j lie in the original spectator space. Summing (1) gives

    dim A_m-w ≤ Σ_j η(P_{j-1},G_{m-j+1})
              ≤ Σ_j (1+φ(P_j)-φ(P_{j-1}))
              = m+φ(I)-φ(T) = m-L = δ.                (5)

No monotone-distance assumption is made: φ may rise, remain constant or fall.
The actual defect charges telescope even when the word has inversion slack.
A scalar basis change preserves H and K, so the ranks are unchanged while
performing the constructive splittings.

Choose a basis of U_1, then U_2, and so on, followed by a basis of S_m.
Together they form one basis of the original S. Appending the unchanged
original active basis gives a single B=I_A⊕B_S. This is not a sequence of
unpaid address changes, and it never changes an original active coordinate.

Let J include A_m in R in this basis, and K_0 project R onto A_m along S_m.
Then K_0J=I. For every original factor define u_i'=K_0u_i and v_i'=v_iJ.
Support and annihilation give u_i=Ju_i', v_i=v_i'K_0. Hence

    v_i'u_i'=v_i u_i=1,
    G_i J = J G_i',       K_0 G_i = G_i' K_0,
    G_i = G_i' ⊕ I_{S_m}  in the chosen basis.

The last identity is coefficientwise in F2[S4], not merely represented.
Multiplying the intertwiners proves G_1'⋯G_m'=K_0 T J=Q_A⊕I_{⊕U_j}.
This proves the theorem, including every dirty input, every off-diagonal
coefficient, the rank-one idempotent condition and unchanged paid chronology.

## 5. Boundary and use

**Sharpness for the stated word-preserving basis restriction.** Take one active
role e0 and two dirty roles e1,e2. Let u=e0+e1, v=e0*+e2*, and
G=G_(12)(u,v). The word G_(23)(e0,e0*) G G has m=3, L=1 and δ=2,
with endpoint diag([(23)],1,1). Its dirty vector and dirty functional are
both nonzero and their pairing is zero. These properties are invariant under
any scalar change of spectator basis. They cannot both be supported on one
dirty dimension: a nonzero vector and nonzero functional on a one-dimensional
space have nonzero pairing. Therefore preserving these actual normalized
factors requires at least two dirty dimensions, attaining w+δ=3.

This is **not** a lower bound on the optimal workspace or call cost of that
endpoint: G G cancels, and the endpoint has a one-call coordinate realization.
It proves that the coefficient one in the reduction's preserved-factor bound
cannot be lowered uniformly. The dense padded version of this fixture is
included in CASES.json and checked in both implementations.

The theorem supplies a finite role bound at a chosen excess-call budget; it
does not claim that all δ retained directions are necessary for every word,
or that a shorter word cannot discard cancellable factors. A word formed by inserting G G can
use dirt with positive slack, so the zero-slack conclusion cannot simply be
extended unchanged. The quantitative statement measures a preserved word.

The simple-label/rank-one assumptions make (2) have exactly one negative
root direction. An arbitrary involution or a higher-rank paid projector can
have several such directions and is outside this proof. Full spectator
identity is essential to both the negative-coordinate exclusion and the
positive-space inclusion. Clean ancillas, discarded outputs and free address
maps are different models. Weighted prices are preserved by the reduction,
but the workspace budget uses the unweighted call excess m-L.

No fixed mixed-target optimum is recalculated. The proof uses no C++ census
or finite exclusion premise. Its bounded exact controls corroborate the local
rank charge and constructive factor restriction; they do not establish the
universal quantifiers. Physical realization and complete supplier costs are
separate unknown obligations.

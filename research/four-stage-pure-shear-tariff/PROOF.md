# Exact four-stage pure-shear tariffs

This contribution was produced by Nick Petalas. Apache-2.0.

## Boundary and charge

Let F be any field and K a positive integer. Both data banks contain K
arbitrary independent field coordinates. A pure stage has one direction:

```text
U(A) = [I A; 0 I],       L(B) = [I 0; B I].
```

A stage may have any rank from zero to K. Zero means an unused stage. The
required complete endpoint is block antidiagonal with both off-diagonal
blocks invertible. There is no auxiliary data bank, promised input subspace,
or free cross-bank exchange. Arbitrary invertible block-diagonal bridges
may occur before, between and after stages. Their physical price is outside
this rank-tariff relaxation. Pure means the entire stage has one direction;
it may act on many independent pairs at once.

This is the one-direction-per-stage subclass of themilkman216's PR2052
multi-pair model. A simultaneous stage with both off-diagonal blocks
nonzero is outside this theorem. PR2052's general lower bound and its
finite searches are cited, not reproved or replayed.

## 1. Remove bridges without changing stage ranks

For G=diag(S,T) with S,T invertible,

```text
G U(A) G^-1 = U(S A T^-1),
G L(B) G^-1 = L(T B S^-1).
```

Move every bridge to the left using these identities. Invertible left and
right factors preserve each stage's rank. The remaining exterior bridge
preserves the zero diagonal blocks and invertibility of the off-diagonal
blocks of the required endpoint. Thus it suffices to study shear words
with no bridges. No assumption of one common port basis was added.

## 2. Complete alternating four-stage classification

Write the chronological directions as U,L,U,L, so the endpoint is

```text
M = L(D) U(C) L(B) U(A).
```

Ordinary block multiplication, without commuting any coefficients, gives

```text
M11 = I + C B,
M12 = (I + C B) A + C,
M21 = D (I + C B) + B,
M22 = D ((I + C B) A + C) + I + B A.
```

Consequently M is block antidiagonal if and only if

```text
B is invertible,    C = -B^-1,    D = B + B A B.             (1)
```

Indeed M11=0 forces CB=-I, hence B and C are invertible. Then M12=C,
M21=B and M22=DC+I+BA, which is zero precisely at the stated D.
Conversely (1) yields M=[0,-B^-1;B,0], including both invertible
off-diagonal blocks. This works in characteristic two as well.

Put P=-AB. The complete rank profile is

```text
(rank P, K, K, rank(I-P)).                                 (2)
```

The rank inequality for I=P+(I-P) implies total rank at least 3K.
Equality holds exactly when P is idempotent. To see necessity, equality
makes Im(P) and Im(I-P) complementary. For any vector x,

```text
P(I-P)x = (I-P)Px
```

belongs to both images, hence is zero. Thus P^2=P. Conversely an
idempotent gives the direct sum Im(P) plus Ker(P), so its two ranks sum
to K. Every equality profile (r,K,K,K-r), 0<=r<=K, is attained by B=I,
P=diag(I_r,0), A=-P, C=-I and D=I-P.

At the first named instance K=4, r=1 gives the complete rank profile
(1,4,4,3), total 12. Therefore an 11-unit four-stage swap, if it exists
in PR2052's larger model, must use a genuinely simultaneous mixed-direction
stage. Unpaidmoon's fork PR125 already reports a finite exclusion of the full
mixed model at K=4 over F2. That result is cited without replay. The present
all-field pure-stage argument leaves the mixed question open over other
fields, including Q, rather than reopening that finite F2 instance.

## 3. Exact directional tariffs

Let f_U,f_L be nondecreasing functions on {0,...,K} with f_U(0)=f_L(0)=0.
Among alternating four-stage words, the exact minimum tariff is

```text
f_U(K) + f_L(K) + min_(0<=r<=K) (f_U(r) + f_L(K-r)).         (3)
```

For an arbitrary endpoint word let a=rank P and d=rank(I-P). Since a+d>=K,
choose r=K-d. Then 0<=r<=a and K-r=d. Monotonicity and (2) prove the lower
bound (3). Every r is attained by the displayed idempotent construction.
Swapping the bank names gives the same formula for L,U,L,U.

If each directional tariff is also subadditive, formula (3) is the exact
minimum over all words of at most four pure stages. Adjacent stages with
the same direction merge by U(A2)U(A1)=U(A1+A2), or the analogous lower
identity. Rank subadditivity, monotonicity and tariff subadditivity show
that merging cannot increase the bill. If the two ranks sum to more than K,
choose smaller nonnegative ranks summing to K, apply subadditivity there,
then use monotonicity. The reduced directions alternate.
Pad a shorter word with zero stages to reach four alternating positions;
zero stages cost nothing. The construction in section 2 attains (3).

For one common nondecreasing subadditive tariff f, the minimum is exactly
3f(K): subadditivity forces f(r)+f(K-r)>=f(K), with equality available at
r=0 or K. In particular no fourth pure stage improves any common concave
power tariff r^theta, 0<theta<=1, even with free bridges. For different
positive coefficients c_U,c_L multiplying that same power, concavity
makes the minimum of the outer term occur at an endpoint. The exact cost
is (c_U+c_L+min(c_U,c_L))*K^theta.

Subadditivity matters. With f(r)=r^2, K=2 and r=1 the alternating word
costs 1+4+4+1=10, while every three-stage pure swap costs 12. This is a
control on the tariff hypothesis, not an improvement under a concave
recursive cost.

## Scope of the result

The theorem is all-field, all-K algebra with a complete arbitrary-input
endpoint. Its proof is the block identity, rank argument and attaining
projector family. Finite tests corroborate those statements. They do not
prove the quantified result by extrapolation.

Allowing both directions in one stage changes the stage-depth budget.
Splitting that stage into two pure stages is not justified for this
four-stage theorem. Extra banks, incomplete return contracts and different
endpoints are also outside it. No physical realization of free bridges,
Clifford phases, helper/owner program, precision, tape cost, full signed
recursive invoice, supplier admission or multiplication bound follows.
Independent human and formal proof-kernel review are unclaimed.

Credit themilkman216 / PR2052 for the explicit even-stage question and
multi-pair relaxation; Johnny Franks / cross-shear-stage-bound for the stage
potential; Jacob Alan Sussman and the archived borrowing-chain/controller
lineage for the attaining three-stage exchange. Block Gaussian elimination,
rank subadditivity and projector decompositions are classical. The new
repository result is this complete four-stage classification, equality
criterion and directional tariff formula. No literature-priority claim is
made for the elementary tools.

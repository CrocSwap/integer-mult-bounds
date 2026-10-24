# Mixed targets have no call sharing in prime-degree binary semilinear groups

This is a scoped algebraic proof. It answers Nick Petalas's mixed-target
question in PR #5202; his normal-C7 theorem, F8 representation and rank method
retain their credit. Cinna Davis's PR #2011 supplies the order-21 model and
earlier orbit census. Neither predecessor census is an assumption of the
self-contained argument below. No physical supplier or new kappa is claimed.

## Model and theorem

Let p be an **odd prime**, F = F_(2^p), and

    G_p = F^* semidirect C_p,
    (a,j)(b,k) = (a b^(2^j), j+k mod p).

Call a nonidentity element with j=0 **normal**, and an element with j!=0
**outside**. At p=3 this is C7 semidirect C3 with the action in #2011/#5202.
All nonidentity labels are allowed, at unit price.

Work in Mat_r(F2[G_p]), for any finite r>=1. Every register starts arbitrarily
dirty. A paid operation is

    D_N(g) = I + N tensor ([g]+[1]),
    g != 1,  N=x y^T over F2,  y^T x=1.

Thus N is a rank-one idempotent. Arbitrary GL_r(F2) scalar maps may be
interleaved freely. No other address operation, clean workspace, COPY or ERASE
is free. The required endpoint is the **full formal operator**

    T = diag([g_1],...,[g_r]).

Let n be the number of normal targets, m the number of outside targets, and
w=n+m. Identity targets designate restored dirty registers. Repeated target
labels are permitted.

**Theorem.** The minimum paid-call count is exactly w. If a word is optimal,
then, after moving its free scalar maps to the right, it has exactly n normal
calls and m outside calls. In every normalized normal call, both x and y are
supported only on normal target roles. In every normalized outside call they
are supported only on outside target roles. In particular, no normalized
optimal paid factor touches a restored identity role, and the two target
types never mix in a normalized optimal word.

These support statements concern the normalized algebraic word. They do not
claim that an implementation's interleaved free scalar maps avoid workspace.
They also do not force coordinate projectors within either target class.

## A constant-displacement representation

On the p-dimensional binary vector space F, use

    rho(a,j)(z) = a z^(2^j).

This is a group representation by the displayed group law. For a!=1 and j=0,
rho(a,0)-I is multiplication by a-1, so has binary rank p.

For 0<j<p, a nonzero fixed point satisfies z^(2^j-1)=a^(-1). The standard
Euclidean identity

    gcd(2^j-1, 2^p-1) = 2^gcd(j,p)-1 = 1

shows that this power map permutes the cyclic group F^*. There is exactly
one nonzero fixed point, as well as zero. Hence rho(a,j)-I has a
one-dimensional binary kernel and rank p-1. This uses primality of p.

Choose a characteristic-two extension K containing a primitive p-th root of
unity zeta. Such an extension exists because p is odd: p divides 2^(p-1)-1,
and the multiplicative group of F_(2^(p-1)) is cyclic. Define the quotient
character

    chi(a,j) = zeta^j.

Its displacement rank over K is zero on normal labels and one on outside
labels. Extend the binary matrices rho to K and put R = rho direct-sum chi.
Extension of scalars preserves the rank of a binary matrix. We obtain

| label | rank(rho(g)-I) | rank(chi(g)-1) | rank(R(g)-I) |
|---|---:|---:|---:|
| identity | 0 | 0 | 0 |
| normal | p | 0 | p |
| outside | p-1 | 1 | p |

The new quotient block makes the displacement rank **p for every paid
label**, including the outside labels omitted from #5202's target theorem.
Both representations extend linearly to the full group algebra. They need
not be faithful as algebra maps: only necessary consequences of a formal
endpoint are taken through them.

## Free maps and the sharp lower bound

For S in GL_r(F2),

    S D_N(g) = D_(S N S^-1)(g) S.

Conjugation preserves binary rank-one idempotence. Move all free scalar maps
to the right. Augmentation [g] -> 1 sends every paid factor and T to I, so
the remaining scalar product is I. We have a normalized paid-only word of
the same length and the same labels.

Under R, each paid factor A has

    A-I = N tensor (R(g)-I),    rank(A-I)=p.

The represented target has rank(R(T)-I)=p w. Rank subadditivity and

    AB-I = (A-I)B + (B-I)

give p w <= p L for a normalized word of L calls. Thus L>=w, with no
restriction on r or on the number of restored dirty registers.

Conversely, for each g_i!=1 apply D_(E_ii)(g_i). These w coordinate factors
attain T **in the full formal algebra**, for every input in every role.
The other roles are identically restored. This proves the exact minimum;
equality merely in a representation is not used for attainment.

Writing c_N,c_O for the two paid label counts, the separate representations
also give

    p c_N + (p-1)c_O >= p n + (p-1)m,
    c_O >= m.

At L=c_N+c_O=n+m the first inequality implies c_O<=m. Therefore c_O=m and
c_N=n. At p=3 these are precisely the missing paired inequalities
3c7+2c3>=3n+2m and c3>=m.

## Rigidity of optimal normalized factors

For any product A_1...A_L, telescoping from the right and from the left gives

    col(A_1...A_L-I) <= sum_i col(A_i-I),
    row(A_1...A_L-I) <= sum_i row(A_i-I).

Here <= means subspace inclusion. For example, the first follows from
the expansion sum_i (A_i-I) A_(i+1)...A_L; the second follows from
sum_i A_1...A_(i-1)(A_i-I). If the word is optimal, the left side has
dimension pL, while the sum of the individual dimensions on the right is
also pL. Consequently both inclusions are equalities, and **each** factor's
column and row spaces lie inside the corresponding target spaces.

Project the column containment to one register role t. For a factor with
N=x y^T and x_t=1, the projected column space is col(R(g)-I). The target's
space in that role is col(R(g_t)-I). The identity target has zero space,
so x_t must be zero there. A normal call has full dimension p in the rho
block and zero in the chi block. It cannot fit inside an outside target's
(p-1)-dimensional rho image. An outside call has a nonzero chi image, so
cannot fit inside a normal target's zero chi block. Thus x has the stated
type support. Applying the identical argument to row spaces and y proves
the corresponding assertion for y. This proves the rigidity statement.

## Boundary, credit and verification

The p=3 all-normal case is already #5202's theorem. The additions are all
mixed/outside target lists, the normalized optimal-factor support theorem,
and the odd-prime-degree family. The proof above includes the inherited
representation/rank steps to be readable without an unmerged dependency.
The exact checks are finite corroboration, not a proof of universal quantifiers
or independent human acceptance. Elementary finite-field facts and ordinary
rank algebra are used explicitly, with no numerical or asymptotic premise.

The prime-degree and odd-characteristic-order hypotheses are used at the two
specified steps. No conclusion for composite degrees or p=2 follows from
this argument. Nonuniform label prices, restricted alphabets, higher-rank
paid factors, non-diagonal targets and extra free address maps have different
boundaries. Native realization, ownership, routing, restoration implementation,
precision, hosting, stock/compiler and full recursive/outer costs are unpriced.
The theorem supplies no physical supplier or complete multiplication theorem.

Predecessors: Nick Petalas, PR #5202 at
`99ed6d2fc13101cb5ec0d3b1cdc826b75bc27fc7`; Cinna Davis / 1337isnot1337,
PR #2011 at `b971a6c68d6f60c2693b2057ecf3489efb75efc4` and PR #3893;
eumemic / #288 and the retained register-model lineage. Prepared by
Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.

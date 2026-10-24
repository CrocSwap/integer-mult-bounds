# Independent review of reciprocal signed centres

The coefficient theorem passes. For the actual signed 48-port family,
the full response is a dyadic unit exactly when its eight parameters
have the form

```text
beta_v = (1-(-2)^n_v)/12, with n_v an integer.
```

If the full response and both specified principal blocks must all be
dyadic units, each n_v must be one of -2,-1,1,2. This gives exactly
65,536 distinct responses. The family is closed under inversion.

The four-value conclusion includes the full-unit hypothesis. Principal
units alone admit more choices. For example, the earlier coefficient
beta=1/2 makes both principal blocks dyadic units, while the full
48-port response has determinant 5^8 and is not a dyadic unit.

The theorem makes a local reciprocal response possible without an odd
denominator in its inverse. It does not supply a native schedule or
identify responses in different stage charts.

## Source and independent method

The producer is
`controller-followthrough-20261017/reciprocal-centres-20261018`.
Its freeze SHA-256 is
`8dbeea6d6ed538592b7f20cb651dd1ad257a1fbaa60c9b0d3c04a2a51e98c99e`.
The signed source payload has decompressed SHA-256
`0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee`.

This review imports no producer. It uses the actual matrices and
selected ports from that payload. It computes determinants by
integer Bareiss elimination after clearing row denominators.
This differs from the producer's rational Gaussian elimination.
It also checks the six-step ordinary gauge on all 40 input columns,
its inverse in both orders, and the ordered interface inverse.

The nine matrix cases include all four uniform admitted choices,
a different mixed admitted choice, the old beta=1/2 response,
a full unit with nonunit principal blocks, a singular selected
block, and mixed exponents outside the four-value range.

## A proof from the actual matrix identities

The independent checks establish

```text
K K^T = 12 I_8,
G^T = G, G^2 = I_48, det(G)=1,
G K^T = K^T Lambda.
```

Here Lambda has the actual alternating component signs. For diagonal
D=diag(beta_v), define E=G-K^T Lambda D K. Since G K^T=K^T Lambda,

```text
E = G (I-K^T D K).
```

The determinant identity det(I-AB)=det(I-BA) therefore gives

```text
det(E) = product_v (1-12 beta_v).
```

Put s_v=1-12 beta_v. Direct multiplication, using K K^T=12I,
gives

```text
E^-1 = G + K^T Lambda diag(beta_v/s_v) K.
```

This proof needs no unverified choice of component projectors. It
follows from the actual source identities above. It also fixes the
order of the factors and does not commute an intrinsic Q phase
through the response.

Let R=Z[1/2], and assume every beta_v is in R. Then s_v is nonzero:
beta_v=1/12 is not in R. E is a unit over R if and only if every s_v
is a unit. Necessity follows because a product of elements of a
commutative ring can be a unit only when each factor is a unit.
Sufficiency follows from the displayed inverse.

## Infinite coefficient classification

The units of R are +/-2^n. Reduction modulo 3 is defined on R because
2 is invertible modulo 3. The equation s=1-12 beta implies s=1
modulo 3. Among +/-2^n, exactly one sign has this residue:
s=(-2)^n.

Conversely, 1-(-2)^n lies in 3R for every integer n. Dividing by 12
therefore leaves an element of R. Inversion sends s to 1/s and
hence n to -n.

This proves completeness over all integer exponents. The checker
uses the range -128 through 128 only as a control. That finite
range is not the reason that the classification is complete.

## Principal blocks

The selected set is

```text
S=[0,7,15,36,42,46,79,89].
```

The actual selected matrix K_S has determinant -4, and G_SS=0.
With L=E_SS and H=E_UU on the other 40 centre ports,

```text
det(L) = det(-K_S^T Lambda D K_S)
       = 16 product_v beta_v.
```

The selected block of the full inverse is
K_S^T Lambda diag(beta_v/s_v) K_S. Jacobi's complementary
principal-minor identity gives

```text
det(H) = det(E) det((E^-1)_SS)
       = 16 product_v beta_v
       = det(L).
```

This identity holds for every dyadic coefficient vector, including
vectors with a zero beta. The full response remains invertible over
the rationals in that case, so Jacobi's identity still applies.
Both principal blocks are units over R exactly when all beta_v
are units over R.

Now impose the full-unit classification as well. For n>0, the
integer 1-(-2)^n is odd. After its factor 3 is removed, beta is a
dyadic unit exactly when

```text
abs(1-(-2)^n)=3.
```

For odd n this is 1+2^n=3, so n=1. For even n this is
2^n-1=3, so n=2. For n=-m<0, clearing 2^m gives the same two
equations with m, and hence n=-1 or n=-2. At n=0, beta=0.
There are no other integer cases.

The four beta values are 1/4,1/8,-1/4,1/16. Reciprocity exchanges
1/4 with 1/8 and -1/4 with 1/16.

Different coefficient vectors give different matrices. Indeed,
if K^T Lambda diag(delta_v) K=0, multiplication on the left by K
and on the right by K^T gives 144 Lambda diag(delta_v)=0.
Thus every delta_v is zero. Consequently 4^8 counts distinct
responses, not only formal parameter choices.

The checker also reproduces the complete determinant distribution
by an eight-step count recurrence. It does not copy the producer's
enumeration of all coefficient tuples.

## The existing-data gauge

Let T=G(S), and let R_0 contain the other 32 centre ports. The source
checks establish that T is disjoint from S, K_T is a dyadic unit,
G maps T back to S, and G_R0 is a signed permutation. Thus on the
ordinary coordinates ordered as (T,R_0), the G term is
diag(0,G_R0).

Put B=diag(alpha_v beta_v). Start with arbitrary data (t,r), and
apply the six steps from the producer:

```text
t <- K_T t
t <- t+K_R0 r
t <- -B t
r <- G_R0 r
r <- r+K_R0^T t
t <- K_T^T t
```

After step three, t=-B(K_T t_initial+K_R0 r_initial).
The last two output expressions are therefore exactly H(t_initial,
r_initial). If every beta_v is a dyadic unit, each step is an
invertible dyadic operation. The two scatter steps are shears.
No value is cleared and no initial zero is used.

Reversing these six steps and inverting each factor gives H^-1.
The independent checker compares that reverse factor with an
unrelated Gaussian inverse on all 40 columns. This proves the
existing-data representation claim. It does not price the
elementary scalar word for every coefficient choice.

The ordered block formulas for A and A inverse also pass both
inverse products. On the 48-port centre part,

```text
det(A)=det(L)/det(H)=1.
```

This statement must keep its dimension. The frozen 64-port
complement has square 4I and determinant 2^64. It belongs to the
ordinary block of the full interface. Therefore the corresponding
full 112-port interface has determinant 2^-64, still a dyadic unit.
It does not have determinant one.

## Orthogonality and scope

The same identities give

```text
E^2 = I + K^T diag(12 beta_v^2-2 beta_v) K.
```

Multiplication by K and K^T shows that E^2=I exactly when every
beta_v is 0 or 1/6. The latter is not dyadic. Thus the only
orthogonal member with dyadic parameters in this fixed signed
family is G itself.

This is a family-specific obstruction. New matching responses and
other rank-two responses can lie outside this family. They are
not ruled out by this theorem.

The useful uniform reciprocal pair is beta=1/4 and beta=1/8.
Both use the same eight centre rows. The theorem permits a native
construction to change their scatter coefficients and keep a
dyadic inverse. It does not prove that the actual schedule can
form those queries at the required cuts. Native phase correctness,
arbitrary helper restoration, complete recursive price, routed
stage composition, and terminal decoding remain separate work.
No kappa improvement follows from this matrix packet alone.

## Reproduction and credit

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/reciprocal-centres-review-20261020/check_review.py
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/reciprocal-centres-review-20261020/check_review.py
```

Both runs must report:

```text
PASS_INDEPENDENT_RECIPROCAL_CENTRE_CLASSIFICATION
```

The receipts must have equal bytes. FREEZE.json records the proof,
checker, receipt, and source pins.

The coordinating agent supplied the full-unit exponent
parameterization. The controller lane supplied the principal-unit
classification and the actual coefficient family. The earlier
bridge-review signed-pivot work supplied the six-step gauge. The
signed source also uses the oblique and budget-geometry work.
This independent review used OpenAI Codex assistance. No PR,
commit, or push was made.

Before a future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.

# Sharp COPY-power bill for the single PR2021 (0,1) completion

Hanhong Zhao (@Hope7Happiness), with substantial OpenAI Codex, Claude Code and Gemini assistance.
Prospective H q_a9e057b2a674468b:e15; experiment e17.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006#discussioncomment-18940755).
This is a written coefficient-universal argument supported by exact finite
geometry, not a finite shear-search inference or a native supplier theorem.

## Statement and fixed conventions

Use precisely the source-bound X, binary labels and j=0,k=1 in ROOTS.json (after removing the first eight frame rows).
Let e=e_0, f=e_1, s=X[0,:]^T, t=X[1,:]^T and

    K=XX^T-(XX^T e-4e)e^T+e f^T,
    L=[X,e], R=[(I-ee^T)X,4e+f].

The coefficient vectors s,t have s^T s=4, s^T t=2; their nonzero coordinate
sets coincide, namely {1,2,4,7}. Every transpose is ordinary, over C.
For every exact factorization K=D T^T into nine rank-one terms, define
rho_i=rank_F2 B[supp(D_i),supp(T_i)] on the original binary labels.

**Claim proved here, subject to the finite certificate below:**

    min sum_i rho_i^q = 7*8^q + 7^q + 1,  for every 0<q<=1.

One rational factorization attains the minimum simultaneously for all q.
Thus the minimum COPY sum is64, improving the displayed predecessor65 control,
but for 0<q<1 the power bill is strictly greater than the original eight-H8
bill8*8^q. No recursive improvement or complete native invoice follows.

## 1. Factor coordinates and the complete finite classification

Direct all-entry replay gives K=L R^T and rank(L)=rank(R)=9, hence rank(K)=9.
Every nine-term factorization has D=L M,T=R N with M,N invertible and M N^T=I9.
Thus N=M^(-T); if m_i=(a_i,c_i),n_i=(b_i,d_i) are coefficient columns,

    m_i^T n_j=delta_ij,       sum_i a_i b_i^T=I8.                 (1)

This is a consequence of full rank, not a restriction to a gauge-search orbit.
In particular at least eight terms are mixed: a_i and b_i are both nonzero.
All nine factor columns are nonzero, and a basis contains at most one column
on any fixed coefficient line.

The executable model.py computes the exact rational kernel of each of the
511 character constraints, separately for L and R. For h in F2^9\{0}, it
uses rows i for which h dot label_i=1. A coefficient column has support in
h^perp precisely when it belongs to this kernel. Rational RREF supplies
both exact ranks and null vectors; these kernels extend unchanged to C.
No numerical or mod-prime-only upper bound is used.

Let z=(0,...,0,1), l=(s,-4), v=(s,0), u=(t,-4). Let E_r denote a column
whose binary support spans the hyperplane perpendicular to removed-frame
label r, with a nonzero original coordinate component. The entire catalogue is:

- Left Z: coefficient line Cz, physical support {j}, binary span dimension1.
- Left E_r: coordinate coefficient direction e_r, with arbitrary z coefficient
  if s_r!=0 and zero z coefficient otherwise; nonzero coordinate part. Span8.
- Left V: coefficient line Cl; binary support span j^perp, dimension8.
- Left F: every remaining nonzero coefficient vector; full binary span9.
- Right W: coefficient line Cz, physical support {j,k}, binary span dimension2.
- Right E_r: coordinate coefficient direction e_r, with arbitrary z coefficient
  if t_r!=0 and zero z coefficient otherwise; nonzero coordinate part. Span8.
  This equals the left-side rule here because supp(t)=supp(s)={1,2,4,7}.
- Right V: coefficient line Cv; binary support span j^perp, dimension8.
- Right U: coefficient line Cu; binary support span k^perp, dimension8.
- Right F: all remaining nonzero coefficients; full binary span9.

There are10 distinct nonzero character kernels on the left and11 on the right.
Their nullity histograms over511 characters are respectively
{0:251,1:256,2:4} and {0:378,1:129,2:4}.
model.py checks each kernel against these symbolic model spaces. It also
checks that any intersection between distinct nonzero kernel spaces is either
zero or the pure z line. Consequently every non-pure proper support has
exactly ONE nonzero annihilating character and dimension8. This handles every
complex coefficient, including cancellations and isotropic choices. It does
not infer universal support types from finitely sampled coefficient vectors.

The certificate computes the actual binary pairing rank for representatives
of every class pair. Once the two support spans are fixed, bilinearity makes
this the same rank for EVERY member of those classes. the classification field of CERTIFICATE.json
contains the full11-by12 table. Its proof-relevant consequences are:

(a) Every mixed term costs at least7. A cost7 mixed term requires left V or
right V/U. Left V paired with right V costs8.
(b) The only zero-cost class pair is left Z with right V.
(c) Left Z costs1 against every right class other than V.
(d) Right W costs1 against left Z or V, and2 against every left E/F.

For clarity, a coefficient-vector dimension or rank is never used as a COPY
rank. All numbers in (a)-(d) are ranks of the actual binary support pairings.

## 2. Duality excludes zero terms and controls low-rank terms

The relevant exact coefficient pairings are

    z^T v=0,        l^T v=4,        l^T u=18.                (2)

Left Z/right V therefore cannot be an actual factor pair: its diagonal
coefficient pairing would be zero, contradicting m_i^T n_i=1 in (1).
Thus all nine COPY charges are positive. This does NOT claim that cost-zero
terms are generally impossible for masked decoders; it uses this fixed K.

There are at most two cost7 mixed terms. If left V never occurs, the only
possibilities use right V or U, each a fixed line occurring at most once in
an invertible basis. If left V occurs at index i, (2) forces every right V/U
column to have the SAME index i; otherwise off-diagonal duality fails. They
cannot both occupy that column. All other mixed terms then cost at least8,
and at most one mixed term costs7.

## 3. Exhaustive compensation cases

If all nine terms are mixed, their rank profile dominates

    (8,8,8,8,8,8,8,7,7).                                   (3)

Otherwise there are exactly eight mixed terms and one unmixed term i.

**A. Left column i is pure Z.** Equation (1) forces d_j=0 for every j!=i.
Right U has nonzero last coefficient, so it cannot occur among the eight
mixed terms. Only left V/right V can furnish cost7, and their nonzero
cross-pairing in (2) permits at most one such term. The unmixed term has
positive integer cost by section2, so the complete profile dominates

    (8,8,8,8,8,8,8,7,1).                                   (4)

This case includes the possibility that both sides of term i are pure.

**B. Right column i is pure W and left column i is not pure.** Duality forces
c_j=0 for j!=i, excluding left V from all mixed terms.
If left column i is V, its nonzero pairings with both right V and U in (2)
exclude these two right classes at every mixed index. All eight mixed terms
cost at least8; the unmixed V/W term costs1. The profile dominates

    (8,8,8,8,8,8,8,8,1).                                   (5)

If left column i is E or F, its W pairing costs2. The eight mixed terms
have at most two cost7 terms, giving the complete lower profile

    (8,8,8,8,8,8,7,7,2).                                   (6)

These exhaust all nine-term factorizations: a non-mixed term must have
one of its coordinate projections zero. No compensation term is omitted.

## 4. All real powers 0<q<=1, and attainment

Let P=(8,8,8,8,8,8,8,7,1). Profiles (3) and (5) dominate P coordinatewise
when sorted, and (4)=P. Profile (6) and P have the same total64. The descending
partial sums of (6) do not exceed those of P. Hence (6) is majorized by P,
and concavity of x^q for0<q<=1 gives sum(6)^q >= sum(P)^q. The exact integer
partial-sum certificate is checked in model.py; there is no numerical
sampling over q. This proves the stated universal lower bound.

For an attaining factorization, take p=1 (the first nonzero coordinate of s).
Let N be I9 with column p replaced by v=(s,0); it is invertible since s_p=1.
Set M=N^(-T), D=L M and T=R N. WITNESS.json gives M and N exactly; model.py derives D and T.
Independent all12,544-entry multiplication and binary support elimination
return ranks (8,7,8,8,8,8,8,8,1). This attains P for every q simultaneously.
This is a single derived basis choice, not a coefficient/shear search.

For0<q<1, strict subadditivity gives 7^q+1>8^q, so the sharp bill is strictly
greater than8*8^q. Atq=1 they coincide at64. This proves the prospective
COPY-power hypothesis, with a sharper same-object conclusion.

## Evidence boundaries and credit

The universal result is the written argument using complete finite character
and pairing premises. The JSON files are exact finite evidence; they are not a
formal proof-assistant certificate. The mathematical proof and exact witness were independently reviewed by separate
Opus agents. This is AI-agent review; no independent human review or formal
verification is claimed.

Source completion and factorization65: commdata2338 / PR2021. One-anchor
classification method and compensation precedents: Arham Tahir / PR1591,
bitplane / PR1652, and the PR845/717/968/1077 geometry lineage. The R-space
classification and specific fixed-completion dual pairings are checked afresh;
the one-anchor theorem is NOT assumed to apply to R. All predecessor files
remain unchanged. Substantial OpenAI Codex, Claude Code and Gemini assistance.

No native/frame, arbitrary-dirty physical realization, owner hosting,
precision/reserve, all-size or selected-exponent claim is made. The proof concerns
nine factors of precisely this matrix with separate actual-support COPY billing.
Changing the completion, labels, term count or sharing physical COPY work changes
the theorem's premises.

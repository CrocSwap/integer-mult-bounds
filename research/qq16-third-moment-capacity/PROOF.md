# A third-moment lower bound for the QQ16 transcript

Fix the conserved F0/B_1_2 maps and ordinary tail of Ali Romman's
[PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969), retained
in `research/joint-query`. Let G be a finite group of actual owner routes,
acting regularly, and write N=|G|. Use cover-dependent fields constant in
every payload block. Payload translations then act trivially, but the
owner action remains regular. No nonfaithful quotient identifies routes.

Under the inherited erased-family observation contract, an additional
read-only rational-linear record of rank at most d leaves at least

```text
max(0, ceil(176N/13) - d)
```

original selected A/T dimensions invisible. In particular, thirteen
rational scalars per owner leave at least ceil(7N/13) invisible dimensions.
Fourteen is necessary, not proved sufficient or a sharp minimum.

The two-moment method is Ross Richardson's PR2104. The joint A/T defect
identity is commdata2338's PR2153. This contribution supplies the third
moment and the spectral polynomial that strengthen their bound.

## 1. Exact route premise

Write B_s=R_s iota_U for s=0,1,2. The ordinary set U has 96 ports.
For each p in U let r_p be its eight-component integer query column and
let g_s(p) be its owner route. The frozen packet gives

```text
g_0(p)=1,       ||r_p||^2=4,
sum_p r_p r_p^T=48 I_8.
```

Each g_s(p), s=1,2, swaps an ordered orthonormal eight-frame C_p in the
first nine binary axes with eight external axes E_s. The external axis
sets are disjoint: E_1 uses axes 9 through 16, E_2 uses 17 through 24.
Each route fixes the unused external block and the remaining 48 axes.
The 96 ordinary ordered frames C_p are distinct.

These are finite source facts, checked on the literal F1/F2 alignment
maps and rebound to the current and future alignments in B_1_2. The
verifier checks both the complete ordered-product sets and an independent
chart-swap reconstruction. It does not execute the native local words.

The swap description proves

```text
{g_1(p)g_1(q): p,q in U} intersect
{g_2(r)g_2(t): r,t in U} = {1}.
```

Indeed, a stage-2 product fixes E_1 pointwise. If a stage-1 product also
fixes E_1, then g_1(q)e_i=C_q,i must equal g_1(p)^-1 e_i=C_p,i for every
external basis vector e_i. Distinctness of the ordered frames forces p=q.
The same argument gives r=t. Thus identity products have only diagonal
port pairs. The independent full census gives 9,216 ordered pairs and
9,121 distinct products per stage, with exactly one common product.

The relative routes g_s(p)g_t(p)^-1 are also distinct over the 96 ports
for each s<t. The executable checks all three pairs. For the stage-1/2
pair this also follows from the product intersection above.

## 2. The third moment

For the regular owner action Q_g, tr(Q_g)=N for g=1 and zero otherwise.
Consequently B_s B_s*=48 I_(8N). Set

```text
P_s = B_s*B_s/48,          T = P_0+P_1+P_2.
```

Each P_s is an orthogonal projection of rank 8N. The two-moment source
calculation gives

```text
tr(P_s P_t) = (2/3)N       for s != t.
```

To see the normalization, the coefficient at the relative route indexed
by p in B_s B_t* is r_p r_p^T. Distinctness makes the identity trace of
B_s B_t* B_t B_s* equal sum_p ||r_p||^4 N = 1536N.
Divide by 48^2 to obtain (2/3)N.

The distinct-stage triple has the ordered trace

```text
tr(P_0 P_1 P_2) = tr(B_0 B_1* B_1 B_2* B_2 B_0*) / 48^3.
```

Its group word for ports p,q,r is

```text
g_1(p)g_1(q)g_2(q)g_2(r).
```

It is identity exactly when g_1(p)g_1(q)=g_2(r)g_2(q).
Section 1 forces p=q=r. The scalar trace weight is
(r_p^T r_q)(r_q^T r_r)(r_r^T r_p), hence

```text
tr(P_0 P_1 P_2) = 96 * 4^3 N / 48^3 = N/18.
```

Cyclic invariance of trace and transpose give the same value for all
six distinct-stage orderings. In the cubic expansion, three words use
one stage, eighteen use exactly two, and six use three. Therefore

```text
tr(T)   = 24N,
tr(T^2) = 24N + 6(2/3)N = 28N,
tr(T^3) = 24N + 18(2/3)N + 6(1/18)N = (109/3)N.
```

## 3. A spectral polynomial

All eigenvalues of T lie in [0,3], because it is a sum of three
orthogonal projections. Use the rational polynomial

```text
p(t) = 1 - (1 - 12t/13)^2 (1 - t/3)
     = (85/39)t - (248/169)t^2 + (48/169)t^3.
```

It has p(0)=0 and p(t)<=1 throughout [0,3]. Summing over the nonzero
eigenvalues gives rank(T)>=tr(p(T)). The exact moments imply

```text
rank([B0;B1;B2]) = rank(T)
 >= [(85/39)24 - (248/169)28 + (48/169)(109/3)] N
  = (280/13)N.
```

This improves the two-moment bound (144/7)N. It is still a lower bound,
not an exact rank calculation. Rational and real matrix ranks agree.

## 4. Transfer to the selected-input defect

This is PR2153's defect argument, restated to identify the inherited
contract. Write P_(s,A), P_(s,T) and ell_(s,A), ell_(s,T) for the
ordered selected sections and their two-sided inverses. For h in ker B1
put only pair 0 nonzero and set

```text
X_U=h,       Y_U=0,
X_A=-P_(0,A)B0h-P_(2,A)B2h,          Y_A=-X_A,
X_T=P_(0,T)ell_(0,A)P_(2,A)B2h,      Y_T=-X_T.
```

The original selected defect J(h)=(X_A,X_T) determines both queries:

```text
B0h=-ell_(0,A)X_A-ell_(0,T)X_T,
B2h=ell_(2,A)P_(0,A)ell_(0,T)X_T.
```

Conversely, the two queries determine J(h). Since rank(B1)=8N,

```text
dim J(ker B1)=rank([B0;B1;B2])-8N >= ceil(176N/13).
```

The ordered F0 query is zero. After F0 the ordinary fields are X_U=Y_U=h,
the selected A fields are opposite P_(2,A)B2h, and both T fields are zero.
At B_1_2 the future query is zero, the logger clears its A output,
and the current query is B1h=0. Only Y_(0,U)=h remains.

The retained witness proof and independent rational review establish
that the ordinary tail moves h into the former-Y hole. All selected
values after B1, completed-X descendants and five forward histories
are zero. Later homogeneous selected-only controls preserve zero.
The formal-h tail is inherited evidence, not rerun by this package.
There is no separately retained transient F0 A output or free read
of the former-Y hole in this observation contract.

Restrict an additional rational-linear record to this family, obtaining
C of rank at most d. Linear algebra gives

```text
dim J(ker C) >= dim J(ker B1) - rank(C).
```

A complement of ker C has dimension rank(C), so its image can account
for at most that many defect dimensions. A positive residual supplies
an input with zero observations but nonzero required selected output.
No decoder, even nonlinear, can distinguish it from zero. Fixed offsets
and common arbitrary dirty baselines do not change this comparison.

For q scalars per owner, capacity is at most qN on this subspace.
At q=13 the residual is at least ceil(7N/13)>0. An eight-coordinate
record, including the full original R2 X query, leaves at least
ceil(72N/13) invisible dimensions. Extra independent payload storage
must count in d. These are information dimensions, not paid ranks.

## 5. Limits

The finite route facts and exact arithmetic are checked by the new
verifier. The spectral and defect implications are written proofs,
not proof-assistant formalizations. The global erased-family trajectory
and local packet-to-native binding remain inherited from PR1969.

Records of width fourteen or fifteen remain unresolved. PR2174's
sixteen-coordinate logical recovery also grants selected values at
the B1 cut and does not supply a final-only physical controller.
Changed first pairs or schedules, nonlinear record encoders and a
complete native invoice lie outside this result. No supplier admission,
recursive precision bound or multiplication exponent change follows.

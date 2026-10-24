# Scalar centre mixing in the retained native word

The retained response grammar does not permit a rank-seven scalar centre
map with a nonzero diagonal data response. This result permits all 64
entries of the centre map to vary. It is not limited to deletion of one
centre coordinate.

The result does not give a lower bound for a changed native word. It does
not exclude scalar gates between unequal physical frames, a changed source
code, new native hops, or a new centre query or scatter space.

## 1. Source and question

Use the two providers in `new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz`.
The decompressed SHA256 is
`a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa`.
There are 112 data ports in each bank. The exact source matrices satisfy

\[
R\in\mathbb Z^{8\times112},\qquad K=R^T/4,\qquad RK=14I_8.
\]

The clean cross response is \(J=I-KR\). Each diagonal entry of \(KR\)
is one. Let \(A\) be an arbitrary constant scalar \(8\times8\) matrix.
The proposed centre response is \(KAR\). A fixed scalar factor on each
port can give an ideal shear only if a retained response \(E\) satisfies

\[
E+KAR=\operatorname{diag}(d_0,\ldots,d_{111}),\qquad d_p\ne0. \tag{1}
\]

A factorization through seven scalar centre channels has
\(\operatorname{rank}A\le7\). The calculation below permits such a
factorization without charging for its access. Thus a failure here is not
caused by an assumption that centre mixing is free.

The first test retains the source and helper computation, the Y-only
scalar word, and all native events. It changes only gains on existing
non-Y-to-Y ADDs. It permits arbitrary initial-I-helper entry corrections.
All other helper terms and all nonempty operator words must cancel.

The second test permits new one-way equal-frame ADDs at every cut in the
supplied `ALL-CUT-EDGES.json.gz` inventory. The source computation and the
Y-only tail remain fixed. No Y-to-source feedback is added. The inventory
has 4,276 products from 267,854 source/target pair checks. Its completeness
and physical cut admission are source dependencies. This packet checks
the supplied products; it does not create a stronger owner contract.

## 2. Exact existing-site certificate

`check_mixing.py` imports no producer. It replays each full clean word on
all 640 input columns. It checks scalar frames, native frame changes,
the source identity, all 408 arbitrary helper outputs, and the exact
clean-J data map. C0 is cleared. C1 through C7 retain their arbitrary
inputs in this source core.

The program builds the source row and remaining Y-tail column for each
existing cross ADD. There are 825 active site variables. Add the 64
entries of \(A\). The exact rational system has 13,900 equations and
889 variables. Its rank modulo 1,000,003 is 888. `MIXING.json` records
the independent row keys and pivot columns for both providers.

The original cross gains, together with \(A=I_8\), satisfy every equation
over the rationals. A nonzero minor modulo a prime is also nonzero over
the rationals. Therefore the exact rational nullspace has dimension one.
Every solution has

\[
A=cI_8. \tag{2}
\]

This rank argument does not restrict the denominators in a proposed
rational solution. In particular, division by an odd integer does not
change the result. The first certificate uses coefficientwise cancellation
in the formal operator-word model. The next certificate removes that
restriction for the supplied all-cut products.

## 3. Spatial support of the actual monomial words

Write \(q_p\in\mathbb F_2^9\) for the actual odd label of port \(p\).
At a listed cut, let \(F\) be its current native frame subspace. For each
source term from X port \(s\), let \(W\) be its ordered logical warp word.
The source definition `new-native-recipes-20261017/sources/bw_adapters.py`
defines each warp as a monomial \(K_G\) with linear address part \(G\).
Its quadratic phase can be nonzero. A negative occurrence has linear
part \(G^{-1}\).

The checker composes these signed linear maps in event order. It checks

\[
W_{\rm lin}q_s\in F,
\qquad F\subseteq q_t^\perp \tag{3}
\]

for each final target \(t\) in the remaining scalar Y tail. Both providers
pass 6,920 source-term checks and 8,856 source/target incidences. These
counts include 1,160 nonempty source words. They do not discard the actual
warp terms.

Suppose \(q_t\cdot q_s=1\). Equation (3) implies
\(W_{\rm lin}q_s\ne q_s\). In the computational basis,

\[
\langle q_s|W|q_s\rangle=0. \tag{4}
\]

Every monomial phase is irrelevant to this zero. Equation (4) remains true
after any scalar sum of these terms. Thus an identity operator on the
payload cannot appear in this source/target response. This argument does
not assume that distinct warp words are linearly independent.

The same witness works at every tensor depth \(\lambda\ge1\). Use the
input label \((q_s,0,\ldots,0)\). A linear warp fixes each zero column and
fails to fix the first column. This is a spatial-basis argument. It is not
a Fourier-character or constant-payload argument.

It follows that every solution of (1) must satisfy

\[
R_{:,t}^{\,T} A R_{:,s}=0
\quad\text{if }t\ne s\text{ and }q_t\cdot q_s=1. \tag{5}
\]

## 4. A small integer certificate

There are 6,608 pairs in (5). `SUPPORT.json` gives 63 of them. Delete the
column for \(A_{7,7}\) from their coefficient matrix. The resulting
\(63\times63\) integer matrix has determinant

\[
-2361183241434822606848=-2^{71}. \tag{6}
\]

The checker computes this determinant by exact integer elimination. It
also checks that \(I_8\) satisfies all 6,608 equations exactly. Hence the
kernel of (5) is precisely (2). This conclusion holds over the rationals
and the Gaussian rationals. The power-of-two minor also gives the same
kernel over coefficient rings in which two is a unit, for these scalar
equations.

If \(c\ne0\), \(cI_8\) has rank eight. If \(c=0\), the diagonal response
in (1) is zero: the support argument also excludes each same-port scalar
response, since every \(q_p\) is odd. Therefore no rank-seven \(A\)
solves (1) in this grammar.

A concrete test shows why a nonzero diagonal is not sufficient. The
dyadic rank-seven projection

\[
A=I_8-\mathbf1\mathbf1^T/8
\]

gives diagonal entries of \(KAR\) equal to 1 on 42 ports, 7/8 on 56 ports,
and 1/2 on 14 ports. All are nonzero. The matrix fails the off-diagonal
conditions (5).

## 5. Reproduction and limits

Run from the repository root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/coherent-port/centre-mixing-20261018/check_mixing.py
python3 -I -B work/centre-encoding-campaign-20261014/lanes/coherent-port/centre-mixing-20261018/check_support.py
```

The first command gives quotient rank 63 and exact rational nullity one
for each provider. The second command gives
`PASS_SPATIAL_SUPPORT_AND_INTEGER_MINOR` and determinant `-2^71` in decimal.
The first checker uses assertions and rejects `-O`.

`probe_all_cuts.py` is a separate modular check of the supplied inventory.
It finds product-space rank 3,740 and centre-quotient rank 63. The proof
in Sections 3–4 does not use a rational lift of that modular basis.

This result does not test a changed centre query dictionary, a changed
centre scatter space, arbitrary operator-valued centre entries, unequal-
frame physical gates, changed native paths, or global encoded endpoints.
It does not give a native-child lower bound for those larger grammars.
It supplies no complete controller, all-size cost, precision result, or
improvement in the multiplication exponent.

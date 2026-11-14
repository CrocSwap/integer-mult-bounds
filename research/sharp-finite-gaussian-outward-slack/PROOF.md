# Sharp finite radius-five Gaussian outward slack

## Theorem

Let

\[
S_5=\{x\in\mathbb Z^4:\|x\|_2^2\le25\},\qquad
U=H_4/2,
\]

where

\[
H_4=\begin{pmatrix}
1&1&1&1\\
1&-1&1&-1\\
1&1&-1&-1\\
1&-1&-1&1
\end{pmatrix},\qquad H_4^T H_4=4I.
\]

For an injection \(F:S_5\to\mathbb Z^4\), require the pointwise error
\(\|F(x)-Ux\|_2\le1\), and define its outward slack by

\[
\Delta(F)=\max_{x\in S_5}(\|F(x)\|_2-\|x\|_2).
\]

The minimum of \(\Delta(F)\) over these finite injections is exactly

\[
\beta=\sqrt{21}-\sqrt{19}.
\]

The same \(\beta\) is a necessary lower bound for the global outward slack of
any injective integer-output map on \(\mathbb Z^4\) with uniform error at most
one for \(U\). By an exact signed-permutation transfer, this applies to the
actual ideal Gaussian pair map \(C_+\) from #6509 and, by conjugation, to
\(C_-\). The global infimum at error cap one is only bounded here by
\([\beta,1]\); this note does not construct a global map attaining \(\beta\).

## Finite proof

The compressed certificate [R5-OPTIMUM.json.gz](R5-OPTIMUM.json.gz) is the
byte-exact expansion of the pinned R5 input in `SOURCES.json`. It contains a
pair \((x,F(x))\) for each point of \(S_5\), together with a Hall input set
\(T\) and its claimed strict-\(\beta\) output neighborhood. The checker
`verify.py` uses only the standard library and does not import the search,
constructor, or earlier author checker.

First, it independently enumerates \(S_5\) and verifies the 3,121 listed
pairs. It checks that each input appears once, outputs are distinct, the
integer numerator of each squared error is at most four, and every outward
increment is at most \(\beta\). All square-root comparisons use integer
arithmetic: comparing \(\sqrt m-\sqrt n\) with \(\sqrt a-\sqrt b\) is
reduced to comparing the nonnegative sums \(\sqrt m+\sqrt b\) and
\(\sqrt a+\sqrt n\), then resolved by sign-aware integer squaring. Fifty-eight
matching edges attain \(\beta\), with squared input and output norms 19 and
21, so this injection has \(\Delta(F)=\beta\).

For the lower bound, the certificate gives \(|T|=1,692\). For every \(x\in
T\), the verifier enumerates all integer outputs \(y\) satisfying
\(\|y-Ux\|_2\le1\). It uses the exhaustive coordinate interval

\[
\left\lceil\frac{(H_4x)_i-2}{2}\right\rceil
\le y_i\le
\left\lfloor\frac{(H_4x)_i+2}{2}\right\rfloor
\]

and retains a candidate exactly when
\(\sum_i(2y_i-(H_4x)_i)^2\le4\). It then filters by the exact strict
condition \(\|y\|_2-\|x\|_2<\beta\). The complete union of these strict
neighbors has 1,691 outputs, exactly the certificate's declared set. Thus
Hall's inequality rules out an injection even at every threshold below
\(\beta\). Together with the matching at \(\beta\), this proves the exact
finite optimum.

This lower-bound argument uses only a subset of the inputs and the complete
set of their allowed outputs. In particular, no search history or assumption
about a matching algorithm is part of the proof. The verifier also confirms
that if equality at \(\beta\) is incorrectly admitted into the Hall graph,
the neighborhood grows to 1,719 outputs; the strict inequality is essential.

The same strict graph has a shorter, certificate-independent invariant Hall
witness. The set \(T_1\) has 1,809 inputs and its complete strict-\(\beta\)
neighborhood lies in the explicitly described 1,777-point set \(N_1\), so
it gives deficiency at least 32. Its two-exclusion orbit formula, exact
representative check, and full quotient min-cut are in
[compact-hall/PROOF.md](compact-hall/PROOF.md). This supplement does not
replace the matching witness needed for the upper bound.

## Transfer to the actual pair map

In real coordinates \((\Re x,\Im x,\Re y,\Im y)\), the numerator matrix for
the ideal pair \(2C_+\) is

\[
2C_+=\begin{pmatrix}
1&-1&1&1\\
1&1&-1&1\\
1&1&1&-1\\
-1&1&1&1
\end{pmatrix}.
\]

Define the signed permutations

\[
R(a,b,c,d)=(a,-b,c,d),\qquad L(a,b,c,d)=(a,c,-d,b).
\]

Direct integer multiplication gives

\[
H_4=L(2C_+)R.
\]

Therefore \(H_4/2=L C_+R\). If \(F_C\) is a pair map for \(C_+\), then
\(F_H(x)=L F_C(Rx)\) is the corresponding map for \(H_4/2\). In the other
direction, \(F_C(x)=L^{-1}F_H(Rx)\), since \(R^{-1}=R\). These transformations
preserve the integer lattice, the complete input ball, injectivity, error,
and both input and output norms. Complex conjugation is another signed
permutation and transfers the result to \(C_-\). The checker verifies the
matrix identity and signed-permutation conditions exactly.

Consequently any global injective \(C_+\) or \(C_-\) rounder with error at
most one has outward slack at least \(\beta\), by restriction to the
transferred copy of \(S_5\). The #6509 source supplies a global bijective
rounder with error at most one; the triangle inequality gives outward slack
at most one. Thus the global infimum lies in \([\beta,1]\), conditional on
that inherited #6509 construction. This package proves no global sufficiency
below one.

## Scope and predecessor credit

The R5 matching and Hall set were supplied as candidate data by the current
@CubeJerry workstream. This package independently checks the finite claim and
the native-pair transfer. Its exact source hashes, author context, and
canonical base are in `SOURCES.json`.

Nick Petalas's #6619 studies radial error and norm contraction for rational
orthogonal maps; it cites ywz65's finite-sphere argument in #2589. Ali
Romman's #6509 supplies the ideal pair map, its inverse, and its global
error-one construction. Those are credited predecessor results. The finite
R5 Hall obstruction and its exact transfer are the claim established here.
The package makes no claim about other radii, other error caps, global
attainment at \(\beta\), a new \(\kappa\), or a change to the conditional
multiplication frontier.

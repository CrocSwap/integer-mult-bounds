# Optimal binary Schur sharpness dimension: n = 3d for every d >= 2

**Written algebraic theorem with exact finite corroboration. No new kappa.**
Prepared by **lee-phys**, with substantial OpenAI Codex assistance, under
Apache-2.0. This resolves the minimal-dimension question left by
[PR4617](https://github.com/CrocSwap/integer-mult-bounds/pull/4617) for every
d >= 2 in its invertible-block setting.

The requested first case, d = 3 and n = 9, has an explicit witness below.
A single block construction then handles every odd d >= 3 and every even d >= 2.
The proof uses only binary matrix algebra and two fixed seed matrices.

## 1. Statement and conventions

All matrices are over the field $\mathbb F_2$ and act on column vectors.
Addition and subtraction coincide. A projector means an algebraic idempotent,
not an orthogonal or symmetric projector.

For an n-by-n matrix with a common coordinate split d + (n-d), write

$$
X=\begin{pmatrix}A&B\\ C&D\end{pmatrix}, \qquad
\operatorname{Sch}_d(X)=D-CA^{-1}B,
$$

when A is invertible. Define $[S,Z]=SZ-ZS$.

**Theorem.** For every integer d >= 2, the smallest ambient dimension n for
which there exist commuting idempotents P,Q with invertible leading d-by-d
blocks and

$$
\operatorname{rank}[\operatorname{Sch}_d(P),\operatorname{Sch}_d(Q)]=2d
$$

is exactly n = 3d. The construction has
$\operatorname{rank}P=\operatorname{rank}Q=2d$ and equal leading blocks.
These blocks are invertible; they are **not required to be identity matrices**.

The rank bound 2d for general commuting pairs is the predecessor result of
Nick Petalas, [PR4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597).
For the minimum-dimension theorem here, the necessary bound follows directly
from size: the commutator is (n-d)-by-(n-d), so rank 2d requires n-d >= 2d.
It remains to construct a pair at n = 3d.

The case d = 1 is outside the new theorem. Ryanson Jonathan's
[PR4609](https://github.com/CrocSwap/integer-mult-bounds/pull/4609) reports
minimum n = 5 over $\mathbb F_2$ for that case. That negative classification
is credited, not independently repeated here.

## 2. Construction from a matrix without eigenvalues 0 or 1

The construction isolates the compatibility between P and Q in their deleted
block. After elimination, the two surviving blocks are coupled by an invertible
matrix R. We arrange that both R and R+I are invertible, which makes their Schur
commutator invertible too.

Let T be any d-by-d binary matrix for which T and $A=I+T$ are both invertible.
In three blocks of size d, set

$$
P=\begin{pmatrix}
 A&A&T\\
 T&T&T\\
 0&0&I
\end{pmatrix},
\qquad
Q=\begin{pmatrix}
 A&T&A\\
 0&I&0\\
 T&T&T
\end{pmatrix}. \tag{1}
$$

Their leading blocks are both A. We now verify all remaining properties.

### Idempotence, commutation and projector ranks

Introduce the rectangular matrices

$$
L=\begin{pmatrix}I\\I\\0\end{pmatrix},\quad
M=\begin{pmatrix}I\\0\\I\end{pmatrix},\quad
F=\begin{pmatrix}T&A&T\end{pmatrix},\quad
G=\begin{pmatrix}T&T&A\end{pmatrix}.
$$

Because T+A=I and T+T=0,

$$
FL=GM=I,\qquad FM=GL=0.
$$

Directly expanding (1) gives $P=I_{3d}+LF$ and $Q=I_{3d}+MG$.
Consequently,

$$
(LF)^2=L(FL)F=LF,\qquad (MG)^2=M(GM)G=MG,
$$

and $LF\,MG=L(FM)G=0$, $MG\,LF=M(GL)F=0$. Thus

$$
P^2=P,\quad Q^2=Q,\quad PQ=I_{3d}+LF+MG=QP.
$$

Since FL=I, L is injective and LF is a projector of rank d.
The kernel of $I_{3d}+LF$ is exactly the image of LF: if
$x=LFx$ then x is in that image, and every vector in that image is fixed by LF.
Hence P has rank 3d-d=2d. The same argument applies to Q.

### Schur complements

T commutes with A=I+T and therefore with its inverse. Put $R=TA^{-1}$.
For P, the off-diagonal blocks at the d + 2d split are
$B_P=(A\ T)$ and $C_P=(T\ 0)^{\mathsf T}$, giving

$$
\begin{aligned}
S=\operatorname{Sch}_d(P)
&=\begin{pmatrix}T&T\\0&I\end{pmatrix}
 +\begin{pmatrix}T\\0\end{pmatrix}A^{-1}
  \begin{pmatrix}A&T\end{pmatrix}\\
&=\begin{pmatrix}0&T+TA^{-1}T\\0&I\end{pmatrix}
 =\begin{pmatrix}0&R\\0&I\end{pmatrix}.
\end{aligned}
$$

The last equality uses
$T+TA^{-1}T=TA^{-1}(A+T)=TA^{-1}$.
Likewise, with $B_Q=(T\ A)$ and $C_Q=(0\ T)^{\mathsf T}$,

$$
Z=\operatorname{Sch}_d(Q)=\begin{pmatrix}I&0\\R&0\end{pmatrix}.
$$

In particular, S and Z are idempotent. Their commutator is

$$
K=[S,Z]=\begin{pmatrix}R^2&R\\R&R^2\end{pmatrix}. \tag{2}
$$

Here R is invertible and

$$
R+I=(T+A)A^{-1}=A^{-1}
$$

is invertible. In characteristic two, the cross terms in the square of (2)
cancel, so

$$
K^2=
\begin{pmatrix}
R^2(R+I)^2&0\\
0&R^2(R+I)^2
\end{pmatrix}. \tag{3}
$$

Both diagonal blocks are invertible. Therefore K is invertible and has rank
2d. This proves the construction lemma for every admissible T, without any
assumption that T is diagonalizable or belongs to a field extension.

## 3. The requested d = 3, n = 9 witness

Take

$$
T_3=\begin{pmatrix}0&0&1\\1&0&1\\0&1&0\end{pmatrix}.
$$

Direct multiplication gives $T_3^3+T_3+I=0$, hence

$$
T_3(T_3^2+I)=I,\qquad (T_3+I)(T_3^2+T_3)=I.
$$

Thus both T_3 and I+T_3 are invertible. Inserting T_3 into (1) yields the
following matrices. Each binary string is one row in left-to-right column
order; multiplication is modulo two.

    P9                     Q9
    101101001              101001101
    111111101              111101111
    011011010              011010011
    001001001              000100000
    101101101              000010000
    010010010              000001000
    000000100              001001001
    000000010              101101101
    000000001              010010010

Deleting the first three coordinates gives the commutator

    K6
    101111
    111100
    011110
    111101
    100111
    110011

Equation (3) proves its invertibility; direct binary elimination independently
checks rank 6 in the accompanying verifier. P9 and Q9 both have rank 6.

## 4. Every odd d, then all d >= 2

Use also the two-dimensional seed

$$
T_2=\begin{pmatrix}0&1\\1&1\end{pmatrix}.
$$

It satisfies $T_2^2+T_2+I=0$, so $T_2(T_2+I)=I$. Therefore T_2 and I+T_2
are invertible.

For odd d=3+2k with k >= 0, choose

$$
T=T_3\oplus T_2^{\oplus k}.
$$

For even d=2k with k >= 1, choose $T=T_2^{\oplus k}$.
In each case T and I+T are block diagonal with invertible blocks.
Section 2 therefore produces the required pair in dimension 3d.
Together with the size lower bound, this proves the theorem.

Appending equal zero blocks to P and Q also attains rank 2d at every n > 3d
with the same leading d-coordinate split. This does not address all possible
projector ranks or prescribe the leading blocks to be identity.

## 5. What is new, and what is checked

- **Predecessor #4597:** ordered block-Schur commutator identity and the 2d
  bound, with sharpness over $\mathbb F_5$.
- **Predecessor #4609:** binary examples at (n,d)=(5,1) and (6,2), and small
  minimal-dimension results. Its d=2 example already yields optimal even d
  by direct sums and a coordinate permutation.
- **Predecessor #4617:** uniform binary sharpness at n=5d, leaving minimal n
  open. The new part here is the explicit optimal d=3 example and the
  block-algebra proof closing every odd d>=3; the same formula covers even d.

Exact heads inspected:

| PR | Contributor | Head |
|---|---|---|
| [4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597) | Nick Petalas | dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb |
| [4609](https://github.com/CrocSwap/integer-mult-bounds/pull/4609) | Ryanson Jonathan | eb5ccf9288808d973551e6264300d30d2f6e48a0 |
| [4617](https://github.com/CrocSwap/integer-mult-bounds/pull/4617) | Ryanson Jonathan | 96c01a2124e234d798e9e97643c20fb5b430840d |

The standalone verifier independently computes full-matrix products, inverses,
Schur complements and ranks. It checks the literal 9-by-9 witness, the block
formula for d=2 through 12, and one larger-ambient padding. It exhausts all
16 binary 2-by-2 and all 512 binary 3-by-3 seed matrices: respectively 2 and
48 have both T and I+T invertible, and every such seed passes the full checks.
This enumerates seeds for our family, not all projector pairs.

Six rejecting controls preserve or break distinct hypotheses: a singular
leading block; zero T; nonzero singular T; identical projectors with zero
commutator; a bit change destroying idempotence; and a separately conjugated
projector retaining idempotence and its invertible pivot but losing commutation.
Checks remain active under optimized Python.

The universal result is proved in Sections 1-4, not extrapolated from the finite
checks. This is author-checked work with substantial AI assistance; independent
human review and formal proof-kernel verification are not claimed.

## 6. Reproduce and scope

From the repository root, using Python 3.12 and the standard library:

    python3.12 -W error -B research/binary-schur-minimal-dimension/verify.py
    python3.12 -W error -O -B research/binary-schur-minimal-dimension/verify.py
    python3.12 -B scripts/research_package.py --package research/binary-schur-minimal-dimension --check-only
    python3.12 -B scripts/research_package.py --package research/binary-schur-minimal-dimension

Expected direct marker: PASS_BINARY_SCHUR_MINIMAL_DIMENSION.
The registered runner additionally reports PASS_REGISTERED_RESEARCH_PACKAGE.

The proof and verifier are self-contained. No pending predecessor executable,
matrix file, or external library is a live input. SOURCES.json pins the task
catalogue and selected record only as historical provenance at main
fbc9ea0249746acca4f504d4fda2b84e0e36cf0d; neither enters the theorem.
TASK.json records the donor's explicit scope and the original card.

This is a local algebraic interface result in the block-Schur line arising
from BIT/header work. It does not provide a header density, physical caller,
supplier admission or an improved integer-multiplication exponent. The
selected construction, full scientific replay, Lean and Docker are outside
the verification scope. The optional full-history preflight is not run in
this shallow checkout.

## Open next questions

**What changes if both leading blocks must equal I_d?** The present construction
uses A=I+T, and setting A=I in this family forces T=0 and destroys sharpness.
That observation excludes only this parametrization. The predecessor n=5d
construction has identity pivots, so existence is known with more room.

This question separates arbitrary invertible pivots from a stronger interface.
Start by deriving the block identities forced by P^2=P, Q^2=Q and both pivots I_d,
then test whether they obstruct rank 2d at n=3d. A sharp result for that additional
constraint is not supplied here. The same question is structured in TASK.json.

## Credit

Nick Petalas supplies the block-Schur bound and its predecessor PR4278.
Ryanson Jonathan supplies the binary witnesses, the n=5d construction and the
minimal-dimension question, with Claude Code assistance as credited in those
packages. The present construction, written proof and standalone verifier were
prepared by lee-phys with substantial OpenAI Codex assistance. No predecessor
code or data is copied into this package. Apache-2.0.

# Two coordinate swaps cost exactly six calls

This is a scoped theorem about a formal nonabelian register model. The proof
below holds for any finite number of restored dirty registers. The finite
censuses corroborate the proof and its implementation; they are not its
all-register justification.

## 1. Complete model and statement

Let `G = GL_2(F2)`, acting on two binary address coordinates, and let
`R = F2[G]` be its **formal group algebra**. Write

\[
 a=\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
 b=\begin{pmatrix}1&0\\1&1\end{pmatrix},\qquad
 s=\begin{pmatrix}0&1\\1&0\end{pmatrix}=aba=bab.
\]

These are the two coordinate CNOTs and the coordinate swap. They are distinct
involutions; `ab != ba`. Products are matrix products, so the rightmost map
acts first. The six group elements are `1,a,b,ab,ba,s`.

For any finite `r >= 2`, a register word is an `r` by `r` matrix over `R`.
The complete allowed alphabet is:

* A free scalar basis change `B in GL_r(F2)`, embedded using the identity
  group label. This grants all scalar XOR preparation and restoration for
  free, an optimistic paid-call relaxation.
* A paid unit
  \[
   D_N(g)=I+([g]+1)N,\qquad
   g\in\{a,b\},\quad N=uv^T,\quad v^Tu=1,
  \]
  with binary `u,v`. Thus `N` is a rank-one idempotent. Each occurrence
  costs one, including undo operations.

There are no free address transformations, translations, copies, erasures,
or clean allocations. The `r-2` additional registers start arbitrarily dirty
and must be returned identically; no effect of their inputs may leak to an
active output. Their availability is otherwise free in this relaxation.

Put `P=diag(1,1,0,...,0)`. The required endpoint is the formal identity

\[
 T=\operatorname{diag}([s],[s],1,\ldots,1)
   =I+([s]+1)P.                         \tag{1}
\]

Equality in `M_r(R)` is required, not equality in the two-dimensional
address-matrix representation. In particular, it implies the boundary on
every `R`-module and arbitrary register inputs.

**Theorem.** For every finite `r >= 2`, the minimum paid-call count for (1)
is exactly **six**. Arbitrarily many restored dirty registers and arbitrary
free scalar mixing do not reduce the direct `3+3` bill in this alphabet.

This changes the address algebra of the rational abelian starting model. It
does not reduce rational frame entries modulo two and does not establish a
physical bit supplier or a multiplication exponent.

## 2. Normalize free scalar operations

Moving scalar basis changes to the right conjugates each `N` by an invertible
binary scalar matrix. Rank one and idempotence are preserved, and `g` remains
`a` or `b`. Any word becomes a product of the same number of paid units,
followed by one scalar matrix `B_total`.

The augmentation `R -> F2`, `[g] -> 1`, sends every paid factor to `I` and
sends (1) to `I`. Consequently `B_total=I`. It suffices to consider products
of paid units alone. This does not normalize away address transformations;
none are available for free in the stated alphabet.

## 3. The number of paid calls is even

The action of `G` on its three nonzero address vectors identifies it with
`S_3`. Its sign homomorphism sends each of `a,b,s` to the nonidentity element
`t` of `C_2`. In characteristic two,

\[
 \mathbb F_2[C_2]\cong\mathbb F_2[\epsilon]/(\epsilon^2),\qquad
 t=1+\epsilon.
\]

Apply this group-algebra homomorphism to the normalized word. Each paid factor
becomes `I+epsilon N_j`; the product is exactly
`I+epsilon sum_j N_j`, because `epsilon^2=0`. The target becomes
`I+epsilon P`. Thus

\[
 \sum_j N_j=P.
\]

Taking the binary trace gives

\[
 \#\text{calls}\equiv\sum_j\operatorname{tr}N_j
 =\operatorname{tr}P=0\pmod2,
\]

since `tr(uv^T)=v^Tu=1`. Any improvement on six must therefore use zero,
two or four calls. The zero- and two-call words have no `[s]` coefficient:
`s` has length three in the generators `a,b`.

## 4. Every four-call label pattern fails

Write `x=[a]+1`, `y=[b]+1`. These commute with scalar matrices (not with
one another), and `x^2=y^2=0`.

### At most three runs

A maximal run of one repeated label collapses exactly:

\[
 (I+xN_1)\cdots(I+xN_k)=I+x(N_1+\cdots+N_k),
\]

and likewise for `y`. With one or two runs, the support cannot contain `s`.
With three runs the product has the form

\[
 (I+xA)(I+yB)(I+xC)
\]

or its label-reversed counterpart. Its `[s]` coefficient is exactly `ABC`.
Four calls distributed among three nonempty runs have run lengths a
permutation of `(2,1,1)`. At least one of the outer runs has length one,
so `A` or `C` is a rank-one original projector. Consequently `rank(ABC)<=1`,
whereas (1) has `[s]` coefficient `P` of rank two. This is a contradiction.

### Four runs: `abab` or `baba`

Consider `abab` and define the linear coefficient functional

\[
 \lambda(f)=\operatorname{coeff}_{[s]}f+
            \operatorname{coeff}_{[ba]}f.
\]

Applied entrywise to the product, direct formal expansion gives

\[
 \lambda\big((I+xN_1)(I+yN_2)(I+xN_3)(I+yN_4)\big)=N_2N_3.       \tag{2}
\]

For completeness, among the sixteen selected subsets of positions, the
group-algebra monomial `yx` on positions `(2,3)` is the only one on which
`lambda` is one. Singletons and `xy` have neither coefficient; `x^2=y^2=0`;
both `xyx` and `yxy` contain `[s]` and `[ba]`, so their contributions cancel;
and `xyxy=xy`. This proves (2) without any commutativity assumption on the
`N_j`. The package independently expands these polynomials with noncommuting
formal scalar variables.

For (1), `lambda(T)=P`. Equation (2) would therefore require
`P=N_2N_3`, which has rank at most one. For `baba`, use the same argument
with `a,b` interchanged and the functional `coeff_[s]+coeff_[ab]`.

These cases exhaust the sixteen four-call label patterns. Combined with
parity, no word shorter than six reaches (1), for any `r`.

## 5. Six calls attain the bound with the complete formal boundary

For any scalar idempotent `N` and group elements `g,h`, expansion gives

\[
 D_N(g)D_N(h)=D_N(gh).
\]

Use `a,b,a` on `N=E_11`, followed by `a,b,a` on `N=E_22`. Since `aba=s`,
the product is exactly (1). Every other register is unchanged on arbitrary
dirty input. There are six paid calls, no additional role, no scalar basis
changes, and no omitted restoration operations. Free scalar work was granted
only in the lower-bound relaxation; the attaining word does not need it.

Allowing `s` itself as a paid unit would instead cost two calls, as in the
broader affine rank-priced model of PR1333. Allowing a rank-two scalar
projector at unit price would cost three calls. Both are outside this
alphabet, and both appear as explicit scope controls in the verifier.

## 6. What the finite replay does and does not prove

For `r=2,3`, enumerate every binary rank-one idempotent and both labels.
Their counts are `6,28` and therefore `12,56` paid generators. Each generator
is an involution. A breadth-first traversal constructs exact formal balls
`B_2,B_3`. A word of length at most five reaches `T` exactly when

\[
 \{p^{-1}T:p\in B_2\}\cap B_3\ne\varnothing.
\]

Both intersections are empty. A shorter word can always be split into a
prefix of length at most two and suffix of length at most three; repeated
states are retained at their shortest distance. Thus deduplication does not
discard an endpoint or length. The six-call witness supplies the upper bound.

A separate implementation enumerates all binary scalar matrices, filters
rank-one idempotents, and multiplies full `12x12` or `18x18` binary matrices
in the **faithful left regular representation** of the group algebra. It
generates the address group from actual binary `2x2` matrices, not the first
implementation's permutation table, and expands from the opposite side.
The complete state sets and exact distance layers agree, not just a few
columns or aggregate counts. The written argument in Sections 2-5 is what
extends the conclusion beyond those two finite register counts.

This proof is not Lean-checked, and no independent human proof review is
claimed. Physical compilation, common-label realization, hosting, precision,
tape and analytic transfer remain outside this scoped result.

## Attribution

Gareth Davidson (@bitplane), PR1333 at
`7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`, posed the restricted coordinate-CNOT
direction after proving the broader affine-rank-priced theorem. That theorem's
augmentation/free-scalar normalization is reused as an argument, with credit;
none of its implementation is imported. The contribution here is the
two-swap six-call obstruction in the restricted alphabet, including the
sign-trace and four-label coefficient argument and two independent finite
implementations. Eumemic (PR288), Ali Romman (PR468) and David Govea (PR720)
are credited for the surrounding register-model and rational-address work.
No new general rank principle or literature-priority claim is made.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

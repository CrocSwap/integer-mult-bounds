# Compress restored helpers by their paired scalar rank

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped written proof, not proof-kernel verification.

## 1. Exact statement

Use the scalar-idempotent model of #468 and #288. Address exponents belong
to a torsion-free abelian group; the coefficient field remains F_2. There
are k factors

\[
 D_j=I+a_jx_jy_j^T,\qquad a_j=[A_j]-1\ne0,\qquad
 x_j,y_j\in\mathbb F_2^{t+r},\quad y_j^Tx_j=1.
\]

The exact whole-matrix endpoint is

\[
 P=\prod_jD_j=\operatorname{diag}(d_1,\ldots,d_t,I_r),
 \qquad d_i-1\ne0.                                             \tag{1}
\]

In the multiplication model, d_i=[C_i] for nonzero C_i; invertibility of
the address targets is sufficient but unnecessary for this result. Every
helper returns to identity on arbitrary inputs. Correctness only on
zero-initialized ancillas is a different hypothesis.

Write X=(x_1 ... x_k)=[B;U] and Y=(y_1 ... y_k)=[C;V], where B,C
have t data rows and U,V have r helper rows. Put

\[
 u=\operatorname{rank}_{\mathbb F_2}U,\quad
 v=\operatorname{rank}_{\mathbb F_2}V,\quad
 w=\operatorname{rank}_{\mathbb F_2}(V^TU).
\]

**Theorem.** Another exact word has the same k frames in the same order,
the same data components B,C of every scalar projector, and endpoint
diag(d_1,...,d_t,I_w), with

\[
 u+v\le k-t,\qquad
 w\le\min(u,v)\le\left\lfloor\frac{k-t}{2}\right\rfloor.          \tag{2}
\]

It preserves every scalar pairing y_i^T x_j. Among realizations preserving
B,C and all these pairings, w is the least helper dimension. This is not
the least helper count among every possible word for the endpoint.
There is no restriction on address dimension, frame span, target flags,
or target commutativity. Original rank-one address frames stay unchanged.

## 2. Call surplus bounds the helper spans

The finitely generated exponent subgroup is free abelian, so its binary
group algebra is a Laurent polynomial domain. Work over its fraction
field K. The inherited ordered-product factorization is

\[
 P-I=XHY^T,                                                     \tag{3}
\]

where H is upper triangular with nonzero diagonal a_1,...,a_k. Its i,j
entry sums the increasing call paths from i to j. Each path coefficient
depends only on the a_l and scalar contractions y_p^T x_q. Thus H is
invertible over K. This is the rank factorization of #468 and the retained
arbitrary-register treatment in `research/bit-dirty-auxiliary-registers`.

By (1), P-I has rank t and its column and transposed row spaces equal the
data-coordinate subspace E. Therefore E lies in the column spaces of X
and Y. The inclusions hold over F_2 as well as K: adjoining the binary
basis of E does not increase rank, and binary matrix ranks do not change
under field extension. Projecting these spaces to helper coordinates gives

\[
 \operatorname{rank}X=t+u,\qquad\operatorname{rank}Y=t+v.
\]

Sylvester's rank inequality applied to XH and Y^T now gives
t>=t+u+t+v-k, proving u+v<=k-t. The remaining inequalities in (2)
are matrix-rank bounds. Nonidentity helper endpoints would raise rank(P-I)
and invalidate this particular surplus calculation.

## 3. The construction preserves the entire endpoint

Let W=im U and W_0=W intersect ker(V^T). Choose an r-by-w binary matrix S
whose columns form a complement of W_0 in W. Choose Q:F_2^r -> F_2^w
vanishing on W_0 with QS=I_w, first on W and then by extending a basis.
For each column of U, U-SQU belongs to W_0. Therefore

\[
 V^TSQU=V^TU.                                                   \tag{4}
\]

Set U_hat=QU, V_hat=S^TV, X_hat=[B;U_hat], Y_hat=[C;V_hat]. Then

\[
 Y_{\rm hat}^TX_{\rm hat}=C^TB+V^TSQU=Y^TX.                    \tag{5}
\]

In particular each new self-pairing is one, so all new scalar projectors
remain rank one and idempotent. All ordered path coefficients agree and
the same H gives P_hat-I=X_hat H Y_hat^T.

The original endpoint has BHV^T=0, UHC^T=0 and UHV^T=0. The new upper
cross block is BHV^TS, the lower cross block is QUHC^T, and the helper
block minus identity is QUHV^TS. They all vanish; the data block BHC^T
is unchanged. This proves exact identity on arbitrary new helper inputs,
not only equality of a data block. When w=0 the same calculation removes
all helpers. Nonzero U,V may have V^TU=0, so their separate dimensions
alone do not determine how many helpers survive.

## 4. Executable factorization, cost and precise optimality

Form the k-by-k binary matrix G=V^TU and select w independent columns,
with indices j_1,...,j_w. Take S to be those columns of U. For each j,
express G[:,j] uniquely in the selected column basis; use these coordinates
as column j of U_hat. Row l of V_hat is the transpose of G[:,j_l].
This is precisely the quotient construction above, without constructing
an arbitrary ambient extension of Q.

Direct binary inner products cost O(r k^2); elimination and all coordinate
solves cost O(k^3). Input and temporary storage use O(rk+k^2) bits. These
are finite preprocessing costs, not recursive-query savings. The generated
word executes k calls with unchanged frames and order. Its scalar vectors
are specified directly in the retained formal alphabet; no physical
register-basis change is granted for free. Separately charged scalar
mixings, routing, allocation, native operations and cleanup need their own
implementation bill.

Any h-helper realization preserving B,C and all pairings factors the same
G as V_new^T U_new, so h>=rank G=w. This proves the stated optimality.
The invariant bound (2) can be attained: t coordinate data calls and p
independent helper-only cancelling pairs give k=t+2p and w=p. Reassigning
or deleting those pairs can use a different number of helpers, but changes
the preservation contract; no universal need for p helpers is claimed.

## 5. The outstanding five-call block becomes a one-helper question

The merged `research/bit-span4-auxiliary-structure` (#4118) leaves a
five-call, three-data-target, two-dimensional address block with auxiliary
registers. Its arbitrary nonidentity-helper-endpoint question remains
broader than this theorem. For the **exactly restored** helper subcase,
k=5,t=3 give w<=1. Thus a counterexample with any number of restored
helpers exists if and only if one exists with at most one restored helper;
untouched extra coordinates give the converse.

The predecessor `research/three-register-no-target-flag` (#720) excludes
zero helpers. Citing that result, the remaining restored-helper case has
four scalar registers. Its alphabet has 120 binary rank-one idempotents,
versus 28 on three registers. The naive five-call domain has
120^5=24,883,200,000 ordered words. No such census is performed here, and
rational address realizability and relation-lattice obligations remain.
For eight calls and three nonidentity data targets, at most two restored
helpers suffice, independently of address span.

This reduces an unbounded register-count question to bounded dimension.
It supplies no five-call construction and no new paid-call lower bound.

## 6. Evidence and limits

The verifier checks every pair of two-by-three binary helper matrices
(4,096 cases), formal words with nested inverses, paired-rank sharpness,
and a zero-pairing case with both helper spans nonzero. Controls challenge
corrupted pairings, invalid projectors, missing restoration and incorrectly
counted identity targets. These finite checks corroborate the universal
proof; they do not infer it by extrapolation.

Credit Ali Romman's #468 and eumemic's #288 model/factorization, waynenilsen's
arbitrary-register domain/rank treatment, David Govea's #720 zero-helper
result, and unpaidmoon's #4118 open block question. Classical rank inequalities
and bilinear-space quotients are not claimed as new. The contribution is
this complete-endpoint compression and the explicit call-surplus bound.
SOURCES.json pins the exact canonical source notes and original task card.

**No new κ.** Zero-initialized-only ancillas, nonidentity helper endpoints,
approximate identities, other scalar alphabets, interposed free address
maps, physical/native tariffs and complete multiplication admission are
outside scope. All five selected assumptions remain; no human or formal
proof-kernel acceptance is claimed.

# Two clean helpers suffice, and are necessary, for the six-target case

Prepared for ToikY with substantial source-aware OpenAI Codex assistance.
Apache-2.0. The dirty-capacity theorem, normalization and Gram lineage of
Nick Petalas6800 and its credited predecessors retain attribution below.

## 1. Exact statement and changed promise

Let K be any field of characteristic two and R=K[Q]/(Q²−1), with Q a
formal central involution. Constant invertible matrices over K are free.
A paid gate is I+QN, where N is constant, N²=0 and rank(N)≤2.
There are six public coordinates, h helpers and at most four paid gates.
Require precisely

    W(x,0)=(Qx,0) for every x in R^6.

Helpers start at zero and return to zero; arbitrary old helper values need
not return. Under this promise the least possible h is exactly two.
The construction uses four rank-two paid gates, total paid rank eight.
We do NOT assert eight is the least total paid rank with clean helpers.

Nick Petalas6800 proves that restored arbitrary DIRTY helpers cannot lower
the corresponding total-rank floor nine. Its even-clean question is open
in the pinned source. The new result answers this fixed six-target case,
including its minimum helper count. It changes the entrance promise and
does not contradict or reprice the dirty theorem. All dimensions, ranks
and costs here belong to the stated abstract linear query model.

## 2. Four square-zero summands

Use four blocks K², for a total of eight scalar coordinates. Let J be the
4-by-4 block matrix every block of which is I₂, and put P=I₈+J.
Since four is zero in K, J²=0 and P²=I₈. The diagonal blocks of P vanish;
its off-diagonal blocks equal I₂.

For i=1,2,3,4, let U_i:K²→K⁸ embed into block i and let V_i:K⁸→K² be
block row i of P. Set R_i=U_i V_i. Then V_i U_i=0, so R_i²=0.
V_i is surjective (any one of its other three blocks is I₂), and U_i is
injective, so rank(R_i)=2 over every K. Summing block rows gives

    R_1+R_2+R_3+R_4=P.

This is a block all-ones/rank-factorization construction, using classical
linear algebra and the credited simplex/Gram viewpoint, not a new query
alphabet or an uncharged physical gate implementation.

## 3. Literal query word and its complete operator

Set ε=1+Q. Then ε²=0 in R. Since R_i²=0,

    (I+R_i)(I+Q R_i)=I+ε R_i.

Each such factor uses one allowed constant free gate and one paid gate.
The free gate is invertible with inverse itself. The paid gate is likewise
its own inverse. Products of two ε terms vanish, hence in any order

    product_i (I+R_i)(I+Q R_i)=I+εP.

For public blocks x₁,x₂,x₃ in K² and a helper block h in K², define the
constant free basis

    C(x₁,x₂,x₃,h)=(x₁,x₂,x₃,x₁+x₂+x₃+h).

C²=I. The block sum of C(x,h) is h, so J C(x,h)=(h,h,h,h).
It follows directly, on ALL inputs, that

    C⁻¹ P C(x₁,x₂,x₃,h)=(x₁+h,x₂+h,x₃+h,h).

Let L be the 6-by-2 matrix obtained by stacking three copies of I₂.
The literal word applies C, the four free/paid pairs, then C⁻¹. Its full
R-linear matrix is

    W=C⁻¹(I+εP)C = [ Q I₆   εL  ]
                         [   0    Q I₂ ].

Thus W(x,0)=(Qx,0), as required, for every formal-ring x. All six public
columns and both unspecified helper columns have been stated, not just
tested on a chosen set of numerical inputs. W²=I because ε²=0 and the
characteristic is two, so the inverse restriction is identical. The
reversed literal word also supplies the inverse using allowed gates.

There are exactly four paid gates of rank two and six free basis gates:
four I+R_i factors plus C and C⁻¹. No physical tariff is assigned to those
free bases or to preparation/ownership of the zero helpers.

## 4. Why arbitrary dirty restoration fails

For x=0 and h=(1,0), the output helper is (Q,0), rather than (1,0), and
each public block acquires (ε,0). Both differences are nonzero in the
formal ring. In particular the complete matrix is not diag(QI₆,I₂).
Numerically substituting Q=1 would erase exactly this distinction and is
not a test of the formal endpoint. The derivative coefficient
C⁻¹PC=[I₆,L;0,I₂] is an involution, but is not a projection: its square
is I₈ and L≠0. Applying the source's projection bound to it would discard
the clean/dirty boundary.

## 5. No word with zero or one helper can satisfy the clean promise

Consider ANY permitted word with h≤1, including arbitrary constant free
gates and at most four square-zero paid terms of rank at most two.
The following normalization is the one credited in source6800; here its
constant endpoint need only fix the public subspace pointwise.

Evaluate ε=0 (equivalently Q=1) and call the constant word A. A is
invertible, and the clean promise implies A(x,0)=(x,0). Its free inverse
also fixes that subspace. Therefore replacing W by A⁻¹W preserves the
clean promise and uses no additional paid gate.

Move all constant factors to one side, using
I+QN=(I+N)(I+εN). Conjugation by constants preserves rank and square-zero.
The normalized full matrix is I+εD, where

    D=sum_i T_i,   T_i²=0,   rank(T_i)≤2,

with at most four terms. Every square-zero matrix has trace zero, hence
trace(D)=0. The clean public-column identity gives D(x,0)=(x,0).

If h=0, D=I₆ and the full endpoint is QI₆. If h=1, for some column b
and scalar d in K the FULL coefficient is

    D=[I₆  b]
      [ 0  d].

Since six is zero in K, trace(D)=d=0. Consequently D²=D and rank(D)=6.
The constant public-fixing shear S=[I₆,b;0,1], with S²=I, conjugates D
to diag(I₆,0). After this allowed free conjugation the normalized word
has full arbitrary-input endpoint diag(QI₆,1): it is a restored DIRTY
word with the same at-most-four paid gates and the same rank cap.

Source6800's credited dirty-capacity necessity applies. For k=4 its
m_k=2 and six public coordinates require

    total paid rank ≥ 6+ceil(6/2)=9.

The candidate word has total paid rank at most 4·2=8, a contradiction.
The same source theorem excludes h=0. Zero-rank padding covers words
using fewer than four gates. This proves h≥2; Section3 attains h=2.

The new lower-bound step is the one-helper trace/projection reduction.
The dirty floor and its projection-complement proof are source6800's
work, cited rather than a new census or an independent re-certification.
The displayed reduction checks its exact hypotheses; it does not assume
that an arbitrary clean endpoint with two or more helpers is a projection.

## 6. Evidence and limits

This is an all-field written proof, not a proof-kernel certificate.
The new verifier is finite corroboration of the explicit word, complete
formal endpoint, inverse and premise-removal controls. Its exact executed
domains/counts are reported by generated receipts and the README after
observation. It imports and executes no predecessor scientific program.
Finite checks alone do not prove all-field feasibility or the universal
minimum-helper claim; the argument above supplies those implications.

Initialized helper preparation, ownership, basis implementation, native
alignment, actual caller chronology, retention/restoration costs and the
complete signed supplier invoice remain separate obligations. This is no
physical saving, supplier admission, κ improvement or selected-frontier
change. All five selected assumptions remain. No general clean-capacity
classification, total-paid-rank optimum, human acceptance or formal-kernel
verification is asserted. The original native-conversion task gate is
unmet; the catalogue scope is explicitly changed and its outcome partial.

## 7. Predecessor credit

Nick Petalas6800 supplies the dirty theorem, projection-complement
normalization, clean-versus-dirty distinction and explicit even-clean
question. Josie Elliston6138 supplies its earlier workspace-free theorem
and workspace question; Nick6122, Cinna Davis's simplex/controller line,
Ali Romman5617's coupled Gram/block simplex and Matarener6114 retain credit.
Rank factorization, dual-number linearization, block all-ones matrices,
trace and constant shear conjugation are classical. Exact retained source
texts and their immutable foreign commit/blob/SHA pins accompany this note.
Substantial OpenAI Codex proposal, implementation, source-aware challenge,
overlap and metadata roles share source context; they are not blind or
independent human/proof-kernel acceptance.

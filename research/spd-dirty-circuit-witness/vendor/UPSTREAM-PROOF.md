# Compact universal certificates for dirty linear circuits

## Result and provenance

Let K be a field, let r registers contain arbitrary independent vectors in one
K-vector space V, and let X_a be finitely many **independent unary operator
symbols**. A program uses scalar ADD, SCALE, SWAP, unary APPLY, and queries
`v_d += c X_a v_s`. Source and destination may coincide. Coefficients are
central elements of K. Retain every input and every returned register,
including borrowed dirty registers. There are no implicit zero inputs.

**Bridge theorem.** A program with q unary occurrences has a coefficient
representation with exactly r+q states, independent of its expanded word count.
For two programs, put D=2r+q_left+q_right. Their complete endpoints are equal
under every K-linear operator substitution, in every dimension, if and only if
their difference has a certificate consisting of at most D reachable rows,
initial-span coordinates, closure coordinates, and zero final projections.
Such a certificate can be found with polynomially many exact field operations.
If the endpoints differ, the search finds a shortest nonzero coefficient word
w. Matrices of dimension |w|+1 with entries zero or one realize that coefficient
as an actual endpoint discrepancy, including the offending dirty input/output.

The same procedure applied after substituting X_a=I+Y_a supplies a discrepancy
using **simultaneously upper triangular unipotent**, hence invertible, operators.
In either version |w| is at most the maximum unary dependency depth of the two
programs, and at most D-1. For a program compared with an explicit polynomial
target, replace q_right by the sum of its displayed term lengths.

This is a project-specific compilation and certificate bridge to **classical**
weighted-automata equivalence and noncommutative polynomial identity testing.
No new general PIT algorithm, free-algebra separation theorem, or tensor
independence theorem is claimed. Primary references are Stefan Kiefer,
[Notes on Equivalence and Minimization of Weighted Automata, §§1–2 (2020)](https://arxiv.org/abs/2009.01217),
and Ran Raz and Amir Shpilka,
[Deterministic Polynomial Identity Testing in Non Commutative Models (2005)](https://www.cs.tau.ac.il/~shpilka/publications/RazShpilka_PIT.pdf).
The new artifact specializes these methods to the project's complete dirty
register contract, gives a compact compiler and separately transcribed checker,
and binds them to a real scheduler and constructive failure diagnostics.

The existing [free-word tensor-lift audit](../free-word-tensor-lift-audit/README.md)
already proves a particular provider's lift with explicit reduced free-group
words. The [universal dirty-phase identities](../universal-dirty-phase-identities/README.md)
already replace numerical tests for their typed local identities. Neither result
is claimed here. This method avoids word expansion for its own independent-symbol,
equal-space linear grammar; it does **not** replace their relation-aware or
rectangular-block arguments.

## 1. Register compilation without word expansion

Create r leaf atoms x_0,...,x_(r-1). Maintain each register as a scalar linear
combination of atoms. Scalar instructions update these combinations directly.
For each unary occurrence on expression e, create one fresh atom z_j=X_a e
and record its label a and its scalar dependency row e. APPLY replaces its
register expression by z_j. A query adds c z_j to its destination expression.
Take e from the pre-instruction source, also for self queries. Thus the number
of atoms is exactly r+q. Their dependencies always point to earlier atoms.
No symbolic polynomial, fresh clean vector, or physical helper is created by
this representation: atoms are compiler records only.

Write U for the final r register rows. For each symbol a, form the state matrix
T_a: row j is atom j's dependency row if its label is a, and zero otherwise.
Let V map each original leaf to its corresponding input coordinate and all
unary atoms to zero. Induction on the acyclic dependencies gives

    coefficient of word a1 ... ak in endpoint (o,i)
        = (U T_a1 ... T_ak V)_(o,i).

Words use ordinary matrix-product order: [B,A] denotes BA, which applies A
first. Empty words supply scalar multiples of the identity on payloads.
Subtract two programs by a direct sum of their state spaces, concatenate
their initial rows with a minus sign on the second, and stack their final maps.
Inputs remain shared *semantically* through V; the compiler's two copies of
the leaf indices do not introduce independent copies of the actual data.

The compiler supports rational coefficients, Gaussian rationals Q(i), and prime fields.
The executable's finite fields are F_p for primes p<=2^31-1; a displayed
fraction is admitted only if its denominator is invertible. The written
argument applies over any field. There is no numerical tolerance.

## 2. The certificate and its small checker

Let B have b<=D rows in the difference representation. A positive certificate
gives paths identifying these reachable rows and scalar coordinates H,C_a such
that

    U = H B,       B T_a = C_a B for every symbol a,       B V = 0.

These **finite equalities** are the whole acceptance condition. They imply
U T_w lies in the row span of B for every word w, by induction on word length.
Hence U T_w V=0 for all words. Free words are a basis of K< X_a >, so the
complete matrix polynomial is zero. Evaluation in End_K(V) preserves sums,
ordered products and scalar coefficients, proving universal substitution.
No independence or minimality of B is needed for soundness.

Conversely, if the polynomial is zero, the reachable row space
span{U_o T_w} is finite-dimensional, stable under every T_a, and annihilated by
V. Choose a reachable basis. Its initial and closure coordinates give exactly
the displayed certificate. This proves completeness for the declared grammar.

`linear_words.py` computes that basis by incremental exact elimination.
`check_certificate.py` imports no producer code and does no elimination or
search: it separately reconstructs the dependency representation, rebuilds
the path rows, and checks all three equations. Both share `fields.py`, which
is explicitly part of the trusted arithmetic surface. Neither is a proof
assistant kernel. Source transcription, Python and the arithmetic/compiler
implementations remain trusted; bounded differential tests address faults.

There are at most D accepted basis rows and |alphabet|D successor tests.
A dense implementation needs O(|alphabet|D^3 + L D) field operations for a
length-L pair of programs, plus parsing the target. Coordinate storage has at
most O(|alphabet|D^2+rD) field elements. These are arithmetic bounds; exact
scalar sizes and dense/sparse constants affect runtime. The reference checker
may recompute path rows and is polynomial, rather than performance optimized.

## 3. Shortest distinguishing words and literal counterexamples

Initialize a FIFO queue with independent rows of U. For each queued row U_o T_w,
test its output projection, and enqueue independent successor rows U_o T_w T_a.
All path rows of length at most k are spanned by accepted path rows of length
at most k. This follows by induction, including every rejected dependent row:
its expression uses earlier rows with no greater length, whose successors
span its successors. FIFO order therefore finds a word of least length among
all nonzero coefficients. Dimension increases at most D times. In the acyclic
representation, a word longer than either program's unary dependency depth is
already zero. The checker validates nonzeroness, **not a minimality certificate**;
shortestness is a property of the proved search algorithm.

Suppose coefficient c != 0 occurs in output o, input i, word w=a1...ak.
On a space with basis e_0,...,e_k set

    N_a = sum_{j: a_(j+1)=a} E_(j,j+1).

Every factor advances exactly one coordinate. Thus a word u has matrix entry
(0,k) equal to one exactly when u=w, and zero otherwise. Longer words vanish;
shorter words cannot reach coordinate k. Consequently the actual endpoint
discrepancy on input role i with payload e_k has output-role-o coordinate e_0
equal to c. All other roles can be zero in this concrete witness; they were
independent during the universal check. If k=0, use one-dimensional zero
operators and the empty-word coefficient. Matrices for symbols absent from
w are zero too. This proves finite-dimensional separation constructively.

For invertible generators run the algorithm on Q(Y)=P(I+Y). Substitution
X->I+Y is a free-algebra automorphism, with inverse Y->X-I, over every field.
It preserves nonzeroness and does not increase degree. Apply the preceding
construction to Q, and evaluate the original circuit at X_a=I+N_a. These
matrices are unipotent with finite inverse I-N_a+N_a^2-...; they share one
triangular flag. This proves the invertible version without assuming that a
separately named inverse symbol denotes this inverse.

The degree+1 bound is sharp for this **unipotent witness class**: P(X)=(I-X)^d
vanishes on every unipotent operator of dimension at most d, whereas the
(d+1)-dimensional Jordan witness is nonzero. This is not a claim that d+1 is
the least dimension of an arbitrary invertible counterexample.

## 4. Tensor substitution and dirty boundaries

If a positive certificate is accepted, substitute X_a=G_a^(tensor f) for any
chosen endomorphisms G_a and any positive integer f. Polynomial evaluation
gives the endpoint identity on the enlarged payload space. Scalar c remains
c times its identity. For example X-I becomes G^(tensor f)-I; it does not
become (G-I)^(tensor f), and cX does not become (cG)^(tensor f).
The *evaluated unary word* tensors multiplicatively; the whole linear sum
must still be evaluated term by term. The certificate never tensorizes a sum.

Complete role coverage means a borrowed field must return its arbitrary
input functional. A target with `identity:true` supplies that requirement
automatically for every unspecified block. Losing dirt is a nonzero endpoint
residual even when the intended visible target increment is correct.
External source/target aliasing changes the independent-role contract and
requires a new problem transcription. Reusing a role inside the word is legal.

A negative result disproves universality for **independent** operators. It
does not disprove an identity under commutation, inverse, involution,
Clifford, fixed-dimension, reachable-state or nonlinear leaf constraints.
Such constraints are not silently added. Physical native implementation,
precision, rounded restoration, hosting, stock, compiler uniformity and the
complete paid/outer invoice all remain separate obligations.

## 5. Bound application

The adapter imports the exact pinned `echo.py` from the credited multiway dirty
echo package and translates its emitted `(src,dst,factor,sign)` instructions
literally into queries. Its reference is identity on all roles plus
`target += sign A_(n-1)...A_0 source`. Source and every borrowed input are
retained. Each accepted finite schedule now has an inspectable universal
coefficient certificate, extending beyond its earlier fixed matrix controls.
The echo theorem and scheduler are predecessor work, not newly discovered.
The tested schedule range is in README.md; no finite range substitutes for
that predecessor's arbitrary-n written induction or rounded-leaf argument.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.

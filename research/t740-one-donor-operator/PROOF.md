# Five residual phases in the pinned owner-zero word

This is a statement about the exact eight-stream data operator specified by the
retained T740 replay inputs. Fix owner replica 0, port 0, its complete chronology,
all hosted slices, and all translation phases. Change only the residual phase
operators of children 8, 10, 12, 13 and 14. The first four have no hosted axes;
child 14 has 31 hosted axes and one residual axis. Their residual ranks are
respectively 48, 48, 48, 48 and 1.

For a character \(x\in\mathbb F_2^{73}\), let \(z_c(x)\) be the multiplier
by which the residual phase of child \(c\) changes. These five multipliers may
first be treated as independent indeterminates. In particular, the operator
calculation below does not require a proposed axis list or a rank bound.

## Exact ambient-character calculation

Write a binary parity as an integer in \(\{0,1\}\). For every binary vector
\(v\), its lift modulo four satisfies

\[
\langle v,x\rangle_{\mathbb F_2}
\equiv \sum_i v_i x_i-2\sum_{i<j}v_iv_jx_ix_j\pmod4.
\]

This follows by expanding \(1-\prod_{i:v_i=1}(1-2x_i)\) and dividing by
two: terms of degree at least three vanish modulo four. Consequently every
source phase has an exact representation

\[
q(x)=\sum_i a_i x_i+2\sum_{i<j}b_{ij}x_ix_j\pmod4,
\qquad a_i\in\mathbb Z/4,\quad b_{ij}\in\mathbb F_2.
\]

This representation includes the physical parity of the recipe's vector
\(q\); it does not regard that parity as an independent Boolean variable.
The Hamming-weight prefix phases are linear polynomials in the same 73
coordinates.

Each matrix entry is propagated as a finite integer linear combination of
terms \(z^m i^{q(x)}\). A phase gate adds its quadratic exponent and, at one
of the five selected sites, its formal variable. A shear adds an integer
multiple of one row to another. The terminal swap exchanges rows and negates
the required row. Equal exponent/monomial keys can be merged exactly. No
sampling, floating arithmetic, or inference from coordinate characters enters
these operations. Distinct phase polynomials need not be linearly independent
as complex-valued functions; that fact is unnecessary here, because the
calculation eliminates every nonzero ambient exponent explicitly.

Both implementations start from the authenticated raw fill, journal, order,
dispatch, provider widths, plan, template and port recipes. The primary checker
also reconstructs the predecessor's complete fill digest. The independent
checker projects the 30 owner-zero/port-zero rows directly, validates all
journal preimages, reconstructs the hosted prefixes, and implements the event
semantics without importing either checker or any predecessor executable.
Its quadratic representation uses two bit planes for linear coefficients and
one bit plane for the even cross coefficients.

After division by the common phase \(i^{|x|}\), the computed matrix is the
following polynomial, with all omitted entries zero:

\[
A(z)=
\begin{pmatrix}
z_{13}&0&z_{13}-1&0&0&0&0&0\\
0&z_{12}&0&0&0&0&0&0\\
0&0&1&0&0&0&0&0\\
0&z_{12}-z_{14}&0&z_{14}&0&0&0&0\\
0&0&0&0&1&0&0&0\\
0&1-z_{14}&0&z_{14}-1&0&1&0&0\\
0&0&0&0&0&0&z_8&0\\
0&0&0&0&0&0&0&z_{10}
\end{pmatrix}.
\]

Thus the source-bound identity is
\(M_x(z)=i^{|x|}A(z)\) for every one of the \(2^{73}\) characters and all
complex values of the five formal variables. The replay has 21 symbolic terms
at its largest intermediate point and 16 at the end. Every surviving exponent
after normalization is the zero polynomial. These finite symbolic facts
certify the displayed identity; the checker is not a formal proof kernel.

Setting all five variables to one proves the baseline operator identity in
this model for all characters. Conversely, the diagonal entries at positions
6, 7, 1, 0 and 3 respectively force

\[
A(z)=I_8\quad\Longleftrightarrow\quad
z_8=z_{10}=z_{12}=z_{13}=z_{14}=1.
\]

The reverse implication also follows immediately from the displayed matrix.
The recorded enumeration of all \(4^5=1024\) fourth-root assignments accepts
only the all-one tuple. That enumeration is an additional finite check; the
symbolic identity and its forcing diagonals establish the universal statement.

For actual phase functions, apply this equivalence separately at every
character. The complete operator is preserved exactly if and only if each of
the five residual phase functions is preserved separately. Equality on the 73
coordinate characters alone would not suffice: the parity of \(x_0+x_1\)
and the integer sum \(x_0+x_1\) agree there, but their lifted phases differ
at \(x_0=x_1=1\).

## Consequence for independent residual bases

Suppose the residual axes of a child are a linearly independent binary family
\(v_1,\ldots,v_r\). This includes the source orthonormal bases and any
replacement whose full hosted-plus-residual basis satisfies the same
orthonormality requirement. Define

\[
f(x)=i^{\sum_{j=1}^r\langle v_j,x\rangle_{\mathbb F_2}}.
\]

For uniformly distributed \(x\), the \(r\) independent parity bits are
uniform on \(\mathbb F_2^r\). Hence

\[
\mathbb E_x f(x)=\left(\frac{1+i}{2}\right)^r,
\qquad |\mathbb E_x f(x)|^2=2^{-r}.
\]

Two such phase functions that agree at every character therefore have the same
rank. The fixed translation phases cancel from their ratio; no assumption of
positivity of Fourier coefficients is needed. Applying this observation to
the five forced phase equalities shows that every operator-preserving
replacement in this scope retains each residual rank separately. For legal
combined independent hosted-plus-residual bases, the full child rank is the
sum of those two ranks. The hosted ranks are fixed by hypothesis, so those
full child ranks also remain unchanged. In particular, this five-site
residual-only move domain offers no rank-profile improvement under that
combined-basis requirement.

Independence is essential. Four repeated copies of one axis have identically
trivial total phase, so arbitrary dependent lists cannot have their lengths
recovered this way. Conversely, the result does not force literal basis
equality: in six coordinates, the six standard vectors and the six vectors
each missing exactly one coordinate are different orthonormal bases with the
same lifted phase function and the same rank.

## Scope and attribution

The retained `idle-star-paired-axis-census` implementation and its source stack
provide the physical event semantics, source geometry and chronology. This
package derives the five-variable matrix and rank consequence from those
fixed inputs. PR #3263's source-bound rejection and explicit next question
motivate adding one partially hosted donor to the four idle sites; the
four-idle-site investigations in PRs #3199 and #3204 are predecessor work,
not a claim of novelty here.

The statement is limited to the named owner, port, sites and unchanged hosted
prefixes, translations and schedule. It does not classify changes involving
both partially hosted donors, altered hosting, other ports or owners, or
changes to the data word. It certifies the retained eight-stream operator
model, not a complete native supplier, physical layout, controller, recursive
consumer, or multiplication theorem. It does not validate a global T740
headline or change the selected frontier.

## Open next questions

- Add another explicitly named residual site or a change to a hosted slice,
  then derive its complete character-dependent operator before searching for
  rank improvements. The present five-variable identity does not answer that
  changed problem.
- If a larger move domain admits an operator-preserving rank change, bind its
  full allocation, paid operations, source chronology, native admission and
  recursive obligations before treating a numerical root as an admitted
  multiplication result.

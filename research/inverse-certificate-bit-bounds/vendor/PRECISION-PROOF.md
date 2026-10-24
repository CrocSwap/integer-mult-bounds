# Exact separation and a funded dyadic endpoint detector

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a written proof with finite exact corroboration.

## Contract and result

Use the rational complete register grammar from
[PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262): r
independent input roles, every role returned, old-value scalar assignments,
apply calls G_a^(+/-1), and queries dst += c G_a^(+/-1) src, including aliases.
Only inverses of named generators occur. Let q count all apply/query calls
in both programs, and let m count all instructions in both programs.

Take any labelled skew path word of length d-1 and a reduced rational
parameter t=A/B with 0<t<=1/4 and B>0. Use the exact special-orthogonal Cayley
matrices O_a(t) of [PR #5315](https://github.com/CrocSwap/integer-mult-bounds/pull/5315).
Give one chosen input role e_(d-1), and give all other roles zero. Let f be
coordinate zero of any chosen output difference. This concrete input does
not change the universal grammar's independent-role contract.

Let C be the product of the positive reduced denominators of **every** scalar
coefficient occurrence in both programs. Include query coefficients and every
term of a linear assignment, even repeated roles or zero coefficients. Then

    f != 0  implies  |f| >= eta = 1/[C (3B)^(dq)].                 (1)

A dyadic implementation below computes fhat with |fhat-f|<=eta/4. Hence

    f=0   iff |fhat|<=eta/4,
    f!=0  implies |fhat|>=3eta/4.

The threshold eta/2 therefore decides this selected endpoint exactly. It
does not need an exact endpoint replay or coefficient certificate as its
decision oracle. A false universal program identity still needs the source
producer's distinguishing word/input/output, or another search for one.
A zero at one chosen tuple is not a universal equality certificate.

## 1. Integer denominators

For each path label a, write K_a for its skew adjacency matrix and

    M_a = 2B I - A K_a,    P_a = 2B I + A K_a,
    O_a = M_a^-1 P_a.

M_a and P_a have integer entries. Each column has squared Euclidean norm at
most 4B^2+2A^2 <9B^2. Hadamard's determinant bound gives

    1 <= D_a = det(M_a) <= (3B)^d.

The determinant is positive: M_a is invertible on the real parameter line,
its determinant is continuous, and at A=0 it is (2B)^d>0. Also P_a=M_a^T,
so its determinant is the same D_a. The adjugate formula shows that every
entry of O_a and O_a^-1 is an integer divided by D_a. Cancellation can only
reduce a reduced denominator.

Maintain one common integer denominator for all registers on one program
side. At a linear assignment multiply it by the product of the denominators
of that assignment's coefficients. At an apply multiply it by D_a. At a
query multiply it by D_a times the scalar denominator. The unchanged
registers and old destination can use this same denominator. Old source
values also have it before the assignment, including on alias. This proves
by induction that a common denominator for the two endpoint vectors divides

    C product_(all q occurrences) D_(label).

The endpoint difference has the same divisibility property after the two
side denominators are multiplied. A nonzero numerator is a nonzero integer.
The displayed product is at most C(3B)^(dq), which proves (1). The actual
common denominator need not divide the larger numeric bound C(3B)^(dq);
only this inequality is used.

For the source witness grid with cap t0=a/b and L=dq, its rational points
have reduced denominator B<=b(L+1). Thus a uniform separation bound over the
whole grid follows by replacing B in (1) with b(dq+1). No floating root
separation or generic numerical noncancellation premise is needed.

## 2. Complete register gains

Use the maximum absolute coordinate over the entire r-register bank. Every
entry of an orthogonal matrix has absolute value at most one, so its row
absolute sum is at most d. Assign each instruction the following two bounds:

| Instruction | beta | gamma |
|---|---:|---:|
| linear dst = sum c_j src_j | max(1, sum abs(c_j)) | 0 |
| apply G_a or G_a^-1 | d | d |
| query dst += c G_a^(+/-1) src | 1+d abs(c) | d abs(c) |

Beta bounds the exact map on the whole bank; beta>=1 also covers unchanged
roles. Gamma bounds the effect of rounding each operator entry by at most h.
Define G as the product of all beta values in both programs, and Gamma as
the largest gamma (zero for no calls). G>=1.

Truncate each exact forward matrix entry toward zero to the h=2^-p grid.
Use the transpose of that integer table for its inverse call. Since exact
inverse equals transpose, this is the same entrywise truncation of the
actual inverse. Each stored entry still has absolute value at most one.
Read all instruction sources before writing the destination. Multiply and
sum exactly, keep scalar coefficients exact, then truncate each new data
coordinate once toward zero to the same grid.

This operation does not increase the absolute value of a coordinate. By
induction each computed bank has norm at most the product of its previous
beta values, hence at most G. This bound includes arbitrary scalar gains,
all helper roles, and self-source queries. It does not assume that a rounded
map is linear or that its stored inverse undoes its stored forward map.

Let E_i be the bank error on one program side after instruction i. The exact
map contributes at most beta_i E_(i-1). Entry quantization on the computed
input contributes at most gamma_i h G. The final data truncation adds at
most h. Thus

    E_i <= beta_i E_(i-1) + (gamma_i G+1)h.

Every suffix product of beta values is at most G. Sum both program errors,
using their combined instruction count m. Every returned coordinate of the
endpoint difference therefore has error at most

    E = m G (Gamma G+1) h.                                    (2)

Choose an integer p>=0 with

    2^p >= 4 max(1, m G (Gamma G+1)) C(3B)^(dq).

Then E<=eta/4. This also covers an empty program pair, where m=0 and its
endpoint difference is exactly zero. Equations (1) and (2) prove the
threshold decision and the claimed separation between its two cases.

## 3. Executable and arithmetic boundary

`detector.py` uses no exact endpoint or Magnus producer. It takes the program,
word, parameter, input role and output role. It forms each rational Cayley
matrix from the retained tridiagonal basis action, quantizes the entries,
and replays both complete programs with integers. A query computes its old
sum before one final division. A linear assignment uses exact rational
scalar arithmetic before one truncation. Every dirty output is retained.

For alphabet size s the code stores 2sd^2 matrix-entry slots. The dense
replay pays qd^2 integer matrix products and md coordinate truncations,
plus all linear/query scalar products and additions. Matrix formation,
source parsing, gain/denominator calculation, allocation and returned banks
are additional work. There is no claim that this dense numerical method is
faster than exact rational replay or an admitted native primitive.

After the word is supplied, the required fractional precision satisfies

    p = O(log C + dq(1+log B) + log(m+1)
          + log G + log(Gamma G+1)).

This is polynomial in the explicit program/word lengths and scalar/parameter
binary input sizes. Exact scalar sums and products give polynomial-size
representations of C, G and Gamma. Integer path matrices have entry size
O(log B); their minors have O(d(1+log B+log d)) bits. The tridiagonal basis
solves use ratios of these minors and polynomially many exact operations.
The stored data have magnitude at most G, so their integers use at most
p+O(log G) bits. Dot products add at most O(log d) bits; exact scalar sums
use coefficient denominators whose product divides C. This bounds the
arithmetic bit sizes in the supplied detector polynomially as well.
This statement is for this detector after a word is given. It is not a new
bit-complexity analysis of the upstream coefficient producer.

## Evidence and limits

The verifier uses the exact tridiagonal endpoint and a separately transcribed
dense Gaussian-inverse interpreter only as test oracles. It compares every
returned coordinate with (2), not just the threshold verdict. Equal programs,
exact cancelling grid points and failed identities are separate cases. Tiny
parameters, a scalar discrepancy 2^-80, scalar gains 2^100, dirty returns,
aliased queries and a delayed inverse series test different terms in the
bound. Corrupted code tests remove scalar denominators, parameter denominator
size, cumulative gains or the inverse transpose.

The guard is deliberately conservative. It is not a least precision, an
IEEE floating-point guarantee, or a proof that an unspecified numerical
library respects these rounding rules. It adds no finite native alphabet,
Clifford relation, physical tape tariff, supplier admission or complete kappa
improvement. The selected frontier and inherited native/analytic obligations
remain unchanged. No independent human or proof-kernel review is claimed.

## Attribution

Ali Romman's [PR #5315](https://github.com/CrocSwap/integer-mult-bounds/pull/5315),
consumed at `9bebc267c4608e51fcc94a543b8e0d66077cdfbb`, supplies the rational
orthogonal realization, literal action and tests retained in `vendor/`.
Krzysztof Wójt (@krzysztofwojt) supplies the inverse compiler and shortest-word
proof in [PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262).
The retained notices credit zxv's
[PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235), the
dirty-echo/tensor/phase lineage and classical rational-series methods.
Cayley transforms, Hadamard's determinant inequality and forward-error
propagation are classical. This result binds their explicit constants to
this complete register grammar and one literal dyadic consumer.

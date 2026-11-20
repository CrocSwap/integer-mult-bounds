# Exact width for a pre-carry convolution digit

Let \(a=(a_0,\ldots,a_{m-1})\) and \(b=(b_0,\ldots,b_{n-1})\) be arbitrary
Boolean inputs, and let

\[
c_k=\sum_{i+h=k}a_i b_h\quad\text{in }\mathbb Z
\]

be their convolution coefficient before carry propagation. Indices in a sum
are always in the respective input ranges. For a fixed integer \(j\geq 0\),
write \(r=2^j\) and \(s=\min(m,n)\). The requested digit is
\(F_k(a,b)=\lfloor c_k/r\rfloor\bmod 2\) at every \(0\leq k\leq m+n-2\)
when both inputs are nonempty.

## Model and result

A channel \(\ell\) has fixed positive integer lengths \(p_\ell,q_\ell\).
It takes an arbitrary Boolean encoding \(U_\ell(a)\in\mathbb F_2^{p_\ell}\)
and a separately defined arbitrary Boolean encoding
\(V_\ell(b)\in\mathbb F_2^{q_\ell}\). It returns all coefficients of the
ordinary univariate polynomial product \(U_\ell(a;z)V_\ell(b;z)\) over
\(\mathbb F_2[z]\). Encodings, channel lengths, and the finite list of
channels are fixed before the input is given. The decoder is a joint linear
map of all product coefficients. We also allow a joint affine map. The empty
list is admissible. Length means the number of prescribed positions, including
any padding. The channel can have either side shorter, and this choice can
vary between channels.

**The minimum total shorter-operand width is**

\[
\min\sum_\ell \min(p_\ell,q_\ell)=\binom{s}{r},
\qquad \binom{s}{r}=0\ \text{if }r>s .
\]

The same list attains the optimum for the entire digit sequence. It also
minimizes the total number of coordinates on each side individually.

## Digit identity

In the polynomial ring \(\mathbb F_2[z]\),
\((1+z)^{2^d}=1+z^{2^d}\) by repeated squaring. If \(c=\sum_d c_d2^d\)
is a nonnegative integer in binary, then

\[
(1+z)^c=\prod_{d:c_d=1}(1+z^{2^d}).
\]

The only possible selection of distinct powers of two summing to \(2^j\) is
the selection of the single power \(2^j\). Accordingly
\([z^r](1+z)^c=\binom{c}{r}\bmod 2=c_j\). For
\(I_k=\{i:0\leq i<m,\ 0\leq k-i<n\}\) and \(t_k=|I_k|\), this gives

\[
F_k(a,b)=\sum_{\substack{S\subseteq I_k\\|S|=r}}
\left(\prod_{i\in S}a_i\right)
\left(\prod_{i\in S} b_{k-i}\right)\quad\text{in }\mathbb F_2 .
\tag{1}
\]

Each term counted by the sum is a choice of \(r\) distinct occupied pairs
on the antidiagonal. For \(t_k<r\) the sum is empty and the digit is zero
for every input.

## Lower bound

Fix an output position \(k\). For each channel write
\(\lambda_{\ell,k,d}\) for the weight of product coefficient \(d\) in the
decoder of that output. Its contribution is

\[
U_\ell(a)^{\mathsf T} H_{\ell,k} V_\ell(b),\qquad
(H_{\ell,k})_{i,h}=\lambda_{\ell,k,i+h}.
\]

This rectangular matrix has rank at most \(\min(p_\ell,q_\ell)\). Evaluating
the contribution on any finite lists of \(a\) and \(b\) gives a matrix of
the form \(X H_{\ell,k}Y^{\mathsf T}\), where rows of \(X,Y\) contain the
encoder evaluations. Its rank is bounded by the same number even when the
encoders use arbitrary nonlinear Boolean functions.

For an affine decoder, let the zero anchor be the zero input on each side.
Apply the double difference

\[
\Delta G(a,b)=G(a,b)+G(a,0)+G(0,b)+G(0,0).
\]

Every target \(F_k\) vanishes when either input is zero, so
\(\Delta F_k=F_k\). The affine constant cancels. Each channel's contribution
becomes

\[
\big(U_\ell(a)+U_\ell(0)\big)^{\mathsf T}
H_{\ell,k}
\big(V_\ell(b)+V_\ell(0)\big).
\]

The same rank limit applies to these centered encoders, including when the
original encoders are nonzero at zero. The difference also cancels any
additive function of one input alone. Rank subadditivity now bounds every
target output matrix by \(\sum_\ell\min(p_\ell,q_\ell)\).

Take rows indexed by the \(r\)-element subsets \(S\) of \(I_k\), with \(a\)
supported exactly on \(S\). Take columns indexed by the \(r\)-element subsets
\(T\) of \(I_k\), with \(b\) supported exactly on \(\{k-i:i\in T\}\).
Then \(c_k=|S\cap T|\). Since \(c_k\leq r\), its \(j\)-th digit is one
exactly when \(S=T\). This is an identity submatrix of size \(\binom{t_k}{r}\).
Equation (1) also gives that many rank-one terms, so the full truth table
has rank exactly \(\binom{t_k}{r}\). When both inputs are nonempty,
\(k=s-1\) has \(t_k=s\), proving the lower bound for the full sequence.
For just one position \(k\), the bound \(\binom{t_k}{r}\) is itself also
attainable by the length-one products in (1).

## Matching construction for all positions

Use one channel per normalized \(r\)-element shape \(D\) with
\(\min D=0\) and \(D\subseteq\{0,\ldots,s-1\}\).
Write \(d=\max D\). Build input polynomials of lengths \(m-d,n-d\) with
coefficients

\[
U_D(a)_u=\prod_{e\in D}a_{u+e},\qquad
V_D(b)_v=\prod_{e\in D}b_{v+d-e}.
\]

The allowed translations are \(0\leq u<m-d\) and \(0\leq v<n-d\).
The offsets on the second input are reflected. Read the coefficient at
degree \(k-d\) from each channel and add the results in \(\mathbb F_2\).
Coefficients outside a product's degree range have value zero.

For a fixed \(k\), take any \(r\)-set \(S\) in (1), let \(u=\min S\) and
\(D=S-u\), and let \(v=k-u-d\). The translated reflected set
\(v+d-D=k-S\) lies in the second input, so \(v\) is in range. The channel
contributes this term at degree \(u+v=k-d\). Conversely, a term from a
channel with \(u+v=k-d\) has left indices \(u+D\) and right indices
\(k-(u+D)\). Every term of (1) appears exactly once, since the minimum and
normalized shape of \(S\) are unique. This reasoning applies at every \(k\)
with the same encoded inputs and products.

The channel's shorter width is \(s-d\). This counts exactly the translations
of \(D\) that fit in \(\{0,\ldots,s-1\}\). Grouping all \(r\)-subsets of
that interval by their normalized shape gives
\(\sum_D(s-\max D)=\binom{s}{r}\), proving optimality.

## Counting both operands

Let \(N_A\) count \(r\)-subsets \(S\) of the first input with
\(\max S-\min S<n\), and let \(N_B\) count \(r\)-subsets of the second
with span \(<m\). The matching construction uses exactly \(N_A\) left
coordinates and \(N_B\) right coordinates. Its slots enumerate the eligible
subsets by their shapes or reflected shapes.

To prove a lower bound on the left total, pool the truth-table columns
indexed by \((k,b)\), with rows indexed by the first input. For each eligible
\(S\), take \(k=\max S\) and support \(b\) exactly on \(k-S\). That column is
the Boolean function \(\prod_{i\in S}a_i\), since \(b\) places precisely
\(r\) available pairs on that antidiagonal. On rows supported exactly on
the eligible \(r\)-sets these columns give an identity. Every pooled column
lies in the span of the left encoder coordinates as functions of \(a\).
For affine decoding, first apply the zero-anchor difference and use the
centered coordinates. Thus \(\sum_\ell p_\ell\geq N_A\). Exchanging the
inputs gives \(\sum_\ell q_\ell\geq N_B\). The exact cost when charging
both operands is \(N_A+N_B\), which is \(2\binom{n}{r}\) for two
\(n\)-bit inputs.

## Edge cases and scope

- For \(j=0\) and \(s>0\) the sole shape is \(\{0\}\). An ordinary
  carryless product has width \(s\), and its output already gives parity.
- For \(r>s\) every requested digit is zero and the empty product list
  has cost zero. This includes a zero-length input, with an empty target
  sequence or, equivalently, zeros at any explicitly requested positions.
- For \(r\leq s\) the optimum is positive. When \(r=s\) there is one
  normalized shape, the full shorter input, and the shorter width is one.
- For a fixed digit \(j\) and growing \(s\), the optimum is
  \(\Theta(s^{2^j})\). The first digit above parity is \(j=1\), so a
  square-input scheme for that digit cannot have \(o(n^2)\) width in this
  model. For rectangular inputs the same statement uses the shorter length.
- Width prices prescribed polynomial positions. The theorem permits
  arbitrary local encoding work and concerns one digit plane of the
  separated pre-carry coefficients. Nonlinear joint decoding, input-dependent
  channels, and chained products are outside this interface.
- The ordinary integer product has already combined convolution coefficients
  with their positional weights. For example, \(3\cdot3=1\cdot9\), yet the
  pre-carry sequences are \((1,2,1,0,\ldots)\) and
  \((1,0,0,1,\ldots)\). The width theorem gives no lower bound for computing
  only the ordinary integer product or for the complete caller's \(\kappa\).

## Finite replay and source context

Run `python3 -I -B -W error verify.py` next to this proof to reproduce
the deterministic `certificate.json`. The verifier uses direct integer
convolution for its oracle and independently computes GF(2) ranks. Its
finite checks corroborate the argument above.

The research round uses canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`. PR #7830 at
`87fbf4f7b35b0f18ab12b5767775a9a424cf0b15` supplies the whole-multiplier
comparison. PR #6252 bounds the magnitude of propagated carries. The pinned
supplier, FFT, Gaussian, and signed-packing work uses different interfaces.
The argument here is self-contained. [PR #7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) · [PR #6252](https://github.com/CrocSwap/integer-mult-bounds/pull/6252)

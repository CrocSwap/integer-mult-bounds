# A table-free bijection for local Frobenius automorphisms

This scoped constructive proof was produced by Nick Petalas. Apache-2.0.

## Statement and credited premises

Fix an enumerated finite field L of size Q and characteristic p. Its element
indices are 0 through Q-1, with zero at index zero. Field arithmetic and this
enumeration are supplied. Let

```text
B = L[x_1,...,x_r]/(x_i^(p^h_i)),   h_i >= 1,
t_i = p^h_i,    N = product_i t_i,
r_e = number of i with h_i=e,
k_e = N - p^(sum_j max(h_j-e,0)),
C = sum_i k_(h_i) - sum_e r_e^2,
M = Q^C product_e product_(j=0)^(r_e-1) (Q^r_e-Q^j).
```

Empty height lists are allowed: B=L and M=1.

**Theorem.** There are explicit inverse maps between the integers
`0 <= z < M` and the L-algebra automorphisms of B, represented by the r
generator images, each in its N-monomial basis. Both maps use polynomially
many field operations and integer bit operations in r, N and log Q, with
supplied polynomial-cost field arithmetic. They require no N-by-N algebra
multiplication table and no rejection of a candidate substitution. A uniform
input integer therefore gives an exactly uniform automorphism.

The local power-kernel description, tangent criterion and order M are inputs
from Nick Petalas's [#6578, local count sections 1-3](https://github.com/CrocSwap/integer-mult-bounds/pull/6578).
That package credits apoursh's #5663 intrinsic coefficient-field and type
structure and Ali Romman's #5459 height flag. Those results and their
scientific executables are not replayed here. The new assertion is the
explicit invertible encoding and its resource bound, answering #6578's Open
next question. Ordered-basis completion and positional integer notation are
classical. No global literature-priority claim is made.

## 1. Decode an invertible tangent block without rejection

For an n-dimensional L-space, let v_0,...,v_(j-1) be the columns already
chosen. Complete them to an ordered basis P by scanning the standard unit
vectors in coordinate order and appending a vector precisely when it increases
the span. This is deterministic and always finishes after n candidates.

Every vector outside the old span has unique P-coordinates `(a,b)`, where
`a` has j field elements and `b` has n-j field elements and is nonzero.
For a vector of field indices define

```text
enc(c_0,...,c_(s-1)) = sum_i index(c_i) Q^i.
```

Thus the next column is indexed bijectively by

```text
d = enc(a) + Q^j (enc(b)-1),
0 <= d < Q^n-Q^j.
```

Decode d by division by Q^j, adding one to the quotient before decoding b.
The quotient range is exactly 1 through Q^(n-j)-1, so b cannot be zero.
Coordinates in P give the next column. Conversely, solve in the same
deterministically completed basis to recover a, b and d.

Use the successive radices `Q^n-Q^j`, j=0,...,n-1, with the first digit
least significant. This gives inverse integer codecs for GL_n(L).
Induction on j proves that all intermediate columns are independent and
that the forward and inverse constructions use the same P. Each ordered
basis occurs once. For n=0 the unique basis is empty and its index is zero.

## 2. Select exactly the free generator coefficients

Enumerate the exponent tuples `a` with `0 <= a_j < t_j` lexicographically.
For image y_i, let E_i be the monomials for which

```text
there exists j with a_j p^h_i >= t_j.
```

The cited power-kernel theorem says precisely that y_i is a linear
combination of E_i. In particular, the allowed degree-one monomials are x_j
with h_j<=h_i. The same-height coefficients of the images with height e
form one square block in GL_(r_e)(L). All remaining coefficients on E_i
are unrestricted. Call their ordered position set F, sorted first by i
and then by the monomial order. Exactly the same-height diagonal blocks
have been removed, so `|F|=C` by the cited dimensions k_e.

Decode z first in the GL-block radices, in increasing height order. Fill
each same-height tangent block using section 1. Decode the residual integer
into C base-Q field indices and put these into F. Put zero in every
forbidden position. The first GL block and first free coefficient are the
least significant digits of their respective stages.

Every image obeys its defining power relation. The tangent matrix is block
triangular with invertible diagonal blocks, so the cited tangent criterion
makes this substitution an automorphism. Conversely, every automorphism
has exactly these allowed positions and invertible diagonal blocks. Extract
those blocks with the inverse GL codec, read the free coefficients, and
recombine the same positional digits. This is inverse to decoding in both
directions. It proves bijectivity, including surjectivity, without using a
finite test as a universal argument.

## 3. Costs and exact uniformity

Scanning the N exponent tuples for each generator takes O(r^2 N) elementary
exponent comparisons. The generator-image output itself has rN field
entries. The ordered-basis algorithm in section 1 can use at most n unit
candidates at each of n stages, with a Gaussian rank calculation costing
O(n^3) field operations per candidate. Coordinate solves cost O(n^3).
The GL work is therefore O(sum_e r_e^5), and filling or extracting the
remaining coefficients adds O(rN). This is a deliberately loose polynomial
bound, not a performance measurement or an optimality claim.

Live storage consists of the exponent list and generator images, O(rN)
field indices or small exponent entries, plus O(r^2) elimination workspace
and the integer index. The index has at most rN log2 Q bits because every
automorphism is among Q^(rN) image tuples. Standard integer arithmetic and
radix operations consequently have polynomial bit cost. No products of
algebra basis elements or N-by-N multiplication table are needed for either
codec. The separate finite oracle computes products only to test the new maps.

Each automorphism has exactly one index. If z is uniform on 0,...,M-1,
each output has probability 1/M. This is a rejection-free decoder given
a uniform integer. It does not claim a fixed-length fair-bit sampler for
arbitrary M, nor implement a randomness source.

## Limits

This is a supplied-field, supplied-height local-algebra construction.
Residue-field discovery, nonsplit product permutations, semilinear
automorphisms, tensor-character transport, arbitrary-tensor recognition and
physical native execution are separate. No new kappa or multiplication theorem
follows. The universal assertion rests on this proof and the named premises;
the executable's bounded domains only corroborate the construction.

# Exact width-nine rank for the four-qubit Clifford alphabet

This scoped proof was produced by Nick Petalas. For the full projective
four-qubit Gaussian-dyadic Clifford alphabet, the tensor Gram matrix at
width nine has **rank 10,107,260,791,808** out of **12,128,668,876,800**.
Its nullity is **2,021,408,084,992**. In particular, the pointwise
tensor-independence threshold satisfies **T(4) ≥ 10**.

This answers the width-nine step of alephnan's four-qubit question. The
calculation reduces the Gram rank to 81 exact character inner products in
\(\operatorname{Sp}(8,2)\). Twenty quotient irreducibles are absent.
[PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714)

## Proof

### From tensor rank to quotient characters

Let \(G\) be the group of all four-qubit unitary Clifford matrices over
\(\mathbb Z[i,1/2]\), \(V\) its 16-dimensional natural representation, and
\(P\) its Pauli subgroup including \(z=iI\). The scalar kernel has order
four. The Gaussian-dyadic phase gate, the Gaussian-dyadic version
\((1+i)H/\sqrt{2}\) of the normalized Hadamard \(H\), and CNOT realize the
usual symplectic generators. Consequently \(S=G/P=\operatorname{Sp}(8,2)\)
and \(|G/\langle z\rangle|=256|S|\).

In the central sector \(z\mapsto i\) every irreducible of \(G\) has the
form \(V\otimes\sigma\) for a unique \(\sigma\in\operatorname{Irr}(S)\).
The restriction of \(V\) to \(P\) is the unique irreducible with that
central character. For any representation \(R\) in this sector,
\(\operatorname{Hom}_P(V,R)\) is a quotient representation under the
action \(\phi\mapsto R(g)\phi V(g)^{-1}\), and evaluation recovers
\(R\). Write \(V^{\otimes 9}=V\otimes W\) in this way.
These are the odd-sector reductions used for three qubits in the pinned
predecessor. [PR #6714, proof §§1–3](../clifford-three-qubit-threshold/PROOF.md)

For \(s\in S\), write \(d(s)=\dim\ker(s-I)\) on the symplectic label
space. A lift of \(s\) acts by signed permutation of the Hermitian Pauli
basis. Its adjoint trace is the sum of its signs on fixed labels.
Those signs form a character on the fixed space by multiplicativity of
Pauli conjugation. Multiplication of the lift by a Pauli adds an arbitrary
binary character on the fixed space, by nondegeneracy of the symplectic
pairing on the full label space. Hence a lift \(g\) exists with
\(|\operatorname{tr}V(g)|^2=2^{d(s)}\). For a Gaussian-dyadic trace of
this squared modulus, clearing a power-of-two denominator and repeatedly
dividing out common factors of two shows that the trace is on an axis or
a diagonal of the Gaussian plane. Its eighth power is \(2^{4d(s)}\).
The trace is nonzero, so the tensor factorization gives

\[
\chi_W(s)=\operatorname{tr}(V(g))^8 = 2^{4d(s)}.
\]

This is the permutation character on ordered four-tuples of vectors in
\(\mathbb F_2^8\). It includes the zero vector in each coordinate.

### Identifying the fixed dimensions

The permutation character on all vectors is
\(2+\chi_{119}+\chi_{135}\). To see this, the action on quadratic
refinements of the symplectic form has the same fixed-point count as
the action on vectors. For any \(s\), start with a refinement \(Q\).
The functional \(Q\circ s-Q\) is linear and vanishes on \(\ker(s-I)\).
It is therefore \(\ell\circ(s-I)\) for a linear \(\ell\), so \(Q+\ell\)
is fixed. All other fixed refinements differ by an \(s\)-invariant
functional, giving exactly \(2^{d(s)}\) of them.

The refinement orbits of the two Arf signs have sizes 120 and 136.
For example, writing \(Q(a,b)=a\cdot b+\alpha\cdot a+\beta\cdot b\),
the sign is determined by \(\alpha\cdot\beta\) and counting the pairs
gives the sizes. For fixed \(Q\), refinements of its sign other than
itself correspond to nonzero singular vectors via
\(v\mapsto Q+\omega(v,\cdot)\). Witt's lemma makes the stabilizer of
\(Q\) transitive on those vectors. Each orbit action is thus doubly
transitive and its augmentation character is irreducible. Their degrees
are 119 and 135, unique in the ordinary table. [Independent identification of the orbit characters](https://link.springer.com/article/10.1007/s13370-024-01197-2)

### Exact inner products and nullity

Use the ordinary `S8(2)` table in Thomas Breuer's GAP Character Table
Library, release 1.3.11, which attributes this table to the ATLAS.
For row \(i\) of degree \(b_i\), define the integer
\(A_{i,d}=\sum_{C:d(C)=d}|C|\chi_i(C)\) for \(1\le d\le 7\),
summing over conjugacy classes \(C\). The unique dimension-eight column
is the identity. Subtract the trivial character from \(\chi_W\) to
eliminate every dimension-zero column. In the positive-dimension columns
all table values are integers. Row 73 is Galois conjugate to row 72 and
has the same retained values. Therefore the multiplicities are

\[
m_i = \mathbf 1_{i=1} +
\frac{b_i(2^{32}-1)+\sum_{d=1}^7 A_{i,d}(2^{4d}-1)}{47{,}377{,}612{,}800}.
\]

[PROJECTION.json](PROJECTION.json) records the degree and seven sums
for each row in library order. The zero multiplicities occur at rows
\(2,4,7,14,15,17,20,23,27,32,38,40,51,52,58,59,66,68,72,73\).
The sum of their squared quotient degrees is \(7{,}896{,}125{,}332\).
[CTblLib 1.3.11 and source information](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/)

The group algebra ideal with central character \(i\) has a basis indexed
by projective classes. By semisimplicity its block for \(V\otimes\sigma\)
has dimension \((16\dim\sigma)^2\), and tensor evaluation is injective
on that block precisely when it occurs. The missing blocks thus have
total dimension \(256\cdot7{,}896{,}125{,}332=2{,}021{,}408{,}084{,}992\).
Subtracting from \(256|S|\) gives the stated Gram rank. The normalized
Gram matrix at width \(f+1\) is the Schur product of those at widths
\(f\) and one. Since the latter has unit diagonal, positive definiteness
at any earlier width would propagate to width nine.

### Checks independent of the table arithmetic

The verifier counts symplectic orbits on ordered \(k\)-tuples for
\(0\le k\le 8\) by Witt's lemma. Regard a tuple as a linear map from
\(\mathbb F_2^k\) into the label space. An orbit is specified by the
kernel and the alternating form induced on the quotient. For quotient
dimension \(r\) and radical dimension \(u\), the form embeds exactly
when \(r+u\le8\). There are \({k\brack r}_2\) kernels,
\({r\brack u}_2\) radicals, and
\(|\mathrm{GL}(r-u,2)|/|\mathrm{Sp}(r-u,2)|\) nondegenerate forms
on the remaining quotient. This follows by choosing the radical and
using transitivity of \(\mathrm{GL}\) on symplectic bases up to the form's
stabilizer.

Burnside's lemma then checks each of the nine moments of the
fixed-dimension histogram. The verifier also checks
\(\sum_i b_i^2=|S|\), \(\sum_i b_i m_i=2^{32}\), and
\(\sum_i m_i^2\) against the eight-tuple orbit count. Two failure
controls change one character sum and move one element between
fixed-dimension bins, respectively.

## Reproduce

Run these from the repository root with CPython 3.12.15 and the standard
library.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-four-qubit-width-nine
python3.12 -B scripts/check_research_commit.py --package research/clifford-four-qubit-width-nine --check-source-history
python3.12 -B -W error research/clifford-four-qubit-width-nine/verify.py
```

The registered replay uses the derived integer projection as input. To
rederive every projection entry from the external table, run the following
optional check. It authenticates the release archive and exact table member
before reading the 81 rows and compares the complete projection.

```sh
scratch_dir=$(mktemp -d)
curl -fsSL 'https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbllib-1.3.11.tar.gz' \
  -o "$scratch_dir/ctbllib-1.3.11.tar.gz"
python3.12 -B -W error research/clifford-four-qubit-width-nine/verify.py \
  --ctbllib-archive "$scratch_dir/ctbllib-1.3.11.tar.gz"
```

The archive SHA-256 is
`f201e9da571c681a7bbfb1e4683bdb2c80a23b005099ed0453521f59cb443434`.
The SHA-256 of `ctbllib-1.3.11/data/ctosymp1.tbl` is
`461519e33cb31b2bc46f554b09f283f0afb7125fd805840d79bfc614fce75b6f`.
The proof takes the published ordinary character table as input.
Formal proof-kernel review remains open. The computation concerns exact
Clifford operators at one width. It leaves physical implementation,
recursive costs and the five selected framework assumptions outside
its scope.

## Open next questions

- Is width ten already independent? Use the twenty missing odd-sector
  rows as the only possible constituents of the reciprocity obstruction
  for a missing even-sector irreducible. The remaining step is to rule
  out, or realize, such a combination using the two quadratic-form
  stabilizers. The width-nine rank alone does not decide this.

## Credit

Credit alephnan's [PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714)
for the four-qubit question and the odd-sector reduction, Ali Romman's
[PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526) for the
pointwise framework, and Nick Petalas's
[PR #5967](https://github.com/CrocSwap/integer-mult-bounds/pull/5967) for the
general lower bound \(2n+1\). The published character table data are
credited to the ATLAS and Thomas Breuer's CTblLib. The new calculation,
proof and checker are Apache-2.0.

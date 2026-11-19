# Sharp conditioning at the four-qubit threshold

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Use the full Gaussian-dyadic four-qubit Clifford group G, natural
representation V of dimension 16, Pauli subgroup P and scalar subgroup
Z=<iI>. Put S=G/P=Sp(8,2). The exact orders are

```text
|S| = 47,377,612,800,
N = |G/Z| = 256 |S| = 12,128,668,876,800.
```

Choose one representative U_a for each scalar coset. At tensor width f,
let A_f have columns vec(U_a^(tensor f))/16^(f/2), and let K_f be its
Hermitian Gram matrix. Thus

```text
K_f(a,b) = (tr(U_a^* U_b)/16)^f.
```

The columns have norm one. Another choice of scalar representatives
changes K_f by diagonal unitary conjugation. The following statements
are therefore independent of that choice.

## 1. Exact spectrum at the first independent width

[PR #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766)
proves T(4)=13 and computes all 81 multiplicities in

```text
V^(tensor 13) = V tensor W13.
```

Its [pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md)
uses the actual natural representation, including its Gaussian phase.
For s in S with fixed-space dimension d, W13 has character
`(-1)^d 2^(6d)`. Its dimension is 2^48. The source's complete
multiplicities m_j and quotient degrees e_j are authenticated and
recomputed here.

Every irreducible in the central-character-i sector has the form
V tensor sigma_j, with degree 16 e_j. The normalized projective Gram
formula from [alephnan's proof, Section 2](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
gives

```text
lambda_j = N m_j / (16^13 (16 e_j))
         = |S| m_j / (2^48 e_j),
regular block dimension = (16 e_j)^2.
```

To check the factors, central convolution on all of G has eigenvalue
`|G| m_j/(16 e_j)`. Combining four scalar lifts and dividing by the
column normalization gives the displayed formula. The projective
regular block has dimension `(16 e_j)^2`; it has no extra factor four.
The sum of these block dimensions is N.

All 81 eigenvalues are positive. There are 52 distinct values. The
complete values, grouped equal levels and full eigenspace dimensions
are in `RESULT.json`. Exact rational comparisons give:

| Endpoint | Quotient row | Quotient degree | Tensor multiplicity | Eigenvalue | Eigenspace dimension |
| --- | --- | --- | --- | --- | --- |
| Minimum | 1 | 1 | 651 | 470624175/4294967296 | 256 |
| Maximum | 2 | 35 | 1518660 | 7841980575/1073741824 | 313600 |

No other row attains either endpoint. Define these two eigenvalues
as alpha and beta. The exact Gram condition number is

```text
cond_2(K_13) = beta/alpha = 101244/1519.
```

The condition number of A_13 is its square root, approximately
8.164052, with the rigorous upper bound 8.165. This is the condition
number of the stated normalized tensor map. It is not a condition
number for an unspecified physical decoder.

## 2. Complete spectral moments and an independent normalization check

The verifier checks all block dimensions, all 81 exact eigenvalues,
all 52 combined levels, both endpoint witnesses and

```text
sum_j (16 e_j)^2 lambda_j = N.
```

There is a second complete moment check that uses no character rows.
Among the 256 projective Pauli lifts of a symplectic element with
fixed-space dimension d, exactly `2^(8-d)` have nonzero trace. Each
such trace has squared modulus `2^d`. This is the signed-Pauli argument
in the retained source. If c_d is the number of symplectic elements
with that fixed-space dimension, then

```text
tr(K_13^2) = N sum_(d=0)^8 c_d 2^(12d-96).
```

This expression agrees exactly with the sum of squared spectral
values, including their complete regular dimensions. The source's
independent twelve-vector orbit norm gives the same result.

A separate check constructs the entire one-qubit projective Clifford
group from literal Gaussian-dyadic S and H' matrices. There are 24
elements and all 576 projective products close. The verifier builds
its full normalized width-thirteen Gram matrix with rational Gaussian
entries. Pauli averaging directly gives the S3 quotient character
4096, -64 and 1 on identity, transpositions and three-cycles. Its
multiplicities are 651, 715 and 1365. Thus the proposed eigenvalues are

```text
1953/2048, 2145/2048, 4095/4096,
with eigenspace dimensions 4, 4, 16.
```

The literal matrix is Hermitian and has diagonal one. The product of
the three matrices obtained by subtracting these scalar roots is zero.
Their distinctness, the dimension, trace and second moment determine
all three eigenspace dimensions. This checks the group-order,
representation-degree and column-normalization factors against an
actual complete Gram matrix. Controls with each of these factors
changed fail the trace identity.

## 3. Uniform recovery bounds for later widths and subalphabets

For every positive integer k, K_k is positive semidefinite and has
diagonal one. Entrywise multiplication gives

```text
K_(f+k) = K_f o K_k.
```

The Schur product theorem preserves positive semidefinite order.
Since `I o K_k=I`, the exact width-thirteen bounds imply

```text
alpha I <= K_f <= beta I             for every integer f>=13.
```

The same bounds hold for every principal submatrix, hence for every
subset of the scalar-coset alphabet. These uniform constants are
sharp for the class that includes the full width-thirteen alphabet.
They need not be sharp at a particular larger width or proper subset.

For any complex coefficient vector c on such an alphabet,

```text
alpha ||c||_2^2 <= ||A_f c||_2^2 <= beta ||c||_2^2.
```

In particular, the least-squares inverse on the span has norm at most
`1/sqrt(alpha)`, which is strictly below 3.021. If the observation is
`A_f c + e`, its least-squares coefficients differ from c by at most
`||e||_2/sqrt(alpha)`. This remains valid when e has a component outside
the span, because the pseudoinverse first projects onto the span.
The bound is attained in the minimum eigenspace for the full alphabet
at width thirteen. The norm bound for the Gram inverse itself is
`1/alpha`; it is different from the tensor-map recovery norm.

## Evidence and limits

The eighteen retained files and all predecessor notices are unchanged.
The full source verifier runs in both registered modes. This includes
its threshold and literal Bell/Pauli checks. The new verifier uses exact
rational arithmetic for every spectral value and the complete small
Gram calibration. No floating-point eigenvalue calculation is used.

The published ordinary character table remains a mathematical input.
The source's authenticated projection is consumed here; this package
does not repeat the optional full archive extraction. No full four-qubit
group, Gram matrix or inverse is materialized. The full three-qubit and
even-sector suites, selected cold replay, Lean and Docker are not run.
No independent human or formal-kernel acceptance is claimed.

Native preparation, realization of the inverse, precision allocation,
routing, owned-state recovery, stock and the complete caller bill remain
unpriced. These algebraic constants do not discharge any of the five
framework assumptions or improve kappa. The threshold T(4)=13 and the
selected frontier are unchanged.

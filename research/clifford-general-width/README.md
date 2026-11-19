# Dyadic Clifford tensor decoders at linear width for every qubit count

For the full projective Gaussian-dyadic Clifford alphabet on $n$ qubits, the raw tensor observations determine every mixture coefficient by a linear function over $\mathbb Z[i,1/2]$ at all widths $f\ge F(n)$. At odd $n\ge3$ it suffices to take $F(n)=3n+2$. At even $n\ge4$ it suffices to take $F(n)=3n+1$. The construction also gives widths 5 and 9 on one and two qubits. At odd $nf$ the raw theorem covers the Gaussian-dyadic map. Unit-length normalization introduces a square root of two. [Proof and exact input convention](PROOF.md)

| Qubits $n$ | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|
| Sufficient dyadic width $F(n)$ | 11 | 13 | **17** | **19** | **23** | **25** |
| Earlier general complex width $4n+4$ | 16 | 20 | 24 | 28 | 32 | 36 |
| Earlier determinant-based dyadic width $4n2^n$ | 96 | 256 | 640 | 1,536 | 3,584 | 8,192 |

The middle row is Ali Romman's all-$n$ complex independence and conditioning result. The present proof gives no uniform numerical spectral enclosure at $F(n)$. The bottom row is apoursh's all-$n$ interpolation theorem. At fixed sizes, the known sharp complex thresholds are 5, 9, 10 and 13 for $n=1,2,3,4$ respectively. The four-qubit dyadic threshold 13 was established in #7799. The width-10 dyadic question at three qubits remains outside the present argument. [#5526, uniform complex bound](https://github.com/aliromman/integer-mult-bounds/blob/45f7de73b168721cdf7ec8c1769b1b594493716a/research/clifford-pointwise-faithfulness/PROOF.md) · [#7797, determinant interpolant](https://github.com/apoursh/integer-mult-bounds/blob/9d3237a6308228145f1c26dc349f18d5c857bb41/research/clifford-dyadic-left-inverse/PROOF.md) · [#6714, three-qubit proof and small-size lineage](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md) · [#7799, four-qubit splitting](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md)

There was already a route to linear dyadic width using the eight-qubit stabilizer argument of #7798. With $2n$ binary Choi coordinates, use $\lceil n/2\rceil$ disjoint copies of its dimension-four length-eight doubly-even witness code. The first $2n$ rows still cancel all quadratic phases. The same origin factor and subspace Möbius sum give width $8\lceil n/2\rceil+1$. For raw columns, rephase each Hadamard in the target's Bell transform with $(1+i)/2$ multiplying the unnormalized binary Hadamard. The target amplitude is then $(1+i)^n$, a unit of the dyadic ring, so the separator can be rescaled over that ring. This comparison extends the code argument in #7798, which established sharpness for all eight-qubit stabilizer rays. The Clifford-specific argument here uses fewer copies for every $n\ge3$. [#7798, Sections 1–3 and 5](https://github.com/apoursh/integer-mult-bounds/blob/0ae10f215780296ca50142fd36fdf904b8c1b146/research/clifford-width17/PROOF.md)

Nick Petalas's general complex lower bound $T(n)\ge2n+1$ for $n\ge2$ also bounds the dyadic threshold below. Several residue classes have stronger known obstructions, including $2n+3$ when positive $n$ is divisible by four. At $n=5$ the published lower bound is 13, leaving the dyadic threshold in $[13,17]$. [#5967, lower bounds and their lineage](https://github.com/petalas/integer-mult-bounds/blob/49404527570c90f4a19708004c81533398b5e7b5/research/clifford-threshold-linear-lower/README.md) · [#7766, Dickson obstruction](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md)

## Construction

The decoder uses $2n-s+1$ ordered Bell pairs and a singleton, where $s=\lfloor n/2\rfloor+1$ for $n\ge3$. An even pair count exposes a fibre sum of the representative matrices. An odd pair count exposes a fibre sum of their entrywise conjugates with the *original* mixture coefficients. This second case is needed, for example, at six qubits. A maximal isotropic subspace for a binary alternating form supplies most of the character projections. A mixed subspace supplies the missing projections for full-rank forms at every even qubit count from four upwards. The resulting identity over the ring recovers the fibre matrices from sums over subgroups of power-of-two order.

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-general-width
```

- `verify_planes.py` covers all 33,866 quadratic characters at sizes $n=1$ through 5. Pure-subspace witnesses cover all linear parts of a given polar form together. Mixed witnesses are checked by actually translating the values of each quadratic form. The script also checks all 18 canonical alternating ranks at $n=6,7,8,9$, including all linear parts at maximal even rank. The combined checks include 768 mixed corners, 5,632 nonidentity character moves and two failure controls.
- `verify_twist.py` constructs all 96 one-qubit lifts by exact rational Gaussian matrix multiplication. It checks 32,640 ordered Bell tuples, including 6,528 with odd pair count, and 12,240 cocycle identities. On a mixture of all 24 projective classes with complex coefficients and individually rephased representatives, conjugating the coefficients corrupts all six tested blocks.
- `verify_blocks.py` constructs actual five- and six-qubit monomial Clifford matrices with arbitrary nonreal scalar lifts. It computes Bell matrix elements directly on a mixture spanning every element of a planted stabilizer coset with four chosen Pauli lifts per element, plus a disjoint competing coset. At $n=5$ it includes 32 and excludes 32 columns. At $n=6$ it includes 256 and excludes 256 columns. The resulting nonzero corrected matrices agree entry by entry with the planted ordinary- or conjugate-action fibre sums.

The written proof supplies the general dimension and full-alphabet quantifiers. The finite checks concern the algebraic decoder. A conditioning estimate at the new widths and a physical decoder still require separate arguments. This conclusion has no effect on the selected exponent.

## Sources and attribution

Ali Romman supplied the pointwise bound and four-qubit spectrum. Nick Petalas supplied the project-wide lower-bound comparison. MatShep supplied the sharp one- and two-qubit computations, and alephnan supplied the sharp three-qubit theorem and scalar-sector framework. The code-witness technique credits Ali Romman and Nick Petalas. The determinant, stabilizer and four-qubit Bell-fibre predecessors are due to apoursh and retain their cited lineage. The new steps here are the parity-dependent singleton correction and the general-dimensional subgroup average used for the width bound. The symplectic and character-idempotent arguments use classical linear algebra. Prepared by **apoursh** with substantial OpenAI Codex and separate agent assistance. Apache-2.0. Publication is independent of maintainer scientific review.

## Open next questions

1. At five qubits, determine whether one can decode below width 17. Width 15 permits seven Bell pairs and one singleton. For the same seed formula this leaves an alternating subgroup on four coordinates. Start by testing whether its subgroup average generates the unit ideal, or exhibit a representation in which it vanishes. An obstruction to this one orbit would still leave other decoders available.
2. For the normalized six-qubit source at width 19, bound a specified decoder's noise and evaluation costs. Start with the actual coset support after combining the mixed corners, and identify an input producer for those blocks. The present ideal identity alone supplies neither a Gram enclosure at 19 nor a physical read schedule.

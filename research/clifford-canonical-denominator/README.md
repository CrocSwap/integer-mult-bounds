# Exact canonical denominator for the four-qubit Clifford decoder

At tensor width 13, the least positive odd integer that clears all odd denominators of the canonical Moore–Penrose decoder is **22,742,436,009,630,709,072,767,882,717,680,300,149,753,125**. The coefficient ring is $\mathbb Z[i,1/2]$, and the columns are the normalized tensor powers of one Gaussian-dyadic unitary representative of every projective four-qubit Clifford. The sharp odd denominator among *all* optimal-norm decoders is only 470,624,175. These two values answer different arithmetic questions about the same observations. [Proof](PROOF.md) · [Optimal-norm denominator and handoff, #7802](https://github.com/apoursh/integer-mult-bounds/blob/ebe2c019e398d73444e4f33f2d71bd5775795a01/research/clifford-dyadic-noise-floor/README.md)

The dyadic splitting identifies the canonical decoder's denominator with that of its inverse Gram matrix. A character expansion bounds every entry. Two explicit inverse-Gram entries then certify the full bound.

| Relative operator | Reduced odd denominator |
|---|---:|
| Identity (diagonal entry) | 7580812003210236357589294239226766716584375 |
| The order-17 operator of #6208 | 22949540428586199553125 |

The least common multiple of these denominators is the stated 44-digit answer. The order-17 entry supplies the additional factor of three missing from the diagonal. Its computation needs only representation degrees, multiplicities and the symplectic centralizer, without expanding the twelve-trillion-column Gram matrix. This is a coefficient-denominator result. A multiplication supplier and a price for physical divisions remain separate obligations. [Order-17 circuit and fixed scalar phase](https://github.com/apoursh/integer-mult-bounds/blob/4e3f55105e436dfa364029f9032c90f6a239fbe0/research/order-seventeen-clifford/PROOF.md)

## Reproduce

From the repository root, run with Python 3.12 and its standard library:

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-canonical-denominator
~~~

The primary checker reads the 81 rows of the exact width-13 spectrum, groups them into 80 rational character packets, reconstructs the order-17 column values and checks both reduced fractions. The independent checker generates the operator's phases from its gates, reconstructs its eight binary generator images, enumerates its full 17-element symplectic centralizer, and checks the missing $3^{12}$ directly using the independent fixed-space projection file. All 52 spectral levels contribute to the upper bound. The diagonal-only and eigenvalues-only denominators both fall short. [Numerical sources, original Git blobs and SHA-256 hashes](SOURCE-PINS.json)

## Credit and scope

Ali Romman supplied the threshold spectrum, odd-sector normalization, and earlier canonical odd-division obstruction. Nick Petalas supplied the quotient character projection from the ATLAS/GAP Character Table Library of Thomas Breuer. The Clifford conventions retain alephnan's Pauli-sector work. The sharp width-13 splitting, the noncanonical norm-optimum distinction, and the explicit order-17 representative are earlier contributions of apoursh. Classical character orthogonality and cyclotomic restriction are used throughout. This contribution is the matching universal bound and concrete two-entry certificate for the canonical decoder. Prepared by **apoursh** with substantial OpenAI Codex assistance. Apache-2.0. [Canonical obstruction, #7792](https://github.com/aliromman/integer-mult-bounds/blob/9321c67e29c3c41a188154bc5c2add7d7802b694/research/clifford-odd-division-obstruction/PROOF.md) · [Width-13 splitting, #7799](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md) · [Research claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19754792)

## Open next questions

1. At which larger odd widths do the same two inverse-Gram entries certify the canonical denominator? Start at widths 15 and 17 using the eigenvalue polynomials from #7788 and the appropriate defining or conjugate trace. Additional primes may require another symplectic class.
2. Can an exact implementation realize the denominator with a short common division schedule? Factor the proven denominator into its prime powers and bind the proposed schedule to an actual coefficient-access layout. The two-entry certificate establishes arithmetic necessity and leaves storage, movement and operation counts open.

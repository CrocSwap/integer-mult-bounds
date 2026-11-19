# The sharp five-qubit Clifford tensor threshold is 15

For the full projective five-qubit Gaussian-dyadic Clifford alphabet, the tensor columns are linearly independent over $\mathbb C$ exactly at widths **15 and above**. Two absent representation blocks account for the entire width-14 nullity. At 15, all 198 blocks in the relevant scalar sector occur. This determines the complex threshold and tightens the minimum width for a raw Gaussian-dyadic left inverse to **[15,17]**. The upper bound 17 comes from #7803. [Proof](PROOF.md) · [Five-qubit handoff](https://github.com/apoursh/integer-mult-bounds/blob/0fefff647d869054f2e2c4eef3cdcb6e3c60c573/research/clifford-general-width/README.md)

| Width | Missing blocks | Nullity | Rank |
|---:|---:|---:|---:|
| 13 | 7 of 198 | 6,466,626,860,503,040 | 25,404,356,051,598,684,160 |
| 14 | 2 of 319 | 6,954,742,423,552 | 25,410,815,723,716,763,648 |
| 15 | 0 of 198 | 0 | 25,410,822,678,459,187,200 |

At width 14 the two missing blocks have dimensions $528\cdot868$ and $496\cdot5236$ in the plus and minus quadratic-form orbits. For unit-normalized columns the sharp width-15 Gram spectrum endpoints are $394477183485/2^{43}$ and $7279231852517625/2^{45}$. Schur positivity propagates their enclosure to all larger widths. The rank result also applies to raw columns by scalar rescaling. Evaluating or pricing a full inverse and connecting it to a multiplication supplier remain open.

## Verification

The seven-pair seed proposed in #7803 also has a nonzero fixed subspace in every ordinary symplectic irreducible. The character-table extraction certifies all 198 subgroup averages. Whether the same seed splits over the Gaussian dyadics at width 15 remains open. [Independent Gram moments and the seven-pair seed](MOMENTS.md)

From the repository root, use CPython 3.12 and the standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-five-qubit-threshold
~~~

- **Block calculation.** The primary checker reads the 517 projected irreducible character rows, checks their group orders and multiplicities, and computes the missing blocks and extremal eigenvalues. The phase mutation gives positive multiplicity to each of the two genuinely absent width-14 blocks. [Exact replay](verify.py)
- **Physical representation.** Independently of the character tables, six literal five-qubit circuits check the trace sector on all 6,144 Pauli translates and check 60 Bell-label congruences, including a genuine change of trace sign. [Direct matrix checks](check_gates.py)
- **Counting controls.** The independent moment check compares group fixed-space counts and Gram moments with the projected-data calculation. [Moment check](check_moments.py)

The primary external input is the ATLAS ordinary character tables and class fusions as distributed in GAP CTblLib 1.3.11. CTblLib is distributed under GPL-3.0-or-later. The new Apache-2.0 code reads the separately obtained archive; the files of that distribution retain their original licensing. The package retains the derived fixed-space sums in table row order. The registered calculations run without network, GAP or the original archive. To regenerate every sum directly from the cited archive, pass its local path to the extraction command. The extractor checks the release and individual table-file hashes, then compares every rebuilt row. It reads the numerical table format directly in Python. [Original data distribution](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbllib-1.3.11.tar.gz) · [Extraction source and SHA-256 pins](extract.py) · [Derived projection](PROJECTION.json)

~~~sh
python3.12 -I -B research/clifford-five-qubit-threshold/extract.py /path/to/ctbllib-1.3.11.tar.gz
python3.12 -I -B research/clifford-five-qubit-threshold/check_archive_modular.py /path/to/ctbllib-1.3.11.tar.gz
~~~

The second command checks the original cyclotomic entries in a prime field, including the nontrivial Galois row references. It certifies the prime and root order and verifies all 715 width-specific multiplicities. The prime exceeds the upper bound for each multiplicity, so the residues determine the exact nonnegative integers.

## Sources and attribution

The reduction builds on alephnan's three-qubit scalar-sector treatment, Ali Romman's odd-width trace phase, four-qubit threshold and orthogonal Bell-sector spectra, and the lower bounds of Nick Petalas. MatShep established the small-qubit thresholds in the preceding line of work. apoursh's five-qubit dyadic construction and the handoff in #7803 supplied the starting upper bound. Credit for the external character data belongs to the ATLAS of Finite Groups and Thomas Breuer's GAP Character Table Library. The new calculation resolves widths 14 and 15 of the five-qubit alphabet. Prepared by **apoursh** with substantial OpenAI Codex assistance under Apache-2.0. [Ali Romman's four-qubit threshold](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md) · [Nick Petalas's general lower bound](https://github.com/petalas/integer-mult-bounds/blob/49404527570c90f4a19708004c81533398b5e7b5/research/clifford-threshold-linear-lower/README.md) · [Research claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19754784)

## Open next questions

1. Does the raw tensor matrix already split over $\mathbb Z[i,1/2]$ at width 15? Complex full rank identifies the first candidate. Start with the width-15 Bell seed and an odd prime dividing the relevant finite group order. A complex invariant-space census alone cannot establish modular splitting at these primes.
2. Can a compressed implementation at five qubits approach the width-15 complex noise optimum? Construct a finite representation of one canonical or near-optimal row, specify how the observations are encoded, and price its acquisition and arithmetic. The spectral enclosure supplies the target norm but no compressed realization.

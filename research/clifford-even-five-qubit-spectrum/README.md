# Five-qubit Clifford decoder arithmetic at every even width

The Moore–Penrose decoder for the full five-qubit Clifford alphabet first exists at width 15. Its least common odd denominator $D_f$ at even width follows two distinct laws. At widths divisible by four, $\log_2D_f=295(f-2)+O(1)$. At widths congruent to two modulo four, $\log_2D_f=190(f-2)+O(1)$. The corresponding odd-width slope from #7812 is $136(f-1)+O(1)$. Each even law comes with a finite class formula that computes the *exact* integer at any width. The sharp normalized Gram endpoints and the minimum odd denominator among all norm-optimal left inverses are also determined for every $f\ge15$. [Proof](PROOF.md) · [Odd-width predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7812)

| Width | Corner denominator digits, in orbit order | Canonical digits | $D_f$ / odd LCM of the raw eigenvalues | Minimum odd denominator at the optimal noise norm |
|---:|:---:|---:|---:|---:|
| 16 | 115, 169 | 219 | 25,515 | 394,477,183,485 |
| 18 | 201, 192 | 301 | 309,825 | 112,383,262,265,014,125 |
| 20 | 280, 428 | 625 | 2,835 | 8,114,691,052,558,369,125 |
| 22 | 327, 332 | 551 | 42,525 | 361,414,506,069,008,076,363,525 |

At 16 and 20 the corners are the full symplectic group and a nonzero-vector stabilizer. At 18 and 22 they are the plus and minus full orthogonal groups. At each width in the table both corners supply necessary odd factors, and taking the LCM of the spectral scalars alone misses the displayed ratio. The Fourier transform on the Pauli group shows *integrally away from two* why the ordinary character projectors in these smaller groups determine every entry denominator of the Clifford decoder.

A recursion computes the spectrum of the nonzero-vector stabilizer from smaller symplectic and orthogonal groups. At rank five it reproduces all 322 native irreducibles and their 143 distinct eigenvalue polynomials. The two sector LCMs have degrees 592 and 381. The root at zero has multiplicity two and one, respectively; these powers only contribute factors of two at the actual evaluation points. [Parabolic fixed-space recursion](RADICAL.md) · [LCM factors](FACTORS.json)

## Reproduction

From the repository root run the four registered standard-library checks with Python 3.12.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-even-five-qubit-spectrum
```

To print the exact denominator, sharp normalized interval, and optimal odd denominator at a specific width, run the following from the package directory.

```sh
python3.12 -IB verify.py --width 18
```

The retained data in [CORNERS.json](CORNERS.json) contain coefficient arrays in ascending degree, ordinary character counts per distinct level, and columns of the form `[class mass, fixed dimension, packet values...]`. The four checks verify the class transforms and endpoint inequalities, the polynomial LCMs and 2-adic cancellations, the smaller-rank recursion against an independent rank-five character table, and the literal radical Fourier identity on 727 Levi elements (2,906 invariant-character cases).

The optional native reconstruction uses GAP 4.14.0 and CTblLib 1.3.11. It obtains the nonzero-vector stabilizer as a permutation group on 1,023 points and constructs its character table directly. All other large tables come from ATLAS data in the pinned library. The comparison is independent of the ordering of computed classes and irreducibles. Both commands ran against the retained file.

```sh
gap -r -T -A -q -b export_tables.g > /tmp/clifford-even-five-tables.txt
python3.12 -IB rebuild.py /tmp/clifford-even-five-tables.txt
```

## Scope and sources

This is a decoder-arithmetic result. The project frontier still requires a priced integer-multiplication construction. The five-qubit threshold and splitting, the odd trace phases, the Bell/Symplectic weight decompositions, and the sharp noise-denominator criterion are prior results. Provenance includes the ATLAS authors, Thomas Breuer's GAP Character Table Library, and The GAP Group. The new class formula, stabilizer recursion, and calculations were prepared by apoursh with substantial OpenAI Codex assistance. New proof and verification code are available under Apache-2.0. [Pinned sources](SOURCE-PINS.json) · [Collaboration claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19756383)

## Open next questions

1. Which conjugacy classes and Pauli-orbit combinations realize the entire even-width denominator with the fewest literal Clifford entries?
2. Can the stabilizer recursion recover inverse class coefficients as well as their spectral polynomials, avoiding a direct rank-six parabolic ordinary character table?
3. What arithmetic and movement cost does an explicit decoder pay to exploit these denominators under the repository's circuit model?

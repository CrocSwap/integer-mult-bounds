# Five qubits split over the Gaussian dyadics at width 15

**Fifteen is the minimum raw tensor width for an exact Gaussian-dyadic left inverse of the full projective five-qubit Clifford alphabet.** The seven-Bell-pair seed already suffices at that width. Width 14 has a complex kernel, and #7803 previously gave an integral construction at width 17. The result closes the interval [15,17] from #7806. [Global proof](PROOF.md) · [Characteristic-three argument](THREE.md)

The obstruction is a simple symplectic-group module with no fixed vector for the same group of 64 shears. The published tables rule this out at 5, 7, 11, 17 and 31 in all 931 cases. At 3, the two orthogonal subgroups give incompatible trace ratios for an obstruction. Their tables have only three possible zero rows between them. Together with the ordinary calculation at primes away from the group order, these checks lift the subgroup-average identity to $\mathbb Z[i,1/2]$. The proof establishes existence of an exact raw inverse. A usable decoding circuit, a noise bound, the cost of its observations and any effect on the selected multiplication bound remain open.

The fixed space has dimension at least $6\dim(M)/6919$ for **every** finite-dimensional symplectic-group module in odd characteristic. The coefficient is sharp when matching the two orthogonal restrictions only on the identity and both shear classes. [Quantitative bound and matching witness](PROOF.md#a-universal-lower-bound-for-the-fixed-dimension)

## Reproduce the certificate

From the repository root run the registered CPython 3.12 checks. Their inputs are the compact numerical evidence and the code in this directory.

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-five-qubit-modular-seed
~~~

The primary checker recovers all 1,005 modular triples from exact decomposition equations, compares the two trace ratios and checks the ordinary class columns and the full restriction to the 64-element subgroup. A separate program generates all 64 binary shears, realizes the six generators as commutators in both orthogonal groups and counts the classes geometrically. [Retained numerical data](CHARACTERS.json) · [Primary checker](verify.py) · [Independent geometry check](check_orthogonal.py)

### Regenerating from the original sources

Two independent extraction routes reproduce the character calculation. The first uses the standard GAP interface with CTblLib 1.3.11. In this directory run

~~~sh
gap -r -T -A -q -b gap_rows.g > /tmp/clifford-five-brauer-rows.json
python3.12 -I -B verify.py --gap-rows /tmp/clifford-five-brauer-rows.json
~~~

The second route uses the original GAP archive for the ordinary characters and the published MOC decomposition-matrix PDFs for the seven modular tables. Put the original PDFs in one directory under their published names. Run the following from this package with Python and PyMuPDF. Both external methods were exercised during preparation, using GAP 4.14.0 and PyMuPDF 1.26.3 respectively. The registered replay needs only CPython and its standard library. [Release archive](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbllib-1.3.11.tar.gz) · [Archive and PDF SHA-256 pins](rebuild.py)

~~~sh
python -B rebuild.py /path/to/ctbllib-1.3.11.tar.gz /path/to/pdfs
python -B check_orthogonal.py /path/to/ctbllib-1.3.11.tar.gz
~~~

The symplectic PDFs are [mod 5](https://www.math.rwth-aachen.de/~MOC/decomposition/tex/S10%282%29/S10%282%29mod5.pdf), [mod 7](https://www.math.rwth-aachen.de/~MOC/decomposition/tex/S10%282%29/S10%282%29mod7.pdf), [mod 11](https://www.math.rwth-aachen.de/~MOC/decomposition/tex/S10%282%29/S10%282%29mod11.pdf), [mod 17](https://www.math.rwth-aachen.de/~MOC/decomposition/tex/S10%282%29/S10%282%29mod17.pdf) and [mod 31](https://www.math.rwth-aachen.de/~MOC/decomposition/tex/S10%282%29/S10%282%29mod31.pdf). The orthogonal PDFs use the simple groups. [Plus group mod 3](https://www.math.rwth-aachen.de/~MOC/decomposition/tex/O10%2B%282%29/O10%2B%282%29mod3.pdf) · [Minus group mod 3](https://www.math.rwth-aachen.de/~MOC/decomposition/tex/O10-%282%29/O10-%282%29mod3.pdf)

## Attribution and scope

The source character data belong to the ATLAS of Finite Groups, the Modular ATLAS, Gerhard Hiss and Thomas Breuer's GAP Character Table Library, with decomposition matrices published by the MOC project. CTblLib retains its GPL-3.0-or-later license. The package records numerical character values and decomposition multiplicities keyed to those published tables. The new proof and code were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0.

The group-algebra reduction is from apoursh's raw Bell interpolation construction, with earlier Clifford representation and spectrum results by alephnan and Ali Romman. The complex lower bound and ordinary fixed-space calculation at five qubits are from #7806. The new result handles all odd residue characteristics and proves sharpness over the Gaussian dyadics. [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19755739) [#7803 pinned Bell construction](https://github.com/apoursh/integer-mult-bounds/blob/0fefff647d869054f2e2c4eef3cdcb6e3c60c573/research/clifford-general-width/PROOF.md) · [#7806 pinned complex threshold](https://github.com/apoursh/integer-mult-bounds/blob/b42e665721e76e69d05f24a19bdabee0e0f77c04/research/clifford-five-qubit-threshold/PROOF.md)

## Open next questions

1. Can one exhibit a short translated-subgroup identity over the Gaussian dyadics? Start by constructing a sparse expression for 1 in the ideal of the seven-pair seed and bounding its support and coefficient sizes. The local-to-global existence argument supplies neither quantity.
2. Can an explicit five-qubit decoder at width 15 meet the complex noise target with a priced observation interface? Begin with one fibre and its required inputs, compare its row norm against the Gram enclosure in #7806, and account for acquisition, precision and storage. Recoverability alone does not establish a supplier.

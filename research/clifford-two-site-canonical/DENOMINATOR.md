# Exact common odd denominator

The least positive odd integer clearing every canonical two-site coefficient into $\mathbf Z[i,1/2]$ for all Gaussian-dyadic joint inputs is
$$D=21{,}556{,}663{,}020{,}569{,}210{,}160{,}884{,}269{,}703{,}315{,}625.$$
It has 115 bits. The analogous one-site divisor from #7823 has 73 bits. This statement prices the fixed coordinate interface. Circuit costs depend on the producer, precision and schedule.

**Reduction to five full Walsh sweeps.** For each distance $j$, use the symplectic map exchanging $Z_s$ and $X_s$ on the first $j$ qubits and fixing the others. Every relative $S'$ at this distance has the form $A S B^{-1}$ for this representative $S$ and $A,B$ preserving $Z$. Indeed pairs of Lagrangians of the same distance lie in a single symplectic orbit, by extending a common intersection basis to adapted symplectic bases. Because the scalar Gram is central, its transformed flag weight is invariant under simultaneously moving the two marked flags. Therefore the weight at $S'$ in the coefficient formula equals the weight at $S$ with the output mark transformed by $A^{-1}$ and the input mark by $B^{-1}$. A linear symplectic map preserving $Z$ acts on a fixed coset $(z,x)$ by an invertible linear change of $x$ and, within the coset, an affine change of $z$. Such changes permute Walsh frequencies and introduce only signs. Thus the set of absolute scalar multipliers is identical throughout each shell, also when the physical bases of the repeated site are rotated.

Write $x=r\oplus i$, $y=c\oplus k$, $\alpha=r\oplus m$ and $\beta=c\oplus n$. The four independent four-bit strings parametrize all $65,536$ Walsh values per shell, including the extraction factor $1/16$. The remaining factor is a conjugated matrix entry. When nonzero this is a Gaussian-dyadic unit: its squared modulus is $2^{-j}$, so its inverse is also Gaussian-dyadic. At least one Pauli translate has a nonzero entry at any requested matrix address since translations of any nonempty column support reach all rows in the left stabilizer basis. All four strings are realizable taking $r=c=0$. These observations prove that the lcm of the odd denominators of the Walsh values is exactly the desired joint divisor. Linear superposition with Gaussian-dyadic coefficients preserves the bound.

| Distance $j$ | Distinct absolute multipliers | Zero multipliers out of 65,536 | Distinct odd divisors | Shell lcm |
|---:|---:|---:|---:|:---|
| 0 | 10 | 64,140 | 10 | $D/3$ |
| 1 | 25 | 62,720 | 22 | $D$ |
| 2 | 42 | 57,216 | 35 | $D$ |
| 3 | 44 | 38,912 | 36 | $D$ |
| 4 | 27 | 0 | 24 | $D$ |

No individual matrix-unit entry realizes all the prime powers of $D$. A pair already forces it. For $B=E_{00}$, take $p=0$ in both queries. At the identity, the defects $E_{11},E_{11}$ have canonical odd denominator $562788258996425089753125$. At the one-qubit exchange representative, $E_{22},E_{44}$ have canonical odd denominator $6293916210385170849893217431625$. Their lcm is $D$. The verifier recovers these divisors from actual complex output coordinates. [Complete sweep and witnesses](denominators.py)

A single query attains the complete divisor if the joint observation is allowed to be a superposition. With $B=E_{00}$, choose the four-qubit exchange representative ($j=4$), $p=0$, and
$$
 J=E_{00}\otimes E_{11}+E_{11}\otimes E_{22}+2E_{11}\otimes E_{42}.
$$
Its canonical coefficient is exactly $35434033216309953801405149/(2^{16}D)$ in lowest terms. Thus one real output of an integer input can require the entire 115-bit odd divisor.

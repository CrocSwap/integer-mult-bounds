# Exact quadratic compilation of the Clifford atlas

The compiler takes the literal frame table, the list of graph moves and the original owner layout. At the seven-stage source there are 1,103 frames, 2,971 ordered paid pairs and 104 ports. It produces the original signed monomial–Fourier–monomial factor for every pair and both factors of every port. The normalization convention is the Gaussian square root of a bit flip. [Compiler](phase_atlas.py) · [Exact matrix elements](gauss_phase.py) · [Original frame and grade convention](https://github.com/CrocSwap/integer-mult-bounds/blob/a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e/research/grade14-native-realization/charts.py)

## The phase of one entry

Consider a circuit on n bits with reversible binary linear permutations P, bit translations X, global powers of i, diagonal Clifford phases D, and gates C(q,σ) for σ in {1,−1}. The actual interchange gate is

```text
C(q,σ) = [(1+iσ)I + (1−iσ)X(q)]/2
       = (1+iσ)/2 · [I + i^(−σ) X(q)].
```

Introduce one bit t for each C gate. On one path the current address is an affine function of all earlier path bits. A P gate maps the rows of this function by its binary matrix. An X gate changes its constant. A C gate adds q·t. The first pass computes the final address. Binary row elimination solves exactly the final-address constraints. An inconsistent system has matrix entry zero. Otherwise every valid solution occurs once as an affine function of the free bits.

The second pass substitutes this solution into the circuit. A global phase adds a constant. A C gate contributes −σt to an exponent modulo four. A diagonal gate adds linear terms in the current bits and twice their indicated pair products. For a bit parity its integer value modulo four equals the sum of its terms minus twice the sum of all distinct pairs. A constant bit one complements this value. Twice a product of two parities depends only on their product over the binary field. Its diagonal terms are linear since a bit equals its square. Consequently the exponent throughout has the form

```text
Q(u) = c + Σ a_j u_j + 2 Σ b_ij u_i u_j  (mod 4).
```

In the compiler each affine form stores its constant in the low bit. Each row of the symmetric edge mask stores the nonzero b_ij. The `add_linear` and `add_cross` methods implement the preceding identities, including their constant and diagonal terms. Thus the desired matrix entry is the sum of i^Q over all free bits, times the product of the C prefactors.

To sum a variable x, write its terms as ax+2xL where L is the parity of its current neighbors. If a is odd, summing x multiplies by 1+i^a and adds −aL to the remaining phase. This holds for each of the two values of L. If a is even, the sum is two on L=a/2 and zero on the other fibre. When x has a neighbor y, solve the constraint for y, substitute it in the entire remaining phase and discard both variables. An isolated even x contributes two for a=0 and zero for a=2. The empty sum is the single term i^c. At each elimination the number of live variables decreases. These identities prove the algorithm for every supported circuit, every input address and every requested output address.

The scalar accumulator stores zero or a power of √2 times an eighth root of unity. An odd elimination changes that exponent by one and the eighth-root phase by ±1. A pair or isolated-zero elimination changes the exponent by two. Each original C prefactor changes it by −1 and adds σ to the eighth-root phase. All these updates use integers. When the gate product is monomial the returned entry at its affine offset is a unit in {1,i,−1,−i}. Both its size and its exact phase are checked. [Formal elimination and physical C identities](PhaseSum.lean)

## Signed composition

The symplectic reduction uses the predecessor's choice of binary basis and its prescribed active Fourier rank. For each target operation the signed Pauli tableau determines the image of all coordinate X and Z generators. The monomial subroutine takes the invertible address matrix from the X columns and the affine offset from the signs of the Z columns. The Z components and phases of the X columns give the symmetric quadratic and linear diagonal terms. It constructs the literal gate sequence, replays its complete signed tableau and checks equality. The entry at the affine offset determines the remaining global scalar by the first theorem.

For a paid rank r, the code extends its independent active columns, reduces them to the first r coordinates, and removes their induced diagonal. It emits a right monomial, the positive r-bit Gaussian Fourier factor, and a left monomial. The emitter checks the final signed tableau against the target. It also computes the (0,0) entry of the target followed by the adjoint of its compiled program. It requires this entry to be exactly one. Two unitaries with the same signed tableau differ by a scalar. Indeed their quotient commutes with every coordinate Z, so it is diagonal. It commutes with every coordinate X, so this diagonal is constant. Its (0,0) entry fixes that scalar. This check covers every input column and includes absolute phase. The port checks require rank zero, identity Y ingress, full X egress and the original hosted endpoints.

The graph, its layout and the canonical emitted atlas each retain a separate fixed digest. A separate implementation uses exact Gaussian state propagation and signed Pauli action to check all 2,971 factors and all 208 port sides. An altered global phase keeps a tableau intact and fails this independent check. Random finite examples compare every matrix entry to the original dense engine. These controls supplement the elimination and composition arguments. No input operand enters setup. [Actual installation delta](production.patch) · [Controls](verify.py)

## Original coefficients and chronological ownership

Each sparse helper update has a covector, a direction and a nonzero pivot. In the original algorithm an unaffected donor row has zero pairing with the direction and lacks the removed donor. Removing that donor and adding the pairing multiple of the substitution are then both identities. The replacement scans every donor identifier for this support and reads or copies exact rational values only when this test, an injected term, or a changed output row requires them. The new recovered and observed rows use the predecessor's exact pairing formula. All other rows retain their original canonical order and coefficients. Topological sorting receives the same ordered positive dependencies. Both intermediate journal digests, the final graph digest, the owner-layout digest and all original file checks remain active. The compiled row table interns immutable rationals at equal literal strings. This leaves every row and every numerical application unchanged. [Sparse source transformation](sparse_helpers.py)

For the native caller, first enumerate every external root in its original order. Build one tuple of all nonmain helper identifiers and grades in original owner order. Build one tuple of returning node identifiers and grades in the actual execution order of the move graph. Each native instruction appends its distinct (kind, clock, call) prefix attached to these same tuples. A query or idle instruction adds its own literal entry at its actual clock. Concatenating these lists gives exactly the original sequence of (tag,rank) pairs. Every virtual port has exactly one position, and the finite index selection procedure agrees with that concatenation. No two jobs share a payload because only the immutable role and rank descriptions are shared. Both original and returned owner checks still run inside the native interpreter. Extra preparation and cleanup are charged in the [complete cost](COST.md). [Clock-labelled port generator](clock_ports.py)

The Lean kernel checks the physical complex coefficient identity and the two finite-sum elimination identities with arbitrary finite exterior weights. The affine compiler, binary elimination, total signed composition, chronological machine, resource proof and complete product are covered by written arguments and executable checks. They are outside the Lean development.

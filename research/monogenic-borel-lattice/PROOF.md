# A monogenic paired-lattice obstruction for dyadic Borel words

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. No new κ.

## 1. Contract and predecessor

Write R = Z_(2), the rational numbers with odd denominator. A full R-lattice
in Q^m means a free rank-m R-submodule spanning Q^m. A paired lattice in
H ⊕ D is L ⊕ L, using the same L on both halves and on every register.

We use the formal superposition model and the rank theorem of Sagar Thakrar's
[PR2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613), especially
PROOF.md, Setting and Corollary. These are cited premises, not replay targets.
The model is a matrix over F2[G], where G acts on Q^m ⊕ Q^m. Its moves are
binary register mixing, register-local free block-lower maps, and paid calls

    I + xy^t ([n_A] - [I]),    n_A = [[I,A],[0,I]],

with the source's scalar-projector condition y^t x = 1. Each call costs
rank_Q A. Applied free maps are invertible over Q, but may have singular
reduction modulo 2. Every inverse actually applied is a separate map subject
to the same hypotheses. Left and right actions are both allowed.

The source theorem states that if all applied matrices are 2-integral and
the required data-to-data block is a block permutation of single group labels
g_w with invertible reduced upper-right blocks, then

    sum_paid rank_Q A >= mW.

Here W is the number of data registers. The other entries of that data block
are zero. Auxiliary outputs are unconstrained in this source contract.
Additional independence or dirty-restoration requirements can restrict the
word further; relaxing them does not weaken this lower bound. eumemic's
PR288 supplies the general register/lattice framework, and Swapnil Jain's
P1 supplies the retained rank functional. We claim neither as new.

The new restriction is that every m-by-m block of every applied matrix is
f(T) for one common rational matrix T and a polynomial f in R[x]. The
polynomial coefficients and the complete applied list are hypotheses. Being
a polynomial over Q is insufficient. No complete family of rational
rank-one projector blocks is required.

## 2. Exact criterion and constructive proof

**Theorem.** For every m >= 1 and T in M_m(Q), the following are equivalent:

1. T preserves a full R-lattice.
2. The characteristic polynomial χ_T belongs to R[x].

If they hold, the explicit module

    L_T = R^m + T R^m + ... + T^(m-1) R^m

is a full invariant lattice. It is common to every polynomial in R[T].
Consequently, if all applied blocks belong to R[T] and T itself is one
actual applied block, χ_T in R[x] is necessary and sufficient for a common
paired lattice. Without the actual-block condition it remains sufficient.

**Proof.** If T preserves L and B is an R-basis of L, then B^-1 T B has
entries in R. Its determinant polynomial lies in R[x], and similarity
preserves that polynomial.

Conversely, Cayley-Hamilton expresses T^m as an R-linear combination of
I,T,...,T^(m-1). It follows that T L_T is contained in L_T. The module L_T
has m^2 displayed generators, contains R^m, and is a torsion-free submodule
of Q^m. Since R is a PID, it is free of rank m. Stability under R[T] follows
by repeated application of T and R-linearity. If every block preserves L_T,
every whole applied matrix preserves L_T ⊕ L_T. Conversely, preservation of
a paired lattice by a whole matrix implies preservation by each block, by
testing a vector supported in one half. If one block is T, necessity follows
from the first implication. This proves the criterion.

The algebraic ingredients are classical. See the
[Stacks Project's Cayley-Hamilton section](https://stacks.math.columbia.edu/tag/05G6).
The contribution here is this precise monogenic test and its application to
the source's dyadic register question, with an unanchored separating family.
No general literature-priority claim is made for invariant-lattice theory.

## 3. Transfer to the full Borel model

Take a basis B of L_T and conjugate every address matrix analytically by
diag(B,B). Use that same matrix on every scalar register. This preserves
binary mixing, block-lower shape, the form of each paid call, and the rational
rank of A. All transformed applied matrices are 2-integral by section 2.

For required labels n_I the transformed label is still n_I. More generally
the source theorem applies whenever every transformed required upper-right
block is a unit modulo 2. Thus

    sum_paid rank_Q A >= mW,

and for every a in [0,1], with nonzero paid ranks r_j,

    (1/W) sum_j (r_j/m)^(1-a) >= (1/(mW)) sum_j r_j >= 1.

Indeed, x^(1-a) >= x for 0 < x <= 1. Zero-rank calls are identities and can
be omitted. This excludes a favorable recursive bill even before additional
nonnegative charges, under this exact source contract.

The basis change is an analytic representation choice. No physical basis
conversion is supplied or declared free. Using distinct H and D bases can
destroy the target-unit hypothesis and is outside this transfer. Failure of
χ_T integrality excludes this common lattice when T is applied; it says
nothing by itself about a saving or about other representations.

## 4. An unanchored family missed by coordinate-diagonal gauges

For any s >= 1 set q = 2^s and

    T_s = [[1/q,        1/q, 0],
           [-(q^2+1)/q, -1/q, 0],
           [0,             0, 0]].

Its characteristic polynomial is x(x^2+1). An explicit basis is

    B_s = [[1, 1/q,          0],
           [0, -(q^2+1)/q,   0],
           [0, 0,            1]],

and B_s^-1 T_s B_s = J ⊕ 0 with J = [[0,-1],[1,0]]. Thus all R[T_s]
blocks have a common paired integral lattice for every s.

Any coordinate-diagonal conjugation leaves each diagonal entry unchanged.
The first diagonal entry 1/q is not in R. Therefore no common paired
coordinate-diagonal gauge can work if T_s is actually applied. This is
outside ywz65's PR2671 diagonal-only filter, not a counterexample to it.

Also Q[T_s] is isomorphic to Q(i) × Q. Its only idempotents are 0, P, Q, I,
where P = -T_s^2 has rank two and Q = I+T_s^2 has rank one. A field has only
the idempotents zero and one. The irreducible quadratic factor therefore
cannot split into rational rank-one idempotents. No applied block list
contained in this algebra can contain a complete family of orthogonal
rational rank-one projectors summing to I. The complete-anchor premise of
Nick Petalas's earlier PR6027 is unavailable. That earlier result is a
distinct filter, not a predecessor theorem needed for this proof.

This is a genuine mixed-rank example, rather than a field algebra in which
all nonzero paid blocks have full rank. Both rank-one Q and rank-two T_s
are legal algebra elements. The address labels also need not commute.
For example n_T and v_T, where v_T = [[I,0],[T,I]], do not commute because
T^2 = -P is nonzero.

## 5. A sharp abstract endpoint

Let T = T_s, Q = I+T^2, X = Q-T and X^-1 = Q+T. Both normalizers belong
to R[T]. Put l_X = diag(X,I). Direct block multiplication gives

    l_X n_T n_Q l_X^-1 = n_I,
    g = v_T l_X n_T n_Q l_X^-1 v_-T = v_T n_I v_-T.

The label g has upper-right block I, even in the original coordinates.
The two paid calls have ranks two and one. Every other displayed label is
a source-model free block-lower map. T occurs as an actual applied block.
All matrices are invertible over Q. Applying this word to each of W data
roles attains total paid rank 3W. This proves sharpness of the transferred
floor within this abstract family. It is not a native supplier or a claimed
physical cost improvement. The replay literally mixes two data roles before
the identical words and unmixes afterward, while retaining a third arbitrary
dirty role unchanged. The final F2[G] matrix is diag(g,g,I).

## 6. Bounded implementation and evidence

The public constructor `lattice.solve(T)` supports 1 <= m <= 4 and exact
integer/Fraction entries whose numerators and denominators have at most 64
bits. Unsupported inputs raise ValueError, not a mathematical obstruction.
It computes χ_T by the trace recurrence. A nonintegral coefficient is a
negative certificate for T-stability. Otherwise it reduces the m-by-m^2
generator matrix by column operations over R to produce a basis.

At pivot k choose a nonzero entry of least 2-adic valuation in the remaining
submatrix. Every elimination ratio is in R. Column swaps and additions are
invertible over R, and row swaps only change the displayed coordinates.
The original generators have full rank, so there are m pivots. Afterward
the extra columns vanish. Undoing the row permutation produces an R-basis
of L_T. No recursion or open-ended saturation loop is used.

The separate checker recomputes χ_T by the determinant's permutation
expansion, inverts the returned basis by rational elimination, and checks
T-stability and containment of every displayed lattice generator. It accepts
any such stable full lattice; it does not certify minimality of a supplied
basis. The producer's elementary-column argument proves its own exact L_T
description. Finite examples corroborate the quantified proof, not replace it.

Python's managed exact arithmetic is a deviation from fixed allocation.
Input dimension/bit bounds, m^2 generator columns, at most m pivots and fixed
finite replay corpora bound its live resources. Functions are below 60
physical lines. A single local module is loaded by its exact path to permit
isolated Python execution; no arbitrary module target, network or subprocess
appears in scientific replay. The fixed rejection helper calls only the
explicit constructor/checker functions listed in verify.py. Warning-strict
normal and optimized execution are the available recurring diagnostics.

No claim is made about general unanchored matrix algebras, blocks outside
R[T], native realization, stock/precision/tape, compiler closure, a complete
supplier invoice or outer admission. The five selected framework assumptions
remain. Independent human and formal proof-kernel review are unclaimed.

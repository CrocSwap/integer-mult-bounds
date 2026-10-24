# Paid OR normalization of nonzero 2 × 2 tensor factors

Prepared for Dugongue with substantial OpenAI Codex assistance. This is an informal all-input algebraic theorem and its implementation boundary. It is not a new multiplication κ claim.

## Theorem

Let F be a field and let G_i = [[a_i,b_i],[c_i,d_i]] for i = 0,…,k−1, with all four entries nonzero. Set N = 2^k, t_i = a_i d_i / (b_i c_i), and

    f(z) = ∏_{i : z_i = 0} t_i   for z ∈ {0,1}^k,
    M_f[x,y] = f(x ∨ y).

There are explicit invertible diagonal matrices D_out,D_in and the bit-complement permutation P on k-bit indices such that

    ⊗_i G_i = D_out P M_f P D_in.

All diagonal values, f values and address maps can be generated in O(N + k) field/address operations, with O(N) memory and no search. Given any explicit circuit for M_f, the theorem supplies a circuit for ⊗G_i with O(N) extra field operations and O(N) moves. It computes the exact action on every input vector, including arbitrary independently initialized entries.

## Proof and construction

For one factor define L_i = diag(1/a_i,1/c_i), R_i = diag(1,a_i/b_i), and J = [[0,1],[1,0]]. Direct multiplication gives

    L_i G_i R_i = [[1,1],[1,t_i]],
    J L_i G_i R_i J = K_i := [[t_i,1],[1,1]].

Consequently G_i = L_i^−1 J K_i J R_i^−1. Tensor multiplication distributes over composition, so with D_out = ⊗L_i^−1, D_in = ⊗R_i^−1 and P = ⊗J, the claimed decomposition follows from ⊗K_i = M_f. The latter identity holds entrywise: K_i[x_i,y_i] equals t_i exactly when x_i = y_i = 0 and equals 1 otherwise. The product of these entries is f(x ∨ y). This proves the identity over every field, without a characteristic restriction.

For arbitrary nonzero factor choices α_i(0),α_i(1), generate all tensor diagonal products by starting with [1] and appending the old list multiplied by each of the two next choices. This takes at most 2(2^k−1) multiplications and writes. Apply the same recursion to f using choices [t_i,1]. Compute t_i and the one-factor inverses in O(k) operations. The bit-complement index is x XOR (N−1), so each accessed address takes O(1) ordinary word operations when k fits the address width.

The input diagonal pass, the first permutation, the supplied M_f circuit, the second permutation and the output diagonal pass are actual operations. A caller may absorb a permutation into an existing address map, but no cost reduction is claimed unless that complete map is charged there. The O(N) bound above pays for separate passes if necessary. Distinct input/output buffers implement the construction directly. An in-place or borrowed-register contract requires the supplied M_f evaluator to satisfy that same contract; the algebra alone does not supply it.

## Precision and scalar preparation boundary

Suppose F = ℂ and all |a_i|, |b_i|, |c_i|, |d_i| and their reciprocals are at most 2^A for A ≥ 0. Then |t_i| ≤ 2^(4A), each f(z) has magnitude at most 2^(4Ak), entries of D_out have magnitude at most 2^(Ak), and entries of D_in have magnitude at most 2^(2Ak). The same reciprocal bounds hold for those diagonals. These follow by multiplying at most k one-factor bounds. Thus Ak = O(p) is an explicit sufficient magnitude condition for O(p) integer bits in the external factors. It does not bound the internal coefficients or intermediate amplification of the M_f circuit.

For exact dyadic or algebraic factors, prepare and apply their values with the corresponding exact arithmetic. For approximate complex factors, use directed enclosures or an explicit straight-line perturbation bound for every multiplication, division and circuit layer. Nonzero exact entries do not alone guarantee that an approximation safely admits division. In particular the theorem does not silently equip a Word RAM with exact complex division or roots of unity.

## Application to a newer shallow-circuit theorem

Alman and Li, *Kronecker Powers, Orthogonal Vectors, and the Asymptotic Spectrum*, FOCS 2025, Corollary 1.1, https://arxiv.org/abs/2509.14489 , gives M_f a depth-4 circuit of size O(N^1.249424), improving the older N^1.25 shallow exponent. The reduction above identifies the exact Gaussian/tensor factors and explicitly charges the diagonals and permutations needed to use that result. The asymptotic size statement is external predecessor mathematics. Our added scope is the concrete normalizer, enumeration tariff and precision boundary, not priority for the general reduction already discussed in that paper.

This is useful when a caller needs a shallow tensor evaluator and currently pays the older exponent. It does not beat a native O(N log N) evaluator of the same unconstrained problem, and does not improve the current multiplication κ without a changed complete caller invoice. The finite test script checks exact rational instances and rejects malformed zero-entry factors; finite tests do not replace the universal proof above.

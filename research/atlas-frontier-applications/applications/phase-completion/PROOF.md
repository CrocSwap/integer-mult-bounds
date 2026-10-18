# Why missing-phase repair works for every prime order

The proof concerns exact phases, not approximate measurements. Let p be prime, ζ=exp(2πi/p), and let E be a p×(p−1) integer matrix. Set A_ij=ζ^(E_ij). Assume the received columns are pairwise orthogonal. Every column already has squared norm p. We prove that the algorithm appends a pth-root column z with z_0=1, preserves A, and obtains H*H=pI.

## 1. Exact vanishing test for p roots

The polynomial Φ_p(X)=1+X+⋯+X^(p−1) is the minimal polynomial of ζ over Q. One elementary justification is that Φ_p(X+1)=((X+1)^p−1)/X is monic, all its lower coefficients are divisible by p and its constant coefficient is p, not divisible by p². If it factored into nonconstant monic integer polynomials, reducing modulo p would force both factors to have zero constant coefficient modulo p, contradicting that constant term. Passing from rational to primitive integer factors is justified by Gauss's lemma: products of primitive polynomials are primitive because reduction modulo any candidate prime divisor takes place in a polynomial ring without zero divisors.

Consequently an integer polynomial of degree at most p−1 that vanishes at ζ has all its coefficients equal. If nonnegative phase counts n_a sum to p, then Σ_a n_a ζ^a=0 holds exactly when every n_a=1. This proves the repair tool's incoming-column validation: the p rowwise phase differences of each column pair must contain each residue once. It also proves the independent checker's full-column validation. Diagonal Gram entries are p automatically because every entry has unit modulus.

## 2. A unit-modulus sum of p−1 roots omits exactly one phase

Suppose α=Σ_{a=0}^{p−1}c_a ζ^a, where c_a are nonnegative integers summing to p−1, and |α|=1. Define cyclic autocorrelations s_t=Σ_a c_a c_(a+t). Expanding α times its conjugate gives Σ_t(s_t−δ_(t,0))ζ^t=0; changing t to −t does not matter because s_t=s_(−t).

By the minimal-polynomial fact, all integers s_t−δ_(t,0) equal one value L. Their sum is (p−1)²−1=p(p−2), so L=p−2 and s_0=p−1. Thus Σ c_a²=Σ c_a. Every c_a is a nonnegative integer, so each c_a is zero or one. Exactly one phase m is absent. Since Σ_a ζ^a=0, α=−ζ^m. This includes p=2 without a separate assumption.

## 3. Orthogonal completion forces the missing-phase pattern

The normalized received columns A/√p are orthonormal. Extend them by one unit vector using finite-dimensional orthogonal completion, and rescale the new column to obtain H=[A,z] with H*H=pI. Since H is square, also HH*=pI. Each old row has p−1 entries of squared modulus one, so the diagonal row equation forces |z_i|=1. Multiply z by one global phase so z_0=1; this changes no received column.

For every row i≠0, orthogonality with row zero gives

    Σ_(j=0)^(p−2) ζ^(E_ij−E_0j) + z_i = 0.

The sum therefore has modulus one. Section 2 shows its p−1 phase differences contain each residue exactly once except one m_i, and its value is −ζ^(m_i). Hence z_i=ζ^(m_i). The algorithm computes precisely these missing residues, with new phase zero in row zero. It therefore recovers the orthogonal complement already proved to exist, without computing floating eigenvectors or guessing a phase.

This establishes the general sufficient theorem: any prime-order input passing the exact incoming orthogonality test admits the returned completion. The extra row missing-phase check is a directly checkable certificate and a defensive consistency check; it is never an unproved promise that supplies a missing gadget.

## 4. Preservation, verification and uniqueness

The implementation copies each received row and only appends its computed phase. Thus every received integer code is preserved, including signed representatives. The independent checker first verifies this literal prefix equality, then tests all p(p−1)/2 full column pairs by direct integer histograms. It does not use the missing-phase algorithm or import its code. A malicious common phase change to a received column can preserve orthogonality, so the separate preservation check is essential.

The orthogonal complement of p−1 independent columns in C^p is one-dimensional. Any two unit-modulus completing columns therefore differ by a global unit phase. Requiring their first entry to be one removes this freedom. In a fixture with a known erased column, the recovered column is that erased column multiplied by the conjugate of its first entry. The table need not retain its original column position because the CLI appends it.

## 5. Practical interpretation and limits

An exactly phase-coded orthogonal pilot or signal matrix with one entire column absent can be restored from its p−1 remaining columns. Scaling by 1/√p gives orthonormal pilot vectors. This conclusion needs every stated hypothesis: prime order, exact pth-root phases, correct dimensions and exact received-column orthogonality. The application supplies neither a noise tolerance theorem nor a capacity or performance improvement. The mathematical ingredients are atlas B082/B097 and classical cyclotomic and finite-dimensional linear algebra, with no novelty claim.

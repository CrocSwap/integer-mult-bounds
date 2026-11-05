# The upper factor has a length-preserving Newton merge

This is a structural advance, not yet the missing fast normalized FFT implementation. It concerns the nonperiodic factor from LOWER-FACTOR.md.

Write `d_i=exp(-a rho^2 i^2+a beta_i^2)` in this note (this is the column diagonal called `e_i` in LOWER-FACTOR.md). The upper inverse is

`(U^-1)_ij=(d_j/d_i) [X^i] prod_(k<j)(X-x_k)`.

For a node interval `[l,r)`, define the local Newton polynomial

`Q_[l,r](X)=sum_(l<=j<r) d_j u_j prod_(l<=k<j)(X-x_k)`.

Store its degree-k coefficient divided by `d_(l+k)`, for `0<=k<r-l`. The resulting local transform's entries are

`(d_j/d_i)(-1)^(j-i)e_(j-i)(x_l,...,x_(j-1))`, `l<=i<=j<r`.

The partition estimate of LOWER-FACTOR.md applies to every local transform, so its row norm is polynomial in `theta^-1` at `a=O(log(1/theta))`, independently of l and r.

Split at m. The exact identity

`Q_[l,r]=Q_[l,m]+P_[l,m] Q_[m,r]`,

`P_[l,m]=prod_(l<=k<m)(X-x_k)`,

merges children without increasing the number of coefficient records. In the above normalized coordinates its matrix is

`M=[[I,B],[0,D]]`,

where every right-child column j to parent row i has entry

`M_ij=(d_j/d_i)(-1)^(j-i)e_(j-i)(x_l,...,x_(m-1))`,

interpreted as zero unless `0<=j-i<=m-l`. In particular, D is a **unit upper triangular Toeplitz matrix conjugated by the Gaussian diagonal**. It has the exact shear factorization

`M=[[I,B D^-1],[0,I]] diag(I,D)`.

Both B and D have a uniform polynomial row-norm bound: for h=j-i, their elementary-symmetric polynomial is at most `c^-1` times the product of its h largest left-node variables; those variables are coordinatewise no larger than `x_i,...,x_(j-1)`. The Gaussian bound from LOWER-FACTOR.md therefore applies.

For D inverse, use the complete-symmetric kernel. If `x_*=x_(m-1)`, then

`|(D^-1)_ij|=(d_j/d_i) h_(j-i)(x_l,...,x_(m-1))`

` <= c^-1 (d_j/d_i) x_*^(j-i)`.

For i>=m and h=j-i, the logarithm of the last Gaussian factor is at most

`a/4-a rho^2 h^2-a rho(2rho-1)h-2a rho^2(i-m)h`.

Thus D inverse also has row norm `O(exp(a/4))`, and the shear B D inverse has polynomial norm. These statements hold on arbitrary signed/complex records.

## Remaining realization problem

The algebra is length preserving and the exact blocks have bounded norm. Directly executing their diagonal-Toeplitz-diagonal presentation is not yet safe for full-dimensional tensor fusion: the raw d_i ratio can have logarithmic range `Theta(a(r-l)^2)`. A local FFT using that presentation therefore reintroduces an O(p) guard for blocks of length sqrt(p/a).

A plain unit triangular Toeplitz map can be implemented by recursive Toeplitz shears and in-place cyclic/negacyclic Fourier transforms, as suggested by the parent investigation. To close this upper-factor route, that primitive needs a version for the **Gaussian-conjugated** Toeplitz blocks above whose intermediate norms stay polynomial, or a different bounded lifting factorization of them. The final exact block norms alone do not prove the intermediate FFT normalization claim.

The numerator Sylvester merge in the lower-factor moment tree remains a separate lifting problem; the one-product Newton merge here avoids that two-product merge for the upper factor only.

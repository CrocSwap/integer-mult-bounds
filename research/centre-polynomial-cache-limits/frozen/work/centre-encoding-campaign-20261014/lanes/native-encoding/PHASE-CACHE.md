# Exact phase cache and native tensor limits

Status: a mathematical cache theorem and exact local calculations. There is no new native encoder, supplier, or kappa value. The theorem gives an encoder when the inputs already have one common coordinate representation. It does not pay to obtain that representation.

## The minimum cache for specified diagonal updates

Let R be a matrix over C, with one column per source. Let D_1,...,D_t be diagonal matrices. Partition the source columns into fibers F. Two columns have the same fiber if every D_j has the same diagonal entry at those columns.

The smallest subspace E of source row vectors which contains row(R) and is closed under every D_j is

    E = direct_sum_F row(R restricted to F).

Thus its dimension is

    dim(E) = sum_F rank(R restricted to F).

This is both a lower bound and a construction. In each fiber, cache a basis of the rows of R restricted to that fiber. A diagonal update multiplies each such cache row by the corresponding fiber scalar. Add the fiber contributions to recover R. All these operations are scalar operations in the common representation.

Proof. Every stated fiber space is invariant and their direct sum contains row(R). Conversely, choose a linear combination D of the D_j whose diagonal entries distinguish the finitely many fibers. Such a choice exists over C: each forbidden equality is one proper linear hyperplane in the coefficient space. Lagrange interpolation gives each fiber projector as a polynomial in D. Hence every invariant E that contains row(R) contains each row of R restricted to each fiber. These spaces have disjoint supports. Their dimensions add. This proves minimality and the stated encoder.

For sign characters D_s[p,p]=(-1)^(q_p dot s), the fibers are the values of q_p on span(s). The same theorem applies to inverse-C eigenvalues, since 1 and i are a nonconstant affine function of the sign character. Tensor products introduce products of these eigenvalues; a cache that is invariant under the generators is invariant under all those products.

This theorem concerns exact linear scalar caches. It permits redundant rows and arbitrary diagonal eigenvalues. It does not claim a lower bound on a native encoder whose input maps have source-dependent address operators.

## Binding to the selected clean centre matrix

The source pin is bce54fb3f895cbe5cd4c0eb477c3afeed100190f. The input archive is research/community-frontier1042-audit/selected-replay.tar.gz, SHA-256 22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754. The full native map and its frame convention are derived in the earlier centre-sharing handoff. This lane uses the same forward boundary R.

Exact calculations give R R^T = 56 I_8. Each of the 112 columns has four nonzero entries, each 1 or -1. Their supports form fourteen tetrads. Each tetrad contains eight columns and has row rank four. The eight centre-frame normal vectors are

    42, 7, 25, 52, 82, 127, 97, 76.

They span a binary space N of dimension four. Two ports have the same values against N if and only if their R columns have the same tetrad support. The exact minimum cache closed under these sixteen sign characters therefore has 14*4 = 56 rows. For the listed order of normals, the successive cache dimensions are

    8, 15, 28, 44, 44, 56, 56, 56, 56.

For the first d coordinate characters, the dimensions are

    8, 16, 31, 53, 85, 101, 112, 112, 112, 112.

The latter sequence proves that six particular independent character directions already force all 112 source rows in this cache model. In particular, the 56-row cache is not closed under the full native source phase family.

Within each tetrad, choose its first nonzero coordinate as sign reference. The other three signs form all of F_2^3. The source label q is an affine function of those three sign bits. Its eight labels form an affine three-flat which does not contain zero. Their linear span has dimension four. These facts give a compact cube model for a possible joint native encoder. They do not give such an encoder by themselves.

## Why the eight totals cannot receive a nonconstant phase update alone

Let W = row(R). The orthogonal projector on W is P=R^T R/56. Form a graph on the 112 columns, joining p and q when their inner product is nonzero. The graph is connected; each vertex has 52 neighbors.

If a diagonal complex matrix D preserves W, then it commutes with P. Indeed, the spectral projections of a diagonal matrix are polynomials in D. W is invariant under them, so W is a direct sum of its intersections with their orthogonal coordinate subspaces. Therefore W is reducing for D. For each nonzero P[p,q], commutation gives D[p,p]=D[q,q]. Connectivity forces D to be scalar.

Consequently an exact update B R = R D on only the eight totals exists only when D is scalar. This statement permits arbitrary complex 8-by-8 B; it does not assume that B is unitary or diagonal. For native sign characters the only scalar cases are s=0 and s=511, because the 112 labels are odd and their differences span the even-parity hyperplane. The finite ranks are eight for those two characters, fifteen for sixteen characters, and sixteen for the remaining 494.

This excludes a proposed eight-register phase update. It does not exclude a larger cache, rereads, or a source-dependent native encoder.

## A tensor test for proposed native identities

Let A_1,...,A_r be nonzero pairwise nonproportional matrices over C. Their tensor powers A_i^(tensor lambda) are linearly independent for every lambda >= r-1.

Proof. For each fixed i and each j != i, choose a linear functional l_ij with l_ij(A_j)=0 and l_ij(A_i)!=0. Apply the tensor product of these r-1 functionals to the first r-1 factors. If lambda is larger, use a functional that is nonzero on A_i on every additional factor. This functional annihilates every A_j^(tensor lambda) except the i-th one. Apply it for every i.

A fixed finite linear native circuit expands into finitely many paths. Each path carries a scalar coefficient times the tensor power of a product of its base native matrices. Group projectively equal path matrices and apply the lemma. Thus cancellations between different base native operators at lambda=1 cannot be used as an all-size identity. A proposed joint encoder must either have the correct projective native path operators, cancel each unwanted operator class separately, or use a mechanism outside this fixed tensor-path model.

For example C_q^-1 = ((1-i)/2) I + ((1+i)/2) X_q at lambda=1 does not imply the same two-term formula for C_q^(-tensor lambda). At lambda=2 there are two additional mixed translations, with nonzero coefficient 1/2. A zero-rank scalar implementation based on the two-term formula is invalid.

## Cost boundary and next step

The 56-row phase cache can be formed with scalar operations only if the required source values are already in a common representation. Starting at the actual local C_q entrances, copying all sources to frame zero costs 112 rank units before storage and scalar work. Forming four separate queries in each tetrad's rank-four frame costs 224 rank units. Neither method beats the retained 64 centre rank units for one call.

The useful remaining construction question is whether actual repeated calls provide a common-frame birth or an existing native computation which can form this cache once and keep its phase updates within N. A second possible route is a joint native cube encoder which is cheaper than four separate rank-four queries in each tetrad. No such route has been admitted here. The exact cache theorem supplies the representation and its compatibility test; a complete supplier cost remains open.

Research and implementation: OpenAI Codex under the user's direction, with substantial AI assistance. The selected supplier, its exact Clifford compiler, and the preceding centre-sharing native-map calculation supply the inputs. No independent human review is claimed.

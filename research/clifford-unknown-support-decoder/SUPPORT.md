# Which supports can be recovered?

Write k=floor((f−1)/2). Each statement below guarantees independent k-th tensor powers for **every** permitted support. The cut proof converts that fact into exact recognition and recovery of the entire support. Larger powers preserve independence. The limits are sufficient. The next rejected row-sum certificate does not exhibit a dependent support.

| Four-qubit observation width | Certified support at the stated width |
|---:|---|
| 13 | Any 19 labels |
| 15, 17, 19, 21 | Any 32, 64, 119, 234 labels, respectively |
| 23 or 24 | Any 447,742 labels |
| 25 or 26 | At most 226,718 complete symplectic fibres. In particular, any 58,040,063 labels |
| 27 and above | Every subset of all 12,128,668,876,800 projective labels |

A fibre contains all 256 Pauli lifts of one symplectic transformation. Partial fibres can be arbitrarily numerous at widths 25 and 26. For example, a support with 255 labels in each of the 47,377,612,800 fibres meets the guarantee. Large cardinalities in the table describe proved classes. Emitting s labels needs at least s output records.

## Elementary bounds and the nineteen-label theorem

For any s distinct projective vectors, their (s−1)-st powers are independent. For each vector multiply s−1 linear forms, each zero at a different competitor and nonzero at the chosen vector. These products separate the s columns. This proves the bound s≤k+1, including a singleton at k=0.

For distinct projective Cliffords let V be a relative unitary. Expand it in the orthonormal Hermitian Pauli basis for the inner product tr(M*N)/d. The coefficient of I is tr(V)/d. Let S be its symplectic action, K=ker(S−I) and L=im(S−I)=K-perp. For x in K, conjugation by P_x changes V only by a sign. Every Pauli coefficient in its support then obeys the same fixed-character equations. This restricts the support to one affine coset of L. The relation V=±P_(Sx) V P_x propagates its coefficient magnitudes under all translations by (S−I)x. The entire coset therefore occurs with constant magnitude 2^(−rank(S−I)/2). At rank zero a distinct Pauli has trace zero. This proves coherence at most 1/sqrt(2) and the simple sufficient condition (s−1)²<2^k by strict diagonal dominance of the normalized Gram.

A distinct neighbour at maximum overlap has exactly two Pauli terms, I and a nonidentity Hermitian P. Equal magnitudes and unitarity force the ratio to be ±i. Conversely each (I±iP)/(1+i) is a Gaussian-dyadic Clifford, since it fixes commuting Paulis and carries each anticommuting Pauli Q to ±iPQ. All other distinct nonzero overlaps have modulus at most 1/2.

Connect two labels when their relative unitary is such a maximum neighbour. For P≠Q the two-step product (I±iP)(I±iQ) has four Pauli labels I,P,Q,PQ, each with a nonzero coefficient. Thus the graph has no triangle. A given four-term endpoint has at most three possible first Pauli labels. Its relative coefficient to I fixes the sign, and then the second step is fixed. For P=Q the endpoint is the identity or the Pauli P. The latter has exactly two two-step paths. Thus any two distinct vertices have at most three common neighbours.

For the adjacency A on an s-set, a row of A²+2A has sum at most deg+3(s−1−deg)+2deg=3(s−1). It follows that the spectral radius ρ(A)≤sqrt(3s−2)−1. At k=6 the entries of |Gram−I| are bounded by (7A+J−I)/64, where J is the all-ones matrix. Applying this bound to the absolute values of the entries of a complex test vector gives

    ||Gram−I|| ≤ (7(sqrt(3s−2)−1)+s−1)/64.

At s=19 this is strictly less than one, since 53²−49·55=114>0. This proves independence for any nineteen labels at k=6 for every qubit count. The finite checker independently counts all 510² four-qubit two-step paths. It also compares a literal generator criterion with all 32,768 pivot-normalized four-qubit real sign diagonals. [Checker](nearest_check.py)

For general k≥1 put q=2^k and c=ceil(sqrt(q))−1. Multiply the Gram error bound by q. A maximum neighbour has weight sqrt(q), and all other off-diagonal entries have weight at most one. The same argument now bounds the result by c(sqrt(3s−2)−1)+s−1. The implementation checks the strict inequality against q using integer squares. It uses the elementary bound when that is stronger.

## Recover restricted independence from a missing representation

Put G equal to the four-qubit projective group, S=Sp(8,2), M=|S|=47,377,612,800 and N=|G|=256M. The retained table calculations give two absent quotient degrees 595 and 3213 at k=11, just the corresponding inflated modules at k=12, and complete support at k=13. These are predecessor results. In particular the nullities at 11, 12 and 13 are respectively 2,733,412,864, 10,677,394 and zero. The [checker](flank_certificates.py) rederives the missing rows and the class data used below from the two pinned projections. The group representation identifications in the source proofs remain inputs. [Odd-width decomposition](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md) · [Even-width kernel and projector](https://github.com/aliromman/integer-mult-bounds/blob/ff9bdc0e82e75ab5ed39f3ff034ac8ddb3ea06d2/research/clifford-width-twelve-nullity/PROOF.md)

Let Q be the orthogonal projector on the full nullspace. If a nonzero null vector has support contained in B, then Q_BB has eigenvalue one. It suffices that the maximum absolute row sum on that restriction be strictly less than one to exclude this possibility. The global projector is invariant under projective left translation up to row and column phases. Every row has the same sorted absolute values. The sum of its largest b entries therefore bounds the norm of every restriction to b labels. This uses the class distribution of the missing blocks, which is stronger than a bound from their dimension alone.

For a quotient conjugacy class C define

    t(C) = 595 χ_9(C) + 3213 χ_22(C),
    D(C) = 2 + χ_5(C) + χ_6(C) = 2^dim ker(S_C−I).

At width eleven the absent projective modules are the conjugate natural module tensored with those two quotient modules. They have degrees 16·595 and 16·3213. Character orthogonality in the regular central-character sector gives absolute projector entry (16/N)|tr(V)| |t(C)| at a relative lift V. The phases of the section and conjugation do not change this modulus. For each element of C, precisely 256/D(C) Pauli lifts have trace modulus sqrt(D(C)). Indeed, the Pauli support of one lift is one coset of size 256/D(C), as shown above. Multiplying by a Pauli moves the identity coefficient through the 256 positions. Other lifts have zero trace.

Sort the resulting absolute numerators over the 81 classes with their actual multiplicities. The largest 447,742 sum to

    11,911,956,830,592 + 153,237,880,320 sqrt(2) < N.

Including the next changes the rational part to 11,911,970,828,800 and makes the sum exceed N. Both comparisons are exact by integer squaring with positive sides. This proves the width-23 and width-24 bound.

At width twelve the full nullspace projector at (g,h) is t(C)/N, with C the class of the relative symplectic images. Hence a null vector is constant on each complete 256-element fibre. Equivalently it is the pullback of a quotient null vector with projector entries t(C)/M. A dependence supported on B must fit entirely in the *complete* fibres of B. Changes from the canonical normalized columns to pivot-normalized columns preserve every dependence support, even if they rescale its coefficients. Sorting |t(C)| with multiplicity |C| on the quotient gives

    47,377,582,336 < M < 47,377,722,042.

The left sum uses the 226,718 largest entries. The right adds one. Thus at most 226,718 complete fibres cannot support a nonzero dependence. Fewer than 256·226,719 labels always meet this condition. This proves the width-25 and width-26 claims, including the arbitrary 58,040,063-label guarantee. The recognizer computes the symplectic image of each recovered label, groups equal images and counts groups of size 256. It never allocates the full quotient atlas.

At width thirteen the full dictionary has rank N. This proves the unrestricted result at observation width 27. Direct recomputation at k=13 also gives 81 positive blocks, 52 spectral levels and least normalized eigenvalue 470624175/4294967296. The checker tests the restricted-projector premise on all 24 one-qubit fourth powers, where the full kernel is the constant line and every 23-column deletion has full rank. It does not materialize the four-qubit Gram or enumerate its 12 trillion labels.

## Unrestricted decisions from a measured cut

At f≥14 a cut can have a long side of at least 13 and a short side of length p≥1. For an arbitrary full-span mixture with s distinct nonzero terms the long-side power columns are independent, irrespective of s. Its flattening therefore has rank exactly equal to the rank of its short-side columns. Write K(p) for the guaranteed independent cardinality above. If the observed flattening has rank at most r with r<K(p), then s≤r. Otherwise some r+1 short columns would be independent. This implication begins with an arbitrary full-span mixture and derives its sparsity from the input.

For f=14 through 26 the program sets p=min(f−13,k,12) and checks the two orientations. A packed bond dimension is a sound rank upper bound. When that bound is too large it calculates the actual rank from independent prefix and suffix boundary samples. Their dot products are entries of the flattening. The two sampling maps span the respective boundary spaces, so their matrix has the full flattening rank. A successful certificate also checks that r fits any explicit user cap. The balanced recovery class then contains every possible full-span representation of this input. Its negative answer excludes the *entire* Clifford span. At f=19 this holds on a six-site cut of rank at most 18. At f=24 it holds on an eleven-site cut of rank at most 447,741. At f=25 and 26 a twelve-site cut of rank at most 58,040,062 suffices. This criterion is optional evidence on a particular input. Failing it leaves the stated support-class decision valid.

The implementation uses the full group if its cardinality fits a certified bound. Sharp sparse thresholds, general noisy identification and physical multiplication-provider interfaces are open.

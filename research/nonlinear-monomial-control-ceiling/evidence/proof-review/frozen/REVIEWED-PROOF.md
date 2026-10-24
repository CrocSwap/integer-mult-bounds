# Support-partition extension of the released four-control obstruction

Root derivation revised after independent review; final review pending. Local-only. No paid lower bound or kappa claim.

## Changed scope and exact predecessor

The published PR #5160 head 7800589ce99d932bdb063aafca1f501f1a38626d proves the obstruction for fixed finite columnwise monomial-Clifford/scalar-owner programs. This extension permits arbitrary invertible one-column monomial matrices, including nonlinear address permutations and arbitrary nonzero complex weights, in a fixed finite columnwise owner program. More generally, it suffices that the complete one-column operator products occurring in each proposed control have a fixed finite support independent of width f; only their outer scalar coefficients may depend on f. Merely fixing a finite generating alphabet is insufficient if word products or lengths vary without bound with f: weighted monomial generators can generate infinitely many projective products. That larger class is not covered. It does not cover growing alphabets, noncolumnwise or general width-dependent permutations, extra paid Gaussian calls, a changed endpoint, compressed/input-coded targets or a changed source.

Scientific source remains 4c0a359d88f22f05189d51f48387750b801a45d4, research/coded-native-caller. Reuse the authenticated source facts and exact normalizer conventions in outputs/released-operator-intersection-20261023/PROOF.md and its source checker. There are 112 owners; A is invertible with zero diagonal. K1s/K3r are actual signed linear permutations supported on q+U / q+W, G_s e_q=q_s, and distinct source q_s make G_s^-1 q_j=e_q iff s=j. Q and D3 are supported on q and W respectively, with every entry inside their respective coset blocks nonzero. These are inherited source premises, not newly machine-checked here.

## Lemma 1 — a monomial intertwiner preserves support partitions

Let F be an invertible matrix whose support is exactly a disjoint union of complete square blocks indexed by a partition P of the computational basis. If h and k are invertible monomial matrices and F h = k F, then their address permutations both map every P-block bijectively to a P-block, with the same induced permutation of blocks.

For a column y, support(F h e_y) is the entire P-block containing sigma_h(y). Support(k F e_y) is sigma_k(P(y)). These must be equal. If y,y' belong to the same P-block, the latter set is unchanged, so sigma_h sends that block into a single block. Invertibility and the equal finite block sizes force equality. The same identity supplies the assertion for sigma_k. No phase restriction is used; multiplication by a monomial matrix creates no internal cancellation.

For a two-sided variant F_out^-1 a F_in monomial, where F_in/F_out have complete equal-size coset blocks (possibly different partitions), write a F_in=F_out m and use the same column-support argument. The address permutation of a maps input blocks to output blocks. This variant uses no Clifford/symplectic classification.

## Lemma 2 — transported letters preserve the required partitions

Let H be the group of all invertible monomial matrices on the actual 17 one-column bits. Let h in H satisfy Q^-1 h Q in H and k=D3 h D3^-1 in H. From h Q=Q(Q^-1 h Q), Lemma 1 says sigma_h preserves q-cosets. From D3 h=k D3, both sigma_h and sigma_k preserve W-cosets.

The join of the q- and W-coset partitions is the (q+W)-coset partition, indexed by U coordinates. An invertible permutation preserving both component partitions preserves their join, hence sigma_h preserves (q+W)-cosets. D3 and D3^-1 act inside these join blocks. Therefore k=D3 h D3^-1 has no nonzero matrix entries between an input join block and any output join block other than h's induced image. Because k is monomial, sigma_k also preserves the join partition.

Consequently, sigma_k cannot map a pair lying in different(q+W)-cosets to a pair in the same(q+W)-coset.

## Lemma 3 — every nonzero terminal source term remains nonmonomial

For the same four-control equations as PR #5160, let a=K3i^-1 K3r and b=K1s^-1 K1j. A terminal term has address operator Q^-1 a k b Q^-1, coefficient A[i,r] b[r,s,k] A[s,j]. If this operator were monomial, write a k b Q^-1=Q m. The two-sided support lemma implies a k b maps q-cosets to q-cosets. Since a,b are invertible signed linear permutations, sigma_k must map cosets of v=G1s^-1 q_j to cosets of w=G3r^-1 q_i.

Here v belongs to span(q)+U and w belongs to span(q)+W. A w-coset consists of two points in one(q+W)-coset. If v has a nonzero U component, every v-coset has its two points in different(q+W)-cosets. This contradicts Lemma 2. Thus v=e_q, so s=j by the actual distinct source directions. But then A[s,j]=A[j,j]=0. Every terminal term with nonzero source coefficient is therefore nonmonomial. This does not require r=i and does not assume the invalid transported central equality from the old draft.

## All-width conclusion for fixed operator support

Use the elementary tensor-separation lemma from PR #5160: tensor powers of a finite collection of pairwise nonproportional nonzero operator vectors are independent for sufficiently large f. It applies to arbitrary matrices, not only Clifford operators.

For any fixed finite columnwise owner program, take the finite set of complete one-column operator products in its expansion and combine projectively equal products. The same applies to all four proposed control implementations. This finite-support premise is essential. Requiring t0, Q^-1t0Q and D3t0D3^-1 to have finite monomial expansions forces every surviving one-column letter h of t0 into the exact intersections in Lemma 2 for all sufficiently large widths. Coefficients may depend on f; the complete operator support remains fixed independently of f. Lemma 3 places every surviving terminal E term outside H. Cancellation may remove outside-H classes but cannot produce an H class. Separating the finite combined set against any proposed finite monomial program for E gives E_f=0 for all sufficiently large widths.

The actual C1,C3 and Q are invertible, so E=Q^-1 C3 t C1 Q^-1=0 implies t=0 and t0=0. Hence an all-width invertible t0 is impossible in this enlarged class of fixed finite columnwise arbitrary-monomial programs, or explicitly fixed finite complete-product supports. No paid Gaussian query lower bound follows. Programs with unbounded width-dependent products even from finite weighted generators, growing supports, or noncolumnwise FREE programs and altered four-control/target contracts remain outside this theorem.

## Verification and credit still required

Independent proof review must check the partition argument, the exact matrix order of every intertwiner and the source support conventions. A small exact support checker with nonaffine examples can discriminate the extension but cannot prove the all-width theorem. No operator alphabet enumeration or native/compiler replay is proposed. Primary credit: Dillon released equations, Dugongue/mdumitrean source A, real normalizer authors and Cinna Davis/1337isnot1337, Cao Yifan/intqwq, zxv and retained helper/Clifford/compiler lineage. This extension is a root support-partition derivation with substantial OpenAI Codex assistance; it is not a published-paper theorem or formal-kernel proof.


## Revision note

The first draft used “fixed alphabet” too loosely outside its fixed-program paragraph. Independent review identified that finite weighted monomial generators need not have finitely many projective products. This revision explicitly requires a fixed finite program or fixed finite set of complete operator products; it excludes unbounded width-dependent word products. The first draft remains in history/PROOF-DRAFT-v1.md. No source or predecessor proof was changed.

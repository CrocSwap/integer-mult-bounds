# Independent review of the nonlinear monomial four-control extension

**PASS for the revised fixed finite complete-product support theorem.** The support-partition argument excludes an all-width invertible interleaver in the declared class of fixed finite columnwise arbitrary-monomial owner programs. It permits arbitrary nonlinear permutations of the actual one-column address set and arbitrary nonzero complex weights. It does not classify all physical FREE programs, give a paid-query lower bound, or cover changed endpoints or input encodings.

Reviewed author proof SHA256: `76bea47531ed557c0c9cb210c4324d6000c74415bf13e5747b7036567853f6ef`. Its exact bytes are `frozen/REVIEWED-PROOF.md`; eight byte-preserving captures and the inherited source identities are recorded in `SOURCES.json`. Scientific source: `4c0a359d88f22f05189d51f48387750b801a45d4`, `research/coded-native-caller`. The stated predecessor is PR #5160 head `7800589ce99d932bdb063aafca1f501f1a38626d`; this review relies on the captured predecessor proof and source records, not a fresh public-head verification.

## 1. A real scope defect was found and repaired

The first draft's repeated “fixed finite alphabet” description was insufficient for weighted monomial generators if their word lengths/products could vary without bound with width. For example, `diag(2,1)^n` gives infinitely many distinct projective one-column products from one generator. Finite permutations alone do not remove this weighted-product problem.

The reviewed revision explicitly requires a fixed finite owner program, or a fixed finite set of the **complete one-column operator products** in each proposed control, independent of width. Only the outer scalar coefficients may vary with width. This is the condition needed for the finite tensor-separation argument. The first draft is preserved as `frozen/FIRST-DRAFT.md`; it is not the accepted statement. No counterexample was found to the revised theorem.

## 2. The support-partition lemma is sound

Write a monomial map as `h e_y = c_y e_sigma_h(y)`, with every `c_y` nonzero. If `F` is fully supported inside each block of a partition, `Fh e_y` has precisely the block containing `sigma_h(y)` as its support. If `Fh=kF`, the other side has support `sigma_k(P(y))`. A monomial multiplication cannot create cancellation inside these supports. For all `y` in a fixed input block, this equality identifies the same output block; bijectivity gives a block bijection and the same induced block map for h and k. The source coset blocks have equal sizes, as required by the proof's stated application.

The two-sided form also has the correct order: from `F_out^-1 a F_in=m`, obtain `a F_in=F_out m`. Column supports imply that the monomial address map a takes each input-partition block to an output-partition block. No affine, orthogonal, symplectic, unitarity or finite-phase restriction is used.

## 3. Join transport is valid; the stronger false invariant is unnecessary

For an initial letter h, `Q^-1 h Q` monomial gives `h Q=Q m`, so h permutes q-cosets. The equation `D3 h=k D3`, where `k=D3 h D3^-1`, gives that both h and k permute W-cosets. In particular h preserves the join of the q- and W-coset partitions, namely the `(q+W)`-cosets indexed by U.

Let B be one such join block and tau(B) its h-image. Both `D3` and its inverse operate entirely inside these join blocks. Therefore `D3 h D3^-1` maps the vector space supported in B into the vector space supported in tau(B), even if multiplication creates cancellations. Since k is invertible monomial, its underlying permutation maps B bijectively to tau(B). Thus two addresses in distinct join blocks cannot be sent into a common join block.

This argument does **not** assert that k preserves q-cosets, fixes the central direction, or belongs to the untransported intersection. It replaces the erroneous stronger transport inference with exactly the join-block condition needed below. Nonlinear address maps and nonconstant weights do not change it.

## 4. Terminal order and source directions check

With rightmost operators applied first, the terminal address word is

`Q^-1 a k b Q^-1`, where `a=K3_i^-1 K3_r` and `b=K1_s^-1 K1_j`.

If this word is monomial m, then `a k b Q^-1=Q m`. Apply the two-sided support lemma with `F_in=Q^-1`, `F_out=Q`, and monomial intertwiner `a k b`. Both Q and its inverse have complete q-coset support. Hence `a k b` maps q-cosets to q-cosets.

Pulling those cosets through b and through `a^-1` gives exactly

`v=G1_s^-1 G1_j e_q=G1_s^-1 q_j`, and `w=G3_r^-1 G3_i e_q=G3_r^-1 q_i`.

The order of the two inverse factors is correct. Signed weights do not alter these support directions. The first vector is nonzero and lies in `span(q)+U`; the second is nonzero and lies in `span(q)+W`. If v has any U component, a v-pair starts in distinct `(q+W)` blocks while its required w-pair endpoint lies in a single such block. This contradicts the transported join invariant. Over the binary address space the remaining nonzero possibility is `v=e_q`. Distinct source directions then give `s=j`, and the source coefficient contains `A[j,j]=0`.

Thus **every terminal term with a nonzero scalar coefficient is nonmonomial**. The reasoning does not require `r=i`, projective distinctness of all terminal terms, or an absence of cancellations among nonmonomial terms.

The inherited exact source premises are the 112-owner invertible scalar A with zero diagonal; `K_i=Z_z P_G` using G rows as rows; `G_i e_q=q_i` with distinct q_i; disjoint q/U/W embedding; and complete nonzero Q/D3 coset support. Source PHYSICAL.md gives the rightmost-first convention, Gaussian entries and columnwise lifting. The Gaussian factors and their inverses have nonzero entries in their full coset blocks. No source-specific absolute phase identity beyond these premises is discarded: in particular Q is not silently treated as an operator involution.

## 5. The all-width conclusion has the required quantifiers

For m pairwise nonproportional nonzero operator vectors, tensor powers are independent for every `f>=m-1` (and positive f). For each vector choose m-1 linear functionals killing the other vectors but not that one; tensoring them isolates its tensor power. Extra factors extend to larger f. This proof applies to arbitrary complex matrices, whether monomial or not.

Take the finite union of all complete products in the four proposed implementations, their relevant conjugates, and the terminal source products. Combine projectively equal matrices first, carrying their scalar factor to its f-th power. Conjugation is projectively injective, so a surviving initial letter whose Q or D3 conjugate is nonmonomial cannot be concealed by a distinct initial projective class. Tensor separation therefore puts each surviving initial class into the hypotheses of Lemma 2, at each sufficiently large width.

By Lemma 3, all surviving terminal source classes are outside the monomial group. Grouping equal classes or canceling their coefficients can remove these classes but cannot introduce a monomial class. The finite union with the proposed monomial implementation of E is separated at sufficiently large width. Therefore membership of E in that implementation forces `E_f=0` there. The source codes are invertible at every width: each is a conjugate of the scalar owner matrix A, not a tensor power of its owner-space sum. Invertible C1, C3, Q and D3 then give `t_f=0` and `t0_f=0`.

The conclusion is pointwise at every sufficiently large width satisfying the four memberships. A family supported only at finitely many small widths is not excluded; an all-width invertible family is. No small practical value of the separation threshold is claimed. Actual executable inverse programs need not be inferred from algebraic invertibility because the forward memberships already give the obstruction.

## 6. Verification boundary and optional discriminator

This was a written mathematical review with bounded reads of the proof, predecessor and pinned source premises. It did not execute a t0 search, operator enumeration, source/native/compiler/Lean replay, or a new numerical checker. The predecessor source checker was inspected as source-premise evidence; its structural receipt is not an all-width proof.

An optional bounded exact discriminator can use 16 addresses with bits q,u1,u2,w. The nonlinear monomial map `q -> q XOR(u1*u2)`, with nonzero weight `2^(u1*u2)`, commutes with the central Gaussian and the w Gaussian, exercising both a nonlinear permutation and nonunitary weights. A diagonal `(-1)^(q*w*u1)` phase supplies a transported example where k can fail to preserve q-cosets while retaining the join partition. Exact support and inverses must be checked using the actual Gaussian matrix, not just a binary involution. Such examples can reject accidental affine/unitary/central-fixing restrictions; they do not replace the symbolic proof and are not required for this PASS.

No external writes were made. Original author and predecessor files were left unchanged. This review accepts only the stated theorem; research admission, overlap, publication, paid constructions and any next experiment remain with the parent task.

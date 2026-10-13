# Certified hybrid composition for exact matrix multiplication

Alejandro Zarzuelo Urdiales  
OpenMath; 7 October 2026. Author-review manuscript.

## Abstract

We describe an exact synthesis interface for matrix-multiplication circuits with different algebraic requirements at different levels. A bilinear outer identity is evaluated on matrix-valued blocks, while a possibly nonbilinear commutative circuit is used only on scalar entries. If the outer identity has $r_a$ products and the scalar leaf of order $b$ has $\ell_b$ scheduled products, their explicit composition computes order $ab$ with $r_a\ell_b$ scheduled multiplication gates. A second interface refines valid matrix-valued instruction programs, including transpose, while preserving their states, sharing and cost. The Lean development proves these constructions and closes the explicit order-16 count 2208 without unproved component premises. A denominator-cleared realization keeps its intermediates integral and uses guaranteed exact division by eight only at the outputs. Using the known commutative leaf bound $W(b)=b(b^2+2b-1)/2$ yields the general bound $r_aW(b)$; perfect squares are one specialization. We give comparison tests, factor-selection and arbitrary-order fringe statements, retaining the historical order-81 example and its separate certificate scope. Scheduled product counts, tensor rank, current optimality and measured speed remain distinct.

**Keywords:** exact matrix multiplication; arithmetic circuits; commutative algorithms; block composition; Lean; certified synthesis.

## 1. Contribution and prior work

Fixed-size multiplication counts remain useful in exact arithmetic when coefficient products are expensive. A circuit that exploits commutativity can save products by multiplying forms that mix entries of both input matrices. Such a circuit needs a different composition rule from a usual bilinear tensor decomposition. The scalar calculation and the matrix-valued block calculation must be separated explicitly.

This article develops the generalization in the author's July 2026 manuscript into a reproducible construction interface. Its central object is the assembled circuit, with its input maps, scalar products, output maps and exact schedule cardinality. The general composition argument is also a short mathematical proof, so the paper can be reviewed without reading the full Lean implementation.

Block composition and fringe reduction have substantial precedents in Drevet, Islam and Schost [DIS]. The commutative leaf formula and its division-free realization are due to Rosowski [R]; Waksman's earlier formulation uses division by two. Rosowski also gives specially structured nonbilinear algorithms that support recursion through transpose operations. Thus nonbilinear recursion is possible in appropriate frameworks. Our condition is narrower: the selected scalar leaf is not automatically a valid identity on arbitrary noncommuting blocks.

The 48-product rational outer identity belongs to Dumas, Pernet and Sedoglavic [DPS], and the cited 486-product ternary outer identity belongs to Perminov [P]. These are inputs to the synthesis theorem. We do not claim to have discovered those decompositions, the commutative leaf, or block multiplication. The contribution of the present revision is a precise construction and proof interface, its domain and cost discipline, and the explicit generalized synthesis and comparison statements. Independent mathematical priority for a numerical portfolio requires comparisons beyond the older DIS table.

## 2. Model and component certificates

Let $K$ be a commutative unital ring. Write $M_b(K)$ for the ring of $b\times b$ matrices. Fixed coefficient scales and linear combinations are recorded separately from multiplication gates whose inputs are computed from the matrix entries. This is an arithmetic-complexity model; it does not assign hardware latency to an operation.

An outer scheme of length $r$ is specified by coefficients $\alpha_{\rho ij},\beta_{\rho ij},\gamma_{ij\rho}\in K$. Define

$$
U_\rho(X)=\sum_{i,j<a}\alpha_{\rho ij}X_{ij},\qquad
V_\rho(Y)=\sum_{i,j<a}\beta_{\rho ij}Y_{ij}.
$$

For the required block size, its correctness certificate is the identity

$$
(XY)_{ij}=\sum_{\rho<r}\gamma_{ij\rho}U_\rho(X)V_\rho(Y),
\qquad X,Y\in M_a(M_b(K)).
\tag{1}
$$

Coefficients act centrally on the blocks and the order of the two factors in every product is retained. Scalar correctness alone is not substituted for (1). A standard bilinear coefficient/tensor certificate supplies this block-stability property after the usual central-coefficient lifting argument; that argument and any particular input certificate must be checked in their actual coefficient domain.

A scalar leaf has $\ell$ indexed products. Its left and right input forms $L_\lambda(A,B),R_\lambda(A,B)$ may use entries from both input matrices, and its output recombination is

$$
\operatorname{Leaf}(A,B)_{uv}
=\sum_{\lambda<\ell}w_{uv\lambda}
L_\lambda(A,B)R_\lambda(A,B).
\tag{2}
$$

Its separate certificate is $\operatorname{Leaf}(A,B)=AB$ for every $A,B\in M_b(K)$. The leaf is therefore a circuit for scalar matrix multiplication; it need not be a bilinear tensor decomposition. The multiplication schedule is the finite index set $\{0,\ldots,\ell-1\}$. Degenerate forms can produce constant or zero gates, so the schedule size always gives an upper bound on input-dependent products and is not an optimality assertion.

## 3. Explicit hybrid composition

Index an order-$ab$ matrix by pairs $(i,u)$ with $i<a,u<b$. The block map is

$$
\operatorname{blk}(A)_{ij}(u,v)=A_{(i,u),(j,v)}.
\tag{3}
$$

The inverse simply flattens the blocks. Distributing the ordinary matrix-product sum over the pair index gives

$$
\operatorname{blk}(AB)=\operatorname{blk}(A)\operatorname{blk}(B).
\tag{4}
$$

For each outer product $\rho$, form the two $b\times b$ scalar matrices $U_\rho(\operatorname{blk}(A))$ and $V_\rho(\operatorname{blk}(B))$. Apply the scalar leaf to these two matrices and recombine its outputs using $\gamma$. Every actual scalar product in the result has the explicit index $(\rho,\lambda)$.

**Theorem 1 (sound composition and scheduled cost).** Suppose the outer scheme satisfies (1) at block size $b$, and the leaf (2) is correct on $M_b(K)$. The constructed hybrid output is $AB$. Its scheduled multiplication-gate set has cardinality $r\ell$.

**Proof.** Leaf correctness replaces each constructed leaf output by the corresponding block product $U_\rho V_\rho$. The outer correctness identity then gives the block product of the two blocked inputs. Equation (4), followed by flattening, identifies this output with $AB$. All input and output transformations are fixed linear combinations. The remaining scheduled products are indexed by the Cartesian product of the two finite product index sets, whose cardinality is $r\ell$. No correctness or gate-count property of the desired hybrid circuit is used as a hypothesis. $\square$

The formal companion implements this construction over arbitrary commutative rings. Its component hypotheses refer to the outer scheme and scalar leaf separately. This is a normal compositional proof: it does not certify an arbitrary external scheme merely because the scheme declares a product count.

## 4. The scalar commutative leaf

Rosowski's square-matrix construction supplies the known bound

$$
W(b)=\frac{b(b^2+2b-1)}2,\qquad b\ge2.
\tag{5}
$$

For even $b$, the mechanism is transparent. Pair adjacent inner indices $u=2h,v=2h+1$. For a row $i$ and a noninitial output column $j$, define

$$
\begin{aligned}
P_{ih}&=a_{iu}(b_{u0}+a_{iv}),&
R_{ih}&=a_{iv}(b_{v0}-a_{iu}),\\
Q_{hj}&=b_{vj}(b_{u0}+b_{uj}),&
M_{ihj}&=(a_{iu}+b_{vj})(a_{iv}+b_{u0}+b_{uj}).
\end{aligned}
\tag{6}
$$

The initial output column is $\sum_h(P_{ih}+R_{ih})$; every other column is $\sum_h(M_{ihj}-P_{ih}-Q_{hj})$. Expanding these expressions in the commutative ring cancels the extraneous same-input products and leaves the ordinary two summands from each inner-index pair. The $Q$ products are shared across rows. The product families have sizes $b^2$, $b(b-1)/2$ and $b^2(b-1)/2$, whose sum is (5). The odd-order construction uses Rosowski's separate formulas rather than an unsupported leftover-pair argument.

At $b=4$, these four product families contain $8+8+6+24=46$ gates. This small leaf is useful as an explicit formal test of the mixed-input model. Commutativity is essential to its cancellation; applying the same formulas to arbitrary matrix-valued entries is not justified by the scalar proof.

**Corollary 2 (general factor composition).** An admissible outer scheme of order $a$ and length $r_a$, composed with a valid leaf of length $W(b)$, supplies an order-$ab$ multiplication circuit with scheduled cost

$$
H(a,b)=r_aW(b).
\tag{7}
$$

For perfect-square order $m^2$, choosing $a=b=m$ gives $r_mW(m)$. For unequal factors, reversing the two chosen sizes can change both the available coefficient domain and the cost. The synthesis theorem therefore does not privilege perfect squares.

## 5. Beyond bilinear outer stages

The outer stage can be specified by an instruction graph rather than bilinear coefficient arrays. Use input registers containing the two blocked matrices' entries or zero. Allow copying, addition, subtraction, fixed coefficient scaling, block transpose and block multiplication. Each instruction reads the current register state; chronology preserves sharing and operation order without expanding the graph into a tree.

**Theorem 3 (instruction refinement).** Suppose this outer graph has $r$ multiplication instructions and, when evaluated on actual $b\times b$ matrix blocks, correctly computes the outer matrix product. Replace each multiplication instruction by an actual product-vector evaluation of a correct scalar leaf of length $\ell$, followed by its fixed linear output recombination. The translated graph has the same register states at every chronological stage and the same matrix output. Its scheduled scalar multiplication count is $r\ell$.

**Proof.** Initially the register states agree. Copying, linear operations and transpose preserve this agreement. At a multiplication instruction, the leaf's scalar matrix-correctness theorem makes its reconstructed output equal to the original block product. Induction along the instruction list proves equality of all states and outputs. Each original multiplication instruction contributes one leaf product vector of length $\ell$; all other instructions contribute no new input-dependent multiplication gate. This gives the stated schedule count while retaining the original sharing and operation order. $\square$

The companion Lean theorem uses the correctness of the *unrefined* outer graph and the separate leaf as its component hypotheses, and derives the refined conclusion. Its transpose instruction is actual matrix transpose. This broadens the July bilinear-only synthesis interface to eligible nonbilinear outer programs, including the kind of involution-sensitive program studied by Rosowski. It does not prove that every commutative formula is a valid recursive outer program, or claim a new outer algorithm or improved exponent.

## 6. Comparisons and factor selection

For $a\ge1,b\ge2$, direct simplification gives

$$
\frac{H(a,b)}{(ab)^3}
=\frac{r_a}{a^3}\left(\frac12+\frac1b-\frac1{2b^2}\right).
\tag{8}
$$

Thus an outer count no worse than $a^3$ yields a strict saving from the classical cubic count. The direct commutative construction already improves on the cubic count, so it is a stronger initial comparator. The exact test against that construction is

$$
H(a,b)<W(ab)
\iff
r_a<\frac{a(a^2b^2+2ab-1)}{b^2+2b-1}.
\tag{9}
$$

At a perfect square, comparison to using the same outer scheme twice becomes $r_mW(m)<r_m^2$ exactly when $W(m)<r_m$, provided $r_m>0$. An independently specified baseline $B_{ab}$ is beaten precisely when $r_aW(b)<B_{ab}$; neither (8) nor (9) proves a current best-known result.

A catalog of certified outer circuits supplies a finite optimization problem. Enumerate admissible factor chains $n=d_1\cdots d_k$, use block-stable outer circuits at the first $k-1$ levels, and use the commutative scalar leaf at the last level. Each chain supplies the upper bound

$$
\left(\prod_{i<k}r_{d_i}\right)W(d_k).
\tag{10}
$$

The final leaf is the only level allowed to rely on its scalar commutative cancellation. Taking the smallest admissible recorded cost selects a witness circuit; it does not establish the globally smallest possible circuit. Domain compatibility, concrete component validity and a replayable factor lineage are part of every candidate, rather than annotations added after a count is selected.

| Order | Selected outer/leaf | Scheduled count | Comparison and scope |
|---|---|---:|---|
| 16 | rational outer $r_4=48$, leaf $W(4)=46$ | 2208 | 88 below $W(16)=2296$; requires the outer dyadic coefficients |
| 12 | Strassen outer $r_2=7$, leaf $W(6)=141$ | 987 | 15 below $W(12)=1002$; integer-coefficient outer |
| 81 | cited ternary outer $r_9=486$, leaf $W(9)=441$ | 214326 | 57915 below $W(81)=272241$; cited integer-coefficient certificate |

These are valid constructions in their specified models, not assertions of worldwide optimality. In particular, the familiar 2208-versus-2212 comparison concerns the historical DIS commutative table. The modern catalogs distinguish fields, commutative and bilinear models, explicit schemes and formula-only bounds [C]. A lower count in characteristic two is not automatically a rational-domain comparator.

A tempting additional factorization is to combine a reported 27-order outer count 10045 with the order-three commutative leaf count 21, giving 210945 for order 81. The downloaded LRP artifact currently has 10250 active products, with no zero or proportional ordered-product rows explaining the discrepancy. Its rational coefficients use denominators dividing 15. Consequently that advertised input has not been promoted to a verified new corollary here. Recovering the matching certified input is a concrete further research task, rather than evidence of a completed improvement.

## 7. An arbitrary-order fringe construction

**Theorem 4 (fringe bound).** Let a valid order-$p$ kernel have scheduled count $C_p\le p^3$, with $p\ge1$. For any $n\ge1$, let $q=\lfloor n/p\rfloor$. There is an order-$n$ circuit of scheduled cost

$$
F_p(n)=n^3-q^3(p^3-C_p).
\tag{11}
$$

When $C_p<p^3$, the construction strictly improves on the cubic count exactly when $q>0$, equivalently $n\ge p$.

**Proof.** Partition each index set into $q$ full groups of width $p$ and a final group of width $n-qp$ if it is nonempty. In the ordinary blocked product, exactly $q^3$ triples of block indices use full groups in all three positions. Replace each corresponding cubic $p$-block multiplication by the supplied kernel. Leave the remaining triples unchanged. The original scalar-product schedule has $n^3$ gates and every replacement saves $p^3-C_p$, proving (11). The output remains the ordinary block-sum matrix product. $\square$

With the order-16 kernel, (11) is $n^3-1888\lfloor n/16\rfloor^3$. It applies to prime orders too, without claiming that it beats every other commutative construction. For instance it gives 3025 at order 17, while the direct leaf gives 2737. Against that leaf the exact test is

$$
q^3(p^3-C_p)>\frac{n(n-1)^2}{2}.
\tag{12}
$$

Padding provides another candidate, but it must pay for the padded schedule unless zero simplification is actually performed. Equations (9), (11) and (12) allow a finite catalog to select exact-factor, fringe, direct or padded candidates under a common domain and cost model.

## 8. Integral intermediates and exact output quotients

The recovered 48-product input has integral left and right coefficient vectors; only its output coefficients require a common denominator eight. Replace those output coefficients by their integer numerators. The actual integer coefficient certificate then contracts to eight times the matrix-product target. Its lifting gives a denominator-cleared block output $8XY$ over every commutative ring, with no invertibility assumption.

Compose that numerator-valued outer stage with the explicit 46-product leaf. All input linear forms, products and output accumulations have integer coefficients. The resulting actual order-16 evaluator $N$ satisfies

$$
N(A,B)=8AB,
\qquad A,B\in M_{16}(K),
\tag{13}
$$

over every commutative unital ring $K$. This identity, including the supplied coefficient and leaf proofs, is now checked in Lean. At integer inputs, every output entry is divisible by eight and

$$
\operatorname{IntAlg}(A,B)_{ij}=N(A,B)_{ij}\mathbin{/}8=(AB)_{ij},
\qquad A,B\in M_{16}(\mathbb Z).
\tag{14}
$$

Here the quotient is exact integer division, including for negative outputs. The Lean theorem proves both the actual integer matrix product and the same 2208-slot multiplication schedule without assuming that two is a unit in the integers. There are 256 final fixed divisions. They are explicitly outside the variable-product count and must be included in an implementation's operation audit.

The same argument applies at order $4b$ when an actual correct integral leaf of order $b$ and length $\ell$ is provided: the numerator is eight times the product and the schedule has $48\ell$ products. This arbitrary-$b$ construction and exact integer quotient are also proved in Lean; leaf validity is its separate normal component hypothesis, and the desired numerator or final product is derived. With Rosowski's known leaf this gives $48W(b)$ integer products followed by $(4b)^2$ exact output quotients. This is a change in realization and arithmetic domain, rather than a new product-count or tensor-rank record. It addresses the July manuscript's restriction that the literal dyadic reference schedule need not keep integer inputs integral at intermediate stages. No runtime or bit-complexity improvement is inferred solely from moving the divisions.

## 9. Verification, numerical behavior and availability

**Review entry points.** The [immutable companion index](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/CURRENT_GUIDE.md) binds this manuscript to its actual proof sources. Start with [block composition](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/lean/BlockComposition.lean), [instruction refinement](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/lean/DAGRefinement.lean) and the [concrete order-16 theorem](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/lean/Concrete16.lean); then inspect the [integer output-division theorem](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/lean/IntegerLateDivision.lean) and its [arbitrary-size generalization](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/lean/IntegerGeneralization.lean). The [final 11-source/45-declaration manifest](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/lean/final_source_manifest.json) and its checker record exact hashes and endpoint scope. The [flat-circuit replay instructions](https://github.com/alejandrozu/openmath-2026-judging/blob/9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd/personal-matrix-hybrid-2026-10-07/circuit/README.md) offer a separate exact polynomial check. These links supply reviewable evidence without replacing the readable component hypotheses and proofs above.

The supplied original reference implementation of the order-16 circuit is pinned at `spicylemonade/faster_16x16`, revision `7743ee6848ed876615012c4edb3bc46a1f870afd`. The July audit independently checked the outer noncommuting polynomial identity, all 4096 output coefficients, the commutative leaf expansion and the multiplication schedule. It corrected the coefficient-domain wording and identified an unsafe integer-truncation comparison in the original verifier. Exact rational equality is the required comparison; truncating a rational output can conceal an error.

The integer ternary order-nine input is associated with revision `3183c54c754b60311edb1947417bc6060bc04db1`; the July record gives SHA-256 `6f8ee5d7e89221d2a63c702c0e42444387644c70e08a905bebab172f1033a2b6`. Its stated 531441 coefficient checks and integer domain belong to that retained audit. This revision does not relabel historical external checks as a new Lean replay.

The formal companion's actual checked scope is reported in its source/endpoint index and compiler receipts. The generic composition theorem uses outer block-correctness and scalar leaf-correctness as normal component inputs. Their desired hybrid conclusion and scheduled cardinality are derived. The particular 48-product input now also has an actual Lean proof of all 4096 denominator-cleared coefficient equations and their lifting to every block size over commutative rings in which two is invertible. The 486-product input retains its separate historical exact audit; the advertised 10045-product input is not certified here. The linked records distinguish component validation, generic synthesis and each concrete assembly.

**Concrete formal corollary.** The frozen nine-source core closes the order-16 assembly. For every commutative ring $K$ in which two is invertible and all actual $16\times16$ input matrices, the specified algorithm equals their matrix product and its scheduled gate count is 2208. This theorem has no external outer-validity, leaf-validity or coefficient-certificate hypothesis: those component facts are proved from the supplied data and explicit leaf. Its 35 selected declarations use only standard kernel axioms. The two additive integer modules close the numerator, fixed quotient and arbitrary-$b$ generalization, bringing the actual selected scope to 11 sources and 45 declarations. No admitted proof or native-evaluation axiom supplies these results.

An independent generator produces a sparse, fully flattened order-16 circuit with 2208 products in 512 input variables. Its left and right forms have integer coefficients and its 256 outputs have a common denominator eight. The separate verifier expands all 256 commutative quadratic output polynomials and checks them against eight times the ordinary matrix product. All 4096 expected mixed-input terms match and every same-input-bank term cancels. The certificate, generator, independent verifier and exclusive replay receipts are supplied. Their exact polynomial check took 1.14 seconds in the recorded run; that is verification time, not multiplication throughput or a formal proof of the generator itself.

| Result or artifact | Verification scope in this revision |
|---|---|
| Block and instruction-graph composition | General Lean theorem; separate component hypotheses; actual matrix output and scheduled cost derived |
| Paired-inner commutative leaf | General rectangular even-inner construction and explicit order-four bridge in Lean |
| 48-product outer identity | All 4096 integer coefficient equations and dyadic lifting to arbitrary block sizes proved in Lean |
| Concrete 2208-product circuit | Unconditional actual order-16 matrix theorem in Lean, under the commutative-ring/two-invertible domain |
| Integer numerator and final quotients | Actual all-ring $N=8AB$ identity and exact integer output-division algorithm proved in Lean; 2208 scheduled products plus 256 fixed quotients |
| General integer order $4b$ | Actual numerator and quotient construction in Lean from a separately valid $\ell$-product leaf; $48\ell$ scheduled products |
| Flat sparse JSON circuit | Independent exact integer polynomial check; generator itself is not asserted Lean verified |
| Universal odd-order leaf and 486-product input | Published/input mathematics and retained exact audit; not new full Lean ports |
| Arbitrary-order fringe construction | The readable constructive proof above; no full encoded fringe generator asserted |

The arithmetic count is also distinct from numerical accuracy. In the order-four leaf, taking $a_{00}=a_{01}=T$, $b_{00}=b_{10}=T^{-1}$ and other entries zero makes the relevant intermediate terms $1+T^2$ and $1-T^2$, whose exact sum is two. A floating-point implementation can lose the corrections before recombination. The exact proof therefore supports exact arithmetic without asserting a stable replacement for a conventional floating-point GEMM kernel.

For applications, additions, coefficient scales and movement must be counted alongside the saved products. The July literal order-16 schedule, after removal of zero initializations, records 2208 variable products, 16096 additions/subtractions and 5392 dyadic scales, versus 4096 products and 3840 additions in the classical schedule. Optimizing the linear network and testing an exact-arithmetic workload are appropriate next steps; a multiplication count alone does not establish latency or energy savings.

**Authorship and acknowledgements.** Alejandro Zarzuelo Urdiales authored the personal generalized review manuscript. The earlier concrete result and reference implementation were reported under Archivara Research Team and `spicylemonade`; their provenance is retained. The outer decompositions and commutative leaf retain the attribution given above. Codex AI assisted the present research synthesis, drafting and additive formalization; the author must review the mathematical text, references and contribution statement before submission. Alejandro also judged and evaluated OpenMath 2026 submissions in the event's Harvard/MIT community context. That judging role is separate from independent refereeing of this personal paper.

## References

[DIS] C.-E. Drevet, M. N. Islam and E. Schost, *Optimization techniques for small matrix multiplication*, Theoretical Computer Science 412 (2011), 2219-2236. [Publisher article and correct DOI](https://doi.org/10.1016/j.tcs.2010.12.012).

[R] A. Rosowski, *Fast commutative matrix algorithms*, Journal of Symbolic Computation 114 (2023), 302-321. [Earlier full-text version, arXiv:1904.07683v2](https://arxiv.org/abs/1904.07683v2).

[DPS] J.-G. Dumas, C. Pernet and A. Sedoglavic, *A non-commutative algorithm for multiplying 4x4 matrices using 48 non-complex multiplications*. [arXiv:2506.13242v7](https://arxiv.org/abs/2506.13242v7), 2026 revision.

[P] A. I. Perminov, *Meta Flip Graph meets Serendipitous Product: new Fast Matrix Multiplication results*. [arXiv:2606.02480](https://arxiv.org/abs/2606.02480); [primary algorithm repository](https://github.com/dronperminov/FastMatrixMultiplication).

[C] B. Chatain Lacelle, *A catalog of fast matrix multiplication algorithms with exhaustive derivations*. [arXiv:2606.13408v3](https://arxiv.org/abs/2606.13408v3). This is an independent comparator, not the author's repository.

[F] [FMM-Lille order-27 catalog entry](https://fmm.univ-lille.fr/27x27x27.html) and its linked coefficient artifact; the advertised-count/downloaded-schedule discrepancy is recorded in the supplementary research report.

[I] [Pinned original order-16 implementation](https://github.com/spicylemonade/faster_16x16/blob/7743ee6848ed876615012c4edb3bc46a1f870afd/main.py).

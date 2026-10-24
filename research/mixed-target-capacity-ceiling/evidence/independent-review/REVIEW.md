# Independent review of mixed-target input-encoding capacity

**PASS for the stated unchanged-provider contract**, including both the Clifford proof and the stronger arbitrary-monomial fixed-complete-product-support extension. At every sufficiently large column width, at most 112 of the 224 independent original main inputs can receive genuine rank-17 Gaussian jobs through the declared endpoint, FREE input encoding, FREE readout and saved-input bypass. Under the retained helper-completion and paid invoice, even granting rank 16 to every other main target makes the optimistic recursive moment strictly negative for every `0<C<1`.

Reviewed report SHA256: `11c0e2a054ac107ad605262f0c2ed3d3ab9ff3dbfc4fc7f0eadd17d1832462cc`, captured byte-for-byte as `frozen/REVIEWED-REPORT.md`. The scientific source is `4c0a359d88f22f05189d51f48387750b801a45d4`, actual `research/coded-native-caller`. Exact source/capture identities are in `SOURCES.json`. This is an independent written mathematical review plus a small exact scalar-data/invoice audit, with no author checker imported or executed.

## 1. Scope clarification found and repaired

The first reviewed wording required fixed finite columnwise complete-product support for controls, encoders, readouts and bypasses but described target entry/exit charts only as ordinary monomial charts. The formal coefficient projection also needs the target side in its finite union. The author repaired this: target entry and exit charts must themselves have fixed finite columnwise complete-product supports independent of f, or be the retained canonical native charts. Growing and noncolumnwise target-chart families are explicitly excluded.

The accepted result allows arbitrary mixing of both main banks at input, rectangular readout, arbitrary owned clean buffers, width-dependent outer scalar coefficients, a rank-deficient t0 and FREE access to saved original inputs. It does not require E to be FREE, does not assume U invertible, and does not import the earlier unchanged-original-feed obstruction. The independent original-owner Gaussian jobs, fixed address stock, first three control memberships and exact paid paths remain constraints. Fixed finite generating alphabets with unbounded width-dependent complete products are insufficient in the nonlinear extension.

## 2. Exact endpoint order and the source edge premise

Rightmost operators apply first. The negative bank is `-E G`, with

`E=Q^-1 C3 t C1 Q^-1`, `G=D1 D3 Q`.

Since D1, D3 and Q act on disjoint axes, `Q^-1 G=D1 D3` exactly. Expanding the two scalar owner codes therefore gives terms

`T=Q^-1 N3 k N1 D1 D3`,

where `N3=K3_i^-1 K3_r`, `N1=K1_s^-1 K1_j`, and the scalar coefficient contains `A[i,r] A[s,j]`. There is no replacement of Q by its inverse or by an operator involution.

For a nonzero right source edge, orthogonality of the actual G matrices gives

`a=N1 e_q=G1_s^-1 q_j`, `e_q dot a=q_s dot q_j=0`.

Thus a is nonzero and lies entirely in U. These are G rows used as rows. Signed phases do not affect this direction calculation. The independent scalar checker reconstructed every q directly from the first bit of each stored G row, checked the literal q masks, distinctness and orthogonality, and found exactly 5,824 nonzero source edges with zero dot-product exceptions. The source code is the old A, not the changed provider with diagonal 6/7.

## 3. Clifford negative-bank rank cut

For surviving transported Clifford k, the reviewed first-three-control theorem gives an invertible linear block R preserving W and `span(q)+W`. Hence `R^-T` preserves U, the annihilator of `span(q)+W` under the binary dot product.

The vector `(0,e_q)` lies in `D1 D3 L0`. Signed orthogonal N1 sends it to `(0,a)` with a nonzero in U; k sends it to `(0,R^-T a)`, still nonzero and in U. N3 and Q^-1 fix that vector because they act only on q+W. Thus `T L0` has nonzero intersection with L0 and T has Fourier rank at most 16. This pure-Z argument uses only the right edge. It does not assume k fixes the central direction after D3 transport.

The Clifford module argument also passes. At a sufficiently large width the finite projective Clifford class representatives have independent tensor lifts. The monomial span B is a finite-dimensional twisted group algebra, with cocycle factors raised to f. Projection to Fourier-rank-17 classes is a B-bimodule map. The negative bank, lower-rank target terms and FREE bypass vanish; the positive part factors through `B^112`. Each selected rank-17 target is invertible, so its action on B is injective. Comparing image dimensions `m dim(B)` and `112 dim(B)` gives `m<=112`. No semisimplicity or scalar-owner-rank substitution is necessary.

## 4. Nonlinear sparse-support argument

For arbitrary invertible monomial h satisfying the first three memberships after tensor separation, the previously reviewed support-partition lemma applies to `h Q=Q m` and `D3 h=k D3`. It makes h permute q-cosets and W-cosets, hence their `(q+W)` join blocks. Because D3 and its inverse act internally to those blocks, k permutes the same join blocks. Its induced U-coordinate permutation may be nonlinear; only its block bijectivity is used.

Every column of `D1 D3` is supported on one full q-coordinate hyperplane, with exactly `2^16` addresses. Under the orthogonal signed N1 this is the hyperplane `a dot x=c` with the same nonzero `a=N1 e_q` in U. It is therefore exactly half of the U-indexed join blocks, each of size `2^9`. The monomial k sends it to exactly half the join blocks. N3 and Q^-1 operate within those blocks and cannot populate a missing U block. Any cancellations only reduce the support. Every complete negative-bank term thus has at most `2^16` nonzeros in every one-column matrix column.

Left or right monomial multiplication preserves this per-column support upper bound, so arbitrary FREE input/readout factors do not change this classification term by term. In contrast, G has no zero matrix entries, and every member of its monomial double coset `H G H` is fully dense. Genuine rank-17 target jobs with the declared charts belong to that double coset. Canonical rank-at-most-16 Gaussian jobs, with the declared monomial charts, have at most `2^16` entries per column and do not belong. These are necessary support distinctions; the proof never equates every dense matrix with a member of `H G H`.

## 5. Project first; evaluate second

The potentially infinite monomial group creates no gap in the revised argument. Choose representatives of projective invertible one-column operator classes. Their products have scalar cocycles; using those cocycles to the power f gives an associative twisted algebra with evaluation `[g] -> g^(tensor f)` as a unital homomorphism. The proof needs coefficient faithfulness only on the fixed finite collection in the proposed identity, not on this entire infinite algebra.

At each sufficiently large f, finite tensor separation makes the proposed physical endpoint equality a coefficient identity in that formal algebra. Width-dependent owner coefficients are allowed; equal projective products are grouped with their correct f-dependent scalar factors. The finite union must include the proposed target charts, as the repaired report now says.

Projection onto the basis classes `H G H` is a bimodule map for the monomial algebra: left or right multiplication by H preserves that double coset and its complement. Thus all negative terms, FREE bypass terms and lower-rank target terms disappear. Every positive term is a monomial product on either side of G, so survives unchanged. Selecting the m target rows and their matching original input columns gives the formal identity in the correct order:

`diag(G_1,...,G_m) = L_positive t diag(G,...,G) U_positive`.

There are exactly 112 copies in the middle diagonal. Evaluating this already projected identity at the same sufficiently large width is legitimate. The target block diagonal has physical rank `m N_f` because each genuine target job is invertible on its original address field. The right side factors through 112 such fields and has rank at most `112 N_f`. Therefore `m<=112`. Common spectators multiply both dimensions by the same factor. There is no inference from raw data rank before projection, or from coefficient rank alone.

## 6. Ownership and scope of the factorization

The factorization concerns independent original main inputs, not coded mixtures credited as new jobs. The source has no main/helper leakage; the retained 816 helper endpoints are autonomous. With their paths unchanged, they are not additional observations of main inputs. The owned query bank is dependent workspace and receives no productive credit. FREE copies, clean scratch and saved-original access only change the encoder/readout or add the grade-zero bypass.

This requires the report's exclusion of separately available native history, extra paid observations and changed helper paths. Access to an additional paid Gaussian observation could supply another channel and would change the factorization. The result does not transfer to that model or to Dillon's separately held native-history mechanisms. Similarly, arbitrary new input encoding is allowed only within the declared FREE class and unchanged physical source endpoint; changing the source, target chart family or actual intermediate paid path is outside the theorem.

## 7. The complete optimistic invoice loses exactly

The retained native bill is `P0={1:2201,2:412,3:510,4:127,5:40}`. Two native bills, the 112 H1 query bank, and the rank-nine helper complements give

`P=2P0+112H1+94H1+14H2+56H5`

` ={1:4608,2:838,3:1020,4:254,5:136}`.

The two native helper banks have `94 H8`, `14 H7`, `56 H4` and `652 H9` jobs. Completing them gives exactly 816 H9 outputs, credited once; the earlier H4/H7/H8 rewards are replaced rather than retained additionally. This invoice is the declared retained completed-helper contract, not a universal comparison against altered helper invoices.

For `0<C<1`, `r^(1-C)` is increasing. At most 112 main jobs can be rank 17 and every remaining main job has rank at most 16, so

`T_actual <= T_max=112H17+112H16+816H9`.

Both this optimistic target and P have exact rank mass 11,040. Each target rank is at least 9, and each paid rank is at most 5. For positive C this gives

`T_actual(C) <= T_max(C) <= 11040*9^(-C) < 11040*5^(-C) <= P(C)`.

The upper bound on actual targets uses `C<1`; the strict support-gap inequality then uses `C>0`. At C=0 the optimistic masses tie and positivity still fails. No numerical root, finite-work credit, compiler reserve or inverse-transpose completion is needed to establish this necessary failure. Those additional costs cannot repair it.

## 8. Verification and limits

`check_evidence.py` independently reads the captured CODE.json and NORMALIZERS.json, checks the scientific SHA256 pins, reconstructs source directions and all supported-edge dot products, and reconstructs the exact invoice/mass and helper multiplicities. It imports none of the author's engines. Normal and optimized Python outputs are byte-identical. Rejection controls catch a newly nonzero diagonal edge, a duplicated direction, omission of the query bank, and granting a 113th H17 target while retaining only 111 H16 targets under the same mass budget. These controls validate scalar source/accounting premises only; they do not machine-check the symbolic capacity theorem.

No t0 solver, group enumeration, native/emitter/compiler/Lean campaign, moment scan, external write or source change was performed. The original report and all predecessor files were preserved. This review does not independently refresh upstream overlap or canonical main; those remain the separate monitor/root records. It accepts a source-bound ceiling within the declared contract, not a universal physical FREE obstruction, a construction, or a new kappa result.

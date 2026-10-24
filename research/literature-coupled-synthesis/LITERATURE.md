# Literature-to-code sweep: 25 primary papers

Each entry maps a paper technique to an executable, restricted adaptation on the pinned multiplication interface. This is not a claim to implement or reproduce the complete paper. `PAPERS.json` records primary links, method locators, access levels and temporary PDF hashes. Twenty entries have accessible primary method material (18 PDFs, one publisher-indexed method section and one author slide deck); five have only a primary bibliographic record or abstract. Their formulas are independently checked here, but their full texts were not reviewed. No paper PDF is redistributed.

All metrics below are regenerated in `RESULT.json`. The overarching construction choice and complete cost caps are in [SYNTHESIS.md](SYNTHESIS.md).

## P01: kalman62

R. E. Kalman (1962). [Canonical Structure of Linear Dynamical Systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC220821/).

**Technique adapted:** observable quotient and retained restoration directions.

**Implementation:** [experiments.py:kalman62](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** Observation rank 8 becomes rank 112 when arbitrary-original restoration is included.

**Construction decision:** Compress observation history; preserve all 112 independent originals.

**Reading and access:** decomposition into observable/reachable parts; bibliographic record only; primary bibliographic record/abstract; full text unavailable.

## P02: kalman63

R. E. Kalman (1963). [Mathematical Description of Linear Dynamical Systems](https://doi.org/10.1137/0301010).

**Technique adapted:** reachable/observable realization and Schur residual dimension.

**Implementation:** [experiments.py:kalman63](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The actual two-generation witness has 8 new residual directions and 16 independent test columns.

**Construction decision:** Keep generation-tagged latent state; an eight-mode stationary realization fails.

**Reading and access:** Sections 3-5, complete observability and canonical decomposition; primary PDF method sections.

## P03: ma26

Linkai Ma; Christos Boutsikas; Mehrdad Ghadiri; Petros Drineas (2026). [A Note on the Stability of the Sherman-Morrison-Woodbury Formula](https://arxiv.org/abs/2504.04554).

**Technique adapted:** inverse residual and conditioning, beyond symbolic invertibility.

**Implementation:** [experiments.py:ma26](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The capacitance is -13I; a coefficient error delta gives inverse error norm 56 delta and residual norm 728 delta. The small-update corollary does not apply.

**Construction decision:** Certify exact residuals and amplification; symbolic inversion alone is insufficient.

**Reading and access:** Introduction and Theorems 2 and 6; small-update hypotheses; primary PDF method sections.

## P04: sherman50

Jack Sherman; Winifred J. Morrison (1950). [Adjustment of an Inverse Matrix Corresponding to a Change in One Element of a Given Matrix](https://doi.org/10.1214/aoms/1177729893).

**Technique adapted:** rank-one inverse update.

**Implementation:** [experiments.py:sherman50](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The norm-56 single mode gives the exact inverse coefficient -1/52, checked by the rank-one product identity.

**Construction decision:** Use exact rank-one algebra for checks; no physical Gaussian disappears.

**Reading and access:** rank-one inverse update; publisher record only; primary bibliographic record/abstract; full text unavailable.

## P05: henderson81

H. V. Henderson; S. R. Searle (1981). [On Deriving the Inverse of a Sum of Matrices](https://doi.org/10.1137/1023004).

**Technique adapted:** rectangular Woodbury/Schur-complement inverse.

**Implementation:** [experiments.py:henderson81](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The full 112-column Woodbury product is identity, through an 8-dimensional capacitance matrix.

**Construction decision:** Low-rank inverse is algebraically closed; implementing it must still pay reads and restoration.

**Reading and access:** inverse-of-sum identity; publisher record only; primary bibliographic record/abstract; full text unavailable.

## P06: bennett73

Charles H. Bennett (1973). [Logical Reversibility of Computation](https://doi.org/10.1147/rd.176.0525).

**Technique adapted:** compute-copy-uncompute with original inputs retained.

**Implementation:** [experiments.py:bennett73](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The literal purchased-response exit checks 344 arbitrary inputs; deleting its first CLEAR is rejected. It pays 120 H1, 896 ADD, 464 monomial maps, 112 COPY and 224 CLEAR.

**Construction decision:** Retain an observation until its last use, then charge its actual cleanup.

**Reading and access:** compute, copy output, run backward; primary PDF method sections.

## P07: bennett89

Charles H. Bennett (1989). [Time/Space Trade-Offs for Reversible Computation](https://doi.org/10.1137/0218053).

**Technique adapted:** reversible pebble schedules and charged recomputation.

**Implementation:** [experiments.py:bennett89](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** Exact reversible pebbling on an eight-node path: four saved nodes need 25 moves, eight need 15; three cannot end cleanly.

**Construction decision:** Checkpointing trades retained observations for recomputation; every recomputed child stays paid.

**Reading and access:** reversible checkpoint/pebble time-space construction; primary PDF method sections.

## P08: buhrman14

Harry Buhrman; Richard Cleve; Michal Koucky; Bruno Loff; Florian Speelman (2014). [Computing with a Full Memory: Catalytic Space](https://doi.org/10.1145/2591796.2591874).

**Technique adapted:** transparent register updates on arbitrary dirty memory.

**Implementation:** [experiments.py:buhrman14](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** All 112 existing paid forward-bank query wrappers match common Q with absolute phase. Dirty difference needs two contacts, or one additional contact if same-version Qa survives.

**Construction decision:** Try versioned dirty observations at real paid sites; helper-bank xi does not equal arbitrary main Y.

**Reading and access:** Section 4.1 and Lemma 15; primary PDF method sections.

## P09: cook24

James Cook; Ian Mertz (2024). [Tree Evaluation Is in Space O(log n log log n)](https://doi.org/10.1145/3618260.3649664).

**Technique adapted:** finite-field interpolation and cancellation of catalytic nuisance values.

**Implementation:** [experiments.py:cook24](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** On actual M mode energies, dirty polynomial cancellation returns 3420 exactly. The root-of-unity probe over F17 returns 3 using four evaluations; rational quadratic extraction needs three.

**Construction decision:** Interpolation removes dirty dependence but introduces contacts; preserve source versions and charge every evaluation.

**Reading and access:** Section 3, Lemmas 7-8; roots of unity cancellation; primary author-repository PDF method sections.

## P10: hong81

Jia-Wei Hong; H. T. Kung (1981). [I/O Complexity: The Red-Blue Pebble Game](https://www.eecs.harvard.edu/~htk/publication/1981-stoc-hong-kung.pdf).

**Technique adapted:** explicit load/store and live-bank scheduling.

**Implementation:** [experiments.py:hong81](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The actual balanced program has LRU field reads/writes 1190/144 at capacity 8 and 120/120 at capacity 120. These are fixed-order upper bills.

**Construction decision:** Choose block order against measured residency; a scalar ADD saving is not yet a tape-motion saving.

**Reading and access:** red-blue evaluation game and I/O versus storage; primary PDF method sections.

## P11: schwartz23

Oded Schwartz; Noa Vaknin (2023). [Pebbling Game and Alternative Basis for High Performance Matrix Multiplication](https://doi.org/10.1137/22M1502719).

**Technique adapted:** joint basis-conversion and DAG scheduling.

**Implementation:** [experiments.py:schwartz23](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The 448-edge actual observation DAG can use eight accumulators and 112 source frame maps, or one accumulator and 448 maps with streaming or separate output storage. Eight observations still need initialization and return accounting.

**Construction decision:** Use eight resident accumulators when source maps are expensive; owned or borrowed state must be invoiced.

**Reading and access:** Section 4 pebbling rules and exhaustive schedule (indexed publisher text); primary publisher indexed method text; PDF download blocked.

## P12: karstadt20

Elaye Karstadt; Oded Schwartz (2020). [Matrix Multiplication, a Little Faster](https://doi.org/10.1145/3364504).

**Technique adapted:** recursive alternative-basis boundary fusion.

**Implementation:** [experiments.py:karstadt20](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** All 120 columns support common-frame whole-bank ADD and an involution. Sixteen compatible calls would need two endpoint conversions instead of 32; actual main-only ADD requires HPH instead.

**Construction decision:** Retain a common coupled type across compatible consumers; prove intervening thin queries in that type.

**Reading and access:** author SIAM AN17 slides, alternative-basis algorithms and recursive conversion; primary author conference slides for same work; journal full text unavailable.

## P13: schwartz26

Oded Schwartz; Sivan Toledo; Noa Vaknin; Gal Wiernik (2026). [Alternative Basis Matrix Multiplication Is Fast and Stable](https://doi.org/10.1007/s00211-026-01531-9).

**Technique adapted:** basis-dependent error growth and conversion accounting.

**Implementation:** [experiments.py:schwartz26](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The scratch-free H(-4,3) uses 1344 ADD, 16 SCALE and 240 monomial maps. Mode-block squared Frobenius norm improves from the prior PR4935 gauge's 898 to 688; the continuous optimum is 674.

**Construction decision:** Use the balanced scratch-free involution as a coupled boundary seed; prove precision through the full recursion.

**Reading and access:** Section 1.4 and Theorem 1.1, speed/stability and basis scaling; primary PDF method sections.

## P14: bini80

Dario Bini (1980). [Relations between Exact and Approximate Bilinear Algorithms. Applications](https://doi.org/10.1007/BF02575865).

**Technique adapted:** interpolation converts degree-d approximation to d+1 exact evaluations.

**Implementation:** [experiments.py:bini80](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** Degree-two exact recovery uses three evaluations with weights (3,-3,1), checking all 896 mode coefficients; weight one-norm is 7.

**Construction decision:** Exactify an approximate seed only after pricing evaluation multiplicity and precision; matrix-exponent overhead is not harmless here.

**Reading and access:** publisher abstract: exact recovery from degree-d approximation costs d+1 evaluations; primary bibliographic record/abstract; full text unavailable.

## P15: demmel07

James Demmel; Ioana Dumitriu; Olga Holtz; Robert Kleinberg (2007). [Fast Matrix Multiplication Is Stable](https://arxiv.org/abs/math/0603207).

**Technique adapted:** recursive coefficient-growth error recurrence.

**Implementation:** [experiments.py:demmel07](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** A deterministic actual complex Q / rounded / inverse-Q seam sends (1/3,0) to (1/2,0), leaving defect 1/6. Local independent-contact propagation gives bound 5441/4.

**Construction decision:** Track independent rounding contacts and coefficient growth; a formal inverse pair does not erase them.

**Reading and access:** normwise error propagation and recursive stability; primary PDF method sections.

## P16: dumitriu26

Ioana Dumitriu; Olga Holtz; Abraham Hsu; Nicholas Liskij; Yoav Moran; Ryan Schneider; Oded Schwartz; Shuncheng Yuan (2026). [Fast and Stable Arbitrary Precision Approximate Matrix Multiplication](https://arxiv.org/abs/2610.13905).

**Technique adapted:** nilpotent cyclic-filtration degeneration, trace screen, and dyadic exact recovery.

**Implementation:** [experiments.py:dumitriu26](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The native WZ cycle is non-nilpotent: trace powers are 8*14^k. A nilpotent three-factor positive control has 23 transformed entries all with positive exponent one. The balanced boundary has exact dyadic intermediate coefficient denominator at most 2^4.

**Construction decision:** Reject shrinking the whole non-nilpotent WZ cycle by similarity; separate exact grid recovery from leading recursive precision.

**Reading and access:** Theorems 2.1-2.2 nilpotent cyclic filtration; exact recovery and precision sections; primary PDF method sections.

## P17: ballard16

Grey Ballard; Austin R. Benson; Alex Druinsky; Benjamin Lipshitz; Oded Schwartz (2016). [Improving the Numerical Stability of Fast Matrix Multiplication](https://arxiv.org/abs/1507.00687).

**Technique adapted:** diagonal scaling and tighter coefficient accumulation bounds.

**Implementation:** [experiments.py:ballard16](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** In the seven tested gauges, scalar row-sum bound is 69 at the norm-equivalent prior PR4935 gauge (-6,2), 97 at (-4,3) and 50 at (-12,1). The value 349 at (-1,12) is an unbalanced reference, not the prior implementation baseline. The compiler metric decides the useful gauge. A transposed program for (-12,1) uses only dyadic constants, 1344 ADDs and eight sign SCALEs, without scratch.

**Construction decision:** Optimize the precision metric used by the compiler; the 2-norm-optimal gauge need not minimize row-sum error.

**Reading and access:** diagonal scaling and coefficient growth; primary PDF method sections.

## P18: dehaene03

Jeroen Dehaene; Bart De Moor (2003). [Clifford Group, Stabilizer States, and Linear and Quadratic Operations over GF(2)](https://arxiv.org/abs/quant-ph/0304125).

**Technique adapted:** binary symplectic plus quadratic-phase exact operator representation.

**Implementation:** [experiments.py:dehaene03](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** All 120 source port/mode tableaux preserve the symplectic form, checking 324 Pauli-generator pairs each.

**Construction decision:** Use binary symplectic forms to search composable frames, with a separate absolute-phase witness.

**Reading and access:** binary symplectic and quadratic-form representation; primary PDF method sections.

## P19: aaronson04

Scott Aaronson; Daniel Gottesman (2004). [Improved Simulation of Stabilizer Circuits](https://arxiv.org/abs/quant-ph/0406196).

**Technique adapted:** tableau propagation and stabilizer state comparison.

**Implementation:** [experiments.py:aaronson04](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** All 120 frames have exact zero-state phase anchors; a global-i mutation keeps the tableau but changes the anchored state and is rejected.

**Construction decision:** Tableau plus one anchored state authenticates Clifford phase; tableau equality alone is inadequate.

**Reading and access:** stabilizer tableaux and state representation; primary PDF method sections.

## P20: patel08

Ketan N. Patel; Igor L. Markov; John P. Hayes (2008). [Optimal Synthesis of Linear Reversible Circuits](https://arxiv.org/abs/quant-ph/0302002).

**Technique adapted:** blocked binary elimination and shared row-pattern elimination.

**Implementation:** [experiments.py:patel08](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** On 112 actual 9-by-9 wrapper matrices, scalar Gauss-Jordan needs 2587 CNOTs; choosing panel widths 1..4 per matrix uses 2350. Physical field-volume cost remains.

**Construction decision:** Apply panel elimination to ordinary wrapper synthesis; it cannot merge independent physical field volumes.

**Reading and access:** panel/duplicate-pattern elimination for reversible linear circuits; primary PDF method sections.

## P21: amy14

Matthew Amy; Dmitri Maslov; Michele Mosca (2014). [Polynomial-time T-depth Optimization of Clifford+T Circuits via Matroid Partitioning](https://arxiv.org/abs/1303.2042).

**Technique adapted:** linear-independence matroid partition of phase/readout forms.

**Implementation:** [experiments.py:amy14](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** A feasible greedy independent-form partition has 14 batches versus dimension lower bound 13. No optimality or Gaussian-call saving is claimed.

**Construction decision:** Batch independent phase/readout forms for ordinary scheduling; each independent payload remains a separate volume.

**Reading and access:** matroid partition of linear phase forms; primary PDF method sections.

## P22: bravyi21

Sergey Bravyi; Dmitri Maslov (2021). [Hadamard-free Circuits Expose the Structure of the Clifford Group](https://arxiv.org/abs/2003.09412).

**Technique adapted:** Hadamard-free double-coset flags and canonical structure.

**Implementation:** [experiments.py:bravyi21](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** All 112 actual Kp_i Q columns have distinct right monomial cosets; an identical-column positive control has one group. This excludes one shared Gaussian after monomial aggregation.

**Construction decision:** Reject one-Gaussian-after-monomial-aggregation for this source; seek a two-sided or endogenous observer.

**Reading and access:** Hadamard-free subgroup and canonical decomposition; primary PDF method sections.

## P23: maslov18

Dmitri Maslov; Martin Roetteler (2018). [Shorter Stabilizer Circuits via Bruhat Decomposition and Quantum Circuit Transformations](https://arxiv.org/abs/1705.09176).

**Technique adapted:** minimal Hadamard layer and monomial-Gaussian-monomial factorization.

**Implementation:** [experiments.py:maslov18](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** All 6216 pairs have rank_B(Ej^-1 Ei)=2 and rank_B(Ei Ej^-1)=0, exposing the orientation distinction needed for two-sided boundary cancellation.

**Construction decision:** Cancel compatible two-sided boundaries in the correct order; independent inputs still pay physical volume.

**Reading and access:** Bruhat and two-sided layer decomposition; primary PDF method sections.

## P24: edelman98

Alan Edelman; T. A. Arias; Steven T. Smith (1998). [The Geometry of Algorithms with Orthogonality Constraints](https://arxiv.org/abs/physics/9806030).

**Technique adapted:** Grassmann subspace geometry, basis-invariant residuals.

**Implementation:** [experiments.py:edelman98](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The exact physical residual has rank 8 and determinant 1389039784345493055/26985857024; a unimodular mode-basis change preserves both.

**Construction decision:** A mode-basis search cannot repair a subspace mismatch; change the observable state or the contact.

**Reading and access:** subspaces, orthogonal projections and invariant geometry; primary PDF method sections.

## P25: kailath79

Thomas Kailath; Sun-Yuan Kung; Martin Morf (1979). [Displacement Ranks of Matrices and Linear Equations](https://doi.org/10.1016/0022-247X(79)90124-0).

**Technique adapted:** low-rank displacement generators and composition.

**Implementation:** [experiments.py:kailath79](experiments.py), using the shared exact engines in [algebra.py](algebra.py).

**Executed finding:** The cross-chart displacement has 16 operator-generator blocks. Its action on all eight actual witness inputs has Gram 196G and first entry 2422; generators are not scalar call credits.

**Construction decision:** Carry chart displacement generators with generation tags, then solve their legal readout and termination.

**Reading and access:** publisher abstract: displacement rank under operator structure; primary bibliographic record/abstract; full text unavailable.

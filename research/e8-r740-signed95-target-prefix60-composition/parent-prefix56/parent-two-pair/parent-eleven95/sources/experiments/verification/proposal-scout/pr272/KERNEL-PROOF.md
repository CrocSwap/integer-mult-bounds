# Collective response-kernel condensation: sufficient rewrite

Fix a checkpoint before any chosen helper is modified, after its initial target-correction reads. Let C be the selected helpers' complete accumulated prefix response into target data, and R their full suffix response into target data, over F2. Require that target input perturbations remain confined to targets through the prefix, with an invertible target matrix A. Correctness of the old scalar word then forces the suffix target-input block to be A^-1 on targets and zero on helpers, so R=A^-1 C. The selected helper prefix columns must consist only of their own unchanged helper value plus C: in particular there are no prefix reads of these helpers into another helper. No selected helper is a copied/source-owned role. These are actual trace prerequisites, not conclusions of a response hash. Target-to-target prefix changes are allowed.

Partition chosen helper coordinates into pivots P and donors D. Choose kernel vectors v_p=e_p+sum_(d in D) a_dp e_d, with Rv_p=0 and no other pivot coordinate in v_p. Put N e_p=sum_d a_dp e_d and N e_d=0. Thus N²=0 and Q=I+N is invertible. Q^-1=I-N over the integer gate presentation; over F2 signs coincide. Each nonzero a_dp is one paid ADD donor_d += a_dp*pivot_p. The gates commute because a destination is never a source pivot. Distinct pivots may use the same donor without changing this fact.

Remove the old initial target-correction reads from the pivot helpers only. At the checkpoint apply Q. Run the unchanged scalar suffix, including actual copied-center lifetimes. At its final full helper frame apply Q^-1. The suffix helper block is identity, so the final helper vector is exactly the original one. Each donor's old accumulated target correction still cancels R e_d. Removing all initial pivot correction reads removes precisely C e_p at the checkpoint; each pivot now contributes zero because this correction is absent and RQe_p=Rv_p=0. Input data behavior is unchanged. This proves correctness for all scalar inputs over F2, including arbitrary dirty-helper correlations. It does not assert the same cancellation over Z; the implementation still retains actual integer ADD coefficients for address/cost analysis.

For physical legality, require every forward gate's endpoints to share a nondegenerate frame E contained in every affected helper's first positive frame. Give each pivot initial frame E; the donors retain zero entrance and move to E for the paid Q gates. The original future frame chains remain legal by containment. Q^-1 occurs at the final full frame. Normalizer charts must be supplied for every actual pivot residual I-sigma_E. When all frame moves remain nested and no COPY ownership changes, telescoping dimensions give raw movement-rank saving dim(E) per pivot; histograms and ADD invoices must still be recomputed from the literal word. The exponent requires the separate exact moment and outer-assembly checks.

## Eight actual Pasch components

The32 saved triple relations form8 groups, each with6 helper roles and4 triples. Label three of the triples

  (a,b,c), (a,d,e), (f,b,e).

The fourth is their F2 sum. Choose pivots c,d,f and donors a,b,e. The six required forward gates are

  a+=c; b+=c; a+=d; e+=d; b+=f; e+=f.

All commute, and their integer inverse subtracts the same contributions. The three response-kernel columns have unique pivots, so all three entrances are exposed simultaneously; disjoint-support matching would expose only one.

The exact C++ rank check `pasch-intersection.cpp` reads the literal first positive frames from the pinned249 event stream. For every component, it verifies that the intersection of all6 first frames has dimension equal to the union of the4 candidate frame bases: respectively4,3,5,9,9,9,12,14. Thus each component admits its full common entrance E for all three pivots. This removes a potential geometric obstruction to shared donors; it is stronger than counting independent scalar relations.

Three pivots per component give total entrance rank195 rather than65. Combined with the existing132 pair pivots this is327, divisible by3, so the unchanged40-replica bank construction applies without dropping any pairs. Predicted literal stock is868870, normalized173774. These are construction formulas, not a final price receipt: the collective literal word and the combined source-bound bank checker must pass before composition.

## Sufficient compatibility beyond disjoint blocks

Disjoint support between selected kernel blocks is stronger than necessary. A sufficient combination rule is: every pivot is unique and belongs to no selected donor set; for each shared donor, all entrance subspaces of blocks using it form a chain under exact subspace inclusion. Each block's entrance is contained in the first positive frames of its own pivots and donors.

Order the forward kernel blocks by increasing entrance dimension. On any shared donor, this visits its chain monotonically; every pivot appears in just its own block. Therefore all paid gates are physically legal and lead into the original first positive frames. The same N²=0 proof applies because no destination donor is ever a pivot source, even across blocks. Gates with the same donor commute as usual. The inverse gates take place at full frames, where their order is unrestricted. This admits compatible nested-frame donor overlaps that disjoint-support packing rejects, without requiring a new address compiler. Actual histograms and simultaneous weighted-kernel independence remain subject to literal word replay; no estimated gains are added.

Turyn full-port labels and scoped cost budgets
=============================================

This package lets labels vary across the eight high lines previously
grouped into each glue class. It uses the same 23,040 actual Turyn ports
and real rank 512 tensor kernel. No improved kappa or complete scalar
supplier is claimed. Arbitrary global full-port binary labels remain open.

The included exact results are:

* No choice of block signs repairs the natural 25-dimensional Leech map.
  Four actual edges contradict even independent source and target signs.
* Arbitrary profile-dependent linear maps of the full 25 affine Leech
  coordinates still require fitting rank 27. Finite edge witnesses force
  zero cross-profile Gram blocks and rank 9 within each profile.
* A larger family combines independent affine glue maps for each high
  line with all quadratic glue features, giving 168 features per profile.
  Finite constraints force a 60-port restriction to satisfy a nine-clique
  parity certificate, again requiring symmetric binary fitting rank 27.
* Each full profile needs at least nine symmetric binary label dimensions,
  even with arbitrary nonlinear dependence on the high line. A 24-port
  witness is exhausted in 43 search nodes; cyclic copies cover all three
  profiles. The known labels attain nine. This does not sum to a global
  bound unless the three profile spans are mutually orthogonal.
* With the existing 27-bit labels, every nonzero real linear tensor
  encoder has label-support rank 27. Hence real basis changes and
  rank-minimal 512-feature factorizations retain an encoder bill of at
  least 13,824. Redundant encoders outside the tensor column space are
  outside this bound.

The inherited controller's no-helper full-port screen gives nominal
kappa about 0.00142213, below the pinned PR592 claim. This is a scoped
accounting result, not a universal obstruction at binary dimension 27.
Different controllers, helper hosting, label maps, or redundant real
factorizations must be charged separately. COSTS.txt records the exact
assumptions and useful budgets; PROOF.txt explains the finite certificates.

Replay with Python >= 3.10 and NumPy:

    python3 -I research/turyn-port-labels/verify.py

Use --output DIRECTORY to save the deterministic combined receipt, or
--check-pins for package and inherited-source hashes only. Python -O is
supported: verification uses explicit checks. No SAT solver is required.
The verifier constructs the ports and checks the recorded finite edges;
it does not build the full pairwise graph or audit a new proposed labeling.

The frozen research/leech-lattice package is imported without changes and
pinned by file hashes. The new package is pinned by MANIFEST.json. PR592
and PR595 metadata are retained at exact heads as comparison sources;
neither supplier nor PR595's complete structural analysis is replayed here.

A successful new supplier still needs an exact binary fitting map, a
charged scalar encoder circuit, a complete controller and helper invoice,
and all inherited outer checks. Nominal budget headroom alone is not a
new exponent result.

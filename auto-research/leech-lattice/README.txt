Leech lattice and Turyn construction experiments
================================================

No improved kappa is claimed. This package starts from upstream main
7dfa22b and compares with PR588 at
6d0e53b66c29abd17981881a09eaff41ac862d85. That PR declares conditional
kappa=0.001602278921983212; its supplier was not freshly replayed here.

The main result is an exact test of Turyn's construction, including an
explicit transform to another space and back. The 24-dimensional lattice
is constructed from two polarized 8-bit Hamming codes. Its three-block
minimal vectors yield 23,040 canonical tensor ports and a real rank-512
kernel. Each of its three 7,680-port profiles has a valid 9-bit fit.

Within each profile, however, 64 ports share each E8 root and binary label.
Their remaining-block tensors form an orthogonal basis. The recorded
dyadic basis changes reduce the complete normalized scalar kernel to
G_E8 tensor I_64. Thus this particular Turyn construction is exactly
64 copies of E8 in different bases, rather than a larger exponent gain.

Combining the profiles shares 512 real centers. Their fixed 9-bit fits
require disjoint binary spaces: for every pair of profiles, 81 active
edge constraints independently force all 81 entries of a cross-Gram
matrix to zero. This proves a 27-dimensional requirement only for linear
overlaps of the three fixed rank9 label maps. A representation with extra
radical components, different labels, or another scalar kernel is outside
this result.

Other retained experiments:

* The full Leech shell has 98,280 lines and an explicit 25-bit fit for
  the normalized cubic kernel (t^3-4t)/48. A 2,600-center dyadic
  factorization is supplied. Every literal encoder support spans all
  25 bits, so its center bill is 65,000 in the existing interface.
* Norm-six directions give a rational basis of 2,600 cubic encoders
  with support rank24. A modular independence certificate and explicit
  support witnesses are included. A dyadic decoder and complete scalar
  word for this alternative have not been constructed.
* Exact, deliberately optimistic moment comparisons and their limits
  are recorded in COSTS.txt and evidence/SCREEN.json. Relaxation
  headroom is not a constructed gain.

Reproduce with Python and NumPy:

    python3 research/leech-lattice/verify.py

The runner generates arrays in a temporary directory, checks the
committed deterministic receipts, and exercises corruption controls.
Use --output DIRECTORY to retain the generated arrays and logs.
Checks use explicit exceptions and also run under python -O.

The package changes no production supplier, selected certificate, or
earlier research package. It does not establish worst-case O(1)
indexing. No code-review workflow or numerical-improvement PR was run.

See PROOF.txt, TURYN.txt, COSTS.txt, NOTICE, and sources/ for details,
attribution, and the distinction between tested constructions and open
directions.

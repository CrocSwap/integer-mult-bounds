# Independent reconstruction and proof review

Prepared for @CubeJerry with substantial OpenAI assistance. These were separate
OpenAI-agent investigations, not external human or proof-kernel reviews.

## Independent computational reconstruction

Worker A first rebuilt the #6824 native word through the retained #6833
constructor and checked the canonical payload against the pinned export. Its
native improvement searches found no priced witness. It then wrote
`independent_audit.py` without importing the primary checker, discovery code or
predecessor checker, and without reading the frozen certificate.

The independent method reconstructs each register's complete event trace,
checks all 1,278 × 15,072 ordered deletion/compensator possibilities, solves
full sparse boundary outer-product equations, and uses sparse Gaussian
elimination on each complete changed public matrix. It does not use the
primary direction buckets, normalized one-scalar formula, or rank-two
determinant witness.

It independently found 1,466 visits, 1,278 deleted ADDs, 172 compatible pairs
(103 with both derivatives nonzero and 69 zero-derivative cases), 157
inconsistent equations and 15 singular maps. Every singular map has exact
rank 771. All 15 event/coefficient triples agree with the primary result.
`INDEPENDENT-AUDIT.json` records that reconstruction, including independent
kernel vectors and a diagnostic local runtime. The exact source digest is
checked by both implementations.

Worker A also proposed the reverse-transpose positive control for the earlier
zero-output compensator, twelve identity checks with nonzero COPY overwrite,
and mutations of all 15 actual null witnesses. These controls were integrated
into the primary checker using explicit exceptions. The independent algorithm
was copied unchanged apart from additional explicit guards on its reproduced
census and rank 771.

## Separate mathematical review

Worker B read the complete PROOF, primary verifier, README, certificate and
source pins, and ran the primary replay successfully. It independently checked
all cases of the two-event expansion and direction filter, including the
ordering-dependent zero-derivative cases, the rational equation solving, and
the determinant-to-literal-null-vector argument.

It also read the pinned #6835 PROOF §3.4 and `verify.check_hub` to check the
actual pre/middle/post factorization. It identified a useful clarification:
the replaceable hub parts are not simply every event at a zero/full frame.
The final proof states the disjoint-register commutation, self-contained post
private lifetimes, and invertibility argument explicitly. No mathematical
defect was found in the scoped theorem.

## Joint extension for deletion 10947

The joint extension was developed after the complete two-coefficient class
was closed. It fixes deletion 10947 and solves two further coefficients
together. It does not first choose a singular one-compensator repair or
claim the larger domain for all deletions.

Worker C reconstructed the deleted baseline, its inverse, every direction
class and all 46,381 pair equations. It simplified the residual certificate
to 2,012 fixed-first-coefficient and 936 fixed-second-coefficient identities;
there is no general nonlinear solver in the primary extension checker.
Fourteen literal endpoint/null-vector checks, an omitted mixed-term
corruption, and a successful small joint-repair control pass.

Worker B independently derived the rank-screen necessity and determinant
formula, checked every residual coordinate-line identity and all four
one-compensator corners, and wrote the companion proof. The lead read the
full proof and production verifier and found no defect. The lead also
independently reconstructed the pair domain using direct sparse span/rank
tests, sharing only the scalar replay primitives. Its 23,101 column-common
and 23,280 additional row-common pairs have the same canonical domain hash
as the primary and independent reconstructions.

Worker A then wrote `independent_joint_audit.py` without importing the
primary checker, joint checker or predecessor code, and without reading
the frozen boundary equations or determinant coefficients. It uses its
own native replay and adjoint, obtains the deleted public inverse by full
772-row Gaussian elimination, and rebuilds all transfers and expanded
boundary-coordinate equations. It independently reproduces the complete
99 / 43,334 / 2,012 / 936 partition and all four zero-change cases.

Its literal controls also compare exact full-matrix determinants at
nondyadic coefficient choices, check singular C1 solutions and their null
vectors, reject a corrupted transfer, and accept a repairable parallel-ADD
example. `JOINT-INDEPENDENT-AUDIT.json` records the compact result and exact
equation/determinant stream hashes. The optional detailed report can be
regenerated from the independent checker.

The proof distinguishes supported endpoint wrappers from replacing actual
hub parts. When a compensator is inside a replaceable hub, absorption
reduces the claim to the verified one-compensator or deletion-only case;
no inverse of a singular retuned hub is used.

## Limits of the review

The new exact result excludes only the declared finite source and edit class.
The exploratory input/output lift and changed-frame searches are not
certificates and are not additional claims of this package. The selected
frontier, complete supplier, compiler, precision tape and analytic recovery
were not replayed here. Full-history source ancestry is not claimed from the
shallow checkout. Standard metadata and committed-byte checks complement this
review but are not mathematical acceptance.

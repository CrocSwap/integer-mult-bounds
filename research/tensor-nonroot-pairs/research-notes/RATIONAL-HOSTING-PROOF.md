# Rational non-root entrances with whole-owner hosting

## What is proved

For every rational subspace E of rational Euclidean n-space, four copies of E and of its orthogonal complement admit explicit rational orthonormal bases. There is a rational orthogonal matrix G of size 4n which sends the four residual spaces into mutually orthogonal subspaces of one coordinate block of dimension 4(n-dim E). These residuals can be hosted, whole, in ONE pending child of ONE physical family. The remaining 4 dim E coordinates must be available in that same family as restored spectators. This is a sufficient local route theorem, not a claimed global multiplication bound.

For suitable forms two copies suffice. The concrete newly discovered non-root line E=span(0,0,1,1,0,0,0,0) has a fully checked two-copy route: one pending block of rank14, two spectator coordinates, and 32 elementary address operations in each direction. This line is not among the stored120 E8 root lines. Geometric first-touch intersections can expose it even where intersection of root LABEL sets is empty.

## Exact construction and proof

Use rational Gram-Schmidt to obtain orthogonal bases v_i of E and E-perp. For every nonzero v let a=v.v>0. Write a=p/q in lowest terms. Lagrange's four-square identity supplies integers z_0,...,z_3 with sum z_i^2=pq, hence rationals h_i=z_i/q with sum h_i^2=a. The quaternion matrix

H = [[h0,-h1,-h2,-h3], [h1,h0,-h3,h2],
     [h2,h3,h0,-h1], [h3,-h2,h1,h0]]

satisfies HH^T=aI4. Four copies of v, combined using rows of H/a, therefore have Gram matrix I4. Vectors arising from different v_i remain orthogonal. Listing residual vectors before entrance vectors gives G with GG^T=I. Its inverse is its transpose. No square root is used.

If a=x^2+y^2 with x,y rational for EVERY pivot in this chosen orthogonal basis, the same proof with [[x,-y],[y,x]] gives a two-copy construction. Failure of that particular two-copy test is not a proof that no two-copy isometry exists. Four copies always work. The explicit non-root line above and its complement have pivots1 or2, so the two-copy criterion holds.

Let P be the orthogonal projector onto E-perp and B_j its placement in copy j. Set U_j=G B_j G^T. Then U_j^2=U_j=U_j^T, rank(U_j)=n-dim E, U_i U_j=0 for i!=j, and sum U_j=diag(I_(c(n-dim E)),0_(c dim E)), where c=2 or4. Each U_j is one intact residual. No U_j is distributed across distinct owner families.

For the corresponding involutions, the exact product identity

product_j (I-2U_j) = I-2 sum_j U_j

shows that the orthogonal residual factors multiply to the pending coordinate child. This is precisely the operator identity missing from a cross-family direct-sum split. The source helper theorem must be pulled through each full G-bound map, including the entrance directions and arbitrary dirty residual inputs. Disjoint coordinate SUPPORT is unnecessary; orthogonal projectors are the relevant invariant.

All matrices are rational. Gaussian elimination gives a literal finite sequence of swap, scale, and row-add factors reducing G to I. Exclude every prime dividing a denominator in G or these factors, and every numerator of a scale that must be inverted. Reduction modulo every remaining prime, and extension to every field of that characteristic, preserves all matrix equalities and invertibility. The finite list must be tied to the frozen selected frame witness. It is not a q-dependent oracle or a probabilistic solver.

## Paid invoice and exact admission boundary

For a c-copy route in n dimensions, the local footprint is cn. Its active pending block needs c(n-e) dimensions and its spectators need ce dimensions, all in the SAME physical family and the SAME chronological idle window. The full local operations must restore spectators before that window ends. Each original helper residual remains whole in this owner. Schedule and owner compatibility are genuine requirements; the local matrix theorem does not manufacture them.

A concrete Gaussian sequence has at most N^2+N operations for N=cn, and the forward/backward route has at most2N^2+2N. The sample pair has32 operations per direction,64 round-trip, footprint16, active14, spectators2. The sample rank2 quartet has127 per direction,254 round-trip, footprint32, active24, spectators8.

To price a selected global word, charge these actual operations per routed occurrence, including the duplicated map on both address halves, all entry/exit uses, and the existing array permutation primitive. An elementary invertible address operation can be evaluated over the field and gives a bijective permutation of the full q^(2m) array. A conservative explicit out-of-place realization scans all addresses, computes the changed coordinates, and scatters once; it needs q^(2m) coefficient cells and O(q^(2m) poly(m,log q)) bit work per elementary factor with the project field arithmetic. This observation is an implementation, but it is NOT a claim that this larger workspace/toll is already accepted by the current in-place compiler contract. If the inherited reversible permutation primitive is used instead, its exact source-bound cost and scratch bound must be included. Neither implementation has been globally invoiced here.

The current shipped bank_routes.py validator permits only coordinate-root rows and at most7 swaps. Thus this witness needs an explicit validator/compiler extension; it is not a drop-in certificate accepted by the old narrow checker. A sufficient completion is: install the complete rational maps and their inverse factors, extend the provider audit to verify the U_j equalities, exhibit an owner/window allocation, replay all changed local columns, and add the literal route costs to the existing assembly. No unknown gadget is posited by this list: the concrete route matrices are present, while the global algorithm has not been built.

## Capacity screen for the0.0014 target

Width7 singleton windows cannot host a pair of rank7 residuals, since the pair needs14 pending coordinates and two same-family spectators. A quartet needs28 plus4 spectators. It is invalid to sum capacity across unrelated width7 families. A rank56 pending window can fit four pairs or two quartets by pending width, provided its physical family has the required spectator capacity and the selected occurrences are coeval. If each pair/quartet needs separate spectator coordinates simultaneously, the full footprints must also be counted. A coordinate or sum-of-two-squares residual can still use the smaller admitted multiplicity; no uniform fourfold replication is required.

For an optimistic target screen, use the exact existing moment equation sum_r n_r r((m/r)^b-1)=D. Replace only genuinely removed children, preserving the selected rank/deficit ledger, and evaluate at b sufficient for kappa0.0014. This yields an upper bound before scheduling. A number of abstract null vectors or eligible carriers is not itself a child-removal count. PR485's586 upper nullity is not a realizable new gain: the current source screen finds only16 additional non-coordinate ROOT-line kernel dimensions. The newly discovered geometric non-root intersections remain to be counted modulo the already-used prefix.

## Reproduction and scope

quaternion_route.py constructs the exact witness. Its construct(roots,frame,copies=2,basis=[...]) entry accepts an explicit rational basis; copies=4 is the universal fallback. four_squares uses a finite pair-sum search suitable for the frozen small frames; no efficient general binary integer factoring/four-square theorem is claimed.

NONROOT-LINE-PAIR.json binds source word SHA25686ec5a244728e90714d545d0ecb8557346577f9e5c4a265b1cad844398ba4f02. Its conservative excluded-prime set is{2,3};3 appears from the optional reflection factorization, so a pared-down selected route may admit more primes, but the saved claim keeps the safe union. QUATERNION-RANK2-v2.json contains the earlier four-copy rank2 witness with excluded primes{2,3,5}.

Run:

    python -B audit_rational_route.py NONROOT-LINE-PAIR.json

The independent literal matrix audit passed G inverse/orthogonality, all whole-residual projectors, support, ranks, orthogonality, sum, pullback copy support, entrance annihilation, and elementary reduction. Four controls separately modifying G, an inverse entry, a projector, or deleting an elementary factor all reject.

## Public high claim scope retained honestly

PR480 at668c7dd0fa76d0da4289c9dea63b965e730142d0 reports kappa0.001372550159367980 under inherited disputed cross-copy admission from PR448. It assigns one logical residual to two physical owner families. PR451's operator obstruction applies to that direct-sum split. This note does not certify or reuse that disputed operation. It instead gives full explicit whole-owner rational maps and a sufficient local operator identity, which still require a new global candidate and paid assembly before reporting any new kappa.


## Existing compiler bridge: no array-scatter extension needed

Inspection of pinned PR490's docs/WHOLE-OWNER-BRIDGE.txt and docs/GL-TRANSFER.txt identifies the actual sufficient inherited contract. For fixed route sigma in the admitted group, a helper at cover class d is assigned to the WHOLE array indexed by (family,d sigma^-1). This is reindexing by a group translation. It is not an extra physical scatter of every array at every scalar call. If g=d sigma^-1, its endpoint is P_g (P_sigma H P_sigma^-1) P_g^-1. Right translation bijects the full cover, so every pending family receives the required residual once per complete sweep. The local theorem on arbitrary dirt gives sound sequential reuse.

For our pair construction use sigma_j=placement*(G directsum I)*swap(copy0,copyj), extended to dimension78. Both sigma_j are full orthogonal matrices; their distinct active projectors ensure distinct matrices, and group cancellation ensures distinct actual owners at every cover class. Other paired banks have disjoint active blocks. Their projected endpoint operators commute, and product plus the explicitly charged leftover child is the original pending operator. The two spectator directions are within the same family; each complete helper invocation restores its entrance endpoint.

All18 selected pair frames have dyadic G entries. The fixed dyadic matrices therefore fall under PR490's already stated ordered-affine and weighted GL-routing contract. No new routing oracle is introduced. Using that GL cover retains its row invoice28416 and finite symbolic B_GL in bootstrap cutoffs, rather than silently inheriting the smaller orthogonal-group row discount. The factor matrices merely give an explicit finite implementation witness for the selected fixed translation; they do not enlarge scalar coefficients because the operation is an index permutation. For fixed q the low-type table and its carry cases are finite. A full changed assembly must bind these new fixed routes to its B_GL contract and recheck the strict margins.

The general four-copy route with other denominators also fits this contract after choosing the fixed prime outside its explicit finite bad set, but this round's concrete candidate needs dyadic pairs only.

## Concrete22-pivot candidate and feasible allocation

The kernel lane produced NONROOT-JOINT-WORD.json, SHA25616bea049646b4473ceebd4337e7226e2144c01f84c5dfb4eb30683b14188cd18, with22 additional rank1 entrance pivots. Its exact local audit checks955 columns, rational frames, and integer operand spans. The local child delta is+84 rank1 minus53 rank2, rank-mass decrease22. The22 affected helper residuals change from rank8 to rank7.

paired_owner_witness.py emits paired22/PAIRED-OWNERS.json. It supplies all62,920 source-bound whole residual owners over11 stages and8replicas. The1936 affected helper occurrences are paired into968 indivisible rank14 tokens. All18 rational route frames independently pass matrix/projector/elementary audits. Pair tokens never occupy rank7 singleton windows. The allocation uses at most2 pairs per same family/window and4 same-family spectator dimensions, below the available dimension78 footprint. Ordinary and paired active blocks have disjoint intervals; within a pair the two complete residuals have orthogonal projectors instead of disjoint coordinate support.

The actual feasible paid profile is {1:221080,2:88058,3:22968,4:27256,5:9944,6:6864,7:4248,8:792,36:1,56:775}. Its rank mass is745536, deficit3264, and numerical bit saving nomination is0.001302768563042178. This is a genuine positive early price gate, not a final certified kappa. Full source-bound scalar emission, alias-aware coefficient invoice and GL sharp outer assembly are the subsequent checks; no0.0014 claim is made.


## Final current candidate on the139-entrance baseline

The latest source-bound word is kernel_codes/provider-new139/word.json, SHA256c50c9b21f11a8dc0c93c669bbf46e91aa40ac19ddb948397d7e276c3b91a535b. Its161 entrance rank includes the22 new non-root pivots. The local native exporter and955-column/legality/Gram audits pass unchanged; a decoder adapter explicitly admits all56 auxiliary geometric lines without changing the120 ports.

The paired allocation is paired-new139/PAIRED-OWNERS.json. Its feasible paid profile is {1:222672,2:87431,3:22648,4:27124,5:9944,6:6848,7:4280,8:792,50:1,56:793}; the rank mass remains745536 and deficit3264. The numerical bit-saving nomination is0.0013036679750784708. The final root kappa must come from the exact GL/complex assembly, not rounding this nomination.

emit_paired.py produced global-new139-v3. Its complete program includes1,733,496 scalar/local/bridge events in the chronological source-bound digest. Every local invocation passes955 independent columns, every stage passes9065 independent columns, and the actual owner aliases give prefix1684bits, rounded conservatively to1728. Ordinary entrance maps, all source frames, initial/final states, paired registry and source-word hash are rebuilt into the emitted template; no old coordinate-map registry is claimed for the new entrances.

audit_actual_pairs.py constructs the actual full78-column matrices. Crucially, it prepends the source-bound ambient basis for the owner's port and the pending child's actual source/target axes; using a standard first-r block without this factor would be wrong. It verifies exact owner/template binding, all88 invocations, all62,920 whole helper owners,11,423 distinct full matrices and each chronological interval. The sigma-stream SHA256 is60024b82cbe1cc424b290766b08d5768f9a7186b85bbe51b0f1568a2e4497726. The1936 new helpers are whole paired residuals, not cross-family splits.

route_factor_invoice.py checks all120 source port bases and all18 pair matrices. At most29 Gaussian factors are needed for a port basis and33 for G. Including8 copy swaps and two permutations of at most77 swaps gives224 factors per direction. The assembly deliberately charges512 residual-isometry factors per direction, and its existing leading factor2 pays the inverse. Every scalar in these SELECTED elementary factorizations has numerator/denominator at most2. Thus no odd exceptional prime is introduced; the older sample receipt's prime3 belonged only to an unused optional Householder factorization. The remaining asymptotic compiler assumption is exactly the fixed-dyadic ordered-affine GL contract already stated by PR490, with full GL row allowance28416 and symbolic finite B_GL, rather than an unstated new permutation primitive.

An independent agent is replaying the whole emitted invoice before final root assembly. The results in this note establish the new concrete construction and checked finite pipeline, and are not a claim that the0.0014 target was attained.

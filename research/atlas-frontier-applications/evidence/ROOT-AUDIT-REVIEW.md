# Independent review of root's owner, moment and admission checks

Disposition: passed code and mathematical review for the exact source hashes recorded below. No root source was edited. This review is separate from the allocation producer and from root's execution receipts; it is not a second execution of the full native or outer release.

## Independent dyadic moment auditor

`root/audit_moment.py` uses only exact Python integers and Fraction arithmetic. It imports no inherited logarithm, exponential or moment implementation.

The logarithm range reduction is valid for each actual argument 73/r: repeated division by two leaves a number in [1,2], and the omitted powers of two are restored by adding k log 2. For z=(y−1)/(y+1), one has 0≤z≤1/3. The 128 included terms end at z^255/255. The next numerator is z^257, and every remaining denominator is at least 257, so 2z^257/[257(1−z²)] rigorously bounds the entire positive tail. The implementation's updated `term` and denominator 257 are correct.

The exponential includes degrees 0 through 24. Its first omitted term is y^25/25!, implemented as `term*y/25` after the loop. Every subsequent ratio is at most y/26, so division by 1−y/26 bounds the remaining positive tail. The required domain 0≤y<1/10 ensures a positive denominator and convergence. Actual savings and ranks satisfy this domain. Both lower and upper logarithm bounds are multiplied by nonnegative savings, and exponential monotonicity therefore gives valid endpoint inclusions.

The `down` and `up` functions are floor and ceiling at denominator 2^192, including their signs. All weights r·count/(73W) are positive at the actual inputs. Summing interval endpoints and rounding outward again preserves inclusion. The intervals are sufficiently fine for the requested 26-digit rational bracket; an inconclusive sign raises an error rather than selecting a side.

The code checks both exact rank masses and the complete comparison polynomial

    2·new − 3·old = 2H_32 − 2H_5 − 3H_2 − 3H_16.

This correctly compares 372 replicas with 248 replicas after normalization, rather than comparing unnormalized costs. The bracket endpoints have strict signs. The claimed target lies strictly below the certified lower endpoint, and positive rank weights with r<73 make the normalized moment strictly increasing in the saving parameter. Thus the lower target is admissible for the finite histogram. The full pinned PR2848 rational target, rather than a truncated decimal, is used for the gain comparison. Its interval upper moment is below one, and the new upper moment lies below the old lower moment at that same target.

The exact log 1 / exp 0 identities and the inflated-endpoint and extra-rank-32 charge checks are valid controls. These three listed controls comprise one identity check and two rejection inequalities; they should not be described as three full mutated-driver executions.

## Separate source-event owner auditor

`root/audit_owners.py` correctly attributes and adapts PR2848's owner implementation. Its independence is from the candidate producer and inherited owner engine; its source lineage is not claimed to be independently invented.

The auditor authenticates each retained source file using both SHA-256 and its Git blob digest. It requires the candidate order to equal a complete round-robin lift of the authenticated T124 order, and its dispatch to equal the corresponding provider lift. Every replica's expanded source projection must be exactly events 0 through 29, with terminal events exactly 30 and 31. Thus matching stage counts alone cannot substitute for the actual event chronology.

For each literal role it checks six integer coordinates, valid call/helper/owner/port ranges, strict containment between expanded source-event endpoints, and at most one use of each actual physical family in a call. The family formula uses the authenticated pair/side map, so different child labels cannot evade a collision on the same physical family. Helper bitsets reject duplicates and require all 408 actual helpers in every call.

Capacity is checked against the authenticated child's rank. Shifted masks reject overlap. The identity `mask & (mask+1) == 0` correctly characterizes a used prefix starting at offset zero, including the empty mask; this prevents internal unused gaps from being priced as a single residual child. Recounting every owner, child and port includes completely unused bins. Adding the unchanged native provider profile once per actual call gives the entire paid histogram, and the final exact rank-mass equation is correct.

Logging all changed rows, rather than restricting acceptance to precisely three edits, is appropriate for this general owner auditor: any accepted alternative must still satisfy the same complete allocation predicates. The exact three-edit construction is separately bound by the producer receipt and candidate hashes.

This auditor reads the explicit `DISPATCH.json` as the authoritative provider table. It does not separately validate unused fill metadata such as column labels or `dispatch_overrides`; the actual candidate's corresponding fields come from the authenticated lift, while the full reconstructor and admission checks remain responsible for their runtime interpretation. It does not claim to verify native operator identities, the physical transcript, precision or the outer construction.

## Admission-driver change

The normalized-text diff of `root/admit_atlas_candidate.py` against the pinned PR2848 `admit_dirtentry_replica_latest.py` is exactly one added `COMPARISONS` entry:

- PR 2848, head `c50d12e4720cd1fef2b5a65e337e37de9731879a`.
- Claim SHA-256 `aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9`.
- Full rational comparison field `kappa`.

The actual downloaded claim has exactly that digest. The existing code still requires the immutable claim hash, rejects a supplier-only comparison claim, reads its full rational target, and requires strict improvement. Source manifests, native/cache receipts, complete replica/order coverage, explicit dispatch, source-stage projection, changed-runtime predicates and final release binding are untouched. The existing pre/post source, cache and external-input guards remain intact. This is a new authenticated comparison choice, not a relaxed acceptance predicate.

## Operational scope

The two standalone auditors assume a frozen input snapshot and report its hashes; they do not themselves implement a transactional filesystem snapshot or a complete pre/post guard on every file. In this campaign the producer outputs are frozen, and the admission driver separately authenticates and rechecks its external inputs. Their receipts should remain attached to those exact hashes. This review found no mathematical or predicate error for the pinned inputs, and it does not turn a finite owner/moment pass into a complete release without the remaining native, global, physical and outer receipts.

Normal prose spacing and Unicode are retained. Candidate JSON and frozen allocation files were not changed.

## Reviewed source hashes

- `root/audit_moment.py`: `0c71705f3640f5cbf10924792d52b5bea7c319493ea1b25622723b89d012052c`.
- `root/audit_owners.py`: `3f1cc497c0574317998139d24c21ee4e2f5f2fffedba97b9c3cc980827fc6895`.
- `root/admit_atlas_candidate.py`: `50a909442b8c845bf9232aca9a119a032f7d5232d7194e899f1c5b7e020584b0`.
- `upstream/pr2848/admit_dirtentry_replica_latest.py`: `b926725ea029c71979e48e785578aa4821ea7ea73c8e9139c4e2c71fa6bfc91b`.
- `upstream/pr2848/CLAIM.json`: `aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9`.

Reviewer: the allocation worker, separate from root’s auditor author. No external service, Lean process or new mathematical search was used for this review.

# P1: specialize the selected physical grammar to final #4610

This note proves a conditional **specialization**, not a new physical primitive theorem. Let H_selected denote precisely the native normal-form, compact movement/repair, scalar/owned-storage, completed-call, fixed-tape and outer hypotheses retained by selected #4470 through its reviewed #4359/#4416 lineage. Under H_selected, the actual final #4610 catalogue is an instance of that same physical grammar, with newly counted fixed constants. The proof does not introduce a separate assumption that the new recipes work.

Candidate #4610 is Cao Yifan/intqwq's existing construction, head `20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`, final local-word payload `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`. Pinned canonical source is `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`. Selected #4470 remains .00302015; this note does not modify selection or claim construction/gain priority. Exact source bytes, including the following premise texts, are bound in `SOURCES.json`.

## 1. The selected premise already quantifies over the required class

The premises used here are the following statements in the selected source closure, with their original physical qualifications retained:

1. `notes/general-clifford-frames.tex`, “Exact representatives and nested children”: for an arbitrary binary subspace U and deterministic invertible basis extension G, the exact Gaussian-dyadic K_G and its conjugate by F have rank zero and are fixed binary address permutations with unit quadratic phases. For **every** nested U subset V, the exact transition is two rank-zero adapters around a positive coordinate C child. Exact phases and finite movement/scalars are charged. The statement is not restricted to the selected word's list of old frame labels.
2. `notes/compact-control-movement.tex`, “Compact-control selected-bit addition” and “Application to a fixed binary change of basis”: either ordering of two complete slots admits exact selected-bit row addition with restored arbitrary temporary fields; a fixed binary basis change is a fixed number of such additions. The fixed-tape bound is `O(V*((e*log p)^tau+1))`, including repair and descriptor work, under the stated complete-field reservations and record-size hypotheses. Constants and cutoffs are uniform within each fixed parameter family.
3. Selected #4359 `PROOF-REVIEW.md` section2: free-word evaluation allows arbitrary positive column multiplicity by substituting lifted generators, separately tensor-lifting exact paid/helper factorizations. Absolute monomial phase is `a*f+sum q(x_j)`. Helpers are normalized only after their autonomous completed endpoint. Section3 explicitly permits fixed template matrices/matchers to change dimensions/counts/constants while retaining the same movement exponent and tape uniformity. Section4 separately pays address permutations and unit phases and replaces semantic precision constants.
4. Selected #4416 `PROOF-REVIEW.md` section2: exact whole-job normal forms use independent **two-sided** recorded factors. They need not be an inverse pair. Canonicalize the complete job, place its axes by a charged coordinate matcher, execute the child, and restore the prescribed adapters before resuming its parent. Distinct physical owners and separate live centers are preserved.
5. Selected #4470 `PROOF-REVIEW.md` sections1–3 applies these rules to new actual helper normalizers, paid transports, p16/query/idle events and their new finite scalar/route/owner/precision constants. The retained conditions include all-column implementation, whole-job adapters, owned erasure, fixed-tape movement, precision and outer hypotheses.

Consequently the permitted class is generic fixed finite Gaussian-dyadic monomial/positive-child programs with the stated arbitrary-owner and spectator ABI. It is not the stronger assertion that an arbitrary RAM gather or arbitrary address function is cheap. The reduction below uses only the selected binary row-addition/ordered-movement operations, finite unit phases and the same scalar/child/owned alphabet.

## 2. A constructive grammar for every actual monomial

Use the source's exact composition convention. A record m has invertible binary matrix A of size9, affine offset b, constant a modulo4, linear coefficients alpha_i modulo4 and symmetric binary quadratic matrix Q, with `alpha_i mod2=Q_ii`. On a basis address x it acts as

```
|x> -> i^(a+q(x)) |A*x xor b>,
q(x) = sum_i alpha_i*x_i + 2*sum_(i<j,Q_ij=1) x_i*x_j  (mod4).
```

This is exactly `prune_native.monomial`: diagonal phase first, then binary permutation, translation and absolute phase. The Q diagonal is encoded in alpha, not added again as a quadratic term. No phase convention is inferred from the binary matrix alone.

Gaussian row elimination reduces any such A to identity with at most72 row additions and8 row swaps. Reversing that list implements A. Replace a row swap by three XOR row additions. This gives at most96 selected-bit row-addition records. The affine offset takes at most9 selected-bit translations. The phase takes at most27 unit-S records for the nine alpha values,36 controlled-sign records for the off-diagonal pairs, and3 global i records. Thus **any** admitted nine-axis monomial, including its inverse, has a recipe of at most

```
96+9+27+36+3 = 171
```

retained elementary movement/phase records; two independent adapters need at most342. These bounds are conservative and independent of f and the eventual multiplication input. The checker constructively reconstructs A, checks symmetry/parity and phase coefficients, and verifies the decomposition on zero, basis, pair and additional addresses. The algebraic row-reduction and degree-two polynomial argument establish the universal nine-bit statement; the probes corroborate it.

The physical interpretation introduces no new instruction species. A row addition is precisely the selected compact-control addition with its full dirty-control restoration and repair. XOR translations are fixed selected-bit affine operations. For a phase, compute its fixed degree-two residue modulo4 once per complete record from address/descriptors, then apply one of `{1,i,-1,-i}` to its Gaussian-dyadic value. This is a sign change and/or exchange of real and imaginary components on the retained fine grid, with zero coefficient height. For f columns, computing the residue scans at most O(f) selected address bits and therefore costs a fixed polynomial in the existing descriptor length A. The record-paid offset/phase setup is absorbed by the **same** retained superpolynomial record fiber, not charged as a new per-payload-bit scan. Complete address ranges and control reservations are the selected source hypotheses throughout.

In particular, neither a new field extension nor scalar rounding nor a free arbitrary permutation is used. The full address transformation is factored into the selected row-addition primitive and inverse routes; its workspace is the source's restored complete control fields and fixed work tapes, with newly substituted template constants.

## 3. Quantifiers and the all-f lift, including the absolute phase

First fix the complete finite word, every matrix/phase recipe, its ordered owner list and all fixed matchers. Only after those choices let f be any positive integer column multiplicity. For x=(x_1,...,x_f), the lifted monomial is

```
x_j -> A*x_j xor b  for every j,
phase = a*f + sum_(j=1..f) q(x_j)  (mod4).
```

Apply the finite row-addition list to the corresponding pair of complete f-axis slots, and use the pointwise residue above. Each selected slot is a full range; arbitrary intervening, preceding and following spectator fields remain present. The temporary complete compact fields are returned by each addition. Thus the lift is exactly m tensor-powered f, acting as identity on the other address fields. It uses one fixed list of primitive **types/operations**, rather than f separately allocated tapes. Its per-record descriptor arithmetic is polynomial in the same selected address bound, and the number of work tapes stays fixed for the template.

For a recorded positive-rank recipe, source equality is the ordered product `right.then(C_r).then(left)`. Tensoring this product gives `right_f.then(C_(r*f)).then(left_f)` after the fixed coordinate reordering. This is one ordinary positive rank-r*f child on the actual owner's full stream, with its input and output monomials independently retained. Inverse orientation and Pauli corrections are included by the actual signed recipes. No identity distributes a tensor power over a matrix sum.

For the scalar word itself, use selected #4359's free-word substitution theorem: replace each warp generator by its f-column lift while leaving ADD/SCALE coefficients and chronology unchanged. This is an algebra homomorphism from the noncommuting free-word algebra; hence the already checked arbitrary-input word identity survives. The scalar program is not itself tensor-powered. Keeping a single constant phase a instead of a*f would violate the lift; a negative control explicitly distinguishes that mutation at f=2.

The ideal algebraic lift holds for every positive f. Its physical tariff applies only in the selected source domain: f<=p, A=O(p), K/log p tending to infinity, and a superpolynomial record fiber. In the actual layer f<=e<=floor(b_in^epsilon) and p=6*b_in eventually. No tariff is extrapolated to arbitrary independent f,p/geometry. The compact-control parameter hypotheses are unchanged: f slots, complete dirty reservations, `A=O(p)`, record fiber beyond fixed powers, and the same selected movement exponent. The final uniform template may have much larger fixed dimensions and operation counts. That changes constants and thresholds through section6 below, rather than changing these quantifiers or creating a new tape per coordinate.

## 4. Exhaustive family/owner specialization

The executable source census is over the actual final payload, not its proposed histogram. It classifies every event in both21449-record orientations, and checks exact scalar coefficients/opcodes/chronology against the selected THREE-base word. Main charts on all224 persistent main owners are exact retained records. Every scalar target/source belongs to the632 declared persistent owners or the one declared owned C0. Clear and overwrite COPY target only C0; ADD arguments are distinct owners; no new borrowed owner, alias or productive C0 is introduced.

| Actual family | Membership/coverage | Selected physical interpretation |
| --- | --- | --- |
| 180 signed warp classes,240 occurrences | Each actual G is invertible; both signed recipes have rank0;800new monomial records cover this and the changed families below | Fixed affine binary permutation and unit quadratic phase from section2; same all-f native generator |
| 3290 borrowed climbs per orientation | Actual source/target bases strictly nested, correct current owner/frame and rank | The selected arbitrary-U-subset-V factorization: two rank-zero adapters and one positive rank-r*f child |
| Eight center calls per orientation | Actual nested comparable bases, owned C0 only, all eight rank8 jobs billed | Same positive child plus signed adapters; no productive credit, no allocation of a new arbitrary input |
| 408 helper endpoints | Actual strict nested entrance/exit, profile `{4:28,7:7,8:47,9:326}` | Complete two-sided normal form on each distinct arbitrary input field; no internal scalar reframing shortcut |
| 448 main entrance/exit charts | Exact event equality with retained base main charts | Source-identical selected chart/axis interface, with its retained charge |
| 17453 scalar records per orientation | Exact old opcode/coefficient sequence, dyadic grammar and current-frame checks | Retained ADD, dyadic unit SCALE, owned COPY/CLEAR; identical scalar tariff |
| Ten phase labels | Fixed annotations, no new physical instruction | Existing scalar-word scope boundaries; not extra outputs or uncharged operators |

Exact factorization equality and arbitrary-input endpoints are independently established by the admission dossier's native/phase replays, not by a syntactic schema. This module supplies the missing **physical class implication** for those exact factors. The new phase receipt covers180signedwarp classes,105newpaid pairs and5changedhelper pairs. The382 unchanged helpers are bound to the selected #4470 phase receipt through gain_acceptance's exact ordered-basis/owner lineage;26changed helpers use the new five-pair receipt. The independently replayed all2855paid-pair factorization module supplies the full actual paid-pair coverage. These coverage claims remain separate from this module's fresh class/census checks.

For owned return, the local word retains one physical C0 and ends its C0 updates with a permitted erase. The existing arbitrary-input native proof establishes completed main/helper endpoints and C0 clearance. During product/compiler substitution, each suspended local occurrence receives its own center bank; all child inputs are distinct actual fields, even when values are correlated or one input is a parent's center. The child finishes and its adapters/role ordering return **before** the parent resumes. The parent clears only its own bank after its last use. Every such bank is excluded from productive W and included in full O. This is exactly the selected compiler ownership rule; no one-bank-per-depth reuse or undeclared initialized input is used.

## 5. Finite raw tariffs in the selected unit

The tariff unit here is a retained elementary scalar/movement/phase **record**, each realized with the selected physical primitive's asymptotic bound. It is not one literal tape instruction and does not suppress the f-dependent movement bound. Choose the same common upper unit for the fixed primitive alphabet as in the selected finite-word accounting. Each new two-sided nine-axis recipe has at most342 elementary records, below the retained conservative1000-per-group allowance. Unchanged main charts retain their selected count/unit. The selected primitive implementation constants, record-paid setup, scans and repair remain paid in that common physical unit. Changing the finite catalogue does not require a new asymptotic movement assumption.

The actual local route groups are

```
3298 paid jobs + 2*408 helper wrappers + 240 warps + 448 main charts
  = 4802 groups,
4802*1000 = 4,802,000.
```

The source scalar allowance formula, reimplemented directly without importing its evaluator, gives158120 forward and158168 backward. Therefore

```
158168 + 4802000 = 4960168 < 10^7.
```

This is an instantiation of the selected raw-unit bound with a smaller changed paid count, not reuse of an old expanded compiler cap. The controller remains18full calls and15thin queries, with the exact retained physical-event and boundary programs. The complete source raw bound is

```
18*10^7 + 15*1792
  + 32*112*(#physical_events + #left_boundary_program + #right_boundary_program)
  = 181098496 < 10^9.
```

Each thin query's paid rank-one request, owned copy/add/erase and inverse orientation remain in the source invoice. Idle jobs, main normalizations, inherited controller geometry and actual exact phase bills remain charged. No local or controller charge is credited as a new productive output. These numerical bounds concern **raw** supplier records only; they are not the expanded uniform word's operation count, storage or literal physical runtime.

## 6. Expanded compiler, precision and tape constants

Apply the selected chronological product, same-owner paid completion, disjoint splitting and integer finite compiler to this now-specialized raw program. The algorithms are finite and only instantiate the same grammar. Their matching uses complete job endpoints and restores adapters, and their owner allocation is the rule just proved applicable. No new movement species occurs when a fixed matcher has a larger fixed rank: binary basis/coordinate permutations have the same finite elimination construction, now with a larger fixed list.

Let W,P,O be the actual final productive width, paid rank-one count and full owned-bank allocation; let R count the full native/movement/normalizer records, including product, completion, split and compiler routes. Let G be their fresh dyadic coefficient/phase allowance, computed by summing the actual scalar allowances (plus the source's conservative non-scalar charge). These are finite computable integers of the new expanded template. They are fixed before multiplication input size varies. A record-count overestimate and one owned bank per relevant occurrence suffice; no practical materialization or old p3 numerical count is needed.

Use the **new** values in the selected semantic prescription:

```
Z=W+O,
E=64*(Z+N+P+G+1)^3,
B=P+E,
C0=32*N*B^2.
```

The selected completed-child argument gives `A(e)<=A(floor(e/N))+P*floor(e/N)+E`, hence `A(e)<=2B*e`. Monomial permutations/unit phases add no coefficient height but do retain their execution/descriptor costs. The new C0 determines a new eventual fine-grid threshold. The compact row reserve, full simultaneous stock products, depth-first parking, fixed tape inventory and polynomial setup degrees also use the new W,P,O,R,N and selected formulas. Fixed enlarged degrees/counts are absorbed by the same retained superpolynomial record fiber and strict outer epsilon<1 after increasing the threshold. In particular, neither raw10^9 nor selected p3/p16 reserve constants stand in for these expanded values.

Thus P2–P4 can consume a genuine new finite instance of H_selected's grammar and precision/stock/tape prescriptions. This note does not independently prove the historical native movement/repair or outer analytic/recovery stack. Those are exactly the assumptions already retained by selected #4470, with no additional candidate-specific implementation assumption.

## 7. Conclusion and exact limits

Given H_selected and the source-bound exact semantic/phase endpoints supplied by the independent native dossier, the final catalogue has permitted explicit all-f realizations, legal actual-owner return, finite raw tariffs and the selected expanded-constant substitution. No extra primitive or changed movement exponent is required. P1 is therefore a **consequence** of H_selected for this instance. It need not be restated as a new hypothesis “the new recipes implement.”

`checks/specialization.py` runs through the master verifier and its source-authenticated `--repo` working-byte loader; it never substitutes clean Git blobs for dirty inputs. Its new actual catalogue has800monomials with at most83 elementary records each, compared with the uniform171 bound. It also checks1692selected monomial records by the identical schema, exhaustive event/role/rank/scalar census in both orientations, helper geometry, retained main charts, the4802route grouping and raw bounds. Controls reject singular maps, non-Z4 absolute phases, borrowed clear, unpaid rank changes, non-dyadic scalars and an unlifted f=2 global phase. Exact phase/operator equality is intentionally supplied by the separate phase/native verification rather than inferred from membership.

Credits remain with Cao Yifan/intqwq (#4610), Cinna Davis (#4470/#4416/controller/helper lineage), zxv (#4359/native/compiler/semantic precision), icekylinx and Dugongue (general Clifford/transported frames), Jacob Alan Sussman (mixed integer compiler), and all retained physical/BIT/geometry/analytic contributors. This new specialization/proof/check uses substantial OpenAI assistance. It is a scoped conditional AI verification contribution, not an unconditional multiplication theorem or independent human/kernel acceptance.

# Contextual observability calculus with explicit reversible cleanup

## The sufficient theorem

Let the finite register module over a field K be B direct-sum Y. B contains every source and temporary register; Y contains observed outputs. A body is a finite word in invertible elementary additions and nonzero scales. Every instruction that writes B reads only B. Instructions writing Y may read either summand. Initial registers, including temporary dirt, are arbitrary.

For a cut immediately before an invertible background instruction G, write the body as S G P (rightmost factor acts first), and let pi_Y project to Y. Define H = pi_Y S. Replace G by an invertible instruction or finite background block G' with

    H G = H G'.

Then pi_Y S G P = pi_Y S G' P on the ENTIRE register module. This is equality on all dirty columns, not only on an intended clean input subspace.

Let B_old and B_new be the background maps of the old and new bodies. Both are invertible because the background instructions are invertible and never read Y. Append the inverse background instructions in reverse chronological order, leaving Y untouched. The completed old and new words then both restore B exactly and produce the same Y. This proves equality of the completed operators on arbitrary input dirt. Any fixed prefix, suffix, or previously derived dirty compensation can be retained by ordinary composition.

For a sequence of rewrites it is sufficient to recalculate H from the actual current suffix at each rewrite. Induction then gives equality of the full completed word. No assumed synthesis oracle is used: H is obtained by exact finite matrix propagation and G' is explicitly emitted.

## Constructive nonzero-response retarget rule

Suppose G is z_t += q z_s with s != t, t in B. Choose u in B distinct from t and s, and compute the two columns H_t,H_u. If H_t = lambda H_u, replace the instruction by z_u += lambda q z_s. Indeed

    H (I + q e_t e_s^T) = H + q H_t e_s^T
                               = H (I + lambda q e_u e_s^T).

Both instructions are invertible. Neither response column need vanish. This therefore strictly extends dead-store deletion as a sufficient rewrite rule. More generally, if H_t = sum_u c_u H_u and each u is a distinct background register different from s, the replacement consists of the commuting additions z_u += q c_u z_s. The source is unchanged by those additions, so the same identity holds exactly.

This algebraic theorem does not make the replacement free. All new scalar instructions, inverses, coefficient growth and frame transitions must be charged. Native implementation additionally restricts addition coefficients to allowed dyadics and scales to its supported invertible coefficients.

## Constructive frame and resource refinement

Attach the actual entrance frame, every instruction frame, required center/target checkpoint, and terminal cap to each logical register. Every resulting frame chain must satisfy the retained native compiler's monotone-subspace conditions. A gate retarget is admissible only if the replacement's new source and destination can both be represented in its stated frame. In the monotone case this can be checked by predecessor subset gate-frame subset successor, plus all fixed checkpoints.

Rebuild the scalar cleanup from the altered background instructions. Compute the recursive histogram from the ACTUAL changed chains, including all inserted and deleted transitions. This produces a sufficient compiler refinement: the completed scalar operator is unchanged by the theorem above, the frame chains are legal by the explicit subspace checks, and the cost is the freshly computed histogram and scalar invoice. The all-size compiler contract remains the inherited hypothesis; this finite theorem does not prove it.

A useful exact specialization is chain-preserving retargeting. If each register's entire deduplicated frame chain is identical before and after, then every frame-transition child, entrance width and final cap is identical. Thus the paid recursive histogram is identical. The scalar program and its intermediate norm envelope may change, so their independent replay and invoice must still be refreshed. Equality of the histogram is NOT evidence of a numerical improvement.

## A further sufficient protected-input extension

One may weaken full-column body equivalence only with an explicit replacement compensation. Split initial background columns into protected X and unentered dirty D. Include all source columns and every nonzero-entrance helper among X. Assume an invertible, background-only body and invertible target block T are exhibited, so its output is A X + B D + T Y. If a changed body preserves A and T but gives B', prepend the explicitly computed target preparation

    Y <- T^{-1}(Y - B' D).

Its completed output is then A X + Y and its background inverse restores every background register. This works only when the displayed target preparation is actually expressible and billed in the physical interface. In particular all D registers must be available at the required entrance frame and the target preparation must be compiled with its exact coefficients. Nonzero-entrance dirt cannot silently be included in D.

An exact gate-level sufficient condition follows from prefix rows: if the protected restrictions of the current rows satisfy X_s = lambda X_u, replacing t += q s by t += q lambda u preserves all protected columns. Recompute B', emit its compensation, and rebuild cleanup. This is not a license to alias arbitrary logical roles on the same physical family.

## Actual construction used this round

Input: the filtered PR531 descendant at response/filtered-coalesced/FULL-WORD.json.gz. It has 112 ports, 504 helpers and 728 arbitrary input columns. The frozen deterministic constructor rewrite_observation.py computes the suffix response exactly and checks

    A[645] : register 31 += (1/2) register 240
    H_31 = -2 H_245 != 0.

It replaces this with register 245 -= register 240 at the same frame [296,168,120,6], then regenerates the full inverse background cleanup. Both registers are background registers. Every deduplicated frame chain, entrance width and center checkpoint is exactly unchanged. The local paid profile remains

    {1:2048, 2:732, 3:176, 4:360, 5:56, 6:56, 7:8},

with rank mass 6152. An independent changed-word audit checked all 728 forward columns and all 728 inverse-transpose columns, exact frames and native dyadic restrictions. The final supplier registry additionally binds the selected provider's actual programs, phase recipes and entrance adapters at each complete invocation.

This is an applied, constructive, nonzero-response theorem witness. It contributes no independent decrease in kappa's moment. The numerical improvement comes from the new filtered supplier together with the resource matching that fits (5,9,9,9) into rank32 owner bins. Selecting original filtered and response-retargeted variants at different complete invocations demonstrates contextual composition without multiplying or adding incompatible gains.

## Bounded discovery ledger

All searches below had exact finite scopes; neutral or failed searches do not imply impossibility outside their scope.

- Projective suffix retarget: PR531 510 alternatives,65 legal; filtered 438 alternatives,65 legal. Every legal fixed-frame move was moment-neutral.
- Suffix retarget with gate-frame endpoint adjustment:72 legal candidates; no positive paid gain.
- Multi-destination response-span retarget at free frame insertion:531 had500 split gates and344 free candidates; filtered504 and222. No required span identity found.
- Native neutral-face search:8 bounded runs,23 to39 neutral moves each, no positive paid gain. Modular nominations would have required exact rational replay; no claimed positive witness arose.
- Protected-prefix retarget:531884 equivalents/401 legal, filtered728/181; all legal fixed-frame candidates neutral.
- Protected-prefix zero slicing:zero removable operations under the frozen protected-column interface.

The positive neutral witness above was independently replayed; it is not inferred solely from those search statistics.

## Structural source provenance and novelty scope

OpenAI OAI.Computability.WLIdentification.FiniteRefinement.map_eq_of_kernel factors observables through an equivalence kernel for mapped multisets. OAI.Algebra.GroupRing.WordResponse develops composition laws for word responses. These are structural motivations for tracking only what a suffix observes and composing response certificates. They do not themselves assert the linear dirty-register compiler theorem proved here. Exact source hashes accompany this note. The live DAG was searched for kernel/composition/quotient structures; its source-only search matches were not treated as Lean verification.

The elementary matrix identity and contextual replacement principle are standard linear algebra. The contribution claimed here is their explicit sufficient calculus, native frame/resource refinement and applied dirty-register witness in this construction. No globally novel theorem, new Lean certification, or unconditional integer-multiplication bound is claimed.

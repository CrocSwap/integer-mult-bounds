# Exact limit for the current asynchronous inventory and finite word menu

Baseline: PR473 conditional kappa0.001371428043382419, complex b0.001373311441205186394130. This is a model-specific obstruction and research record, not a universal upper bound on integer multiplication.

## Timing and mixed words

The [timing ledger](async505-order24-neighborhood/LP-LEDGER.json) contains133 unique schedules: the baseline,70 adjacent independent-call swaps and62 distinct nearby delay/pacing perturbations. None improves the relaxed cost;90 tie within the stated floating tolerance. Two generated orders duplicate existing orders and are skipped. The separate143-profile word-mixture LP also ties the baseline. Floating solver output alone would not justify an impossibility claim.

## Exact dual certificate

The global inventory relaxation discards every time window, distinct-call physical-owner constraint and integrality requirement. It retains73 dimensions,7680 live families,72 complete local invocations,560 helpers per invocation, and the pending-child inventory:5760 rank8,3840 rank16,3840 rank32 and3840 rank48 children. Every helper stays whole, with residual widths in {5,7,8,9}; a pending child's remainder is paid as a child. Fixed fallback law:10^-16 times32m^2 rank-one calls per paid child.

For each leftover rank r, let c(r) be its exact moment numerator including that fallback, with c(0)=0. The verifier constructs rational inventory prices alpha and width prices beta. It enumerates all348 possible width patterns and proves

`alpha[capacity] + sum(beta[width] for width in pattern) <= c(capacity - sum(pattern))`.

It separately prices each of146 frozen local profile/width pairs. Adding the348 verified inequalities gives a lower bound for *every* allocation or mixture in this enlarged model; no LP/MILP optimizer is invoked in the certificate. Exact outward corrections guarantee dual feasibility rather than trusting approximate dual coefficients.

At b_next =0.001373311441205186394131, both independent rational arithmetic engines give a strict positive moment-minus-one lower bound: approximately3.1131651758e-26 (Mercator) and3.1123866414e-26 (base two). The unique lowest-cost menu item is the current baseline. Therefore no allocation or mixture in this model can certify b_next or any larger saving under the retained moment rule. The retained six-step outer assembly with fixed eta/beta also cannot reach the next kappa grid point. This does not exclude changing the local word menu, inventory, stock, geometry, stages, fallback law or outer assembly.

Portable checks, from this category directory, choosing new output paths:

```
python -B exact-certificate/verify.py exact-certificate/INPUTS.json exact-certificate/moment.py /absolute/new-mercator-result.json
python -B exact-certificate/verify.py exact-certificate/INPUTS.json exact-certificate/base_two_moment.py /absolute/new-base-two-result.json --base-two
```

The two checks are standard-library only. They reconstruct exact interval costs, check every inequality, reject two deliberately infeasible duals, and verify the strict bound. Original exact receipts are in [async505-inventory-bound](async505-inventory-bound/EXACT-WALL-146.json), with the [independent base-two receipt](async505-inventory-bound/EXACT-WALL-146-BASE-TWO.json). The finite input menu is explicitly retained; local constructor pass is not claimed to establish physical admission for its losing members.

## New local-word screens

Retiming PR505's COMPONENT, JOINT-47 and JOINT-51 selections yields three locally constructible words. All lose under the exact inventory dual, and are included in the146-profile certificate. Their words, selections, profiles and exact scores are preserved in async505-retimed-new-kernels.

The rank-two entrance screen enumerates16084 distinct binary two-dimensional subspaces contained in helper first frames of the retimed bare core. Retaining the current gauge exclusions gives3988 eligible sets of at least two columns; removing exclusions gives8052. All have full response-column rank. Across2719 distinct column sets, full rank modulo1000003 proves rational independence (all response denominators are invertible). No dependence is found. This constrains common rank-two entrances on this fixed response map, not different words or scalar reorderings. The script and complete counts are preserved.

The completed donor/pivot screen tries292 single exchanges within the retained kernel classes:111 constructor passes and181 rejections, with no improving move. This is a bounded neighborhood, not an exhaustive statement about all response bases. Timing variants should no longer be repeated with the same inventory and menu; a useful next attempt must change an assumption outside the exact obstruction. Scripts outside exact-certificate retain discovery workspace paths and are not portable verification entrypoints.

Credits: PR505 asynchronous whole-owner method, PR501/502 retiming, PR496 pooling, PR484 gauges/kernel, PR361 and independent base-two arithmetic engines, with inherited notices. Exact inventory dual, new screens and scope analysis by Rohan Arun with OpenAI Codex assistance.

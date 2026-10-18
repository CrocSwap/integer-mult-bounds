# Seed 55: determinant-balanced cyclic lifts

Track: recursive interfaces. Assignment seed **55**, drawn using
`secrets.randbelow(100)` from OS randomness on 2026-10-13 at 05:18 UTC.
Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`, freshly fetched `origin/main`.
Selected result: PR626 with PR543, conditional kappa
`51110230636731/31250000000000000`; it is not a target for editing here.

Three candidates considered:

1. Multiple clean checkpoints in a dirty factor chain. Not chosen: PR714,
   PR730 and PR758 already cover nearby checkpoint/tree scheduling questions.
2. Batch multiple Gaussian boundary right-hand sides. Not chosen: PR481's
   concrete Strassen construction already covers the most immediate mechanism.
3. Enlarge a stable real cyclic factor by one scalar to balance its determinant;
   implement the enlarged map by rounded integer shears and compose it in place.
   **Chosen:** this changes the leaf interface, rather than the echo tree.

Exact scope: a length-L real cyclic recurrence with position-dependent rational
coefficients of absolute value at most 1/2. One arbitrary dirty length-L array
and one arbitrary dirty scalar are borrowed. Test a reversible LU/pivot lift,
then a two-evaluation conjugation adapter for an ordered factor product.
Seed 55 selects the 55-factor, length-5 signed dyadic fixture. Include genuinely
noncommuting factors, complete rounding and restoration checks, an independent
dense rational reference, instruction corruption controls and a complete cost
recurrence. No common-label primitive or new multiplication exponent is assumed.

Expected deliverable: standalone research construction and exact certificate,
or a scoped obstruction if the mechanism fails. Stop after the stated finite
domain and one implementation; do not search for a new frontier. Target finish:
2026-10-13 01:18 America/Chicago (06:18 UTC); reserve 06:03 onward for verification
and publication/handoff. The scope was selected within the first 20% of this hour.

Preimplementation cost screen: the adapter pays four executions of the enlarged
pipeline, two source translations and two target scatters; exact prefix/closure
coefficients can grow with L. A smaller factor-execution count therefore does not
imply a supplier moment improvement. The experiment targets the changed leaf
contract and exact restoration, with that coefficient expense retained.

Coordination: GitHub reported no pinned issue at 05:18 UTC; the only open issue
was #650 (Discussions). No reservation issue is created. Relevant pending PRs
#628, #663, #665, #673, #689, #705, #714, #730, #744, #758 and #764 were inspected
at the description/source level as applicable. The chosen one-scalar leaf lift
is distinct from their additive leaf/echo-tree and spectral-hosting contracts.
PR756's balanced-Fano verification tooling is reserved for the coordinating chat.

Contributor: Wentao Li (@VictorLiwentao; X: [@Is__Victor](https://x.com/Is__Victor)), with substantial OpenAI Codex
assistance. No independent human review or priority claim is made.

## Completed result (one final claim update)

Published [PR805](https://github.com/CrocSwap/integer-mult-bounds/pull/805) on
2026-10-13 at approximately 01:02 America/Chicago (06:02 UTC).
Status: research construction / recursive interface; **no new kappa**.
The exact real half-stable cyclic leaf and ordered product restore one arbitrary
dirty array, one dirty scalar and the source. The n55/L5 fixture uses 220 enlarged
factor executions and 2,660 coordinate updates. The predecessor's 3,232 additive
leaf calls have a different leaf interface and price.

The frozen mathematical source commit is
`055e34ecc195529841f0a75c7b53a61c12cce694`; publication receipt changes are documentation
and context pins only. The base and consumed PR628 source pins remain above and
in SOURCES.json. Reproduce with
`python3 -I -O -B research/balanced-cyclic-lift/verify.py`; expect
`PASS_BALANCED_CYCLIC_LIFT` with 1,560 factors, 7,420 columns, 4,680 rounded factor
cases, 315 products and 25 controls. Optimized/offline/package-corruption and
Python 3.9.6/3.13.2 checks pass. Root make verify passed seven historical groups,
then failed at gen4-bank-verify because the unchanged base environment lacks SymPy.

The final full overlap refresh covered 621 open PRs through #802, followed by
an immediate pre-creation inspection of #803's separate analytic inverse bound.
No matching cyclic in-place leaf contribution was identified. Related echo-tree,
checkpoint and analytic authors are credited in NOTICE.md; no concurrent code is
consumed. The original selected result and upstream files are unchanged.

Verification and handoff began early, at approximately 05:40 UTC, retaining more
than the final quarter of this work for checks and publication. Remaining limits:
exact coefficient entries grow with cycle length; the full complex/root/scaling,
physical compiler, tape/layout, supplier invoice and multiplication transfer are
not supplied. The bounded experiment ends at this one reviewable contribution.

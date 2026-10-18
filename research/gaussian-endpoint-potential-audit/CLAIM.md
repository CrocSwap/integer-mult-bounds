# Local sprint claim

- Track: adversarial mathematical audit; OS-random seed: 62 (cryptographic byte rejection at 200, then modulo 100).
- Base: f567884aeb8851b6e794af1184119a3bfbe1e631.
- Object: notes/fast-gaussian-resampling.tex, lem:correction-powers; retain the correlated endpoint squares in the existing potential argument.
- Hypothesis: combining the endpoint terms gives beta_end^2/theta - beta_start^2/theta, reducing the exponential prefactor; derive certified residual counts without confusing a power residual with the inverse tail.
- Method: written universal algebra; exact rational path enumeration, a separate integer-scaled oracle, rational constant bounds and adversarial sign/tie/carry controls. Seed 62 fixes supplemental path samples.
- Deliverable: one scoped proof/audit package with a deterministic certificate and offline verification command. No new kappa; no selected-frontier change.
- Expected finish: 2026-10-13 12:00 UTC (14:00 Europe/Paris).
- Three candidates considered: packed-bit exceptional repair (already addressed by #735/#763/#773); signed coefficient extraction (already addressed by #690/#693); Gaussian correction-power endpoint accounting (chosen).
- Overlap: current open PR titles through #898; targeted all-state searches for selected-bit, signed packing, resampling, Neumann and correction powers. #5 supplies the original potential; #684 audits chirp windows and explicitly excludes Neumann evaluation. No duplicate endpoint-power refinement found in these searches. This is a bounded metadata inspection, not an exhaustive review of every PR's source.
- Coordination: the open-issue query returned only #650, a request to enable Discussions, not a pinned sprint issue. Claim recorded locally; no reservation issue opened.
- Budget: scope now frozen; reserve the final quarter of implementation/verification effort for adversarial checks and handoff.

## Result (single completion update)

Completed: the combined endpoint potential removes the additive `1/2` from
the old burn-in exponent and gives the exact odd/even denominator refinement.
The same-decay term count improves on 1,876 of 3,296 declared parameter cases.
Eight new test groups pass normally and under optimized Python; isolated
reproduction and the existing selected-record checks pass. No new kappa.

Review: https://github.com/CrocSwap/integer-mult-bounds/pull/902

The final overlap refresh covered arrivals through #901 and the targeted
Gaussian/potential search. The remote main still equals the recorded base.
The base ledger records #5 as partially reviewed and #371 as unreviewed;
these wider predecessor reviews are not completed by this narrow audit.
All scientific changes are confined to this package; see VALIDATION.md.

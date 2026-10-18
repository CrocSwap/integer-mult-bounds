# Conditional paid-balanced transfer with nullity banks

Under the explicitly retained all-size contracts, this composition supports
`T(n) = O(n (log n)^(1-kappa))` with

    kappa = 118877394946471 / 200000000000000000
          = 0.000594386974732355.

This is about 0.0702% above pinned PR163's 0.000593970203079492.
It combines PR163's fused complex supplier and paid balanced positional transfer
with the PR161 completed-core nullity-bank bit refinement. Gains are not added.
The resulting supported saving is complex-limited.

## What changes

For PR161's bit word, eighteen explicit four-coordinate blocks and three explicit
24-coordinate blocks each partition Fin72. Applying completed-core bank sharing
removes exactly 5720 rank60 exterior children while retaining all other children.
The normalized volume is 66364/3, rank mass 1590800, deficit 1936, maximum child22.
The paid bit moment and positive atom toll yield ordinary saving
151223451172976757106049 / 250000000000000000000000000,
which clears the PR163 complex supplier. The full scalar, router, group and row
bills are retained; all47 strict constraints and seven margins pass.

## Reproduce exact arithmetic (Python3.11+, standard library; assertions enabled)

Obtain two separate source snapshots at these immutable commits:

- PR161: https://github.com/eumemic/integer-mult-bounds , commit
  d14e29157bc905be1ced0776dd893d0714013f3a.
- PR163: https://github.com/chafreaky/integer-mult-bounds , commit
  e1813796ef5c3ca38c5dd7b9e8d81b3908ff5997.

The verifier requires Git checkouts pinned to those exact commits, with unchanged
tracked sources. A reviewer can acquire them using Git; the submitter can upload
this folder using GitHub's website without using Git locally.

    python3 -B research/balanced-nullity-banks-163/verify.py --pr161 /path/to/pr161 --pr163 /path/to/pr163

The verifier does not download or modify sources. It reconstructs the packed
ledger, proves the finite coordinate partitions by enumeration, recomputes the
bit moment using two interval implementations, checks its adjacent-grid control,
recomputes the PR163 complex moment, and replays the unchanged paid-balanced
assembly and full finite bill against expected.json. It rejects the next final
10^-18 grid point at these fixed certificates and parameters. This is not a claim
of global optimality. The verifier checks arithmetic; it does not substitute for
upstream physical-word verification.

## Lean scope

BankAndBalanced.lean is a single-file Mathlib-importing snapshot of existing
proof bodies: actual split-projector address interchanges, explicit partitions,
weighted endpoints, arbitrary dirty-content semantics, PR161 packed inventory,
and the47 finite arithmetic guards. See PROOF-ORIGINS.json for provenance.
It does not assert an all-size multiplication theorem. The bit inventory theorem
is proved alongside actual bank endpoints; connecting them to the full physical
multiplier still uses the contracts below, not merely the histogram arithmetic.
The Lean version is4.33.0. The compatible Mathlib commit is
`db584cd6d46c92f209a44c0f1c829460d327499d`. VERIFICATION.json records the
independent source replay and axiom audit. In that Mathlib environment, run
`lake env lean research/balanced-nullity-banks-163/BankAndBalanced.lean`.
The52 audited theorem names are listed in AUDIT-TARGETS.json.

## Dependency and publication scope

This is an additive research package. It depends on the unmerged PR161/PR163
snapshots above and changes no existing source. A PR to CrocSwap/main should
explicitly state those dependencies; it does not silently import their entire
diffs or claim they are already merged.

The completed all-input word, split-frame charts, invocation/stage cover,
weighted local-ring implementation, arbitrary-width complete-spectator routing,
borrowed-row restoration, paid layout applicability, precision/recovery,
prime supply, uniform setup and sharp fixed-tape analytic transfer remain
inherited all-size contracts. PROOF.md states these boundaries. This is a
conditional finite witness, not a fully formalized unconditional multiplier.

See NOTICE and LICENSE for attribution.

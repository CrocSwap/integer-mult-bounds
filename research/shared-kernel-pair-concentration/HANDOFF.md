# Research handoff — 2026-10-16

## Publication refresh

At the 05:08 UTC publication refresh, pending PR2863 at
`34328b1d5e5bebac62d5cabec993dfbfd7b2123f` reported the stronger T185 saving
`0.001720100805416885927944 - 10^-46 - 10^-70` and a fixed-inventory packing
optimum. Its body, pinned README, review list and exact-head check list were
inspected; its complete certificate was not replayed here. This T74 package
is a verified improvement over its pinned baseline, superseded in reported
kappa, with no current-record claim. See `PUBLICATION-REFRESH.json`.

## Best verified result

Conditional multiplication exponent saving:
`kappa = 0.001720097402339781716060 - 10^-46 - 10^-70`.
Exact rational and 70-place terminating decimal: `CLAIM.json`.
Exact improvement over the reproduced PR2857 headline:
`48353434319693/62500000000000000000000 = 7.73654949115088e-10`.
Complete strict release, independent source-event/owner audit and independent
directed-integer moment checks pass. The construction is two interleaved T37
copies plus one width-seven transfer; complete delta `H2+H16-2H9`.

The last paginated census at 2026-10-16 04:19:17 UTC found 541 open PRs, with
PR2857 still the strongest comparable construction identified. PR2858 has no
kappa claim. Exact source: PR2857
`0b2e2537b368a0cade07ce3f71452ea018ebe394`. Final main:
`d311a18c6061af67d0aa35cbeced605b8b7472ed`. Reviewed main still selects PR1094,
`836330098538459/500000000000000000`; do not replace that reviewed record.
Detailed PR review/check coverage is bounded and disclosed in FRONTIER.json.

## Executed validation

The initial PR2853 baseline (`d01045dfb67428679618027dff552f1d032fa999`)
passed its complete release with four fresh native chains (838.88 seconds).
Its manifest SHA256 is
`44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be`.
The first improved candidate also passed but was superseded during the run.

The PR2857 baseline passed its documented portable full replay twice. The second
run used its exact pinned numpy/scipy/sympy/mpmath/gmpy2/psutil requirements
in a separate Python 3.12 environment and took 499.15 seconds. It freshly
ran two current native chains and authenticated two older chains and the
retained parent proof by complete source hashes. The final candidate reuses
those unchanged current chains and passes its complete admission/release in
493.89 seconds. Its complete tree and final rational are checked by
`verify_release_binding.py` against the reproduced baseline.

Actual inherited rejecting controls: 119 admission, 12 bit, 25 controller,
8 owner and 6 geometry; the outer has 63 strict rows and 17 rejecting controls.
Independent new owner checker rejects four role corruptions; exact moment
checker rejects the old doubled profile at the candidate endpoint and the next
endpoint grid point. The portable package additionally rejects changed source
bytes. Full original local/kernel/native checks remain required.

Exact commands, exit codes, environment variables, elapsed times and log hashes
are in `evidence/run-logs/`. Receipt/source hashes are in CLAIM and evidence.
`README.md` supplies bounded and full reproduction commands. The top-level
`reproduce.py` orchestrator was assembled from those successfully executed
constituent commands; it was not rerun end-to-end a third time. Its constituent
full baseline, full candidate and final binding were executed separately.

Required `make verify` and `make frontier1094-verify` failed on unchanged main,
including final d311a18c6. See REPOSITORY-CHECKS.md. The new registered package
passes. No expected hash was changed to bypass the historical-source failure,
and no verifier predicate was weakened. No fresh Lean build or hosted CI pass
is claimed.

## Workspace and artifacts

Run root: `/workspace/scratch/bc9e58970b2a`.
Focused branch: `research/two-swap-exponent-20261016` in `integer-mult-bounds/`.
Only `research/shared-kernel-pair-concentration/` is committed as the new result.
The review patch records its exact commit and parent.

Important retained paths:

- `newer-frontier/replay-pinned/`: pinned PR2857 full replay and fresh natives.
- `pair-candidate/`: generated literal input and independent receipts.
- `pair-admission/`: complete derived package, discovery, frozen strict release.
- `replay-pr2853/`: initial complete cold baseline.
- `candidate-complete-release/`: superseded two-swap strict release.
- `superseded-two-swap-package/`: source-bound reproduction of that earlier result.
- `frontier-snapshot/`, `frontier-final/`: direct paginated API responses.
- `run-logs/`: all successes and failures, including development mistakes.
- `.venv/`, `.venv2857/`: isolated environments; dependency pins are saved.

The saved archive contains the focused patch, PR description, full derived
supplier, pinned dependency packages, command records, frontier snapshots and
superseded research. It excludes reconstructible large native intermediates.
No pre-existing work or upstream sources were removed or edited.

## Failed and bounded searches

See EXPERIMENTS.md and experiments/. Fixed-boundary quartet maps have rank
three/nullity one, so invertible raw-dirt mixing alone cannot supply a second
zero compensation column there. This is not a global circuit obstruction.
The PR2853 pair census found two improving swaps; that result was superseded.
The PR2857 same-call census screened 16,671,312 pairs with zero moves. Multi-role
paths, different orders, families and local words are outside that negative result.

## Next work and publication

No additional large packing search is justified by this session. Independently
reproduce PR2863 and its claimed fixed-inventory optimum before reopening that
gap, or address a named all-size obligation in PROOF.md. Refresh GitHub first.

The initial packaging lacked an available fork. Browser authentication later
succeeded, `digitalis-p/integer-mult-bounds` was created, and the user approved
adding that public fork to the existing GitHub app's selected repositories.
The scientific package was uploaded on `research/two-swap-exponent-20261016`.
Remote commit `b39aa97a6f4e6f784ebbde0d5f7dd73a3d70952c` has exactly the frozen
local scientific tree `2921cc364eabb7f9ed0d24830cbd6ca45f437103` and original
parent `d311a18c6061af67d0aa35cbeced605b8b7472ed`. This documentation refresh
labels the intervening stronger proposal before opening the review-ready PR.
No result is merged or claimed maintainer-accepted.

All inherited all-size compiler, common-label/mutable-source, hosting,
precision/tape, exact-recovery, analytic-transfer, corrected recurrence and
bit H1–H5 assumptions remain. Finite success is not the complete asymptotic
multiplication theorem. This result is not a measured runtime speedup.

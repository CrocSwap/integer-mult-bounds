# Analytic D6 four-puncture capacity18

For a33-root projective axis fiber of an orthogonal E8 root plane, delete
FOUR mutually orthogonal roots in that same fiber. Every remaining subset
of binary label rank at most six has at most18 roots. The bound is sharp,
and an actual18-label support attains it in the fixed P112 configuration.

[PROOF.md](PROOF.md) replaces PR3267's complete support-space census as a
mathematical premise. It uses a32-root affine quadratic model plus one
exceptional root, proves that every twenty-point section meets the puncture
at least twice, and characterizes equality. Exact finite checks bind the
model to all7560 ordered orthogonal root pairs and every legal puncture.
The separate checker corroborates all10795sixspaces in one canonical fiber,
without rerunning the historical896fiber census.

The numerical capacity18 is existing work. This adds its analytic proof,
equality classification, structural source binding and literal sharpness.
Two-puncture31-root fibers are outside scope. No new shortening threshold,
caller, full C5, supplier, selected-frontier update or kappa is claimed.

## Reproduction

From the repository root, with standard-library CPython3.12:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/d6-punctured-capacity18
```

The three direct commands in [VERIFY.json](VERIFY.json) also run in an export
containing only this package and its declared geometry input, without Git.
Primary expected output is `PASS_D6_ANALYTIC_CAPACITY18`; separate output is
`PASS_D6_INDEPENDENT`; controls print `PASS_D6_CONTROLS source=7 hypotheses=4`.
[RESULT.json](RESULT.json) fixes the full root-order indices, labels' basis,
punctures and actual fixed-P112 attaining support.

The fixed source inventory authenticates live geometry before execution.
[SOURCES.json](SOURCES.json) also records two byte-identical PR3267 payloads
for attribution. They do not execute or supply a missing capacity theorem.
No pending-PR Git object is required by direct exported replay.

## Evidence and limits

Written proof and exact finite model binding are internal computational
evidence. Independent human and proof-kernel approval, selected cold replay,
Lean, Docker and the old896fiber census are unrun. The finite binding uses
all canonical punctures and exact simple-reflection label transport;
it does not assume every arbitrary binary support fills its closure.
Checks and runtime deviations are in [ENGINEERING.md](ENGINEERING.md).

The baseline is463113d675af7410ac91d53a4fed51ec6494eb9a, guidance revision6.
Initial public overlap covers329open PRs and2123Discussion records through
20:38Z, with complete pagination. Closed work, code diffs and unpublished
results are not exhaustively searched. Two unreserved candidate collisions
were resolved before computation; [TASK.json](TASK.json) records actual scope.
Concurrent A2 joint32, mixed5/5/6 cut40, original-rule caller and global C5
charging investigations have distinct predicates; no sibling result is used.

## Open next questions

The structured questions and first steps are in [TASK.json](TASK.json).
Formalize the affine-radical proof and finite binding in a proof kernel.
For any caller application, first verify four orthogonal deletions in the
same actual fiber. A two-puncture fiber does not inherit18. No further
construction round is proposed here.

Credit Nick Petalas/PR3267 for the original18capacity and finite dependency,
David Arias's retained quadratic model, the root-simplex/E8/P112 lineage
including joaqcoo, and DreamingOfClouds/PR3154 for the reduction motivation.
Frozen predecessor sources and the selected result remain unchanged.
Apache-2.0.

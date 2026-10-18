# Binary-rank-six endpoints exclude one more P112 profile

The actual historical TWOSIDE `(6,3)` profile `2,6^5,7^3` is impossible
over every characteristic-zero field. Delete its three unrestricted last
pieces. At least three code dimensions remain on `2,6^5`.

The new shortening theorem uses four binary-rank-six endpoints and a common
small-support union of at most 22 coordinates. Their span meets the P112
evaluation code in dimension at most two. The support-only A3 count reaches
`80=80` and cannot prove this. At equality, each endpoint must contain sixteen
coordinates whose binary span already has rank six, but has only those
sixteen live coordinates. Thus four endpoints can supply at most 64 support
incidences, contradicting the required 80. See [PROOF.md](PROOF.md).

This follows the released deletion handoff in
[Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156)
and Nick Petalas/PR3211. It is one named profile exclusion, not full C5,
`C(P112)>=64`, supplier admission or a new kappa. The selected frontier and
frozen inputs are unchanged. Evidence is author-checked, not independent
human or proof-kernel review.

## Evidence and reproduction

[RESULT.json](RESULT.json) records the A3 extension orbits, the complete
2,025-frame enumeration counts, all 240 extremal binary spans and live
closure masks, the 788,035-flat capacity census, historical profile and
retained geometry.
Twelve behavioral groups include a separate root-lattice label construction,
level-by-level frame enumeration, Gaussian binary-span oracle, a losing
support-only control and source/semantic rejection controls.

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p112-a3-rank-six-shortening
```

Direct commands are `python3.12 -B research/p112-a3-rank-six-shortening/verify.py`
and then `test_verify.py` in the same directory. The verifier writes nothing
by default. An optional `--output /absolute/external/new-file.json` creates
an exclusive external receipt. Source-only exports must retain the package
and both declared `VERIFY.json` inputs under the same relative paths.
No pending PR Git objects are needed for direct replay.

[SOURCES.json](SOURCES.json) binds exact sources and the unchanged retained
geometry. [TASK.json](TASK.json) declares the handoff-first scope change.
[CHECKS.json](CHECKS.json) records the environment and verification evidence.
[ENGINEERING.md](ENGINEERING.md) records boundedness and implementation limits.

## Open next questions

Before another geometric extension, reconcile the seventeen historical
`(6,3)` profiles with exact public exclusions and identify a still-open
caller. The blocker is that the historical survivor list is not a current
proof-disposition ledger. The structured first step and stop rule are in
[TASK.json](TASK.json). This result does not justify another construction
round without such a caller.

## Credit

DreamingOfClouds/PR3154 supplied TWOSIDE and the original decoder-floor
reduction. Nick Petalas/PR3211 supplied the two-piece deletion handoff;
PR3164, PR3175 and PR3173 supplied the retained root-simplex, orbit and
coordinate methods. The exact geometry file is an unchanged copy from
`research/p112-simplex-coordinate-bound/vendor/geometry.py` at main
`463113d675af7410ac91d53a4fed51ec6494eb9a`. The original source and its
E8/P112 lineage, including joaqcoo's model, retain their credit. The binary
A3 equality obstruction and this three-piece deletion application are new
here. New work is Apache-2.0. Development used substantial automated
assistance.

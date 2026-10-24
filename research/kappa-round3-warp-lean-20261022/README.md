# Conditional kappa 0.00302176 with fresh Lean certificates

TL;DR: the changed joint helper/native-map construction supports conditional
**kappa = 9443/3125000 = 0.00302176**, improving PR4610's frozen 0.00302152 by
**0.00000024**. This is a changed paid profile, with the complete controller,
completion, uniform compiler and outer ledger included. The raw complex root
lies in `(0.0030217758,0.0030217759)`; it is not the claimed saving.

The actual mathematical witness is in
`../kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`. Its canonical payload SHA256
is `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
The guarded patch changes 26 arbitrary helper entrances, 316 scalar contact
frames, 20 warp frame pairs and 20 native G maps. All scalar opcodes and their
coefficients/order, public main endpoints, helper exits and owned jobs remain.

The local paid profiles are:

```
PR4610: {1:2201,2:412,3:506,4:135,5:36,8:8}
new:    {1:2201,2:412,3:510,4:127,5:40,8:8}
helpers:{4:28,7:7,8:47,9:326} (same complete rank census)
```

Four pairs of rank-four jobs become rank-three/rank-five pairs. Strict
concavity gives `old(t)-new(t)=4*(2*4^t-3^t-5^t)>0` for every `0<t<1`.
The whole p16 construction still contains 64404 paid calls and 10928 independent
productive fields. No query, idle, diagonal, centre or completion cost is waived.

## Verification coverage

The companion native checker replays both orientations on all 632 independent
persistent input columns with two retained interpreters. Exact physical lowering
checks the 20 changed native maps on all 512 columns, all 180 actual warp
classes, all 105 newly occurring paid frame pairs and all 26 changed helper
interfaces, including their absolute phases in both orientations. Exact prior
phase evidence is reused only for unchanged source-bound data.

This package transcribes and checks all 4429 binary frames, 72 invertible maps,
2863 paid classes, 180 warp classes, all 408 actual helper interfaces, and every
event of both 21449-event words in Lean. Both directions are split into eight
proof files; each of their 168 segments carries an ordinary `decide` proof.
No proof is inferred from discovery solver status.

`AnalyticGain.lean` proves the strict real concavity gain.
`NumericalMoments.lean` proves actual real-power contraction and both charged
tails at tested saving `0.00302177`, using log/exp remainders and exact rational
arithmetic. Its conservative productive-minus-paid margin exceeds 0.00144974696.
`CompilerCapacity.lean` proves the real complement-capacity bounds.
`ArithmeticCertificate.lean` checks all 54 strict outer predicates and four
functional predicates, transcribed from their source formulas, together with
the finite integer compiler inequalities. The compiler keeps
`N=2^31385200000000`; its expanded word is algorithmically defined and is not
materialized. The claimed saving leaves strict compiler/outer slack.

The final authority for an actual completed Lean replay is
`LEAN-VERIFICATION.json`, its source/log/output hashes and genuine module logs.
Only status `PASS_SCOPED_LEAN_REPLAY` denotes completion. Partial receipts do not.
The pinned environment is Lean4.21.0 (release commit 6741444a63ee), mathlib
308445d7985027f538e281e18df29ca16ede2ba3. No `sorry`, custom axiom,
`native_decide` or kernel-checking bypass is used. Printed axiom reports are
checked against `{propext, Classical.choice, Quot.sound}`.

## Reproduce

From the repository root, first run the companion `regenerate.py`,
`verify_candidate.py` and `phase_check.py`. Repricing and generator commands:

```
python3.14 -B research/kappa-interface-round2-20261022/price_profile.py --native research/kappa-round3-warp-20261022/NATIVE-VALIDATION.json --kappa .00302176 --out research/kappa-round3-warp-20261022/ARITHMETIC.json
python3.14 -B research/kappa-round3-warp-lean-20261022/prepare.py
python3.14 -B research/kappa-round3-warp-lean-20261022/replay.py
```

Use the global Python3.14 executable required by this workspace; no virtual
environment is needed. The retained PR4610 proof package supplies the pinned
Lake configuration and proof-audit implementation. Its `.toolchain` and `.lake`
directories are ignored installation/cache locations. Install the pinned Lean
release there, run its Lake dependency/cache setup, and make the pinned
`Mathlib.Analysis.Convex.SpecificFunctions.Pow` module available in that cache.
The replay checks dependency Git revisions and tracked source cleanliness.
It compiles in this new package with this package first on `LEAN_PATH`.

Default replay is fresh. Explicit `--resume PATH` validates earlier successful
module source, compiled output, genuine log, axiom reports and dependency
hashes before reuse; it is not independent attestation. `--only` produces a
partial receipt. Receipt files must not be regenerated concurrently with a
proof replay. Regenerating native receipts changes timings and therefore their
hashes: rerun repricing and `prepare.py` before the Lean replay.

## Scope, attribution and open questions

These are scoped Lean proofs of the finite binary frame/invoice certificates,
real moments, capacity and rational compiler/outer predicates. The JSON-to-Lean
transcription and source hashes are an explicit Python boundary. Amplitudes,
absolute phases and the free noncommutative endpoint remain separately checked
by the retained exact Python engines. Uniform physical execution, whole-job
normalization, fixed-tape movement, permitted owned erasure, precision, stock,
analytic decomposition, prime avoidance and exact recovery retain the
predecessor hypotheses. This is not an unconditional or fully formalized
integer-multiplication theorem, a practical speedup, or a selected-frontier change.

Cao Yifan's PR4610 supplies the starting warp geometry and Lean generators;
Cinna Davis's PR4470, Dugongue's transported frames, zxv's native/compiler work,
Jacob Alan Sussman's mixed-target recursion and their credited predecessors
remain the source lineage. Pierre-Loic Doulcet's concurrent PR4626 at
c665f908fc991aa558ea8a8cd33e9ad26f97a22d reports a different helper621 boundary
giving 0.00302156. That existing result is credited, not rediscovered here.
Its direct combination with this witness worsens the moment; see the saved
screen. The new joint search and certificate stand on their own changed profile.

Open next questions: change the scalar word or helper graph beyond the present
contact model; test coupled helper/controller types with every restoration bill;
and formalize the native amplitude/phase and complete compiler transfer boundaries.
The saved finite-model optimality reports do not settle those questions.

Signed-off-by: Cao Yifan. Substantial OpenAI Codex assistance. Apache-2.0.

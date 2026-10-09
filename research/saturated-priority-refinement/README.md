# Saturated frame priority refinement

Full verification passed on research commit `06f174c48b06856a3d6c96ee232dc3fc44145c39`: `make -j1 verify` and package `verify.py --full` completed in 3663.98 seconds with no source drift. All 45 GitHub checks on that research commit passed. See [validation.json](validation.json) for commands, log/archive hashes and scope. The inherited general interfaces remain conditional.

Under the inherited analytic, stopped-product and fixed-tape interfaces,
κ = 54642831733/500000000000000 = **1.09285663466e-4**.
This is **0.00418096% above** updated PR114 (7dfa16e), and above PR120.
This is a small finite improvement, not a new asymptotic architecture or
unconditional theorem.

The PR117 DAG, carrier matching and bit supplier remain unchanged. We use
PR114/120 saturated placement with its exact rational priority and vary only
its final equal-priority ties. Seed 1 from a bounded 16-seed search produces
4,708 deferred roles, compared with PR114's 4,706; all 28,705 physical roles
remain paid. The complex saving is 27327417/250000000000 = 1.09309668e-4.
The full child profile determines the improvement; deferral count alone is
not the objective.

Run `python3 research/saturated-priority-refinement/verify.py --full` for
source pins, producer and bit replay, exact assembly, independent reflected
frame audit and adversarial controls. Then run `make -j1 verify` for inherited
repository coverage. General proof scope and credits are in PROOF.md.

The expanded readout unit-shear repair from PR118 is retained. All 47 exact
constraints and seven margins, next-grid exclusions and the old-profile
negative controls are required. This package makes no global-optimality claim.

Prepared by Rohan Arun with OpenAI Codex assistance; credit eumemic for the
PR117 graph and PR114/120 saturated construction, Avi Eisenberg, Swapnil Jain,
icekylinx, Zhihao Chen, RaD/hipotures, Aurel Prosz/Paureel, Rohan Gupta and all
predecessors. Parent headers and licenses remain intact.

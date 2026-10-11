# Early reset and response-kernel composition

Conditional kappa = 0.001133508328719775. Eleven early resets give R747. After remapping the PR435/417 kernel and deriving eight additional rank-four relations, 118 entries give entrance rank 160. The 727 complete width-64 helper banks per stage give 14,223 live and 14,232 physical families. No gains are added: the final emitted program is repriced.

Run `python -B research/e8-early-reset-kernel/verify.py /absolute/new/output` using the Python standard library. This freshly replays the complete earlier-reset construction and all upstream phases, then applies and independently audits the kernel composition.

At this draft update, all changed scalar/frames/source-span checks, global banks, two moments and the finite assembly passed. The full uninterrupted wrapper and CI for the new 118-entry selection are pending. Prior 110-entry Python 3.11 and 3.14 receipts remain historical evidence with their exact code/source hashes.

All-size interfaces remain conditional assumptions; no unconditional multiplication theorem or new Lean proof is claimed.

# Twelve early resets, response cancellation and frame retiming

Conditional kappa = 0.001134386495022041. Twelve early resets reduce R758 to R746. Revalidating the response kernel after physical reuse leaves 116 entries with entrance rank 152 and 115 donor slots. Ten exact frame changes preserve the primitive ADD sequence. The 727 complete width-64 helper banks per stage give 14,223 live and 14,232 physical families. The final emitted program is repriced from scratch.

Run `python -B research/e8-early-reset-kernel/verify.py /absolute/new/output` using the Python standard library. This freshly replays every upstream phase and the pinned eleven-reset construction, applies RESET12.json, SELECTION.json and RETIMING.json, and independently audits the complete result.

Before this draft update, all changed scalar/frame/source-span checks, both global programs, independent bank audits, two moments and finite assembly passed. Packaged reconstruction reproduces the exact tested word and rejects eight mutated witnesses. The new uninterrupted full wrapper and GitHub CI are pending. Historical 110-entry and 118-entry full Python 3.11/3.14 receipts remain explicitly bound to earlier source hashes.

All-size interfaces remain conditional assumptions; no unconditional multiplication theorem or new Lean proof is claimed.

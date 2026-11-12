# Verification

The direct CPython 3.12 replay exited zero in 0.64 seconds. The relocated Git-free replay with an empty inherited environment exited zero in 0.52 seconds. All four receipts matched byte for byte.

The primary replay tests 47,490 typed cuts across the 15 fixed direct MOVE placements and finds zero legal ADD slots. The independent replay reads all 76,466 events, verifies all five old paid and scalar windows, and matches all ten commuting intervals and original partners. It checks the owned lifetime of role 1555 and confirms no endpoint hit even with an arbitrary direct MOVE clock inside each original window. The engines' built-in controls exercise commuting and noncommuting ADDs, COPY guard behavior and owned lifetime barriers.

[Provenance](PROVENANCE.json) · [Replay command](README.md) · [Agreement](receipts/AGREEMENT.json)

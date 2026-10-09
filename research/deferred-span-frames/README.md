# Deferred retired-span reconstruction

**Conditional κ = 5.279858969335e-5 = 1055971793867/20000000000000000.**
The bit saving is `26400688765809/500000000000000000`. The selected finite
construction uses **130,427,779 wires** and axis roles **26,409 / 34,749**.

The new h25 compiler clears a redundant pending role after reserving an
exact representation of its future value on retired carriers. It reconstructs
that value with paid literal XORs at the future use. An ordered Gaussian
basis exposes 23 three-carrier witnesses that the earlier one/two-carrier
search missed. The result saves 23 h25 roles, improves the preceding aligned
candidate's saving by about 0.0312%, and retains its exact h23 word/profile.

All reservations, reconstruction XORs, frame changes and exterior banks
are charged. Arbitrary dirty scratch is restored. The finite mechanism and
conditional scope are detailed in [PROOF.md](PROOF.md); inherited graph
and exchange arguments remain in [partition-proof.md](partition-proof.md)
and [exchange-proof.md](exchange-proof.md).

## Reproduce

```sh
python3 research/deferred-span-frames/verify.py
```

Requires Python 3.11+ and C++17. The gate regenerates both words, checks
dense scalar supports, tests the two/three-carrier primitive with negative
controls, replays the full dirty basis in both orientations, independently
rebuilds every transition and exact CRT profile, and verifies the complete
paid recurrence, all 47 inequalities, seven margins and next-grid exclusions.
The independent arithmetic checker uses separate rational formulas.

`SOURCE.json` pins the complete selected inputs and inherited archives;
verification never refreshes pins. `pin_sources.py` is an explicit maintainer
freeze operation. `validation.json` and `verification.log` record the selected
gate, while `certificate.json` contains exact numerical values and margins.
Ordinary verification writes its run log outside the repository and leaves
the tracked receipt/log unchanged; `verify.py --record` explicitly records
a new run after a maintainer freezes the inputs.
Fresh generation must leave every checked deterministic artifact unchanged.
The engine extension is reviewable in `ENGINE-PATCH.diff` and its complete
source in `storage_engine.py`. Root integration receipts are separate outputs.

## Credits and limits

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance.
Builds on Chafik Boukhalfa (PR71/79/84), Rohan Arun (PR65/67/78/82),
Dominik Scholz (PR63/68/76), Alejandro Zarzuelo Urdiales (PR70), eumemic
(PR57/69), Rohan Garg (PR59), Avi Eisenberg (PR62), and retained contributors.
Original Git source archives, Apache-2.0 licenses and notices remain unchanged.

The all-size compiler, analytic transfer, fixed-alphabet tape, precision,
routing, prime selection and exact recovery hypotheses remain assumptions.
This is a finite conditional witness, not an unconditional multiplication
theorem, a measured runtime speedup or a global optimality claim.

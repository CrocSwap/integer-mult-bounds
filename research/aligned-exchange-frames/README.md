# Aligned recursion and indexed carrier exchanges

**Conditional κ = 5.2782144231390e-05 = 5278214423139/100000000000000000.**
The bit saving is `52784930333197/1000000000000000000`. This verified finite construction uses
**130,468,512 wires**, with axis role counts **26,409 / 34,772**.

It improves the previous PR74 saving by **1.8350912%** and the pinned PR84
claim by **0.9773150%**. These are historical comparisons, not a global
optimality claim. Both complete prior child lists are strictly excluded at
the new accepted bit saving, along with the pinned PR71 and PR82 profiles.

## What changed

- Align and split six top-level pairs for h23 and nine for h25.
- Choose deeper split vectors `[first6,1,1]` and `[first9,1,1,2]`.
- Use half-plane row/column coarse sums for three levels, then columns.
- Compose core node ordering with PR84's future basis completion, exact
  candidate indexes, three single-exchange and three two-cycle passes.
- Route h25 outgoing uses by descending future deadline; retain h23's
  baseline routing. Price transitions in the explicitly selected coordinates.

Every resulting graph, dirty physical word and ordered fixed-basis profile
is checked. [PROOF.md](PROOF.md), [partition-proof.md](partition-proof.md),
and [exchange-proof.md](exchange-proof.md) give the identities and scope.
The independent checker reconstructs all paid parts and all 47 inequalities
and seven margins using separate rational logarithm/exponential formulas.

## Reproduce

```sh
make aligned-exchange-frames-verify
```

Requires Python 3.11+ and a C++17 compiler. This regenerates both words,
checks dense scalar supports, replays every ordinary and arbitrary dirty
basis vector in both orientations, rebuilds literal frame transitions and
CRT profiles, then checks exact moments and next-grid exclusions.
Verification never refreshes source pins. `pin_sources.py` is an explicit
maintainer freeze operation; `SOURCE.json` binds the selected construction.

The exact values, profiles, strict margins and arithmetic cutoffs are in
[certificate.json](certificate.json). Configuration and word hashes are in
[selection.json](selection.json). Fresh-run and CI evidence are recorded
separately; earlier package verification does not stand in for this gate.

## Credits and limitations

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance.
The construction composes work by Chafik Boukhalfa (PR71/79/84), Rohan Arun
(PR65/67/78/82), Dominik Scholz (PR63/68/76), Alejandro Zarzuelo Urdiales
(PR70), eumemic (PR57/69), Rohan Garg (PR59), Avi Eisenberg (PR62), and the
other retained contributors. Exact original Git sources, licenses and
notices remain under `references/frame-compiler/pr69`, `pr71`, `pr82`, `pr84`.

The inherited all-size compiler, analytic transfer, routing, precision,
prime selection, exact recovery and fixed-alphabet tape hypotheses remain
assumptions. This is a finite conditional witness, not an unconditional
multiplication theorem or measured runtime speedup.

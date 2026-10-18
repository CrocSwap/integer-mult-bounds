# Candidate and overlap record

Seed 27, complex-supplier track, exact base ba82555c64e1879e4b7decce28186f208fcb8262. Three candidates were identified before the main experiment:

1. Fixed-frame-slot commuting ADD transpositions of the actual selected R480 A/B stages: chosen, then strengthened to the complete first-crossing closure argument.
2. U8 echo/Steinberg simplification: rejected after reading [PR1115](https://github.com/CrocSwap/integer-mult-bounds/pull/1115), which already replaces four three-gate B-stage echoes by two-gate exact maps.
3. Sparse cleanup refactorization: rejected after reading [PR1119](https://github.com/CrocSwap/integer-mult-bounds/pull/1119), which supplies two-sided Markowitz LPR cleanup factorization on U8.

Live Curiosity Bot GitHub queries on 2026-10-13 included `"commuting" "frame"` and `"adjacent" "complex"`, restricted to this repository's PRs. The closest result, [PR815](https://github.com/CrocSwap/integer-mult-bounds/pull/815), was read live. It proves fixed-sequence frame optima and performs commuting-reorder annealing with frame re-solving on PR626/741. We do not claim a new general commuting-search idea. Our source word is the newer selected R480 construction; our conclusion is an exact reachability obstruction under fixed ordered frame slots, proved by enumerating every possible first boundary crossing. Re-solving the frame assignment is explicitly excluded.

[PR309](https://github.com/CrocSwap/integer-mult-bounds/pull/309) describes older dirty-response commuting schedules. [PR933](https://github.com/CrocSwap/integer-mult-bounds/pull/933) studies bit-word relocation and Steinberg rewrites. Neither supplies this source-bound R480 closure certificate. This targeted search is not a claim of exhaustive literature coverage.

A fresh final query at 18:56 UTC returned [PR910](https://github.com/CrocSwap/integer-mult-bounds/pull/910), which was then read live. It enumerates 56 single slides, 1,372 paired slides and four tie-order swaps for eight SW4 compensation pre-reads, preserving cost on that older word; triples and larger slide groups are explicitly excluded. This is important prior finite scheduling work. The present source and class differ: all A/B commuting ADD occurrences in the R480 word, closure under arbitrarily many legal moves, and an exact first-crossing certificate with frame slots held fixed. We do not claim a result about PR910's alternative insertion frames or other excluded mechanisms.

The same final metadata query reached PR1127 (bit 3-to-2 rewrites). Upstream had meanwhile selected PR1094 at ce7ad1b6; the present result remains pinned to the PR1042 word at its stated base.

Concurrent work is kept separate: round22 uses CK helper butterflies; round23 proves the k8 cells' positive-lift 21-ADD minimum; round25 examines S6 cell relabeling and dirt/frame behavior; round28 inventories selected archive provenance. This package consumes the selected archive member as pinned data and does not claim any of those results.

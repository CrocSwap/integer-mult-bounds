# Candidate triage and prior work

Seed 24, complex supplier track; frozen base `ba82555c64e1879e4b7decce28186f208fcb8262`, selected-at-base PR1042. Three narrow candidates were considered before the main experiment:

1. Consolidate a selected set of existing per-register SCALE histories across complete A/B stages, with explicit boundary restoration and whole-stream pricing. Chosen; the blanket variant fails, while the deterministic selective variant saves 540 real primitives per orientation.
2. Search a single SCALE relocation. Rejected as overlapping [PR750](https://github.com/CrocSwap/integer-mult-bounds/pull/750), which exhausts 123 scales by 8309 positions for its pinned PR626 word and reports the profitable register-97 relocation.
3. Refactor the helper cleanup. Rejected as overlapping [PR1119](https://github.com/CrocSwap/integer-mult-bounds/pull/1119) and its two-sided cleanup work.

Fresh Curiosity Bot GitHub provider queries for scale absorption, diagonal normalization, and scale fusion were followed by reading PR750 and [PR1064](https://github.com/CrocSwap/integer-mult-bounds/pull/1064). PR1064 optimizes persistent diagonal state on a fixed small factory topology and proves a nine-shift minimum there. The present work credits that mechanism; it does not claim new diagonal-conjugation algebra or a general minimum. It instead emits a new full R480 stage construction with 63 selected register histories, exact restored endpoints, both orientations, unchanged paid frame events, and full scalar pricing.

[PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) supplies the stronger COPY-initialized and unit-coefficient lowering used for the main comparison. The original Horner pricing is retained as a secondary comparison, not the headline gain.

Concurrent round32 was explicitly coordinated: it optimizes one persistent helper gauge through the full PR1094 word while fixing all existing SCALEs, with an unbounded integer exponent search and paid entry/exit scales. This round relocates and consolidates existing SCALEs with a time-varying diagonal ledger; it does not perform that search or claim its savings. The newer live PR1094 frontier is not substituted into this frozen PR1042 experiment.

Other excluded active scopes were round22 dyadic butterflies, round23 fixed positive-lift core minimum, round25 cell relabeling, round26 legal adjacent frame-slot transpositions, round28 archive provenance, and round29 literal Clifford transition ranks. None is repriced or extended by this package.

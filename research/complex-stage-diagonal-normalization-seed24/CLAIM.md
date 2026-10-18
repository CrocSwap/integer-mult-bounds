# Seed 24 claim

At frozen base ba82555c64e1879e4b7decce28186f208fcb8262, investigate consolidating existing diagonal SCALE operations within the actual selected-at-base PR1042 R480 A/B scalar blocks: adjust ADD coefficients while carrying diagonal state, then restore the full map with explicit per-register boundary scales. Keep every paid climb event. Recount all scalar primitives including coefficient preparation/private clearing and boundary restoration, compare stronger available lowering, and verify both orientations and coefficient growth before claiming a gain. The blanket experiment is a priced failure; the final construction uses the precisely specified selective rule in PROOF.md.

This is distinct from a single-scale relocation (PR750), whole factory fixed-topology diagonal optimization (PR1064), generic cleanup factorization (PR1119), and concurrent round32's fixed persistent helper gauge on PR1094. No helper gauge exponent search is included. No new kappa or native admission is implied.

Prepared for @woklerx with substantial OpenAI Codex assistance; Apache-2.0.

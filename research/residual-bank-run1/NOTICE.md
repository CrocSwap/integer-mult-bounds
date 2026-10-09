# NOTICE

## Provenance

Package construction and the enumeration/schedule/arithmetic/verification code:
prepared for the CrocSwap/integer-mult-bounds queue with **OpenAI Codex
assistance**, 2026-10-10.

## Vendored sources (byte-identical, sha256-pinned in SOURCE.json)

- `interval_moment.py` — PR200's exact rational interval moment engine
  (Chafik Boukhalfa, `research/paired-cube-diagonal-bit-168/arithmetic/`,
  package Apache-2.0).
- `paired_cube_assembly.py` — the unchanged balanced assembly
  (PR168-v4/PR184 lineage via ikeboy's PR193 tree; original attributions retained).
- `banks.py` — incidence colouring helpers (Evan McKinney, PR197, Apache-2.0;
  vendored via rohanarun's PR205 package).
- `references/pr193-source-assisted-v4.certificate.json` — ikeboy's PR193 complex
  supplier certificate (unchanged; its own credits and AI disclosures stand).
- `references/pr200-bit.certificate.json` — Chafik Boukhalfa's PR200 bit word
  certificate (unchanged).
- `references/pr205-packed.certificate.json` — rohanarun's PR205 packed-row
  certificate (unchanged).

All mathematical content of the vendored files is the work of their authors as
credited in the upstream packages. The new content of this package is the rank-22
enumeration (derived from the pinned PR200 word), the absorption schedule, the
retained-ledger arithmetic and the obligation statement.

## AI assistance disclosure

The new code, enumeration and text in this package were prepared with OpenAI Codex
(GPT-class model) assistance. The exact arithmetic is machine-replayed by
`verify.py`; the mathematical claims remain conditional as stated in PROOF.md.

Apache-2.0.

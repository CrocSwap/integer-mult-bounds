# Browser upload

PR title: **Attain the fixed-word packing optimum: conditional κ ≈ 0.0017201008054**

Branch: `research/shared-kernel-packing-optimum-20261015`

Use `PR-BODY.md` as the body. Create this branch from current main in `CrocSwap/integer-mult-bounds`; use the same branch for every batch.

- Batch 01: drag `F:/proof/up/kc57/01/research` at the **repository root** (80 files recursively).
- Batch 02: drag `F:/proof/up/kc57/02/research` at the **repository root** (80 files recursively).
- Batch 03: drag `F:/proof/up/kc57/03/research` at the **repository root** (5 files recursively).

Each batch preserves `research/shared-kernel-packing/` exactly. Upload the extracted files by dragging the named `research` folder. The intended union is 165 files; no existing research package is deleted. Each batch has at most 80 files recursively, every file is below 25 MiB, and the longest staged absolute path is 128 characters. The external `PREFLIGHT.json` verifies every staged byte against the final source manifest and records its digest. Intended `.json.gz` files contain compressed JSON proof data. Original licenses and notices are included.

After all batches are committed, compare with `MANIFEST.json` and run the fast offline verifier. Full replay is documented in README. This handoff prepares a new PR; it does not publish one or guarantee against browser/network errors.

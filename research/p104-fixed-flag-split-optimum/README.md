# Exact rational split optimum for fixed P104 flags

The eight flags in PR7748 have exact split-gather junk minimum **4,745**.
The single-gather minimum on these flags is **4,814**. A complete schedule
attains all 104 column minima, including **43** in source column 4, where
the predecessor attained 44. It uses 490 nonzero gather pieces and keeps
every diagonal and required odd zero.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [verify.py](verify.py),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).
The lower bound uses 4,715 fixed entries and 23 exact contradictions that
force 30 more. Two methods agree on all 1,400 equation subsets.

Use Python 3.12 and its standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-fixed-flag-split-optimum
```

Both modes print `PASS_P104_FIXED_FLAG_SPLIT_OPTIMUM`. There is no new
kappa or global flag optimum. Physical gather and restoration costs are
not supplied. All five framework assumptions remain.

## Open next questions

- Apply the same exact prefix equations to an available low-junk flag
  witness. The fixed flags here remain worse than the 4,216-entry witness
  reported in PR7689; that witness was not replayed here.
- Price the extra pieces and their restoration on a specified native
  carrier. This schedule uses 74 more nonzero pieces than active chains.
  A decrease in junk entries alone is not a paid supplier improvement.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

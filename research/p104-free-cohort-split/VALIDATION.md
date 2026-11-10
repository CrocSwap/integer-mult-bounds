# Execution evidence

The first complete local CPython 3.14.7 scientific run passed: full source reconstruction, all-input native maps, signed caller, exact prices, ordinary charges, precision, compiler/outer gates, chart columns and phase, complete finite native physical and signed-route replays, and mutation controls. Its receipt is the basis of RESULT.json. The subsequently added rank-histogram rejection control was executed separately against `prepare`; the final registered replay recomputes it with all other fields. The retiming counter implementation was clarified to use frame dimensions directly before that final replay.

Commands:

```
python3 -I -B research/p104-free-cohort-split/verify.py --out /tmp/kappa-free-cohort-first.json
/tmp/kappa-python312/python/bin/python3.12 -B scripts/research_package.py --package research/p104-free-cohort-split
python3 -B scripts/research_package.py --package research/p104-free-cohort-split --check-only
```

The registered replay uses isolated CPython 3.12.16 and the runner's fresh bytecode-cache namespace. REPLAY.txt records its final stdout. Its launcher line says outcome=partial because completion metadata was updated only after the successful run; scientific files and expected receipts were unchanged afterward. Frozen receipts are compared in full, and compressed words are compared by the complete canonical decompressed payload. The standalone proof engines require only the standard library. No Lean, Docker or historical full-suite replay is used. Source-aware engine reuse is not independent human or kernel review; exact limitations and remaining application obligations are in README.md.

Publication uses the exact package tree from a canonical-main research commit. A package-only publication commit is based on the account fork's older main because the available credential cannot push workflow-history changes. The scientific SOURCE base remains canonical main; a hosted PR merge includes that base. The package's entire scientific predecessor closure is committed and offline, so the standalone replay needs no unmerged Git objects. The PR records both commits and their package-tree equality, and distinguishes research-commit source-history checks from publication ancestry.

# Execution evidence

Two complete local scientific runs passed on CPython3.14.7, standard library, in the isolated research worktree. The first generated the full receipt. The final run checked every frozen receipt field and additionally rejected the two insufficient grids and legacy nonsmooth swap. REPLAY.txt is the final full stdout. Both runs included source reconstruction, all-input algebra, complete signed pricing/ordinary/precision gates, chart phase/columns, host-native physical replay and signed caller routes. No Lean, Docker, historical suite or concurrent artifact-regenerating replay was used.

Commands:

```
python3 -I -B research/p104-smooth-swap-split/verify.py --out /tmp/kappa-smooth-first.json
python3 -I -B research/p104-smooth-swap-split/verify.py
python3 -B scripts/research_package.py --package research/p104-smooth-swap-split --check-only
```

The repository metadata/pin check passed. Committed-byte/mode/source-history checks are run before publication and reported in the PR. Python3.12 is the registered hosted environment; no local3.12 run is claimed. The source's historical shell wrapper was not rerun wholesale: its authenticated constructors are replayed directly, and affected native, caller, price, precision and physical checks are run by this verifier.

Passing finite evidence and source integrity do not constitute independent human, formal-kernel or complete changed-source application approval. See README.md for the exact scope and remaining five-assumption/provider obligations.

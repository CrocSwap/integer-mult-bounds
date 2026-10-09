# Paid frame refinement of PR168

This additive package improves the finite conditional witness at PR168 commit
`98c115b53742b6613ad630de4d493f37b0119da7`, using PR169's frame plan as
the selected search starting point. It combines a bidirectional
operation-frame search with exact paid supplier refinement and deterministic
verification of both scalar words. See [RESULTS.md](RESULTS.md) for the
certificate-generated saving, active supplier and matched comparisons.

From the repository root, with Python 3.11 or newer:

```sh
python3 -B research/paired-cube-bit-descent/search.py
python3 -B research/paired-cube-refinement/verify.py
python3 -B research/paired-cube-bit-reuse/check_obstruction.py --check
python3 -B research/paired-cube-refinement/compare_pr169.py
```

The first command reproduces the frozen frame plan. The second reconstructs
the exact certificate and its numerical report. The third independently
checks why the existing bit gauges cannot reuse any eligible donor. The last
command independently checks PR169's bit plan and compares the two complete
profiles under the same refinement rules. Normal
verification is read-only. `--write` is an explicit authoring mode, not an
acceptance shortcut. Source files, the original PR168 tree and the selected
frame plan are pinned in `SOURCE.json`.

The package preserves PR168's scalar modules, arcs, operation order, gauge
stock and persistent register inventory. The search can lower a causal
prefix or raise a causal suffix of operations sharing a frame. Both moves
are priced by the complete boundary moment, including the change in the
fallback bill. The trusted checker accepts a plan only after exact support,
frame nesting, nondegeneracy, determinant and complete child-ledger checks.

The arithmetic uses the proof's exact rare-class upper bound and its full
direct fallback count, refines the coarse root with rational intervals, and
chooses the least paid atom exponent on the stated grid. The full finite
group, virtual scalar inventory, router, precision and row charges remain
present. All 47 balanced-assembly inequalities and seven final margins are
recomputed. Malformed plans, missing compensation, a missing partner, an
unsupported supplier, undercharged stock, an unpaid atom and the next
final grid point are rejected.

The complex word is checked on every source, target and dirty column over
the rationals using an injective packed representation with a recomputed
coefficient bound. Both shear directions and inverse cleanup are checked.
The bit word is checked on every formal column over F2 and against its
defining integer decoder. These strengthen the seeded replays in PR168.

This is a conditional finite witness. The inherited all-size tensor and
Clifford compiler, uniform weighted bit compilation, restored internal rows,
balanced positional layout, analytic recovery and fixed-tape interfaces
remain assumptions. There is no global optimality or practical runtime claim.

See [PROOF.md](PROOF.md), [REVIEW.md](REVIEW.md) and [NOTICE](NOTICE).

# Exact adaptive typed bills

A fixed-matrix test does not check every combination of allowed supplier rows.
This package constructs an exact certificate for a finite nonnegative rational
menu at each type. It either gives the exact worst unit-toll total under all
adaptive choices, or gives one legal fixed policy that fails contraction.
The independent checker uses only row products and inequalities.

The [proof](PROOF.md) shows termination of uncapped policy iteration, exact
attainment by one stationary policy, a common strict contraction ratio and a
finite-depth tail bound. This is a scoped certificate implementation and proof.
It is not a new general matrix theorem, a physical supplier or a new kappa.

The [example](example.json) has exact total (5,3) and common ratio 4/5, despite
an allowed row sum of 6/5. A separate control has two nilpotent whole modes but
an unsafe legal row combination. Thus neither a plain row-sum test nor separate
checks of the original whole modes settle the declared adaptive contract.

## Reproduce

Use CPython 3.12 and the standard library from the repository root:

```sh
python3.12 -I -B research/adaptive-row-bill/bills.py research/adaptive-row-bill/example.json
python3.12 -I -O -Werror -B research/adaptive-row-bill/verify.py
python3.12 -B scripts/research_package.py --package research/adaptive-row-bill
```

Save a producer certificate and pass it with `--check certificate.json` to check
it against the problem. The checker checks the problem directly. The producer
accepts 1..64 types and 1..64 rows per type. Its default is 4096 policy solves;
`--policy-limit` can set a different positive limit. Exhaustion produces no
certificate. Certificate rationals have an 8192-bit budget. Exact arithmetic
can grow; no uniform practical runtime or polynomial complexity is claimed.

The verifier independently enumerates all policies for 2538 finite row families:
2025 two-type families on the stated three-value grid, 512 three-type binary
support/complement families, and the example. Permutation determinants check
all principal minors. Cramer's rule checks every finite total. It checks 12200
policies, 1629 literal prefix/tail inequalities, four chain sizes through 64,
and 18 invalid-input or false-certificate controls. There are 181 safe and 2357
unsafe families. These tests corroborate the written proof; they do not replace
its all-size argument or independent human review.

## Applicability and overlap

Each row must include all recursive children and all adapter and restoration
charges. Row choices must be independently legal for each type. A bad policy
in an upper-bound or independently enlarged menu does not disprove a smaller
physical contract. The examples are synthetic. No current native supplier,
compiler, stock, precision or outer budget is recertified. The selected frontier
and all five selected assumptions are unchanged.

The base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority 8.
The required selected-source binding check passed after sparse source files were
restored. The current record selects PR6030; older numeric text in the priority
page is historical. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/6458)
records the changed card scope. Live Discussions, open PRs and targeted all-state
searches were checked before the claim. The full overlap cache found no match
for its three targeted phrases. Sparse local files, arbitrary historical diffs
and unpublished work remain limits. No search establishes novelty.

[PR5785](https://github.com/CrocSwap/integer-mult-bounds/pull/5785) supplies the
fixed-matrix certificate. [PR5892](https://github.com/CrocSwap/integer-mult-bounds/pull/5892)
already treats observed forcing and reachable types. [PR6271](https://github.com/CrocSwap/integer-mult-bounds/pull/6271)
treats synchronized paid switching periods. These are different contracts, and
no predecessor scientific result is counted or audited again.

## Open next questions

The structured questions are in [TASK.json](TASK.json). Bind one current complete
supplier menu to the row contract, then use its actual compiler and outer bill.
A separate optimization can reduce the common ratio when that ratio controls a
real reserve or cutoff. A favorable abstract certificate alone is insufficient.

## Attribution

Prepared for Ali Romman with substantial OpenAI Codex assistance; no subagents.
Credit classical M-matrix theory, Bellman policy iteration and
[Kozyakin's independent-row-uncertainty theory](https://arxiv.org/abs/1507.00492).
Credit Ali Romman's PR5785, Nick Petalas's PR5892 and PR6271, and the retained
Nick Petalas, David Ganz / Dugongue, Jose Manuel and typed-recursion lineage.
No predecessor executable is imported. Apache-2.0.

# Sharp reserve for an adaptive two-type bill

Scoped proof with exact finite corroboration, produced by Nick Petalas.

For the exact synthetic row menu of Ali Romman's [PR6472](https://github.com/CrocSwap/integer-mult-bounds/pull/6472), the optimal common positive-weight contraction ratio is

```text
lambda = (1+sqrt(41))/10.
```

The minimizing weight ratio is uniquely `(1+sqrt(41))/4`, so no positive rational weights attain it. The explicit rational weights `(37,20)` certify ratio `137/185`. Every allowed source row is retained. This answers the source's open common-ratio optimization question; it does not audit or replay the existing total-bill result.

Using the cited exact total `u=(5,3)`, the new all-depth tail bound is

```text
0 <= u-x_d <= (137/185)^d (111/20,3).
```

It certifies relative error at most `2^-64` at depth 149. The source's `4/5` bound first certifies it at depth 199. These are cutoffs of the two certified bounds; neither is asserted to be the actual first successful depth of the recurrence. The [proof](PROOF.md) establishes the optimum over every positive real weight and the tail inequality for every depth.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/sharp-adaptive-reserve/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/sharp-adaptive-reserve/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-adaptive-reserve
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-adaptive-reserve --check-source-history
```

Another CPython 3.12 interpreter can replace that path. Expected markers are `PASS_SHARP_ADAPTIVE_RESERVE`, `PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`. The direct verifier prints a generated receipt bound to all nine package files. An optional `--receipt /absolute/scratch/path.json` writes it outside the package. No receipt is hand-written or required as an input.

The verifier compares literal source-row products with the reduced ratio formula for all 4,096 integer weight pairs in `1..64` squared. It checks 257 exact nonlinear finite-depth prefixes against a separate two-by-two matrix recurrence, the tail inequalities and minimality of both stated cutoffs. False reserve, invalid precision and source-corruption controls must reject. These finite checks corroborate the written proof; they do not establish its universal quantifiers.

## Sources and scope

[ORIGIN.json](ORIGIN.json) identifies the exact PR6472 commit and source file. Its four-row example is retained byte for byte in [inputs/example6472.json](inputs/example6472.json), authenticated before parsing. The package imports no predecessor executable and does not require the pending source commit in local Git history. [SOURCES.json](SOURCES.json) binds the canonical base and historical task catalogue.

The chosen card is `complex-rank-shape-decoder`, explicitly changed to this analytical side question. Common reserves can control compiler tail cutoffs, but this example is synthetic. The metadata binding baseline passed for selected PR6030. Live handoffs, open and merged PRs, source/formula searches on main, and the bounded overlap cache were checked. Unpublished work, arbitrary historical diffs and uninspected replies remain coverage limits.

No physical supplier, native word, compiler admission, complete cost invoice, precision/stock/tape result, new kappa or selected-frontier change is supplied. All five selected framework assumptions remain. Selected cold replay, Lean and Docker were not run. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Can a complete source-compatible supplier row menu use optimized reserves to lower a real compiler cutoff? First extract a named caller's complete row menu and required tail tolerance, including all adapters, restoration and extra fees. Actual row legality, native realization, compiler applicability, storage, precision/tape and outer costs remain blockers. Structured fields are in [TASK.json](TASK.json).

## Attribution

The new reserve optimization and proof were produced by Nick Petalas. Ali Romman / PR6472 supplies the exact menu, adaptive contract, total `u=(5,3)`, original `4/5` reserve and the explicit next question. Classical weighted norms, nonnegative matrix and Perron theory retain credit; no general literature-priority claim is made. The source package retains its full predecessor attribution, including its fixed-matrix, observed-forcing and synchronized-switching interfaces. None is recertified here. Apache-2.0.

## Implementation limits

The retained input is fixed, has two types and four rows, and is hash-checked before parsing. All loops have explicit finite bounds. Cutoff requests accept 1..128 precision bits, search at most 1,025 depths and reject exhaustion. Verification checks use explicit exceptions, so optimized Python preserves every check. Functions remain below 60 physical lines. Python's managed fractions, JSON and hashing allocate dynamically, a rule-3 deviation bounded here by the fixed input, 4,096 weight pairs, 257 prefix depths and at most 1,025 cutoff iterations. This is a finite exact-arithmetic check, not a fixed-memory embedded implementation. The normal and optimized warning-strict registered commands are the diagnostics; no separate Python static analyzer is configured for this package. A future configurable or native implementation must revisit these resource bounds.

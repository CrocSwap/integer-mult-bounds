# Conditional implementation of the fixed two-split composition

The fixed graph from [PR #7716](https://github.com/CrocSwap/integer-mult-bounds/pull/7716)
has a complete conditional application with `kappa >= 0.00376313686053`.
This exceeds the parent upper value `0.00376154487712` by
`0.00000159198341`. The [proof](PROOF.md) states the exact scope.
The [application receipt](results/application.json), [source pins](SOURCE-PINS.json)
and [credit](CREDITS.md) give the evidence and dependencies.

The graph is unchanged. This result resolves its previously open physical,
signed-operator and ordinary/compiler cost obligation. It does not count
its normalized construction again. It retains all five framework assumptions.
No selected record is changed. The larger finite arithmetic constants do
not imply a practical speed improvement.

Use CPython 3.12 and the standard library. From the repository root, run:

```sh
python3.12 -B scripts/research_package.py --package research/quotient-split-physical-application
```

Expected final line:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/quotient-split-physical-application outcome=completed
```

[VERIFY.json](VERIFY.json) registers one application and three serial
catalogue shards. The application command checks saved catalogue coverage;
the three catalogue commands recompute the signed evidence. Run all four.
Do not use optimized Python: retained compiler assertions are required.
The package has four declared repository inputs. The supplier copies and
notices are retained, so no unmerged history is required for replay.

[DERIVATION.md](DERIVATION.md) records the source export. This is author
checking with reused engines. Human review, a formal-kernel proof and a
materialized all-size rounded multiplier remain open. The selected cold
replay, complete predecessor suites, Lean and Docker were not run.

## Open next questions

Can an independent proof discharge the five retained uniform interfaces?
Start with the exact source-bound application and selected contracts.
The finite certificate does not provide a new native, compiler, tape or
analytic theorem. A later construction must check live claims and carry
its own complete implementation bill. No new construction is reserved here.

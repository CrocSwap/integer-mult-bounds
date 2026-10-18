# Mutation coverage of the selected finite invoice

**Adversarial audit of one named current condition; no new I&#954;, no certificate,
supplier or frontier change.** The frozen PR1087 `code/invoice_allcold.py`
(SHA-256 `71eb5751...58a8`, inside `research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz`)
is the selected #1094 chain's finite-invoice stage. Its `run()` carries the
finite inequalities that gate the selected composition — the prefix obligation
(`required_prefix < 512` payload), the row obligation (`physical_row_coefficient < 20161`),
the halving guard, and six more — and it has no mutation-control block of its
own. This package answers open question 3 of
[`research/t16-audit-mutant-coverage`](../t16-audit-mutant-coverage/README.md)
(PR https://github.com/CrocSwap/integer-mult-bounds/pull/1959, Josie Elliston):
*mutation-test the invoice*, and, through the downstream probe, whether the 69
admission controls cover the invoice's inputs.

Aaron Wang, with help from opencode (substantial AI assistance; no independent
human review claimed). Apache-2.0.

## Result

The harness runs the pinned `invoice_allcold.run()` in-process over the archived
selected fixture (`research/community-frontier1094-audit/selected-replay.tar.gz`),
with marshal-free isolated JSON copies and in-place mutation with restore.

**Positive control.** On the unmutated fixture the stage reproduces the archived
selected `PREFIX-AND-INVOICE.json` and `GLOBAL-PREFIX.json` exactly, every field.

**Census: 37 semantic mutants, 31 rejected by the invoice itself, 6 accepted.**
Every mutant the invoice accepts is rejected by the downstream receipt admission
(`assemble.py`, the layer the 69 admission controls exercise). No mutant tested
passes both layers.

| Mutant class | Count | Rejected by `run()` | Accepted by `run()` |
| --- | ---: | ---: | ---: |
| A raw template fields (stored hashes stale) | 2 | 2 | 0 |
| B hash-consistent template fields | 11 | 11 | 0 |
| C audit-receipt fields | 14 | 10 | 4 |
| D provider inputs | 4 | 4 | 0 |
| F fully consistent stock inflation | 2 | 1 | 1 |
| E retained-invoice fields | 4 | 3 | 1 |

The six accepted mutants, each with its downstream binding (recorded verbatim
in [EXPECTED.json](EXPECTED.json)):

| Mutant | What `run()` accepts | Where `assemble()` rejects it |
| --- | --- | --- |
| `C3b_owner_profile_same_mass_same_max` | owner profile reshuffled at equal rank mass and equal max rank | line 130: the idle-remainder split must stay nonnegative |
| `C4_owner_explicit_idle_remainders` | `explicit_idle_remainder_children` raised by one | line 69: SPEC literal `expected.idle_remainders` = 7526 |
| `C6_owner_actual_73column_sigmas` | `actual_73column_sigmas` raised by one | line 68: SPEC literal `expected.actual_73column_sigmas` = 10002 |
| `C10_control_mutation_claims_cleared` | controller audit's own mutation claims cleared | line 75: invoice and owner receipts must record the same controller audit hash |
| `F2_consistent_stock_inflation_row_subthreshold` | stock inflated about 2^1840-fold, all identities consistent | line 67: SPEC literal `expected.rank_mass` = 1041408 |
| `E2_retained_previous_bound_zero` | retained invoice's `conservative_pervertex_used` set to 0 | line 153: the retained prior allowance must be a positive integer |

**Where the invoice's own rejects land.** Seven mutants die at the four-way
template-content hash binding (source line 175); five die at the deficit literal
`m*live-mass == deficit == 5120` (line 253); the provider class dies at the
registry and recount bindings (lines 35-45); and the finite-inequality block
itself (line 284) is the first rejecting statement for three mutants: the
halving guard (`C3`, max child rank 52 at equal rank mass), an inflated retained
allowance (`E3`), and the row guard (`F1`, below).

**Smallest falsifying instance for the row obligation.** Classes `F1`/`F2` are
a boundary pair: fully hash-consistent template, owner and parent stock
inflation preserving every run() arithmetic identity (deficit literal included),
aimed exactly at the row guard `row = 2*stock_bits + 11185 < 20161`.
`F1` reaches stock bit length 4488 (row exactly 20161) and is rejected at the
inequality block. `F2`, one stock bit less (4487, row 20159), passes the invoice
alone with every strict check true. One bit of stock width separates rejection
from acceptance; below the threshold the invoice does not anchor the stock, and
the anchors are the downstream SPEC pins and the driver-level literals.

**Answer to the coverage question.** The 69 admission controls mutate the two
*receipts* and require `assemble()` to reject; they do not touch the invoice's
input files. The invoice's input bindings are enforced as follows:

| Input binding | Enforced by | Evidence |
| --- | --- | --- |
| template content identity (4-way hash) | `run()` line 175 | classes A and B raw rejects |
| template call/sweep/registry semantics | `run()` lines 177-230 | class B rejects |
| owner arithmetic identities, deficit 5120 | `run()` line 253 | classes B/C rejects |
| provider bytes and recounts | `run()` lines 35-45 | class D rejects |
| finite inequality values | `run()` line 284 | classes C3, E3, F1 |
| owner receipt scalars (idle remainders, chart types, rank mass) | `assemble()` SPEC pins | classes C4, C6, F2 |
| controller audit identity | `assemble()` line 75 | class C10 |
| retained prior allowance positivity | `assemble()` line 153 | class E2 |
| stock identity at the selected values | `verify_t16.py` final binding with `indep16.py` | static reading, not executed here |

So the invoice's acceptance *does* depend on an independent check for the six
fields above, and the chain binds them one layer down. Two caveats are precise:
the retained invoice's `conservative_pervertex_used` is only bounded below by 1
and by two pinned scalars (class E2); and the last row is a static reading of
`verify_t16.py` (`ind['rank_mass'] == owner['rank_mass'] == 1041408`,
`owner['deficit'] == 5120`, `ind['physical_row_coefficient'] < 20161`), not an
executed replay.

## Reproduce

From the repository root, standard library only, CPython 3.10+ (the registered
replay uses 3.12):

```sh
python3 -B research/invoice-mutant-coverage/verify.py
python3 -B -m unittest discover -s research/invoice-mutant-coverage -p test_package.py
```

The first command reruns the positive control and the 37-mutant census and
compares the whole record against [EXPECTED.json](EXPECTED.json); `--write`
regenerates the receipt after an intentional harness change. The second is the
package test with a failure control (the halving-guard mutant's recorded
rejection line must match the receipt). Nothing is written outside a fresh
temporary directory.

Pins checked before computation: the PR1087 archive
(`d4acf04d...dea86`), the archived selected replay
(`f1da8061...29d6`), `code/invoice_allcold.py` (`71eb5751...58a8`), the three
package data files copied over the source data exactly as the pipeline does,
and the retained vendor invoice (`ce1bfa49...8478`, asserted unchanged after
all retained-invoice mutants, which run on a scratch copy).

## Method and scope

- Mutants are single-field or single-identity changes. Class A leaves the
  stored template hashes stale (superficially invalid); class B resynchronizes
  them (superficially well-formed); class C mutates the audit receipts, whose
  file hashes are recorded but not pinned inside `run()`; class D mutates
  provider inputs; class E mutates a scratch copy of the retained invoice;
  class F synthesizes a fully consistent stock inflation across the hosted
  template, the owner receipt and the parent template, preserving the deficit
  literal, the geometry identities and the modular constraints.
- Each verdict records the first rejecting statement in `invoice_allcold.py`
  (line and source text) or the acceptance, plus `assemble()`'s first rejecting
  statement for accepted mutants.
- **Not checked:** well-formed provider *program* mutations with resynchronized
  registry and hashes (the recount chain closes over them; synthesizing edits
  that keep every identity needs its own harness); the `emit` and `audit`
  stages; `audit_allcold.py` (PR1959's object); executed `verify_t16.py` /
  `indep16.py` coverage (quoted statically only); any claim about kappa, the
  certificate or supplier admission. The census is evidence about this fixture
  and these 37 mutants, not a completeness proof for arbitrary mutations.

## Credit

The audited stage is the PR1087 archive's `code/invoice_allcold.py`, the
call-specific mixed-provider invoice adapted from the retained PR558, PR552 and
PR531 lineage (Jeremy Kothe's #870/#1087 chain with Hao Yan's (@FanPUYen) #858
T16 edits). Rohan Arun's #1094 supplies the selected exchanges and archived run;
the maintainer's `research/community-frontier1094-audit` archived the fixture.
Josie Elliston's `research/t16-audit-mutant-coverage` (PR
https://github.com/CrocSwap/integer-mult-bounds/pull/1959) posed the exact open
question, supplied the harness pattern and established the adjacent
`audit_allcold.py` coverage; jackmgaller's
https://github.com/CrocSwap/integer-mult-bounds/pull/1939 explains the copy
cost this harness avoids by mutating files in place. The downstream admission
controls and `assemble.py` are the same PR1087 code. The task card is retained
as [task-card.md](task-card.md).

## Open next questions

1. **Hash-consistent provider program mutants.** Why it matters: the recount
   chain (registry hashes, `LOCAL-CHECKS`, call program hashes) is only tested
   here with raw mutations, which die at the first hash mismatch. First step:
   extend class D to resynchronize the template registry and stored hashes after
   editing `LOCAL-PROGRAMS` events. Blocked by: synthesizing event edits that
   keep the recount identities (paid profile, real, macros) internally equal.
2. **Execute the driver-level anchor on the F2 fixture.** Why it matters: the
   claim that `verify_t16.py` + `indep16.py` reject F2 is a static reading.
   First step: run the `indep16.py` stage alone on the F2-mutated tree and
   compare `rank_mass`, `deficit` and `physical_row_coefficient`. Blocked by:
   the lift/bind/emit stage chain above the invoice in the strict replay.
3. **Pin the retained prior allowance.** Why it matters: `run()` accepts any
   `conservative_pervertex_used >= 1` in the retained invoice (class E2), and
   only positivity is rechecked downstream; a large value fails safe (it can
   only worsen the run's own inequalities, class E3), but the binding is thin.
   First step: compare the retained invoice's hash or its allowance against the
   vendor `UPSTREAM-PINS` in the invoice stage's invocation. Blocked by: a
   maintainer decision on wrapping the frozen driver.

# Drive the padded balanced CRT inverse from encoded source with 79 retained roles

This completes the reverse schedule and subtractive whole-node consumer
left open by the [published forward endpoint](https://github.com/CubeJerry/integer-mult-bounds/tree/532b60ac427f47191175aba2e1317db0f3508d51/research/encoded-balanced-crt-endpoint).
It evaluates the inverse of that same balanced CRT **address-state** map
on the same actual padded source. Runtime receives no decoded node start,
level, width, precision, coordinate or traversal list. Both composition
orders are identity on the entire admitted padded rectangle. The proof
is relative to explicitly pinned source contracts. **No new kappa.**

The new [inverse_frontend.py](inverse_frontend.py) bootstraps the unary
half-size from the encoded depth and halves it between descending levels.
The new [inverse_producer.py](inverse_producer.py) has exactly one scientific
line changed from the current-coordinate producer: modular subtraction
replaces modular addition in its whole-node updated field. The forward
source writer is byte-for-byte unchanged. It stages the result, closes
the numerical lease, then commits the owned source at the same extent.
[SEAMS.json](SEAMS.json) records the precise seams; the replay authenticates
the one-line producer replacement and all nine source exports.

The complete source cost is O(A^4), where A is the sum of declared widths,
and retained backing is K_source+O(A^2). All source reads, staging, writing,
head returns, precision preparation, lease retirement and cleanup are paid.
One invocation owns 79 roles. A fresh forward/inverse round trip retains
both inventories, **158 histories**, and charges both complete invocation
bills. Source acquisition in the admitted format and clean private backing
remain explicit premises. No same-bank restart is claimed.

## What is new and what remains open

The balanced inverse algebra and logical padded callers were already supplied
by [#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) and
[#4195](https://github.com/CrocSwap/integer-mult-bounds/pull/4195).
[#7152](https://github.com/CrocSwap/integer-mult-bounds/pull/7152) already
implements physical forward/reverse source-state trees at compiled geometry;
[#7154](https://github.com/CrocSwap/integer-mult-bounds/pull/7154) supplies
the encoded forward numerical iterator. [#5053](https://github.com/CrocSwap/integer-mult-bounds/pull/5053)
already proves the arithmetic and current-left reconstruction used here.
The contribution is their exact encoded reverse consumer join on the
forward writer's physical interface, with a complete current-state,
precision and retained-history argument.

[#4024](https://github.com/CrocSwap/integer-mult-bounds/pull/4024) already
supplies an encoded bidirectional triangular payload converter, consumed
after integer recovery by [#5095](https://github.com/CrocSwap/integer-mult-bounds/pull/5095).
That different format and routing contract is not replaced by this one-vector
helper. Likewise, the raw compact macro inverse in
[#4169](https://github.com/CrocSwap/integer-mult-bounds/pull/4169) is not
implemented by this package. No first CRT inverse, payload permutation,
exceptional-key epoch or selected outer caller is claimed.

The five selected foundational assumptions remain conditional. The complete
selected conditional kappa remains 0.00363005817. The source proof does not
certify the numerical value of its fixed finite-control refinement constant,
literal binary lowering, analytic error bounds or integer recovery.

## Reproduce and review

[PROOF.md](PROOF.md) gives the quantified claim, exact predecessor boundary,
all-size argument and complete cost ledger. With Python 3.12 and its standard
library, from this directory:

```sh
python3.12 -I -W error -B verify.py
python3.12 -I -O -W error -B verify.py
```

Both executed modes print:

```text
PASS_ENCODED_BALANCED_CRT_INVERSE cases=53 nodes=380 roles=79/158 controls=11
```

The main fixed family runs both composition orders on all 32 padded pairs
for moduli (3,5), fifteen four-axis cases, four composite-modulus cases and
two eight-axis cases. Its 380 actual numerical nodes use 85,291,890 measured
source actions; these are finite observations, not the asymptotic proof.
A separate three-node `run()` test supplies no iteration count or schedule.
The main oracle independently solves each current-left congruence system
by exhaustive search. The complete endpoints also match the source-pinned
balanced forward/reverse oracle; observer results never enter runtime.

Negative controls detect wrong level order, the wrong arithmetic sign,
stale pre-root left data, hidden current precision, nonblank older guard
tails, an extra physical role, wrong unary transition, forgotten retained
backing, current coordinates misread as original digits, a global-invalid
identity shortcut and source commit before retirement. Host geometry/decode
names are poisoned and physical constructors sealed after initial acquisition.
Failure detection is not an arbitrary error-rollback theorem.

Actual precision is read from each current selected node. It decreases
between levels but can increase within a level: (2,2,3,3) declared widths
give inverse precisions **11,5,7**. The checks preserve all old backing and
require exact current guard extents plus blank older tails. Source metadata,
inaccessible nonblank history, extent, backing identity and heads are checked
after every node. Both fresh invocation inventories remain charged and blank
after each full-source round trip.

[INPUT-PINS.json](INPUT-PINS.json) records exact repository, commit, byte hash
and Git-blob pins. Direct replay is offline and Git-free. The canonical base
is `e54523517d0f03e58352e647c403a5af3e525a57`, the frontend head is
`cc35ecedce6f208d5056fab6d17c58555affc73c`, and the unchanged forward writer
is at `532b60ac427f47191175aba2e1317db0f3508d51`. The pending dependencies
are preserved as exact package-local source, rather than inferred from a
moving branch or PR title.

## Open next questions

The structured first steps and blockers are in [TASK.json](TASK.json).
An actual exceptional-key caller needs paid source production, conversion
and return transport plus its separate raw compact macro contract. A restart
theorem could reuse the same 79 histories; this package charges 158 for two
fresh invocations. The balanced payload caller still needs its synchronized
encoded row/target/header schedules. The full provider closure and clean
private acquisition also need a common literal binary program and tariff.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance;
Apache-2.0. Retain JoyboyBrian's numerical/entry/owner work; Ali Romman's
encoding and retired-write boundary; Cinna Davis, Hiroki KUMAZAKI, Tekalign,
ToikY, commdata2338 and every notice in the unchanged exports. Full credit
is in PROOF.md. AI cross-review is not independent human or formal-kernel
acceptance.

## Independent acceptance checks

The orchestrator's [REVIEW.md](REVIEW.md) and separate
[PEER-REVIEW.md](PEER-REVIEW.md) accept the frozen source-relative theorem.
The peer authenticated all nine exports and independently checked reverse
control, current-left reconstruction, retirement, precision regrowth and
complete cost/history sums without rerunning the author verifier.

A separate CRT-idempotent and global mixed-radix inverse oracle passes 20
cases and 52 actual nodes, including padded axes, eight-axis cases, widths
up to nine bits, historical tails, the 11,5,7 precision sequence and a rejected
stale-coordinate mutation. Its portable command is:

```sh
python3 -I -W error -B research/encoded-balanced-crt-inverse/independent_check.py
```

`INDEPENDENT-RESULT.json` records the full domain and exact code hashes.
The author normal and optimized replays also pass from this final packaged
directory with identical output. These are independent AI checks; no human
or formal-kernel acceptance is claimed. The full proposed PR description
is committed in `PR-DESCRIPTION.md`.

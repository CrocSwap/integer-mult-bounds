# Exact total tape traffic for high-field doubling and halving

For every odd Q>=3 and positive canonical spectator extents B,S, PR2915's
literal `kernels.doubled` has the same exact logical tape traffic in either
direction and costs less than `1024 BQS` reads, writes and unit head moves.
The new result is the all-parameter source-level invoice in [PROOF.md](PROOF.md),
including Count setup, normalization, division, countdowns, copies and cleanup.
The algorithm and its endpoint remain Jose Manuel/jmbarrancoml's contribution.
Arham Tahir/PR2877 supplied the shared countdown identity used here.

This independently audits one local cost implication in the proposed fast
BIT caller. No production source, frozen evidence or selected result changes.
A physical allocator, whole route, complete caller, supplier and new kappa
are not established.

## Evidence and reproduction

From the repository root, with standard-library Python 3.12 or newer:

```sh
python3.12 -I -Werror -B research/high-scaling-total-traffic/verify.py
python3.12 -I -O -Werror -B research/high-scaling-total-traffic/test_verify.py
python3.12 -B scripts/research_package.py --package research/high-scaling-total-traffic
```

The primary replay checks 390 complete calls and all 152,352 payload origins
against an independent modular address map, along with the exact traffic and
construction count. It also checks 45 shared-countdown boundary/padding cases.
Thirteen test groups cover source/receipt corruption, malformed inputs, wrong
direction, omitted cleanup, actual Ring rejection of padded words, fixture
bounds and read-only Git-free exported replay. Normal verification reads and
compares [RESULT.json](RESULT.json); `--emit` prints without changing it.

An endpoint-preserving extra-countdown mutant changes 10,354 operations to
49,874 while retaining the complete permutation. Its exact excess is 39,520.
Thus endpoint-only evidence misses a cost defect. A padded-width control costs
74,392 against the proposed 3,072 bound; the real canonical Ring rejects that
padding. Neither control reports a production bug.

The checker authenticates complete shared modules and compiles the unchanged
named function nodes for `copy_rows` and `doubled`. This is a local source-slice
check, not execution of PR2915's whole loader or physical ScratchPool. Factory
traffic outside literal Tape construction has a separately charged interface
`T+aA`, with exact construction count `A=7+3B+2BQ*[S>1]`. It is not assumed zero.
All external dependencies are pinned in [SOURCES.json](SOURCES.json) and declared
in [VERIFY.json](VERIFY.json). Finite executions corroborate the written proof;
they do not themselves establish its universal quantifier.

Registered normal/optimized replay and all thirteen test groups pass locally
on Linux/WSL2 with CPython 3.12.15. Optimized CPython 3.13.5 replay and tests,
all 144 research-workflow tests without skips, and strict lint/format checks
also pass. The fourteen consumed provenance/input rows match refreshed main
`389fa10d714f5b40afe624908e487eb5e424498d` at 14:03 UTC; guidance and selection
are unchanged. These are local checks, not hosted CI or independent review.

## Open next questions

- Bind the exact allocation/lease contract at this actual call, including
  marker reads and any factory work. Start from the `T+aA` interface and the
  current physical pool, then meter each physical tape only once. This matters
  because logical source traffic alone does not admit physical placement.
  Complete fixed-role placement and failure cleanup remain separate obligations.
- Independently price one complete high-route call, including its encoded
  setup, ordinary B1 swaps and teardown. Start with PR2915's actual reached
  route and its canonical-width/prefix hypotheses. This checks the next cost
  implication; the present two scaling passes are only components of that bill.

The decision is to finish this independent audit without expanding the caller
construction. Unknown route/consumer costs are not zero.

## Sources, scope and credit

Base canonical main is `3aa52a3b2f8c08994978f97d98c62cfa8e4916fb`, priority
revision 5. The task draw nonce was `4df3b8eaf796c033bd50c605b106587f` on the
adversarial-audit track; `uniform-transfer-audit` is refined to this successful
local tape/time implication. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18974953)
and [TASK.json](TASK.json) record overlap, freshness and stopping scope.

PR2915 is pinned at `fecc5a87574df441ddc3dad44f99fca9bd7fdd92`; its current
main kernel is byte-identical. PR2877 is pinned at
`bbafe95af535004c7b605059e611cc8a569f88f6`. The seven shared runtime modules
match its authenticated exports of PR2753
`7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, retaining Jose Manuel's PR2697
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1` source lineage. The route helper
is the exact retained PR2697 export in selected-route-live-volume. No predecessor
package is modified or copied to acquire new provenance.

Credit Jose Manuel/jmbarrancoml for the scaling implementation and caller;
David Arias for the all-size caller; Arham Tahir for the countdown/sign traffic
proof; and the source-specific attribution retained in their packages, including
ywz65's primitive lineage and the selected PR589 work by DreamingOfClouds on
eumemic's base. This package adds only the independent scaling invoice, bound,
source-slice checker and failure controls.

Nick Petalas. Apache-2.0. Substantial automated assistance; author-checked
written proof and local executable evidence, not independent human or
proof-assistant review. Full selected cold replay and hosted CI are not claimed.

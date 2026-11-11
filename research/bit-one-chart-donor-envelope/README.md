# One-chart donor exclusion for the fixed-volume BIT retag

**NO VERIFIED GAIN. Exact conditional κ change 0%.** The eight-port
retag of the retained #7001 BIT word has 35 adjusted deliveries. For each
delivery, consider a donor from one distinct positive canonical chart.
Grant free access through the first next contact with the recipient to
every normalized row previously observed in the chosen chart. The target
row is outside that span in all 22,190 chart/delivery pairs. Formation,
routing, ownership and restoration may all be free in this relaxation,
and each delivery may choose a different chart without interference.
The resulting optimistic whole-word saving upper bound is exactly zero.

The fixed stock has 635 positive canonical charts, of which 627 have
nonzero observed rows. Each delivery has 634 alternate charts. The
exhaustive test finished with zero unresolved pairs. It includes
nonnested and oblique alternate chart pairs within the retained cache
contract. It leaves donors combining multiple charts, new synthesized
rows, different recipient deadlines, altered field volume and the other
103 ports outside the tested scope.

## Price and evidence

At fixed target κ = 0.0040075385047236, the replay reconstructs the
36-copy paid and productive invoice, charges 18 retagged calls and
credits the 111 formal rank-one savings from QUERY 349. The retag's
per-call native rank histogram changes by
`{1: -48, 2: 21, 3: -6, 4: 6, 6: -8, 7: 8}`. The directed interval
requires more than 88.3884026799643 raw units of further compatible
whole-word savings, or more than 4.91046681555357 per changed call.
The replay saves [PRICE.json](PRICE.json) before decoding donor
supports. The exact endpoints are in that receipt.

The first engine computes high-pivot binary spans for the 659-column
normalized trace. The second engine solves the transposed low-pivot
dual equations separately for each chart/delivery pair. A separator
must vanish on all available donor rows and evaluate to one on the
target. Appending the target row in a synthetic fixture makes those
equations inconsistent. Both engines reuse the pinned trace and
geometry of #7200. Its 79 empty, 512 explicit and 382 shared-certificate
strict-prefix cases form the predecessor control. Its trace checks
normalized endpoints and 237 owned lifetimes. [STOCK.json](STOCK.json)
records the full census and all case-level price bounds.

## Replay

From a clean checkout, use CPython 3.12 with assertions enabled and
the standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/bit-one-chart-donor-envelope
python3.12 -B scripts/check_research_commit.py --package research/bit-one-chart-donor-envelope --check-modes --check-source-history
~~~

A Git-free export including the two declared inputs can run
`python3.12 -I -B research/bit-one-chart-donor-envelope/replay.py --root .`.
The replay authenticates workspace-relative inputs by SHA-256 and Git
blob ID and rejects duplicate JSON keys and source paths. It compares
all deterministic price and stock fields.

## Predecessors

[#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001) at
`d777f3a0aa2878bea0478918923dabcf86b9878b` supplies the retained
signed BIT caller and invoice, and #6726 supplies its native word.
[#7200](https://github.com/CrocSwap/integer-mult-bounds/pull/7200) at
`08f41734863055b42b3975c0d434ecf2ca4fcaf8` supplies the exact retag,
trace and strict-prefix controls. This package extends its tested cache
domain to every distinct retained positive chart. [#7177](https://github.com/CrocSwap/integer-mult-bounds/pull/7177)
at `f59cf773c6038d72bc3b5aeae204cbe1923b34bf` supplies the formal
QUERY 349 credit. [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
at `ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the complete
comparable κ = 0.003645669928698. The exact native input and invoice in
this replay come from canonical commit
`e54523517d0f03e58352e647c403a5af3e525a57`. OpenAI Codex and
subagents materially assisted.

## Open next questions

Can a changed provider supply a row through a richer chart interface?
The next test should pin that chart and ownership contract and bound
the fully charged stock across all relevant deliveries before building
one instance. An algebraic fit would still need signed forward and
adjoint action, ownership and restoration, and a complete paid and tape
invoice.

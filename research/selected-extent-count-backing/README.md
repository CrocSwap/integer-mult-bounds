# Retained count backing at native extent preparation

For unchanged PR2697 `Layout.extents`, private count backing including LEFT,
erased cells and the exponent Counter is bounded by

```text
S + max(I+2,3W+9)
S = sum(bit_length(e_i)+2), W = max bit_length(e_i)
```

Here e_i are returned positive extent values and I is encoded index Word
width. At return, exact backing is `sum(bit_length(e_i)+3)`.
[PROOF.md](PROOF.md) gives the all-parameter source argument and an exact,
operand-order-sensitive `Count.product` peak.

An actual successful zero-exponent call reaches 267 private count cells with a
256-bit index, versus 21 with an 8-bit index. Both return the same 12-cell
marginal cohort. Ignoring index padding underprices this preparation phase.

This answers one part of the released
[PR2902/2905 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18968627).
[PR2749](https://github.com/CrocSwap/integer-mult-bounds/pull/2749), head
`a18ba3bbfb549af66488a890edcb4a3744de90a3`, already bounds occupied count
content and expressly excludes backing and LEFT. Main's numerical packages
cover a separate category. No total private A, stock coefficient, physical
allocator, supplier admission or new kappa is claimed.

## Evidence and reproduction

Python 3.12, standard library only, from repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/selected-extent-count-backing
```

The checker authenticates all declared source bytes before execution and
observes allocations/writes with weak references. It counts array lengths
without retaining dead tapes. Independent integer products, extent formulas
and complete ADD address permutations check actual results. It restores prior
module bindings on every exit, bypasses bytecode caches, and leaves frozen
sources and notices unchanged. Geometry and the ADD-only action are extracted
as unchanged AST definitions; unrelated compiler imports are not exercised.

The fixed receipt covers 4,099 products, 58 extent preparations, six complete
native ADDs and four embedded rejection/padding controls. Products 1..64 in
each operand exhaust that finite domain, with three larger power-of-two
cases. Extents cover unary/binary calls, every position in two small bank
widths, all three gap locations, q=3/5, w=1/2 and index padding. Finite evidence
supports the written proof; it does not alone prove all-parameter statements.

Normal replay is read-only. `verify.py --write` explicitly regenerates the
receipt. Tests separately cover underbudgets, cleared backing, source corruption
and preloaded modules. VALIDATION.md records commands, review and limitations.

## Open next questions

1. Join this extent backing with PR2905's countdown cohort, numerical backing,
   callback records and continuations at the same ADD cuts. Start with the
   exact callback baseline including suspended parents. Callback records and
   ownership release block total private A; separate maxima are insufficient.
2. Realize that ledger on fixed physical tapes. Start with last-borrower and
   release obligations of the bank codec. Strong reachability does not prove
   physical placement, bounded movement or safe reuse.

Structured questions and assignment freshness are in TASK.json.

## Credit

Nick Petalas. New material is Apache-2.0. Jose Manuel/jmbarrancoml supplied
PR2697's caller and count implementation. Ross Richardson's PR2801 exports
and Layout numerical analysis retain the source binding used here. Credit
Nick Petalas's PR2749 count-content and PR2905 countdown-backing results,
kumagi's PR2882 packet interface, PR2902's payload component, Ross Richardson's
PR2874 backing analysis, starship-s's residual work and the full retained
lineage in the declared source NOTICE.md. Their results remain separate.
Substantial AI assistance was used for derivation, implementation and
review. No independent human or formal-kernel review is claimed.

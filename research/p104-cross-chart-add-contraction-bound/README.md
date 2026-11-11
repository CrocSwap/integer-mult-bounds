# Fixed-chart cross-chart ADD contraction on #7314

**NO VERIFIED GAIN. Conditional κ change 0%.** The exact funded-return
word in [#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314)
contains 64,080 consecutive ADD triples after ignoring MOVE records only.
There are 5,467 cross-chart triples, 215 with exactly three roles, and two
directed triangles after excluding roles 863, 1355 and 1568. Both triangles
have a public middle role. Direct reversal at their old scalar charts would
require a public descent in each. The owned-middle stock is empty. Both
censuses exhausted their scope, and zero cases remain unresolved.

The candidate edit reverses two ADDs forming a directed chain, removes the
third ADD if it is their exact signed correction, and routes the three
touched roles directly between the original literal ADD charts and fixed
window endpoints. Unrelated MOVE events retain their order. All other native
events, the caller and the productive profile stay fixed. The final paid
saving upper within this scope is zero. The result applies to one such
literal local edit. Changing ADD charts, retiming past another scalar
operation or composing broader words remains open. See [PROOF.md](PROOF.md).

## Evidence and reproduction

The comparator is exact #7314 head
`9d0119eb12fbd9fa534b48cd37b68e7099757b91` at certified κ
`0.003646221436446`, with [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
caller head `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The source pins,
baseline price and admission receipts ship with this package. Admission records
the earlier local predecessor replay and its assumptions. The replay here
authenticates those receipts and reproduces the new exclusion. The existing
native all-columns, owned-erasure, compiler, precision/tape and analytic-recovery
premises are inherited.

From a clean checkout, with CPython 3.12 and its standard library:

```sh
python3.12 -I -B research/p104-cross-chart-add-contraction-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-cross-chart-add-contraction-bound
```

Use `--out fresh-directory` to retain the reproduced receipts. The replay
authenticates immutable path-keyed pins, rebuilds the saved lead price and
support receipts, and runs an independent reverse chart walk at the same
128-case and 30-second limits. It compares the new plaintext receipts with the
frozen SHA-256 values and rejects a stale price digest and a changed caller.
Both engines also exercise exact signed positive and corrupted-correction
controls. No prior temporary files, download, or local Git refs are required.

## Open next questions

Can a lawful MOVE retiming expose an owned-middle triangle if a literal ADD
chart or a scalar boundary can change? Begin with one explicitly bounded
retiming family. Freeze its exact charts and price the whole compatible
native paid delta against the complete caller invoice. A surviving edit
needs signed arbitrary-input and adjoint action, ownership and restoration,
plus unchanged compiler, precision and tape premises or proofs for the
changed interfaces.

## Credit

[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) provides the
funded-return word and invoice, and
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) provides
the signed caller. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
provides the directed tariff. The older A2 and signed commutation precedents
include [#3998](https://github.com/CrocSwap/integer-mult-bounds/pull/3998),
[#4019](https://github.com/CrocSwap/integer-mult-bounds/pull/4019),
[#4041](https://github.com/CrocSwap/integer-mult-bounds/pull/4041),
and [#4112](https://github.com/CrocSwap/integer-mult-bounds/pull/4112).
[#5170](https://github.com/CrocSwap/integer-mult-bounds/pull/5170) studies
a related corrective expansion. [#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319)
supplied the carried-forward Round 58 invoice price. Round 60 tests a literal inverse contraction with fixed
charts and endpoints. OpenAI Codex and subagents materially assisted.

# Type A rank-17 shared-input prefix exclusion

**NO VERIFIED GAIN.** On the exact signed #7113 caller inherited by #7481, neither root pair `(7,25)` nor `(10,28)` admits a productive rank-17 to rank-8 and rank-9 split at a literal caller boundary using an invertible body-independent, central-even change of its initial two-input basis. This fixes the old prefix and paid itinerary. Roots in each pair share the same final body mask and signed phase. This tests the shared input basis left open by #7510's fixed single-column census.

The forward sweep covered all 4,784 boundaries per pair, both body orders and both parity assignments for the first body, for 38,272 keys. Every key had a nonzero forbidden coefficient minor in the positive central sector. The independent reverse sweep recovered the initial columns, found forbidden rank two in both sectors for every key, and checked every forward minor against its reconstructed coefficients. The scope exhausted with zero survivors and zero unresolved keys.

At #7481's directed crossing bracket, one hypothetical paid-neutral split across all 96 Type A ports would give gross credit strictly between 4.07820585157566 and 4.07820585157568 raw before adapters and other costs. No split was realized. See [the proof and price](PROOF.md), [exact path pins](PINS.json) and [verification receipts](VERIFICATION.md).

## Replay

Use CPython 3.12 and its standard library on POSIX. From a clean checkout run

```sh
python3.12 -I -B research/p104-type-a-rank17-shared-input-bound/replay.py
```

Expect `PASS_RANK17_SHARED_INPUT_BOUND`. The verifier regenerates the forward journal in a fresh temporary directory and verifies both independent sweeps. It requires no network, prior temporary state or Git metadata. Both scientific engines have a 30-second cap.

## Open next questions

Can a named already-paid caller operation change the prefix and supply a missing direction? This is the next useful gate because moving the split within the old itinerary and mixing either of these initial pairs cannot pass. Start by naming the operation, its first affected read, and the exact signed support available at that clock to its sender and receiver. Charge any repair, ownership and restoration before construction. Mixing other input groups or changing the body representation or phase interface remains open under separate premises.

## Credit

[#7510](https://github.com/CrocSwap/integer-mult-bounds/pull/7510) supplies the fixed-column predecessor, open shared-basis question and price receipt. [#7398](https://github.com/CrocSwap/integer-mult-bounds/pull/7398) supplies both Laurent engines, its earlier checked cuts and the necessary prefix convention inherited from [#7316](https://github.com/CrocSwap/integer-mult-bounds/pull/7316). [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the exact signed caller, [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) the complete comparator and invoice, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed tariff. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.

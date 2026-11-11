# Fixed-chronology mixed ADD rechart on #7314

**NO VERIFIED GAIN. Conditional κ change 0%.** Two exact walks of the
[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) word
match all 374 ADDs with one public operand and one owned operand.
Each operand needs a paid MOVE as its nearest earlier contact and
another as its nearest later contact for the proposed rechart.
No ADD has all four MOVE neighbors, even before applying protection.
The planned scope excludes 65 main, hosted or protected cases and
finds the missing-neighbor obstruction on all 309 other cases.
No cases remain unresolved and the compatible paid saving upper
is zero.

The edit would keep the four MOVE clocks, ownership flags, outer
chart endpoints and monotone directions. It would change their
common interior chart and the ADD's literal chart while preserving
its coefficient, every other operation and the signed caller. It
preserves paid and productive counts and rank mass. The predecode
optimistic upper is about 0.37412316129256057 raw for one edit and
8.604832709728893 raw for at most 23 edits with disjoint paid MOVE
incidences. The exact scope and pricing are in [PROOF.md](PROOF.md).

## Evidence and reproduction

The tested comparator is exact #7314 head
`9d0119eb12fbd9fa534b48cd37b68e7099757b91` at certified κ
`0.003646221436446`, with exact
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
head `07a76c5e2738882c0cb322278e56f6cae3c9885d`.
The existing native all-columns, owned-erasure, compiler,
precision/tape and analytic-recovery premises remain in force.
The package authenticates the comparator admission. A stronger
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
claim, exact head `aaeec8c0acf01e99a5f331ef363a698d9c084ace`,
proposes κ `0.00364665195644` using a different helper-319 fusion.
Its independent replay was pending at this checkpoint. The
exclusion here is about the pinned #7314 word.

From a clean checkout, use CPython 3.12 with assertions enabled.

```sh
python3.12 -I -B research/p104-mixed-four-move-rechart-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-mixed-four-move-rechart-bound
```

Use `--out fresh-directory` for the four regenerated plaintext
receipts. The package uses only committed files and the Python
standard library. It saves the complete price before both contact
walks, matches each ADD clock and four contact slots, and rejects
a stale price digest and changed caller bytes.

## Open next questions

Can a changed scalar chronology create a mixed ADD with four paid
neighboring transports at positive fully charged margin? First pin
one retiming family and price every moved or added operation. A
survivor still needs exact signed action and adjoint, ownership and
restoration, and full compiler, precision and tape verification.

## Credit

[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314)
supplies the literal word and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
the signed caller. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
and [#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319)
supply directed pricing and its retained adapter.
[#7297](https://github.com/CrocSwap/integer-mult-bounds/pull/7297)
and [#7122](https://github.com/CrocSwap/integer-mult-bounds/pull/7122)
supply related rechart precedents that preserve mixed contacts.
[#7311](https://github.com/CrocSwap/integer-mult-bounds/pull/7311)
studies mixed scalar order. [#7325](https://github.com/CrocSwap/integer-mult-bounds/pull/7325)
and [#7326](https://github.com/CrocSwap/integer-mult-bounds/pull/7326)
supply related concavity and transport pricing precedents.
OpenAI Codex and subagents materially assisted.

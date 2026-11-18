# One fewer paid transfer on the cf6a nine-swap word

Under the five selected framework assumptions, the changed 16-call banked construction gives **κ ≥ 0.0037300417**. This is **0.00000069852193** above the upper endpoint of SYLforge’s supplied nine-swap invoice, and **0.0000034128230** above the upper endpoint of the earlier qualified banked graph. The selected record on the submission base is #7000 at 0.00363005817. [Supplied word and scope in #7700](https://github.com/CrocSwap/integer-mult-bounds/pull/7700) · [Banked comparator #7697](https://github.com/CrocSwap/integer-mult-bounds/pull/7697) · [Selected record](../../certificates/selected-result.json)

On helper 1256, paid MOVE 95828 sends an array from chart 476 to chart 878. Its only reader is the unit-coefficient sender for MOVE 104442 from 878 to 127. The new graph sends the original payload directly from 476 to 127 at stable raw key 104442. Its execution advances from ordinal 4,114 to 3,310, after its four donors are available. Those spans have dimensions 3, 6 and 9. This replaces two rank-three payments with one rank-six payment in each of the sixteen invocations. Every productive owner keeps its entrance and exit. [Construction](CONSTRUCTION.md) · [Ordered transforms](NATIVE.md)

| Complete signed application | Supplied nine-swap parent | New banked relay |
|---|---:|---:|
| Paid native transfers per invocation | 6,144 | 6,143 |
| Paid jobs, including the caller | 101,856 | 101,840 |
| Independent productive jobs | 21,152 | 21,152 |
| Directed raw crossing | (0.00372934317806, 0.00372934317807) | (0.0037300417703, 0.0037300417704) |

The submitted parent at `7d84799a447867d36137d12ef7ca5646154d763c` supplies immutable native-word bytes with canonical SHA-256 `ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472`. The rebuilt folded parent is `72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f`. The changed graph is `8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf`. These hashes identify three different objects. The proof starts from the supplied word and constructs the two banked graphs. The upstream nine-swap search and its seed generator are outside this derivation. [Proof and comparison contract](PROOF.md) · [Source record](SOURCES.json)

## Reproduce

From the repository root, run on Linux with CPython 3.12 and its standard library.

```sh
python3.12 -B scripts/research_package.py --package research/cf6a-banked-role1256-relay
```

The registered commands rebuild the graphs, replay every arbitrary public input and its adjoint, check every original CLEAR relation, execute the native chart maps, and price the complete signed program with its charged bank service. A separate checker and held-array replay exercise the consequential observations. The package contains its inputs and writes temporary results outside the source tree. [Replay commands](VERIFY.json) · [Evidence](evidence) · [Physical contract](PHYSICAL.md) · [Caller and prices](CALLER.md)

## Open next questions

1. Can an independent maintainer reproduce the relay and verify its import into the selected five-assumption application, particularly the charged retirement of private banks and the new ordered native transform?
2. On the same folded parent, a separate sender/receiver pivot has a positive normalized invoice. A future composition would need to verify the receivers, every common donor, paid order and physical allocation on one combined graph before giving either credit. The present invoice contains only the relay. [Investigation handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19708867)

SYLforge supplied the nine-swap word. DreamingOfClouds, Ali Romman, Rohan Arun and the credited selected-framework contributors supplied its antecedents, bank model and caller. This contribution used substantial OpenAI Codex and ChatGPT Pro assistance. Independent agent checks and a request for maintainer review accompany the conditional claim. [Notices](NOTICE) · [Retained upstream credits](credits)

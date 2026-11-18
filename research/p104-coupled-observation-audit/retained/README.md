# Conditional κ ≥ 0.00382063778168 from grouped P104 helpers and a mixed caller

The construction improves the upper endpoint **0.00378751509487** of PR 7726 by **0.00003312268681**, or **0.87452%**. This increment is **35.87% larger** than the previous increment of 0.00002437823416. The raw crossing is in **[0.00382063778176, 0.00382063778177]**. The compiler uses the stated lower point. [Previous complete proposal](https://github.com/CrocSwap/integer-mult-bounds/pull/7726) · [Complete pricing and compiler receipt](results/application.json)

| Native graph | Caller | Raw κ crossing interval | Certified compiler point in this package |
| --- | --- | --- | --- |
| PR 7726 | Original 16 calls | [0.00378751509486, 0.00378751509487] | 0.00378751509478 in PR 7726 |
| PR 7726 | New 1,024 calls | [0.00379502629537, 0.00379502629538] | Price comparison only |
| New | Original 16 calls | [0.00381302461209, 0.00381302461210] | **0.00381302461201** |
| New | New 1,024 calls | [0.00382063778176, 0.00382063778177] | **0.00382063778168** |

The price margin decreases throughout the tested range. Its upper crossing endpoint puts the fixed invoice within **0.00000000000009** of the certified point. The ordinary BIT pin of **0.00385248** leaves **0.00003184221832** of headroom above that point even if the native circuit or caller improves. Another gain as large as this one would require a higher BIT pin or a change to that compiler requirement. [Signed interval and derivative checks](vendor/interval_gate_signed.py) · [BIT source record](vendor/selected-bit-ambient.json)

## The two contributions to the bound

**Native circuit.** The number of paid transfers per call falls from **5,810 to 5,746**. Two new helpers bring the total to 862 independent helpers and 400 main fields. Where several old transfers share endpoints, a change of basis can put a selected disturbance on one arrival. Nine groups then replace 45 paid arrivals with independent helper entrances. At each affected receiver, a small set of old source equations corrects all the disturbances together. Eight single arrivals, 13 direct relays and two paid splits complete the journal. Every paid and productive rank is counted. [Native proof](PROOF.md) · [Exact edit journal](EDITS.json)

For example, charts 144 and 177 each supply one of two different source equations. Both paid impulses disturb both terminals. One chart reads the sum of the disturbances and the other reads their difference. Together the two equations restore both independent outputs. The verifier derives each chart's observable rows from its six local banks. [Worked two-receiver example](PROOF.md#two-impulses-that-need-each-other) · [Rational evidence](results/witness.json)

**Caller.** A thirty-field root uses fourteen type A contacts and two type B contacts. This permits a finite assignment of different root types to the 104 physical ports at each native call. The batch serves 210,176 root owners and 882,688 native helper owners. It pays for 197,088 caller jobs and 5,883,904 native jobs. The geometry uses 137 axes. All visits of one root share a fixed head direction after an ordinary coordinate permutation and a phase translation at each end of the visit. The ordinary work bill includes these maps. [Caller proof and construction](MIXED-PROOF.md) · [Physical coordinate checks](mixed_geometry.py)

## Replay

Use CPython 3.12 at the repository root. The registered checks use the standard library.

```sh
python3.12 -B scripts/research_package.py --package research/p104-parallel-bank-punctures
```

The forward pass checks 10,950,501 exact scalar products, including 5,941,998 nontrivial exact divisions. A reverse pass checks all 1,262 public columns with a further 15,552,082 products. The catalogue checks every surviving phased chart pair and all native main adapters. The caller replay checks every signed output of each template, every physical port and body color, the 409,600 main bindings, grid precision and ordinary work. A second reader consumes all 17,777,792 emitted instructions. Two modular character probes apply the absolute port actions and compare all 210,176 final owners. The complete application checks both signs of the crossing, the compiler's interior probe, and all 54 strict and four functional outer predicates. [Registered commands](VERIFY.json) · [Forward and caller evidence](results/application.json) · [Reverse evidence](results/witness.json) · [Full emitted batch](results/batch.json)

To export the compact native graph, run the command below. Its SHA-256 is `c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84`. The caller proof includes commands to emit and inspect the chronological caller separately. [Source pins](SOURCE-PINS.json) · [Caller replay](MIXED-PROOF.md#physical-budget-and-reproduction)

```sh
python3.12 -I -B research/p104-parallel-bank-punctures/construction.py > /tmp/p104-parallel-bank.json
```

Both lower points inherit the selected framework's five assumptions for native all-column application, owned erasure, the recursive compiler, precision and tape accounting, and analytic recovery. Independent scientific review is open. These are conditional asymptotic bounds. The package provides no multiplication timing. The maintainer-selected record on the base commit is 0.00363005817. [Assumptions](vendor/selected-claim.json) · [Selected record](../../certificates/selected-result.json)

## Open next questions

- Which other groups of transfers admit independent source equations and local corrections for every surviving output? Rebuild group 26 and vary one source equation while retaining both pulse checks.
- Can a different assignment of the A and B ports give a larger caller gain with the same sixteen body colors? Compare the complete bills at a fixed native graph and charge the head changes at both ends of every visit.

The task card gives the starting points and remaining obligations. Ali Romman prepared the construction with substantial OpenAI Codex assistance. [Task record](TASK.json) · [Credit and source lineage](CREDITS.md) · [Coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19718386)

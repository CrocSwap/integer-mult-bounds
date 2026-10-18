# Independent verification of the eight-transfer threshold, with all 2,502 solutions

**Independent verification; no new κ.** Seed 58 (recursive interfaces), card
`connector-alphabet-change`, refined scope recorded in [TASK.json](TASK.json).
Base `0b1cccf8`; the catalogue is at priority revision 3, which leaves this card
unchanged.

The threshold theorem is **not new here**. Hanson Sun's (bbMisk)
[PR1615](https://github.com/CrocSwap/integer-mult-bounds/pull/1615), at head
`96916897`, answered first:

- **PR1498's question.** It answers open question 1 of bitplane's
  [PR1498](https://github.com/CrocSwap/integer-mult-bounds/pull/1498): six
  transfers fail for every source-port split.
- **The threshold.** Cinna Davis's word from Discussion #1412 reaches eight, so
  the threshold is eight.

This package was built concurrently, without reading PR1615's code. It agrees
with every PR1615 number it overlaps, and adds three things:

1. **Independent re-certification in the generic CI hook.** PR1615's
   registered hook is witness-only, and its exclusion needs a native C++
   workflow. Here a gap-reduction lemma (below) brings the exhaustive `t ≤ 7`
   exclusion and the `t = 8` count into a pure-Python census. It takes about
   20 s and 50 s on 10 cores and runs in the generic Python 3.12 package hook.
   It is cross-checked by two further code-disjoint engines:
   - a C engine that enumerates every placement;
   - a numpy engine with per-occurrence ports.
2. **Every eight-transfer solution.**
   - Exactly **2,502** canonical schedules realize all 31 masks with eight
     transfers.
   - **r = 1** (one source on `z1`) gives 2,376; **r = 5** (all on `z1`) gives
     126.
   - No schedule with r = 0, 2, 3 or 4 is universal at eight transfers. The
     best coverages are 31, 31, 27 and 24 of 32.
   - The r = 5 class is Discussion #1412's restricted-port alphabet, up to
     swapping `z0` and `z1`. The r = 1 schedules lie outside it. Free port choice
     enlarges the solution set but saves no transfer.
   - Every one of the 2,502 is replayed as a complete 80-call program.
   - PR1615's census tool would yield these counts with a small change; they
     are recorded here with replay evidence.
3. **PR1498's four-transfer split bounds.** PR1498 gives bounds
   31, 31, 25, 17, 19, 31 for r = 0…5 and notes they need not be sharp. The
   r = 2 bound of 25 is **not attained**: the exact maximum is 21. The other
   five bounds are exact.

## Interface

The interface is unchanged from
[woklerx's PR1438](https://github.com/CrocSwap/integer-mult-bounds/pull/1438)
and PR1498. PR1438 is merged in-repo as
[two-connector-transfer-boundary](../two-connector-transfer-boundary/README.md).
PR1498 is pinned in [REMOTE-SOURCES.json](REMOTE-SOURCES.json).

**Rows.**
- Five read-only source rows `x_j`.
- 31 output rows `y_m`, one per nonzero mask `m` in F2⁵.
- Two independent arbitrary-dirty connector rows `z0` and `z1`.

**Complete operations.**
- `B_j(p): z_p += B_j x_j`.
- `A_m(p): y_m += A_m z_p`.
- One paid one-way transfer `C: z0 += z1`.

**Constraints.**
- Ports are chosen freely at every occurrence, and are charged.
- Every `B_j` and every `A_m` occurs exactly twice: 10 B and 62 A calls.
- Every source and both connectors are restored.
- The maps are generic, non-commuting F2-linear maps, and the dirt is
  arbitrary.

PR1498 step 1 shows that restoration forces both calls of a source onto one
port. A mask is realizable exactly when two cuts on the same connector have
equal dirt and source parts that differ by that mask.

## Census

| `t` | Universal schedules | Maximum masks covered (of 32) by port split r = 0…5 |
| --- | --- | --- |
| 1, 3, 5 | none: no schedule restores the connectors | — |
| 0 | 0 | 31, 17, 11, 11, 17, 31 |
| 4 | 0 | 31, 31, **21**, 17, 19, 31 |
| 6 | 0 | 31, 31, 28, 22, 23, 31 (as in PR1615) |
| 8 | **2,502** (r = 1: 2,376; r = 5: 126) | 31, 32, 31, 27, 24, 32 |

Counts use canonical words, with labels by first occurrence, and one port per
source.

## Gap reduction

Between two consecutive B calls `z1` is fixed. Further transfers there only
alternate `z0` between two states of opposite dirt parity. So three transfers
in one gap give the same readout states and parities as one, and four give the
same as two.

A schedule with three or more transfers in some gap therefore reduces to a
schedule with `t − 2` transfers, identical coverage and unchanged restoration
parities. This has three consequences:

- censuses with at most two transfers per gap, run at `t = 0, 4, 6`, together
  with PR1438's full-placement `t = 2` census (no 32-mask bin), exclude every
  universal schedule with `t ≤ 7`;
- odd `t` cannot restore the dirt;
- at `t = 8`, a universal schedule with a long gap would reduce to a universal
  `t = 6` schedule, so the reduced count of 2,502 is the exact count.

## Verification

```sh
python3 scripts/research_package.py --package research/two-connector-eight-transfer-census-seed58 --check-only
python3.12 scripts/research_package.py --package research/two-connector-eight-transfer-census-seed58
```

`verify.py` uses only the standard library, parallelised over words. It has
three registered parts.

1. **`controls`.** The engine reproduces:
   - PR943's in-repo 105- and 945-word censuses for 4 and 5 sources, bin for
     bin;
   - PR1438's in-repo full-placement `t = 2` censuses for 1 to 5 sources: every
     restored count and coverage histogram, with no gap reduction;
   - at `t = 0` and `t = 4`, every port split: no universal schedule, with the
     complete per-split coverage histogram pinned;
   - no restored schedule for `t = 1, 3, 5`.
2. **`six`.** An exhaustive `t = 6` census over all 945 words and 32 port
   splits: 44,936,640 restored reduced schedules, none universal, with the
   per-split maxima and the complete coverage histogram pinned.
3. **`eight`.** An exhaustive `t = 8` census:
   - exactly 2,502 universal schedules, with a pinned SHA-256 of the sorted list
     (`ba04f277…`) and the split counts;
   - each becomes an 80-call program (62 A, 10 B, 8 C), run on dense random
     non-commuting F2 maps with arbitrary dirt;
   - Discussion #1412's pilot is among them;
   - on three witnesses (the first r = 1 schedule, the first r = 5 schedule and
     the pilot), deleting any `C` or `A`, or reading any `A` on the wrong port,
     fails.

**Independent engine (offline).**
[independent/census.c](independent/census.c) enumerates every transfer
placement, with no gap reduction. It agrees on every per-split maximum, and
reproduces PR1615's `t = 6` totals:

| `t` | Candidates | Restored | Universal |
| --- | --- | --- | --- |
| 4 | 30,270,240 | 10,402,560 | 0 |
| 6 | 242,161,920 | 74,692,800 | 0 |
| 8 | 1,323,241,920 | 384,199,200 | 2,502 |

Run it with `cc -O2 -o census independent/census.c && ./census 8 0 1`, or
slice it with `./census 8 <slice> <slices>`. The receipts are in
[EXPECTED.json](EXPECTED.json).

[independent/census_numpy.py](independent/census_numpy.py) lets every
occurrence choose its own port, filtered by exact `z1` restoration.

| `t` | Legal schedules | Universal | Run time |
| --- | --- | --- | --- |
| 4 | 10,402,560 | 0 | — |
| 6 | 74,692,800 | 0 | 842 s on one core |

Both match the per-split maxima above. So does PR1498's lemma that
restoration forces one port per source.

## Scope

- **Family:** only the incidence-minimal 72-operator-call family. Extra or odd
  A/B incidences, reverse or bidirectional transfers, combined queries and
  source mutations are not covered.
- **Proof:** a finite census with a short reduction lemma.
- **No supplier claim and no κ change.** The completed-price condition is
  PR1498's `t·σ` tariff, instantiated at `t = 8` by PR1615: `8σ + ΔH < 2c`
  against the 74-call repair, under equal port prices.

## Open next questions

The structured entries are in [TASK.json](TASK.json).

1. **Is there a short structural proof that six transfers fail?** It should
   also explain why only r = 1 and r = 5 reach eight. A projection argument
   like PR1498's step 2 might do both, and it would remove the census
   dependency.
   - *First step:* classify the 2,502 witnesses by their transfer phases `u_i`.
   - *Blocker:* none.
2. **Can extra incidences lower the threshold?** This is PR1615's question 1.
   - *First step:* extend `engine.py` to 73 calls, with full dirt vectors per
     readout.
   - *Blocker:* the paired-readout reduction no longer applies.

## Credit

- **Hanson Sun (bbMisk), PR1615:** the six-transfer exclusion and the sharp
  threshold, with priority.
- **Gareth Davidson (bitplane), PR1498:** the four-transfer obstruction,
  source-port lemma, tariff and open question.
- **woklerx, PR1438:** the two-connector interface and full-placement censuses.
- **Cinna Davis (1337isnot1337), Discussion #1412:** the eight-transfer
  construction.
- **Ross Richardson, PR943:** the universal-connector boundary and 945-word
  census.

Prepared by Sagar Thakrar with substantial Anthropic Claude assistance. That
included explorer and judge subagents, two of which wrote the independent
engines. New work is Apache-2.0.

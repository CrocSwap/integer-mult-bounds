# Partial leaver cells on #1005's word: a negative result (no κ claim)

**No κ claim.** This note tests the obvious next step after #1005: extending mutable-leaver cells beyond the eight all-K cells. It does not raise κ. The note records why, because two of the obstructions will bind any further leaver-style rewrite on this line.

## Setup

#1005 replaced the eight all-K delivery cells with helper-free circuits that use *leaver* sources (registers with no later reads) as scratch. Outside those cells, 144 face events remain. Only 32 of them have leaver operands. They form **16 keys** (p, ε) with leaver operands in exactly two of their three blocks: the two blocks whose targets request the face. The third block (0123 for eight keys, 4567 for the other eight) feeds an M combination instead. Each of these keys uses three face copies and one slot copy. No other key has leaver operands in all three blocks, which is why #1005 stopped at eight cells.

For each key, four targets each need four of five inputs (their own row, the other leaver pair, and the third block's face), and one register must end holding the sum of the four leaver inputs (M).

## Method

- **Exact legality as taint bits.** A register frame F fits target t's hyperplane iff every generator of F is orthogonal to the port P_t. That property is a union under frame joins. So frame legality for these circuits is exactly a few bits per register: one per circuit target, plus one per class of downstream targets whose final-frame allowance can bind.
- **Layered CP-SAT** (`code/satcell.py`) over set and taint states, with optional helper registers, target-to-target gates on/off, reader constraints for kept helpers, and allowances on final frames.
- **Construction hook** (`patches/cgx_leaver.patch`): applies a circuit template per key inside #1005's constructor, drops the freed copies through the helper map exactly as #1005 drops its copies, and recomputes frames. The constructor's own exact identity check runs unchanged.
- **Port stages.** Moving own-row reads breaks the port stage's gate alignment (the all-K cells lose their anchor and land before the entrance reads). `patches/port_stage_x.patch` adds two construction-side options: successor anchoring for unmatched gates (`PORT_SUCC`) and a monotone frame repair that reports any hyperplane violation (`PORT_REPAIR`). On #1005's own word both are byte-identical no-ops. On every variant below, all four port stages needed **zero** repairs.
- **Verification** is the inherited chain: regroup, HPE, cold44, then the native audit (exact forward and inverse replay with arbitrary dirt), ledgers and the local replay.

## Results

Profiles are measured on the cold-end word (before #1005's later layers), as a per-call delta against #1005's cell word. κ is #1005's global profile plus 72 × delta, with the saved rank mass placed as rank-48 idle (ideal packing, an upper bound on what an owner map can achieve). Bits are the local replay's coefficient bound (L1 prefix), which must stay below **192**.

| variant | helpers removed | cold-end pairing in the 8 touched blocks | native audit | bits (fwd) | κ, ideal packing |
|---|---|---|---|---|---|
| #1005 baseline | 0 | 4 each | pass | 188 | 0.001671387264390146 |
| one helper + 2 target-to-target gates (reuses an entering copy) | 32 | 0 | **fail**: zero-frame compensation reads an entering helper | — | (0.00168268 if it were legal) |
| two kept entering copies, all 16 keys | 16 | 0–1 | pass, all stages | 107 | 0.0016650 (loss) |
| one fresh non-entering helper, all 16 keys | 32 | 0 | pass | **210** (over the cap) | 0.0016702 (loss) |
| one fresh helper, 4567 class only | 16 | 2 each | pass | **203** (over the cap) | 0.0016723 (+0.05 %) |
| one fresh helper, one key | 2 | 3 in two blocks | pass | 187 | 0.0016712 (loss) |

`reproduce.sh` rebuilds every row and writes `RESULTS.json` with the exact deltas, pairing ranks, stage outcomes, bits and prices.

## Obstructions

1. **The packet copies are entering helpers.** After the port stages, the copies start holding arbitrary dirt, and each original reader pre-reads the copy so its dirt cancels. A kept copy must therefore be read exactly once by each of its original readers, and no circuit may copy a dirty target into another target. The 32-helper circuit violates both and the native audit rejects it. With own rows first and one helper, CP-SAT proves the key infeasible (L ≤ 20); with one *fresh* helper the audit passes, but fresh helpers start at the zero frame and add rank-1 climbs.
2. **Cold-end pairing collapses.** Every target in the eight touched blocks belongs to one of the 16 keys. Using their own-row registers as leavers moves all of them out of the block frame, so the rank-4 cold-end pairing in those blocks falls from 4 to 0–2. The copies were what kept the own rows inside their blocks. At roughly the same price per item, a lost cold end costs about as much as a removed helper earns.
3. **The 192-bit coefficient allowance is nearly exhausted.** #1005's word already needs 188 of the 192 bits allowed by the local payload rule, attained in the full-frame cleanup of block 4567's scratch registers. Leaver rewrites add accumulation chains: eight circuits push it to 203 bits and sixteen to 210. Only one or two circuits fit. Anyone extending #1005's line with more leaver mutations will hit this bound before the others.

## Reproduce

```sh
bash research/leaver-partial-cells/reproduce.sh . /tmp/gauge44-pr635 /tmp/leaver-partial-cells
```

The second argument is the pinned #635 supplier prepared as in #645. The script runs #645's no-triangle base, #1005's cell driver with its pins checked, the census, the raw-level template checks and the five variants, then prices them. It takes about 45 minutes on a laptop.

The circuit search is optional and needs ortools. For example, after a run:

```sh
PC_CENSUS=/tmp/leaver-partial-cells/census/raw/CENSUS.pkl PC_PROTO=/tmp/leaver-partial-cells/notri-base/hamming/PROTOTYPE.json \
PC_PORTED=/tmp/leaver-partial-cells/base/port3/FULL-WORD.json.gz PCELL_MOVEOWN=1 PCELL_H2=0 \
python research/leaver-partial-cells/code/postport.py "((0,2),1)" 1500 2
```

`TEMPLATES.json` holds the four circuits used above.

## Scope

Finite, local measurements on #1005's cell word. Prices assume ideal owner packing and omit #1005's later layers (NP and p6n ends, promotions, hybrids, frame re-optimisation), which act mostly on other registers. The negative conclusions do not depend on either: the legal variants lose or break the 192-bit rule before any layer is applied.

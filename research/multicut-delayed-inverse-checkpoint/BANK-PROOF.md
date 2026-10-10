# Exact bank delta for the PR259 replacement

This document explains the selected five-quartet removal, seven delayed-inverse
interval insertion and final once-counted 25 retimings. The bundled
[bank_check.py](bank_check.py) and [bank_template.py](bank_template.py) check the
actual retimed source context and global ledger. The complete construction's
evidence and inherited assumptions are stated in [PROOF.md](PROOF.md).

## Literal capacity and role assignment

The focused source has 16,587 independent helper roles, of which 2,827 have a
nonzero entrance. Its residual rank counts are

```
4:2200, 6:22, 7:7, 9:4, 10:8, 11:55, 12:30, 13:14, 14:2,
15:20, 16:1, 18:1, 19:31, 20:19, 21:3, 22:41, 23:369, 24:13760.
```

Their sum is 16,587 and their residual volume is 351,267 per replica. For each
residual width r other than 4 and 24, use 10 times its role count banks with four
blocks of width r and 30-r blocks of width 4. Each such bank has exactly
4r+4(30-r)=120 coordinates. This uses 65,830 of the 88,000 available width-4
occurrences across 40 replicas. The remaining 22,170 width-4 occurrences fill
739 banks of 30 blocks. The 550,400 width-24 occurrences fill 110,080 banks of
five blocks. There is no rounding, unused capacity, or fractional bank.

This gives 117,089 banks per stage and 585,445 stage-private bank families across
five stages. There are 40*4*1760=281,600 data families, for literal stock 867,045.
The one external work family is separate from the live-stock count.

Roles retain their actual original IDs. Within each residual family they are
sorted, and occurrence q means role floor(q/40), replica q modulo 40. The segment
mapping in bank_template.py assigns every occurrence to one contiguous bank
block. bank_check.py independently enumerates sequential slots and compares all
3,317,400 stage/replica/role assignments against that callable mapping. The
bundled production census also checks the exact role set against physical ownership,
borrowed roles, and removed roles. No source producer or ownership is changed.

## Generic charts and full addresses

All 770 actual entrance frame IDs are rebuilt. For an actual source basis S and
its Euclidean annihilator row a, the residual vector is 15a-sum(a)*1, divided by
its integer row gcd. It is orthogonal to S for the actual form 9I-J. The residual
vectors followed by S form a 24-column chart B. The checker computes A,d with
BA=AB=dI, checks projector action on every chart column, and replays every exact
rational row factor to the identity. This establishes independence and exact
conjugacy without a norm-four or rank-one special case. The checked maxima are
576 chart factors, factor numerator 165, and denominator 1080.

For a stage i and assigned block b, the normalizer is
N=(b+1) Pi embed_i(B^-1). Pi sends the actual residual coordinate window to its
assigned contiguous block. A column outside the stage window is fixed by the
embedded chart; its image under N is (b+1)e_(Pi(j)). Distinct blocks have distinct
positive scalars, so these witnesses distinguish the normalizers even when
chart matrices repeat. All full (family, route) namespaces are injective for all
200 stage/replica pairs, including both active data banks, all helpers, and the
external work register. The 34,965 intentional same-family coincidences retain
different full routes. Equality of family numbers alone is not an address test.

The production callable lowering preserves every scalar, frame, projection,
stage and reversal field and changes only actual stream operands. ADD/COPY
operands are checked for full-address nonaliasing. Original helper class
d*tau_i is routed to bank class d*tau_i*N^-1. The inverse-normalizer multiplication
order and all denominators are retained. Every actual logical operand and all
five paid stage streams are bound by the fresh checker before acceptance.

## Complete banks and completion discharge

Every bank pattern partitions all 120 coordinates. Its disjoint projected block
swaps therefore give the full swap on all 240 arbitrary-dirty bank/work columns.
The inverse word restores all columns. bank_check.py tests omission and repetition
of every individual block in every one of the 18 patterns. The phase-major
schedule completes all cover classes for each replica before proceeding;
boundary phases follow all 40 replicas of their stage. Banks are stage-private.

There are 2,827 independent entrance completions with width counts

```
5:369, 10:41, 15:3, 20:19, 25:31, 30:1, 40:1, 45:20,
50:2, 55:14, 60:30, 65:55, 70:8, 75:4, 85:7, 90:22, 100:2200.
```

The checker matches the exact tagged entrance list and every completion record
before subtracting these counts. Widths 5, 10, 15, 20 and 50 also have ordinary
paid children. It subtracts only the tagged count and deletes a histogram bucket
only if the remainder is zero. A whole-bucket deletion would fail the retained
ordinary-child assertions and exact ledger comparison. The address mapper rejects
completion opcode 6; discharge is explicit, never a silent mapper shortcut.

## Retiming boundary and conservative tariff

The focused source before the 25 compatible retimings has 494,670 retained
five-stage calls per replica and rank mass 2,596,735. Retimings preserve all
entrance gauges, charts, packing and rank mass. The final checked count is
494,665 per replica, reconstructed by bank_check.py from the actual live ledger.
Forty replicas have rank mass 103,869,400 and deficit
120*867045-103869400=176000.

The normalizer bound remains the conservative 838: 576+119+120=815 is below it.
No faster route or selector tariff is claimed. The charged selector allowance is

```
2*5*40*((867045-1)+16587*120*838) = 667542305600 < 2^40.
```

## Actual retimed registry binding

The final raw word is
acf510b1377a6bd96eea50577de1aa049382499335fa7e5cac9b0300ecb377c7.
The bundled checker reconstructs its initial frames and actual entrance bases.
The actual 770-chart hash is
98d3fbe41db017678b416bdffe4e79361ad08ceda99a84eed340a7dc9d1467d2.
These chart IDs contain 459 distinct entrance bases. An exact rebuild checks
both inverses and every rational factor for the actual registry. The maxima
are 576 factors, numerator 165 and denominator 1080.

Annihilator row sign changes do not change the represented subspace.
Assignment and namespace separation use the actual reconstructed charts;
the outside-column separation proof is invariant under such sign choices.
No earlier chart presentation is an input to these checks.

The live callable bank checks bind all five actual operand streams, all
2,827 tagged completions, the charts, the assignment and the full namespaces.
The actual global ledger confirms 494,665 retained calls and rank mass
2,596,735 per replica after subtracting precisely those completions. Across
forty replicas its literal histogram has 19,786,600 calls and rank mass
103,869,400. The complete verifier also checks the current prime inventory,
exact moments, outer inequalities and finite bill. These finite checks retain
the conditional theorem interfaces described in PROOF.md.

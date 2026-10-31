# Two paid queries replaced by a prepared split helper

Use PR5599's exact complete word at
`0644592d421b375c221045954fdf13932575ffa8`.
Its fifteen helper splits, scalar bases, phase conventions and caller remain
credited to that source. This construction changes only the preparation
and two queries described below.

## Exact source-version identities

Write `h_r` for original input r and `x_r` for its current normalized value.
The source has 750 independent productive inputs and eight owned roles.
Fresh exact replay, before any preparation, proves:

| Source event | Current-value identity | Paid source operation |
| --- | --- | --- |
| 13670 | `x573-x572+2*x732 = -2*h573` | `MOVE 573: 3 -> 595`, rank 1 |
| 13691 | `x573-x572-2*x710 = -2*h573` | `MOVE 573: 595 -> 603`, rank 1 |

The identities include every source input coefficient and current data version.
They are derived by `verify.py:source_relations`, rather than read from a
saved relation table. The source scalar basis changes are included in replay.

Source helper 573 starts at frame 3, the zero subspace, and finishes at
frame 603, a two-dimensional subspace. It is the rank-two prefix target
created by PR5599's eleventh split. The rank-seven successor has its own
independent input and remains in the word.

Declare role 573 owned and initialize it to zero before the source's entry
basis program. Its arbitrary dirty entry is erased. Thus `h573=0` is an
internal preparation, not a promise on any retained productive input.
Remove its rank-two target from the productive invoice.

All other source output rows are independent of `h573`. Exact replay of the
new word checks all 749 retained independent inputs, 208 main outputs,
541 helper outputs and every owned return. A dense integer transpose checks
the same complete linear map through a separate arithmetic path.

## Explicit replacements

At source event 13670, roles 572 and 732 are already at frame 595.
Replace the rank-one MOVE with:

```text
CLEAR 573 at 3
INIT 573 at 595
COPY 573 <- 572
ADD 573 += -2*732
```

The first identity proves that this gives the required value in frame 595.
Keep the following source ADD and every later source instruction.

At source event 13691, roles 572 and 710 are already at frame 603.
Replace the rank-one MOVE with:

```text
CLEAR 573 at 595
INIT 573 at 603
COPY 573 <- 572
ADD 573 += 2*710
```

The second identity proves that this gives the required value in frame 603.
In particular, the following source SCALE and split basis operations remain
unchanged. No operation is moved across their reads or writes.

After the source program, clear role 573 at frame 603. Its exact output was
already zero because its prepared input was zero. The eight original owned
roles retain their source operations and cleanup.

The word has 758 total roles, nine owned roles, eleven owned lifetimes and
peak owned occupancy two. All nine original dirty owned columns vanish from
all outputs. The new instructions use only the source INIT, CLEAR, COPY and
ADD operations. Neither a zero retag nor a new Gaussian operator is needed.

## Native meaning and every positive width

The normalized row in a frame denotes a linear combination of arbitrary
original fields under that frame's native operator. Both reconstructed
values use sources already in the required physical frame.
The COPY and scalar ADD operations therefore act on the actual physical
fields, with no omitted transport or phase correction.

For each legal positive tensor width f, substitute the tensor power of every
source native chart. Keep rational scalar coefficients outside the tensor
power. Equal charts commute with these whole-field scalar combinations.
The two source identities therefore prove both replacements at every width,
under the same native premise as the source.

No retained independent input is copied into another productive input slot.
Role 573 is owned and receives no target credit. Its old external entrance
normalizer can be omitted because its input is replaced by zero. Its old
exit normalizer can be omitted because its output is owned zero.
All other helper normalizers and both main interfaces remain unchanged.

The verifier checks that every retained paid-map pair occurs in the source.
The source native evaluator rechecks the signed Pauli images and absolute
phase anchors of all those maps, all original helper endpoints, and the
208 main adapters. Checking the discarded helper endpoint is harmless extra
evidence; its target and two unused normalizers are removed from accounting.

## Complete invoice and conditional bound

The local paid profile is:

```text
{1:2209, 2:459, 3:494, 4:94, 5:164, 6:18, 7:14}.
```

The retained productive helper profile is:

```text
{1:4, 2:4, 4:90, 5:10, 7:5, 8:18, 9:410}.
```

Relative to PR5599, the local paid delta is `-2 H1`, and the target delta
is `-H2`. For `0<t<1`, `2^t<2`. The target-minus-paid moment therefore
increases by `2-2^t>0`. At t=1 the delta is zero.

The unchanged physical controller has 18 local calls, 15 thin query stages
and 15 whole idle stages. Each call uses its own 541 fresh helper inputs.
It invokes the complete new supplier, which returns all owned storage zero.
The global deltas are `-36 H1` paid and `-18 H2` productive.
There are 66,816 paid jobs and 13,066 independent productive fields.
The complete rank surplus stays 760.

The new word has 25,510 instructions and scalar allowance 220,432.
All initialization, erasure, copying, scalar operations and routes are charged.
The route allowance includes eleven owned lifetimes and peak occupancy two.
The local cap 10^7 and global cap 10^9 remain sufficient.
The added owned role replaces a productive role, so the total field count
stays 758. The native paid-rank sum is recomputed from the changed word.

All scalar coefficients are dyadic and satisfy the source growth bound.
There are fewer than 26,000 operations, each with growth below 2^16.
The same precision and tape premise covers this explicit finite template
with its charged constants. The rounded multiplier is not materialized.

The source pricing code is retained with the exact edits listed in
`PRICING-EDITS.json`. The target debit is included in both completion tails.
The source's tail decay 39/40 and compiler logarithm power 1024 are retained.
Two rational moment engines test saving 0.0030987101 and fund the claim
**kappa=0.00309871**. They also reproduce PR5599's predecessor crossing.
The same run checks the compiler threshold, BIT stock, 54 strict outer
predicates and four functional predicates.

The five inherited framework assumptions remain. This is an author-checked
conditional construction, without independent human or proof-kernel acceptance.

# Generate exact chronological compiler libraries from product tables

For a fixed separated default-height mixed rule, this package computes
every replication, productive width, expanded rank-one leaf count and
expanded mixed-unit count through rank N as evaluated binary integers.
It avoids enumerating paid paths and individual unit slots.

The [proof](PROOF.md) gives explicit parameter-dependent bounds. In its
declared indexed metadata model the bit work is `N*polylog N`; a separately
specified fixed-tape scan construction costs `N^2*polylog N`. The powers
and constants depend on the fixed rule through K, Z and the local-table
formulas. This is not polynomial in log N: N completed library rows are
output. No native scalar word or physical source-routing program is emitted.

## Exact result and predecessor delta

The least chronological gcd/LCM policy is unchanged. Source complements
retain their actual multiplicities, and each deepest exit retains its
original one-job cut. Ordered target-word and paid-word product tables
recover fresh sources by subtracting matched incoming jobs from all target
slots. Coincident products add counts; paid positions retain multiplicity.
Source rank n has no complementary program.

```
a_n=lcm({B_(n-s)/gcd(B_(n-s),S_s):s<n}
        union {B_e:rank-e exits exist}),
B_n=a_n*sum_s S_s.
```

P_n and O_n add all whole smaller-program copies; O_n also counts outer
unit instances. O_n is an expanded occurrence count, not live physical
storage. Exit multiplicities may combine in addition, never in a pooled
gcd denominator.

[#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507) and
[#5071](https://github.com/CrocSwap/integer-mult-bounds/pull/5071) already
supply the recurrence; [#4638](https://github.com/CrocSwap/integer-mult-bounds/pull/4638)
and [#5962](https://github.com/CrocSwap/integer-mult-bounds/pull/5962) supply
strong width bounds. The added result is exact all-rank generation with
compressed counts and complete metadata costs. A normalized contracting-chain
argument bounds P_n and O_n without positive rank surplus. No factorization
or unevaluated arithmetic expression is hidden in the computation.

The prior [source-complement-port package](https://github.com/CubeJerry/integer-mult-bounds/tree/bd63147b1a193f68b5713e5814ac3b2c743beff8/research/source-complement-port-index)
identifies individual sources and ports. This package evaluates their
smaller-library numerical data. It does not infer native-program validity
from a numerical width.

## Reproduce

Python 3.12 and standard library only, from this directory:

```sh
python -I -W error -B verify.py
python -I -O -W error -B verify.py
```

Both produce the same JSON receipt with status
`PASS_QUANTITATIVE_RANK_LIBRARY`. The checker authenticates eight inert
source texts, imports no predecessor compiler/verifier, and constructs an
independent literal role-word/path graph with unique incoming edges.
Prime-deficit replication and normalized Fraction recurrences check all
four output integers by a different route.

Executed author evidence includes 35 literal fixtures, 1,061 complete
library rows, 24,586 units, 51,727 separate cuts and 14,278 fresh source
occurrences. Two fixtures have negative rank surplus. Fifteen rejection
controls cover invalid domains/capacities, product overwrite, missing
incoming subtraction, fit equality, omitted outer units and merged roles.

A separate 2,048-row negative-surplus example has maximum output fields
of 336 bits and inspects 85,044 product pairs. Its largest height has
387,420,489 paid-path labels, which are not enumerated. Another 1,023
homogeneous rows agree with the credited [#6612](https://github.com/CrocSwap/integer-mult-bounds/pull/6612)
formula; this is calibration, not a new width result.

The separate tape worker supplied a strict-separation pooling control:
targets `(3,3,5)`, paid `(2,2)`, n=135. Sixteen separate rank-16 cuts each
require B_16=24. Correct replication is 12,509,640; pooling yields
1,563,705, with remainder 9 modulo 24. The evaluator rejects that
nonintegral individual invocation despite aggregate divisibility.

## Limits, next obligation and credit

Default executable capacities are rank <=4,096, local record bounds
<=200,000 and arithmetic values <=16,384 bits. These bound the reference
experiments, not the written universal theorem. The literal oracle has
a separate small domain. Python is not claimed to be the sequential
tape construction whose scans are specified and priced in the proof.

Native scalar instructions, coefficient encodings and adapter production
need additional bounds. All-column correctness, owned initialization and
erasure, physical stock/routing, precision/tapes, analytic recovery and
the complete outer theorem remain conditional. The selected conditional
kappa remains `0.00363005817`; no selected astronomical library is emitted.
Independent AI reviews are separate; no human or proof-kernel acceptance
is claimed. The next useful obligation is to attach an actual permitted
local-word/adapter producer with its encoded output-cost bound.

Prepared for @CubeJerry with substantial OpenAI assistance. Credit Jacob
Alan Sussman for the lockstep/Pascal compiler, zxv for the retained flow,
Mihir Srivastava (#4507/#4586), codyw912 (#4638), Nick Petalas (#5962/#6612),
#5071's symbolic batch proof and the full retained native/flow lineage.
The source-row and source-port packages supply occurrence identities.
New material is Apache-2.0. Copied reference texts retain their original
notices and exact source pins.

## Independent acceptance checks

[REVIEW.md](REVIEW.md) records the root's separate proof/code review and
literal target-field/parent-edge oracle. That oracle checks every census and
all four library outputs for seven fixed rules and 336 complete ranks, with
zero/negative surplus and coincident products included. It rejects an actual
exit-pooling mutant on the smaller n=12 witness, an exceeded rank budget and
a nonseparated rule. [The complementary peer review](peer-review/REVIEW.md)
independently authenticates the retained width/flow sources, audits all
indexed and sequential costs, and verifies a different n=135 cut witness.

```sh
python3 -I -W error -B research/quantitative-rank-library/independent_check.py
python3 -I -W error -B research/quantitative-rank-library/peer-review/exit_cut_control.py
```

Final packaged author normal and optimized runs agree. The independent
scientific receipts pin the reviewed bytes. No human or proof-kernel
acceptance is inferred. The complete proposed PR description is `PR.md`.

## Open next questions

Can the evaluated leaf/unit counts be bound to an actual emitted native
scalar-word and owner manifest with a complete bit-output/production bound?
This matters because numerical library generation does not by itself
construct the smaller programs. The first step is to audit the retained
#6878 occurrence adapters and the native word's constant encodings; the
obligation is blocked by any missing uniform local-word/adapter producer.

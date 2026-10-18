# Linear aggregate padding on a fixed set of bit tapes

PR [#2457](https://github.com/CrocSwap/integer-mult-bounds/pull/2457) proves a
binary-spectator completion lemma under an explicitly assumed linear charged
scan. This package supplies that scan for the five aggregate fields
`[P,Q,G,Q,S]`: an executable one-cell tape machine, a uniform amortized bound,
and translated-origin/head/cleanup checks. It does not implement the completed
fast exchange or its ancestor-parking contract.

For positive cardinalities `q_i`, let `L_i=ceil(log2(q_i))`,
`R_i=2^L_i`, `N=product R_i`, and `D=sum L_i`. Empty binary descriptors represent
singleton fields. Padding and restriction each use **17 tapes**: three for
each of five coordinates, one input and one output. The alphabet is the fixed
set `{0,1,^,$,_}`. Each operation reads one cell, writes one cell or moves one
head one cell. The model charges these operations and constant finite-control
work; it supplies no unit-cost integer coordinate or random-access primitive.

Given canonical binary descriptors of `q_i-1` and owned zero counter cells,
each complete scan costs at most

```
1024 N + 128 D + 128
```

charged primitive steps. This deliberately loose bound is independent of
ancestor depth and cardinality bit lengths except for the additive setup term.
The data heads finish at their initial first-cell positions, descriptors are
unchanged, and both counter tapes per coordinate return to all-zero work.
Output is the requested padded/restricted data, so it is retained rather than
erased. Inputs and all cells outside the owned delimited intervals are fixed.

## Machine and correctness

`tapes.py` contains the machine. `Tape` is its instrumented ordinary tape
semantics; only `read`, `write` and one-cell `move` are used by its routines.
Host integer arithmetic in the test harness serializes inputs and measures
traces. It is not used to compute a cursor coordinate during the scan.

For each coordinate keep two little-endian counters of width L:

* padded remaining, initialized to `2^L-1` by writing ones;
* genuine remaining, initialized by copying the immutable `q-1` descriptor.

A finite-control bit initially marks the coordinate genuine. After each
coordinate visit, decrement padded remaining modulo `2^L`. While genuine,
also decrement genuine remaining; its borrow out clears the genuine flag.
On padded borrow out, recopy the descriptor and set genuine true. The padded
borrow propagates to the next outer coordinate. Five coordinates and five
flags are fixed, so this is finite control. An empty counter borrows on every
visit and correctly represents a singleton.

At position x in a coordinate cycle, padded remaining is `2^L-1-x` and the
flag is true exactly when `x<q`. While true, genuine remaining is `q-1-x`.
This invariant follows by induction through the three decrement/borrow cases.
The five nested cycles therefore visit the padded lexicographic rectangle
exactly once and mark precisely its genuine subrectangle. Genuine positions
occur in original lexicographic order. Padding consumes the next source bit
there and writes owned zero elsewhere; restriction consumes every padded bit
and emits exactly the genuine ones. No payload-dependent routing occurs.

Every decrement and descriptor copy rewinds by scanning to the left marker;
no head jump is free. After the outer borrow, every coordinate has completed
an integer number of cycles. Clearing owned work by one marker-delimited pass
restores its initial zeros. Data heads rewind by scanning their entire used
intervals. Arbitrary translated origins do not change the transition word or
cost; the machine never crosses either marker except moving onto a right
marker to detect borrow/end. The fixed-marker input/work intervals and fresh
output region are part of the ownership contract.

## Uniform cost proof

Consider one coordinate cycle of length R=2^L. For positive values v, binary
decrement inspects `1+nu_2(v)` bits before rewinding. The elementary count
`sum_(v=1)^m nu_2(v)=sum_(j>=1) floor(m/2^j) <= m` bounds any initial countdown
from m to zero. The single decrement of zero traverses L bits and its marker.
Thus all decrement bit visits in a full padded cycle are at most `2R+L`;
the genuine countdown uses at most `2q+L <= 2R+L`. Frozen genuine periods
perform no genuine-counter scan. Descriptor reset and both head rewinds cost
O(L), once per complete coordinate cycle, not once per payload row.

Counting the reads, writes, marker tests, one-cell moves and constant control
in the displayed routines gives a conservative `64R+64L+64` steps per cycle,
including reset. For L>=1, `L<=R` and `1<=R`, so this is at most `192R`.
The L=0 singleton case takes fewer than 192 steps directly. Coordinate i
executes `N/R_i` or fewer whole cycles: inner fields cycle more often, outer
fields less often. Its total is at most `192N`; all five cost at most `960N`.
Payload reads/writes/moves, emission control and final data rewinds cost at
most `16N+16`. Initial counter setup and final clearing cost at most
`128D+64`. Hence the claimed `1024N+128D+128` upper bound.

The test counter uses the same primitive accounting; the bound is proved by
the countdown argument, not extrapolated from timings. Finite-control tests
over five flags can be expanded into a fixed number of transitions; the
slack in the bound covers that expansion. This is an explicit multi-tape
algorithm, not a compiled table of every finite-control state or a measured
wall-clock complexity claim.

## Composition with PR2457 and boundary

For `[P,Q,G,Q,S]`, PR2457 already proves `N<32 P Q^2 G S`, or `<8 P Q^2 G S`
when Q is binary-complete. Those volume factors and its completed-exchange
argument retain their credit. This implementation discharges the linear
padding/restriction scan for **aggregate canonical descriptors**. It also
makes the cleanup and local head behavior concrete. It does not reparse
arbitrarily many singleton ancestor descriptors at every call.

The machine assumes owned zero counter cells and a fresh output interval,
plus valid canonical descriptor/interval lengths. Obtaining that ownership,
parking unbounded caller contents, computing aggregate descriptors, invoking
a real fast completed callee, and joining the selected recursive caller are
separate obligations. Malformed/unbounded tapes are not an adversarial input
parser contract. Restriction must still occur after the complete callee
endpoint. The indexed exchange in the tests is a semantic oracle only.
No stock coefficient, supplier, selected kappa, all-size multiplication theorem
or complete physical caller is claimed.

## Reproduce

```sh
python3.12 -I -B scripts/research_package.py --package research/aggregate-padding-tapes
```

The checker compares against a separate mixed-radix rectangle oracle, tests
translated origins, all Boolean payloads on one small nonbinary-gap fixture,
source immutability, counter cleanup and exact primitive counts. Semantic
controls remove the genuine reset or corrupt a descriptor/endpoint; a counter
microcheck independently measures every small countdown. The uniform proof
remains a written proof, not a proof-assistant theorem.

## Provenance and open next questions

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority four; assignment nonce
`8330d61012b3611fa2f3917e7e0b6151`. The selected-stock baseline passed. Existing
stock/depth/later-stage work already covers those candidate questions, so
`TASK.json` declares the change to a concrete uniform-transfer scan obligation.
Exact PR2457 source pins are historical attribution; no predecessor code is
imported. Claim: [PR2457 comment](https://github.com/CrocSwap/integer-mult-bounds/pull/2457#issuecomment-6196912013).

## Open next questions

Join the scan to an actual completed exchange at translated parking origins,
charging acquisition/clearing of its owned intervals and preserving caller
metadata. First expose the callee's actual head/work/parking interface and
replace the indexed oracle. The fast callee and that joined physical ownership
contract remain the blockers. Aggregate descriptor construction must also be
charged once, rather than silently reparsed from an unbounded ancestor list.

## Credit and license

PR2457 supplied the aggregate-before-padding reduction and explicit scan
handoff, building on commdata2338's PR2399, Jose Manuel's PR2234 and Adam Gall's
PR2087. The retained supplier, descriptor and parking lineage keeps its
attribution. Binary countdown amortization is elementary prior technique;
the contribution is its complete source-bound scan/cleanup implementation.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0;
no independent human review or full supplier replay claimed.

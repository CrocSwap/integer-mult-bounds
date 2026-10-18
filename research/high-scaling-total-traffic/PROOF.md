# Exact high-scaling logical tape invoice

Nick Petalas. Apache-2.0.

## Statement and boundary

For odd `Q>=3`, positive integers `B,S`, and `V=BQS`, the literal
`kernels.doubled` introduced by Jose Manuel/jmbarrancoml in PR2915 has the
same exact logical tape traffic in either direction. On canonical input
encodings that traffic is less than `1024 V`. This is a source-level
successful-call theorem, not an inference from the finite tests.

The source is the complete Boolean stream `[B][Q][S]`. Its LEFT is at zero
and its head is at one. The supplied before/suffix Counts encode their
positive values without leading zeros. The borrowed modulus Word has
`L=bit_length(Q)+1` digits, with one leading zero margin, and head one.
The literal Ring constructor enforces that modulus convention. All three
payload factories return distinct fresh literal Tapes. Every other Tape
construction in the invoked code is also literal and fresh.

Traffic is the sum of all Tape and Word reads, writes and unit head moves,
from function entry through successful return including its `finally`.
It includes Count construction, validation, normalization, division,
increment, all countdowns, copies, rewinds and erasure. Initial construction
of the borrowed objects and eventual disposal of the returned output are
excluded. The returned output remains owned, distinct and rewound; source,
extents and modulus are restored. Private cardinality and bucket tapes
are erased and rewound.

Python allocation, initial LEFT creation, fixed-role placement, allocator
bookkeeping and observer operations are outside this logical metric.
Factory traffic is not implicitly free in a different implementation.
A separate exact construction count below supplies an additive interface
for a bounded-cost allocator. This theorem does not price a complete
physical caller, the other high-field operations or B1 calls.

## Retained countdown and suffix costs

Write `d(n)=bit_length(n)` for positive n. Arham Tahir's PR2877 proves the
fully drained Counter cost, including its source reads, constructor and close:

```
C(n,d) = 15n + 14d - 5 popcount(n) + 36   for n>0,
C(0,d) = 14d + 40.
```

We use that identity and independently check it against these exact shared
source bytes. The countdown formula is predecessor credit, not a new result.
For canonical positive Counts, `C(n,d(n))<=65n` follows from `d(n)<=n`.

Each `copy_bits` probes `one_bit_suffix` once. With an unpadded Count its
probe cost is

```
p(S) = 4                         if S is even,
       15                        if S>1 and S=1 mod 4,
       12                        otherwise.
```

For S=1 no suffix Counter is constructed; otherwise a complete
`C(S,d(S))` follows. The S=1 probe here costs 12, not PR2877's 15 for a
one-high-zero marginal. The encoding distinction matters for the exact bill.
Each copied payload bit costs five operations: source read and step, plus
the destination append's read, write and step.

## New exact composition

Set

```
H=(Q-1)/2, E=H+1, l=d(Q), h=d(H)=l-1, e=d(E),
t=v_2(E),
U=43l+5e+5t+92+3*[t=h].
```

In either direction the complete traffic is

```
T = 20+[B even]+[S even]                    validation
    +U                                     Count setup and cleanup
    +23V+32                                payload and bucket cleanup
    +2 C(B,d(B))                           outer countdowns
    +B [2 C(H,h)+C(E,e)]                    row countdowns
    +2BQ [p(S)+[S>1] C(S,d(S))].            suffix operations
```

Brackets denote integer indicators. No numerical operand is decoded by the
routine. These integers describe the trace for the proof and external checker.

### Validation and setup

For a positive canonical Count n, its `zero` check costs `10+[n even]`:
two rewinds, the low-bit test, one step and the short-circuited RIGHT test.
These two calls supply the first line.

A positive Natural copy with d source digits and k significant digits costs
`18d-4k+20`. The source loop costs `6d`, normalization trims `d-k` zeros,
and the literal rewinds and delimiter operations give the remaining terms.
Consequently copying Q from its padded Word costs `14l+38`. Directly counting
`divide_small(2)` on this odd l-digit Q gives `10l+19`: its scan writes all
l quotient digits and normalization removes the single high zero. Copying H
then costs `14h+20`.

Incrementing H costs `5t+10+3*[t=h]`. Exactly t trailing ones change to zero;
the all-ones branch writes a new high digit and delimiter. Closing the two
Counts costs `5h+12` and `5e+12`. Summing these contributions gives U.
If an isolated callable instead receives an L-digit modulus Word, with
`L>=l`, the exact setup changes by `18*(L-l-1)`. This wider interface is
useful for a premise control but is not admitted by the canonical Ring.

### Copies, counters and rewinds

One pass splits the source into the E- and H-slice buckets. The other pass
merges them. One pass alternates pairs H times, then copies the final E
slice; the other performs E and H contiguous copies. Reversing direction
only exchanges the order of those two traversals.

There are exactly `2BQ` calls to `copy_bits`, one H countdown per prefix in
the alternating pass, and one E plus one H countdown per prefix in the
contiguous pass. Each pass has one B countdown. Every countdown drains fully.
This proves the final three lines of the formula, equally in both directions.

There are 2V copied bits, costing 10V. The source rewinds cost `2V+6`, the
post-split bucket rewinds `2V+6`, the output rewind `2V+3`, and clearing the
two consumed buckets `7V+14`. Source/bucket completeness tests cost three.
Their sum is `23V+32`. Closing the Counts was already charged in U.
No source is cleared and no returned output disposal is silently included.

The split/merge order also proves the inherited endpoint. Doubling maps
`(b,x,s)` to `(b,2x mod Q,s)`; reversing the passes gives multiplication by
`2^-1 mod Q`. Both preserve prefix and within-slice order. The algorithm and
endpoint belong to PR2915; the independently derived complete bill is new.

## Uniform bound and construction interface

For canonical encodings, the six formula lines are bounded respectively by
`8V`, `80V`, `34V`, `44V`, `98V`, and `160V`. In detail:

- Validation is at most 22 and V>=3.
- `U<=43Q+5E+5H+95=48Q+95<=80Q<=80V`.
- `23V+32<=34V`.
- `2C(B,d(B))<=130B<=44V`.
- `B[2C(H,h)+C(E,e)]<=65B(2H+E)<98V`.
- The suffix probes cost at most 30V; suffix countdowns at most 130V.

Thus `T<=524V<1024V`. This is a conservative bound, not an optimal constant.
It holds for every odd Q>=3, not only prime powers.

Exactly

```
A=7+3B+2BQ*[S>1]
```

private Tape constructions occur. There are two Counts, three payload tapes,
two outer countdowns, 3B row countdowns and the indicated suffix countdowns.
If an allocator preserves the literal operation semantics and adds at most
a fixed a traffic units per construction, the complete interval is bounded
by `T+aA`. This is a conditional accounting interface, not a proof that an
arbitrary supplied factory or physical placement meets that contract. For
example, A<=6V, so one marker-read per construction still fits below 1024V.

## Failure controls and evidence limits

The unchanged Q=65, B=2, S=1 call costs 10,354 operations. A deliberately
inflated implementation constructs and immediately closes a padded zero
Counter at every copy call. It preserves the full origin permutation and
borrowed state but costs 49,874. The exact difference is
`2BQ*C(0,8)=39,520`. More generally this mutation adds a log Q factor per
copied slice. An endpoint test alone therefore cannot certify linear time.
This is not a production bug; the unchanged implementation passes the bill.

An isolated padded-Q=3 call with L=4096 costs 74,392, exceeding 1024V. The
actual Ring constructor rejects that padding. Omitting the width premise
would make the universal claim false, not invalidate the canonical routine.

The checker compiles authenticated complete core modules and the unmodified
AST FunctionDef nodes for `copy_rows` and `doubled`. It does not execute the
unused route/stage imports, nor substitute a reimplementation of those loops.
Named bindings are explicit in source.py. This is a local source-slice audit,
not execution of the whole PR2915 loader, ScratchPool, high route or caller.
All executed external bytes and the tested export manifest are pinned and
registered as live inputs. Source and typed-receipt corruptions fail the CLI.

The 390 complete calls cover 152,352 payload origins in both directions.
Forty-five countdown cases check the retained identity at power boundaries
and padding widths. Wrong-direction and omitted-cleanup mutants fail, and
malformed streams reject. Those finite checks corroborate the written
all-parameter source proof; they are not the proof's quantifier.

Failure-path complete cleanup, concurrent callers, physical movement, complete
route setup/teardown, other ordinary operations, supplier admission and the
multiplication exponent remain outside this result.

## Engineering constraints

New fixture loops have explicit bounds: Q<=129, B,S<=100, volume<=25,000,
Word width<=4096, and each authenticated source<=1 MiB with at most twenty
inputs. The registered commands have 60-second timeouts. Historical runtime
loops are unchanged; the proof uses their positive countdowns and finite
encoded lengths. There is no recursive new runtime path.

Python requires managed allocation, a Power-of-Ten rule 3 deviation. The
fixture bounds limit live observer memory; the recorder intentionally retains
all observed Tape objects and is not a storage measurement. Rules 8 and 9
also require a bounded exception for authenticated compile/exec, AST function
selection and the observation subclass. Targets are the seven named core
modules and two named literal functions; acceptance never executes cached
predecessor bytecode. Tests mutate only private in-memory source trees or
private exports, and subprocesses have 30-second limits. Reassess these
controls before enlarging the domain or changing the loaded functions.

Strict lint, warnings-as-errors and normal/optimized replays are the Python
diagnostics used here. A proof-assistant kernel, independent human reviewer
and separate subagent review are not claimed.

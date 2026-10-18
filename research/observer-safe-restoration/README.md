# Observer-safe deferred dirty restoration

**Recursive-interface research construction and correction; no new kappa.**
Adam Gall (@adamgall), with substantial OpenAI Codex assistance in the research,
proof, implementation, verification and writing. New material is Apache-2.0.

## Result and provenance

[PR1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155), Aaron Wang
(@navinor), proposes replacing per-child workspace restoration by one final
composed restoration. Its frozen README says this preserves final observables
“if and only if no child reads the workspace's intermediate value” and that
“one reader child breaks it”. Its exhibited bad reader is a valid counterexample
to *unrestricted* deferral, but cannot establish that necessity statement.

This package gives the exact replacement criterion, a strictly larger constructive
class with nonzero readers, and the distinction between terminal and prefix
observations. It does not dispute PR1155's read-free examples or claim priority
for restoration coalescing. Its finite census is new evidence, not a finite
replay presented as an all-size proof. The proof below supplies the all-size
statement in the specified linear model.

Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. PR1155 source head:
`9821c6e9388f3fc097e94b72be9fa7b41a849527`. The complete source README is
preserved byte-for-byte under `context/`, with attribution intact; `SOURCES.json`
pins it, the license and the base selected record. No predecessor verifier is
imported. The actual selected base result is PR1094, conditional
`kappa = 836330098538459/500000000000000000`, not an open PR headline. Its
[review](../../docs/research/community-batch1099-review.md) and actual
`research/complex-t16-rare-pattern-exchanges/README.md` were followed from the
selected certificate. This package does not modify that construction.

Seed **52**, derived from fresh OS uint32 `3718171852` modulo 100. The seed picks
the recursive-interface track and the concrete odd arity `2 + (52 mod 7) = 5`.
`CLAIM.json` records the three candidates and overlap decisions. No pinned sprint
issue exists; the only open issues at claiming were #913 and #650, neither a
coordination issue. Scope was claimed locally before implementation and reserved
with the parent of the five independent rounds. Prior PRs #1114 and #1098 are
not reused as these rounds' deliverables.

## Exact criterion

Work over any field. Let data be `D in F^d`, borrowed workspace `W in F^w`, and
fixed child `i` perform

```
D <- D + B_i W       (reads the pre-child workspace)
W <- G_i W          (G_i invertible)
```

Read-only external-source increments may be added to both versions and cancel.
The children do not choose later matrices from intermediate data. Eager execution
applies `G_i^{-1}` after every child. Deferred execution applies only
`P_r^{-1}` at the end, where `P_0=I` and `P_i=G_i ... G_1`.

**Terminal theorem.** The two programs agree on final `(D,W)` for every arbitrary
dirty input exactly when

```
Delta_r = sum_{i=1}^r B_i (P_{i-1} - I) = 0.
```

**Proof.** Before child `i`, eager workspace is `W_0`, and deferred workspace is
`P_{i-1} W_0`. Summing the respective data increments gives difference
`Delta_r W_0`. Both restore workspace to `W_0`. Equality on every `W_0` is
equivalent to the displayed matrix vanishing (test the basis columns). This is
an all-size algebraic proof, not an inference from the census.

**Prefix theorem.** If data may be observed after every child, agreement requires
and is equivalent to `Delta_j=0` for every `j`. Subtracting consecutive equations
makes this equivalent to `B_i(P_{i-1}-I)=0` for each `i`. It does *not* require
`B_i=0`. These observations exclude the intentionally drifting workspace itself.
If that workspace must be observed in its entry coordinates, it must be restored
at that observation boundary. If a later control depends on data, use the prefix
criterion; terminal cancellation alone is not an admissible adaptive rewrite.

### Two strict counterexamples to read-free necessity

Let `G_i = [[1,1],[0,1]]` for three children and write workspace `(a,b)`.

1. `B_i=(0,1)` for every child. Each child reads nonzero dirty data `b`, yet
   drift changes only `a`. Every data prefix agrees; both final programs return
   `(D+3b,a,b)`. Final restoration is `a <- a-3b`.
2. `B_1=(0,0), B_2=(2,0), B_3=(-1,0)`. Child 2 genuinely reads the changed
   value `a+b`; child 3 reads `a+2b`. Deferred data increment is
   `2(a+b)-(a+2b)=a`, equal to eager `2a-a=a`. The intermediate data difference
   after child 2 is `2b`, so this batch is terminal-safe but not prefix-safe.

The second example directly addresses observable reads of the changing component,
not just a reader that happens to avoid it.

## Constructive family and fully paid local invoice

For a square-zero drift `U=uv^T` with `v^T u=0`, take `G_i=I+alpha_i U`.
Then `P_i=I+(sum_{k<=i}alpha_k)U`, and its inverse subtracts that coefficient.
Every `B_i` with `B_i u=0` is prefix-safe, even if nonzero. This supplies a family
at arbitrary dimension and arity. Its cheap implementation below uses coordinate
`u=e_a,v=e_b`, rather than pretending a dense outer product costs one primitive.

There are three length-`N` streams `D,a,b`. The concrete child shell is
`D += b; a += alpha_i b`, with each `alpha_i` equal to `+1` or `-1`.
Every source access is retained; no clean copy of `a` or `b` is required.
Eager additionally executes `a -= alpha_i b` after each shell. Deferred executes
`a -= S b` once, where `S=sum alpha_i`, skipping it only when `S=0`.

Count a signed ADD as one scalar primitive and a nonunit constant multiplication
as one additional primitive; this is an exact-arithmetic accounting convention,
not the selected complex real-primitive backend. Let `h=[S!=0]` and
`m=[abs(S)>1]`. At one node the complete shell invoice is:

| Work | Eager | Deferred |
|---|---:|---:|
| nonzero-reader ADDs | rN | rN |
| forward workspace ADDs | rN | rN |
| restoration ADDs | rN | hN |
| nonunit constant MULs | 0 | mN |
| total scalar primitives | 3rN | (2r+h+m)N |

Each ADD reads two data scalars and writes one; each extra multiplication reads
one scalar and writes one reusable scalar temporary. Thus reads are
`2*ADD+MUL`, writes `ADD+MUL`, and peak allocated data is `3N+m` scalars (the
extra scalar may be reused across all nodes). Constants and event descriptors are
read-only program data. For the frozen family they are compile-time constants;
constructing a general coefficient sum costs `r-1` descriptor additions once per
node specification, not an uncharged data pass. Forward shears, output updates,
final restoration, accesses and any temporary are all included. There are no
frame changes, initialized auxiliary streams, source copies, or omitted inverse
recursive calls in this explicitly specified program.

All-positive coefficients give `S=r`, so the priced saving is `(r-2)N`, not
`(r-1)N`: the multiplication by `r` is paid. The seed-selected odd-five family
`(1,-1,1,-1,1)` gives `S=1`, so every command is an ADD: **15N -> 11N**, a saving
of **4N**. Scratch really drifts at children 2 and 4, while each reader still
sees the invariant stream. This is not merely omitting an identity restoration.

## Complete recursion and precision boundary

To make the child term explicit, `emit` constructs an actual recursive program.
At depth `d>0`, split each stream into `r` disjoint equal partitions. For each
child `i`, first invoke the depth-`d-1` source-restoring program on partition `i`
with its arbitrary current dirty `a`, then execute that child's full-`N` shell
above. Eager restores after each shell, deferred only at node exit. A leaf is
the identity and has zero cost. Children can run with drifted `a` because every
data read depends only on invariant `b`; by induction all children restore their
entry workspace. Each position receives `r*d` additions of its own `b`.

For `N=r^d`, the full recurrences, including all recursive work, are

```
E_0(N)=F_0(N)=0
E_d(N)=r E_{d-1}(N/r) + 3rN
F_d(N)=r F_{d-1}(N/r) + (2r+h+m)N
E_d(N)=3rNd; F_d(N)=(2r+h+m)Nd.
```

These equations count scalar arithmetic, not free machine dispatch. There are
`J=(r^d-1)/(r-1)` internal nodes, `rJ` recursive child invocations, and respectively
`3rJ` or `(2r+h)J` stream events. Charging `C_call` per recursive invocation,
`C_event` per event and `C_step` per scalar loop iteration adds exactly
`rJ*C_call + events*C_event + ADD*C_step` in this abstract controller model,
plus the separately tabulated data reads/writes. An event's five immutable
descriptor fields can be charged five descriptor reads within `C_event`.
Routing is an ordered contiguous scan of the named partition, not a free
permutation. A streaming recursive realization keeps an `O(d)` index stack
and the fixed `r` coefficients besides the stated data; it need not materialize
the word. The verifier deliberately materializes the complete event list
(`5*events` descriptor scalars) for independent reversal and replay. Neither
its Python memory use nor its runtime is claimed to attain the streaming
resource bound. All extra controller terms and the reader/scratch work remain;
only the displayed restoration events disappear.

The inverse program reverses all events and negates coefficients, without new
storage; its scalar invoice is identical. `verify.py` replays both directions
on every basis column of all three dirty streams for depths 0..3 and arities 3
and 5. The zero-cost identity leaf is part of this completely implemented
restoration experiment, not a placeholder for a promised supplier. A real leaf
backend of cost `L` would add `r^d L` to *both* recurrences and must independently
satisfy this reader/restoration contract.

For integer inputs of magnitude at most `M`, unit shells along a depth-`d` path
keep both data and scratch magnitudes at most `(1+rd)M`; the temporary for a
nonunit restoration is at most `rM`. Consequently adding
`ceil(log2(1+rd))` magnitude bits (plus a sign bit under an unsigned-magnitude
convention) suffices in this integer model. The code uses unbounded exact Python
integers and Fractions. No fixed-tape implementation, rounded complex arithmetic
contract, native compiler, or supplier precision admission is claimed. This
boundary is distinct from the rounded-leaf obstruction in PR1135 and modular
borrowing in PR1159; it does not evade those results.

## Reproduction, domain and controls

From the repository root, Python 3.10+, standard library only:

```sh
python3 -I -O -B research/observer-safe-restoration/verify.py
```

The command authenticates the pinned source/context bytes, recomputes every
certificate field and compares `EXPECTED.json`. It never writes by default.
`--write NEW_PATH` creates a fresh certificate and refuses to overwrite one.
No randomized search or tolerance acceptance is used.

For one complete relocated replay followed by an actual source-corruption
subprocess rejection (without repeating the expensive census for the corrupt
source), run:

```sh
python3 -I -O -B research/observer-safe-restoration/test_package.py
```

Its final marker is
`PASS_OBSERVER_RESTORATION_PACKAGE relocation=1 source_corruption=1`.

The bounded census is all **46,656** three-child tuples: each `G_i` is one of
four integral shears `I +/- E_12`, `I +/- E_21`; each row reader is one of the nine
vectors in `{-1,0,1}^2`. Full 3-by-3 state-operator composition is compared with
the separately computed two-dimensional defect. The signed coefficient domain,
three-child stopping rule and complete coverage are fixed before execution.
This census is not an impossibility theorem outside its domain. A noncommuting
rational fixture additionally checks the formula with genuine denominators.

The completed census finds **7,776 terminal-safe** tuples, of which **6,048**
are prefix-safe and **1,728** are terminal-only. **7,712** terminal-safe tuples
contain a nonzero reader. Recursive forward/inverse replay covers **588**
dirty-state basis columns across eight `(arity,depth)` instances. At arity five,
depth three and `N=125`, the complete emitted scalar invoice is **5,625 -> 4,125
ADDs** (zero constant multiplications), saving 1,500 ADDs with the same 375 dirty
data scalars. These are emitted-program counts, not a runtime measurement.

Six meaningful controls require failure: a reader outside the drift annihilator,
observing an unsafe prefix of a terminal-cancelling batch, wrong inverse order
for noncommuting shears, omitted final restoration, changing a shear direction,
and a defect hidden by testing only zero-initialized dirty helpers. These are
mathematical counterexamples, not failed searches. The exact receipt records
classification counts, all recursive invoices and the explicit rational defect.

Only this isolated package's checks are relevant. No selected cold replay,
repository-wide `make verify`, remote CI or proof-assistant build is claimed.
The universal theorem is the written argument above; finite tests check the
implementations and exhibited failures. Selected all-size/compiler,
common-label/mutable-source, hosting, precision/tape, analytic and bit H1-H5
assumptions remain untouched. No new multiplication exponent or admitted paid
supplier profile follows from saving these boundary primitives.

## Related work and credit

Aaron Wang / Navinor's PR1155 is the direct predecessor and supplies the model,
coalescing direction and source text corrected here. Its own credits to Chafik
Boukhalfa's dirty-connector work, Gareth Davidson, Ross Richardson, Douglas
Colkitt and the retained complex batching recurrence are preserved in the frozen
README. PR1012 and PR974 price restoration at hosted-assembly level; this package
changes the operator admissibility class, not their rank-mass conclusion.
PR1057/1164 concern borrowed-port echo allocation, and PR1135/1159 concern exact
versus rounded/modular contracts; none is a dependency of this implementation.
PR889 (`e2021d1c9e06948528cbc0a8fd7079b671da981d`) batches common-factor
product shears with a query-minimal one-connector word. It does not supply this
observer defect criterion. PR1105 (`20a960b545f4b0ade4f26922ef686bd5eaf275f4`)
audits projected cleanup with target feedback in PR543; our children have no
data-to-workspace feedback and use full inverse workspace restoration. These
nearby algebraic interfaces are distinct and their negative conclusions are
not reopened.
Substantial OpenAI Codex assistance is disclosed above; no independent human or
formal review is asserted. The repository Apache-2.0 license is retained locally.

# P104 needs 96 added transports even with new workspace lifetimes

**Scoped obstruction, no new supplier or kappa.** Retain the native P104
channel's original transport occurrences, but grant arbitrary additional
source-independent workspace, arbitrary common-frame linear operations,
and arbitrary valid retiming. Identity transfer on its 104 arrays still
requires **at least 96 additional whole-array transports**. In the nested
positive-rank transport model, their added rank mass is at least 96.

The new premise is **additional storage lifetimes**. Jeremy Diviney's
[PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113), head
`fa1a45f91c14bb4b372d19dd7d66e11fea480ef5`, gives the predecessor cut while
retaining existing lifetimes and per-role frame paths. Here every occurrence
of a canonical frame is identified, even across different lifetimes of the
same role. This stronger static cut also gives a count for added transports
that remain live across arbitrarily many original events. It extends the
no-new-storage, local-excursion floor in David Arias's
[PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082).

**Added rank mass is not automatically excess recursive cost.** A new helper
may also contribute productive entrance-to-exit frame progress. The result
therefore does not rule out every changed helper inventory, replacement
producer or coverage law. The conditional moment comparison below explicitly
retains the old coverage requirement.

## Exact finite object and certificate

The input is Rohan Arun's PR1972 4,058-event witness, retained by Chafik
Boukhalfa's PR1991 native realization, at
`research/p104-native-channel/inputs/LOWRANK-WITNESS.json` (SHA256
`0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`).
It has 104 X sources, 104 Y targets, 72 independent dirty helpers and eight
owned C lifetimes. The immutable scientific base is
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.

Make one graph vertex for each distinct binary subspace of F2^9 appearing
as a frame. Forget register identity, chronology and storage lifetime. Keep
every transport as a directed edge except the eight C descents at original
zero-based event indices

```
2463, 2472, 2479, 2487, 2495, 2503, 2510, 2518.
```

These are the same eight edges identified by the temporal and retiming
predecessors. Identifying all frame occurrences is a further relaxation:
free same-frame storage may retain information across any original events.
The exact certificate is:

| Quantity | Value |
|---|---:|
| Distinct canonical frames | 444 |
| Retained transport occurrences / distinct arrows | 1,402 / 732 |
| Frames reachable from the 104 source entrances, R | 222 |
| Frames from which a target exit is reachable, T | 222 |
| Intersection / unclassified original frames | 0 / 0 |
| Retained R-to-T transports | 0 |
| Deleted R-to-T descents | 8 |
| Targets reached after restoring any one deleted descent | 52 |
| Targets reached after restoring all eight | 104 |

The two sets partition all original frames. This partition is unique among
binary potentials fixed to one at every source entrance, zero at every
target exit, and nondecreasing along retained arrows: forward reachability
forces R to one; reverse reachability forces T to zero. The executable
receipt stores every frame as a canonical reduced basis. For the theorem,
all frames absent from this finite graph are assigned outside R as well.
Thus the argument also covers newly introduced intermediate frames.

## Admitted extension model

Fix a positive finite array dimension d over a characteristic-zero field.
Every array has dimension d. Rational or Gaussian-rational arithmetic is a
favorable relaxation of Gaussian-dyadic arithmetic. Every original source,
target and dirty input is independently arbitrary. The desired endpoint is
`y_t <- y_t + x_t` in the original target chart; prescribed source and dirty
restoration remain required. Fixed invertible intrinsic endpoint adapters
do not change the rank argument.

Retain the original 1,410 transport occurrences, each used once. Original
scalar operations can be discarded and resynthesized; original transports
can be retimed in any valid chronology. The proof does not use their
per-register ordering, only the multiset of directed frame transitions.
Replacing, fusing, subdividing or reusing a transport changes this model
unless the new occurrences are charged separately.

Grant any finite number of added workspace lifetimes at any canonical frame.
Their initial values are zero or independently arbitrary dirt, never already
source-dependent. Grant arbitrary finite linear operations, including
singular maps, copies and address-coordinate mixing, among live arrays in
exactly the same canonical frame. Extra storage can persist across any
number of original events. Discarding it creates no information.

Every operation that moves source information between distinct canonical
frames must be a counted whole-array transport. The additional transports
are between distinct nested frames A and B, with paid rank
`abs(dim B - dim A) >= 1`. No free cross-chart relabeling, informative
initialization, increased array width, or access inside a recursive child
is allowed. Native child rank and array dimension are different quantities.

## Written all-program rank proof

Let c count the added transport occurrences from R to outside R, and k count
all added transport occurrences. Every admitted source-to-target block has

```
rank(X -> Y) <= (8+c)d <= (8+k)d.
```

Set all independent non-source entrance inputs to zero to extract this block.
This operation does not assume clean dirt in the circuit's required identity.
List the eight original and c added outward crossings in their actual
chronological order. Each delivers one value `z_i(x)` in F^d, a linear
function of the original source inputs even if it depends on earlier
crossings. Their concatenation defines a linear map Z with codomain
F^((8+c)d).

Replace each crossing output by its own formal z_i. No source entrance lies
outside R. New zero or independent-dirty initialization contributes no
source dependence. Same-frame operations stay on one side. Transports
within the outside set stay there; outside-to-R transports can export
information but can return it only through a later listed crossing.
Induction on the finite event order therefore expresses every final target
as a linear function of the z_i. The source-to-target block factors as LZ,
proving the rank bound. Feedback or repeated use of a stored value cannot
increase the dimension of the concatenated crossing values.

Identity on 104 arrays has rank 104d, so **c >= 96, k >= 96, and the added
paid rank mass is at least 96**. Each original rank-seven descent contributes
d, not 7d, of information capacity. An added high-rank child also carries
only one d-dimensional array. This is a necessary lower bound; no attaining
96-transport construction or minimum histogram is supplied.

The graph premise is a finite exact computation. The rank implication is a
written proof for all finite programs satisfying this model, not a finite
search over programs or a formal-kernel proof.

## Coverage boundary and conditional budget

The receipt includes a concrete nested path `0 -> P -> H -> FULL`, where P
is an actual source line and H an actual target hyperplane containing it.
P lies in R, H outside R, and FULL in R. The path's ranks are `1,7,1` and
sum to nine, exactly its entrance-to-exit dimension increase. If the caller
admits a newly borrowed helper entering at zero frame and leaving at FULL,
its crossing can be productive frame progress. This checked frame path is
**not** a complete chronological dirty-restored supplier. It identifies the
missing premise in any automatic excess-cost inference.

For comparison with the **conditional** nine-stage coverage model of
PR2082/2083, assume `m=73, W=832, N=9`, unchanged ordinary idle mass, and
**no new creditable persistent endpoint progress from the added transports**.
The exact inherited local mass is 2368: 2312 persistent endpoint progress
plus COPY56. Under these separate accounting assumptions,

```
old required idle mass = 72*832 - 9*2312 = 39096
completed mass >= 9*(2368+96) + 39096 = 61272
capacity = 73*832 = 60736
M(0) >= 7659/7592 > 1.
```

For `0 <= a < 1` and `0 < r <= m`, `(r/m)^(1-a) >= r/m`, so this
retained-coverage extension fails the moment test throughout that range.
The arithmetic and value already occur in PR2082's narrower extension
model; the new contribution enlarges the storage/retiming quantifiers of
the transport-floor premise. New productive helper trajectories require
their own complete coverage calculation. No packing cap or new kappa is
claimed for such changed inventories.

## Reproduction and checked boundary

```
python3.12 -I -B research/p104-storage-cut/verify.py
python3.12 scripts/research_package.py --package research/p104-storage-cut
```

The default verifier is read-only and compares its freshly derived complete
receipt with fixed `RESULT.json`. `--write NEW_PATH` exclusively creates a
new receipt and refuses overwrite. It imports no predecessor executables
and needs no network or Git. The generic package metadata check needs Git
history for provenance; direct replay also works from a source export.

The primary checker uses reduced binary bases. A separately written oracle
uses complete XOR spans and independently validates the frame trace. They
compare every transport signature and both complete partition sets, not
just their counts. Controls restore each omitted descent, insert a new
FULL-to-target bypass, corrupt actual source/common frames and declared
rank, and remove the separation guard. Permuted and redundant frame
presentations are accepted. File-level controls cover missing/corrupt
inputs, wrong/missing receipts, exclusive output and normal/optimized
relocation. These checks are AI-assisted, not independent human review.

No fresh full 280-column scalar identity, native Clifford/phase replay,
chronological owner construction, precision bound, all-size lift, outer
assembly, selected cold replay or Lean proof is supplied. The native
channel is inherited; this result needs its authenticated frame transitions
and input/output dimensions, not a new proof of its G/2 identity.

## Open next questions

1. Replace actual producer/transport occurrences and test a new static cut,
   then prove arbitrary-input endpoints and the complete native bill.
   Discussion [2121](https://github.com/CrocSwap/integer-mult-bounds/discussions/2121)
   studies a changed joint-side producer; that replacement is outside this
   retained-occurrence theorem. No claim about its success follows here.
2. Realize one new monotone borrowed helper at legal chronological cuts,
   then derive its actual owner and coverage contribution. Frame-path
   feasibility alone does not justify displacement of old idle work.

The blockers and feasible first steps are also in `TASK.json`. More free
same-frame storage without changed transports cannot escape this cut.

## Credit and scope

Immediate cut predecessors are Jeremy Diviney/PR2113, David Arias/PR2082
and Adam Gall/PR2090. Adam Gall/PR2083 supplies terminal-cut and coverage
context. Rohan Arun/PR1972 supplies the channel; Chafik Boukhalfa/PR1991 its
native realization; Adam Gall/PR1940 its schedule. Retain Josie
Elliston/PR1071, Ali Romman/PR1125 and the PR968/717/446/595/620 geometry and
decoder lineage, plus Sagar Thakrar/PR1012 and Douglas Colkitt/PR1240 for
coverage context. Concurrent PR2089/Discussion2107 correction words are
separate constructions and are not claimed here. Exact inspected heads are
recorded in `SOURCES.json`; no predecessor code is copied or modified.

Prepared for Ross Richardson with substantial OpenAI Codex assistance in
mathematics, code, verification and prose, using the complex-supplier and
exact-circuit-verification specialists. Apache-2.0. No formal-kernel proof,
independent human review, literature-priority guarantee or selected-frontier
change is claimed.

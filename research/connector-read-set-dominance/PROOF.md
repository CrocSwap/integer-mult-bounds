# Continuation-safe read-set dominance

This contribution was produced by Nick Petalas. Apache-2.0.

The state model and its dirty-root semantics are those of ywz65's
[PR2538](https://github.com/CrocSwap/integer-mult-bounds/pull/2538), building
on conorholds's PR2208 and Ross Richardson's connector interface. Their
completeness argument is a cited premise. The new step is the dominance
simulation below and its bounded implementation. Shortest paths and
superset dominance are classical; no general literature priority is claimed.

## Interface and state

The field is F2. Sources x_j are immutable, the two roots start with arbitrary
dirty rows d_0,d_1, and each target y_m also starts arbitrarily dirty. The
opaque linear maps B_j and A_m need not commute and may be singular. All B
and A calls use physical root 0. A root shear C_p adds root 1-p to root p.
The desired endpoint adds A_m(sum_{j in m} B_j x_j) to each target and restores
both roots. Targets are never read and have no intermediate deadlines. Each
complete child call must restore its own scratch and heads.

Fix a source word with each label occurring twice and a nonzero color
v_j in F2^2 for each source. At cut t let Q_t be the two normalized source
coefficient rows. A frame G in GL2(F2) represents physical roots
G(d + Q_t X), where X_j = B_j x_j. Its first row a exposes the read vector
(a,a Q_t) in F2^(n+2). A source event j is legal precisely when G v_j = e_0.

A graph state is (t,G,S), with S the set of all exposed read vectors on the
path so far. A B edge advances t at fixed common source price, represented
as zero in the transfer objective. Either C edge costs one and changes G.
Both edge types add the newly current read vector to S. Edges depend on
t,G and the fixed instance, never on S. The initial state is the identity
frame at cut zero, with its current vector included in S.

Let V be the complete set of possible read vectors at all cuts and frames.
For each target m let d_m be the shortest XOR decomposition length of (0,m)
over V. The predecessor establishes simultaneous attainability of these
individual minima. Thus a terminal state is accepted when t is the final
cut, G=I, and every target has a length-d_m decomposition over S. This is
the fixed minimum-read objective; it does not optimize read/transfer tradeoffs.

## Dominance theorem

Suppose two reached states have the same t,G and respective labels (S,c)
and (T,b), where c and b are transfer costs. If S contains T and c <= b,
the first label can replace the second for every continuation.

Proof. Take any continuation from (t,G,T). Starting from (t,G,S), repeat
exactly the same B and C operations. Every operation is legal because
legality depends only on t,G. The future cuts and frames therefore agree.
After every step the first availability set still contains the second,
since both sets are united with the same newly exposed vector. The first
total transfer cost remains no larger. If the second state eventually
accepts, its target decompositions remain available in the first. Their
lengths cannot be smaller than d_m, since both availability sets are subsets
of V. Consequently the first state also accepts with the minimum read bill.
This proves the assertion for every finite continuation, without a length
bound. The converse is unnecessary. QED.

The proof uses historical availability rather than simultaneous stored
copies. Once the path is chosen, reads can be emitted at the first visit to
their vectors. Targets are independent and unread, so these insertions do
not affect any B or C operation. No extra physical storage or free child
call is inferred from this search representation.

## Incremental pruning and a finite certificate

At each fixed cut/frame, retain labels that are undominated in the joint
order of greater availability and lower cost. Reject a dominated offer.
When a new label dominates retained labels, retire those labels from the
expansion queue. Parent records remain available for witness reconstruction.
Equal sets and equal costs retain one copy. Superset inclusion alone is
insufficient when the superset costs more.

For a finite transfer budget K, explore every unretired queue entry with
cost at most K. Every label in the unpruned graph has a reached dominating
label in the pruned graph. Induct on an unpruned path: start at the shared
initial state, simulate its next edge from a dominating label, then replace
the offered label by any retained dominator. Dominance is transitive, and
costs never increase under replacement. Finite retirement chains therefore
preserve a retained representative. This proves acceptance equivalence up
to K, and hence exact minimum transfer cost whenever an accepting bound is
found. The algorithm reports resource exhaustion as an error, not an optimum.

The certificate checks more than agreement of the two minima. It enumerates
the complete unpruned graph through six transfers, computes its undominated
frontier afterward with a separate pairwise subset test, and compares every
retained label against the incremental result. It also finds a retained
dominator for every unpruned state, with matching cut/frame and no greater
cost. All these are explicit finite checks.

The fixture is source word (0,0,1,1,2,2), colors (1,2,3), and all seven
nonzero target masks. Its global minimum read bill is 15. Both complete
searches find minimum transfer cost six; the pruned five-transfer graph has
no accepting state. The emitted 27-operation program contains six B calls,
15 A calls and six C calls. A separate free-algebra interpreter proves its
arbitrary-input endpoint and literal inverse without identifying A_m B_j
with B_j A_m. This certificate concerns this one fixed source/color instance.

## Termination and implementation limits

The implementation accepts one through six sources and transfer limits
0 through 24. There are at most 39 distinct read vectors and 256 XOR-space
vertices. For every source instance the graph is finite. The implementation
additionally caps discovered labels at 250,000. An individual state's best
integer cost decreases at most K+1 times, so at most cap*(K+1) queue entries
are created. The explicit queue-pop bound includes one extra iteration to
observe an empty queue. Witness reconstruction uses at most one iteration
per stored parent plus one. Resource limits fail closed.

The code has no recursion, dynamic imports or generated code. Python's
managed allocation is a deviation from fixed preallocated memory. Live
collections are bounded by the source, transfer and state caps; this is
not a measured peak-byte guarantee. The certificate uses a quadratic
postprocessing oracle only on its fixed small graph. It imposes no runtime
performance threshold and claims no timing speedup.

## Scope

This answers the same-cut/frame dominance part of PR2538's open next
question. It supplies neither a practical n9/n12 solver nor those instances'
optima. No predecessor executable or published fixture is replayed. No
weighted read/transfer envelope, recursive caller, native price, hosting,
precision, tape, supplier admission, new kappa or selected-frontier change
follows. The five selected framework assumptions keep their prior status.
Independent human and formal proof-kernel review are unclaimed.

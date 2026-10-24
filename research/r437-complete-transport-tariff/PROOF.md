# Completed source transport, with explicit retained backing

This is a scoped upper bound for the original `selection.packet_operation`,
`routes.route_packet/route_cube`, and `Machine.dispatch` gather/return branches.
It is not a bound for preparing Context, a complete node, or an admitted supplier.
The source is the unmodified caller retained at canonical81e9bd6. PR3980 supplies
its current-source owner separation and transport multiplicities; PR2569 supplies
routing semantics. Their results are credited, not re-proved by a small fixture.

## Contract and meaning of cost

Fix the original compiled odd-prime q, dimension1<=d<=64, LowCodes vocabulary of
L classes and compiled Route/inverse. The rational charts are invertible with
unit denominators modulo M=q^w. Let b be the original Word extent, including its
high zero margin; let t>=1 bound the bit lengths of every signed numerator,
denominator and q used as a compiled literal. Supply the actual validated Context,
its canonical modulus/cap/high Count, and enough numerical registers (R slots).
Set H=q^((w-1)d²), O>=1 old physical prefixes, and F>=1 bits per complete fibre.
O and F are canonical encoded Counts; neither is decoded by the algorithm.
The family has V=OLHF bits; a selected packet has P=OHF bits. The stage is a
distinct original physical role, initially containing at most P arbitrary bits.
All caller metadata and other roles are borrowed and distinct. No literal giant
fixture is claimed executed. The bound applies only to successful valid calls.

The completed interval is gather_route, a separately supplied completed map on
the entire P-bit stage, then route_scatter using the inverse chart, including both
Machine.commit calls and all scratch cleanup. Subtract the completed map's own
cost from this interval: it is not priced here. Its preservation/size contract
is a premise; arbitrary changes to the complete returned packet are permitted.

A tape action is exactly one source Word/Tape read, write or unit head move.
Arena/Lease observer meters must not be added to their backing-tape meters twice.
This is a physical cell-action tariff on the source's fixed tape inventory, not
wall-clock Python time. Finite compiled control (slot/tag/matrix labels, q-bounded
carry states) is as in the original machine. No runtime numerical host decoding
is used. Construction/encoding of that fixed control, LowCodes and the supplied
Context remains outside the contract. In particular this is not a single uniform
machine generating its own q-dependent codebook. If a consumer requires that
stronger setup theorem, it must supply and charge it separately. CPython dictionary
and module-patching operations are not declared physical tape operations: the
original ScratchPool.install is compilation/specialization to fixed slot labels.
The finite control can be expanded for each fixed q,d,R; no bound on its description
size, compiler time or common per-action finite-control constant is asserted.

## Explicit bound

Let k=d², u=b+2 and

    n=4+bitlen(O)+bitlen(F)+bitlen(L)+kb,
    K=k(b+1), D=H(K+F), A=q²+128.

Every cardinality Count used below has at most n binary digits. In particular
before/after<=LH, bucket counts<=H, and O,F,H are covered; multiplying a low
ordinal by q^(w-1) k times never exceeds LH. H's bit length is at most kb+1.
Intermediate cardinality construction uses the same bound, not an encoded
payload-sized register. K counts every high-key binary digit and WORD_END.

The following deliberately conservative bounds count all successful actions:

    G =4096(k+1)u³(n+t+2)
       +4096(O+1)(L+1)(H+1)(F+1)(n+2),
    Rte=16384(O+1)[(k+1)(t+u)u³
                  +(H+1)(d+1)³u²
                  +(kb+1)(H+1)(K+F+1)(n+2)],
    T =2G+2Rte+128(V+P+n+1)+8A.

G bounds one complete gather or scatter. Rte bounds one complete route_packet.
T bounds the entire declared two-branch transport interval, including complete
source/target rewinds, owner installation, role clearing and final pool.empty
checks, but excluding the supplied completed stage map. `bounds.py` implements
these integer formulas only; it does not control source execution.

Here is a source-loop derivation rather than an extrapolation from the fixture.
A canonical n-digit Counter initialization, one decrement, or close costs at
most32(n+2) actions, by counting its at-most-two full scans and its constant
read/write/move sites. A full bit copy has at most64(F+1)(n+2) actions, including
its Counter; a row copy has at most128(c+1)(F+1)(n+2) for c rows. Discarding costs
no more. append_tape, clear and rewind cost at most8(s+2) on s symbols. These
bounds include small/zero-count branches and the two delimiters.

A Word scan/zero/copy/free/compare/add/subtract/shift, with all Arena initialization
and returns, costs at most128u actions. Binary long division and Ring.multiply
perform at most b such rounds, with fewer than eight scans/allocations per round,
so each costs at most1024u². Euclid makes at most2b+2 divisions: every two
nonterminal remainders reduce the larger remainder by at least a factor two.
Including Bezout updates and disposal gives at most8192u³ for Ring.inverse.
A signed t-bit literal costs at most512(t+1)u; the chart palette and its d² output
copies therefore cost at most16384(k+1)(t+u)u³. The Rte bracket has prefactor16384 and O+1>O, so covers this
bound once for each of the O original-prefix route_cube executions.
The per-header raw_header, d-by-d product, exact q division, residue comparisons,
key output and odometer advance are at most8192(d+1)³u² actions. The same
O+1/H+1 margins cover that per-header bound inside Rte. Sparse zero/one branches
can only shorten these loops. All matrix entries remain source Word tapes.

For gather/scatter, two high_power constructions each make k radix traversals.
Each traversal has w<=b divisions, plus at most b fixed-q Count multiplications.
The latter scans at most n digits and appends at most bitlen(q)<=b carry digits.
Its carry is bounded by q and is a fixed compiled control state, never a runtime
unbounded integer. Bound these two constructions by2048(k+1)u³(n+t+2).
The remaining three row regions per O prefixes, output erasure on success,
Count disposals and validation scans fit the second summand of G; the first
summand's factor-two margin covers the source-initialization literals and scans.

For each route_cube, decoration has H complete keys and H fibres. Each stable
partition traverses exactly H decorated records, copies each key through its
private key buffer into a bucket and into output, copies each fibre into one
bucket and into output, increments a bounded bucket Count, traverses both bucket
Counts and erases both buckets. The full cost, including clearing the old current
stream after the partition, is at most2048(H+1)(K+F+1)(n+2). There are exactly kb
partitions when cap>1, and zero when cap=1: the cursor starts at1 and advances to
the bth padded Word bit for each of k coordinates. Final key validation/removal
and the outer copies fit two further passes at that same bound. Rte's factor
16384 and (kb+1) cover these, even when cap=1. The outer O loop copies complete
prefix bodies into/out of local roles, closes every Counter, and rewinds all
borrowed heads. Its O+1 factor supplies those boundary scans and initialization.
Finally each commit clears the old role, copies the whole result into that same
role, rewinds it, and ends the Lease. The128(V+P+n+1) margin covers both commits,
the selected/result finally blocks and the fixed borrowed Count wrappers.
Each of the two final pool.empty calls costs4A actions, hence the explicit8A.

These inequalities intentionally overcharge shared scans. They show a finite
constructive cell-action upper bound, not an optimized tariff or asymptotic
advantage over the original algorithm. Keeping G and Rte symbolic at the outer
caller remains appropriate until its source parameters and all other components
have been joined; no moment or reserve admission follows from these large bounds.

## Fixed physical backing and ownership

The actual Machine.run executes dispatch under ScratchPool.install. That adapter
replaces source-global Tape names AND default factory arguments, and forbids new
physical Tape/Arena constructors. Thus the per-record `key=Tape()`, Count copies
and Counter bodies reuse A physical tapes. Merely passing a payload factory
would miss those sites. The verification must use the real installed pool.

A stack count gives at most32 simultaneous scratch leases for this interval:
two outer wrappers plus their selected/local/output roles (at most6), current
cube and returned output (2), partition buckets/counts/record Counter/output/key
(at most8), row/bit Counters (2), ordinal Count construction copies (4), and eight
spare leases for temporary initialization/normalization. These categories are an
overlapping overestimate, not an observed maximum. Numeric matrices use the
separate supplied Arena; require enough R for their successful execution rather
than silently raising its capacity. No lease crosses the supplied child boundary:
gather_route commits into the permanent stage and pool.empty succeeds first.

Every scratch body's extent is at most V+D+P+n+8: this covers whole family,
whole packet, one decorated cube, counters and key buffers. Erasing does NOT
shrink retained backing. Charge all A roles at their maximum, not only the current
live leases. The two touched permanent roles, metadata and delimiter slack are
covered by eight further roles at the same bound. Including the entire R-slot
numeric Arena and template gives

    B=(A+8)(V+D+P+n+8)+(R+1)(b+2).

B is a conservative bound for these touched/pre-reserved roles; every untouched
caller role and suspended parent is an additional entry resident. Arbitrarily
large backing retained by a role before entry must be added (or bounded by this
contract); clearing its short current body does not justify forgetting it.
The source never overwrites an unselected family packet, and chronological
scatter uses the current original family, not a stale snapshot. Borrowed Count,
modulus and low/source fields return with their documented heads. Successful
pool.empty checks complete role erasure; malformed-input rollback is outside this
success contract and is not inferred from these bounds.

## Evidence scope and next questions

The finite verifier executes complete reduced d1 and d2 high cubes through the
actual dispatch branches, including the installed pool, compares with an
independent coordinate oracle, and records physical backing/action totals.
It is not an actual GL64 R437 root, admitted parameter witness, or full caller.
A historical source projection supplies the exact original selected record
accepted by the frozen loader; it does not authenticate the current root entry.

Open next questions: bind these G/S/R formulas to a complete chronological
R437 node including every other component and parent entry resident; supply
and price original-root Context/LowCodes compilation; replace conservative bounds
only where an actual consumer budget needs sharper ones. No new kappa, selected
frontier change, formal-kernel proof or independent human acceptance is claimed.

Credit: Jose Manuel/jmbarrancoml's PR2569/2753/2809 and ScratchPool lineage;
Nick Petalas PR2989 compiler/owner audit; Chris R/Clear1nsight PR3980/3986;
ai-nanachi, zxv and retained R437/OQ4 contributors. Prepared by JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0; original notices are unchanged.

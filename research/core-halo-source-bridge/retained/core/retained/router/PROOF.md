# A physical whole sparse-union window

Prepared for @CubeJerry with substantial OpenAI assistance. **No new κ.**
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## 1. Proposition, premises, and the exact advance

Fix one complete delivered microbox with `g>=1` active coordinate axes and
common side `L>=2`. Its dense payload consists of `D=L^g` complex scalar pairs
in increasing lexicographic coordinate order. Each component is a signed,
little-endian, two's-complement `w`-bit word on the common `2^-P` grid. The
input and coefficient catalogue begin with the same **complete binary context
key**, followed by a fixed delimiter. The key contains the immutable Reference
identity and parameters, absolute source/window origins, admitted interior
partitions, the scalar grid/carrier and block choices, and the retained coarse
spectators. Its length is arbitrary and paid; it is not replaced by a hash.

For axis f let `E_f` be a strictly increasing exposed subset of `[0,L)`,
`a_f=|E_f|`, and let its ordered J mask have `n_f` ones. An empty E has empty J.
A nonempty E has `1<=n_f<=a_f`. The axis catalogue contains the encoded values
`a_f,n_f,b_f`, the E list, J mask and eight coefficient-page strings in exactly
the #6908 order. Every `b_f` is dyadic and at least two. All axes share w,P.
The catalogue is produced from the same immutable rational Reference as its
pages; §2 identifies the actual source producer and its cost.

The input is at the first sparse inverse-window boundary, after the preceding
dense interior stage. That earlier stage, any grid conversion and delivery of
this complete microbox remain caller obligations. On a nonempty complete E_f
line, the retained service implements its precise deterministic rounded version
of

\[
 T_f(u)_{J_f}=F_f^{-1}(u_{J_f}-C_{0,f}u_{I_f}),\qquad
 T_f(u)_{E_f\setminus J_f}=u_{E_f\setminus J_f}.
\]

The service, its current-input source relation, coefficient error, completed
rounding sites and numerical carrier bounds are **inherited from #6908**. The
new program neither substitutes a one-shot rounded shear nor changes a page
or seven-product instruction. Numerical validity retains that service's actual
input-radius, grid and source-admission hypotheses.

**Proposition.** Under these premises, `UnionRouter.run` is a fixed-tape encoded
implementation of every round, permutation, deletion, restoration and dense
return of this whole sparse window. It produces the same dense scalar words
as the full increasing-axis rounded schedule. It preserves the complete
context, restores the borrowed source/catalogue/descriptor bodies and origins,
and leaves one protected output. `consume` erases that output. All other owned
roles are erased, including previously used backing. The time and retained-space
bounds are those of §§7–8, with source preparation and numerical calls added.

The underlying combinatorial schedule and record-level head-travel proof are
#4100/#4327. The field layout is #4583. The rounded class chronology is already
proved in #6908, PROOF §7 and NUMERICS §4. Those are dependencies, not new lemmas
claimed here. This contribution closes their explicit **host scheduler and
header/rank emitter boundary**: no Python record array, tree dictionary, global
stream length, sorting primitive or host payload callback selects online work.
The same actual #6908 consumer is called through its encoded ABI.

The proposition is about delivered complete contexts. It supplies no global
coarse-coordinate gather, production page amortization, prior dense solver,
broad forward window, core/halo assembly, FFT/CRT recovery or complete integer
multiplier. All five selected #6030 assumptions remain retained.

## 2. Source generation and catalogue provenance

There are three separate constructions; none is identified with another for
free.

1. The immutable `Reference` generates exact rational entries in original
   coordinates. The pinned #6908 `source_window.make_window` validates the
   ordinary window, original periods/phases, disjoint admitted interiors and
   exact zero couplings. It computes J as the complete interior complement and
   computes E as J together with **every** original nonzero B0/C0 incident
   interior coordinate. It forms the exact original shear and Schur factors.
   Thus its E lists are generated from the same source as the coefficient pages.
2. `source_carve.partition` additionally executes the unchanged canonical
   `carve` and `Core.partition` bodies. They clip runs at holes and original
   phase changes and produce the retained dyadic interiors. Passing these
   interiors to the same `make_window` yields source-generated production-carve
   lists. The small expensive numerical fixtures instead retain their explicitly
   admitted partitions; they are not described as outputs of the conservative
   carve. Finite source checks distinguish these two cases.
3. The actual online code consumes the serialized E lists and builds flags and
   ordinals on tapes. It does not receive a host membership/rank function.
   `build_membership` merges each E list with the sequential range `[0,L)`,
   checks strict order, range and exact list cardinality, and writes one dense
   axis block. Cell x contains its membership bit and h-bit ordinal if present,
   or canonical zero if absent, where `h=ceil(log2 L)`.

The exact canonical and pending-PR bytes have Git-blob and SHA256 pins in the
manifests. The retained #6908 producer and numerical modules are unchanged.
The runtime adapter changes import search paths only. Exact `prepare_pages`
executes on the serialized exact factors in the source replay; an expected-page
observer is never substituted for physical preparation. `prepare_bank` then
copies those physical page strings into a single axis-ordered catalogue with
paid scans. No payload or RHS count enters source preparation.

The source key binds Reference parameters, absolute origin, partition and
page grid/block. Spectators affect headers/RHSs, not that axis's coefficients.
Different contexts are separate frames. Exact binary key comparison prevents
accidental local-coordinate aliasing between their frames; this is a typed
source-preparation contract, not a cryptographic proof that arbitrary supplied
coefficients obey their claimed key. The source producer establishes that
semantic relation. Global assembly must deliver its data with the correct key.

All source work remains billed. Use #6908 NUMERICS §5 with `u=2+L+b`, source
rational/coordinate height `h_src`, radius-description height `h_R`, and

\[
 H_{\rm rat}=O(u^8(h_{\rm src}+h_R+P+w+\log u+1)).
\]

Its sufficient sequential preparation bound is
`A_ref+O(u^8 H_rat^4+u^2 w)`, with exact matrix storage
`O(u^2 H_rat+C_ref)`. The carve scans at most L local coordinates/runs and uses
original-coordinate arithmetic, not constant-time dictionary access. A loose
additional sequential bound `O(L^3 (Xi+log L+1)^3)`, where Xi bounds the full
source-coordinate description length, covers its arithmetic, list simulation,
serialization and rewinds. This is dominated by the displayed setup envelope
when its declared source height includes Xi. Sum over distinct prepared keys;
charge duplicate catalogue copies separately. Historical source caches and
physical backing are retained unless their complete cleanup is paid.

No claim that this setup is negligible follows from the finite examples. The
online theorem below includes its own complete catalogue scans; the outer
caller must still fund the complete preparation/cache term.

## 3. Literal fields and the carrying catalogue cursor

The unchanged #4583 header is

\[
 01\;x_0\cdots x_{g-1}\;\chi_0\cdots\chi_{g-1}\;
 k_0\cdots k_{g-1}\;|F|\;f,
 \quad H=2+2gh+g+2t,\quad t=\lceil\log_2(g+1)\rceil.
\]

Coordinate and ordinal fields are h-bit big-endian. Counts/tags have t bits,
including the initial sentinel g. Payload words keep the inherited
little-endian scalar format. Internal canonical Count strings are separately
delimited little-endian integers; the parser rejects redundant high zeros.
The metadata check derives h and t on tapes, not from host integers.

`build_membership` makes one catalogue with g dense axis blocks. The active
odometer state has g fixed-width blocks `(coordinate,flag,ordinal)` on one
additional tape. Its current value describes exactly one grid point. A header
requires three sequential state scans: coordinates, flags/count, ordinals.
All counters used during these scans are bounded by polynomial expressions in
L,g,w,b. The g h-bit vector is never interpreted as one integer.

The membership head normally stands at the selected cell of the last axis.
A noncarry step advances it by one cell and increments only the last coordinate.
On a carry, the routine rewinds that axis to its first cell, resets its state,
walks to the preceding axis block, and reaches that preceding coordinate by a
short encoded cell count. Once an increment succeeds it walks forward across
the reset trailing blocks to the last axis's first cell. The state head returns
to its local end. A full carry ends enumeration. This visits all and only
`L^g` points in lexicographic order without ever constructing `L^g`.

For a carry through j trailing axes, extra catalogue travel is
`O(j L(h+2) poly(ell))`, including seeks from both ends. Such a carry occurs at
most `D/L^j` times, apart from the final carry. Since L>=2,
`sum_(j>=1) j/L^(j-1)` is bounded. Extra catalogue travel is therefore
`O(D(h+2) poly(ell)+gL(h+2) poly(ell))`. Header scans cost
`O(D H poly(ell))`. No O(L) seek is paid on a noncarry step. The root review
derived this amortization independently of the author proof.

The forming pass emits one indicator bit for every dense point. It copies the
header and current scalar pair into the union exactly when its flag count is
nonzero. Unselected values remain in the borrowed input. The final dense merge
enumerates the same odometer again and checks every returned marker, coordinate,
flag, ordinal and count against newly generated fields. The final working tag
is discarded. It copies updated union values at selected points and unchanged
borrowed values elsewhere, and checks all streams end together. The caller's
source body is never overwritten.

## 4. Tags, radix inversion, and local stacks without long counts

At zero-based round r, `Geometry.retag` scans the g flags, counts set flags in
a short Count, and writes the r-th flagged axis. It checks the stored flag
count. Python branch values are single bits or comparison outcomes; the axis
itself remains an encoded Count.

For each of t bits, stable LSD distribution scans the current stream, copies
complete records to the zero/one tapes, records their decision bits, and
concatenates the two tapes. No sort of a complete coordinate/spectator key
occurs. Each pass's decision bits are bounded by fixed delimiters on one stack
tape. Using t passes rather than only `ceil(log2 g)` may add one all-zero pass;
it preserves the same order and the claimed bound.

The inverse does not compute `N`, `N_0`, `kN`, or any global split offset.
It locates the last decision block by a backward scan to its start delimiter.
On its first forward scan, every zero bit copies one next record from the
sorted stream to Z. On its second forward scan, every one bit copies the next
record to O. Thus both prefixes have the correct sizes without counting either
size. On its third scan, original decisions interleave Z and O. Both record
streams must end exactly. The completed decision block is erased backward,
leaving the head at its former start: the previous stack-top append position.

This costs a fixed number of decision/record scans per bit. A decision block
may be exponentially long in g; its length is neither an arithmetic operand
nor an index. Previous blocks are not revisited. This replaces #4327's host
`n0s` and `k*N` operations.

At round end the stored flag count decides whether a record continues. Keep
bits and final records are appended to two separate, locally delimited stacks.
A record is stored as final only once. The next round reads only its continuing
stream. At wrap-up, the last keep block interleaves the current final successor
stream with that round's final-record block; both must end together. Both
blocks are then popped locally. Empty final-record blocks are legal. No list
of round sizes or rest sizes exists.

Internal bodies are contiguous up to their current local end. Completed stack
blocks are erased before their old extents are reused. Rewinding an active
work tape crosses its present content; it never seeks to its historical high
water mark. Retained blank backing nevertheless remains space under §8.

## 5. Encoded non-dyadic exposure and actual numerical calls

After radix distribution, one axis's records are contiguous. The bank is scanned
forward in axis order once per round. Each axis's descriptors, E table, mask
and eight pages are copied to fixed active ports, including unused axes; all
copies, checks, erasures and rewinds are billed. Pages from different contexts
are never regrouped by a host key. Empty substreams make no numerical call.

For fixed f, the #4327 source lemma gives a prefix block
`E_f x Z'(prefix)` in the incoming lexicographic stream. Z' is identical in
every active row because the round's tag restriction depends on the other
coordinates, once membership of x_f in E_f is fixed. This inherited lemma
permits complete lines without discovering the potentially huge suffix length.

`unit(k,a,level)` computes the source balanced range tree with Count operations.
It starts at `[0,a)`, repeatedly splits by `floor(n/2)`, and follows the branch
containing k until its range height is at most the requested level. At equal
height its finite role is A or B; below that height it passes unchanged. The
height is `ceil(log2 n)`. Operands are polynomial in L; no host tree or decoded
ordinal is used.

One level first splits A/pass records to M1 and B records to M2. The second
pass uses a raw saved prefix and encoded ordinal interval to detect the current
unit. A merge takes h records from M1, then n-h from M2, repeatedly; every chunk
and both ending boundaries are checked. Pass units are copied. For inversion,
the same split is followed by copying the whole A part and then the whole B
part of each unit. Increasing levels expose lines; decreasing levels restore
order. This is #4327's same non-dyadic schedule, with its keys, tree controls
and comparisons now carried by tape operations. The suffix length never
becomes a Count.

At the exposed boundary the program calls the unchanged
`UnionInverseWindow.run`, supplying its eleven physical data ports and ten
encoded metadata fields. The child checks complete ordered E lines and common
spectator/header bits. It receives current values from the segment stream,
not values reloaded from the dense input. The parent allocator is suspended
during the call; borrowed pages/tables/descriptors lie outside all child-owned
roles. The full protected child result is copied, then consumed, before the
inverse transpose. Parent work and child return tapes are disjoint.

The program neither changes batching nor assumes rounded maps commute. Invoke
#6908's already-proved flag-class chronology: each complete line stays in one
class F; class F receives its active axes in increasing order using updated
values; inactive axes act identically there. Permutations and their inverses
preserve exactly these current values. Deleting a completed class cannot remove
an input needed by a continuing class. Dense restoration therefore equals the
full increasing-axis rounded reference.

For an analytic error corollary, the inherited radius/error hypotheses must
hold at every actual current line. With axis norm bounds K_i and valid local
errors epsilon_i, the sequential estimate is
`E_final <= E_in product K_i + sum_i epsilon_i product_(j>i) K_j`.
These source and incoming-error premises remain explicit. Rounded finite
output equality alone establishes neither recovery nor the prior dense stage.

## 6. Fixed roles, ownership, and the meaning of execution evidence

The router preallocates 256 scratch roles and 27 named buffers, independently
of dimensions, record counts and keys. Its numerical descendants retain their
fixed inventories. Variable metadata use leased Count tapes; long payloads,
prefixes and decisions use named streams. Constructor sealing forbids allocating
a Tape or numerical Arena during a call. The source no-decoding tripwire is
active in registered executions.

A conservative source census gives fewer than 64 simultaneous new-router
metadata leases, below the 256 supplied roles. The fixed Geometry retains nine
Counts. A round, axis iterator and loaded axis descriptors retain at most six
more. `apply_segment` retains at most four before `zip_level`. The latter
retains at most nine for its prefix/range/chunk scopes, then calls one key
reader (at most four more). The retained Count primitives use at most five
leases including their result and transient literal tape; iteration keeps two.
The other metadata paths have smaller fixed-depth combinations. In particular
`unit` closes each old range before its next iteration, and no loop accumulates
leases. These deliberately loose bounds cover construction transients as well
as steady states. The numerical child uses its own pool while the parent pool
is suspended. Finite runs report the observed peak separately; that observation
is not the all-size inventory argument.

Success closes every metadata lease and erases every nonoutput role/marker.
The child owns disjoint tapes. Parent and child scopes suspend/resume without
ending parent leases. A pending flag protects output even if a caller moves its
head past live data; another run requires consumption. Borrowed source,
catalogue and descriptors are rewound and never modified.

Framed inputs use the declared binary/fixed-delimiter alphabet and one unique
local LEFT origin. Forged interior origin markers are outside this tape
representation. Within the interface, tests reject malformed counts, truncated
scalar/page bodies, wrong mask cardinalities, duplicate E coordinates,
different contexts and corrupted return headers. Failure injected after a
completed child return closes that pending child and clears parent scratch.
Atomic descriptor acquisition matters: if the second field fails, the first
field's lease must still be released.

Measured actions are primitive reads, writes and unit head moves, not Python
VM instructions or exact binary-TM transition counts. The finite alphabet has
a constant-factor binary simulation. Python observation counters (rounds,
visits, lines, calls) never select operations. The online code reads no tape
`.cells` or `.head`, constructs no variable-size host record collection, and
makes no external payload callback. External encoders/oracles inspect finished
words; they cannot supply intermediate machine values.

## 7. Complete time invoice

Define

\[
 D=L^g,\quad U=|\{x:F(x)\ne\varnothing\}|,\quad
 S=\sum_x|F(x)|=\sum_f a_f L^{g-1},\quad B=H+2w,
\]

and `ell=1+ceil(log2(L+g+w+b_max+P+2))`. Let R be the number of executed
rounds (R<=g), q the full binary context-key length, C the complete serialized
bank length, and `a_max=max_f a_f`. For a nonempty axis put

\[
 K_{E,f}=\lceil a_f/b_f\rceil,\qquad
 K_{J,f}=\lceil n_f/b_f\rceil,\qquad
 P_f=2[(2K_{E,f}-1)+(2K_{J,f}-1)]b_f^2w.
\]

Set P_f=0 for an empty axis. If `len2(v)=max(1,ceil(log2(v+1)))`, the actual
axis block length is

\[
 C_f=a_f(h+1)+P_f+\operatorname{len2}(a_f)+
       \operatorname{len2}(n_f)+\operatorname{len2}(b_f)+15,
 \qquad C=q+1+\sum_f C_f.
\]

The 15 cells are the three Count terminators, axis delimiters, E/mask delimiters
and eight page delimiters. The dense membership store has length
`M=g[L(h+2)+2]`. These lengths include empty pages/axes; no coefficient bank or
context key is free.

The complete **new transport** bound is

\[
 T_{\rm route}=
 O\left(\left[DB+SB(1+t+\lceil\log_2\max(1,a_{\max})\rceil)
             +M+(R+1)C+1\right]\ell^5\right).             \tag{1}
\]

The DB term is the two dense header/odometer passes, forming indicators and
final scatter. It is not charged to sparsity. M is actual membership production.
The S terms sum the actual live round sizes, not g times the original union.
The C term covers initial validation/production plus every complete per-round
bank scan and active-port copy, including unused axes, context traversal,
rewinds and erasure. All S_r delimiters, round/axis controls, return consumption
and local stack movement are covered; C>=g bounds the separate gR loop cost.

To see the polylogarithmic factor is legitimate, every arithmetic descriptor
is polynomial in L,g,w,b: header offsets, local fields, row/page extents and
balanced-tree ranges. Their lengths are O(ell). Canonical Count copy, addition,
comparison, products and division have elementary polynomial-time tape bounds;
O(ell^3) suffices for those used here. A tree query adds at most log L short
iterations. Sequential raw-prefix comparisons scan O(H) bits and do not perform
arithmetic on a key value. Copy counters are local record/chunk widths, never
D, U, S, N_r, a suffix-row length or a stack offset. Combining these source
loops gives the conservative ell^5 in (1). In particular neither H^2 nor
`(log D)^2` is hidden inside `polylog(p)`.

Numerical work is additional. Let m_rf be the number of complete lines in a
nonempty `(round,axis)` substream, an observer's quantity not a machine counter.
Put

\[
 Z_{rf}=\lceil2m_{rf}/b_f\rceil,\qquad
 Q_{rf}=[2(2K_{E,f}-1)+2(2K_{J,f}-1)]Z_{rf}.
\]

The unchanged child makes exactly Q_rf b_f-by-b_f integer matrix calls and
`Q_rf 7^log2(b_f)` scalar leaves. Retaining its complete invoice gives

\[
 T_{rf}=Q_{rf}T_7(b_f,w)+
 O\left([m_{rf}a_f(H+w)+Z_{rf}K_{E,f}b_f^2(w+\ell)+1]\ell^3\right), \tag{2}
\]

where the retained kernel includes its scalar multiplier and internal width
increases. No call occurs for an empty substream. Every partial-row and last
complex-column ceiling in (2) remains. At most g squared substreams are possible,
but their costs are summed at their actual sizes. Exact incidence gives
`sum_(r,f) a_f m_rf=S`.

The complete scoped time is

\[
 \boxed{\quad\sum_{\rm prepared\ keys} T_{\rm source+pages}
              +T_{\rm bank\ serialization}+T_{\rm route}
              +\sum_{r,f}T_{rf}.\quad}                    \tag{3}
\]

Source setup is §2/#6908's bill, including exact rational serialization and
physical preparation; bank serialization is a linear paid copy with short
metadata operations, included once per actual copy. Borrowed catalogue scans
inside numerical calls are already in (2); extra parent scans remain in (1).
A caller must also add delivery, grid conversion and subsequent stages.

### Conditional complete-context specialization

Suppose `w=Theta(p)`, all local side/block/count parameters are polynomial in p,
`H=O(p^beta log p)=o(p)` for a fixed beta<1, and the inherited carve density is
`a_f/L<=mu=O(W/B_int polylog p)`. Then the first two terms of (1) have the
existing dense group-scan and per-incidence transport shapes. Over d/g complete
balanced groups they are respectively
`O(V(d/g) polylog p)` and `O(V d W/B_int polylog p)`, for payload-bit volume V.
An arbitrary admitted partition does not imply this density; the finite
fixtures are not its proof. The child additionally retains the row-ceiling
hypotheses used in #6908 when converting (2) to the boundary-algebra row.
No historical numerical balance or structured matrix exponent is imported.

There is a useful, explicitly premised amortization of (3)'s preparation and
catalogue remainder. Suppose **each delivered context** has
`g=Theta(p^beta)`, `L=p^Theta(1)`, original-coordinate scale
`ell_original=O(p^(1-epsilon))`, and `beta>1-epsilon`. Assume the source numerical
parameters and radius-description height are polynomial in p and the complete
context description has at most `2^O(ell_original) poly(p)` bits, uniformly over
source keys. There are at most g distinct axis keys in this one delivered
context; this is not a sum over an arbitrary global collection. #6908's source
invoice then gives `sum_keys T_source+pages <= 2^O(ell_original) poly(p)`. Catalogue length is bounded
both by the explicit C formula and by its charged construction writes, so all
(R+1)C traversals and serialization satisfy the same envelope.

But

\[
 \log_2 D=\Theta(p^\beta\log p),\qquad
 \log_2(T_{\rm setup}+(R+1)C+M)=O(p^{1-\epsilon}+\log p).
\]

The second divided by the first tends to zero. Thus that complete fresh setup
and catalogue remainder is `o(Dw)` per delivered context. This uses the lower
bound on g, not merely the header-width upper bound `g<=O(p^beta)`, and uniform
constants over keys. It needs no cross-context cache or RHS regrouping: the
program actually shares each prepared bank across its whole complete context.

This corollary does not prove that the global supplier delivers these complete
contexts, that production Reference/grid promises hold, or that truncated/edge
microboxes may be padded at no cost. Those remain separate obligations. The
unconditional-in-the-parameters invoice is still (3).

## 8. Retained backing and protected return

For a fresh frame let `C_max` be the largest individual serialized axis block.
The parent has the following simultaneous, separately identified stores.

| Physical role family | Sufficient backing |
| --- | ---: |
| Protected dense output and full context | `O(q+Dw)` |
| Current/next, radix buckets, segment and zip buffers | `O(UB)` |
| Round keep decisions | `O(S+g)` |
| Final-record stack | `O(UB+g)` |
| Per-round radix decision stack | `O(Ut+t)` |
| Dense indicator | `O(D)` |
| Membership catalogue, odometer, header/prefix and E table | `O(M+H+Lh)` |
| Active axis mask and all eight page ports | `O(C_max)` |
| Fixed pool of short metadata | `O(ell^2)` |

Each final record is parked once. A keep bit is written once per visit, hence
S, and the radix stack is completely popped before the next round. Named
record streams reuse the same fixed roles. Their total high-water backing is
bounded by a fixed multiple of UB, even if the roles reach their maxima at
different times. The O(ell squared) metadata allowance conservatively covers
all inherited arithmetic temporaries used by this parent; their values have
O(ell) bits and the number of roles is fixed.

Add the numerical child's full retained bound `max_(r,f) S_inv(r,f)` from
#6908 PROOF §6. This includes its headers, input/returned line values, all
intermediate work, padded rows and complex columns, matrix-product recursion
and seven-product descendants. Parent buffers remain parked while that child
runs. It is therefore a sum, not a choice between parent and child space.
A transparent fresh online bound is

\[
 O(q+DB+S+Ut+M+C_{\max}+\ell^2)
       +\max_{r,f} S_{\rm inv}(r,f).                      \tag{4}
\]

There is no additional sparsity premise in simplifying the transport part:
`S<=gU<=UH`, `Ut<=UB`, `U<=D`, and, because `D>=L` and `H>=g(h+2)` up to a
fixed additive constant, `M=O(DH)`. The `g` and `t` delimiter terms are also
absorbed. Thus (4) is

\[
 O(q+DB+C_{\max}+\ell^2)+\max_{r,f}S_{\rm inv}(r,f).       \tag{5}
\]

Borrowed input backing `q+1+2Dw`, the complete bank C, external descriptors,
source caches and setup's `O(u^2 H_rat+C_ref)` storage remain additional unless
already part of the caller's counted stock. A complete accounting adds these
quantities, rather than hiding them in the child. Under the explicitly premised
complete-context specialization of §7, polynomial local/page/setup remainders
are smaller than D and `H=o(w)`; this does not establish a global stock theorem.

Erasing live symbols does not release retained tape backing. For repeated calls
on the same owner, replace each role's fresh bound by its maximum **historical
visited extent**, then sum over the fixed roles. Historical setup namespaces
and borrowed catalogues are accounted in their respective owners. Old blank
tails need no repeated scan: the invariant is that every old live symbol was
already erased when its block or stream was retired. A later shorter call does
not create uncleared holes. A caller may move the protected return head past
its live end; the pending flag still blocks reuse. Any such additional caller
movement/backing belongs to that caller and its subsequent rewind.

Execution receipts report written backing (`sum len(t.cells)`) separately from
this all-size visited-backing convention. Writing a cell retains its allocation
even after its symbol is erased. The finite interpreter does not allocate a
bytearray cell merely because a head visits a blank cell, so the receipt is not
silently identified with an exact visited-cell count. The theorem counts the
complete visited spans, including delimiters, blank lookahead and erasure.
The large numerical run's all-size space conclusion comes from the role bounds,
not from its finite backing number.

## 9. Evidence and unresolved joins

The proof rests on the pinned record schedule, the unchanged numerical service,
and the literal procedures described above. Executions can detect programming
errors and source mismatches; they are not an all-size proof or a proof-assistant
certificate.

The transport verifier uses a separately written dense increasing-axis oracle
and a physical nonlinear line service. Endpoint NAND changes the first exposed
row's low bit using the current last row. It distinguishes wrong axis order and
stale reloaded values, which an identity service would miss. The independent
reviewer additionally uses arithmetic strides on a flat dense vector, with no
imports from the author fixture/oracle. The numerical replay instead executes
the unchanged #6908 source factor/page construction and actual seven-product
consumer, compares every dense scalar word with its independently retained
original-matrix rounded oracle, and checks full context, borrowed views and
consumption. Actual executed instances and measured action counts are recorded
in the receipts and README; source-only carve probes are separately labelled.

The following joins remain open and material:

- A production supplier must deliver the complete same-Reference contexts,
  their common grid and correct incoming dense-stage values, with its actual
  routing and retained stock paid. The complete-context corollary cannot fund
  missing or truncated data by declaration.
- Canonical carve production, original-coordinate catalogue setup and page
  serialization have an explicit source algorithm and invoice here. A literal
  full production setup pipeline with all retained source caches is a distinct
  completion task. The current scope physically executes page preparation in
  its admitted finite instances and the complete online emitter/router.
- The complementary broad forward service, prior interior solves, other inverse
  stages, rounded finite-core/halo assembly and global Gaussian/FFT/CRT recovery
  must be joined on their exact grids and source keys. This one completed window
  cannot stand in for those stages.
- To use the complete-context amortization in the selected outer supplier, prove
  its lower group-size and full-box delivery hypotheses apply to the actual
  supplied classes, while preserving the existing separately charged sparse
  tails. No new generic edge-padding result is needed here.

The selected bound and its five assumptions are unchanged. No claim here makes
#4100's proposed unconditional multiplier an admitted theorem.

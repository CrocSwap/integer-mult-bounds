# A complete source-array backing bound at PR2697 ADD

## Statement and exact boundary

Fix an accepted ADD event at `Consumer.apply` → `packet_engine.run` →
`stream_runner.action` in Jose Manuel's PR2697
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The Layout is the independent-gap
`layout.py` class, not the older class also named Layout in stream_runner.
Start immediately before action's `layout.extents`, with the caller already
owning the source fibre, prefix, directory, Program, Layout and suspended event.
End when action returns its distinct payload. Directory creation, the enclosing
packet loop and full Consumer initialization lie outside this boundary.

The coefficient is exactly the closure nested in Consumer.apply, including its
Fields constructor, and exactly `numeric.selected_coefficient`, including both
adapter and child requests. No abstract callback scratch parameter remains.
The event, source specifications, program, raw fields, canonical word margins,
unit divisions and arithmetic must satisfy the retained successful source
contracts. The native factory is the default Tape. No outside observer/factory
captures arrays or execution frames. Entry arenas have the canonical partition
of live/free slots and fixed-width templates. These hypotheses are essential.

Count distinct strongly reachable **source** Tape.cells and Word.cells backing
lengths, including LEFT/RIGHT, erased tails, inactive allocated numerical slots,
pending source results and templates. This is not Python heap capacity: host
lists, dictionaries, object headers, uncollected unreachable objects and finite
metadata are excluded. Matrix/list records contain references to already
counted Words; they do not introduce another source-cell array. All payload,
count and serialized record arrays within the boundary are included.

Let K0 count the complete entry baseline once by identity: borrowed source and
caller tapes, Program/Fields records, count inputs, both numerical templates,
and every allocated entry numerical slot, live or erased. Borrowed arrays retain
their identities and lengths. Numerical slot backing may grow and is charged
below, even after freeing its slot. Suspended caller residents are included in
L and H, not assumed absent. At the boundary, let H_R,H_I be allocated numerical
slot counts, L_R,L_I all live slot counts and b,I their residue/index digit widths.
The residue has canonical width b=bit_length(M)+1 for M=q^w>1. Let h be the
incoming ancestor depth, c the fixed Program code width, and P the full borrowed
Program backing length, including any erased tail. Actual Consumer.apply has
64<=parent_size<128 and dimension64; the proof retains its complete spectators.

Write the three returned extents U,G,S, F=U*M*G*M*S. Set l_i=bit_length(e_i),
W=max l_i and

    E = sum_i(l_i+2) + max(I+2,3W+9)
    R = sum_i(l_i+3)
    p=l_1+3, m=l_2+3, s=l_3+3, r=b+2
    C = p+r+m+max(m,r+2s*[S>1]).

These are respectively the inherited private count preparation upper bound,
exact returned marginal backing, and native Counter maximum. They come from
Nick Petalas's PR2912/2905/2916. E excludes the entry baseline; R is private to
action even though borrowed by add_pass. Their proofs include pending Count
constructors, retained closed Counter bindings and marginal copy transients.

Define numerical **growth above already charged entry backing**:

    Dpre = (max(H_R,L_R+6)-H_R)(b+2)
         + (max(H_I,L_I+4)-H_I)(I+2)
    Dall = (max(H_R,L_R+max(J_R,6))-H_R)(b+2)
         + (max(H_I,L_I+22)-H_I)(I+2),

where J_R=37672 for an adapter and 20494 for a child request. PR2835 establishes
these callback next-allocation bounds; PR2815 supplies Layout's6/4, and the
native ADD allowance is6/0. Templates already belong to K0. Arena high-water
accounting is PR2831/2923, not new here. New numerical backing is bounded by
Dpre during preparation and Dall thereafter. It persists across both callbacks
and traversals. No maximum of separate live-phase numerical bills is used.

For the conservative PR2758 four-stack bound, define

    a=2I+4, d=b+3, t=max(a,d)
    J(k)=2((k+1)t+kd)+t+d+2.

This per-array bound handles partial pushes, pop reversal and earlier successful
weights with the same depth bound. We deliberately need no sharp joint-grammar
maximum. All Callback constructors allocate fresh Stack pairs. Set

    Q_adapter = J(h)
    Q_child   = 4 + J(h+1) + P + 84+c+2I.

For Q chosen by the actual request branch, the whole boundary uses at most

    K0 + A,
    A = max(Dpre+E,
            Dall+R+max(F+3+Q, 2F+3+C)).                 (1)

This is a conditional upper bound, not a sharp total maximum, a physical bank
capacity, or an unconditional success theorem. One uniform allowance for all
ADD requests uses J_R=37672 and max(Q_adapter,Q_child).

## Closing the callback record and count inventories

The authenticated numeric/forms/matrices/controller/records/words closure has
no Natural or Counter constructor on the adapter path. Matrices allocate only
Words in the same two arenas. Page/forms retain those Words and finite metadata.
The four Tape allocations are the two Stack instances of Callback. Program
and Fields reads create numerical Words, already covered by J_R/22, not fresh
serialized field tapes. Hence callback-private count allowance H_C is zero.

Consumer's coefficient closure first calls Fields(...), creating one empty
Tape, then replaces its tape attribute with the borrowed prefix. The empty tape
becomes unreachable before selected_coefficient starts. It costs one cell and
is dominated by Q in the callback phase; borrowed prefix backing remains K0.
Executing selected_coefficient alone would miss this transient.

The child branch has a materially different inventory. `children.coefficient`
constructs parent Callback, calls `extend`, constructs leaf Callback and calls
leaf.weight. Parent's stacks never receive a weight request: they remain four
LEFTs. The leaf's stacks have depth h+1 and allowance J(h+1). During all of this,
the owned extended Program remains reachable. Parent and leaf borrow the same
Fields tape. There is no copied field matrix record tape and no private Counter.

`extend` writes a same-width root header, copies the parent's canonical STEP
records until BLANK, then appends one STEP. The new STEP has one tag, five
16-bit labels, one c-bit code, two I-bit Words with WORD_END and one RECORD_END:
its length is 1+80+c+2(I+1)+1=84+c+2I. Root header length is unchanged because
new_depth uses the same admitted I-bit width. Parent's complete backing P bounds
the canonical original serialization, even with an erased tail. Therefore
extended Program backing is at most P+84+c+2I, including its LEFT. Partial
construction cannot exceed the completed length. Its cleared backing is still
counted until children.coefficient returns. This proves Q_child. Omitting that
Program or the parent four LEFTs invalidates a four-stack-only join.

Leaf.close, parent.close and extended.clear occur before callback return; they
do not shrink backing, but all private record owners then become unreachable.
No serialization or host shape constants are silently charged as zero dynamic
records. Outside-capture and malformed execution are explicitly excluded.

## Common cuts and ownership

Preparation precedes allocation of ADD payload buckets and callbacks: E+Dpre.
On return, exactly R private marginal-count cells survive. All preparation
numerical high-water backing remains, so subsequent phases use Dall.

add_pass constructs left, right and out before its first callback: three LEFTs.
The first callback has at most Q record cells and no traversal Counter. During
split, bucket payload totals at most F bits, with three LEFTs; callback records
have been released, while Counter backing is at most C. At the second callback,
both split buckets persist, giving F+3 payload cells alongside Q, but the first
traverse frame and all its Counter owners have exited. During merge the split
buckets still have F bits and the pending output grows to F bits: at most2F+3
payload cells and C Counter backing, with no callback records. Numerical growth
Dall persists at every one of these cuts, including the second callback.

Finally, clearing buckets/marginals creates no larger backing. Until their
frames exit, erased buckets and marginal tapes remain charged by the same
bounds. At action return only the distinct owned output and numerical high-water
growth survive above K0. Maxima over these cuts give (1). We do not assert that
component maxima coincide or that a source reference release provides physical
tape reclamation. No reused physical placement or movement bound follows.

PR2882's packet formula counts caller arrays separately from action-private
ones. To compose, retain its caller expression at the action cut, add the
nonpacket baseline (numerical entry backing and other outside owners) once,
and add A. Do not count the action's borrowed local source or prefix again as
new action work. Before another action, update H to the arena's actual retained
high water. (1) does not authorize multiplying an incremental growth bound from
one action into a root-level reserve or replacing the complete caller ledger.

## Actual source discriminator and finite evidence

The inherited PR2835 rank1/depth2/modulus9 fixture has final width256 and cannot
instantiate Consumer.apply's first-width restriction. Our credited fixture recipe
uses root64*64^2 with matching canonical index digit width, giving final64. The
scientific runtime is unchanged. The first actual compile_plan/trace adapter
command is ADD target1/source0 at coordinate0. The source Layout returns
(1,1,9^126), hence full packet9^128. For the first good child ADD the extents
are (1,9^126,1), again9^128. These are executed count/geometry bindings, not
allocated payloads and not a selected catalogue membership proof. The low header
is a declared source-contract fixture, retaining the predecessor's qualification.

Separately, the complete81-bit native ADD uses the same unchanged coefficient
closure and real serialized records, with an explicit two-atom component Layout.
It executes both coefficient callbacks and all81payload bits. Its coefficient
outputs8/8 (adapter) and2/2 (child) agree with the credited integer oracle, and
an independent integer permutation checks the complete payload. It is never
labelled the full64-dimensional packet. Warm erased numerical slots and the
child extended Program distinguish the new composition from a live-only or
four-stack-only ledger.

The weak observer samples source Tape creation/writes and numerical high-water
growth, retaining no dead Tape or frame. It sums complete array lengths by
identity; fixed numerical Word constructor interiors are bounded by the next
complete slot, whose high-water sample dominates. Baseline bytes/lengths and
heads are checked, and all private record/count/bucket arrays must be unreachable
except the owned output. A one-cell-short observer quota rejects; that is a
source-accounting control, not a physical memory allocation experiment.

## Limits and credit

This closes the source-array action-private composition under the stated
contracts. It does not discharge arithmetic semantics, actual selected catalogue
membership, every source failure cleanup, physical allocator/visited-cell or
movement bounds, whole Consumer initialization, recursive/outer reserve, H2/P3,
large-prime admission, kernel verification or a new kappa. The universal statement
is the written composition; finite tests corroborate it. Retain Jose Manuel's
implementation and NOTICE, David Arias's caller lineage, Nick Petalas's component
and fixture proofs, Ross Richardson's retained-arena/count work, kumagi's packet
interface and ywz65's physical/parking lineage. New work is by JoyboyBrian with
substantial OpenAI assistance, Apache-2.0; no independent human approval claimed.

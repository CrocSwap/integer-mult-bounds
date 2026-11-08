# Ordinary BIT visited-space closure and the history correction

This is a constructive, source-bound space theorem. It supplies a local
realization of the old ordinary helper used in #5814/#5829, not an execution
of the unmaterialized final supplier. The canonical source is frozen at
7c49fe32c55de02c2c873655c804b16e4c3fef0a; exact pins are in SOURCES.json.

## 1. Quantified statement

Fix the pinned copied-center ordinary BIT circuit, its rational tables, fixed
radix q, productive width W>=2, and finite stream/temporary roles. It has
m=575 and W=188181929; neither raw number is substituted for a final compiled
template constant. Retain its algebraic endpoint and gate/call list as source
premises. Let V be the bit volume of two complete chunks with arbitrary complete
prefix, gap and suffix fields.

There exists a fixed-tape, source-faithful reusable-origin realization of this
ordinary helper such that every complete invocation has

    retained backing <= K_entry + C_q V.                            (1)

K_entry includes every previously visited cell, including erased cells,
input/descriptor backing, markers, and entry head-to-origin intervals. Entry
heads have the source's canonical convention. Scratch growth is owned blank;
warm scratch is blank at its completed local boundary. Constants depend on the
fixed circuit, radix and arithmetic algorithms, never on chunk widths, payload,
row/spectator lengths, recursion depth or invocation count. V counts physical
payload bits as in 02-streams, including every record bit. If a caller instead
uses a volume U counting records/coordinates, replace V by r(p) U, where r(p)
is the actual encoded record length at global precision p. An unbounded p is
not absorbed into C_q. Every physical marker and coded virtual blank is also
charged: a fixed number per local port/record changes the explicit encoding
length or fixed overhead, and descriptors are separately included below. V is
never a count of unencoded scalar cells. If a caller excludes markers from its
volume convention, their stated length must be added before applying (1).
A history with varying precision uses max_i r(p_i) U_i.
For any completed
sequence at the same fixed root origins, with no unaccounted external head
excursions and input replacement confined to those origins,

    retained backing <= K_entry + C_q max_i V_i.                    (2)

Here K_entry is measured once at sequence start, not separately at each call.
For no calls the added term is zero. The source's time-saving exponent and
native identities are not proved anew by this space theorem.

The literal history-free interpretation of `backing at a node <= K V_current`
is false. Fix q=3. In `02-streams.tex`, the actual two-digit permutation splits
two e-digit chunks into nine buckets. Each bucket receives 3^(2e-2) symbols,
then is erased and rewound. Follow with the same elementary operation at e=1,
of volume nine. Each bucket still has at least 3^(2e-2) visited cells. This
exceeds K*9 for large e. All-zero payloads suffice, and all endpoints and heads
can be correct. These elementary operations occur in the ordinary helper's
digit stages. The old flat-work-tape schedule can likewise leave root-sized
warm backing for a smaller child. This is not a counterexample to a global
linear-space bound or to #5814, which explicitly includes K_initial.

#6098 already distinguishes retained tape history from live leases. Our new
contribution is binding actual ordinary movement procedures to bounded reused
origins, and identifying exactly which interpretation of #5829 is applicable.

## 2. Actual elementary procedures

`02-streams.tex`, elementary-streams, uses q^2 buckets for two-digit permutations,
q for digit moves, and fixed W streams for cyclic whole-row splits. The buckets'
total written payload is V. The procedure merges, erases the just-written
extents and returns heads. Its O(V) time includes counters, shape preparation,
resets, rewinds and visited blank portions. A fixed number k of unit-speed
heads taking cV steps from normalized local origins reaches at most k(2cV+1)
local coordinates. This bounds visited extent, not only nonblank cells.

The ordered-affine procedure uses two pieces totaling V for rotations; fixed
integer scaling uses a fixed number of monotone pieces totaling V. Negation's
whole-block stack and block-reversal stack are each at most V. Fixed rational
preparation and local counter copies belong to the same O(V) bound. An
ancestor-dependent unit is never treated as a fixed number of monotone pieces.
The weighted source instead keeps such units in child weights or additive offsets.

Our realization runs each procedure at a normalized relative origin, records
its current written/visited extent, clears only that extent and rewinds there.
It never searches to the largest position historically visited by an ancestor.
This is an explicit constructive lowering of the source descriptions, not a
claim about every existing Python audit implementation. #5814 section 3 encodes
all virtual symbols, including virtual BLANK, as nonblank fixed-length codes;
a separate physical delimiter marks the local origin. Cleanup therefore includes
coded blank cells. The fixed alphabet/code width only changes constants.

Repeated passes on volume <=U revisit a fixed interval of length cU per tape.
The union of those intervals costs cU independently of pass count. Thus w digit
passes, f atom passes or many completed calls do not acquire a factor w, f or
number of calls in their backing bound.

## 3. Old ordinary recursion: no owned-child circularity

The copied-center word is fixed and finite. Enumerate its finite scalar
instructions and retained-center episodes. Allocate a separate static role for
each private episode; this safe finite inventory need not equal its peak-live
count. `copied-centers-lemma.tex` specifies a complete V/W copy, transform,
unchanged scatter reads and discard in both orientations. Original role banks
are distinct; private banks receive no productive credit. Static source-use
order, not an aggregate recursive restoration assertion, licenses the lifetime.
All nonrecursive scalar gates, INIT/COPY/CLEAR, ordered rational adapters and
bounded digit remainders are section-2 macros. In `copied-centers-bit.tex` every
paid t is smaller than m=575.

`batched-bit-rows.tex` supplies one root padding, complete V_j/W children,
retained unused main digits as spectators and strictly smaller widths
`t floor(e/m)`. No descendant pads. Its descriptor argument gives
`log V_root = O(log(2 V_j))`; each fixed polynomial of descriptor bit lengths
is O(V_j). This is a local geometry/descriptor result, not an owned-child axiom.

Apply #5814's coded-segment primitive simulation and protected return bridge to
these finitely many roles. Its induction derives recursive allocation, output
return and private cleanup from isolated macros and strict width decrease.
We do not quote the old schedule's global cleanup conclusion as a hypothesis.
The complete source algebra remains a separate retained premise. The new
simulation can increase fixed tape counts, symbol-code widths, setup constants
and ordinary tariffs. Given the retained source time argument it preserves
the asymptotic exponent, since its fixed overhead and O(V) local administration
enter that argument's ordinary constants. It does not preserve or certify an
existing numerical finite tariff/admission ceiling automatically; those
constants must be re-priced for this realization.

Here is the retained-history part explicitly. On each physical segment tape,
a push starts immediately after the current parent segment, and pop restores
that exact top. A next sibling reuses the erased suffix, rather than appending
after the old high-water mark. The current node, all its private static roles,
descriptor and delimiters need at most cV_j coded cells. Every position ever
reached on that tape is therefore within an interval of length

    c sum_(j>=0) V_root/W^j = c V_root W/(W-1).

This holds at every time, for every sibling history. Taking the union over time
does not enlarge the fixed interval. Sum this bound separately over the fixed
physical tapes; a maximum of total live space alone would be insufficient.
The global bridge is empty during descent and has an O(V_root) envelope.
At e<m the source executes a bounded number of single-digit operations,
providing the induction base. Empty arrays use the declared direct empty branch;
our positive-volume theorem and checks do not charge a fictitious payload there.
All earlier entry backing remains in K_entry. Erasure leaves visited cells
charged, but restores the top and blank-growth invariant. This proves (1) for
the padded recursion without assuming recursive child ownership.

## 4. Arbitrary widths and repeated histories

`batched-bit-rows.tex` borrows existing high digits and pads their row range R
to `W^D ceil(R/W^D)<2R`. It does not allocate W^D copies of the array. Gathering,
ungathering and bounded exceptional small widths use section-2 digit passes
with the same local origins. Binary-to-radix-q padding enlarges each chunk range
by less than q, so the padded core volume is less than 2q^2 V. Padding and
unpadding streams have that same envelope. The older `04-swap.tex` power-piece
presentation also reuses one restored row reserve across sequential pieces.
Thus the invocation bound is uniform at every positive binary width.
For a sequence, replace each V_i by its maximum before taking each tape's union
of reached intervals. This proves (2), charging K_entry only once.

## 5. Delayed-cover applicability and the remaining edge

The selected query-thinned source section 4 retains the delayed-cover interface.
For a fixed final template, the following actual source operations can use the
new ordinary-helper realization. Constants may depend on that final template.

| Operation | Pinned source | Space consequence |
|---|---|---|
| Fixed right cover route | DELAYED-COVER-BRIDGE section 6; three-stage-cover-bit, finite covers | Fixed scalings, ordered shifts and a fixed number of old width-O(w) interchanges; O(V) envelope. Fixed low types are streams; high lifts are addresses. |
| Stopped weighted atom J_a | three-stage-cover-bit, weighted leaves | Four old ordinary swaps, three prefix-controlled shifts and one sign; sequential old-call maxima give O(V), subject to evaluator scratch below. |
| Atom adapters / peeled atoms | stopped-product-interface, paid atom adapters | O(n) sequential passes reuse origins; a radix-q atom conversion has volume factor below four. Pass count affects time, not backing. |
| Bad-class lower shear | three-stage-cover-bit, local-ring fallback | One ordered atom pass at a time plus constant-dimensional ring arithmetic and generated evaluator scratch. |
| Bad-class swaps, upper-shear brackets, paired scalings, reversals | Same subsection | These are paid recursive children of width <=f, not nonrecursive old-helper calls. Their actual geometry, descriptors and return binding remain the outer dispatcher's obligation. |

Write E for the actual maximum visited coefficient/ancestor-evaluator workspace.
The robust local statement is

    newly generated relative extent <= c_T (V+E).                   (3)

The inherited polynomial-preparation result is already explicit in Jose Manuel's
#2234, `selected-bit-recursive-closure/PROOF.md` sections 6–7: current-prefix
counters, branching-by-two ancestry evaluation, a possible literal-vector
factor, and root-coupled absorption by the complete atom fiber. It is not a
new closure claimed here. That source and the retained cover note specify
fixed-dimensional ring arithmetic and polynomial preparation in w on the root-coupled domain w=ceil(e^delta), fixed delta>0,
generation depth O_T(log e). Unit-speed heads then use polynomial space in w.
Each complete atom target fiber contains q^w records; every fixed polynomial
in w is <=C_T q^w<=C_T V. Finite small-width cases are absorbed. Under that
*source evaluator contract*, (3) is O_T(V). Arbitrarily supplied ancestry or
unbounded external descriptors do not satisfy this conclusion automatically.
The final compiled evaluator/counter protocol is not instantiated here; this
remaining application binding is distinct from the already proved polynomial
preparation and absorption fact.

Thus old ordinary subcalls, fixed routes and stopped weighted leaves have a
source-faithful local space construction. #5829's geometric bound applies if
`K V_j` denotes node-local generated extent/arena capacity, with retained history
handled globally as above. For constant global precision along a recursion,
that bound is K_entry+C_T r(p) U_root L/(L-1), with the actual low-type divisor
L of #5829. V_j=r(p) U_j is required at every depth; neither the record length
nor marker/encoding constants are silently dropped. It does not apply to the history-free reading
refuted in section 1. Final native macros, evaluator storage, fallback-child
binding, all final private lifetimes and production dispatcher remain separate.
The whole selected owned_erasure assumption is not discharged.

## 6. Compact movement

`compact-control-movement.tex` uses at most twelve ordinary chunk swaps on
complete compact fields of the same array. No independent address range is
introduced. Sections 2-4 give O(V) backing for their finite sequential composition.
Rotations use two pieces totaling V, output and fixed arithmetic scratch.

Exceptional repair retains one full stream with marked holes, at most M records
of R bits, O(A)-bit destination keys and a fixed number of radix-sort streams.
A stable binary pass splits all key-record pairs into two streams, merges into
an alternate stream and erases/reuses the partition streams. It never retains
one generation per radix pass. One key's arithmetic uses O(A^c) scratch for a
fixed c, not one such scratch per record. With V=MR the envelope is

    C [ V + M A + A^c ].                                            (4)

The stated A=O(p), superpolynomial record width R, and M>=1 imply (4)=O(V)
within the admitted asymptotic parameter family. Outside that regime retain
(4). Bounded exceptional sizes require the family's stated finite-size handling.
This constructs a fixed-workspace schedule from the source method; no literal
compact repair transition table was executed.

## 7. What the checks do

The verifier authenticates source bytes and runs a newly written literal
q^2-bucket scanner. It meters reads, writes, unit head moves, erasure and all
visited payload/bucket-tape cells. Shape/index arithmetic and control counters
are host driver operations, unmetered here and justified only by the written
source argument; this is not a complete elementary-machine action certificate. Complete one-hot payloads test the permutation on every position
of finite rectangles. Shrinking and repeated calls expose retained warm tails.
An independent interval walker checks nested reusable segment origins. Controls
reject wrong bucket order, live-only accounting, append-only origins, omitted
entry backing and omission of inactive-tape history. Integer checks corroborate
the outer padding bounds.

No huge old word, final compiler/covered word, full fallback payload, compact
repair, numerical multiplier or proof kernel was executed. The universal result
is the written construction and induction, not an extrapolation from tests.
All five selected assumptions and the selected kappa are unchanged.

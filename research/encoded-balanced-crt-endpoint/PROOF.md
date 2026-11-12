# Uniform balanced CRT address-state evaluation through a paid source commit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
This is a source-relative enabling construction, **no new kappa**.

## 1. Exact claim and predecessor boundary

Supply the physical padded axis stream admitted by #5353 and #7154. There
are d >= 2 axes, with d a power of two, declared widths h_i in {ell-1,ell},
ell >= 2, pairwise coprime moduli 2 <= s_i < 2^h_i, and arbitrary padded
coordinates 0 <= x_i < 2^h_i. All admitted h_i are consequently at least
two. Each record is ROOT, h_i unary ONE symbols, WORD_END, h_i modulus bits,
WORD_END, h_i coordinate bits, RECORD_END. LEFT is at cell zero and RIGHT
terminates the logical source. Its head enters at one. Write

    A = sum_i h_i,  M = 2 + 3A + 4d,  P_G = 1 + sum_(i in G) h_i.

The supplied source has historical capacity K_source >= M. Its inaccessible
tail after RIGHT is retained and charged, including any old data there.
The source is owned by this enclosing evaluator. It is borrowed read-only
by each individual numerical invocation.

**Theorem (relative to the pinned numerical and frontend source contracts).**
The fixed finite-symbol program `endpoint.Endpoint.run`, receiving only
that source and its fixed provider modules, computes the complete forward
balanced CRT *address-state* endpoint on that same source. It enumerates
each aligned node exactly once, in increasing level and start order,
using the unchanged #7154 encoded iterator. Each node reads the actual
coordinates left by all earlier commits. There are no runtime host integers
for coordinates, moduli, widths, precision, level, node start or axis count.

Only coordinate bits may change in the final source. Every other cell,
including the source's historical tail, is preserved, its backing object
and capacity are unchanged, and its head returns to one. There are exactly
79 owned roles: the predecessor's 78 roles and one full-source staging
role. Upon successful completion every owned historical cell is blank and
every owned head is one. One lifecycle is claimed; no persistent restart
or arbitrary dirty-backing allocator is supplied.

The complete source-operation cost has the form

    C_state (M+2)^2 + 4096
      + sum_G [2^20(P_G+2)^4 + 2^16(P_G+2)^2 + 4096],       (1)

where C_state is one fixed input-independent finite-control refinement
constant. The raw reads/writes/unit-moves of the frontend and this adapter
fit 2^18(M+2)^2. The separate inherited numerical bounds are added in (1).
The exact complete-control value of C_state is not certified, as in #7154.
For A <= p this is O(p^4) time and K_source + O(p^2) retained cells.

This evaluates one address-state vector. It does not move a payload indexed
by all addresses, produce or select Beneš micro-rows, implement inverse
traversal, or prove a bit-Turing-machine compiler. The source arithmetic,
entry, physical owner and encoded-iterator contracts remain explicit
premises. All five selected foundational assumptions remain conditional.

### Exact pins and novelty

The runtime frontend is #7154 at
`cc35ecedce6f208d5056fab6d17c58555affc73c`, unchanged blob
`8adbe2cfef74da9854ed0b70b6c221f5746efa9f`. The six unchanged numerical,
entry, owner, word, record and canonicalization sources come from canonical
base `e54523517d0f03e58352e647c403a5af3e525a57`.
`INPUT-PINS.json` authenticates all seven exact byte exports by SHA256 and
Git blob. Their copyright and assistance notices are retained.

#7154 supplies a numerical-node iterator and leaves its whole source
read-only. #7152, head `66adbede4bd4ab603ba3e0a7f6708403905b753c`, supplies
the complete actual source-state transform through paid micro-row queries
at compiled geometry. #5053 already supplies each whole-node updated
coordinate, and #5496 explicitly discards that field while building a
single micro-row. None of those predecessor results is claimed anew.

The new implication is that #7154's physical iterator remains correct when
the enclosing owner commits precisely the emitted whole-node coordinate
fields between leases. The accompanying paid projection/commit code proves
that implication on actual streams, with exact extent and lifetime checks.
It bypasses ROM construction only for this one-vector endpoint consumer.
It supplies neither the encoded row scheduler left open by #7154 nor the
payload implementation left open by #7152.

## 2. What one whole-node result means

For a node G = [a,a+2H), let its left child be A_G and right child B_G.
The #5053 numerical contract reconstructs k_A from the *current* left
coordinates, not from their original mixed-radix interpretation. If a
left coordinate is invalid padding, it sets k_A = 0. Otherwise k_A is the
unique integer in [0,S_A), S_A = product_(i in A_G) s_i, satisfying

    k_A = x_i product_(a <= j < i) s_j  (mod s_i),  i in A_G.

For each right axis i in order it returns a P_G-bit pair (c_i, y_i), where

    c_i = k_A [product_(a <= j < i) s_j]^-1 mod s_i,
    y_i = (x_i + c_i) mod s_i   if x_i < s_i,
    y_i = x_i                  if x_i >= s_i.              (2)

Pairwise coprimality guarantees each inverse. The prefix includes all
earlier right moduli, even when an earlier right coordinate is padded.
The output is a sequential ROOT/pair/RECORD_END stream. The numerical
producer, and its proof of (2), are unchanged premises of this package.

For either branch of (2), 0 <= y_i < 2^h_i. Therefore every bit above the
destination's declared width h_i is zero. This is the precise implication
needed to project the common-precision result to the source's heterogeneous
physical fields. `_updated` consumes the offset word by a paid P_G-bit
scan, copies exactly h_i low bits from the updated word, and checks every
remaining high bit is zero before consuming its delimiters. A malformed
or overflowing field cannot be silently truncated. The offset field is
never mistaken for the updated coordinate.

## 3. Snapshot before retirement, commit after retirement

At node handoff, #7154 leaves the source, axis cursor and unary half-size
counter at head one. STEP marks the current node's first axis; VALUE,
when present, marks the following node. The width counter is blank at
head one and may be reused after canonical input construction.

`stage` reinstates LEFT on the sole retired staging role. It scans source
records and the existing axis cursor together up to STEP, copying every
record unchanged. It then takes one unary-half pass over the left group,
also unchanged, and one over the right group using `_updated`. It copies
the remaining suffix unchanged, verifies that source and axis terminate
together, appends RIGHT, and returns all borrowed heads locally.

Each `_record` copies the original unary header and manufactures its width
counter from that header. The modulus field is copied in full. The original
coordinate is either copied or replaced with exactly as many low result
bits as the width counter contains. Thus each record retains exactly its
original extent and all tags. The width counter is cleared after every
record. Source validation and copying use only fixed-alphabet reads,
writes, append operations and unit moves; no width is decoded.

Induction on the scan establishes the exact staged word: it equals the
current complete source outside the right-coordinate fields of G and
contains (2) in those fields. It has the same logical length M. In this
entire phase the actual source is read-only. All source and numeric result
heads return to one before retirement. Staging is an owned independent
copy, not an alias of numerical output or source backing.

`lease.close()` next consumes the numerical output, clears its canonical
input and guide roles, retires the exact-width protected words, releases
the 63-role bank, and advances the encoded topology. The staged word
survives this close in its separate role. Only then may `commit` write
the source. Its guard requires a pending staged word, no live iterator
result and a released bank. It copies cells from staging to the same
source positions until the staged RIGHT and verifies the original source
RIGHT at precisely that position. The final RIGHT need not be rewritten.
It returns the source head and physically retires staging, including LEFT
and RIGHT. No backing is replaced, shrunk or forgotten.

The last node is included: the iterator may retire all topology counters
inside `lease.close`, because commit needs only the already completed
staged word and the source. No dead cursor or retired guide is read during
commit. This is why copying the full framed source is useful at this seam.

## 4. Coordinate-only mutation preserves the encoded iterator

The original #7154 whole-lifecycle source-preservation assertion is not
invoked for a changing source. Instead, use the following explicit extension
of its local state invariant.

At a retired node boundary, allow the enclosing owner to change coordinate
bits while preserving every record header, width, modulus, delimiter,
logical extent and entry head. The encoded axis count, depth, current STEP,
pending-marker discipline and unary half-size are consequently unchanged.
They depend only on the preserved shape and the number of completed nodes.
The next `_record` reads the newly supplied coordinate bits afresh; no
coordinate or arithmetic result is cached in the topology state. The
numerical bank and guards are already blank before the source update.
All next-entry premises therefore hold with the new coordinates.

The projection/commit lemma proves exactly these conditions. In particular
the high-bit check ensures that each new coordinate fits its physical field;
the copied moduli preserve coprimality and the complete-product capacity
margin. The source head returns to one, and mutation does not touch the
encoded next-node cursor. Inducting across all d-1 nodes proves both the
correct schedule and that each node sees the actual state left by its
predecessors, including children before their parent.

The controlled public operation is `step` (or repeated `run`), whose phases
are retired, result-live, staged, numerical-retired, committed. Internal
`stage` receives this evaluator's current lease exactly once; clients must
not bypass that protocol by calling the child iterator directly or retaining
stale lease aliases. This is the predecessor's linear-use interface, not a
general token-authentication or arbitrary consumer-mutation API.

## 5. Equality with the complete balanced CRT endpoint

At one node, every micro-row changes only right coordinates. Its controls
are determined by the unchanged left coordinates and fixed modulus
prefixes. The retained Beneš theorem says the complete micro-row sequence
implements exactly (2), including the padded-wire identity endpoint.
This package evaluates that endpoint directly; it does not suppress a
micro-row based on a padded intermediate, nor assert that the intermediate
states agree with the numerical output.

Distinct nodes at a common level act on disjoint coordinate groups and
read controls only within their own groups. Their micro-row maps commute.
Thus the compiled level/row/node order in #7152 and the level/node order
of complete node endpoints here have the same composed endpoint. Earlier
levels finish before later levels in both schedules. Together with Section
4, this proves the complete forward source-state equality for every
admitted padded input. It transfers no micro-row time, payload map,
physical routing or exception-repair theorem to this implementation.

On fully valid initial coordinates there is an additional independent
closed-form characterization. Put K = sum_i x_i product_(j<i) s_j. The
final coordinate is

    y_i = K [product_(j<i) s_j]^-1 mod s_i.                (3)

Induction on concatenated children proves this: a right-child residue
for its local mixed-radix integer receives the left child's integer times
the inverse full prefix, exactly (2). Later original digits contribute
multiples of s_i and cannot change the congruence. Formula (3) is used
only as a separate verifier oracle; it is not runtime input.

## 6. Complete source cost and retained histories

The inherited #7154 bill already pays shape manufacture, all source
projection/canonicalization, exact-width protected words, each unchanged
numerical invocation, disposal and encoded-cursor advance. The adapter
does not cancel any of those occurrences. It adds these items per node:
one complete framed source copy, right-pair scans at precision P_G,
all width/axis/half/guide/result head returns, equal-length source writing,
staging preparation and full erasure.

A deliberately conservative raw Port-action bound is

    2048 [M + n_G(P_G+2)] + 32                            (4)

for a node with n_G = 2H axes. To verify (4), each unchanged record of
width h uses at most 64(3h+4) raw actions including its width manufacture,
field copies, all local returns and width erasure. A changed record adds
at most 32(P_G+2) actions for the complete offset/updated-pair scans and
result returns. Axis and half traversal plus their returns are below
16(M+n_G+2). Commit and staging erasure use fewer than 32(M+2) actions.
Endpoint formation and fixed-role phase transitions fit the remaining
slack in (4). These are loop-length bounds on the displayed routines,
not extrapolations from measured execution.

The full sum in (4) is quadratic. At level j all nodes have size n=2^j
and partition the source, hence

    sum_G n_G(P_G+2) = 3d log2(d) + 2A(d-1).

This identity sums over all levels. Also sum_G M=(d-1)M. For h_i>=2,
A>=2d, log2(d)<=d-1 and M=2+3A+4d imply each of these two sums is at
most dM<=M^2. Adding (4), initial staging acquisition/retirement and the
predecessor 2^16(M+2)^2 raw frontend envelope fits 2^18(M+2)^2.

All variable adapter loops perform at least one local observation per
iteration; the only unobserved role iteration is the fixed two-child loop.
The symbols, finite phases, role selectors and call depth are fixed.
Expanding this fixed control supplies an input-independent multiplier,
giving C_state in (1). Its numerical value is deliberately not claimed.
The unchanged near-equal-width geometric sums from #7154 bound the fourth
power numerical terms by O(A^4) and the quadratic terms by O(A^2).

Let P*=A+1. The unchanged numerical bank has the rolewise history envelope

    B_num = (P*+1) + 2(2A+2d+2) + 57(P*+2)
            + 3[d(P*+2)+2].

The seven topology roles and eight guards retain the predecessor bounds.
The new staging role retains backing of at most M cells, and writes every
data cell only inside that extent. Appending or clearing the final RIGHT
transiently visits head index M, so literal visited-position accounting
charges M+1 cells. The list backing is never shortened. The retained-backing
envelope measured by the executable is

    K_source + B_num + 8(P*+2) + 6(d+2) + (A+2) + M.        (5)

For a caller charging the staging role's full visited span, replace the
last M in (5) by M+1. The other role terms retain the predecessor's declared
backing model; no literal binary space bound is inferred here.
This sums a maximum for each physical role across its whole history.
Erasure never subtracts capacity, and the source's old tail is counted
as K_source. Reusing the width counter for full-source copying does not
increase its existing A+2 envelope. Initial clean private backing and
the already encoded source remain explicit acquisition premises.

## 7. Evidence, failure boundary and unresolved obligations

`verify.py` authenticates exact source bytes, poisons host geometry/decode
names in both new adapter and frontend, and seals Port, Word and Arena
constructors after the 79 fixed roles are acquired. It executes the actual
providers, not a replacement numerical oracle. At every node an independent
integer search solves the defining CRT congruences. Fully valid inputs are
also checked by (3), independently of any tree recurrence.

The fixed finite family consists of all 32 padded coordinate pairs for
moduli (3,5), twelve four-axis states at (2,3,5,7), and one eight-axis tree.
It includes invalid left coordinates, padded right coordinates, mixed
declared widths, nonzero node starts, changing precision and retained
source tails. This is 45 cases and 75 actual numerical nodes. Runtime
values and decisions never come from the verifier. Histories, source
metadata, actual source object identity, extent, every boundary head,
complete private cleanup and the conservative cost envelopes are checked.

Negative controls reject writes before numerical retirement, advancing
before pending commit, double commit, unchanged stale coordinates in place
of emitted values, missing staging erasure, reversed close/write order,
projection into the wrong half, and a nonzero discarded high bit. The
high-bit control deliberately violates the trusted numerical-provider
postcondition. It demonstrates rejection before source data writes; it
does not establish cleanup or head rollback after that failure.

The successful theorem is not arbitrary malformed-input rollback, crash
recovery, dirty-memory acquisition or unbounded stale-handle validation.
Numerical-provider correctness, per-call entry retirement and #7154's
encoded schedule are inherited source hypotheses. Finite execution and
AI cross-review are not independent human or formal-kernel acceptance.

## Open next questions

1. Supply a reverse encoded node schedule and an actual subtractive
   whole-node numerical consumer. First pin an inverse caller and preserve
   the same current-state and retired-write boundary. This package supplies
   only forward evaluation; reversing the Python node list would reintroduce
   an external schedule and is not an implemented solution.
2. Bind this forward evaluator to an actual exceptional-key epoch whose
   input is already in the admitted axis encoding. Charge both representation
   conversion and the return to that caller's source frame. Generic endpoint
   equality does not establish the three-epoch key contract.
3. Complete encoded micro-row/target/header production for payload routing
   separately. The numerical endpoint shortcut applies to one address vector;
   it cannot replace the synchronized physical payload permutation.
4. Lower the complete fixed-alphabet controls and all providers to a literal
   binary program with a common tariff. (1) is a source-model bound; no
   selected compiler, precision, native-column or analytic-recovery
   obligation is discharged by relabeling it.

## Credit

#7154 and #7152 were prepared for Jerry Chen / CubeJerry with OpenAI
assistance. JoyboyBrian supplies #5053, #5219, #5505 and the #5496 numerical,
entry, owner and current-row contracts. Ali Romman supplies #5353's physical
axis encoding and #5625's retire-before-source-write predecessor. Retain
Cinna Davis's #4100 balanced CRT/Beneš construction, Hiroki KUMAZAKI's
current-coordinate/mixed-width work, ToikY's arena lineage, commdata2338's
storage accounting, and every notice in the unchanged source exports.
The elementary CRT identities and disjoint-support commutation are used
as known facts; the claimed contribution is the exact encoded consumer
join and its ownership, shape-preservation and complete source budget.

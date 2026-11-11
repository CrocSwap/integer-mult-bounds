# A dimension-parametric encoded coefficient consumer

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped consumer and source-arena theorem. **No new κ.** The selected
bound and all five foundational assumptions remain conditional.

## 1. Which missing implication is addressed

At base `e54523517d0f03e58352e647c403a5af3e525a57`, the application of #7000
uses the completed `.0034` BIT interface from `query-thinned-controllers`,
not the historical 64-dimensional supplier. That interface has a large fixed
compiler dimension. #6879 bounds an ordinary retained helper but excludes its
coefficient evaluator. #6903 produces chronological whole-high fields for each
fixed dimension N, while its numerical join explicitly supports only N=64.
#2835 proves noncircular numerical capacity for its pinned N=64 consumer;
#6896 likewise has a fixed-dimensional recursive numerical inventory. Neither
statement installs a dimension-matching coefficient consumer for arbitrary N.

The new contribution is an explicit specialization of the four encoded modules
retained by #6903, a reusable four-tape continuation workspace, and an all-depth
source-arena proof for this particular specialization. It preserves full
N²-digit chronological fields and original source labels. It does not generate
the selected `.0034` catalogue or Program labels, prove their grammar matches
this interface, install a changing-precision physical bank, or complete the
selected dispatcher. Those are separate, source-specific obligations.

All input bytes and the scientific base are pinned in SOURCES.json. The proof
uses the capacity-prefix calculus of #2835 and the retained-history distinction
of #5404; it does not claim those general principles as new results.

## 2. Domain and explicit compilation

Fix N≥2, an odd prime q, and a finite source catalogue before runtime. A label
has Q≥1 bits. Each catalogue member has a distinct label, a rank 1≤r<N, an
N-by-N low matrix, an N-by-N fixed rational preparation S whose denominators
are units modulo q, and a valid Good/Bad classification. On admitted fields,
H=(low+q·high)S is invertible over Z/q^wZ. A Good member has every required
leading pivot a unit. These are inherited algebraic source contracts, not
properties inferred from a finite fixture or from the label's name.

Write R=bitlength(q^w)+1, with w≥1. Residues use that exact canonical extent.
The root extent n₀≥N uses I=bitlength(n₀)+1 bits, exactly as the source guard
requires, and b_N=max(16,bitlength(2N)) is a fixed finite-label extent. Each
runtime depth, coordinate, extent, modulus and residue remains an encoded
Word. Only compile-time labels, matrix positions and finite operation tags
enter native control. Fixed source coefficients can be large; Ring.literal
reduces their compiled bit strings through encoded arithmetic.

`consumer.build(N)` verifies the original four hashes, performs exactly the
17 explicit single-occurrence edits in `changes`, and compiles the resulting
modules. The edits are: one finite-multiplier limit in words; four record
dimension/label-width sites; three matrix limits; seven controller dimension
or finite-label limits; and two controller interface sites that borrow the
two Stack objects instead of constructing them. N is not a runtime word.
All arithmetic loops and the evaluator/stack algorithms are retained. The
compiled instance may have enormous finite control; no efficient uniform
compiler or finite table construction bound is claimed here.

The supported invocation entry is `Workspace.open`, followed by a method of
the returned Callback and `close` (or the inherited `abort` on rejection).
The retained legacy `controller.selected_offset` wrapper does not supply
borrowed stack roles and is outside this new interface. No theorem or test
invokes that wrapper. Low-level Callback construction must supply the same
explicit workspace contract; exporting its source module is not a claim
that every historical wrapper remains a supported entry.

Callback handles obey a linear-use contract: only the current live callback
may evaluate, close or abort, and a returned or aborted handle is permanently
retired. `Workspace.active` supplies exclusivity, not a generation token.
Calling an old Python handle after a later `open` is outside the contract;
the source-arena theorem does not claim a physical stale-handle validation
service or storage for arbitrarily retained host callback objects.

The Program has a root record and h chronological step records. Each step
contains its original global source label and exact parent/child extents. It
is Good, Pair or Unit, using the retained grammar. If f=floor(parent/N), its
child is respectively r f, f, or (for Unit) f or floor(f/2). Children are
positive. Pair fields satisfy
0≤a<2N−1 and reversal is exactly the predicate a≥N. No other reversal or
non-Unit halving is admitted.

The raw Fields tape contains h records at a leaf, or h+1 for an internal
coefficient call, including every field before any Unit reset. Each record
contains its Q-bit original source label and all N² canonical high digits,
not merely an active rank subset. The current field uses the current label.
All inherited head, ownership, finite-metadata, shape, unit and arithmetic
margin contracts hold. The two numerical arenas are distinct and canonical.
No concurrent use, external Word construction or mutation of the arena
partition is allowed. Runtime metadata and host allocation failures are
outside the source-arena bound; their eventual lowering remains a compiler
obligation.

## 3. Exact interpreted semantics

For an admitted field let P=H diag(I_r,0) H⁻¹. Let d₀,...,d_(r−1) be the
Good elimination pivots. Let δ and π be the diagonal and row permutation
returned by the retained 2N-dimensional residual elimination for a Pair.
Define a generated weight W recursively, with root weight the encoded unit u.
For a child coordinate j:

* Good: W_child(j)=d_floor(j/f) W_parent(j).
* Unit: W_child(j)=1.
* Pair: put c=j or f−1−j according to the reversal flag, and set
  B_a(c)=W_parent(a f+c) for a<N and B_a(c)=1 for a≥N. Then
  W_child(j)=δ_a B_π(a)(c)/B_a(c).

These divisions require the inherited unit conditions. They are not inferred
from a successful capacity test. At a current internal site, with current
projector P and f=floor(final_size/N), the result for target row 0<t<N and
column 0≤c<f is

    coefficient(t,c) = −P[t,0]/P[0,0] · W(t f+c)/W(c).

The optional inverse flag negates this shear coefficient; `offset` multiplies
it by its borrowed source residue. It is not a claim that arbitrary matrix
inverse is implemented by negating all entries.

**Theorem 1.** Under the stated noncapacity contracts and sufficient arena
capacities as established in §4, the specialized Callback computes these
expressions. Every normal closed call restores all borrowed numerical heads
and all Program/Fields bytes and heads, and leaves both continuation stacks
empty. Full raw fields are read at their original global indices.

**Proof.** `step` verifies each exact child equation, chronological parent
link, rank, branch and physical pair label. `_validate_program` checks every
step's field label, the current label where applicable, and the precise end
of both records. `Fields.read` seeks the encoded global slot and materializes
exactly N² R-bit digits. It does not delete or renumber earlier fields after
a Unit. `Matrices.prepare` forms H using encoded modular operations and
computes the stated projector; Gauss elimination and the endpoint checks give
the stated pivots, diagonal and permutation. These ring identities and unit
conditions are exactly the retained matrix algorithm, with its finite loop
dimensions replaced by N and 2N.

For clarity, Pair elimination has the expected unit property in this domain.
Conjugating its residual by diag(I,J), where J reverses N coordinates, gives
`[[I−P,P],[P,I−P]]`. Its square is the identity because P²=P. Over the local
ring Z/q^wZ an invertible matrix has a unit candidate at each successive
elimination pivot; otherwise its remaining determinant is divisible by q.
The resulting diagonal entries are units. Together with the Good pivot and
root-unit hypotheses, induction makes every generated weight a unit.

At the `weight` loop boundary, each VALUE asks for one lower-level generated
weight, and each CONSTANT/MULTIPLY/PAIR continuation represents the matching
operation above. A Pair pushes its denominator request before its numerator,
so LIFO evaluation leaves the ordered denominator and numerator expected by
the PAIR branch. Every generated VALUE decreases its encoded level; the
finite stack evaluation therefore terminates. Unit returns one immediately
without arithmetic on dead earlier fields. The current coefficient routine
then applies the displayed quotient using two complete calls to `weight`.
Each borrowed word and record head is restored by the retained helpers, and
the result is the only newly live residue after normal closing. This proves
the semantics for arbitrary finite legal programs, not by testing depths.

## 4. Capacity before the first allocation guard

Let an arena have K allocated slots and L live residents at closed entry.
L includes every suspended caller, modulus, Ring.one, requested coordinate
and unrelated borrowed object. Its erased free slots and live slots partition
K, with restored heads. A pending demand includes the requested new slot
*before* Arena.zero checks capacity. Put

    B_R(N)=16N²+128,                 B_I=128.

**Theorem 2.** On every prefix of construction, one admitted weight,
coefficient or offset evaluation, and closing, before any separate
noncapacity error, the residue pending demand is at most L_R+B_R and the
index demand at most L_I+B_I. The theorem does not assume that a reference
execution succeeds or that either numerical capacity is sufficient.

The effect rule is the predecessor's: sequential (peak,net) effects compose
as `(max(P₁,N₁+P₂),N₁+N₂)`; a loop restoring its baseline does not multiply
peak demand by its iteration count. A partially allocated matrix is bounded
by its planned full shape. The final requested Word is included before its
guard. Free, rollback and record clear allocate no numerical Words.

Here is a deliberately nonsharp source-site derivation. Unsigned division
uses four additional requested/live Words, modular multiply and literal four,
inverse ten, and add/subtract/negate at most three. These same source loops
were proved prefixwise in #2835; changing the fixed `times_small` label limit
changes its loop count, not its two-result-at-a-time invariant.

* `prepare` uses at most 4N²+12 residue Words above its scalar callers.
  This includes the entire high matrix, raw matrix, every distinct fixed
  palette value, all copied preparation entries, the product, and the
  inverse's 2N² augmented entries. These large stages are sequential.
  An identity list aliases the inverse's right half and adds no second copy.
  Matrix multiplication charges its complete output and primitive scratch.
* A Good expansion holds its N²-entry projector, an N²-entry elimination
  copy, at most N pivots, and at most twelve scalar scratch Words:
  2N²+N+12. A Pair expansion holds that projector, its 4N²-entry residual,
  and at most twelve scratch Words: 5N²+12. Permutation labels are fixed
  finite control. Failed unit candidates retire their inverse scratch.
* Construction, callback residents, a retained current coefficient, a first
  generated numerator while its denominator is evaluated, and any popped
  continuation operands fit within 64 further residue Words. At each
  `weight` loop boundary all previous expansion matrices have been freed;
  serialized ancestors never accumulate numerical matrices or Word objects.
* There are at most six retained callback indices. A coefficient retains
  at most two further indices. VALUE/step/seek/division/address construction
  uses at most sixteen additional indices, including the request causing
  a guard. Constructor validation has the same bound. This is below 128.

For N≥2 the displayed residue phases plus 64 are below 16N²+128. All
phases count partially built arrays and a requested replacement while its
old Word is still live. This is a source derivation, rather than the measured
peaks of the examples. It covers prefixes ending in a capacity rejection.

Consequently **C_j≥max(K_j,L_j+B_j)**, established at entry, excludes a first
numerical inventory failure. If no free slot exists at a supposed failure,
all current allocated slots are live. The pending bound gives K_current+1≤C,
contradicting that guard. If a free slot exists the allocator does not test
capacity. This argument does not establish any other success precondition.

## 5. Historical backing in the actual fixed roles

The numerical allocator reuses erased slots before creating a new Word. Its
template and every allocated Word, including erased ones, retain R+2 or I+2
cells. Theorem 2 and this allocator invariant give the numerical backing bound

    (max(K_R,L_R+B_R)+1)(R+2)
      + (max(K_I,L_I+B_I)+1)(I+2).                         (1)

The extra one is the permanent template. This is a bound on the source Word
cell arrays, not the Python heap or an installed finite-tape bank. A physical
lowering must implement the finite slot vocabulary, reusable locations and
head restoration with its actual costs. In particular it must not allocate
a fresh physical bank on every callback or changing precision.

`Workspace` constructs exactly two Stack objects, hence four record Tapes,
once for its fixed pair of numerical arenas. Every callback borrows those
same roles exclusively. `close` returns the lease only after empty-stack and
numerical retirement checks; `abort` delegates to the retained cleanup. No
new Stack or Tape is constructed by `open`. The normal-return theorem does
not assert universal exception safety of partially initialized callbacks.

Let A=2I+4, D=R+3, T=max(A,D). VALUE occupies A symbols, and a scalar
continuation occupies D. On a depth-h traversal, the pending stack has at
most 2h+1 records and the value stack at most h+1. Each reverse tape holds
at most one complete record. Partial push/pop copies, including the time
when an operand exists on both tapes, fit these same individual extents.
Markers and the first blank visited after the logical end add a constant.
Thus the **sum of the four separate historical maxima**, not merely their
simultaneous live sizes, is bounded by

    S_stack ≤ (4h+12) max(2I+4,R+3) + 16.                  (2)

For a sequence of normal closed calls using the same Workspace and the same
fixed R,I, replace h by the maximum depth so far. Erasure never removes tape
backing; each later push starts at the same origin. The induction therefore
bounds the complete history, even after earlier deeper siblings return.
If the workspace entered with previously retained larger spans, take the
maximum with those four entry spans **coordinatewise** before summing.

The complete borrowed record spans, including an endpoint allowance, are

    S_program = 2I+R+10 + h(Q+5b_N+2I+12),
    S_fields  = (h+1)(Q+N²(R+1)+2)+4.                     (3)

The leaf has only h fields, so the displayed h+1 bound still applies. The
root record has two indices and one residue. Every step has five b_N-bit
finite labels, one Q-bit source label, two indices, and delimiters. Each
field has its source label, **every one of its N² high digits**, and all
delimiters. Reads reach no farther than the first blank after the prescribed
last record. Resets do not shrink (3).

If a producer rewrites the same borrowed Program/Fields roles at their fixed
origins across a sequence, their historical backing is bounded by the larger
of their entry spans and the separate maxima of (3). If a caller instead
keeps several ancestor Programs/Fields, those are separate owners and must
all be charged by its recursion theorem. Equations (1)–(3) include one full
borrowed prefix, not all independently retained caller copies. Producer
STATE, PREFIX duplication, payload, source access and other suspended frames
retain the bills of their own source interfaces.

For the standard coupling I=O(log n₀), h=O_N(log n₀), R=O_q(w), the new
component's bound is O_fixed(w log n₀+(log n₀)²), in addition to all entry
resident/history terms. This local source-arena result does **not** by itself
prove a B₀-level c_t V+K_t historical physical bound across changing R or I.

## 6. Complete consumer cost and the exact absorption condition

Each Word primitive scans its encoded operands; unsigned division takes
O(I²) index actions or O(R²) residue actions, and Euclidean inversion takes
O(R³). Fixed N, source tables and coefficient bit strings contribute finite
constants. Matrix preparation includes raw high materialization, rational
palette production, all fixed-dimensional inversions and every copy/free.
A record seek scans the full earlier prefix and updates an encoded counter.

Validation visits h earlier Program and Fields records, including the dead
ones. At most 2^(h+1)−1 VALUE nodes are expanded by a weight evaluation;
continuation operations add a constant factor. Two weights are used by one
coefficient. The first generated numerator remains live during the second.
The following deliberately loose bill includes construction, all field and
program seeks, coefficient preparation, both weights, rewinds and retirement:

    T_consumer ≤ C_fixed (h+1)² 2^h
                        (N²R + I + Q + b_N + 1)³.         (4)

C_fixed may depend on q,N and the finite catalogue, but not on n₀,w,h or
runtime entries. The source arithmetic and stack operations, rather than a
unit-cost numerical oracle, justify this polynomial. Charging the complete
prefix at every visited node is sufficient; no average seek or carry cost
is assumed. Field production, payload access, copying to the producer port,
and the final caller's actions remain additional positive terms.

**Lemma 3 (descriptor depth).** Every admitted step satisfies

    child ≤ ((N−1)/N) parent.

For Good, use r≤N−1 and f≤parent/N; for Pair and either Unit use
child≤f≤parent/N. Since the final child is positive,

    h ≤ log(n₀)/log(N/(N−1)).                             (5)

The exact root coupling is essential. If an actual invocation establishes
`n₀≤e`, `w=ceil(e^(1/250))`, and fixed q,N,Q and source data, then (5) makes
2^h polynomial in e. Since e≤w^250, (4), the retained prefix sizes, and any
fixed number of these operations are bounded by a fixed polynomial in w.
For fixed q≥3 this polynomial is uniformly O(q^(w−1)): the ratio tends to
zero and has a finite maximum over the remaining positive integer widths.

That is the valid absorption implication. It is **conditional on this exact
root-size coupling and the actual number of invocations per charged fibre**.
The completed `.0034` label generator and its root map are not supplied by
this package. Without such a map one must keep (4), or assume explicitly
that its ratio to the proposed fibre allowance is uniformly bounded. A
bare bound 2^h times a polynomial cannot be absorbed if h already consumes
all of the exponent w log₂q and no further slack is proved. The producer's
own invoice and the number of coefficient preparations also remain charged.

## 7. Evidence and limitations

The executable tests use genuine encoded Program and Fields tapes, the
specialized source matrix/word routines, and the same four continuation Tape
identities across reentry. They prohibit runtime Word.inspect and new Tape
construction, observe pending demand before Arena.zero's guard, and compare
with a separate integer oracle on small structured source catalogues. Larger
dimensions cross the historical 64-field and 128-label boundaries. A field
contains N² entries even when the algebraic example has a sparse projector.

These are finite corroboration and failure-detection tests. The source-site
proof supplies the arbitrary-depth/dimension statements. None of the fixtures
is claimed to be the actual selected `.0034` catalogue or an admitted current
producer. The new specialization is a concrete format-matching numerical
consumer, not a literal finite transition-table lowering of it or an executed
join to #6903's `ready` PC. The borrowed field format is the same; an actual
port join must still implement the symbol-code interface and continuation.

## Open next questions

1. Generate the exact completed `.0034` catalogue and chronological Good/Pair/
   Unit Program from its actual controller/strictification construction, then
   prove that every label and preparation meets this consumer's domain.
2. Prove the root-size map n₀≤e and the number of coefficient invocations for
   that source. This decides whether (4) is absorbed by the claimed fibre
   budget, instead of merely by an unrelated exponential.
3. Install the fixed slot inventories and four reusable stacks in an actual
   varying-precision bank. Charge all retained ancestor prefixes, source
   copies, producer STATE/PREFIX roles and caller restoration. Per-call (1)
   is one input to this obligation, not its proof.

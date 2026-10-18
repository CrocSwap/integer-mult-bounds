# Independent certificate for the fixed-cover P104 support cut

The universal pooled cut reported by dcharb78 in PR3182 survives independent
reconstruction, including source acquisition before same-layer relay. Among the
4,992 nonzero entries of `C = I - G/2`, precisely `(Y71,X102)` is absent from the
necessary relaxation on all 2,309 compatible endpoint pairs. Its required
coefficient is `-1/2`.

This independently checks an existing exclusion. The cut, its 1,725/37 cone
sizes and the missing coefficient belong to PR3182. This package adds an explicit
support-inclusion proof, a separate implementation using only three frozen JSON
inputs, complete relation comparisons with literal binary-frame enumeration,
early-write checks and rejection controls. It imports no predecessor executable
or reported result. It is a scoped proof and finite certificate, with no new
supplier, lifetime floor or kappa.

## Contract and conclusion

Fix the 208 departure slots and 208 arrival slots from Nick Petalas's PR2981,
with source and target paths from the original P104 channel. Departure `a` has
line `L[a//2]` and plane `A[a]`; arrival `b` has seven-flat `B[b]` and target
hyperplane `H[b//2]`. A compatible edge satisfies `A[a] <= B[b]`. A chosen
matching assigns one arrival to each departure.

Each added helper follows a single increasing nested flag through

```
0, L[a//2], A[a], F3, F4, F5, F6, B[b], H[b//2], FULL.
```

Transport may skip intermediate dimensions. The proof grants those missing
intermediate frames for free. Scalar operations are linear and may combine
registers only at equal current binary frames. X is immutable, Y is unread and
receives additive increments; the original channel contributes its unchanged
`G/2` map. Helpers enter with independent arbitrary dirt and no X dependence.
Original channel helpers, extra correlated storage, source mutation, target
feedback, frame descents and cross-frame mixing are outside this contract.

Under this contract, no choice of matching, nested helper flags, timing or
scalar coefficients supplies the required correction. In fact, even granting
one virtual helper for every compatible edge simultaneously leaves the
coefficient of X102 in the Y71 increment zero. Independent dirt and any
subsequent restoration cannot create that missing coefficient. This does not
exclude changed covers, changed helper contracts, added storage or an altered
original channel. It is not a complete multiplication theorem.

## Why one contact per dimension is a necessary relaxation

At dimension d, the allowed helper frames are the singleton L, A, B or H at
dimensions 1, 2, 7 or 8. At dimensions 3 through 6 they are all d-flats in
`[A,B]`. Join two virtual helpers when their intervals admit a common d-flat.
Permit each source to be read at every equal frame on its entire frozen path,
ignoring real time. Permit each target to receive at every such frame. Also grant
all direct X-to-Y equal-frame contacts.

For intervals `[A,B]` and `[D,E]`, a common d-flat exists exactly when

```
A <= E, D <= B, dim(A+D) <= d <= dim(B intersect E).
```

Necessity follows from containment. For sufficiency, extend a basis of A+D
inside B intersect E. The interval implementation checks this using subspace
cardinalities. The literal implementation enumerates all quotient subspaces
of `B/A`, a five-dimensional binary space, and groups helpers by their actual
allowed frame. Their complete eight adjacency relations agree, as bound by the
per-layer SHA256 values in RESULT.json.

Let `S_h` be the set of source indices previously reachable at helper h and
`R_h,d` its granted reads at layer d. Seed every helper with `S_h union R_h,d`,
then take exactly one graph step, including the self edge. Accumulate every
resulting source at every granted target writer. This is the implemented
recurrence. It retains all sources; it never stops at the first output source.

To prove necessity, expand any nonzero coefficient into a dependency path
through the actual linear program. Along that path, dimensions cannot decrease.
Within one dimension, a monotone helper has one fixed actual frame. Every scalar
step preserves that frame. Therefore an entire same-dimension run has one common
frame, and its first and last helpers have a direct edge in the relaxed graph.
Replace the run by that single edge. If it begins with a source read, read-first
seeding includes the read before the edge. Target accumulation occurs after the
edge. A path that remains in one helper uses its self edge. Increasing transports
use the free carry from one dimension to the next. Initial independent dirt has
no source coefficient. Direct source/target paths are separately included.
Dimensions zero and nine cannot carry a source into a target, since X starts at
one, Y ends at eight and dimensions cannot decrease.

Thus every legal coefficient path embeds into this layered recurrence.
Cancellation can remove paths, but cannot produce a coefficient without one.
The same proof holds after pooling compatible edges, because every matching
embeds by its selected edges. Choices of intermediate frames and temporal order
are relaxed further. A reachable coefficient would establish only a necessary
test, with no construction or price implied.

Connected-component closure is a different, weaker test. Two consecutive
possible contacts can require different frames at their middle helper. Its
whole component need not share an actual frame. The small controls exhibit
this case and exhaust all actual equal-frame assignments for three registers
in F2^3. In an actual assignment the equal-frame components are cliques, so
one step already carries every same-dimension path.

## The finite cut, including early writes

RESULT.json retains all 104 output support masks, every layer's relation hash,
the complete dimension-five forward edge list and the complete dimension-six
backward edge list. All indices are zero-based.

X102 has 16 possible initial readers and no granted reads after dimension one.
Its forward reached-edge counts at dimensions 1 through 8 are
`16,25,52,365,1725,2283,2285,2297`.

Y71 has two writers at dimension five, twelve at dimension eight and none at
other dimensions. Neither dimension-five writer receives X102. The backward
cone through dimensions eight, seven and six has 37 edges. It is disjoint from
the 1,725 forward edges after dimension five, so no dimension-eight write can
receive X102 either. There is no direct X102-to-Y71 contact. The complete
all-source replay independently checks all earlier writes rather than relying
only on this late cut. All other 4,991 required entries pass this relaxation;
that is not a realization of those coefficients.

## Reproduce

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-pooled-cut-independent
```

The registered replay runs interval and literal contact construction, compares
each complete receipt and runs seven small behavioral groups. Direct commands
also work without Git or network, with this package and its three declared
inputs at their relative paths:

```sh
python3 -I -O -Werror -B research/p104-pooled-cut-independent/verify.py
python3 -I -O -Werror -B research/p104-pooled-cut-independent/verify.py --literal
python3 -I -O -Werror -B research/p104-pooled-cut-independent/test_verify.py
```

Both modes must print `PASS_P104_POOLED_CUT` with 2,309 edges and one missing
required entry. `--emit` prints the checked receipt before the success marker.
Acceptance checks use exceptions and remain enabled under Python optimization.
Controls exhaust the F2^3 interval criterion, all 4,096 actual three-frame
assignments, fresh same-layer reads with two source coordinates, the difference
from component closure, invalid bases/dimensions, duplicate JSON keys, altered
source hashes and altered coefficient geometry. The two full modes share source
parsing, coefficient reconstruction and layered transfer; they are distinct
contact engines, not wholly independent complete audits.

Baseline main is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
SOURCES.json records exact Git blobs and SHA256 values for all three live inputs.
The selected source manifest, review and `make frontier1094-verify` obligation
are unchanged. The selected cold replay, native compilation, complete physical
invoice, all-size proof, formal-kernel and independent human review are unrun.

## Open next questions

Can a changed cover or source-access contract avoid this particular cut while
remaining affordable? First exhibit an explicit allowed X102-to-Y71 dependency
under the changed premise and explain the required additional operations.
A support path alone does not provide coefficients, arbitrary dirty restoration
or a complete physical consumer bill. Those costs remain unknown. No larger
matching search within these exact covers is justified by this result.

Family decision: finish the independent universal-cut audit and stop. This is
not another construction round. TASK.json records the precise scope, overlap
coverage and remaining question.

## Sources, credit and engineering decisions

Nick Petalas. Apache-2.0. Credit dcharb78/PR3182, exact source head
`ad848966cd62e13de5ad8d4b5169c221d74d2fcd`, for the universal cut and numerical
claim audited here. Credit commdata2338/PR3214,
`faa6323371db1c5fbb43ab04c6e00715d2328bc6`, for the output/cycle audit and
read-first control. PR3252 at `4784b71d2e0833537c9ae1e8be05ad2a6b334d92`
proves a distinct memory relaxation; it is not rerun or relabelled here.
Retain Nick Petalas/2981/2996/3013/3019 for covers and optimistic matching
graphs, Arham Tahir/2997 and Ross Richardson/3032 for flag consistency,
Cinna Davis/3124 for rematching, and Rohan Arun/1972, Chafik Boukhalfa/1991,
Adam Gall/1940, Josie Elliston/1071, Ali Romman/1125 and the native/compiler
lineage credited in the frozen inputs.

Separate Before Serializing Shared State kept this package and replay outputs
in the assigned worktree/session cache, with short shared Git operations under
the common OS lock. Prove It Works required actual-frame enumeration, every
early writer and complete receipt comparison instead of trusting the archived
claim. Unslop shaped the scope and proof text.

Power of Ten inspection covers both Python files. No recursion or asynchronous
children are used. Each loop is bounded by 4,058 events, 104 ports, 208 slots,
2,309 edges, eight layers, 512 binary points, 374 intermediate frames per edge
or 4,096 small assignments. Inputs are authenticated before their geometry is
used and capped at 2 MB. Every function has fewer than 60 physical lines.
Source/receipt and geometry checks remain active under optimization.

Rule 3 deviation: Python allocates managed objects. Input bounds and the fixed
domains cap live state, including at most 357,895 helper-frame incidences at
one layer, 2,309 adjacency bitmaps and eight retained relations. This batch
checker exits after one bounded replay. A persistent service would need
preallocated storage and a separate resource review.
Rules 8/9 deviation: tests load one fixed local module via runpy and use a
bounded unittest patch for source corruption. JSON has one duplicate-key hook.
No predecessor or user-selected executable is loaded. The optimized controls
exercise these fixed targets. A plugin interface would require an explicit
static loading boundary. Strict local lint and warnings-as-errors checks are
recorded in the validation receipt; shared build configuration is unchanged.

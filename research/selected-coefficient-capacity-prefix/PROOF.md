# Capacity before successful return

This is a source-bound written proof for the unchanged PR2697 modules in
`vendor/`, head `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The successful-call
constants are credited to Nick Petalas (PR2759/2770/2778/2781) and Arham Tahir
(PR2796). We independently audit the stronger prefix implication needed by
PR2831's capacity-replay handoff. No new sharp coefficient constant is claimed.

## Domain and statement

There are two distinct arenas, with fixed digit widths at least two, positive
integer capacities C_R,C_I, and an initialized valid Ring. At entry arena j has
K_j allocated slots and L_j live slots. The live set and the duplicate-free free
stack partition the K_j slots; each free Word is erased and has head one. All
entry Words, templates, input tapes and source specifications satisfy their
pinned head, shape, ownership and representation contracts. L counts *all*
residents, including unrelated matrices, the modulus, Ring.one, the coordinate
and suspended callers. K may exceed L because erased arrays remain allocated.

Use dimension m=64, good rank 1..42, an admitted odd prime power, canonical
residues/high digits, legal fixed 64-dimensional source/preparation tables,
chronological encoded programs and fields, legal requests, and the source's
arithmetic/index margins. Provider/specification access and instrumentation
allocate no numerical Words and do not alter arena metadata. No concurrency,
external Word construction, resizing, mutation of frozen source or host-language
allocation failure is covered. This retains the predecessors' semantic domain,
but **does not assume sufficient numerical capacity or a successful completed
reference execution**. Actual selected-catalogue membership is not proved here.

For `numeric.selected_coefficient`, define the numerical prefix demand of an
arena at an allocation request to be its live-slot count **plus the requested
one slot**, even when `Arena.zero` is about to reject. Under these domain
conditions, on every prefix before the first noncapacity error, demand is at
most the following, measured above L at closed-call entry:

| Branch | Residue demand | Index demand |
| --- | ---: | ---: |
| adapter | 37,672 | 22 |
| delegated child | 20,494 | 22 |

The same bounds contain ordinary live states between requests. A normal nonunit
return `Ring.inverse -> None` is included in its calling phase; it is not an
exception or an assumption that every attempted pivot is a unit. Error unwinding
allocates no numerical Words. We do not assert it always completes safely.

Consequently capacities `C_j >= max(K_j,L_j+B_j)` prevent a first numerical
inventory failure in either branch, up to any separate semantic/host failure.
For the caller satisfying every other success/termination contract, numerical
capacity is therefore not an additional missing premise. This is a quantified
capacity guarantee for the closed coefficient subroutine, not a proof that the
whole selected caller meets its other contracts or succeeds.

## Prefix composition rule

A local effect `(P,N)` bounds the number of additional requested/live Words on
every prefix by P, and has net normal-return live change N. For a callee
returning N fresh outputs, the contract also preserves all borrowed residents. Sequence composes
by `(max(P_1,N_1+P_2),N_1+N_2)`; alternatives take the largest applicable peak.
A loop whose completed iterations restore its numerical baseline does not
multiply P by the number of iterations. If an iteration intentionally retains
scalars, count the actual bounded number already retained *before* the next
allocation. List prefixes cannot exceed their full planned length. Aliased
lists/views contribute no new numerical Word. Serialized copies on other tape
types are outside this numerical count, and their later pop is charged anew.

These rules are proved by splitting a finite prefix at its last completed
component/iteration. They need only the verified effects of components that
have already returned. For an incomplete component use its own prefix effect,
not a hypothetical successful future return. The requested slot belongs in P
before executing `zero`; erasure/free never allocates. Thus a source-site proof
using these rules cannot omit the very request that would hit a capacity guard.

## Primitive and matrix effects

The live sets of the pinned arithmetic routines give prefix peaks: unsigned
division four, modular add/subtract two, negate three, multiply/literal four,
inverse ten. Division retains scan/quotient/remainder and one replacement;
each replacement frees its predecessor before the next digit. Multiplication
retains scan/result while modular addition requests at most two. Inversion
retains four Euclidean Words, the returned quotient and remainder, then invokes
multiply with those six still present. Each completed iteration frees four old
Words and restores the four-Word invariant. Initialization prefixes and a
nonunit's final disposal fit. These are structural induction statements, not
consequences of terminating finite examples. The original arithmetic premises
are used to exclude invalid arithmetic transitions; no capacity premise is used.

Matrix inverse holds at most `2d^2` augmented-row Words plus ten primitive
scratch; the identity rows alias the right half of those rows. Each replacement
has its old value charged until the source free. Matrix multiply charges its
whole output plus four scratch. Callback.prepare holds at most `4m^2+10`
residues above its entry, including its high matrix: header/palette production,
preparation constants, matrix products, and projector inversion are sequential.
Palette size is bounded by m^2; output construction is charged while the palette
is still resident. Prefixes of a fixed-dimensional allocation loop are bounded
by the completed planned matrix size, even if that allocation never completes.

Good-form accumulation owns `S=2mr-r^2` pivots/row/column scalars, including
zero-valued scalars. Its successive residue prefix bounds above the borrowed
projector are `3m^2+S+10`, `4m^2+S+10`, `5m^2+S+10`,
`5m^2+S+4`, `5m^2+mr+S+4`, `5m^2+2mr+S+4`,
`5m^2+2mr+S+3`, and `6m^2+2mr+S+10`. This charges each currently partial
matrix by its full capacity, and bounds already retained scalar prefixes by S.
Hence `G(r)=6m^2+4mr-r^2+10`; it retains `m^2+S` on normal return.

For fallback with n=2m=128, column j has j(n-1) retained scalar Words.
Failed unit candidates free all inverse temporaries. The pivot phase is at
most `n^2+(n-1)^2+10`; row update and determinant phases fit
`n^2+n(n-1)+5`. Their maximum at m=64 is `F=8m^2-2m+5=32645`.
The final diagonal aliases existing entries. This numerical constant is not
exported to arbitrary smaller dimensions: the pivot term can then dominate.

## Serialized evaluator invariant

At each `Callback.weight` loop boundary, continuation operands are serialized,
and the previous expansion's numerical matrices and scalars have been freed.
A VALUE pop materializes two indices. CONSTANT/MULTIPLY/PAIR materialize one
tagged residue each; value pops add one residue each. The largest scalar-only
PAIR phase has three operands and ten inverse scratch, at most thirteen.
A nonunit-reset VALUE processes one projector/reduction, then serializes what
is needed and frees its matrices/pivots/diagonal before the next request.
Pending depth therefore does not accumulate *numerical* Words.

A VALUE expansion's six indices are level, coordinate, parent, child, f and
slot. Good division requests four more. Pair address construction and the
halved unit step are smaller. The complete evaluator prefix effect is
`(5m^2+10 residues,10 indices)`, retaining one residue. The serialized stacks
can grow with depth and are not included in this numerical result.

## Closed-call composition and corrected child extension

The adapter's phase bounds (residue,index) above closed entry are:

- Callback construction: `(12,15)`; retained callback owns `(2,6)`.
- Current projector preparation: `(4m^2+12,11)`.
- Good construction with projector and callback: `(m^2+G(r)+2,7)`.
- Fallback construction with projector and callback: `(m^2+F+2,7)`.
- Adapter evaluation: at most `(9m^2+13,22)` for the fallback form; a first
  numerator can coexist with the second bank's evaluator.

Every constructor prefix, retained result, nested primitive and requested
replacement is already counted. At m=64,r<=42 their maximum is `(37672,22)`.
On normal return closing the form/callback frees everything except the result;
on rejection the catch/abort/rollback paths only free or clear existing state.

The child branch holds the parent Callback while extending the program, then
holds both parent and leaf Callbacks during leaf evaluation:

| Phase | Residue prefix | Index prefix |
| --- | ---: | ---: |
| Parent construction | 12 | 15 |
| Program extension | 2 | **11** |
| Leaf construction with parent | 14 | 21 |
| Leaf.weight with both callbacks | `5m^2+14` | 22 |
| Optional negative inverse | 15 | 12 |

**Correction to PR2796's extension row.** After dividing final_size by64 and
freeing its remainder, `children.extend` retains f. In the halved unit branch,
`raw.divmod(f,two_index)` then requests four additional index Words while the
six parent indices remain live. Thus the peak is `6+1+4=11`, rather than ten.
The other extension branches fit ten. f is freed before new_depth is allocated;
copying the serialized program allocates no numerical Words. The correction
does not change the complete branch maximum 22. `independent.py` provides a
literal isolated witness: L_I+10 fails, L_I+11 succeeds in extend. Primary
`verify.py` separately observes the same eleven-demand prefix inside the closed
child coefficient. The source code is unchanged.

## Excluding the first inventory failure

Suppose a first failed `zero` exists before any other error. All earlier
completed allocations/frees preserve the canonical arena partition. If the
free stack is nonempty, the source reuses a slot without testing capacity, so
this cannot be that failure. Otherwise all K_t currently allocated slots are
live. Failure requires `K_t >= C`. But the proved requested demand gives
`K_t+1 <= L+B <= C`, a contradiction. Entry feasibility also requires `C>=K`.
This reasoning is separate for each distinct arena and allows arbitrary
canonical warm free-slot order. It does not posit a completed reference trace.

The same accounting and the allocator induction yield numerical backing at
all completed allocation boundaries at most `(max(K,L+B)+1)(b+2)` per arena,
including the permanent template, LEFT and RIGHT positions and erased slots.
An in-construction array is covered by its pending allocation reservation.
This is a component of retained storage, not a Python heap or physical-tape
space bound. PR2831 already proved the general allocator identity; the added
result here is its source-bound noncircular coefficient prefix premise.

## Evidence boundary

The written argument covers arbitrary legal finite program depths, word widths
and admitted values in the stated domain. Finite tests corroborate it and
exercise actual quota guards; they do not exhaust programs or catalogue classes.
Independent means a separate AI source derivation and separately built witness,
not an independent human review or a formal proof kernel.

Full `Consumer.apply` demand, directory/payload/count/program/continuation
storage, physical placement/movement, all-size recursive grants, stronger H2,
outer transfer and selected-supplier admission are still separate obligations.
No exponent saving, selected-record change or universal exception guarantee
follows from this result.

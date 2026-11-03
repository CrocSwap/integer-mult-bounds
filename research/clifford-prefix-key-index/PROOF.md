# Bounded compact keys for exact Clifford prefixes

This contribution was produced by Nick Petalas. Apache-2.0.

## Claim and boundary

The new construction prepares exact Clifford prefix-state cache keys with
O(LG) work per request, where L is the circuit length and G bounds the cost
of freezing, hashing and comparing one gate. It makes no recursive calls.
The retained recursive implementation presents L(L+1)/2 gate occurrences
to complete-prefix cache keys and copies L(L-1)/2 gate references into
prefix slices on a completely cold length-L request. These are key-preparation
counts, not total interpreter running-time bounds.

For every valid retained circuit with 1 through 9 address bits, at most 512
gates, and a valid input basis index, the new evaluator returns exactly the
same Gaussian numerator vector and common power-of-two denominator as the
retained dense compiler specification, and as the sparse evaluator whenever
that recursive evaluator completes. Gates are the retained P, D, C, X and scalar-phase gates.
Their matrix shape, invertibility, quadratic consistency and C sign are the
retained compiler's input contract. There is no claim for malformed gate
objects or arbitrary Python objects. The bounded public entry checks dimension,
basis index and circuit length. Circuit mutation between calls is allowed.
Calls and cache clearing are serial within one process.

This is a scoped implementation-preservation proof. It does not prove a
supplier's scientific claims or a multiplication theorem. In particular,
the inherited all-column statement in the native receipt remains a source
claim, not a new theorem discharged by this implementation change.

## Stable names for prefixes

Within one cache epoch, give every created node a new positive integer ID.
A root key is `(0, ('root', n))`. A child key is `(parent_ID, frozen_gate)`.
The interner compares the complete key, so ordinary hash collisions do not
identify different keys. Its OrderedDict stores at most 8,192 entries.

For the proof, associate every issued ID with its mathematical prefix.
A new root denotes the empty circuit at dimension n. A new child denotes
its parent's prefix followed by the supplied gate. Returning an existing
interner entry preserves this meaning. Evicting an entry never reassigns
its ID. Thus different IDs can denote the same prefix, but one ID cannot
denote different prefixes. No semantic lookup through an evicted parent
is required: its meaning remains an invariant of the issued ID.

The prepared-path cache has 512 entries keyed by `(n, frozen_circuit)`.
Each value is the tuple of IDs of all L+1 prefixes. Such a tuple remains
valid after any interner eviction, because issued IDs retain their meaning.
Before the counter could reach 2^63, `clear` empties the interner, prepared
paths, state cache and gate tables together. A request creates at most
L+1 <= 513 IDs, which is the counter guard used before preparation.
Consequently no old ID can be reused while an old path or state survives.

## Exact states and invalidation

The state cache has at most 512 entries keyed by `(prefix_ID, basis_index)`.
Its values are immutable sparse Gaussian-integer pairs and a denominator
exponent. The empty-prefix state is the requested basis vector.

`step` retains every gate branch from Ali Romman's sparse prefix evaluator.
The verifier compares these branch ASTs literally. P permutes addresses;
X applies an XOR address change; D and scalar phase rotate Gaussian pairs;
C applies the retained two-address numerator formulas and increases the
common denominator exponent by one. These algebraic operations therefore
preserve the meaning of the represented state at every step.

The only normalization change is a bounded loop. If the old exponent is d,
the retained while-loop can divide all numerator coordinates by two at most
d times. The new loop has exactly that iteration bound, breaks on the same
first odd coordinate, and performs the same divisions and decrements.
It therefore yields the identical normalized sparse vector and exponent,
including zero states and d=0.

For a request, search its prepared path backwards for a cached state with
the same basis index. If none exists, begin with its empty-prefix state.
Apply `step` to the remaining gates in order. Induction proves every inserted
state and the returned state correct. Eviction changes reuse, not correctness.
The returned dense list is new; its coordinate pairs and all cached values
are immutable. Mutating that list cannot alter a later result. Freezing the
current gate values on every request makes changed circuits acquire the
appropriate complete-circuit and child keys. No operator-identity shortcut
can hide a mutation.

## Key cost and fixed bounds

A cold recursive request visits complete circuit keys of lengths
L,L-1,...,0. Their total gate occurrences are L(L+1)/2. Each nonempty
recursive call also constructs a slice of length one less, for a total of
L(L-1)/2 copied gate references. For the measured CPython 3.12.15 build, tuple hashing visits each element
and a non-full tuple slice constructs the selected reference array. See
[the version-pinned tuple source](https://github.com/python/cpython/blob/e848e4b09ca4bc67c0041c9ce7526dae471d4c36/Objects/tupleobject.c)
and [the LRU wrapper source](https://github.com/python/cpython/blob/e848e4b09ca4bc67c0041c9ce7526dae471d4c36/Modules/_functoolsmodule.c).
EXTERNAL-SOURCES.json records their exact bytes. The structural counts do
not count every hash invocation or machine instruction.

The new implementation freezes L gates once. On a prepared-path miss it
interns one root and L children, each with a scalar parent ID and only one
gate. On a hit it reuses the path tuple. Backward state lookup and remaining
state insertion use scalar ID/basis keys and at most L+1 probes. The fixed
maximum dictionary sizes bound collision scans independently of L. This
proves O(LG) key preparation. It does not bound gate execution by O(LG):
sparse state operations, gate-table construction and the rest of the native
compiler retain their actual costs. Cache policies and extra ID indirection
can make total execution slower, as the recorded experiment demonstrates.

The construction bounds node entries by 8,192, prepared paths by 512 of
length at most 513, and cached states by 512 with at most 512 Gaussian pairs
each. A valid C gate increases the maximum absolute numerator coordinate by
at most four, so at most 512 such gates give coordinates of at most 4^512
in absolute value before normalization; denominator exponents are at most
512. Valid source matrix entries have nine-bit masks. Frozen scalar phases
in the exercised source and controls have bounded integer size. These are
finite verifier resource bounds, not a fixed-memory native implementation.

## Measured boundary

The complete current native component still builds all 2,941 map recipes,
208 main adapters and 1,124 helper normalizers, checks the signed Pauli
images and absolute phases, and exercises the existing wrong-phase rejection.
Its unchanged receipt hash is checked on every measurement and registered
replay. No recipe acceptance is cached.

Two predeclared five-pair experiments are retained. The first rebuilt every
prepared path on every request. The second added the bounded prepared-path
cache. Neither demonstrates a complete-component speedup on this host.
The ranges overlap, and these timings cannot establish a universal slowdown.
The claimed improvement is the key-preparation bound, with a negative
answer to the measured full-component performance target.

## Implementation deviations and unrun obligations

Power of Ten rule 3: CPython allocates integers, tuples and dictionaries.
The finite capacities and arithmetic bounds above constrain live algorithmic
data. Python allocator internals were not instrumented. A fixed-storage
implementation is required before using this in an allocation-prohibited
runtime; this command is not such a runtime.

Rules 8 and 9: the runner loads the nine fixed, hash-authenticated predecessor
files and the explicit compiler fork using source compilation and ordinary
module dispatch. A fresh temporary bytecode namespace prevents stale bytecode
from replacing imported package source. The bounded `functools.lru_cache`
wrapper dispatches only the prepared-path function. The verifier's rejection
helper calls six explicit finite rejection actions. No externally supplied code
or callback is accepted. Revisit these choices before adding a plugin or an
unbounded execution interface.

The depth check additionally executes 512 gates with an explicit Python
recursion limit of 256. The retained cold recursion raises RecursionError;
the iterative evaluator returns the exact identity state. This is a
controlled stack-budget example, not a claim that 512 gates fail at the
default recursion limit. The 257 cold requests of lengths 0 through 256
also check the exact cache-miss and compact-node construction counts.

The unchanged predecessor baseline still uses recursive prefix evaluation;
it is retained only as the comparison implementation, with length at most
512. The new evaluator is nonrecursive. Source compilation, warning-strict
normal/optimized execution and AST preservation checks supply diagnostics.
No standalone Python linter is configured, and no repository-wide configuration
is changed. Native physical realization, compiler/caller admission, precision,
stock, fixed tapes, analytic recovery, selected cold replay, Lean and independent
human or proof-kernel review remain outside this result.

# Exact native replay with shared prefixes

## Claim and scope

The word is PR6453 at `b1a3e525793eca35c56324aa7ffd0b714cf606d4`.
The complete native component has 2,941 distinct chart maps, 208 main
adapters and 1,124 helper normalizers. Its recipe payload hash is
`4649372e3e86cee6f427df503fc64c32a7e3ae5ebb2b6e7302cb86521656dba9`.
This package changes exact state evaluation. It keeps every native check
and reproduces the entire native receipt. It does not change the word,
invoice, caller, kappa or selected frontier.

## Immutable sparse prefix states

The retained compiler evaluates a circuit as Gaussian integer amplitudes
with a common denominator 2^d. Each gate is linear. Therefore a state's
exact value after a prefix depends only on the dimension, initial basis
index and complete ordered prefix. The cache key includes all three.
Every nested gate coefficient is converted to an immutable tuple.

Induct on prefix length. The empty circuit is the specified basis vector.
A permutation or translation changes addresses. A diagonal or global
phase rotates each integer pair by a power of i. For a C gate, partition
the union of the support and its translate into pairs {x,x xor q}. Read
both input amplitudes, with zero at absent addresses, and apply the two
retained Gaussian-integer formulas. Remove only exact zero pairs. Divide
common powers of two exactly as in the retained evaluator. Each gate
therefore returns exactly the dense retained vector and exponent.

The cached state is an immutable tuple of nonzero address/amplitude pairs.
`zero_state` returns a fresh dense list, so a caller cannot change a cache
entry through the return value. Eviction discards only a computed value;
it does not change the recurrence. The fixed 512-entry cache contains at
most 262,144 amplitude pairs for the actual nine-bit native domain, plus
keys and the separate bounded gate tables. This is a space bound on cached
amplitudes, not a byte-level process-memory claim.

The gate tables retain Charles Bethin's PR662 implementation. Wentao Li's
PR2329 supplies the production-use precedent. The new prefix cache and
sparse pair recurrence extend that approach. The retained native checker
already used sparse states; it keeps credit for that representation.

## Independent Gray-order action tables

The independent native checker keeps its own implementation. It imports
no compiler table helper. Its prior action function recomputed each binary
matrix product or quadratic phase at all 512 addresses. The replacement
visits addresses in reflected Gray order. At step k, bit ctz(k) changes.

For a linear permutation, toggling bit i changes the image by XOR with
column i. For a quadratic phase

    f(x) = sum alpha_i*x_i + 2*sum_(i<j) Q_ij*x_i*x_j modulo 4,

the same toggle changes the phase by

    (+alpha_i if x_i=0 else -alpha_i)
      + 2*parity(neighbors_i & x) modulo 4.

`neighbors_i` contains every other index paired with i in the upper
triangle of Q. The quadratic sign for a one-to-zero toggle has the same
residue modulo four. These recurrences start at zero and visit every
address exactly once. They give the exact original table. The P gate now
reads this table instead of recomputing its matrix product for each live
amplitude. No signed Pauli result or equality decision is cached.

## Complete checks and controls

AST comparisons prove that the compiler forks change only Op.zero_state.
The native driver changes only its explicit C,V parameters and removes
its two implicit source imports. The independent checker fork changes
only action and the P address lookup. All native rank, signed Pauli,
absolute-phase, helper and wrong-phase checks remain.

The state conformance test checks every basis index at dimensions one
through six, both C signs and all four scalar phases, plus all 512 basis
indices in a nine-bit circuit. All amplitudes and denominators are compared
with the original evaluator. The Gray-table check compares 32 permutation
and 32 quadratic gates at every address: 32,768 exact entries. It uses a
fixed seed to choose fixtures; the all-input argument is the recurrence
proof above, not a claim that those finite fixtures are exhaustive.

Changed circuit phases, all basis indices, dimension changes, returned
list mutation, and eviction exercise the cache key and ownership rules.
The complete candidate native replay then checks all 2,941 maps and all
208 adapters against the separate native checker and the retained receipt.
The original wrong-phase rejection also runs. Normal and optimized modes
must return identical scientific results.

## Performance evidence

BENCHMARK.json records three alternating fresh-process pairs. Each process
runs the complete native component. The baseline already has the PR662
gate-table optimization; the comparison does not reclaim that earlier
speedup. Every process must reproduce the same complete native receipt.
The timing includes Python startup and source authentication. Profiling
and exploratory runs are excluded. Timings depend on the host and are
not an acceptance gate.

This package provides an explicit isolated evaluator fork. It does not
replace files in a source tree or patch imported classes. Adoption in a
complete candidate verifier needs an explicit dependency change and that
caller's full replay. The complete PR6453 compiler/outer suite, physical
native execution, a proof kernel and independent review are not supplied.

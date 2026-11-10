# Exact uniform two-capacity completions

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: a scoped written constructive proof with exact finite corroboration.
Given an injection h:U→W over a prime field and two arbitrary simultaneous
capacities `g(A)⊂C`, `g(B)⊂D`, this package constructs a bijection between
integer ranks and every admissible invertible extension g. Sampling a uniform
rank therefore constructs an exactly uniform extension. A finite fair-bit
interface reports exhaustion explicitly and is exactly uniform conditional
on success.

The new step answers the uniform-sampling opening in
[Ali Romman's PR6539](https://github.com/CrocSwap/integer-mult-bounds/pull/6539).
Its exact two-capacity count is a cited premise, not a result established here.
The construction handles overlapping, nonnested source and target spaces and
arbitrary prescribed images. It retains the coupling in every conditional
count. [PROOF.md](PROOF.md) gives the theorem, inverse algorithms, bit law and
operation bounds. The self-reduction and entropy-recycling methods are
classical; no general literature-priority claim is made.

For N admissible maps and a budget of b independent fair bits, the sampler's
exact exhaustion probability is `(2^b mod N)/2^b`. Every map has the same
success probability. On an unlimited stream the expected bit count is below
`ceil(log2 N)+2`, with exactly `log2 N` bits when N is a power of two.
An encoding or decoding path uses at most `1+(n-dim U)q^n` calls to the cited
count oracle, including initialization. It does not enumerate the `q^(n^2)`
complete candidate matrices. This remains exponential in n; no polynomial
runtime or measured speedup is claimed.

## Exact finite evidence

The new decoder and encoder agree with independently enumerated, ordered
matrix sets on 2,118 admissible endpoints in 1,954 contracts. The full small
part has 1,940 contracts and 1,342 endpoints. It includes every ordered pair
of source/target subspaces and every normalized fixed rank over F2 in
dimensions 0, 1 and 2, and F3 in dimension 1. The other 14 contracts contribute
776 endpoints over F3/F5 in dimension 2 and F2 in dimension 3, including
nonnormalized prescribed images, coupled capacities and empty sets.

There are ten additional rank/unrank round trips in two dimension-eight
contracts, with endpoint constraints checked directly. These are selected
ranks, not an exhaustive dimension-eight census. Their ambient cardinalities
are outputs of the cited oracle, not new independently enumerated counts.

The bit checker exhausts 24,564 bit strings for 132 cardinality/budget pairs,
N=1,...,12 and b=0,...,10. It checks exact equality of every output frequency
and the exact exhaustion count. For the six binary 2×2 invertible matrices,
all 256 eight-bit strings give 42 occurrences per matrix and four exhausted
strings. Fourteen rejection controls exercise bad ranks, singular or illegal
maps, nonprime fields, noncanonical vectors, resource limits and empty sampling.
Both ordinary and optimized execution retain these checks.

These checks test the new construction's output and distribution. No
predecessor scientific suite or selected cold replay is run.

## Reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/two-capacity-uniform-codec
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/check_research_commit.py --package research/two-capacity-uniform-codec --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/two-capacity-uniform-codec/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/two-capacity-uniform-codec/verify.py
```

Another CPython 3.12 installation may replace that local interpreter path.
Each registered scientific command has a 120-second timeout. Optional
`--receipt /absolute/scratch/path.json` writes a generated receipt outside the
checkout, bound to the hashes of every package file. Default replay writes
only stdout. No hand-authored receipt is supplied.

For a direct API example, put this package on the Python import path:

```python
from codec import Codec, Contract

codec = Codec(Contract(2, 2, (), (((), ()), ((), ()))))
matrix = codec.unrank(4)  # Matrices are tuples of standard column vectors.
assert codec.rank(matrix) == 4
matrix_or_none, bits_used = codec.sample((1, 1, 0, 0, 1, 0, 1, 1))
```

## Sources, credit and limits

The immediate dependency is Ali Romman's PR6539 at
`96c63f994af628f574c71dca0d7ed219cbfc70c2`. Its proof text and NOTICE are
retained verbatim, authenticated by SHA256 and Git blob digests, and attributed
in [SOURCES.json](SOURCES.json). They were obtained from that immutable public
head. Its relative NOTICE pointers refer to the original package. This
checkout does not contain that head as a Git object, so the generic
source-history check authenticates the main-based provenance; it does not
certify the external head's ancestry. The standalone verifier authenticates
the retained external bytes. No predecessor source code is imported.

Credit ToikY / PR6535 for coupled quotient feasibility, Ali Romman / PR6533
for general simultaneous-capacity rank counts and construction, Nick Petalas /
PR6489 for the nested count, Brian / JoyboyBrian / PR5020 for the original
one-capacity contract, Cao Yifan / intqwq / PR4610 for the caller context,
Nick Petalas / PR4919, codyw912 / PR4735, and the retained Cinna Davis,
Dugongue, zxv and Jacob Alan Sussman lineage. These predecessor theorems and
classical linear algebra are not claimed as new.

The executable enforces n≤12, prime q≤31, q^n≤4,096 and at most 4,096 supplied
bits. The abstract reduction works over every finite field with an ordered
element representation and exact count oracle; extension fields are not
implemented. The function can report entropy exhaustion, and an empty
completion set is an error for sampling.

Python uses managed allocation within these finite input limits. The code has
no recursive calls, hidden random source or unbounded retry loop. Field
inversion, arbitrary-precision integer operations and the standard dataclass
mechanism are managed-runtime deviations from fixed-allocation low-level
rules. Checks use ordinary exceptions and remain enabled under `-O`.

This is an unrestricted GL interface. Native or symplectic realization,
signed phase, actual contacts, physical scalar/basis costs, causal access,
dirty restoration, precision, stock, tapes, compiler and the complete outer
invoice remain unproved. All five selected assumptions remain. There is no
new kappa, supplier admission, full multiplication theorem, or proof-kernel
verification. Independent human and formal proof-kernel review are unclaimed.

The publication base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. `formal-interface-lemma` has changed scope to this constructive
finite-field prerequisite. Its baseline binding command passed; this does not
replay or strengthen the selected supplier.

## Open next questions

1. Can a direct sampler realize the predecessor's quotient/lift factors in
   polynomially many field operations? Begin with the common injection and
   its prescribed quotient discrepancy. Uniform choices of compatible lifts
   must retain the exact branch multiplicities; a feasibility witness alone
   does not give a uniform distribution. This would remove the q^n factor.
2. Can one actual shared native contact use a sampled completion with a
   favorable complete bill? Specify its exact bases and chronology first.
   Symplectic or signed constraints, legal access and physical realization
   are blockers; an unrestricted GL sample does not meet them automatically.

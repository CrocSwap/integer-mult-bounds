# P104 affine-complement lemma in Lean

Lean checks the geometric implication used in Nick Petalas's
[PR2920](https://github.com/CrocSwap/integer-mult-bounds/pull/2920), exact head
`b9ea9def949f9d71d59e21294d0e6cfbe0692a73`. This is independent proof coverage
of an existing lemma, not a new endpoint bound, correction circuit or kappa.

Let V be a binary vector space, D a demand set and f,q linear functionals.
Assume q(x)=1 for every x in D. Then

```text
D intersect ker(f) and D intersect ker(f+q)
are disjoint and their union is D.
```

If f vanishes on some demand and does not vanish on another, both f and f+q
are nonzero. In finite dimension their kernels have codimension one.
For dimension eight they are genuine dimension-seven subspaces. For a finite
D, the two intersection cardinalities sum exactly to |D|. Choosing a
maximizing f is unnecessary for the partition theorem; maximality only
identifies PR2920's first cardinality as its previously computed b.

## Formal statements and finite binding

[AffineComplement.lean](AffineComplement.lean) contains eight named statements:

- `complementary_tests`, the pointwise binary identity;
- `kernel_partition`, disjoint coverage for arbitrary sets;
- `split_forms_nonzero`, the two nontrivial linear functionals;
- `kernel_codimension_one`, using Mathlib's existing dual-space lemma;
- `eight_dimensional_cover`, the dimension-eight specialization;
- `finite_partition_counts`, the finite cardinality identity;
- `even_point_counterexample`, overlap without the odd-section premise;
- `zero_form_counterexample`, a full kernel without a nontrivial split.

The embedded audit checks every theorem in the package namespace, including
five compiler-generated proof helpers. All thirteen declarations use only
`propext`, `Quot.sound` and `Classical.choice`. It rejects package axioms,
`sorryAx` and any other axiom dependency. The proofs use kernel reduction,
not `native_decide` or an external proof oracle.

[verify.py](verify.py) separately reconstructs the 104 arrival and 104 departure
residual sets from the frozen PR1972/1991 word and ordered root fixture. It
checks their rank eight, endpoint containment, odd functional, nontrivial
split, two 128-point kernels and disjoint exact demand coverage. Each orientation
has 4,656 residual demands. The combined census is:

| Demand size | First part | Second part | Endpoints |
| ---: | ---: | ---: | ---: |
| 36 | 24 | 12 | 24 |
| 44 | 28 | 16 | 48 |
| 45 | 30 | 15 | 16 |
| 46 | 29 | 17 | 48 |
| 47 | 30 | 17 | 48 |
| 48 | 30 | 18 | 24 |

The binary integer encoding represents vectors by nine bits, functionals by
bit parity, and functional addition by XOR. Restricting to each endpoint
hyperplane gives the eight-dimensional space in the Lean theorem. This
encoding and the source-to-residual reconstruction are an explicit mathematical
correspondence, **not a Lean proof of the Python extractor**. The finite checker
is a separately implemented corroboration, not new mathematical coverage by
itself. [RESULT.json](RESULT.json) binds its complete census and witness digest.
The price optimization in PR2920 is not formalized or rerun here.

## Reproduce

Finite premises and their three behavioral test groups, Python 3.12+:

```sh
python3.12 -B scripts/research_package.py --package research/p104-affine-complement-lean
```

This opt-in replay is Git-free after metadata checking and needs no Lean.
It does **not** check the formal proof. Its tests cover a positive fixture,
missing odd/nontriviality premises, source and typed receipt corruption, and
optimized source-export execution.

For the proof, provision the repository's existing pinned environment once:

```sh
cd formal/lean
lake exe cache get Mathlib.LinearAlgebra.Dual.Lemmas Mathlib.Algebra.Field.ZMod Mathlib.Data.Finset.Card
cd ../..
python3.12 -I -O -Werror -B research/p104-affine-complement-lean/check_lean.py
```

The checker requires official Lean 4.21.0 at compiler commit
`6741444a63eec253a7eae7a83f1beb3de015023d`, Mathlib
`308445d7985027f538e281e18df29ca16ede2ba3`, and all transitive Git pins from
`formal/lean/lake-manifest.json`. It authenticates the environment configuration,
checks dependency checkout heads, discards inherited Lean search paths, and
compiles a fresh temporary proof copy. It writes no proof objects into the
package and downloads nothing. `--formal-root PATH` can reuse another checkout
with exactly the same configuration and dependencies. Compiled library caches
and the official compiler remain trusted; the checker does not rebuild Mathlib.

Five controls must reject: the wrong complement predicate, dimension eight
instead of seven, an incomplete proof, an injected custom axiom and a missing
audit command. The last control isolates the required success-marker guard.
Expected final marker:

```text
PASS_P104_AFFINE_FORMAL_CONTROLS rejected=5
```

The dedicated [workflow](../../.github/workflows/p104-affine-complement-lean.yml)
provisions the pinned Lean/Mathlib environment and runs these formal checks.
Hosted execution is separate from local evidence. Local Linux x86_64 runs of
both checkers and all controls passed with CPython 3.12.15. Ruff and
warning-as-error Python compilation passed. No independent human review is claimed.

## Scope, credit and open next questions

Task `p104-side-correction` is **changed** to a formal-audit side result because
live PR2920 already supplied the separate endpoint geometry and price analysis.
Base main is `90a72fb3739bfe4e8b8148a8f3dd7de876cfb022`, priority revision 5.
[Task metadata](TASK.json) records source heads, the chooser nonce, canonical
claim and stopping rule. [SOURCES.json](SOURCES.json) pins every live input.
Frozen predecessors and the selected frontier remain unchanged.

Credit Nick Petalas/PR2920/2909/2896 for the geometric lemma and residual-count
analysis; Hiroki Kumazaki/PR2889/2353 for endpoint spans and the monotone
contract; Arham Tahir/PR2675/2682 for the cost-relaxation context; ywz65/PR2614
for later-readable source handling; Sagar Thakrar's mixer handoff; and Philippe
Van Velzen's relay work. Retain Rohan Arun/PR1972, Chafik Boukhalfa/PR1991,
Adam Gall/PR1940, Josie Elliston/PR1071, Ali Romman/PR1125 and the geometry/native
lineage. The dependency-audit pattern is adapted from Ali Romman's
`research/cyclic-schur-lean/Audit.lean`; Mathlib supplies rank-nullity facts.
Nick Petalas. Apache-2.0. Substantial AI assistance is disclosed in TASK.json.

### Open next questions

The remaining question is PR2920's joint flag/acquisition handoff. Can an
affordable complete helper collection actually acquire and deliver the required
coefficients in chronological order and restore arbitrary dirty state? First
specify one actual joint dependency assignment and respect the existing mixer,
endpoint and cut bounds. Separate endpoint covers do not supply such a program.
Its physical owners, routing, idle work, precision, all-size lifting and entire
consumer bill are still missing. This package finishes a proof audit and stops;
it neither admits a supplier nor justifies a construction campaign.

## Engineering limits

Build the Lever shaped the rerunnable proof and mutation checker. Prove It Works
required kernel checking, actual source premises and rejecting controls. New
Python functions are below 60 lines. Loop domains are fixed by 4,058 events,
208 endpoints, 512 vectors, 48 demands per endpoint, at most sixteen dependency
pins and five proof mutants. Lean invocations have 90-second timeouts.

Power of Ten deviations: Python's managed allocations are bounded by those
finite domains and 2 MB input-file limits; no fixed-capacity runtime is claimed.
Importlib in the tests loads exactly the package's own verifier. Lean tactics,
Mathlib and the namespace dependency audit use trusted metaprogramming; the
resulting proof terms are kernel-checked and the audit's failure paths are
exercised. Replacing those runtime mechanisms would require a separate checker,
not changes to frozen sources. No full selected cold replay, native P104 replay,
rounding/circuit semantics or multiplication theorem is checked.

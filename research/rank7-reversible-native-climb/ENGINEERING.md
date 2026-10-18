# Engineering and verification decisions

The engineering-mode hillclimb predicate was a strict reduction in literal
CNOT count against a specified physical-shift C lift, while preserving the
actual A13 Gaussian endpoint, quarter grid, signed format and clean return.
The count is deterministic, so measurement noise is zero. One isolated
mechanism attempt replaced four physical HALF/DOUBLE instructions per C pair
by shifted source reads. The exact saving was 209,920 CNOTs at 69 bits.
The independently checked endpoint and tariff passed, so the attempt was kept.
No plateau search or broader construction round was needed.

Build the Lever led to the retained native-dispatch generator and gate
recount. Prove It Works led to actual bit-gate execution, native source
binding and negative controls rather than a scalar identity alone.
Power of Ten guided the bounds and contracts below. The append-only
`decisions.tsv` records the task choice, experiment and publication gates.

## Scope and resources

Only this new package is changed. Frozen predecessor sources are live inputs
with complete SHA256 and Git-blob pins. No source archive, selected record or
shared compiler is edited. Both provider compilations run serially in one
external session-owned directory. The registered command has a 600-second
process-group timeout and the behavioral suite a 120-second timeout.

New code has no recursion, service loop, retry, network request or executable
code generation. Field inventories are at most 2,048, signed width at most
256, program length at most 12,000 macros, executed gate count at most
8,000,000, and an individual packed C circuit at most 100,000 gates.
The actual uniform native domain uses widths 8 through 133.
The packed truth domain is fixed at widths 3 through 6, at most 262,144
columns and at most 1,048,576 tested four-tuples before the parity filter.
Permutation construction is at most 1,024 iterations per monomial.
Sparse operator support is at most 16 complex entries per row.

Every changed function is below 60 physical lines after formatting.
Executable `require` contracts remain active under optimization. They check
source hashes, legal scalar instructions, indices, arities, divisibility,
signed microstates, exact endpoints, ownership, complete permutations and
clean return. A run mutates a private copy of its input state; failure does
not partially update caller data. All file handles are scoped by Path APIs.
Primitive gate targets are explicit, and source-preserving ADD endpoints
are checked together with their source return.

## Bounded deviations

Rule 3, fixed memory. Python and Fraction require dynamic allocation during
evaluation. The scope is this finite verifier, not a deployed steady-state
service. Input, support, width, program, gate and truth-column caps bound live
collections. Only one provider/fixture runs at a time, the packed truth domain
is consumed one width at a time, and output directories have a single owner.
The registered timeout bounds runtime separately. A native production compiler
would need its own allocation and physical storage proof.

Rule 8, metaprogramming. Source loading uses importlib for two fixed local
module targets after authenticating all declared inputs. It does not generate
Python code or accept a user-controlled import target. The retained predecessor
compiler has its existing implementation and assertions, unchanged and rerun
under the nonoptimized command. Its validation is not claimed as new code
compliance. Replace this loader only if the repository introduces a common
authenticated source-loader interface.

Rule 10, diagnostics. The package runs with `-W error`, optimized behavioral
tests, Ruff E/F/B/SIM/UP checks and Ruff formatting. No diagnostics are muted.
The project does not require an additional Python type-checker for this scoped
standard-library research package. Hosted CI and local results are reported
separately in CHECKS.json. Reproduction does not need Ruff or any new dependency.

# Finite research-tool constraints

This package uses engineering-mode's autonomous-run playbook, Build the Lever,
Prove It Works and all ten power-of-ten inspections. The kept scope is the exact
local residue-domain reduction, not a runtime optimization or supplier release.

1. Structured flow. New code has no recursive call cycle. CLI exits propagate
   ValueError or subprocess failure. Temporary exports use context-managed
   directories and restore permissions in finally before cleanup.
2. Finite loops. Public rank inputs are exact integers in 1..7. Per block N<=128,
   real dimension d<=256. The primary index calculation restricts at most 896
   parity rows, each across at most 256 columns and rows. Simultaneous checking
   retains at most 896x256 residues and eliminates at most 256 pivots. Sparse
   witness input is capped at 100,000 bytes, 256 rows and 256 entries per row.
   Full small quotient tests visit exactly 16 and 65,536 vectors. CLI child
   processes have a 30-second timeout; registered commands have 60/60/120 seconds.
3. Managed-allocation deviation. Python and Sympy allocate dynamically, so fixed
   steady-operation allocation is not claimed. Scope is bounded offline tools
   and a scalar reference. Matrices and vectors obey the above capacities; input
   components have at most 4,096 magnitude bits; exact ideal transforms allow
   the derived 4,097-bit signed-split intermediate. Wide fixtures reach 4,090
   bits and separate positive/negative limit controls reach 4,096.
   The basis-construction column coefficients grow by at most a factor of two
   per nontrivial constraint, and ideal numerators by at most two bits per stage,
   giving a conservative 2,000-bit coefficient bound at these ranks. The modular
   method stores residues below 16. Low-bit triangular reduction has the README's
   conservative 1,053-bit intermediate bound. Temporary exports are scoped and
   removed on success/failure. A future variable-rank or production implementation
   must replace these offline controls with its own storage/cleanup proof.
4. Cohesion/size. Each new function is checked against the 60-line review ceiling.
   Matrix restriction, exact stages, certificate parsing and fixture groups are
   separate responsibilities. No compatibility layer or persistent registry is added.
5. Invariants. Explicit need checks enforce rank, shape, signed magnitude,
   exact division, prefix parities, Hermite shape, lattice index, residue bounds,
   source digest and typed receipt equality. They remain enabled under -O.
6. Ownership. Basis/vectors are local owned arrays, without shared writable
   caches. Only the generator writes, to a caller-supplied new output file.
   The replay reads committed evidence and never regenerates it in place.
7. Contracts/results. Zips require equal length. Subprocess return codes, timeout
   and stderr are inspected. JSON sizes, integer types and sparse index order
   are checked. Internal functions consume validated basis/vector shapes; they
   are not a general untrusted matrix API. File/parse/I/O failures fail the CLI.
8. Restricted code loading deviation. The verifier compiles and executes one
   fixed vendored Python reference only after checking its SHA256 and exact
   predecessor-head pin. It does not use external data as code or read bytecode.
   This preserves the unchanged original floor word for literal comparison.
   Ordinary new modules use standard imports; registered replay owns a fresh
   bytecode namespace. A future alternative oracle must retain equivalent source
   binding. Sympy HNF generation is optional and mathematically untrusted.
9. Shallow calls. New algorithms use direct local function calls and flat
   integer/list matrices. The pinned module has one bounded known target for
   its kernel and wrapper methods. No callbacks, runtime registries or concurrent
   writers are introduced. The general equation is a pure integer identity;
   no physical uncomputation or dirty-memory restoration is inferred from it.
10. Diagnostics. Run Ruff E,F,I,UP,B,SIM,RUF on new Python files, warnings-as-errors
    compilation into an external cache, ordinary and optimized registered replay,
    behavioral controls and publication-byte comparison. No warning is suppressed.
    The unchanged vendored reference is source-authenticated and exercised, not
    reformatted or expanded into a predecessor-wide cleanup. Its original loops
    are bounded here by fixed validated fixtures of at most 512 Gaussian addresses.

The exact commands and local environment are in TASK.json. These runtime and
source-loader deviations do not assert full compliance with fixed-allocation
or no-dynamic-execution platform requirements. A production/native replacement
must eliminate those deviations or supply its own reviewed constraints.

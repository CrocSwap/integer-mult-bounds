# Complex kernel with paid residual adapters

Conditional **κ = 0.001274032589159993**, **0.591885% above PR454** at
`d14eb0dd425bd681e3b43f208d089e679d600176`.
The complex lower endpoint is `0.001297203880559577927527`; the unchanged
PR454 bit endpoint `0.001275657818793753037875` now binds.

PR449's shared-donor kernel has 79 isotropic rank-one entrances. Such an
entrance cannot be orthogonally identified with a coordinate axis. This
package instead gives each residual explicit, paid Gaussian monomials
before and after the complete local call. Their exact product turns the
residual into a coordinate C factor and restores its spectator axis.
There are no uncharged helper entrance transforms.

To make that physical construction valid, at most one helper occupies each
host family within an invocation. A new frozen assignment hosts all 49,280
complex helper occurrences under this restriction in the eleven-stage
dimension 89 schedule. All residuals remain whole. The9,600 live families,
10,178 physical families and 20,161 row allowance are unchanged.

The uniform operator and borrowing proof is in `PROOF.md`. It explicitly
separates the paid two-sided adapters from orthogonal cover-class routing.
The kernel is reconstructed by exact rational elimination; no discovery
optimizer is required for verification. Both800-column orientations,
2,932 phase edges,14 nontrivial adapter frames, all 49,280 owner/route
instances and 25 global mutations are checked. The fresh finite invoice
charges 788,480 extra rank-zero compiler groups conservatively.

## Reproduce

Python 3.11+, SymPy, a C++17 compiler and Boost headers are required:

```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
E8_REPLAY_PHASES=1 python -B research/e8-complex-adapted-kernel/verify.py /tmp/complex-kernel-new
```

The output directory must not exist. Set `BOOST_INCLUDE` when needed.
The verifier rebuilds PR454 and its complete parent chain, runs the default
local-program regression, reconstructs the kernel, regenerates all new
phase recipes, validates the adapters, emits and independently audits the
global program, and recomputes both moment engines, invoices and 47 strict
outer inequalities. `--quick` skips only inherited PR443 exhaustive controls.
Every new check runs in both modes.

The package manifest, upstream source inventory and exact expected results
are mandatory. Generated canonical words are bound by their decoded
canonical JSON so gzip container differences do not alter the operator
identity across Python versions. Frozen source bytes remain individually
hash-pinned. Receipts record completed checks, modes and source hashes.

The two inherited floating-point discovery estimates are finite provenance
metadata, normalized to the frozen report before exact word comparison.
Their numerical agreement is not a proof condition. The verifier tests
2.1e-12 perturbations independently, rejects nonfinite estimates, and rejects
changes to exact gates, register counts or unrecognized report fields.
This fixes the Python 3.11 portability failure reported by PR460; the operator,
kernel selection, exact prices and expected result remain unchanged.

## Scope

The new paid adapter and distinct-host argument is supplied here. The
inherited all-size Gaussian/bit compilers, mutable-basis realization,
restored work, compressed geometry, fine-grid precision, row-divisor and
analytic transfer contracts remain conditional. No cross-family residual
split or entrance-gauge construction from PR449 is used. This is neither
an unconditional multiplication theorem nor a κ=1 result.

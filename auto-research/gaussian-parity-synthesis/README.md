# Parity integration with the community network

This package combines Alejandro Zarzuelo Urdiales's PR45 arithmetic with the
mixed-center producer, copied-center and phase endpoint interfaces retained by
PR46 at `71b6c960c89295e952522dd44111df9cfc51ae90`.

The concrete result is a working **integer-only common-frame scalar decoder**
with a complete producer-image guard, plus a sharper completed-child precision
certificate. The paper is `community-parity-synthesis.pdf`; all source and Lean
proofs are included.

## What improved

- Subtract dirty old/new auxiliary values before exact division. On the actual
  producer image, `sum delta B - 2 sum delta D = -32 T` and each `delta B/2` is
  exact. Collect center, disjoint and intersection-two terms before halving:
  the completed numerator is `2 X`. This uses **zero additional fractional
  bits**, compared with six in the explicitly compared generic old/new scalar
  reference schedule. It needs 3,286 rather than 26,268 Gaussian quotient calls
  in those schedules. These counts omit the optional full image check, which
  adds a producer pass; they are not runtime or optimality claims.
- `checked_fused_delta` checks `P(Q delta)==delta`. This rejects inputs outside
  the complete producer image even when local exact divisions happen to pass.
  `image_conditioned_fused_delta_fastpath` requires an existing producer witness.
- The actual 29-class complex child list has an all-width completed-child
  binary precision charge at most `211345564248*f`, replacing `421548223824*f`
  for that component: a **49.8644% reduction**. The scalar `E`, unfinished
  recursion, total memory/tape costs, and normalized output remain separately
  charged. The multiplication exponent is unchanged.
- `pi_exact.py` supplies canonical Gaussian dyadics with minimal `(1+i)` tags,
  heterogeneous-tag alignment, total butterflies, phases, and dyadic halving.
  Independent controls exercise the actual weight-nine paid endpoint formula.
- `GaussianTensorExecution.lean` formally executes the recursive forward and
  inverse C tensor at **every dimension**, with explicit denominator tags.
  It proves coordinate restoration, binary-grid conversion, and sharpness
  using an actually executed impulse. This closes the earlier written-only
  link for that finite tensor algorithm; physical tape compilation is separate.

## Run everything

Requirements: Lean 4.31.0 and Python 3.10+ standard library. No SciPy, C++
compiler, external math library, network access, or upstream checkout is needed
for the delivered standalone checks.

```sh
lake build
python3 verify_phase_endpoint.py
python3 verify_precision_profile.py
python3 verify_mixed_center_image.py --output work/image-audit
python3 verify_adapter.py --dag work/image-audit/mixed28.bin
```

`make verify` performs these checks. PowerShell users can run `./verify.ps1`
with `lake` and `python` on PATH. The PDF can be rebuilt with Tectonic.

The vendored PR46 source files retain their copyright/license notices and are
checked against `SOURCES.json` **before import**. To audit the original checkout:

```sh
python3 verify_mixed_center_image.py --upstream /path/to/pinned/pr46 \
  --output work/image-audit
```

This also checks its Git HEAD. Modified pinned files are rejected.

## Use the scalar interface

`read_dag` and `check_image` load and independently certify the generated
producer. `numeric_roots` is its exact scalar producer `P`. Its ports include
the disjoint and all pair-star side values; center ports alone are insufficient.

Given old ports `a` and updated ports `a+P(X)`, use
`checked_fused_delta(graph, a, a+P(X), roles, triples, h, d)` to recover `X`.
See the executable examples in the audit.
It operates on `(real_integer_numerator, imaginary_integer_numerator)` pairs.
Gaussian dyadic values must first be expressed at the **promised common input
grid**; the result retains that grid. The guarantee is not that arbitrary
fractional physical values become integers.

`mixed_center_adapter.py` performs this bridge directly on canonical
`pi_exact.Gaussian` values, with an explicit `grid_tag` promise. Its audit uses
the real producer with heterogeneous source and dirty tags, recovers canonical
input representations literally, and restores canonical dirty values.

All ports must be in **one common scalar phase frame**, including side ports.
Matching old/new phases separately within each role is insufficient. Transport
and align physical streams before applying this interface, and charge that
work. The delivered executable does not implement or prove those transports.

## Verification and scope

The source-pinned scalar audit regenerates the actual h28,d19 producer,
independently checks its 78,437 active additions and 13,132 ports, and verifies
all 10,732,176 source/target coefficients using exact integer arithmetic. Six
dirty-input/output trials cover every target. Controls reject off-image ports,
locally divisible non-image ports, missing side corrections, mismatched
snapshots, incoherent cross-role phases, and altered source files.

Lean checks the local arithmetic and generic image-interface theorems;
`FORMALIZATION_MAP.md` distinguishes these from the finite producer linkage,
Python refinement controls, and physical normal-form/tape arguments. `AuditAll`
prints the dependencies of every theorem. The only allowed dependencies are
standard Lean foundational axioms. No omitted proofs, project axioms or
`native_decide` are used.

The upstream repository's full `make verify` was **not** rerun. The package's
passing standalone checks do not prove the full multiplication theorem,
analytic/recovery premises, physical compiler, fixed-tape schedules, or a new
complexity exponent.

`LEDGER.md` and `ledger.json` cover all 46 PRs in the start-of-run inventory,
with their pinned heads and 5,380 cumulative changed-file records. This is a
source inventory, not a claim that every community build was executed locally.
`IMAGE_PROOF.md`, `FRAME_REVIEW.md` and `REVIEW.md` provide the implementation
proof and independent review boundaries. Authorship and prior work are in
`PROVENANCE.md`.

# Gaussian parity certificates for integer-multiplication networks

Prepared for Alejandro Zarzuelo Urdiales on 8 October 2026 with AI-assisted
research and formalization. This line began in an earlier Archivara exploration
and was subsequently developed personally by Alejandro with multiple AI tools,
most recently GPT-6.1 as recorded by the author. See [PROVENANCE.md](PROVENANCE.md)
for the research history, AI-assistance disclosure, dependencies, and credits.
This package contains the paper, two checked Lean modules, exact finite controls,
and verification records.

## Main insight

For the actual synthetic phase butterfly C = (i I + X)/(1+i), the legal
integer-division predicate is equality of the inputs' Gaussian residues
(real + imaginary) modulo 2. The completed D-axis C tensor needs exactly
ceil(D/2) additional binary fractional bits universally, with an extra parity
constraint at odd D. The normalized Hadamard tensor still needs D bits.

One retained defect bit reconstructs all four local half-integer coordinates
from their integer floors. An unchecked change of pairing can invalidate the
next local division. The total algorithm therefore aligns denominator tags
and retains an extra denominator whenever the parity guard fails.

## What is formally checked

DyadicCertificates.lean checks the exact division predicate, Gaussian parity
rules, C's square and inverse, shared defect reconstruction, total fallback,
fraction equivalence, and denominator alignment.

GaussianLattice.lean checks the even/odd ideal hierarchy, constructive binary
conversion for every denominator exponent, arbitrary-depth sharpness, and the
odd-normalization product cancellation. AuditAll.lean prints every theorem's
axiom dependencies. The source has no omitted proofs, project axioms, or
native_decide. Dependencies are Lean's standard foundational axioms only.

The written tensor coefficient formula and its connection to an actual
recursive network are not formalized as a complete tensor-network execution
theorem. They are supported by the paper's elementary derivation and independent
exact finite controls. No tape-cost theorem, full multiplication theorem,
new kappa, or runtime improvement is claimed.

## Reproduce

Use Lean 4.31.0, with its bundled Std library. Mathlib is not required.
The included Lake project can be checked with `lake build`.
In PowerShell, inside this directory:

    ./verify.ps1 -LeanExe /path/to/lean.exe
    $env:LEAN_PATH = (Get-Location).Path
    lean AuditAll.lean
    python verify_exact.py

On a POSIX shell:

    export LEAN_PATH="$PWD"
    lean -o DyadicCertificates.olean DyadicCertificates.lean
    lean -o GaussianLattice.olean GaussianLattice.lean
    lean AuditAll.lean
    python3 verify_exact.py

The Python audit requires only the standard library. verification.json
contains its expected result. kernel-check.log and axiom-audit.log record
fresh checks of the delivered sources. `lake-build.log` records the complete
default-target build, and `repo-unit-tests.log` records 188 passing tests from
the destination repository. Its full `make verify` is a separate generator and
integration check; it was not run locally for this standalone submission.
manifest.json records SHA-256 hashes
and pinned research sources. The paper's LaTeX source is standalone.

## Proposed integration

Use the certificate at exact C-kernel divisions and completed child-return
boundaries in the community's semantic precision note (PR23). Keep existing
internal magnitude/depth bounds, arbitrary-scratch assumptions, and final
normalization. Uniform guarded buffers can keep the local predicate as an
assertion; any adaptive re-encoding or alignment must pay for scans and copies.

Gaussian denominator arithmetic is established prior work; cite
Amy, Glaudell and Ross (Quantum 4, 252, 2020), section 5.4. The contribution is
a checked specialization and audit contract for this multiplication interface.
The proposed submission is a self-contained audit component for the community
repository, with source, paper, exact controls, provenance, and explicit limits.

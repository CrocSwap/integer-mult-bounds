## Result and why it matters

The current normalized Gaussian recovery channel requires compact,
original-order S fields. Canonical GAUSSIAN already states that the
original q-image is monotone, but that prose algorithm and the older
CoreAssembly boundary do not by themselves supply a literal controller
for the full padded q+3-bit field returned by the newer interface.

This package implements a fixed-inventory encoded controller for that
precise boundary. For dyadic `t_i=2^ell_i` with `s_i<t_i<2s_i`, it selects
`floor(t_i*j_i/s_i+1/2)` on every axis, with axis zero fastest, copies
exactly S framed records, and reads the entire T-record input. Arbitrary
hole values are preserved on the borrowed input and excluded from the
output. The grid, numerical error bound and Gaussian restoration are
unchanged; the later codec and native scalar recovery remain separate.

## Exact claim and complete invoice

The proof establishes the encoded remainder successor, packed tensor
odometer, dyadic bit-concatenation address, increasing full scan, fixed
tape inventory, ownership and complete costs. No host coordinate list,
sparse RAM, variable tape inventory, stride table or free cardinality
clock is used. Preparation constructs T and S from the encoded source
packet using actual Count operations.

With `n_addr=log2(T)`, the complete boundary invoice is
`O(n_addr^3 + log(q+1) + T(q+n_addr))` time and
`O(H_borrowed+Sq+n_addr+log(q+1))` backing, where H_borrowed counts
complete historical borrowed capacities. This includes rewinds, setup, copying,
cleanup and simultaneous input/output retention. For the source fine
family's `n_addr=Theta(p0)`, `q=Theta(p0)`, time is O(Tp0); backing
is O(Tp0) under explicit bounded-history admission. Borrowed ports enter
at origins or their initial displacement is charged separately.

## Source pins and novelty

- Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
- Current normalized recovery: CubeJerry/integer-mult-bounds commit
  `1ab10aa78c4b27345c76806d1d32c7b9de481219`.
- Retained sequential B carrier: public bridge
  `73d5adaba2b7dc662e86eb901e81369a3f73be9f`.
- The canonical increasing-projection observation and local C/D work
  in #3851 are prior results. CoreAssembly joins already-compressed
  contiguous source cores; the new controller selects the original
  global image from a complete augmented target field.

All eight canonical input files and three retained public files have
exact Git-blob/SHA256 pins. No selected certificate or existing source
file is changed. `OVERLAP.md` delimits the bounded audit.

## Reproduction and checks

```sh
python -B scripts/research_package.py --package research/original-q-field-extraction
python -B scripts/check_research_commit.py --package research/original-q-field-extraction --check-modes
```

The normal and optimized checks authenticate sources, verify 32,385
independent direct-floor scalar coordinates and execute the actual
native Count program on T4/S3, T32/S15 and T256/S105 fields. The fixture
checks exact copied records, nonzero unrelated holes, reuse, borrowed
descriptors, immutable metadata, origins and cleanup. Negative controls
cover omitted nearest rounding, wrong axis order, contiguous-padding
substitution, invalid axis guards, truncated descriptors, short/extra/
compact inputs, malformed frames, output alias and pending return.
Expected JSON status: `PASS`.

## Limitations and kappa status

**No new kappa.** This is an actual extraction boundary and a universal
source-relative implementation proof. It supplies no production Gaussian
transform, fast Broad implementation, FFT scalar service, CRT/carry
caller, selected frontier improvement or unconditional multiplication
theorem. The production caller must still bind the original periods,
restore its gathers, deliver the complete field and establish its
actual error/radius. The five framework assumptions remain.

Prepared for @CubeJerry with substantial OpenAI assistance in source
audit, proof, code, independent exact oracle and packaging. Credit the
canonical construction, #3851, retained Tape/Count/Gaussian source
authors, the public bridge and normalized-recovery predecessor. No
independent human or proof-kernel acceptance is represented.

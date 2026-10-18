# A precise obstruction to reversible inward phase updates

For the fixed unit phase `z=(3+4i)/5` and every `p>=3`, there is **no** total
injective map of the complete closed dyadic disk `D_p` into itself that both
never increases an operand norm and approximates `zx` within `4*2^-p`.
This remains true for arbitrary nonlinear computations with any restored
helpers, when the complete helper entrance state is fixed independently of
the varying data and every other state is restored exactly.

The result identifies a precise extra return contract that cannot be inferred
from [PR2527](https://github.com/CrocSwap/integer-mult-bounds/pull/2527).
That predecessor supplies a norm/error phase kernel and does **not** promise
injectivity. This is a boundary theorem, not a defect in PR2527, a general
cleanup impossibility, or a claim against a selected supplier.

## Proof and exact source application

[PROOF.md](PROOF.md) contains the full all-precision argument. A finite
injective self-map is a permutation; if every norm can only decrease, summing
squared norms forces every norm to remain exactly unchanged. The dyadic
unit-circle shell contains only `1,-1,i,-i`, by repeated divisibility by two.
Thus the output at input 1 has squared error at least `2/5`. The proposed
error bound has square `16/4^p <= 1/4` for `p>=3`. At `p=1,2` the identity
satisfies these three conditions, so this precision threshold is sharp for
the stated `4h` contract. The standard finite-set/shell arguments are not
claimed as new mathematics; their quantified phase-interface application is
the contribution.

The unmodified pinned PR2527 kernel gives two concrete witnesses:

- For every `p>=1`, inputs zero and one real grid step both produce zero.
  The proof uses its actual inward multiplier and final truncation; finite
  replay checks precisions 1 through 128.
- At `p=3`, phase then conjugate phase executes `1 -> 1/2+3i/4 -> 3/4`.
  Both calls satisfy the original norm/error contract; the roundtrip is not
  an exact inverse. Neither the source nor this package calls it one.

The rational phase is a valid generic input to PR2527. It is **not bound to
an actual selected root phase**. PR2549's explicitly conditional private-erasure discussion motivates precise return premises; this package does
not assert that its cleanup requires inversion of the present kernel.

## Why the hypotheses matter

Two constructive controls change one relevant interface condition:

1. Keep the same inward multiplier but retain its exact product on the finer
   `2p` output grid. The map is injective, norm nonincreasing and within
   `sqrt(2)h` of this rational rotation, with an exact inverse on its image.
   Image membership and the changed output denominator are explicit.
2. Use the standard three rounded shear updates. This is exactly reversible
   on the same full integer grid, with squared error at most `(153/80)h^2`,
   but it can leave the disk: at `p=3`, `(0,8)` maps to `(-7,5)` in grid
   numerators, with squared norm 74 instead of 64. Clipping it breaks return.

These are hypothesis controls, not new rotation algorithms or free native
implementations. No precision-conversion, physical storage, routing or timing
bill is claimed.

The obstruction concerns **destructive in-place return on a fixed helper
fiber**. Retaining the original x permits `(x,y)->(x,y+F(x))` followed by
recomputation/subtraction even if F has collisions; the verifier executes
this with dirty y. A helper initially copied from x is not an independent
fixed fiber. Restricted input domains, extra outputs/history, finer grids,
or outward slack also change the premises. Merely declaring an unbounded
ambient domain does not help if the same finite disk stays invariant.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -I -O -B research/reversible-phase-disk-obstruction/verify.py
python3.12 -I -O -B research/reversible-phase-disk-obstruction/independent.py
python3.12 -I -O -B research/reversible-phase-disk-obstruction/check_integrity.py
python3.12 -B scripts/research_package.py --package research/reversible-phase-disk-obstruction
```

The first command reports `PASS_REVERSIBLE_PHASE_DISK_BOUNDARY inputs=17118
refined=17118 controls=8` and compares the typed committed [RESULT.json](RESULT.json).
`--output NEW_PATH` writes exclusively to a new file. The normal command is
read-only. SHA-256 and Git-blob source checks occur before any predecessor
module is executed. The standalone commands run in a Git-free export with
the declared selected-record input; the generic launcher also checks Git
provenance. The selected record is orientation only and is unchanged.

Every disk point at p=1,...,6 is checked against the actual original kernel,
its conjugate call, the refined-grid inverse, two-sided lifted return and a
retained-input dirty accumulator. There are 68,472 Gaussian-unit checks.
Eight semantic controls reject the additional injectivity/inverse inference,
disk closure of lifting, clipping, the wrong refined denominator, shell
preservation without injection, an illegal source input and a nonimage
refined inverse. The separate checker uses `isqrt` for 13 boundary shells,
all 120 permutations of the five-point disk (24 are contractive), and 3,969
independent rational shear residual/inverse calculations. These finite tests
corroborate the written proof; they do not establish its universal quantifiers.

The integrity command checks optimized Git-free replay, unchanged files and
eight source/typed-receipt/CLI corruptions, including authentication before
altered executable predecessors can run. Primary and independent commands
passed under CPython 3.12.14; a separate Codex agent reviewed the proof and
code and independently replayed them with CPython 3.12.7, finding no blocker.
No human or proof-assistant review, hosted CI or full selected cold replay
is claimed.

## Sources, selection and overlap

[VENDOR.json](VENDOR.json) pins exact Git blobs and SHA-256 values for five
unchanged predecessor files. PR2527 head is
`3e1e819e4d0837123a4fc05674fc1df6bde859a9`; PR2549 head is
`bd3bea4b4e09ead04355a477a7c28559427d1ef6`. The PR2527 original verifier is
loaded as a module and its actual `phase_product` and `rect_error` functions
are executed; its whole original CLI/receipt is not rerun. Mason Hale's
retained PR2313 interval implementation and notice are preserved verbatim.

Fresh canonical main was `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
The picker drew `uniform-transfer-audit`, seed
`bdc59a4c0a8cff6d62e79d5a397eb4e7`, priority revision 4, and its first
baseline command passed. TASK.json records the refined precision/restoration
scope. No selected bound or implementation is changed.

The coordinated complete overlap snapshot covered 768 open PRs at
2026-10-15 15:00:19 UTC and 1,232 Discussion records at 15:03:35 UTC. Search
terms and bounded final REST refresh are recorded in OVERLAP.json. The latest
100 updated open PRs were checked at 15:27:54 UTC; both predecessor heads
were unchanged. Coverage includes metadata and local notes, not every code
diff or closed historical PR; it is not a novelty guarantee.

Related [PR2555](https://github.com/CrocSwap/integer-mult-bounds/pull/2555)
proves full-grid reachability for arbitrary dirty rounded-shear prefixes.
It explicitly excludes bounded entrance domains. The present result instead
uses a complete finite norm-invariant disk; the shear escape is credited as
a standard method and is not the new result. Retained rounded-leaf lattice
and temporal Gaussian rounding notes address different domain/error issues.

## Open next questions

- Which selected phase/tape interface actually needs this destructive update
  on a complete fixed-helper disk fiber? Pin its phase, legal domain, output
  encoding and complete retained state first. This determines whether the
  generic boundary applies; no selected interface is identified here.
- Can a retained-input compute/uncompute interface pay the storage and
  precision needed for a strict-zero collector? First instantiate the actual
  native rounding kernel with a reversible accumulator, then price retained
  input, scratch and hosting. Those physical obligations remain open.

Credit ywz65's PR2527 and PR2549 source interfaces; Mason Hale's PR2313
quantizer/enclosures; Jose Manuel's PR2298 phase-interface context; and the
retained project lineage. New work by ywz65, with substantial OpenAI Codex
assistance in derivation, code, tests, writing and separate-agent review.
Apache-2.0; offered for independent review.

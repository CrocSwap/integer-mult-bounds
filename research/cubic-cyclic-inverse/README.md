# Cubic precision for cyclic inverses

This package reduces the growing-radix precision guard in PR628's cyclic
inverse from O(r^4) to O(r^3). It bounds each partial inverse using the full
inverse and the complementary polynomial, then bounds all rounded prefixes
together. The circle lower bound from PR621 is unchanged.

It also implements exact restoration of a coarse-grid source after in-place
evaluation. The source has owned widened words with reserved low zero bits;
their capacity is charged. Rounding the target increment to the original
grid gives signed shears that compose and cancel exactly with one fixed
precision budget for a planned word.

**No new kappa.** These are numerical-kernel and source-storage results.
The package does not supply arbitrary dirty-bit restoration, common-label
or Clifford compilation, the full transform, or a multiplication reduction.
Its concrete restored-source schedule covers neighboring cyclic layouts.

## Reproduce

Python 3.11 or later, standard library only:

```sh
python3 -I -O -B research/cubic-cyclic-inverse/run.py --out /absolute/fresh/output
```

The output directory must be new and outside this source package. The runner
checks the complete source inventory, executes both suites, and compares
all three mathematical artifacts to their committed SHA256 digests. It
writes stage logs and a receipt with integer-millisecond timing metadata.
No external checkout or untracked historical artifact is required.

Expected final line:

```text
PASS_CUBIC_CYCLIC_INVERSE budgets=5220 kernels=120 prefix_dense=60 composition=20 composition_dense=12 controls=10
```

## What is proved and checked

`PROOF.md` gives the all-length partial-inverse lemma, explicit all-radix
precision and coefficient budgets, paid preparation, and source recovery.
For source norm <=2^m, it gives

    W <= max(p,w)+12r^3+m,      factor budget b <= p+6r^3+m.

The whole word width also includes O(r^3+m) magnitude bits and the target's
initial magnitude. Phase preparation and longer phase descriptions retain
their own charges. The reference executes exact rational arithmetic with
explicit rounding; it is not a fast bit-arithmetic implementation.

The 5,220 budget cases cover all 116 prime-power radices from 3 through 512.
The 120 kernel cases use ten immutable PR628 fixtures through radix 16,
lengths 1,2,3,8,17,64, both directions and varying unit phases. Sixty check
every inverse prefix by independent dense elimination. Every case checks
the polynomial residual, recovery bound, exact source restoration and total
true-kernel error <=2^-128. These finite fixtures reuse their existing
conservative inverse-norm certificates; the cubic asymptotic conclusion
comes from the written general proof, not from fitting their measurements.

`COMPOSITION-PROOF.md` and `check_composition.py` cover six interacting
signed shears and their inverse word on three nonzero arrays: 20 cases,
12 independent dense comparisons, and exact cancellation in every case.
Ten rejection controls across both suites exercise incorrect precision,
nonshared shifts, unstable error propagation, inverse order, aliasing and
violations of the coarse-grid promise.

For p=w=128 and source norm <=1, the explicit new fractional budget is
13,913 bits at r=16, versus the older uniform neighboring-scan budget of
33,580; at r=64 the numbers are 904,401 and 8,396,390. The new bound also
pays for coarse-grid recovery, so this is a comparison of sufficient proof
budgets, not a matched runtime benchmark. At small radices its constants
can be worse. The complete tables are regenerated into the output folder.

## Provenance

`SOURCE.json` gives exact Git heads, blob IDs and hashes for the unmodified
PR621 proof and PR628 proof, scan, coefficient engine and factor fixtures.
The local inverse and source-recovery reference is new code included here.
`MANIFEST.json` covers the complete package. The standard Mahler-measure
argument is proved in the note; PR628's approximate-factorization and
elementary-function preparation algorithms remain cited prerequisites.
Credits and substantial AI assistance are recorded in `NOTICE.md`.

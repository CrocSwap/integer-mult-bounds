# Exact recovery of one prime-phase orthogonal pilot column

This tool completes any valid matrix with p rows and p−1 received columns, for every prime p. Each CSV entry is an integer phase code e representing exp(2πie/p). The received columns must be exactly orthogonal. The tool appends one column, preserves every received integer code literally, and sets the first new phase code to zero. The completed signal matrix H satisfies H*H=pI; dividing its columns by √p gives an orthonormal pilot matrix.

This is a concrete application of atlas B097 and B082: repair a missing orthogonal pilot column from exact prime-phase data. It makes no claim about communication rate, noisy-channel recovery, empirical performance or mathematical novelty. A missing entry, multiple missing columns and approximate phase measurements are different problems and are not silently accepted.

## Commands

From this folder, using Python 3 with only the standard library:

```console
python -B repair.py --input fixtures/p11-received-00.csv --output repaired.csv --certificate repair-certificate.json
python -B check.py --received fixtures/p11-received-00.csv --completed repaired.csv
python -B tests.py --report fresh-test-report.json
```

The repair command requires fresh output paths in existing directories. It rejects overwriting its input, takes per-output locks, and checks the received-file hash before and after writing. The certificate binds the input and output hashes. No configuration, network or external service is used. The independent checker imports no repair implementation: it verifies exact input preservation and counts all phases separately for every completed column pair.

The row count supplies p. Integer exponents may be negative or exceed p−1; calculations use their residues modulo p, while received codes in the output remain unchanged. CSV cells must be integers. The output contains the original p−1 columns followed by the recovered column, rather than moving it back into an erased physical slot. If the original missing column is known for a fixture, the appended column agrees with it up to one global unit phase, fixed by the first-entry convention.

## Fixtures and evidence

The p=11 fixture applies nontrivial row and column permutations and phase gauges to a Fourier phase table. Its 11 different erased-column inputs and their completed outputs are under `fixtures/`. `p11-full.csv` retains the original full table. These fixtures test actual gauges and permutations, not only an unmodified Fourier table.

`TEST-REPORT.json` records 41 successful erasure cases across p=2,3,5,7,11,13, including every erasure position at each order. All 11 p=11 cases also pass the repair CLI followed by the independent checker CLI. Thirteen invalid controls are rejected: perturbed phases, composite and empty/order-one inputs, wrong or ragged dimensions, noninteger codes, changed received columns despite remaining orthogonality, a duplicated new ray, a noncanonical new-column phase, a missing output row, and attempted input overwrite. A separate positive case preserves signed exponent representatives.

The tests establish these finite instances. The proof in `PROOF.md` establishes the general sufficient statement for every prime p. Input validation and independent output verification use integer phase histograms; no floating complex arithmetic or numerical tolerance is involved. Runtime is O(p³) and matrix storage is O(p²). Primality is checked by exact trial division.

`MANIFEST.json` binds the selected 29 source, proof, report and fixture files. Generated test workspaces under `validation/` are retained locally but are not part of the selected deliverable. The manifest itself is outside its file list to avoid a self-hash cycle.

## Attribution

The completion theorem is atlas Volume II B097, derived there from the flat orthogonal completion B082 and the classical prime cyclotomic polynomial. Fourier constructions and orthogonal completion are classical. This implementation and its independent integer-histogram checker are an application of that mathematics, not a claim of a new communications theorem or independent human review. Source code is offered under Apache-2.0; retain SPDX notices when copying it.

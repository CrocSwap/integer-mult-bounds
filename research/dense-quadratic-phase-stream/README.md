# Dense quadratic phase streams with restored coefficients

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped constructive written proof with exact finite corroboration.
For every L>=0, a supplied dense quadratic polynomial q on L Boolean address
bits, with coefficients in Z/4, can emit its N=2^L phases in binary-address
order using exactly

```text
4N - 2L - 4 residue additions/subtractions,
2(N - L - 1) quadratic-coefficient reads,
4N - 3 control events, and at most 3L + 1 pending event records.
```

The current constant and L linear coefficients return to their entry values
after iterator exhaustion. The construction stores no N-entry phase table.
The supplied coefficient matrix uses O(L^2) bits; event records use
O(L log(L+2)) bits. Input validation and linear copying add
O(L^2) abstract work. [PROOF.md](PROOF.md) proves the all-L statement.
[stream.py](stream.py) is a nonrecursive bounded reference for L<=20.

The new project result allows arbitrary Z/4 cross coefficients, including
odd coefficients, with fewer than four unpacked residue updates per emitted
phase and an explicit completed-return contract. Dugongue's
[#4538](https://github.com/CrocSwap/integer-mult-bounds/pull/4538), Theorem 2,
already gives O(N+L) packed-word phase generation for even cross coefficients.
We do not claim the first linear phase stream. The new exact bill uses
individual small residues and no packed gradient-word operations.
Ali Romman's [#5375](https://github.com/CrocSwap/integer-mult-bounds/pull/5375)
supplies the predecessor physical stream for fixed recipe dimension. Its
scientific executables and previous counts are not replayed. Polynomial
cofactoring and Shannon expansion are classical, with no literature-priority
claim here. This does not compare the new arithmetic count with the
predecessor's physical tape-action bill.

## Evidence and scope

The independent direct-polynomial expression agrees with the stream on every
coefficient choice through L=3: 16,660 cases and 132,132 output residues.
Another 72 generated fixtures at L=4..12 compare 65,408 output residues.
The zero polynomial at the L=20 capacity boundary emits all 1,048,576 phases
and executes 4,194,260 updates, with 4,194,301 events and stack peak 61.
Nine invalid-domain and six semantic/return controls pass. These counts
are enumerated by [verify.py](verify.py), which also checks three source
document hashes and emits a receipt bound to all seven package files.
The direct oracle was written with this package; it is not independent
human or formal proof-kernel acceptance.

The input tuples remain immutable at every prefix. Restoring the private
cofactor state requires complete iterator exhaustion, including the call
that observes StopIteration after the last output. Early-abandonment cleanup,
literal tape lowering, input-matrix acquisition, output rotation, affine
routing, native ownership, rounding and the complete physical caller invoice
remain open. An input table may cost more than a fixed compiled recipe.
There is no new kappa, supplier admission, selected-frontier change or
complete multiplication theorem.

## Reproduce

From the repository root with the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dense-quadratic-phase-stream
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/dense-quadratic-phase-stream/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -O -W error research/dense-quadratic-phase-stream/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dense-quadratic-phase-stream --check-modes --check-source-history
```

Both registered commands must print `PASS_DENSE_QUADRATIC_PHASE_STREAM`.
The source-pin wrapper needs Git history; direct verification also works in
an official Git-free export containing the three declared input documents.
No command writes a receipt or cache into the checkout. Environment metadata
is in [TASK.json](TASK.json). Hosted CI is separate from local evidence.

## Open next questions

- Can a fixed finite tape program realize the stream with a complete source
  access and retirement bill? Start with a triangular serialized coefficient
  layout and every access/return at L=4. No literal machine graph is supplied.
- Can one actual native recipe supply this coefficient table and consume the
  phases affordably? Pin a recipe, derive the table preparation and output
  contract, and compare the complete bill. Acquisition, storage and rotation
  are current blockers.

## Credit

Credit Ali Romman #5375 for the physical phase-stream interface; retain
Jose Manuel / jmbarrancoml #2250, JoyboyBrian #5329, Cinna Davis,
Ryanson Jonathan #4325 and the original native/Clifford lineage. Credit
Dugongue #4538 for the prior packed-word theorem and Ryanson Jonathan
#4555 for its separately published finite check. Neither checker is replayed.
[SOURCES.json](SOURCES.json) pins the unchanged predecessor context at
canonical main e54523517d0f03e58352e647c403a5af3e525a57. No predecessor
construction is used as the new main step. The exact card is retained in
TASK.json and explicitly changes scope to this algebraic side result.

## Implementation bounds

All functions are below 60 physical lines. Production loops have explicit
bounds from L<=20, at most 4,194,301 events and at most 61 pending records.
There is no recursion, generated code, subprocess, network call or output
file write. State belongs to one generator and its caller-owned meter.
Exceptions propagate; normal and optimized executions enforce the same
contracts. Direct file reads cover seven small package files and at most
three source documents bounded by one MiB apiece.

Python allocates tuples, integers and lists during execution. Validated
dimension, bounded stack and
the explicit event cap bound live state; the reference cannot accept an
unbounded input. A fixed-buffer runtime would be needed before claiming
allocation-free operation. Standard generator and SHA256 object dispatch
have fixed visible targets. Warning-strict normal/optimized execution and
in-memory compilation supply diagnostics.

# Validation record

Run on 2026-10-15, macOS 27.0.1 arm64, CPython 3.12.15, standard library only.
The scientific source base is `8e22a9d9f621c72ab5b299061c2be4c7f638fd3c`.
Before publication the isolated branch was rebased onto refreshed canonical
main `1696cf14e403b3eab35cd9eab27a4c2eb4e4ae38`. The guidance, selected record,
package runner and consumed stream source were unchanged between those commits.
All changes are confined to this package.

## Registered replay

From the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/fixed-tape-ordered-shear --check-only
python3.12 -I -B scripts/research_package.py --package research/fixed-tape-ordered-shear
```

Results: `PASS_PACKAGE_METADATA_AND_PINS` and
`PASS_REGISTERED_RESEARCH_PACKAGE research/fixed-tape-ordered-shear outcome=completed`.
The manifest registers these exact component commands, each with a 120-second cap:

```sh
python3.12 -I -B research/fixed-tape-ordered-shear/verify.py
python3.12 -I -B research/fixed-tape-ordered-shear/independent_check.py
python3.12 -I -B research/fixed-tape-ordered-shear/test_counters.py
python3.12 -I -B -O research/fixed-tape-ordered-shear/test_independent.py
```

- Sparse replay: 98 cases over 49 shapes, payloads through 4,096 bits,
  1,694,168 transitions; exact output, source immutability, complete scratch
  erasure, head contracts and both resource identities pass.
- Independent dense replay: 164 directional cases plus 15 inverse round trips,
  30 translated-origin cases, 34 authenticated source comparisons and six
  mutation controls. The 164 cases use 1,382,048 transitions; roundtrip and
  negative-control executions are additional. Both directions execute 524 of
  their 531 instructions on successful valid fixtures; rejection paths are
  exercised separately. This is not exhaustive transition-path coverage.
- Counter replay: all extents 1 through 1,024 and 1,025/2,047/2,048/4,095/4,096;
  1,029 positive cases and 13,031,310 transitions. Nine malformed/occupied-work
  controls and three alias controls pass. Source immutability and the exact
  binary-to-unary formula are checked.
- Seven optimized-Python boundary/authentication tests pass, including zero and
  noncanonical descriptors, bad payload length/alphabet, occupied work origins,
  nonlocal instructions, both source hashes and stale timestamp bytecode.

The table SHA256 is
`91100422c3975c4711dfdafb230f3f0ee5de5f657fbb767462e9618e2d0dd660`.
The primary verifier regenerates its entire canonical representation and
compares it byte-for-byte. The independent interpreter does not import any
producer, counter or sparse-interpreter code. Its coordinate oracle is separate
from the authenticated predecessor comparison.

## Export and corruption checks

The package and its single live source input were copied to a temporary
Git-free tree with their repository-relative paths preserved. The four
component commands above passed there. A SHA256 inventory of every exported
file was identical before and after these read-only commands; bytecode writing
was disabled. The generic historical-provenance checker itself requires Git;
the component replay does not.

In separate temporary copies, appending one space to TABLE.json, RESULT.json
or INDEPENDENT-RESULT.json caused its responsible verifier to fail. Appending
a newline to the live `qadic_streams.py` input caused both verifiers to fail.
The source-integrity test also rejects altered executable bytes before executing
them and proves that a valid timestamp `.pyc` cannot substitute for authenticated
source bytes. Regeneration requires the explicit `--write` commands in README.

## Overlap and scope

The initial and final paginated searches and inspected PR heads are recorded in
TASK.json. The final refresh at 21:18 UTC covers 715 open PRs and 1,408 Discussion
records, with complete pagination and no warnings. The source metadata search
excludes arbitrary diffs and unpublished work. Newly published numerical-bank
parking and the active physical-caller lowering claim are credited in README;
neither implements this ordered payload permutation.

Separate AI agents derived the same exact transition formula, examined scratch
cleanup and independently executed the exported programs. This is not external
human review or a proof-assistant check. No complete caller, selected cold replay,
H2 recurrence, outer multiplication theorem or hosted-CI result is claimed.
The all-size proof is the written invariant and exact instruction counting in
PROOF.md; finite replay alone does not establish it.

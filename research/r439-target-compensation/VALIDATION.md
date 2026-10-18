# Executed validation

Executed 2026-10-13 on Linux x86_64, against
`f567884aeb8851b6e794af1184119a3bfbe1e631`.

## Complete runs

Both full verifier runs exited zero and produced receipts byte-identical to
each other and to EXPECTED.json:

- **CPython 3.14.4**, isolated ordinary execution:
  `python -I -B research/r439-target-compensation/verify.py --output NEW --receipt NEW_JSON`.
- **CPython 3.12.3**, isolated optimized execution, launched outside the
  checkout against a **read-only minimal closure with spaces in its path**:
  `python3.12 -I -O -B /path/to/closure/research/r439-target-compensation/verify.py --output NEW --receipt NEW_JSON`.

The closure contained the executable/data package, its pinned predecessor
proof, and exactly the 14 in-tree source inputs in SOURCES.json. It had no Git
metadata or other repository files. Files were 0444 and directories 0555;
all fresh outputs were outside the closure. Native helper subprocesses run
ordinary isolated Python; the parent verifier and imported source checker
also passed in optimized mode.

Each run regenerated the exact 306-step seed-10 recipe and canonical candidate;
reconstructed all row updates with set-valued supports; re-executed **9,643,960
literal positive instructions** across all accepted partial words in both
orders; checked all **661 Boolean columns** of both D words in both directions;
and ran the unchanged full E8/frame/dirty-input checker.

For the baseline, every original interface hypothesis/conclusion is true.
For the candidate, **only H2 and direct K extraction are false**, exactly as
required by the declared semantic substitution. No predecessor predicate is
patched or silently skipped. Non-D fields are compared in full, and the actual
D boundary is independently equal to the baseline on arbitrary input columns.

The final row matrix was independently checked on all **12,210 ordered pairs**:
maximum next-shear complete-cost gain is zero. This is the stated local stopping
condition, not a global circuit optimality certificate.

## Native evidence and toolchain

Both complete words passed freshly compiled, unchanged native legality and
5/9/11-stage column checkers. Coverage per word is **883 / 1,327 / 1,549
physical columns**, with **6 / 18 / 24 omitted-bridge controls** rejected.
All MOVE paths, paid ranks and COPY/ERASE records agree between words.

The candidate has **13,208 ADDs / 16,137 records**, paid rank mass **5,129**,
forward/reverse bounds **49,347 / 9,534,616**, local payload **100 bits**, and
the source nine-stage prefix expression **189 bits**. The last expression
and its bridge exponent were checked against the pinned source AST; the
baseline reproduces its recorded 177-bit bound and 192-bit prefix charge.

Compiler: `c++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0`, `-O2 -std=c++17`, HDIM=8,
NCOPY=9, VPORTS=111, RHELP=439 and KPAIRS=2/4/5. Boost headers came from a
temporary extraction of Ubuntu `libboost1.83-dev`, `1.83.0-5ubuntu5`, archive
SHA256 `c17abc5a40a074c3d959655191ebec1561fa25f14f4948f6788be49417d4b234`.
Both commands set BOOST_INCLUDE to that extraction's `usr/include`. Every
native compile/run command and raw receipt is retained when `--output` is used.

## Controls and binding

All **14 local rejection controls** pass, including the helper-only false
positive obtained by omitting the entire entrance, missing restoration,
wrong undo order, missing injection, illegal frame/donor/destination, omitted
restoration cost, each precision guard, unrelated cleanup and typed-data faults.
A cancelling target pair has the correct semantic endpoint and is charged
exactly two extra ADDs.

All **eight package tests** pass in both environments: source alteration and
absence, duplicate keys/nonfinite JSON values, integer/boolean confusion,
different gzip encodings with identical full payloads, and refusal to overwrite
existing builder outputs, verifier outputs or receipts.

All 14 source hashes match their exact base Git blobs. The retained PR794
proof's SHA256 and Git-blob ID match its immutable API object. Canonical
full-word SHA256 values are:

```text
baseline  5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b
candidate 6aec2c6f91c87a7440af10cdeb90b8814501224a86de14d4033ae3ffa00899da
```

Regenerated gzip files are compared through every decoded JSON field, with
canonical serialization distinguishing booleans and integers. The immutable
baseline container and source files retain exact SHA256 pins.

## Scope and publication

Upstream was refreshed unchanged. Overlap checks included the full open queue,
300 recent all-state PR records, relevant predecessor bodies, and arrivals
through #912. Recent R439 block changes #906/#908 concern B; they do not replace
D. The pinned #794 method and #848 H2 barrier are credited explicitly.

Only `research/r439-target-compensation/` is added. No selected frontier,
`upstream/`, generator or default checker is changed. A full repository suite,
selected cold supplier reconstruction, hosted parent and complete finite invoice,
changed-word outer assembly and Lean multiplication theorem were not run or
claimed. In particular, the new prefix bound alone does not certify every
other invoice allocation. Hosted CI is reported separately at the published
head; these local results are not a hosted-CI pass.

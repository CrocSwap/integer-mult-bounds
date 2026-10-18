# Executed validation

Local validation on 2026-10-13 used CPython 3.12.14, macOS 26.5.2 arm64,
and only the Python standard library. The executable was the Codex bundled
Python runtime. No hosted CI, Linux run or independent human review is claimed.

The exact development base is `007664306fff84fbb1c9a1b4053b69f439764034`.
The experiment was selected and claimed by 08:12 PDT; the completed census
and candidate were available by 08:17. Subsequent work was verification,
fault controls, documentation, overlap checking and publication preparation.
The bounded experiment stopped after the declared complete length-2/3/4 census.

## Commands and outcomes

From the repository root, with Python 3.11+:

```sh
python3 -I -B research/x4-four-source-horner/verify.py
python3 -I -B research/x4-four-source-horner/independent.py
python3 -I -B research/x4-four-source-horner/test_package.py
python3 -I -B scripts/verify_selected_result.py
python3 -B -m unittest discover -s tests -p 'test_selected*.py'
```

- Primary full replay: PASS, all 16,431 candidate identities, 1,174 chosen
  boundaries, 737 arbitrary input columns, exact stream equality between
  engines, 22,048 saved backward primitives and 8,976 beyond pairs.
- Independent integer replay: PASS, all candidate prices and identities,
  separate prefix DP at caps 2/3/4, nine adverse controls, retained forward
  and both backward traces. Its default command checks 14 shared receipt
  fields without importing the primary constructor or Fraction interpreter.
- Seven package test groups: PASS in 68.790 seconds. This includes literal
  equality with PR696 on all 38,394 source macros, 216 signed/denominator
  triples plus quartet cases, gate-deletion and sign controls, source/frame
  boundaries, the strict quartet-versus-pairs example, an endpoint-valid but
  suboptimal greedy recipe, and DP versus exhaustive toy partitions.
- Minimal offline relocation under a path containing spaces: both full
  checkers PASS under `-I -O -B`, with all package/input bytes preserved.
  Corrupt input digest, omitted source pin and integer-to-float receipt
  mutation are rejected. These checks are in the seven test groups.
- Selected-record verification at the development base: PASS. All 17
  selected-record regression tests: PASS. The selected record is unchanged.
- Final `verify.py --emit /absolute/new-file.json`: PASS in 12.02 seconds
  wall time. Decoding/canonical hashing of the exported stream agrees with
  `EXPECTED.json`; a second call to the existing path fails immediately and
  preserves its bytes. Timing is a reproduction observation, not a claimed
  performance improvement.
- Staged whitespace and local Markdown-link checks: PASS. The patch adds
  exactly eleven files under this package and applies cleanly to refreshed
  main using a separate temporary Git index.

Expected primary line:

```text
PASS_X4_FOUR_SOURCE_HORNER candidates=16431 windows=1174 saved=22048 extra_vs_pairs=8976 columns=737 no_new_kappa
```

Candidate stream SHA256 (canonical JSON excluding the final newline):

```text
d95c2ce750263e09c1051dad011e0bb436b696424e8d98513efba09908d757a3
```

Exact input bytes, including immutable gzip archives, are source-pinned in
`SOURCES.json`. Regenerated event streams are compared as canonical JSON,
not by a compression-container hash. No source archive is regenerated.

## Refresh and scope

Before submission, main advanced to
`bbc600db2fc15007b7c914f4f2b2ed55fa909c87`, selecting Jonathan Capalbo's PR942
U8/T37 at conditional kappa `0.001661960547713947`. Its selected record and
maintainer review were read. Every one of this package's nine input files
was checked against that exact main Git object and remains byte-identical.
This is still a historical PR799 scalar construction, not a proposed T37
replacement. The base-era PR890 number is context, not the current frontier.

Recent open PRs were refreshed through #971, together with an all-state
Horner search. PR945 remains open at its recorded head. New #967 concerns
bit helper stars, #968 frame-pair decoders, #969 deferred historical swaps,
#970 bit provenance and #971 triple-decoder verification. None supplies this
three/four-source X4 construction. No savings from those passes are composed.

Full `make verify`, cold supplier reconstruction, native/hosted admission,
global invoice/assembly, rounding/tape certification and Lean verification
were not run. The only changes are in this new research package. Existing
generators, selected certificates, predecessor files and `upstream/` remain
unchanged. The reproducible exact finite evidence has the limits described
in `PROOF.md`; it is not a proof of the full multiplication theorem.

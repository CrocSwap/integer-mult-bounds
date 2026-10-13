# Whole six-wire Boolean synthesis on R439

**Finite construction; no new kappa.** Seven complete phase-A block replacements
reduce the frozen PR936 circuit from **23,711 to 23,673 local ADDs**, including
the required reverse cleanup. The new saving is **38 ADDs**; the cumulative
saving against selected PR589 is **632**, including 254 credited to Gareth
Davidson's PR904 and 340 to Ross Richardson's PR936.

| Complete local resource | Selected PR589 | PR936 input | This candidate |
|---|---:|---:|---:|
| ADDs, including D, scatter and C | 24,305 | 23,711 | **23,673** |
| Exported records | 27,234 | 26,640 | 26,602 |
| Forward positive bound | 49,347 | 41,311 | 41,287 |
| Reverse positive bound | 1,113,070 | 843,188 | 833,084 |
| Local payload bits, cap 104 | 93 | 92 | 92 |
| Nine-stage bound bits, charged 192 | 177 | 174 | 174 |
| Paid rank mass | 5,129 | 5,129 | 5,129 |
| Dirty helpers / rank-seven copies | 439 / 9 | 439 / 9 | 439 / 9 |

All original H1-H5 and their interface conclusions hold. Every register's
ordered MOVE path and every COPY/ERASE record is preserved. No helper, frame,
source-access operation, recursive call or copy is added. The decoder constant
remains 63. The complete 5/9/11-stage ADD savings beyond PR936 are
**190 / 342 / 418**, with the same paid bridges and copies.

## Reproduce

From the repository root, with Python 3.12+, C++17 and Boost headers:

```sh
BOOST_INCLUDE=/path/to/boost-headers python3 -I -B research/r439-six-wire-boolean/verify.py
python3 -I -B research/r439-six-wire-boolean/test_package.py
```

If Boost is installed in `/usr/include`, omit `BOOST_INCLUDE`. The verifier
regenerates the entire bounded search, checks the local truth tables and
positive column maps independently of the search, replays all three full words
in both directions, runs the unchanged geometry/interface checker, compiles
fresh unchanged native legality and 5/9/11-stage checkers, and compares the full
deterministic receipt with `EXPECTED.json`.

Expected final line:

```text
PASS_R439_SIX_WIRE_BOOLEAN: 7 blocks; 38 further ADDs; 632 versus PR589; H1-H5; 5/9/11 stages; 12 controls; no new kappa
```

Use `--output /absolute/fresh/path --receipt /absolute/new/report.json` to retain
native logs and the receipt. `--source-root` supports an offline minimal copy
of the exact source files in `SOURCES.json`. Outputs must be new. Regenerated
gzip files are compared by canonical decoded content, not compression bytes;
immutable predecessor artifacts retain exact source hashes.

## Completed search and novelty

The domain is all **60 complete six-wire A blocks, frames 266-325**, in the
pinned PR936 output. At each block, the search tries every permutation of six
pivots, two fixed donor priorities and two elimination modes: row-only and
mixed row/column. OS assignment seed **19** fixes the donor-priority rotation.
It completes **172,800 nominations**, with 119,983 distinct programs when
deduplicated within each block. There are 15,469 distinct shorter programs,
440 passing both positive guards, and seven blocks with an admitted nominee.
Choose the shortest admitted program, then a deterministic lexicographic tie.
One complete scan is the stopping rule; no restarts or iterative saturation.

Unlike PR904's four-wire and PR936's five-wire windows, each nomination here
replaces an entire six-register operator. Five selected replacements have a
different positive integer transfer, outside PR925's fixed-transfer search
class. PR925 proves a 12-ADD minimum for frame 267 in that class; frame 267 is
unchanged here. The two other replacements preserve their integer transfer.
This is not an unrestricted XOR optimum, a fixed point, proof that six wires
are necessary, or a claim that another five-wire pass cannot also improve
PR936. No failed nomination establishes a lower bound. The D-compensation
results PR915/926/941 and the independent B-block constructions are not composed
into this candidate.

The initial target-delivery candidate was screened out: every consecutive
same-frame B run that writes targets contains only one target. The large
same-frame B blocks write only z registers. This census only excludes that
literal grouping idea, not all target recoding or reframing.

See [PROOF.md](PROOF.md) for the finite argument and complete pricing,
[VALIDATION.md](VALIDATION.md) for executed evidence, and [NOTICE.md](NOTICE.md)
for contributor credit. No independent human review is claimed.

## Pins and remaining work

Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`. PR936 input:
`0679fb6e1e4c91f573ae07ab1d0ea273b13c74e3`; its candidate, certificate and
attribution are retained verbatim under `vendor/pr936/`. Selected PR589 source:
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`. The accepted conditional result at
this base is PR890's **0.001661957774647029**, with the same PR589 bit supplier.
Publication is rebased onto `007664306fff84fbb1c9a1b4053b69f439764034` after
the maintainer's batch932 integration; all thirteen consumed upstream files
are byte-identical across that update. The accepted frontier is unchanged.
Only this research package is added.

The unchanged paid bit profile gives no improvement to the selected moment
or exponent. If adopted, the modified word still needs binding into the
whole-hosted supplier emitter and a regenerated global invoice and outer
assembly. The native stage tests and source-bound nine-stage prefix expression
do not perform that hosted replay. They also do not prove the multiplication
compiler for every input length, realize common labels and mutable sources on
physical tapes, or discharge the inherited hosting, rounding, precision/tape
and analytic transfer assumptions. The original H1-H5 remain satisfied rather
than replaced by a new semantic D contract. No full repository suite, selected
cold complex replay, or formal proof of the multiplication theorem is claimed.

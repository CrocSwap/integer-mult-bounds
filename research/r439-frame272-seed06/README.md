# R439 frame 272: a 12-ADD circuit and the cost of reverse domination

**Finite bit-supplier construction and exact scoped minima; no new kappa.**
The complete phase-A frame-272 circuit of PR589 takes **23 ADDs**. This package
replaces it with **12**, including a literal reverse cleanup in the full word:
**24,305 -> 24,283 exported ADDs**. No helper, frame, copy, source-access operation
or recursive child is added. All 661 register frame paths and the paid rank
histogram are preserved.

The exact minima expose a useful distinction. On the same six ordered wires,
the fixed positive integer transfer needs **11 ADDs** without a reverse guard,
but **12 ADDs** when its reversed positive transfer must be entrywise at most
the selected circuit's reversed transfer. Both lower bounds are independently
recomputed. This is a minimum in a stated finite circuit class, not unrestricted
XOR optimality or a proof of the full multiplication theorem.

The research base is `407d52ff15b2217b6e22bce44728b4c3907b6515`. At that commit
the selected certificate is PR942/T37 with unchanged PR589 on PR555, conditional
`kappa = 1661960547713947/10^18 = 0.001661960547713947`. The exact supplier and
selected-source pins are in [SOURCES.json](SOURCES.json). Older frontiers in
dependency READMEs are historical.

## Reproduce

From the repository root, using Python 3.11+ and the standard library:

```sh
python -I -B research/r439-frame272-seed06/verify.py
```

Expected final line:

```text
PASS_R439_FRAME272 gates=23->12 native_adds=24305->24283 columns=661 rank_mass=5129 controls=9
```

The command regenerates the bounded nomination, independently checks both
minima, reconstructs and verifies the full finite word, interprets the actual
exported records, and rejects nine mathematical mutations. The `native_adds`
field counts exported native-format records; it does not assert that a C++
multistage checker ran. Use `--output /absolute/new/path` to keep both decoded
words and complete record streams. Existing output directories are refused.
The default uses a temporary directory and modifies no repository file.

```sh
python -I -B research/r439-frame272-seed06/test_package.py -v
```

For the unchanged native legality and 5/9/11-stage checks, install no Python
dependencies; use an existing C++17 compiler and Boost headers:

```sh
BOOST_INCLUDE=/path/to/boost CXX=c++ python -I -B research/r439-frame272-seed06/native.py
```

On Windows use an x64 Visual Studio developer shell, `CXX=cl`, and the same
Boost include-root setting. This freshly compiles the original checkers and
checks both complete words: **883 / 1,327 / 1,549 formal columns**, all **96
omitted-bridge controls**, unchanged paid resources and nonincreasing positive
bounds. The expected final status is `PASS_R439_FRAME272_NATIVE`. Only elapsed
time and temporary stream paths are removed from the compared native receipts.

`--write-certificate` explicitly regenerates only this package's certificate.
Gzip container bytes are not used to establish regenerated mathematical equality;
the receipt binds canonical decoded words and the actual record stream.

## Evidence and comparison

The object is exactly phase A `[725:748)`, frame 272, with physical registers
`[242,294,296,302,316,501]`. The original block is contiguous and has no external
observer. The replacement preserves its entire integer transfer on arbitrary
incoming values, hence its Boolean transfer on arbitrary helper dirt.

The discovery graph exhausts **868,423 states / 5,005,248 edges**. A separate
flat-matrix breadth-first implementation adapted from PR925 reaches identity at depth 11
after **798,401 states**, fully expanding depths 0 through 10. An independent
augmented pair-state traversal rules out every reverse-compatible circuit of
length at most 11 with **949,377 states**. The explicit 12-gate circuit supplies
the guarded upper bound. Budget exhaustion raises an error and cannot produce
an optimality receipt. See [PROOF.md](PROOF.md).

Gareth Davidson's PR904 reduces this same frame from 23 to 20 gates; Ross
Richardson's PR936 reduces it further to 18. Gareth Davidson's PR952 leaves it
at 18 after 1,970 distinct nominations, of which 670 are shorter and none pass
its guards. All these versions have the same positive integer transfer.
[OVERLAP.json](OVERLAP.json) retains the actual prior windows and full local
gate lists, whose algebra is rechecked. Historical PR904/952 hashes and heads
are retained provenance metadata, not newly validated source bindings. The
PR589 word and PR936 comparison word are pinned and checked as execution inputs.
Our exhaustive fixed-transfer
class provides new evidence beyond those bounded window/Boolean searches.

The final 12-gate circuit also has a reversed positive transfer dominated by
the prior 18-gate frame. Its local saving over that frame is six forward gates
and six cleanup gates. We replay the complete PR589-based word here, not a
composition with the complete PR936/PR952 candidates, and do not add their
whole-word savings to this package's result.

## Scope and validation

The original H1-H5 interface checker passes, including literal cleanup and all
661 dirty-input columns. An independent set-valued interpreter checks every
exported MOVE, ADD, COPY and ERASE, the nine copy lifecycles, final states and
paid rank mass 5,129. The 64 local Boolean inputs are also exhaustively checked.
The original forward integer transfer is unchanged and the reversed transfer
is entrywise dominated, so the corresponding positive prefix bounds carry over.

The selected frontier is not changed. The C++ legality and 5/9/11-stage checks
pass locally on both words. This package does not execute the whole hosted
invoice, outer assembly, selected cold replay or full Lean theorem.
All inherited all-size/compiler, common-label and mutable
source realization, whole-call hosting, precision/tape, analytic transfer and
bit-interface obligations remain. [VALIDATION.md](VALIDATION.md) distinguishes
the checks actually run from those remaining.

The final queue refresh also identified concurrent PR986's different frame-281
12/13 boundary and PR989's four phase-B block composition. They are separate
objects and are credited without claiming priority for the general distinction
between scalar minima and reverse-envelope admission. The Windows native runner
adapts PR989's compiler interface at its exact recorded head.

The first OS-random assignment was **6**, selecting the bit-supplier track;
`266 + (6 mod 60)` chose this phase-A frame. [CLAIM.json](CLAIM.json) records
three candidate tasks, scope and stopping rules. Live GitHub inspection found
no pinned coordination issue, so the claim was recorded locally. The final
overlap refresh is retained in [HANDOFF.json](HANDOFF.json).

## Attribution

Prepared for GitHub contributor **@woklerx** with substantial **OpenAI Codex**
assistance, including delegated circuit-search and verification agents. Ross
Richardson's PR925 supplies the predecessor exact-transfer and finite-verifier
method; Gareth Davidson's PR904/952 and Ross Richardson's PR936 supply the
explicit comparison circuits. See [NOTICE.md](NOTICE.md) for the retained
supplier and checker lineage. Apache-2.0. No independent human review is claimed.

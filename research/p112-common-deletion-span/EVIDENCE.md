# Evidence and implementation limits

## Scientific delta

PR3158 proves a twelve-line common minimum for five particular directions. It
neither classifies other directions nor maximizes the common-budget-four span.
This successor proves the sharp value three for **all** real and complex
directions at common budget four, on its two fixed spaces. The separate-set
relaxation has exactly ten projective directions and sharp span five.

The proof is in README.md; RESULT.json is a deterministic receipt. It binds no
solver output or floating-point decision. No predecessor direction list is a
runtime input. The fixture's three mathematical fields were compared verbatim
with PR3158's exact Git blob recorded in SOURCES.json.

The initial estimate that the spaces' 20 and 16 lines were disjoint was rejected
by the first exact fixture check. Their intersection has four lines, giving
union 32. This strengthens the support cutoff to 72 and reduces the geometric
coverage obligation to the E7 and D7 parabolic orbits. No incorrect union size
is used in the theorem or retained receipt.

## Checks

Recorded host: Linux 6.6.87.2-microsoft-standard-WSL2, x86_64.
Interpreters: CPython 3.12.15 and 3.13.5. Standard library only.
The proof check takes about 0.12 seconds on this host. Timings are observations,
not part of acceptance or a multiplication-runtime claim.

The registered replay runs the proof and optimized behavioral tests. The 15
test groups include:

- A separate primitive-normal reflection traversal, instead of the production
  root-mask permutation traversal. It reproduces both complete orbits, their
  sizes 120 and 1,080, and the exact 248 qualifying orthogonality systems.
- An XOR-generated evaluation code, instead of dot-product character masks.
  Its restricted code cardinalities independently match every one of the 248
  residual binary ranks.
- Literal label-span closure before and after every admitted cut.
- A rank-nine singleton control requiring two independent characters. A single
  character cannot incorrectly certify a two-rank drop.
- A separate integer fraction-free rank implementation and exhaustive cut-union
  subsets. All 794 subsets of size at most four of the twelve relevant lines
  also reproduce the sharp common span three by direct restricted-code tests.
- Rejecting mutations that drop the reflection action, accept every direction,
  or omit a qualifying direction. Malformed frame/basis inputs, Boolean-valued
  basis entries, oversized/non-object JSON, an over-capacity orbit, altered
  fixture bytes and an altered result receipt also reject.
- An optimized CLI replay in an external Git-free directory, containing only
  geometry.py, verify.py, FIXTURE.json, SOURCES.json and RESULT.json. Corrupted
  fixture/result controls run at that same standalone boundary.

These are different checking methods, not independent human or proof-kernel
review. No separate reviewer was available in this session.

## Reproduction commands

Use an external session-owned RUN directory with an existing `tmp/` child:

```sh
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/p112-common-deletion-span
TMPDIR="$RUN/tmp" python3.12 -B research/p112-common-deletion-span/test_verify.py
TMPDIR="$RUN/tmp" python3.13 -O -B research/p112-common-deletion-span/test_verify.py
python3.12 -O -B research/p112-common-deletion-span/verify.py --output "$RUN/receipt.json"
cmp "$RUN/receipt.json" research/p112-common-deletion-span/RESULT.json
ruff check --no-cache --select E,F,B,SIM,UP research/p112-common-deletion-span
ruff format --check --no-cache research/p112-common-deletion-span
python3.12 -W error -B - <<'PY'
from pathlib import Path
for path in Path('research/p112-common-deletion-span').glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
PY
```

The generic manifest checks historical catalogue/selected-record provenance.
The mathematical replay itself works without Git. Publication bytes are checked
with `scripts/check_research_commit.py` after committing.

## Code and resource review

Build the Lever shaped the deliverable: the proof's finite obligations are a
rerunnable checker, not a saved search assertion. Prove It Works shaped the
verification: separately generated normal orbits and binary evaluation codes
check the actual receipt, including rejecting controls.

All code paths use structured control flow without recursion. Geometry has
120 root lines, eight reflections and 255 proper parabolic seeds. Each orbit
has a hard 4,000-state capacity and fails rather than truncating; the combined
inventory is capped at 6,000. The observed orbits have 120 and 1,080 states.
Characters are 512 entries; annihilator enumeration has at most 130,305 pairs
and retains exactly 43,435 representatives. All integer masks have at most
120 bits. Normal and rank elimination have eight columns and at most 120 rows.
Each JSON read has a one-MiB limit. Test subprocesses have 30-second timeouts;
each registered command has a 60-second timeout.

Power-of-ten deviations:

- Rule 3, managed allocations. Python's integers, sets, Fraction values and
  library calls allocate during checking. The runtime cannot prohibit those
  allocations. Fixed data dimensions and explicit orbit/state capacities bound
  their live cardinalities. Minimal cut construction has at most 130,305
  character pairs per direction; shared states are capped at 65,536. The
  fixed fixture produces ten single-cut directions and six states. A native
  fixed-allocation rewrite is warranted only if this becomes a large census.
- Rule 9, framework dispatch. unittest, its three scoped mock controls, and
  argparse use Python callbacks. Targets are fixed to this package; all mocks
  restore on exit, and all subprocesses are awaited. No production registry or
  dynamic code generation is added.

All functions remain below 60 lines in normal formatting. Internal assertions
check fixed data shapes; externally supplied fixture/JSON errors and acceptance
gates use explicit exceptions, so optimized Python retains rejection behavior.
Ruff E/F/B/SIM/UP, formatting and warnings-as-errors source compilation cover
these paths without changing repository-wide diagnostics configuration.

## Scope not checked

Other six-space pairs, the full C1-C7 reduction, coefficient realizability,
physical/native operators, supplier admission, all-size/precision/analytic
premises, and the selected full cold replay are outside scope. Complex coverage
uses the explicit real/imaginary argument in README.md, not numerical sampling.
No selected record, frozen source, shared verifier or upstream package changes.
Hosted CI and maintainer review are separate from local evidence.

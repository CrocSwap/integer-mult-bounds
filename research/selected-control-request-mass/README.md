# Sharp request bounds for the selected BIT control grammar

For PR2310's unchanged Good/Pair/unit-reset interpreter, a complete final
weight vector at any ancestry depth uses at most **21e/16 value requests**,
where `e` is the original extent. The constant is sharp. Branching is paid
for by the width loss at the same step; no memoization is needed.

The [proof](PROOF.md) also gives sharp bounds on table reads, modular-operation
counts, all interpreter events and sequential frozen-tape head movement:

| Whole-vector quantity | Sharp upper bound |
|---|---:|
| Value requests, including root/reset | `21e/16` |
| Complete table reads | `441e/512` |
| Source-counted modular operations | `441e/512` |
| All popped events | `2205e/1024` |
| Head movement, for page length `L` | `972405eL/262144` |

Global table ages remain charged after unit resets. Under PR2310's retained
fixed-size preparation, sequential-vector and physical-pass hypotheses, this
gives the sufficient preparation envelope `O_q(e*w^3)`, hence `O_q(w^592)`
under `w=ceil(e^(17/10000))`, in place of its looser `O_q(w^1800)` estimate.
The existing factorial absorption argument then uses `2^592*592!`.

This is an author-checked scoped proof and finite source audit. It is not a
physical caller implementation, an independent audit of the matrix producer,
a supplier admission, a practical speedup or a new kappa. The predecessor
already establishes its conditional asymptotic form; this sharpens one
resource estimate within that argument.

## Exact source and overlap

The interpreter is copied unchanged from Jose Manuel's
[PR2310](https://github.com/CrocSwap/integer-mult-bounds/pull/2310), commit
`a5258f548bfb6da71c3b72733fbbd2fb4995c929`. Its proof, README and NOTICE are
preserved alongside it. [SOURCES.json](SOURCES.json) binds every copy by
source path, commit, Git blob and SHA256; the verifier checks the bytes.

The claim is in [discussion #2304](https://github.com/CrocSwap/integer-mult-bounds/discussions/2304#discussioncomment-18942789),
following its released control-work review handoff.
This account's [PR2332](https://github.com/CrocSwap/integer-mult-bounds/pull/2332)
binds actual producer coefficients to the tables; this package does not repeat
that work. [Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319)
reports the generic execution successor [PR2364](https://github.com/CrocSwap/integer-mult-bounds/pull/2364)
and now claims a selected coefficient-site refinement. Both remain separate
from this request-count result. The task card and
exact scope are in [TASK.json](TASK.json).

## Reproduce and inspect evidence

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/selected-control-request-mass
```

The hook performs normal and optimized read-only replays and four integrity tests.
Direct replay:

```sh
python3 -I -B research/selected-control-request-mass/verify.py
```

Expected final line:

```text
PASS_SELECTED_CONTROL_REQUEST_MASS source_programs=628 coordinates=4920 abstract_cases=112347 controls=9 preparation_exponent=592 no_new_kappa
```

[RESULT.json](RESULT.json) separately records:

- 112,347 exact abstract cases: all chains through depth five over eight
  representative operation types, at three root offsets;
- 628 unchanged-interpreter programs and 4,920 coordinates, covering all
  legal Good ranks, six small rings, both orientations and reset pruning;
- an actual depth-ten binary fixture with 2,047 value requests, 1,023 table
  reads and maximum stack size 21;
- sharpness at Good(42) depths one and two by complete vector execution;
  depth four by one coordinate trace plus the proved multiplicity identity;
- nine rejection controls, including lost Pair branches, forgotten resets,
  compacted physical ages and exceeding the final-vector request allowance.

The level-multiplicity oracle is separate from the predecessor's stack order.
Actual popped events are observed with Python tracing; table/movement/ring
counts are checked against the source meters. Value hashes identify the
fixtures; they are not a new proof of coefficient semantics. The written
product and ratio arguments, rather than the finite census, establish the
all-depth theorem. Optimized replay retains every acceptance predicate.

`verify.py --emit` prints fresh evidence without writing. `--write` is the
explicit regeneration option. The integrity tests additionally change saved
evidence and source behavior in isolated copies, including tests that rebind
hashes to ensure semantic work checks still detect the change.

## Open next questions

Bind the request allowance at an actual preparation site in the joined
physical caller: show that a site evaluates at most a fixed multiple of its
current extent, with no recursive parent-vector construction or repeated
spectator-prefix traversal. Begin with one complete Good-to-Pair/reset site
in the Discussion2319 work. This connects the resource theorem to execution;
it requires the completed caller and its physical accounting.

The proof does not determine an optimal preparation algorithm or numerical
bit-cost constant. Tightening either would require an explicit arithmetic
implementation, not another sampled root calculation.

## Credit

Jose Manuel (@jmbarrancoml) supplies PR2310's interpreter, global-field contract
and uniform absorption proof, and PR2234's caller work. The grammar derives
from commdata2338's PR2188, source527 and Ross Richardson's PR2159 fallback
algebra. Gareth Davidson's PR2289/2295 address the separate recurrence and
moment implications. The complete predecessor notice remains at
[sources/pr2310/NOTICE.md](sources/pr2310/NOTICE.md).

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New material is Apache-2.0. No independent human or proof-assistant review is claimed.

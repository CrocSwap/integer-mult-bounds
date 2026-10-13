# Four reviewed R439 schedules compose: 72 fewer complete ADDs

**Finite bit-supplier construction; no new kappa.** The phase-B schedules from
PR880, PR873, PR908 and PR914 compose on the selected PR589 bit word, reducing
the complete local program from **24,305 to 24,233 ADDs**. This package supplies
a single reconstructed word, checks every one of the 16 subsets of these four
replacements, and preserves every paid recursive rank. Its new evidence is
composition and complete accounting, not priority for the individual circuits.

Base commit: `407d52ff15b2217b6e22bce44728b4c3907b6515`. The accepted conditional
result there is PR942's `kappa = 1661960547713947/10^18`, with the unchanged
PR589/555 bit supplier. The selected certificate and upstream sources are
unchanged. [SOURCES.json](SOURCES.json) pins every consumed predecessor artifact,
the supplier word, Python/native checkers and contextual sources by SHA-256 and
base Git object.

| Full local charge | Original | Four-block composition |
|---|---:|---:|
| B ADDs | 934 | 898 |
| C literal cleanup ADDs | 2,629 | 2,593 |
| All ADDs (including D, A and scatter) | 24,305 | 24,233 |
| Exported records | 27,234 | 27,162 |
| MOVEs | 2,911 | 2,911 |
| COPY / ERASE pairs | 9 | 9 |
| Persistent registers / dirty helpers | 661 / 439 | 661 / 439 |
| Paid rank mass | 5,129 | 5,129 |
| Forward positive prefix bound | 49,347 | 49,347 |
| Reverse positive prefix bound | 1,113,070 | 942,262 |
| Local payload envelope | 93 bits | 93 bits |

The paid profile remains `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`.
The nine copies retain rank seven and decoder constant 63. No helper, clean
initialization, source access, frame, COPY, restoration call or recursive child
is introduced. Both the changed forward gates and their required cleanup are
counted. No measured multiplication runtime improvement is asserted.

## Reproduce

Python 3.11+ and its standard library, from the repository root:

```sh
python -I -B research/r439-four-block-composition/verify.py
```

Expected final line:

```text
PASS_R439_FOUR_BLOCK_COMPOSITION subsets=16 cover_edges=32 adds=24305->24233 columns=661 controls=9
```

The command reads immutable sources, builds all 16 words in temporary storage,
checks exact certificates, and changes no committed artifact. `--output PATH`
retains all words and record streams in a **new** directory; an existing path
is refused. `--write-certificate` explicitly regenerates this package's receipt.
Use `python -I -B research/r439-four-block-composition/test_package.py` for the
isolated execution and artifact corruption controls.

The native harness uses an existing C++17 compiler and Boost headers:

```sh
python -I -B research/r439-four-block-composition/native.py
```

Set `CXX` and `BOOST_INCLUDE` when they are not on the default compiler path.
For MSVC, use an x64 developer environment and `CXX=cl`. This rebuilds the
unchanged legality and 5/9/11-stage formal-column checkers for the original and
composed words. Expected marker:

```text
PASS_R439_FOUR_BLOCK_NATIVE words=2 saving=72 stages=5,9,11 columns=883,1327,1549 bridge_controls=96
```

See [VALIDATION.md](VALIDATION.md) for what actually ran, environment details,
failures corrected during development and remaining scope. A command being
provided is not evidence it passed; the recorded receipts are separate.

## Exact composition argument

The four disjoint **source intervals**, in their original execution order, are:

| Frame | PR / contributor | Original B slice | ADDs |
|---|---|---|---:|
| 507 | [PR880](https://github.com/CrocSwap/integer-mult-bounds/pull/880), Krishnendu Purohit / Deftsalt-debug | `[128,163)` | 35 -> 30 |
| 519 | [PR908](https://github.com/CrocSwap/integer-mult-bounds/pull/908), Ross Richardson | `[163,205)` | 42 -> 32 |
| 508 | [PR873](https://github.com/CrocSwap/integer-mult-bounds/pull/873), Aaron Wang / navinor | `[205,242)` | 37 -> 30 |
| 524 | [PR914](https://github.com/CrocSwap/integer-mult-bounds/pull/914), Ross Richardson | `[449,490)` | 41 -> 27 |

For each block, `check_blocks.py` evolves integer basis columns and independently
enumerates all Boolean inputs. It imports neither the composition builder nor
predecessor verification/search code. It establishes the same positive integer
forward matrix, the same set of participating physical registers, and entrywise
domination of the reversed-positive matrix. There are **11,264 Boolean inputs**
across the blocks. The combined B matrix is also checked on all **447 B
participant columns**; its reverse has **298 strictly smaller entries** and none
larger. Registers outside this participant set are untouched by B.

Embed each block matrix into the full register space by identity on untouched
registers. Every intervening positive matrix is nonnegative. If `Q' <= Q`
entrywise, then `L Q' R <= L Q R` for any nonnegative `L,R`. Substituting one
block at a time therefore preserves the complete forward map and dominates the
complete reverse-positive map. This argument does not require disjoint wire
sets. Within an addition-only block, every intermediate nonnegative coordinate
is bounded by its terminal coordinate, so it also controls intermediate
prefixes. COPY/ERASE in the surrounding word is separately interpreted and
priced from the emitted instructions.

The builder applies original source indices from right to left. An independent
streaming builder in `check_blocks.py` must produce exactly the same combined B.
It then rebuilds C as the literal full-frame reverse of every source/helper
write in A and B. That reverse restores arbitrary incoming dirt over F2;
no inverse identity over the positive integers is asserted. The original
owning checker verifies H1-H5, the decomposition and all 661 dirty-input columns.
All 661 complete register frame paths must match the original.

All **16 subsets** are exported and independently interpreted by the retained
PR880 set-valued record interpreter. Each of the **32 cover relations** in the
subset cube must save exactly twice the appropriate block saving and must not
increase either measured positive prefix bound. The complete local bound
`64 F^3 B^2` falls from `9528119495320518471870892800` to
`6828189949769144673901978368`, both below `2^104`. This local formula alone is
not a substitute for the separate native multistage checks.

Nine negative controls reject stale cleanup, removal of a gate from each of the
four frames even after cleanup is regenerated, a shifted source slice, missing
dirty compensation, an illegal frame and a removed literal exported ADD.

## Coverage, overlap and limits

This is a deterministic composition of four fixed witnesses, with exhaustive
coverage of their 16 subsets; there is no randomized circuit search, claimed
optimality or new parameter endpoint. The OS assignment seed is **1**; the
alternatives and local sprint claim are in [CLAIM.md](CLAIM.md).

The predecessor schedules were individually reviewed in the maintainer's
[batch952 review](../../docs/research/community-batch952-review.md), which
explicitly does not compose the individual bit candidates. Their exact
reviewed heads are retained in SOURCES.json. This package adds fresh evidence
for their interaction and a single runnable composition. The unchanged
fixed-word frame optimum and single-write obstructions do not forbid this
combination of already constructed scalar schedules.

Contemporaneous PR973 changes the different frame509 block. PR980's admission
experiment changes phase A and explicitly leaves phase B uncomposed. PR941,
PR965 and PR967 change D under the semantic boundary interface. None of those
pending artifacts or savings is imported here; this composition is not claimed
to be the smallest known R439 circuit.

Full hosted supplier emission, the parent invoice, binding of a substituted
bit supplier and outer assembly remain adoption work. The recursive moment is
unchanged, so these ADD savings cannot on their own increase kappa. All inherited
all-size/compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape/exact-recovery and analytic obligations remain. Finite replay
does not formally verify the multiplication theorem. The selected frontier is
unchanged; broad regenerating suites are not used to retest unchanged sources.

## Attribution and license

Prepared for **@woklerx**, with substantial **OpenAI Codex assistance** in
selection, implementation, proof explanation, testing and writing. Delegated
Codex workers independently implemented block replay and reviewed the package;
this is not independent human peer review.

Circuit credit belongs to the four predecessors listed above. Supplier credit
remains with **DreamingOfClouds** (PR589 and PR545), **eumemic** (PR555/543),
and the retained PR503/510 lineage. The record exporter and native framework
retain **Dylan Crow**, **Zhihao Chen**, **DaysSky**, and the full lineage in
[the supplier NOTICE](../e8-bit-p111-tuned/NOTICE.md). The reused record
interpreter is from PR880, itself crediting **mtpsl / PR691**; the native harness
adapts PR880's **Ali Romman / PR688** lineage and Ross Richardson's frame524
environment reporting. Existing notices remain intact. New files are
**Apache-2.0** under the repository license.

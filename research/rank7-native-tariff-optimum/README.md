# An optimal native tariff for the rank-seven restore block

Four scalar gates can cost less than three. This package replaces one literal
PR3042 restore block, and its derived inverse cleanup, with two ADDs and two
negations. The inherited native emitter's complete real-component primitive
bound falls by **24 per provider word and orientation**. The recursive invoice
and κ are unchanged.

## Replacement and exact result

Set `x = X22`, `y = X230`. Every gate uses the unchanged rank-seven frame
`[256,128,64,38,20,10,1]`.

```text
PR3042                 PR3056                 this package
x -= y                 y += x                y -= x
y += x                 x -= y                x += y
x -= y                 y += 2*x              x = -x
y += x                                       y = -y
```

All three maps send arbitrary dirty `(x,y)` to `(-y,x-y)`. PR3056 proved its
three-ADD word shortest by scalar gate count. The native coefficient tariff is
a different objective. This package's four-gate word attains its exact minimum
of **10 per real component**, compared with 13 for PR3056 and 16 for PR3042.
The same minimum holds for the inverse. [The proof](PROOF.md) covers every
finite two-register word in the specified dyadic ADD/SCALE alphabet, not just
a coefficient search.

The replacement is exactly `restore[175:179]` in both pinned PR3042 words.
`tariff.produce` checks that preimage and derives cleanup from the changed
forward word. Restore and cleanup retain 212 and 5,216 scalar gates. No state,
register, frame or other word section changes.

Fresh execution of the byte-pinned inherited `bw_transport.py` and `bw_emit.py`
checks all 632 arbitrary-input columns in both orientations. It checks the
frame chains and private erasure. A separate tariff recount reads the actual
emitted programs. Both providers give the same complete bounds:

| Word | Forward | Inverse-transpose |
|---|---:|---:|
| PR3042 | 158,148 | 158,196 |
| PR3056 three ADDs | 158,136 | 158,184 |
| This four-gate word | 158,124 | 158,172 |

Each direction retains all 22,760 emitted events, 17,449 scalar macros,
240 warp events and 91 private buffers. Every non-scalar event and every
scalar outside restore and full-frame cleanup is identical. Restore and
cleanup each contribute half the improvement. The compiler reports a
**conservative primitive bound**, not a fully expanded instruction count or
measured runtime.

## Recursive bill and verification boundary

The independent finite-set frame checker from PR3050, retained through PR3056,
confirms identical chronological frame histories for all 704 original registers,
408 ordered helper widths and this local profile:

```text
{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}
```

The unchanged T74 source allocation retains the complete profile:

```text
{1:1637688, 2:474192, 3:159468, 4:71928,
 5:13716, 8:5328, 48:28190}
rank mass = 4,816,512
physical families = 66,813, including all 91 private buffers
```

This is not fresh ownership/admission evidence. Its unchanged-cost implication
is conditional on the inherited allocation and native interface. The old
recursive moment and packing ceiling do not improve. No outer κ is claimed.

A meaningful negative control shows why the native endpoint test is insufficient
by itself. A wrong restore negation followed by its newly derived inverse can
pass the native whole-word endpoint check. The original, now stale, cleanup can
also pass because it has the same operator. This package separately checks the
literal restore operator on arbitrary dirty values and the exact derived
cleanup. Both mutants fail those checks. Nonmonotone frames fail actual native
transport; source-byte, inventory, tariff, child-rank and erasure mutants fail
their named checks.

The compiler and frame checker are reused, not independent implementations of
those contracts. The new result is the native-tariff optimum, its source-bound
application and separate emitted-ledger comparison. No fresh physical Clifford
warp/wrapper replay, prefix/magnitude, precision/tape, movement/backing,
all-size/compiler theorem, supplier admission or outer release is run. The
optional projected-idempotent extension of PR3056 is not claimed for this word.
The actual common invertible-frame contract is the one checked here.

## Reproduce

Python 3.12 and its standard library suffice. Six complete word compilations
and fourteen behavioral test groups take seconds on the recorded host. No
network, solver, numerical dependency or in-checkout output is required.

With `RUN` an existing session-owned external directory:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-native-tariff-optimum/verify.py \
  --work "$RUN/native" > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-native-tariff-optimum/evidence/RESULT.json
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-native-tariff-optimum/test_verify.py
```

`--work` must name a fresh external path. It preserves compiler logs and
programs, including on failure, and refuses existing files. Without it, the
verifier uses disposable work under `TMPDIR`. The inherited validators require
assertions; optimized full replay is refused. Optimized behavioral tests run
the compiler in a nonoptimized child and retain the same checks.

```sh
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/rank7-native-tariff-optimum
```

To emit a candidate word, run `verify.py --emit-word base` or `--emit-word extra`
and redirect stdout to an external file. Emission first runs the full audit.
`evidence/RESULT.json` records canonical word and literal native-program hashes.
[VENDOR.json](VENDOR.json) pins eleven frozen inputs by source commit, Git blob
and SHA256. [SOURCES.json](SOURCES.json) pins the main invoice dependency.
[ENGINEERING.md](ENGINEERING.md) records checks and implementation limits.

## Scope and decision

Canonical baseline is `d8e0f83f00191df62174b641e9fff055c357f641`, priority
revision 6. This is a handoff-first scope override of `independent-moment`.
PR2993/3050/3053 already cover earlier local frame/restore obligations. The
missing PR3056 check was native cost. Its first comparison exposed the better
native-tariff word, which is the single bounded refinement retained here.
The separate live frame-reassignment task is not taken over. Stop at this
finite cost metric, without another frame, packing or lowering search.

Evidence is author-checked, not independent human or formal-kernel review.
The selected frontier and frozen predecessors are unchanged.

## Open next questions

Does a fully materialized coefficient-stream implementation retain the lower
bound as an actual instruction saving, including prefix widths and private
cleanup? Start with the six pinned emitted streams and compare exact expanded
ADD/SCALE recipes. This matters because a conservative tariff improvement is
not a measured physical speedup. Concrete instruction lowering and its complete
precision/storage invoice are the blockers. A fresh supplier/outer release is
separate; the unchanged recursive profile gives no reason to expect a new κ.

## Credit

Nick Petalas contributed the native-tariff word, optimality proof and replay.
PR3056 supplies the identified block, original contraction and source fixtures.
Credit dcharb78 for PR3042's six-skip words, Jeremy Kothe for PR3015,
Marius-Paul Dumitrean for PR2979, Cinna Davis for PR2226's borrowing/native
transport, icekylinx and the PR433/514 emitter lineage, and Tekalign for the
retained fast-native package. The compiler sources and inherited frame/cleanup
helpers remain byte-identical. [Retained credits](vendor/CREDITS.md),
[NOTICE](vendor/NOTICE) and the native PR2226 notices preserve the full
predecessor chain. Apache-2.0. Development used substantial automated assistance.

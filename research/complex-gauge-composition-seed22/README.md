# A changing gauge on seed-selected helper L248

**Finite scalar construction; no new κ.** OS seed 22 selects the 23rd helper
(zero-based sorted index 22) from PR1263's 237 eligible helpers: L248. This is
outside PR1259's seed-37 slice `[37:53]`, whose winner was L276. On the selected
PR1094 k8 word, I re-optimized L248's integer scale at each of its 71 incident
ADDs while keeping PR1263's other 217 constant gauges fixed. The exact best
schedule in this one-helper class saves a further **90 complex primitives per
invocation** over PR1263's 13,000-primitive saving, in both orientations.

| Orientation | PR1094 word | PR1263 constant gauges | Mixed schedule | Increment | Total saving |
|---|---:|---:|---:|---:|---:|
| Forward | 149,002 | 136,002 | **135,912** | 90 | 13,090 |
| Backward | 149,018 | 136,018 | **135,928** | 90 | 13,090 |

The complete bill includes every coefficient-work initialization and clear,
all 217 unchanged helper entry/exit scales, and L248's 12 paid scale changes
including its boundary restoration. The L248 path is optimized over every
integer exponent schedule, not just PR1259's L276 path. The forward and
backward paths are exact inverses. All 712 symbolic input columns agree with
the target map; three arbitrary-dirty primitive replays pass in each
orientation. The positive prefix ceilings remain 52/68 bits and the
conservative dyadic denominator depths remain 24/26, below the retained local
192-bit charge. The recursive paid profile and non-scalar event stream are
identical to PR1263.

This composes two finite research results without adding their savings. PR1259
optimizes a changing gauge on its seed-37 helper slice; PR1263 optimizes 218
constant gauges jointly. Here seed 22 selects L248, outside that slice, and the
new conditional one-helper optimum saves 90 complex primitives after the
many-gauge word. It is not a global optimum over dynamic gauges on other
helpers.

## Reproduce

From the repository root, with Python 3.11+ and the standard library:

```sh
python3 -I -O -B research/complex-gauge-composition-seed22/verify.py
python3 -I -O -B research/complex-gauge-composition-seed22/test_package.py
```

Both commands are offline and write no files. `SOURCES.json` pins the base
selected record, #1094 replay archive and lowerer, and the vendored predecessor
files. `RESULT.json` stores the two full schedules, hashes, endpoint reports
and invoices. The test command also checks that omitting a scheduled scale,
changing an ADD coefficient, dropping a helper restoration, or corrupting a
source pin is rejected.

## Scope, credit and unresolved work

The exact sources are PR1094 (Rohan Arun) on PR1087 (Jeremy Kothe), plus Sagar
Thakrar's PR1259 variable-gauge method and Philipp / @mightyOil's PR1263
simultaneous-gauge result. Their original package evidence and attribution are
retained under `vendor/`; the PR696 copy-init lowerer is reused and credited.
The selected conditional result remains κ = 0.001672660197076918. This scalar
word changes neither its recursive histogram nor that κ. All selected-result
compiler, realization, hosting, precision/tape, analytic and bit-interface
assumptions remain. The mixed word has not been admitted through the native
supplier/controller and full hosted invoice.

Prepared with substantial OpenAI Codex assistance on the user's behalf. No
independent human review is claimed. The contribution is under Apache-2.0.

Open next question: port this frozen mixed trajectory into the native scalar
emitter and repeat the source-bound phase, hosting, precision and complete
supplier admission. That is needed before adopting the word; the first step is
to emit only the recorded L248 path against the already checked PR1263 vector
and compare the full controller invoice. Broader time-varying gauges remain a
separate search class.

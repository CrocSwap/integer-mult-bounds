# Boolean endpoint IDs cross the checked bit-export boundary

Changing only `final[0]` from integer `1` to JSON `true` in the retained PR589
word passes the full symbolic checker and the actual
[`integer-xor-scatter-v1`](../integer-xor-scatter-boundary/README.md) exporter.
The 27,234 binary records and all 636 frame descriptions remain byte-identical.
The final-state JSON changes, and the retained native consumer's terminal
comparison rejects it: its integer frame `1` is not equal to JSON Boolean `true`.

This is a finite source-to-consumer representation counterexample, with an
opt-in repair. The unchanged selected integer input is valid. No new kappa,
supplier admission, or selected-record change is proposed.

## Exact boundary and evidence

The Python checker uses endpoint values as list indices and compares them with
integer frame IDs. `True` indexes frame 1 and compares equal to `1`; all H1-H5,
interface conclusions and all 661 symbolic columns therefore still pass in the
actual witness. The exporter serializes the original endpoint value into
`249-states.json`. Its binary records use integer fields and remain unchanged.

The actual `stage_cohort.py` converts **initial** IDs with `int(v)`, but copies
the final-state metadata without that conversion. The native `legality_h.cpp`
uses the following terminal predicate with its pinned `json.hpp`:

```cpp
if(state[s]!=st["final"][to_string(s)])throw runtime_error("final frame");
```

[verify.py](verify.py) runs the unchanged predecessor's real checked export
and actual staging script, then compiles [json_endpoint_probe.cpp](json_endpoint_probe.cpp)
against that exact JSON header. The probe initializes the integer state from
the baseline's declared final IDs and executes the exact terminal comparison.
It checks **one consumer predicate**, not the complete native loop. This
separation is deliberate: the source, staged initial map and binary records
are identical, so a native execution reaching the same integer final state
cannot satisfy the Boolean final declaration. No fresh full native acceptance
of the baseline is claimed.

| Fixture | Full predecessor check/export | Record and frame bytes | Compiled terminal predicate | New guard |
|---|---|---|---|---|
| Unchanged input | Pass | Baseline | Pass, 661 roles | Pass |
| `start[240] = false` | Pass | Identical | Pass: staging repairs initial ID | Reject |
| `final[0] = true` | Pass | Identical | Reject at role 0 | Reject |
| Both changes | Pass | Identical | Reject at role 0 | Reject |

The initial-only fixture is a **nonfailing consumer control**. It would be
incorrect to report every Boolean endpoint as a native failure. The new guard
chooses a sufficient exact-integer contract consistently at both ends rather
than expanding the accepted schema around incidental coercions.

[RESULT.json](RESULT.json) records all three artifact hashes for all four
fixtures. The baseline record digest `ea44aa04...ef09a` is the existing
#2977/#3801 result, retained as a positive control, not a new discovery.

## Opt-in successor

[boundary.py](boundary.py) supplies `typed-endpoints-integer-xor-v1`. Both
`start` and `final` must be lists of exactly `2*v+R` entries, each with Python
type **exactly `int`** after JSON parsing, in `[0, len(frames))`. Boolean,
float, string, negative and out-of-range IDs reject; so do truncated or padded
endpoint arrays. The existing `v`/`R` bounds are retained. This does not claim
to validate every word field or every JSON encoding.

For any accepted ID `f`, Python indexing, emitted integer endpoint metadata and
the native JSON integer comparison refer to the same numeric frame ID. This
closes the demonstrated type mismatch. It does not prove that the frame is
geometrically or semantically correct; the full original checker still runs.

The wrapper validates before delegation, authenticates its seven delegate files,
and passes a private snapshot of the parsed word to the unchanged combined
integer-label/XOR boundary. The predecessor's normalized scatter, per-slot
COPY/ERASE charges, label checks and complete symbolic check remain active.
Replacing the original input after validation cannot change the delegated word.
Existing output paths are refused. The inherited final copy is not transactional;
an I/O failure can leave a partially copied new output directory.

The baseline and a cancelling scatter-pair fixture preserve **all three**
export artifacts byte for byte. Separate controls reject a fractional label,
an integer label with wrong geometry and an integer final frame with wrong
semantics. Thus the new type predicate does not replace either previous repair
or the symbolic checker. Nine test groups also cover endpoint types/shapes,
all seven delegate-corruption controls, input replacement and output preservation.

## Reproduce

The registered replay needs **CPython 3.12 and `g++` with C++17 support** on PATH.
No third-party Python packages or Boost installation are needed: the small
consumer-predicate probe uses the retained JSON header only. The wrapper itself
uses only Python's standard library.

```sh
python3.12 -B scripts/research_package.py --package research/bit-endpoint-frame-types
python3.12 -I -O -B research/bit-endpoint-frame-types/verify.py
python3.12 -I -O -W error -B research/bit-endpoint-frame-types/test_boundary.py -v
```

The replay prints `PASS_BIT_ENDPOINT_FRAME_TYPES cases=4 semantic_rejections=3
no_new_kappa`. Default verification compares the reconstructed receipt without
writing package files; `--emit` prints a candidate receipt. Compilation and all
delegated files stay in a temporary directory. Each registered audit is bounded
to 120 seconds; the tests have a 60-second limit.

Use the opt-in wrapper as follows:

```sh
python3.12 -I -B research/bit-endpoint-frame-types/boundary.py check WORD.json.gz
python3.12 -I -B research/bit-endpoint-frame-types/boundary.py export WORD.json.gz NEW_OUTDIR
```

Local verification used Windows, CPython 3.12.0 and MSYS2 GCC 13.1.0. Hosted CI
is separate evidence. Exact Git blobs and SHA256 pins for eleven live inputs
are in [SOURCES.json](SOURCES.json); [VERIFY.json](VERIFY.json) declares them all.
The package works from the official Git-free export as well as the repository.
The optional full-history ancestry preflight was not run in the shallow checkout.

## Scope, coordination and attribution

Canonical scientific base: `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority
revision 7. [TASK.json](TASK.json) preserves the drawn card and records the
scope change from four-provider admission to a concrete bit exporter contract.
The selected-baseline binding check passed. Overlap searches covered 323 open
PRs, 4,310 closed PRs, 4,134 Discussion records and all 6,710 tracked local note
paths; arbitrary diffs and unpublished work remain outside that coverage.
The pre-submission refresh fetched main
`4c0a359d88f22f05189d51f48387750b801a45d4`; guidance, selection and all eleven
live inputs were unchanged. The isolated contribution was rebased onto that
main while preserving its scientific source pins. The fresh snapshots covered
308 open PRs (07:23 UTC), 4,155 Discussion records (07:25 UTC), 4,339 closed PRs
(07:25 UTC), and all 6,762 local notes including this package's two new notes.
No overlapping typed-JSON endpoint repair was found within that coverage.
The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2976#discussioncomment-19140401)
records the status and submission.

This result concerns malformed candidate acceptance and consumer compatibility.
Full native legality/columns, nonempty ownership and banks, physical hosting,
precision/tapes, all-size transfer and the complete selected cold replay remain
unrun. Source authentication is not scientific acceptance. Independent human
review and proof-kernel verification are unclaimed.

Credit Nick Petalas for #2977/#3801's scatter analysis and #3273's XOR boundary;
Arham Tahir for #2992's simple-support/snapshot predecessor;
`josecarlosgonzalezroque-design` for #3100's integer-label contract; Pierre for
the combined integer-label/XOR wrapper; and kumagi/Hiroki Kumazaki for #3004's
parity analysis. eumemic and DreamingOfClouds retain the bit word/checker lineage,
Dylan Crow the exporter/stager/native consumer, and Douglas Colkitt the selected
bindings and review framework. The imported JSON header retains Niels Lohmann's
MIT notice; it is authenticated in place rather than copied into this package.

Prepared by Mihir Srivastava with substantial OpenAI Codex assistance in the
investigation, implementation, testing and writing. New work is Apache-2.0.
All frozen sources and notices remain unchanged.

## Open next questions

Should a separately versioned supplier adopt this endpoint contract alongside
the integer-label/XOR contract? First review the four fixtures, then bind one
named producer and consumer and run its full native/ownership/hosting sequence.
The missing step is integration and complete supplier verification, not another
Boolean-value census. This package makes no production adoption claim.

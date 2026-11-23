# Retimed decoder-owned control in a charged binary representation

This source-bound follow-up to #8091 at
`b500f72bbcf9c03a7f7fd40b366eedd6d1dd285b` addresses a stated open item:
`Plan.decode` tables, typed Job descriptors, zero lists and suspended leaf
continuations still lived in unpriced host objects.

## Exact result

For the successful production binary caller of #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`, h>=3000, N=2^h and B=N^92,
the finite-alphabet representation has a uniform sum of per-role allowances
below **32 B N h bits**. The actual complete field W has W/B>=3^(2N), so
these controls fit **less than W bytes**. The source's ordered interface
calls and exact Job values are preserved. The full ordered paid job and
its cursor survive a suspended leaf.

Actual axes carry complete ordered rational bases. All 104,904 paid
occurrences are covered by 595 exact base words, each at most 61 operations,
and the literal all-column lift. The dictionary costs fewer than 2^21 bits.
The immutable event tape is charged too; its own pending dictionary is not
hidden behind an unpriced event-generator handle.

[PROOF.md](PROOF.md) states the theorem and full boundary.
[codec.py](codec.py) defines the format and executable correspondence.
[SOURCE-BINDINGS.json](SOURCE-BINDINGS.json) pins source and predecessor proofs.

## Scope

This is **decoder-owned control**, not the complete native controller.
Native iterator bodies remain resident services, with bounded slots in the
encoded decoder image; their private registers, restoration lists, chart
caches, frames and data retain their own charges. This is not a restartable
serialization of Python generators. Whole-Receiver headers, outer numerical
fields, borrowed backing, setup workspace and fixed-tape time remain open.
The Python checker measures emitted encodings and exact correspondence, not
CPython's physical memory. No selected assumption or κ changes.

A conditional history corollary gives an additional allowance below 2W
across same-stage ancestors and below 4,572 X_max bytes across seven fixed
stage roles. These are additional decoder-control terms. Existing
reservations retain their per-role maxima across erasure and later calls.

## Reproduction

From the repository root, with standard-library Python 3.11 or newer:

```sh
python3 -B research/retimed-decoder-control/check.py --output /tmp/retimed-decoder-result.json
python3 -O -B research/retimed-decoder-control/check.py --output /tmp/retimed-decoder-result-optimized.json
```

Expected marker: `PASS_RETIMED_DECODER_CONTROL`. Results are deterministic.
Outputs are written outside the package. No network, production-sized Plan
or numerical multiplier is required. Universal conclusions rest on the
written argument, not the finite checks.

Evidence includes 7,443 exact chart lifts, 29,772 ordered selections, and a
full source native-metadata execution with 104,904 paid jobs, 285,600 typed
axes and 53,796 routes (numerical bank payloads abstracted). Twelve supplied
calendars give 432 event-boundary comparisons and 2,208 suspended leaf
continuations. Controls reject wrong types, basis/axis bounds, unlisted
rational bases, bad widths, truncation, changed order/zero lists and an
actual source-loop mutation.

## Open next questions

1. Charge native restoration/register state at this same source, beginning
   with `StrongBinarySource.raw` and `BinarySource.inner`.
2. Supply a sequential tape implementation and complete lookup/copy/clear
   tariff for the represented decoder, with setup and callbacks separated.
3. Join whole-Receiver and outer CRT headers with the existing data-file
   bounds. A descriptor-only result is not the global space theorem.

## Provenance and credit

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Selected conditional κ remains 0.00363005817 with all five assumptions.
The scoped source is the later unadmitted retimed construction; this result
does not silently transfer to canonical selection.

Ali Romman and retained contributors supplied the algorithm, charts and
schedule. #8091's owner, mass and geometry results remain premises.
#5286/#5404 retain priority for coordinatewise historical accounting.
The addition is the actual typed-axis closure, charged encoding and explicit
source-specific allowance. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. Model-assisted review is not independent
human acceptance or a kernel proof of multiplication. Apache-2.0.

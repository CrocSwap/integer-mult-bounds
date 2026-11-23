## Decoder-owned control with exact typed axes and a complete local bit allowance

This sequential follow-up addresses a representation gap left by the
ordinary data-file audit. A separately registered sibling package,
`research/retimed-decoder-control`, preserves the existing #8091 package.

### Result

At the exact #8042 binary caller, h>=3000, N=2^h and B=N^92, the represented
rows, decoder tables, zero lists, suspended leaf continuations, immutable
event tape and chart dictionary use less than **32 B N h bits**. The actual
field satisfies W/B>=3^(2N), so these controls fit **less than W bytes**.
The source's ordered interface calls and exact Job values are preserved.

The proof treats `Axis(basis, column)` values. All 104,904 paid labels use a
charged library of 595 exact signed rational words, maximum length 61.
The literal column lift and ordered masks give all-width closure. The
library takes 215,644 bytes; the event tape is also charged. Individual-role
bounds yield a conditional additional same-stage history allowance below
2W and seven-stage allowance below 4,572 X_max bytes, retaining old maxima.

### Reproduction and evidence

```sh
python3 -B research/retimed-decoder-control/check.py --output /tmp/retimed-decoder-result.json
python3 -O -B research/retimed-decoder-control/check.py --output /tmp/retimed-decoder-result-optimized.json
```

Expected marker: `PASS_RETIMED_DECODER_CONTROL`. The author check covers
every paid incidence; 7,443 chart lifts and 29,772 ordered selections; the
actual complete native metadata word (104,904 jobs, 285,600 typed axes and
53,796 routes, numerical bank actions abstracted); twelve supplied-calendar
traces, 432 state-image comparisons and 2,208 suspended leaf roundtrips.
Controls cover basis/coordinate loss, wrong order, omitted zero records,
overflow/truncation and a mutated source loop serving the borrowed prefix.
Universal claims rest on the source/encoding proof.

### Remaining scope and credit

This is **decoder-owned control**, not complete controller storage. Native
iterator bodies remain resident services whose registers, restoration lists,
caches and frames retain their costs. It does not serialize them across
process restarts or price setup, fixed-tape lookup/movement, whole-Receiver
or outer CRT headers. Python validates bit images and correspondence; its
RAM usage and the retained fast tariff are not this result.

Canonical base is e54523517d0f03e58352e647c403a5af3e525a57. The source remains
#8042 at dfd25d553a843a946ca0b94130a5ff8943e98fdd, with owner/mass/geometry
premises retained from #8091 at b500f72bbcf9c03a7f7fd40b366eedd6d1dd285b.
No new κ or complete canonical assumption discharge is claimed.

Credit Ali Romman and retained contributors for source, charts and schedule;
#8091 for the antecedents; #5286/#5404 for historical accounting. Prepared
for Jerry Chen / @CubeJerry with substantial OpenAI assistance and separate
model-assisted review. This is not independent human or proof-kernel
acceptance of the full multiplier.

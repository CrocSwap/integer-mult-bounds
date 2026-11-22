# Retimed P104: the last raw-inventory grid point

This package studies the exact retimed source of [#8042 at
e264251](https://github.com/aliromman/integer-mult-bounds/tree/e26425171238e142cc9ffb510fd953f344bd41c7/research/retimed-native-multiplier).
It proves that the fixed homogeneous 36-call binary inventory has one raw-moment
crossing and that **0.003890115286594461** is the largest `10^-18` grid
point below it. It also installs and checks a candidate at that grid point,
conditional on the source's inherited all-size premises. The source's raw
word, timed scheduler and 11/8 binary and 39/256 numerical tariffs are
retained; its binary dyadic trial is changed and its coupling is recomputed.

The new candidate has seven binary rank logarithms `2*10^12*16^i`
for `i=0,...,6`, positive rank logarithm 36,000, stop exponent `10^-21`,
and binary trial `287039844436133239/2^66`. The literal source checks
24 binary coupling cells, 54 positive coupling cells, all seven stage
rates and 54 strict plus four functional signed gates. The directed binary
raw margin is positive, approximately `3.1153e-21`; the seventh-stage
ordinary margin is approximately `1.5352e-20`. The sufficient public
precision exponent is `35791394008032165519`. These enormous constants
are not a practical crossover. [Exact receipt](ENDPOINT-PRICE.json) ·
[Raw bound and proof](GLOBAL-PROOF.md) · [Source refit and limits](PROOF.md)

The unmodified e264 source trial is below the proposed κ, and its actual
stage-price checker rejects the new profile. A separately reproduced
seven-stage fixed-trial control supports `0.003890115286594460` with the
original `4484997569314581/2^60`. The present 66-bit witness changes the
trial, recalculates its coupling and uses a 66-root precision extension;
it is not inherited from that control. For these fixed seven heights and
stopping margin, even the most favorable funded
64-bit dyadic fails an unrounded ordinary upper bound. A 65-bit dyadic
passes the raw and ordinary arithmetic, while the fully installed profile
here uses 66 bits; no full 65-bit installation is asserted. [Exact design
check](denominator_design.py).

The full asymptotic claim is in the **ideal finite-tape model** under the
source's five premises: all-column native action, owned erasure and
restoration, compiler transfer, precision and tape services, and analytic
recovery. The implication also relies on the source's written dfd
source-to-role, storage, time and geometry binding; the abstract stage-store
lemma and finite fence tests do not themselves prove that mapping. The
finite replay does not independently establish those premises, execute
production-dimensional payloads, establish a measured speedup, or formalize
the full multiplier in Lean. A standalone Lean 4.8
certificate checks the seven exact stage bookings and rejection controls,
conditional on an externally supplied raw endpoint; it does not check the
source tariff or physical construction. The 32-site signed
product exercises its local H kernel; supplier construction and boundary
routing are separate feasible controls, with payload placement mocked at
the astronomical threshold.

## Reproduce

With CPython 3.12, assertions enabled, Git and the standard library:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-retimed-dyadic-endpoint
```

For an offline directory without the repository runner:

```sh
for case in price install schedule physical receiver slabs product; do
  python3.12 -IB verify.py "$case"
done
```

Each case verifies the complete 73-blob e264 source tree before rebuilding
a private source copy. The `source-e264.tar.gz` stores 72 small files and
`predecessor-8030.tar.gz` supplies the single large source blob. The
`ENDPOINT-OVERLAY.json` changes the trial and adds a named installed
profile only after verifying its parent bytes. The source's bootstrap then
applies its original machine and receiver patches. See `VERIFY.json` for
individual limits and exact coverage. An earlier physical run timed out at
350 seconds during concurrent work; the identical complete source case
passed serially in 348.79 seconds under the 430-second limit. This is a
finite replay timing, not an upper bound on other hosts. The [case
receipts](evidence/REPLAY-SUMMARY.json) retain launch limits, observations
and failed calibrations. Byte and Git-tree authentication do not imply
that full upstream history is present.

The optional standalone arithmetic certificate uses only Lean core. It
has been replayed with Lean 4.8.0 and with the source's pinned Lean 4.34.1,
without external Lean modules. It is separate from the Python CI cases:

```sh
lean --trust=0 lean/Endpoint.lean
python3.12 -IB lean/verify.py /path/to/lean
```

The optional harness checks trust-zero compilation, an `.olean` import,
axiom reports, two corrupted-source rejections and, when available, a
separate `leanchecker` replay. Local trust-zero runs completed successfully; [the Lean 4.34.1 harness
log](evidence/LEAN-VERIFY-4.34.log) and [the 4.8 axiom report](evidence/LEAN-4.8.log)
and [certificate](lean/Endpoint.lean) do not formalize the directed raw
interval, source coupling, ownership, tape model or overall multiplier.

The published [#8042 head dfd25d5](https://github.com/aliromman/integer-mult-bounds/commit/dfd25d553a843a946ca0b94130a5ff8943e98fdd)
adds a related stage-store formal refinement; its price and operative
machine source were unchanged in the inspected comparison. This package
uses e264 as its operative pin and does not claim that later Lean checks
formalize the new profile. The earlier [#8048](https://github.com/CrocSwap/integer-mult-bounds/pull/8048)
uses the earlier `3d33cb0` retimed source with different prices and
heights; it must not be substituted for this e264 24/54-cell refit. The
nine-stage hosted local-word packing model has a different coverage
hypothesis; the raw crossing above supplies a
replacement upper bound for this fixed inventory, with
`0.999999999999999966582753100 < κ/c* <
0.999999999999999966582753358`. This ratio is not a complex packing cap.

## Open next questions

1. Can an independent proof establish the source's all-column action,
   owner restoration and precise compiler transfer for this exact profile?
   Start with the emitted 24-cell binary schedule and a source-bound
   all-column owner invariant; finite control replays do not provide it.
2. Can a legal changed physical word increase the raw crossing? Name one
   changed incidence, reproduce both field operators and all owner returns,
   then reprice its complete new paid/productive inventory.
3. Can the astronomical first-use dimensions be reduced without changing
   the funded rate? Start by proving an admissible stage-height/stock lower
   bound under the actual seven-stage retimed receiver and its full invoice.

## Credit

Ali Romman supplied the retimed binary and two-scale Gaussian source and
its physical and tape proofs; #8044 supplied the earlier directed local
raw-crossing interval. This campaign supplies the global one-crossing
lemma, candidate refit and source-bound checks. Other predecessor credit is
retained in [PREDECESSOR-NOTICE.md](PREDECESSOR-NOTICE.md) and the pinned
source archive. Substantial OpenAI Codex assistance was used in research,
implementation and verification. Apache-2.0; see [LICENSE](LICENSE).

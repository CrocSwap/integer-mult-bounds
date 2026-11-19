# Additional independent returns on the two #7781 suppliers

The complete finite construction gives **conditional κ ≥ 0.00387290895338**. Its lower bound exceeds the raw upper endpoint **0.00386981257853** for the submitted #7781 complex word by **0.00000309637485**, including when that word has the same improved ordinary binary service. The fixed donation target is 0.00387981257853. This checkpoint leaves 0.00000690362515 in κ. The selected result at the pinned canonical main was 0.00363005817. [Submitted predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7781) · [Complete application](evidence/application.json) · [Selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

| Under the common tariff H(r) = r^(1−κ) | Binary | Complex |
| --- | ---: | ---: |
| Native calls | 36 | 48 |
| Independent native public fields | 680 | 1,281 |
| Complete paid positions | 107,820 | 283,392 |
| Complete productive positions | 20,706 | 52,128 |
| Directed raw crossing, lower | 0.003874293587814 | 0.00387290895346 |
| Directed raw crossing, upper | 0.003874293587815 | 0.00387290895347 |

On the binary side, eight more formerly grade-seven productive paths split into grades two and five. Each splits a paid grade-six transfer into grades one and five. The journal rebuilds each intermediate and checks the new return on arbitrary fields. The independent compiler admits 0.003874293377807 after charging 936,768,709,776 raw ordinary records and 6,998,904 owned fields. [Eight calibrations](binary/BIRTHS.json) · [Literal replay](binary/REPLAY.json) · [Ordinary compiler](binary/FINITE.json)

On the complex word, two source projections eliminate four paid transfers and introduce two calibrated terminal restorations. Their aggregate saving is 48(2H₁ + H₃ − H₅). The new rational readouts split existing addresses 296 and 681, owner labels 303 and 791. Their intermediate charts are 234 and 243. Each split replaces H₉ with H₄ + H₅ across all 48 calls. The added independent owner labels are 1532 and 1533. The complete operator, separate adjoint, fixed main ports, signed prices, paid restorations and ordinary application are independently replayable. [Paid projections](complex/PROJECTIONS.json) · [Productive witnesses](complex/BIRTHS.json) · [Source pins](CLAIM.json)

## Reproduce

Use Python 3.12 from this directory. The manifest pins 127 public source files at commits for #7781, #7776 and #7774. The fetcher verifies the SHA-256 and Git blob identity of each file. Every output can be directed to an empty temporary directory.

```sh
python3 -IB prepare_sources.py /tmp/p104-iterated-sources --fetch
for part in binary-construction binary-finite construction operator charts-0 charts-1 charts-2 application; do
  python3 -IB verify.py --part "$part" --cache /tmp/p104-iterated-sources --out "/tmp/p104-iterated-$part" || exit 1
done
```

The retained hypotheses cover native all-column correctness, owned erasure, compiler correctness, precision-tape simulation and analytic recovery. The finite evidence includes directed comparisons, dirty-state controls, physical charts and the depth guard for a common outer envelope. A small independent check is to omit the coefficient on restored paid slot 73 at terminal 156037. The rational forward and reverse defects can then be compared against the exact fresh-input and retirement journals. Frontier admission remains with the maintainers. [Independent verifier](complex/independent.py) · [Outer assumptions and predecessor credit](https://github.com/CrocSwap/integer-mult-bounds/pull/7776) · [Notice](NOTICE)

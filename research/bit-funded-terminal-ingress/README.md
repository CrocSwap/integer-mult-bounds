# Exact funded-ingress census for the fixed BIT terminal word

**NO VERIFIED GAIN.** Existing paid arrivals into compatible rank-seven charts add zero useful unmarked terminal slots to the fixed native word, even with free retention of old coframed payloads. The resulting optimistic stock is at most 14 returns out of 22. Paying each added donor split separately still leaves a negative directed margin. A distinct route that changes the marked libraries must expand at least 7, 5 or 4 singleton libraries at the campaign target with zero, one or two separately charged donor splits, respectively.

The pinned complete comparator is [#7244](https://github.com/CrocSwap/integer-mult-bounds/pull/7244) at scientific head `4156504fa39efb51c550d218a9b94fe69dbce8f6`, with independently reproduced conditional κ `0.003645372367832` and effective retained BIT premise `376669/100000000`. The directed trials here are `10018846261809/2500000000000000` and `1002040748181/250000000000000`. Neither trial changes κ or proposes a replacement native word.

## Replay

From this directory in a clean checkout, run CPython 3.12 with assertions enabled. The replay was tested under CPython 3.12.14 in an empty current directory and with a cleared environment. All inputs are bundled, authenticated by their stable paths, and staged in a fresh scratch directory. The replay uses the standard library and runs offline.

```sh
python3.12 -I -B replay.py --controls
```

Expect exit 0 and these markers.

```text
PASS_FORGED_PAID_CLOCK_AND_UNDERPRICED_THRESHOLD_REJECTION
PASS_BIT_FUNDED_INGRESS ports=185 added_useful=0 returns=14 target=7/5/4 strict=8/6/unaffordable no_new_kappa
```

The replay regenerates both predecessor receipts and the 8,170,267-byte detailed incidence receipt, then verifies exact byte counts and SHA-256 hashes. It checks the compact `SUMMARY.json`, reruns the independent geometry and chronology audit, and compares the exact price receipt and independent tariff audit. The controls forge one paid ingress clock and reduce the two-split target threshold from four to three. The independent audits must reject both. A one-byte input change and a duplicate manifest path were also rejected before scientific stdout during the clean test.

Use `--inputs /path/to/inputs` for an explicit replacement root with the same file layout. Use `--write-incidence /path/to/new-result.json` to keep the authenticated full incidence receipt for follow-up. `PROVENANCE.tsv` gives the precise public commit and blob for each vendored file. `SOURCES.tsv` preserves the original scientific manifest, including the generated predecessor receipt pins. `PROOF.md` defines the scoped exclusion and price conditions. `NEXT.md` gives the next bounded test.

## Open next questions

Can the old paid ingress events carry new independently sourced marked directions while preserving the old paid operands and exterior outputs? This is the first route left open by the fixed-payload exclusion. Start with the 60-event zero-leak test in [NEXT.md](NEXT.md). Even a successful formal test still needs physical chronology, ownership, signed restoration and full price.

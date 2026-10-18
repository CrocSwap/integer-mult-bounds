# E8 low-read signed defining-source supplement

This supplement carries the immutable low-read E8 candidate from the PR320
search into the defining signed decoder contract. It does not modify the
candidate archive or claim a new all-size theorem. Input candidate SHA256 is
`1b51df6d03c43743ef2b774def9ce2d6739c8ebc2b6752097e697534c062d602`.

The exporter is the pinned PR370 `code/bit/export_records.py`; run with
Python `-B`:

```
python3 -B /private/tmp/pr370-inspection/code/bit/export_records.py \
  /private/tmp/pr370-low-read-certificate-v1/candidate-word.json.gz \
  /private/tmp/pr370-low-read-signed-source-v1/records
python3 -B audit_signed_source.py
```

Observed audit exit is 0 (receipt chunk `779bc0`; exact execution in
`run.log`). `RESULT.json` is the signed-source receipt. It proves all 1105
formal integer columns, arbitrary-helper dirt restoration, forward and
reflected frame ledgers, and exact roundtrip. The defining clean target is the
explicit integer network decoder `M`; its reduction modulo 2 is identity.
The repair changes only signs: phase-D dirt response and phase-C helper
cleanup are negative in the signed defining source. The byte-parity projection
is exactly the exported candidate word, whose own 742/6308 prefix bounds and
paid profile remain the priced payload interface. No new gates or paid calls
are introduced.

Attribution: candidate/source PR320 and PR370 contributors are preserved;
this audit and repair were prepared with OpenAI Codex assistance. Apache-2.0.

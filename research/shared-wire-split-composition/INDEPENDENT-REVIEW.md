# Independent finite acceptance gate

This support verifies the frozen shared-wire word whose canonical JSON SHA256 is `91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097`, the #6980 QUERY-only caller and the paired E-free BIT receipt. It does not create a selected result or admit a supplier.

Run from any working directory:

```sh
python3 -I -B /path/to/package/full_verify.py
```

The default is read-only and compares every proof-relevant field with `FULL-RESULT.json`. Compression-container differences in the generated word are ignored after canonical payload authentication. An explicit `--out /path/to/result.json` writes a receipt. `--word`, `--caller` and `--bit-receipt` may locate the same pinned inputs elsewhere; their authenticated identities cannot be changed. `--core-only` omits precision reuse and adversarial controls and is not the complete registered check. Assertions are proof checks; optimized Python is deliberately rejected.

`independent.py` independently checks chronological frame/ownership laws and the transposed scalar circuit on every public input. Its exact caller ring is Q(i)[q,D1,...,D18]/(q^4−1), retaining repeated D powers with an explicit degree bound. `interval_gate.py` is a separate outward-rounded rational log/exp engine; Decimal root digits are only diagnostic. The full emitted MOVE/helper/QUERY/IDLE inventory, positive ordinary envelope, finite-tail losses, compiler capacity, exact threshold, input-lift lemma and 54+4 outer inequalities are recomputed.

The frozen claim is .00363005817, tested at .00363005817007. The raw crossing lies between .00363005817468836708593357676489 and .00363005817468836708593357676490. Minimum logarithm power is 2227; the written value 2228 yields H=14174600000000000000. The complete conservative ordinary allowance is 826790496, below 10^9. Both complex and BIT callers have no empty-mask productive root credit.

The numerical BIT price .00376669 conservatively weakens the paired E-free BIT theorem at .00385248, bootstrapped from selected admitted .0034. The pinned receipt records both positive bootstrap debits. The stronger theorem's construction and source review are its own dependency; this support authenticates its receipt and bootstrap arithmetic, not a replacement proof of all BIT providers. No old .00376669 ordinary admission or its empty-root credit enters the bootstrap.

`precision_replay.py` explicitly reuses three unchanged, hash-authenticated engine files from #6970 and #6985. These methods are not independently implemented here. The #6985 helper-count assertion and output metadata change from 1061 to the actual 1080 helpers; both substitutions are recorded. Exact-grid and rounded-service conclusions have different premises: exact completed children for the common grid; total RDiv and complete-fibre unitary contracts for the rounded envelope. Neither installs a physical tape primitive.

This verifier does not prove native Clifford chart lowering, absolute phases at every tensor width, physical owned erasure, literal tape rates or the original compiler/analytic contracts. The construction's chart-map certificate is separate. The five framework assumptions and inherited changed interfaces remain: odd native alphabet/exact-child contract, A6, per-port/two-chain HOST2 interfaces and shared-helper accounting, and ordinary LAMBDA/IDLE tariffs. Removing empty-mask credits does not discharge these premises.

Prepared with substantial OpenAI Codex assistance. This is AI/code-assisted checking, not human review or proof-kernel verification. Exact sources and attribution are in `INDEPENDENT-SOURCES.json` and `INDEPENDENT-NOTICE.md`.

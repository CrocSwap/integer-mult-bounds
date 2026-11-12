# Same-clock Type B odd/even idle fusion bound

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On independently reproduced [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, test the exact signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) Type B caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Replace one signed singleton odd idle and one disjoint-mask even idle by one job at the original odd clock and role. Keep the original q inverse factor, union the body masks, and preserve every other literal operator.

Two independent methods exhaust all 180 keys. At q=+1 and unit body, a normalized derivative for any removed even-mask variable requires equality of the odd and even transported rank-one projectors. All 180 have a nonzero off-axis exact column. The rational coefficient reduces to the primary modular witness for every key. Zero cases remain unresolved. No q=−1, nonunit, formal or physical follow-up is needed. [Proof](PROOF.md).

At equal field volume the complete price for even mask size m replaces paid ranks 9 and 8m by 8m+9 across eight Type B ports. The one-edit gross upper is 0.7850445440362529 raw at the incumbent crossing. The exact weighted matching grants at most four compatible disjoint-call edits and a gross upper of 3.076075380146476 raw. This grants all ancillary costs and all compatibility beyond literal disjoint calls and masks. The fixed moonshot still has more than 136.39071 raw units of deficit. A single added paid rank-one position kills every individual edit through the retained BIT cap. Exact endpoint support reduces this scoped one-edit credit to zero.

## Replay

Use CPython 3.12 with assertions and the standard library. From a clean checkout:

```sh
python3.12 -I -B research/p104-type-b-odd-even-idle-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-type-b-odd-even-idle-bound
```

Use `--out` with a fresh directory for the three deterministic receipts. The replay authenticates the compressed caller and its public Git object, regenerates the complete price and both proofs, compares each witness, and rejects changed caller bytes. [Verification details](VERIFICATION.md).

## Open next questions

A changed multi-role provider would need to preserve both distinct body derivative projectors. Pin its phase/body action and fully charge its volume, setup, owner restoration, routing, precision and tape before constructing a candidate. Other clocks, changed roles and simultaneous endpoint cancellation are outside this one-edit test.

Credit #7315 for the even census and derivative method; #7323 for the odd census and separate phase-transfer exclusion; #7334 for the exact comparison; #7113 for the signed caller; and #7298 for directed pricing. #7296 studies the identical pair (1339,2324) under its different canonical parity-scalar erased-child volume model. OpenAI Codex and subagents materially assisted.

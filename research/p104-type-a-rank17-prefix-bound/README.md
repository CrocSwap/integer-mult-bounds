# Fixed-paid Type A rank-17 split prefix bound

Two exact Gaussian Laurent replays exclude all 330 tested splits of the signed Type A caller. The conditional exponent saving is unchanged. The comparison uses the independently reproduced conditional κ = 0.00364665195644 at exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) `aaeec8c0acf01e99a5f331ef363a698d9c084ace` and its [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The maintainer-selected record at canonical main `e54523517d0f03e58352e647c403a5af3e525a57` records κ = 0.00363005817.

| Role and tested pre-event cuts | Required first body | Exact result |
| --- | --- | --- |
| 10, cuts 1743 and 1744, IDLE stage 9 before J stage 10 | B₉ | Both columns have body-independent terms |
| 7, all 328 cuts 1139–1466, J stage 7 before IDLE stage 8 | B₇ | 285 columns have the required body and both central parities. The other 43 contain a foreign body. |

Each cut must have a prefix divisible by its required body with a residual of one central parity. An odd prefix places the sign on the rank-nine first output. An even prefix puts the sign on the rank-nine second output. The exact forward and reverse implementations agree on the full column at both role-10 cuts and on all 328 role-7 column digests, counts and body and phase witnesses. No case in this scope remained unresolved. The suffix and physical build gates require a prefix survivor.

One hypothetical split across the 96 Type A ports replaces 96 productive rank-17 targets with 96 each of ranks eight and nine. The paid histogram is fixed. The directed one-split gross allowance is below 4.077730393712098 raw units at the upper end of the old crossing, and the complete directed margin at the pinned strictly higher probe exceeds 4.077343926692402 before unbuilt ancillary costs. Four distinct roots have a relaxed gross upper below 16.310921574848387 raw units, and one extra paid rank-one child on each of the 96 ports defeats even that relaxed stock. The four-root price grants compatibility and has no implication for support outside the tested cuts. See [proof and price](PROOF.md) and [exact source identities](PROVENANCE.json).

## Reproduce

From the package directory with CPython 3.12 and assertions enabled, run

```sh
python3.12 -I -B replay.py
```

The command uses the standard library and package-relative inputs. It authenticates the caller and inherited price, replays both directions, compares all exact witnesses, checks the original endpoints and synthetic controls, and rejects a changed caller and a changed price. Add `--out receipts-replayed` to save the five regenerated receipts. Their expected SHA-256 digests are in [receipts/SHA256.json](receipts/SHA256.json).

## Open next questions

A genuinely different, fully priced caller factorization could change the prefix column. Freeze one such paid and ordinary bill, then compute its exact endpoint and first-body column before attempting a supplier. Other roots, other role-10 cuts and bases that need paid phase/body access fall outside the tested scope. A surviving prefix would still require a paired cut dual, a restored suffix and a fresh independent dirty field with the retained all-width ownership, tape, precision, compiler and recovery contract.

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supplies the complete comparable baseline. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the literal signed caller. [#7316](https://github.com/CrocSwap/integer-mult-bounds/pull/7316) supplies the reverse Laurent method and the distinct rank-137 root split criterion. [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) supplies the pinned complete comparator price, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed tariff arithmetic. [#7175](https://github.com/CrocSwap/integer-mult-bounds/pull/7175) supplies abstract fixed-profile comparison context. OpenAI Codex and subagents materially assisted proof development, implementation, independent verification and packaging.

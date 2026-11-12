# Bound one-entrant delayed correction banks

This source-bound exclusion concerns the exact [#7334 native word](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` and [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Keep the omitted source at its old pre-ADD value and ask whether it belongs to the bank at the latest cut before the next target-role operand contact. Keep all other paid positions and charts fixed. The correction may use any rational combination of the available bank rows.

Of 119 historically excluded banks, 106 cuts stay unchanged and 13 gain one donor. The unchanged exclusions carry over. Seven moved banks inherit a valid separating input, and two more moved banks fail exact span checks. No literal proportional donor passed. The four remaining cases are unresolved. The complete bound and κ are unchanged.

Use CPython 3.12 on POSIX. From the checkout root:

```sh
python3.12 -I -B research/p104-one-entrant-delayed-correction-bound/replay.py
```

The replay reads bundled, hash-pinned inputs and writes only to a fresh temporary directory. It uses the standard library and needs no network, prior temporary state, or external checkout. Expected output is `PASS_DELAYED_BANK: 119 surveyed, 115 exact exclusions, 4 unresolved`.

## Open next questions


The open cases are `[41805,41807,43313]`, `[41944,41946,43419]`, `[40430,40432,46222]`, and `[43091,43093,46566]`. Start with exact quotient span at `[41805,41807,43313]` under a 30-second solver cap. An exact span survivor would still need admissible scalars, a literal corrected word, ownership and restoration checks, and a fully charged invoice.

[#7434](https://github.com/CrocSwap/integer-mult-bounds/pull/7434) supplied the fixed historical chronology, candidate inventory and first exact controls. [#7436](https://github.com/CrocSwap/integer-mult-bounds/pull/7436) supplied the two older exact methods and their separating inputs. [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplied the exact native word and caller lineage. Codex and subagents materially assisted the proof, code, replay and packaging.

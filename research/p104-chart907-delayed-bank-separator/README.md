# Exclude delayed correction from the chart-907 bank

This resolves one of the four changed cuts left open in [#7438](https://github.com/CrocSwap/integer-mult-bounds/pull/7438) on exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113). At the latest cut before the next target operand contact, the exact scalar input `(x2,x12,x550)=(-4,4,1)` gives the fixed old source value 4 and zero on all four other live chart-907 roles. Their arbitrary rational combinations cannot supply the omitted source. The optimistic two-MOVE saving is about 0.20766650667 raw and one extra paid rank-one occurrence exceeds it. No complete construction or exponent change follows.

Run from a clean POSIX checkout with CPython 3.12.

```sh
python3.12 -I -B research/p104-chart907-delayed-bank-separator/replay.py
```

The bundled exact word and receipts are authenticated by relative path. The replay derives the complete live bank from the literal word, verifies the separator and a one-component mutant, and checks the directed price. Expected marker `PASS_CHART907_DELAYED_BANK`. No network, prior temporary state or external Python packages are needed.

## Open next questions

The other changed cuts `[41944,41946,43419]`, `[40430,40432,46222]`, and `[43091,43093,46566]` remain unresolved. Start with a fixed-budget exact quotient span at `[41944,41946,43419]`, then independently replay any separator or candidate. A changed source, a new chart or paid operator, and different observer timing require separate evidence.

[#7438](https://github.com/CrocSwap/integer-mult-bounds/pull/7438) supplies the exact latest-cut scope, [#7436](https://github.com/CrocSwap/integer-mult-bounds/pull/7436) the earlier separating-input method, and [#7434](https://github.com/CrocSwap/integer-mult-bounds/pull/7434) the historical bank and MOVE chronology. [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) supplies directed pricing. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.

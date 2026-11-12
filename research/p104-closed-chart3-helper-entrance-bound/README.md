# Bound closed chart-3 native helper entrances

**NO VERIFIED GAIN.** On exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) with the signed [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), every fixed-suffix component of productive chart-3 helpers has a boundary contact. The two exact chronology walks agree on all 477 component keys, first ascent clocks and first blockers. No eligible SCALE-only singleton or closed internal-ADD component can delete its first paid lift in this scope. Compatible saving is zero.

There are 1,101 productive helpers. Of the 860 starting at chart 3, 92 first lifts use the whole productive rank and 768 leave positive residual rank. The 768 eligible starts partition into 477 same-upper components. Every component is excluded and zero cases remain unresolved. The only one-boundary component, helper 624, also fails the fixed-route delay of its main-130 read. All seven cuts after its old first lift and through its first payload write have main 130 in chart 3, while the helper needs chart 117. Main 130 never visits chart 117 or an equal binary span on its retained route. [The proof](PROOF.md) states the necessary condition and the limits of the exclusion. [Component evidence](receipts/COMPONENTS.json) records all role IDs, upper charts, first MOVE clocks and exact first blockers.

## Reproduction

Run from the repository root with CPython 3.12 on POSIX.

```sh
python3.12 -I -B research/p104-closed-chart3-helper-entrance-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-closed-chart3-helper-entrance-bound
```

Pass `--out <directory>` to save the directed price and four exact chronology and delay receipts. The replay authenticates the bundled public word by its Git blob, compressed SHA-256 and decoded SHA-256. The two chronology engines reject altered word bytes. The package uses standard-library Python and resolves its inputs locally. [Exact provenance](PROVENANCE.json) and [verification receipts](VERIFICATION.md) identify the retained assumptions and checks.

## Open next questions

A changed boundary adapter, a different initial chart or a changed suffix may bypass the closure gate. On one explicitly priced contact, test whether a proposed adapter preserves signed forward and adjoint action for arbitrary independent helper inputs and returns, including ownership and restoration. The fully charged adapter must leave a positive whole-construction margin before a replacement word is built. The scoped delay test leaves paid adapters and any reorder that changes a retained route open. [Exact delay receipt](receipts/DELAY-CUT.json).

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supplies the exact native word and complete comparator. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the retained signed caller. [#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319) tests a quiet literal first contact and [#7330](https://github.com/CrocSwap/integer-mult-bounds/pull/7330) tests a funded first-read hoist. [#7361](https://github.com/CrocSwap/integer-mult-bounds/pull/7361) supplies the related closed multi-ADD component precedent with fixed incident paid clocks. [#7122](https://github.com/CrocSwap/integer-mult-bounds/pull/7122) supplies an earlier constructive global input rechart, and [#5567](https://github.com/CrocSwap/integer-mult-bounds/pull/5567) supplies the related free-endpoint normalizer audit. [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supply the complete invoice and directed tariff. OpenAI Codex and subagents materially assisted the proof, implementation, independent replay and packaging.

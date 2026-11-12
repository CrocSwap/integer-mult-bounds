# Bound finished-helper promotion for banked MOVE fusions

**Outcome** — Scoped price exclusion. The complete bound is unchanged.

Across 119 historical-bank MOVE fusion cases with exact separating inputs, only one finished proper helper can supply a coordinate tested by the separator with one strictly nested terminal promotion. It is role 831 for the role-1034 fusion at clocks 48765/48766/48767. Promoting its chart 306 to chart 127 costs one rank-five paid lift and changes its productive rank from four to nine. The directed combined saving is about −0.05464378638 raw across all 17 invocations. It is strictly negative for every 0<κ<1 even when the physical action and ancillary work are free. [Proof](PROOF.md)

## Replay

From a clean checkout on a POSIX host, use CPython 3.12 with assertions and its standard library.

```sh
python3.12 -I -B research/p104-finished-helper-promotion-price-bound/replay.py
```

The replay authenticates the exact native Git blob and payload, rechecks both predecessor separator sets on all 119 retained cases, and reproduces the two independent price censuses. Both find the same sole donor and exact negative interval. Expected final line is `PASS_P104_FINISHED_HELPER_PROMOTION_PRICE_BOUND`. [Verification](VERIFICATION.md)

## Open next questions

- Can a new source supply a missing bank direction without an additional full paid lift? Freeze one exact role and cut and price its full paid and productive invoice before a new span test.
- Can another compatible supplier or a changed productive interface share promotions? Start with an exact changed schedule and prove its signed action, ownership, restoration and fixed-tape obligations. This price bound covers one finished proper helper with one appended strictly nested lift.

## Predecessors

- Clear1nsight’s exact #7334 `aaeec8c0acf01e99a5f331ef363a698d9c084ace` supplies the complete comparator, κ = 0.00364665195644, and native word. Rohan Arun’s exact #7113 `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies its signed caller. [Comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/7334), [signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
- Exact #7434 `5f45414d0cc5d0ce6931167bc3e54b026fd4ca09` supplies the original bank scope, the role-1034 case and top-six separators. The next two exact batches supply 62 and 50 more separating inputs. Both methods’ original receipt bytes are bundled and rechecked. [Historical-bank predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7434)
- #7338 supplies related compensated readout tests with fixed productive roles. #7396 supplies the quiet-terminal helper chronology precedent. #7362 and #7298 supply directed price inputs. [Compensated readouts](https://github.com/CrocSwap/integer-mult-bounds/pull/7338), [terminal lift predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7396), [price receipt](https://github.com/CrocSwap/integer-mult-bounds/pull/7362), [price implementation](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)

OpenAI Codex and subagents materially assisted the proof, implementation and independent replay.

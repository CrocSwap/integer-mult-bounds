# Fixed chart-1051 ingress for helper 1310

**NO VERIFIED GAIN.** On exact #7481, a proposed paid-neutral productive split would expose the old independent input of helper 1310 at chart 1051 and give a new independent input to the original suffix. Test the cut immediately before ADD38219, after both original paid arrivals MOVE38217 and MOVE38218, with the old prefix and paid itinerary fixed. The proposed rank-9 productive target would split into ranks 5 and 4.

An exact reverse solve gives a separator for the historical ingress sum from ADD35424 and ADD35425 against all 11 other chart-1051 rows. Independent normalized forward replay checks a stronger collision. Set old public coordinates `x890=1` and `x1310=−1`, with every other old input and the fresh input zero. The entire 12-row chart bank is zero, as it is on the all-zero input, but the required exposed old value is −1 instead of zero. The named paid arrival of role 1311 is included. This exhausts one fixed case with zero unresolved.

The directed gross of the hypothetical split lies between 0.38075659829390934 and 0.38075659829390936 raw across all 17 signed calls, before corrections or ancillary costs. One extra rank-one paid child per call would cost 17 raw. No saving was realized. See [proof and price](PROOF.md), [path pins](PINS.json) and [verification](VERIFICATION.md).

## Replay

From a clean POSIX checkout using CPython 3.12 and its standard library:

```sh
python3.12 -I -B research/p104-helper1310-fixed-ingress-bound/replay.py
```

Expect `PASS_HELPER1310_FIXED_INGRESS_BOUND`. Each scientific process is capped at 30 seconds. Direct replay requires no Git metadata, network or prior temporary state.

## Open next questions

Can a named earlier encoding or a different paid path distinguish the two collision inputs before the first outward read at ADD38220? Specify the sender, receiver and exact deadline, verify the signed support at that clock, and then price any repairs. Changed old chart banks, earlier recovery, changed routes and pre-encoded fresh inputs remain open.

## Credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) supplies the exact native word and complete invoice, with [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) in its native lineage. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller, [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) the reverse covector method, [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed tariff and [#7508](https://github.com/CrocSwap/integer-mult-bounds/pull/7508) prior public copies of pinned inputs. [#7497](https://github.com/CrocSwap/integer-mult-bounds/pull/7497) supplies two fixed-cut exclusions for role 1451 and cites the earlier [#5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718) and [#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599) split precedents. [#7142](https://github.com/CrocSwap/integer-mult-bounds/pull/7142) supplies a positive funded split at a different helper and boundary. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.

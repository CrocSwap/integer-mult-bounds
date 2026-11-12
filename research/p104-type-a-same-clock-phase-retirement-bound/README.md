# Same-clock Type A phase retirement with two paid queries

**NO VERIFIED GAIN.** The complete comparison witness is
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ
`0.00364665195644`, with the exact signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

Retiring two productive q factors across 96 Type A ports gives a
positive optimistic invoice if two rank-one QUERYs can be saved.
For the pinned caller, keep the four QUERY clocks, all 17 J stages
and all other literal operations. Grant arbitrary q-even rational
coefficients at those clocks and any two rank-one factor differences.
At unit bodies the required q=+1 endpoint is I. The q=−1 endpoint
cannot be diagonal with two or more entries changed from −I. This
excludes all 630 two-root phase retirements in the declared class.

A rank reduction leaves six balanced sign patterns for the four
even coefficients. Independent forward and reverse replays agree
on 212 rank-two anchors out of 216 pattern and role checks. Each
pattern leaves at most one role unanchored, so any pair changes an
anchored diagonal. The fixed all-+1 erased endpoint also has a common
off-diagonal determinant 64 for every diagonal target and requires at
least four rank-one corrections. [Proof and directed prices](PROOF.md).

## Replay

From a clean checkout with CPython 3.12 and assertions enabled, run

```sh
python3.12 -I -B research/p104-type-a-same-clock-phase-retirement-bound/replay.py
```

The standard-library replay authenticates one signed caller payload
and both price inputs, regenerates eight exact receipts, compares the
independent decisions, and rejects altered dependencies and duplicate
path keys. Use `--out fresh-directory` to retain the receipts.
[Source provenance](PROVENANCE.json) · [Verification](VERIFICATION.md).

## Open next questions

Can one changed even operation or QUERY clock preserve the same
contract and permit a pair of phase retirements with a positive
complete price? Start by pricing one literal change, then reconstruct
both unit-body endpoints and test whether each residual has rank at
most two. The four remaining single-role anchor gaps do not establish
feasibility. Changed J stages, clocks, routing and wrappers, corrections
of rank greater than one, and nondiagonal targets are outside the
proved class. The best pair cannot pay for one extra rank-one field
on each port.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
supplies the complete comparison witness, and
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supplies the signed caller.
[#7309](https://github.com/CrocSwap/integer-mult-bounds/pull/7309)
supplies the neighboring relative-rank bound at the original target.
[#7342](https://github.com/CrocSwap/integer-mult-bounds/pull/7342)
supplies the nearby fixed-cut formal pair repair and its open physical
two-return gate. This package tests changed productive diagonals and
covers all pairs with the same-clock even-scalar reduction.
[#7316](https://github.com/CrocSwap/integer-mult-bounds/pull/7316)
studies the same rank-137 roots with the paid profile fixed.
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supply the base invoice and directed tariff.
OpenAI Codex and subagents materially assisted proof, implementation,
independent verification and packaging.

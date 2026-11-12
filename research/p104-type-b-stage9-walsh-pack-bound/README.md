# Type B stage-9 Walsh packing bound

**NO VERIFIED GAIN.** This package tests one literal even Type B idle at clock 2866, role 36 and all eight mapped ports. The independently reproduced comparator remains [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, κ = 0.00364665195644.

The exact phase displacement occupies at least 23/32 of each fixed parked fibre. One rank-seven-or-smaller child occupies at most half, so it cannot replace this rank-eight idle with identity erasure and a fixed bypass. The existing two-conversion Walsh lowering adds eight rank-eight paid positions globally. Its raw saving is strictly below −63.232 even when ancillary work is free. These bounds rule out the two scoped proposals before construction. Realized saving and Δκ are zero. [Proof and price](PROOF.md).

From a clean checkout on POSIX, use CPython 3.12 with assertions.

```sh
python3.12 -I -B research/p104-type-b-stage9-walsh-pack-bound/replay.py
```

The Git-free replay authenticates the exact caller, literal Gaussian gate, complete #7334 invoice, and predecessor quote. It regenerates a directed price receipt and a separate Gaussian-integer forward/adjoint receipt for all 256 width-one basis columns. It also corrupts the selected caller event in a disposable copy and checks that the input is rejected. [Verification and exact source pins](VERIFICATION.md).

## Open next questions

Can an already-paid frame boundary supply an equivalent stage-9 Walsh representation? Identify both exact existing boundary layouts and prove all-input compatibility at this clock, then charge the complete conversion, ownership, routing, precision and tape costs before trying one construction. A changed parked-fibre layout, genuinely cheaper conversion, new erasure action or independently proved tariff requires a new scoped gate. Free indexing remains an optimistic price relaxation.

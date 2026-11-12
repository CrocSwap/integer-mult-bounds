# Bound common-plane growth through four helper directions

At the exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) word and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed caller, test a shared two-dimensional subspace added to any subset of the 482 pure interior public helper components. Initial and terminal charts remain fixed. Among 43,435 total planes, the test covers the 1,014 containing at least one of directions 365, 244, 327 and 371. Two exact methods give upper saving zero on all sampled planes, with 42,421 untested.

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-common-plane-growth-bound/replay.py
```

The [proof](PROOF.md) gives the reduction to cut capacities. The [verification](VERIFICATION.md) describes source pins and the independent controls. The contribution uses the same helper grouping as the R219 one-direction audit and retains its exact reverse index and residual-flow routines. Earlier source-specific grouping and frame precedents include [#7361](https://github.com/CrocSwap/integer-mult-bounds/pull/7361), [#7358](https://github.com/CrocSwap/integer-mult-bounds/pull/7358) and [#7386](https://github.com/CrocSwap/integer-mult-bounds/pull/7386). The directed pricing follows [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362).

## Open next questions

The result excludes the tested common planes under fixed endpoints. Untested planes, distinct plane choices per component, shrinking and endpoint changes remain open. An expanded search needs a new bounded scope and a positive fully charged price before construction. No conditional exponent gain is claimed.

# Capped signed weighted allocation at Gaussian height 490950

This isolated package installs ordinary heights `(8192,124649,524288)` and Gaussian height `490950` with the ordinary and Gaussian bookings inherited from [#8071 at 9555f2df](https://github.com/CrocSwap/integer-mult-bounds/commit/9555f2df027f4a182722f736c97e5efafa5382c6). It certifies conditional κ **0.003898214283192**, up exactly `0.000000000159942` from #8071, and strictly clears #8071's actual stopped ceiling. The new ordinary-limited crossing attains the stated capped three-stage rate supremum under the fixed bookings. [Proof and rates](PROOF.md) · [Exact signed invoice](RESULT.json)

The complete recurring log₂ C bound is `318292011`, down 60. Maximum native height stays `524288`, entry conversion stays `515` bits, and conservative serial fixed setup stays below `2^228`. The first terminal header becomes `2^1148553+4`. The same native, owned restoration, compiler, precision/tape and recovery premises apply.

Reproduce from a clean checkout with Git and CPython 3.12.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-capped-allocation-490950
```

All seven registered scopes authenticate and install the exact signed source. They check full price and signed inequalities, adjacent and old-profile controls, actual calendar and both native widths, exterior and nonzero nested returns, signed multiplication, and fixed setup. The physical coefficient fixture covers entry. Both tiers check signed operation and restored operands. Other resource and supplier classes require separate evidence.

## Open next questions

At the proved capped allocation ceiling, a profitable change must improve a charged cost or supplier inequality. A follow-up should price one distinct ordinary paid mechanism with an exact first-read and restoration witness. The full signed route, native shape and tape price must still hold before any new comparison.

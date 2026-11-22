# Two unsplit paid returns in the retimed Gaussian supplier

The extended profile uses the [#8053](https://github.com/CrocSwap/integer-mult-bounds/pull/8053) signed retimed supplier at `e25494616bf149217644ce08d949181ea3600e13`. The edit stops splitting two base-copy paid rank-one returns. Their indices in the raw paid order are 1,592 and 1,593, with tags `(return, 9977, 0, 91990)` and `(return, 9977, 0, 91966)`. Each whole rank-one return replaces two half-rank returns, in place on the same live owner. The two column blocks in the old request partition the new packet in native order. The native actions, inverse, and restoration follow the original chart transition for each column. Every paid dispatch still goes through the literal controller.

With 1,006 splits, the 54 cells serve all 105,216 productive and 564,142 paid labels. Every compatible cell descends by at least 5/4. A directed cut on the 1,008 unit-rank targets excludes 1,005 splits even if transport probabilities are allowed to vary. The compiler books Gaussian dyadic `133940467/2^35`; the old 1,008-split word has strictly negative raw margin there. The physical edit funds conditional **κ = 0.0038981730255**, with fixed carrier heights 60,000, 960,000 and 20,000,000. The exact increase over #8053's 0.0038981721342 is 0.0000000008913. The full price includes both suppliers and their 36/48 calls, geometry, tape, restoration, precision, and 54 strict and four functional signed checks.

## Replay

With CPython 3.12 and Git:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-gaussian-unsplit-returns
python3.12 -IB scripts/research_package.py --package research/p104-gaussian-unsplit-returns-installation
```

The exact predecessor wrapper, source manifest and compiled archive from #8053 are kept under `peer8053/`. The preparation script authenticates them, applies the literal adapter and weighted price replacements at unique source sites, and verifies the full candidate cost. It reuses the now-shared #8052 and #8042 archived dependencies. The unchanged signed compiler retains five inherited obligations for all columns, ownership and restoration, uniform compilation, tape and precision services, and analytic recovery. Production-scale dispatch is outside the measured scope.

## Open next questions

Further savings need another legal change to the wave of positively priced requests. Reconstruct the complete rank and tag schedule and settle the corresponding 5/4 support cut before attempting any additional departure edit.

## Credit

SYLforge supplied seven binary reductions, the signed retimed package, and inherited verification in [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052). Ali Romman supplied the 48-call, two-scale Gaussian source, literal supplier and compiler in [#8042](https://github.com/CrocSwap/integer-mult-bounds/pull/8042). Clear1nsight supplied retimed price and signed finance in [#8050](https://github.com/CrocSwap/integer-mult-bounds/pull/8050). [#8053](https://github.com/CrocSwap/integer-mult-bounds/pull/8053) supplied the fixed-carrier comparison. The nested archive preserves its notices and original credit. OpenAI Codex assisted materially.

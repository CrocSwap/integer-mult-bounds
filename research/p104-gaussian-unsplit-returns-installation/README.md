# Installation and weighted receiver replay

This companion runs two verification modes of [the Gaussian construction](../p104-gaussian-unsplit-returns/README.md). Both modes use its exact installation and receiver code, signed price and pinned archive. The remaining six modes run in that package. Run both bounded packages to reproduce the complete result.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-gaussian-unsplit-returns-installation
```

## Open next questions

Compare the observed Linux and local wall times for the same installation and weighted-receiver checks before reducing either mode's timeout. The scientific coverage is shared with the primary construction.

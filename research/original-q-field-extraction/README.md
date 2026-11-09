# Original-q full-field extraction

**An actual encoded T-to-S boundary for the current normalized recovery
carrier; no new kappa.** The fixed-inventory `Extract` controller selects
the original tensor image `floor(t_i*j/s_i+1/2)` from a complete dyadic
target field, with axis zero fastest. It copies common-grid q+3-bit
components exactly and preserves arbitrary nonselected hole contents
on the borrowed input.

The universal proof gives
`O(n_addr^3 + log(q+1) + T(q+n_addr))` complete time and
`O(H_borrowed+Sq+n_addr+log(q+1))` backing, where `H_borrowed`
includes all retained historical capacities of borrowed ports. With the retained fine family's
`n_addr=Theta(p0)` and `q=Theta(p0)`, this boundary costs O(Tp0) time.
Its backing is O(Tp0) under explicit bounded-history admission; the
live field length alone does not imply that admission. Borrowed ports
enter at their origins, or entry movement is charged separately.
Its prepared T/S clocks, packed-axis scans, input and output rewinds,
copying, erasure, descriptors and retained storage are included. No
coordinate list, variable tape inventory, free clock or sparse RAM is used.

Canonical GAUSSIAN already states the monotone projection; its novelty is
not claimed. This package supplies the literal encoded controller,
same-grid consumer binding and proof of the full invoice. Canonical
CoreAssembly joins already-compressed source cores and is a different
boundary. See [OVERLAP.md](OVERLAP.md) and [PROOF.md](PROOF.md).

## Reproduce

```sh
python -B scripts/research_package.py --package research/original-q-field-extraction
python -B scripts/check_research_commit.py --package research/original-q-field-extraction --check-modes
```

The registered normal/optimized checker authenticates sources, checks
32,385 exact recurrence coordinates and executes genuine native Count
controllers on T4/S3, T32/S15 and T256/S105 fields. Expected JSON status:
`PASS`. Tests include wrong floor/axis/padding controls and ownership,
framing, source-guard and full-field-extent rejection. No Gaussian,
production transform, FFT scalar, CRT or carry routine is replayed.

## Open next questions

Can a production controller deliver its completed normalized q+3 field
in the original ungathered target order, bind the same `(ell_i,s_i)`
packet and actual radius/error, then call this extractor and the public
deferred-recovery codec with the exact S descriptor? This package closes
the extractor implementation boundary only. A fast grouped Broad source,
the complete production transforms, CRT/carry caller and the five
foundational assumptions remain obligations.

Prepared for @CubeJerry with substantial OpenAI assistance. Credit the
canonical construction, CrocSwap/integer-mult-bounds#3851, the retained
sequential Tape/Count authors, and the public normalized-recovery package
at `1ab10aa78c4b27345c76806d1d32c7b9de481219`.

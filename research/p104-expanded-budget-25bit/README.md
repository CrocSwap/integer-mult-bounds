# A 25-bit enlarged-budget signed P104 profile

This source-bound experiment retunes ToikY's [#8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072) at `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`, while retaining its ordinary K7 word, two-type Gaussian word, and paid finite-factor bookings. It gives a **conditional** rate of `κ = 0.00389846` for ordinary heights `(8192, 38102, 604362)` and Gaussian height `18845936`. Heights are logarithms: height `H` represents native rank `2^H`.

The complete terminal recurring invoice is `log₂ C = 4354317571`, up from `318292011` in #8072. The first terminal public header is `2^19497094 + 2`, and conversion of the entry interval costs 8744 bits. The positive height uses 25 bits, so this result explicitly adds an installer charge; it does not fit the predecessor's fixed caps. [Invoice and boundaries](PROOF.md) · [Exact receipt](RESULT-460.json) · [Fixed-installer argument](SETUP-PROOF.md)

The declared invoice is the smallest in the stated three-stage high-fibre tariff family: the check rules out a smaller ordinary height sum and a smaller Gaussian height at this rate. It is not a lower bound on all machines. The result is conditional on #8072's five supplier, ownership, chronological compiler, precision/tape and analytic-recovery premises. It does not execute a terminal-scale multiplication or constitute independent admission or a selected-frontier change. The gap to `0.0039` is `0.00000154`; the unchanged positive supplier itself has a strict ceiling below `0.0039`.

With CPython 3.12, assertions enabled and Git, run the scopes from this directory:

```sh
python3.12 -I -u -B verify.py 460 price
python3.12 -I -u -B verify.py 460 calendar
python3.12 -I -u -B verify.py 460 raw
python3.12 -I -u -B verify.py 460 exterior
python3.12 -I -u -B verify.py 460 nested
python3.12 -I -u -B verify.py 460 product
python3.12 -I -u -B verify_setup.py 460 setup
python3.12 -I -u -B check_parent_pins.py
```

The product scope uses a POSIX `fcntl` lock shared with sibling checks; `P104_PHYSICAL_PRODUCT_LOCK` can select its path. The terminal upper-cutoff check traces the authenticated opening with exact symbolic powers and proves the integer inequalities, while verifying literal small-height agreement; it does not allocate the billion-bit terminal powers. The fixed installer check executes the source constructor and directory census with lazy native openings forbidden, constructs the actual positive carrier, and charges the enlarged serial envelope. It does not claim a new WASI trace.

[#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057), [#8055](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) and [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052) provide the credited signed source, fixed setup, and K7 physical circuit. The archive retains their notices and license.

## Open next questions

Can a different positive source fund `0.0039` after all finite, owner-return, compiler, precision, and fixed setup charges? Such a source and a complete caller require a new independently checked construction. The five inherited premises and the boundary between finite fixtures and the all-size caller also remain review obligations.

The lower-profile predecessor [#8078](https://github.com/CrocSwap/integer-mult-bounds/pull/8078), head `b72d3fa097d2521939f6b8536029da674648d863`, established the earlier 20-bit allocation and economic-control method on which this higher-width follow-up builds. The high result independently charges and tests the larger installer and rate.

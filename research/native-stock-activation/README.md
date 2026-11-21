# Smaller live matrix stock and earlier activation of the fast multiplier

Replace a large cyclic ternary address by a product of shorter cycles. The new address still holds every independent record. One invertible matrix, reduced to each cycle, now serves all of them. Apply this change at each of the six ordinary stages, process the numerical tensor in stripes, and build the Fourier program on narrower square sides. Together these changes lower the input length at which the actual general multiplier uses all its native stages on data that determines the returned product. The complete proposed exponent remains $\kappa=0.00387992803556$. [Complete algorithm and proof](INTEGRATION.md) · [Numerical thresholds and measurements](RESOURCES.md) · [Verification](VERIFICATION.md)

| Quantity | Previous six-stage multiplier | This construction |
| --- | --- | --- |
| Address values per $w$-trit atom | $3^w$ | $3^w$, with independent payload at every address |
| True high matrices for each invertible low | $3^{N^2(w-1)}$ | $3^{N^2(u-1)}$ with $u=\max_j b_j$ for balanced components of total width $w$ |
| Temporary backing at the same $n$, above the persistent tensor and I/O banks | At least $\Omega(n)$ for a genuine full CRT shuttle | $O_F(n/\sqrt{\log n})+2^{O((\log\log n)^2)}+S$ for the complete fast-path schedule |
| Physical private Fourier compilation at the same $s=\lceil\log_2(p+2)\rceil$ | First dense root alone holds at least $2^{131072s^3}$ scalar entries | Entire private coefficient setup and erasure within $2^{2^{20}(s+1)^2}$ tape steps and bits on the stated tail |
| $\log_2 p$ to run all six ordinary stages inside a genuine complex source | Necessarily greater than $470632530120481927710843371$ | $3840000000000000$ suffices at every later length |
| Internal ranks and installed bound | $N=2^{240000000000000}$, $M=2^{3300000000}$, $S\le N^{20000}$ | Same finite ranks and fixed setup envelope |
| Complete time and peak storage | $S+O_F(n(1+\log n)^{1-\kappa})$, $S+O_F(n)$ | Same exponents, with fewer compulsory configurations and less temporary backing |

Here $n$ counts operand bits and $p=6\lceil\log_2 n\rceil$. A sufficient input bound for the connected call is $n\ge 2^{\lceil 2^{3840000000000000}/6\rceil}$ bits. It remains beyond any practical implementation. The comparison divides an old **necessary** logarithmic threshold by a new **sufficient** one. Neither a single geometric axis nor the fast finite fallback is the activation criterion. The best wall-clock crossover and the least recurring constant are unknown. [Native width derivation](MODULE-ATOMS.md) · [Connected source and outer threshold](OUTER.md)

In the two-trit physical instance the minimum number of independent records fell from 25,509,168 to 314,928. At the *same* 25,509,168 records, an unstriped split-atom route retained the old peak. With 81 stripes, total logical backing fell from 618,597,324 to 109,673,676 bytes. Its additional backing fell from 516,560,652 to 7,637,004 bytes. Reads, writes and explicit head seeks together rose from 17,052,878,808 to 43,582,413,528 byte positions. The data changed between routing and restoration, and both endpoints matched. These figures are for a single complete matcher direction. [Measured receipts](EVIDENCE.json) · [Equal-input controls](STRIPED-BACKING.md)

The full numerical file test produced $-741503\cdot466013=-345550037539$. Its five nonzero pre-carry coefficients were $11811,10996,4152,868,77$. Numerical components, the 36-call binary and 48-call complex programs, the compiled ownership and the fixed-head transfer are independently testable below their actual cofinal ranks. The all-size conclusion uses a written construction plus the kernel-checked statements listed in the verification record. No cofinal input or complete production-rank forest has run on hardware. [Signed product checks](check_binary_io.py) · [Raw numerical word](COMPLEX.md) · [Lean coverage](VERIFICATION.md)

The base is revision 8 of the canonical priorities. The previous complete construction is the 480/264-factor proposal. The seven-stage 451-factor price requires a different physical realization. The current selected result on main remains separate. [Pinned baseline](https://github.com/CrocSwap/integer-mult-bounds/pull/7868) · [Seven-stage proposal](https://github.com/CrocSwap/integer-mult-bounds/pull/7863) · [Selected result](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json) · [Coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/7880) · [Attribution](NOTICE.md)

## Open next questions

Can a smaller, genuinely invariant family replace the full invertible low rows? This would reduce the surviving factor greater than $3^{N^2}/2$. A first test is to compute actual matcher orbits on the compiled role transitions with the placements kept distinct. The obstacle is the requirement that every paid child receive all independent productive outputs in a common restored chart.

Can the repeated full scans in striping share a smaller buffer with fewer head reversals? Compare blocked schedules on the same independently changed records while preserving the reserved controls. A faster route must also close the dense and sparse CRT bills and the numerical operator on a full width-dependent stripe.

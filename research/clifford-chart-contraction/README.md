# One Gauss sum for a compact width-13 Clifford observation

Given a compact 104-bit observation from Ali Romman's absolute-phase Clifford circuit simulator, this package evaluates the complete identity-coefficient row of #7800 with **at most one quadratic Gauss sum**, on at most 52 binary variables. The row's 4,265 signed terms share 22 affine address sets. All have the same linear directions. Their Fourier coefficients therefore reduce to rotations of one value, including for observations outside the Clifford-mixture span. [Proof and cost model](PROOF.md)

| Exact test | Result |
|---|---:|
| Full row on a normalized, explicitly off-image observation with support $2^{104}$ | $2^{-29}$ |
| Single active cell on that observation | $2^{-31}$ |
| Same cell on a family specified by 104 binary phase-mask symbols | 104 reads, 208 head moves, input head restored |
| Fixed lookup data for this tape consumer | 401 bytes |

The off-image example has unequal amplitudes on two inputs related by a register swap, which every vector in the Clifford-column span preserves. A separate product of six four-bit Fourier sums checks the full result. The tape count applies to one identified cell with the phase bits supplied in the declared layout. For general circuit-produced observations the package instead accounts for the chart arithmetic, precision and working storage. A selected-multiplier input supplying such a chart remains an open obligation. There is no change to κ.

## Replay and use

Run from the repository root with CPython 3.12 and its standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-chart-contraction
python3.12 -I -B research/clifford-chart-contraction/verify.py
python3.12 -I -B research/clifford-chart-contraction/verify.py --tape
python3.12 -I -B research/clifford-chart-contraction/contract.py research/clifford-chart-contraction/INPUT.json
~~~

The last example returns exactly **−1/32** for the first nonzero probe in #7800. The JSON takes a #5704 gate array in `circuit` and an optional nonnegative 104-bit computational address in `initial`. It produces the chart, evaluates the row, and reports the exact real/imaginary rational parts, input byte count, and producer/consumer counters. In Python, `contract(state)` accepts an engine signature directly. `one_cell` evaluates one explicitly weighted Walsh cell. Proof-relevant source bytes are authenticated at startup. [Frozen source index](RETAINED.json)

The verifier compares all 4,233 frequency values for all admissible phases with zero constant through dimension three against literal enumeration. It exercises 22 source-produced small-support circuits (one in each shift), four normalized 13-fold Clifford columns including global phase, the full-support off-image fixture, and 137 phase masks on the priced cell. The checks are finite evidence supplementing the general proof.

## Sources and credit

apoursh prepared this package with substantial OpenAI Codex and separate agent assistance, under Apache-2.0. apoursh's #7800 supplies the signed decoder row and its access problem, building on #7799 and the Clifford/Bell, spectral and Pauli lineage of Ali Romman, Nick Petalas and alephnan. Ali Romman's #5727 supplies the exact Gauss routine and affine solver, and #5704 supplies the compact circuit producer. Quadratic stabilizer simulation and Fourier transforms of quadratic phases are classical. The frozen source retains the original attribution and Apache license. [Signed decoder row](https://github.com/CrocSwap/integer-mult-bounds/pull/7800) · [Exact contractions](https://github.com/CrocSwap/integer-mult-bounds/pull/5727) · [Circuit signature](https://github.com/CrocSwap/integer-mult-bounds/pull/5704) · [Original notices](source/engine/source/PR5704-NOTICE.md) · [Public claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19754144)

## Open next questions

1. Does a named multiplication supplier naturally expose this phase mask or a bounded sum of these charts? Bind one producer's actual output bytes and address order, quantify chart count and acquisition, and price restoring its working state.
2. Can several target coefficients share a single elimination on a concrete producer? First derive the target's shift equations and absolute phases, then compare their kernel and polar form with the identity target's. Other coefficient rows need their own source binding.

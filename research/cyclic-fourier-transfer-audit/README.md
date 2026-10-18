# Audit: sharpen the prime-power cyclic inverse's Fourier transfer

**Status: independent Sobolev/Fourier audit of PR621. No new kappa.**

Publication context: Rafael Guevara (@alephnan) concurrently submitted
[PR803](https://github.com/CrocSwap/integer-mult-bounds/pull/803), which proposes
a stronger degree-controlled inverse-gap estimate. This package retains a
separate elementary Sobolev proof and exact regression evidence; it does not
claim the best currently proposed conditioning bound.

The incorporated PR621 proof controls a cyclic inverse using a uniform circle
separation `delta` and derivative bound `M`. Its Fourier step bounds the inverse
norm by `delta^-1 + 2 M delta^-2`. Applying an elementary periodic Sobolev
estimate gives the stronger bound

```
||P(tau Z_L^w)^-1||_infinity^2 <= delta^-2 + (44/7) M delta^-3.
```

It applies to every length, integer stride (including zero and noncoprime
strides), and unit complex scalar. It includes constant polynomials. For fixed
positive `M`, this changes the separation dependence from inverse-square to
inverse-three-halves. The new rational estimate is strictly better when
`M/delta > 4/7`, which includes every prime-power kernel covered by PR621.
The old bound remains valid; this is an overestimate audit, not a defect report.

The [written proof](PROOF.md) establishes the all-length statement. It uses
finite Fourier polynomials and total variation before taking a limit, so it
does not assume the absolute convergence being proved. This is an application
of classical Sobolev/Fourier ideas, with no general-inequality novelty or
optimality claim.

## Reproduce

Python 3.10+; standard library only. From the repository root:

```sh
python3 -I -O -B research/cyclic-fourier-transfer-audit/verify.py --source-root .
python3 -I -O -B research/cyclic-fourier-transfer-audit/test_contracts.py
```

Expected: `PASS_CYCLIC_FOURIER_TRANSFER_AUDIT`, then
`26 prime-power budgets; 200 exact Fourier sequences`; eight tests `OK`.
The first command recomputes and compares the entire [receipt](EXPECTED.json),
including all 648 exact finite inverse cases. The optional `--source-root`
checks five exact predecessor/selected-record pins. Without that option the
package runs independently of the repository and does not check those pins.
Use `--output NEW_PATH` to create an additional receipt; existing files are
never overwritten.

## What changed quantitatively

These are the smallest integer ceilings of `log2` of the **proved upper
bounds**, using PR621's unchanged `delta_r` and `M_r`; every comparison uses
exact integers/rationals. They are not actual inverse norms, execution
precision requirements, measurements, or savings in required fractional bits.

| Radix r | Old log2 ceiling | New log2 ceiling | Reduction |
|---|---:|---:|---:|
| 3 | 28 | 21 | 7 |
| 4 | 53 | 40 | 13 |
| 5 | 165 | 124 | 41 |
| 7 | 510 | 382 | 128 |
| 8 | 455 | 340 | 115 |
| 9 | 870 | 651 | 219 |
| 11 | 2206 | 1652 | 554 |
| 16 | 3843 | 2879 | 964 |
| 25 | 23997 | 17992 | 6005 |
| 27 | 25267 | 18944 | 6323 |
| 32 | 31735 | 23794 | 7941 |
| 49 | 197545 | 148147 | 49398 |
| 64 | 258011 | 193493 | 64518 |

The receipt covers all 26 prime powers in 3..64, not only the displayed rows.
The general proof, conditional on PR621's circle theorem, covers every
prime power r>=3 and every primitive root choice. The logarithmic asymptotic
order remains `O(r^2 phi(r))`. The separate radix-two bound of two is retained.

## Evidence and precise scope

- 200 exact rational Fourier magnitude sequences check the Sobolev estimate;
  three controls catch omitted constant mode, underpriced derivative, and
  omission of negative-frequency derivative energy.
- 648 Gaussian-rational polynomial inverses compare dense Gauss-Jordan against
  a separately implemented finite-geometric factor oracle and both inverse
  identities. The six polynomial fixtures include complex constants, inner,
  outer, mixed complex roots and zero constant coefficient. They are **generic
  polynomial fixtures, not actual cyclotomic-kernel replays**.
- Lengths 1..9, strides -2/0/3 and gauges 1/-1/i/(3/5+4i/5) are fully crossed.
  Rational square-root enclosures certify the row-norm bounds. Six controls
  test wrong direction, gauge/coefficients conjugation, reversed coefficients,
  a unit-circle zero, and a concrete nonunit-gauge counterexample.
- Eight contract tests cover exact logarithmic ceilings, comparison threshold,
  constant mode, admission, prime-power scope and changed source rejection.

The seed changes fixture ordering and the 100 rational-sequence samples;
there is no open-ended search. All declared finite coverage completed.
[Validation](VALIDATION.md) records actual checks and exclusions.
[Review](REVIEW.md) describes separate AI-assisted derivation and scrutiny.

## Dependencies, overlap and attribution

Original research base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Publication base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
The publication-base selected record is
`1661202643272239/1000000000000000000`; this package does not modify or
audit that construction. The historical selected-record hash is retained in
`SOURCE.json`, and the four mathematical predecessor pins remain unchanged.
[Source pins](SOURCE.json) identify Ali Romman's incorporated PR621 at
`520774462b19b29af41554b74def31f9d01e997e`. No predecessor code is imported.

This is distinct from PR668's CRT resultant verification, PR666's composite
lifting, PR628's rounded algorithms, PR764's inverse-square **scan-rounding**
bound, and PR796's nonarchimedean kernel-root valuations. Their contributions
and full selected-construction lineage retain credit. The original metadata
refresh ended at PR802. The publication refresh through PR824 identified
PR803 on the same conditioning step: its proposed bound is
`(1+4 degree(P))^2 / delta`, using root reflection, arc-length and Hardy
arguments. At fixed degree it has inverse-gap exponent one, compared with
three-halves here for fixed positive M. It is pending review and is not
independently certified or imported by this package. PR820 separately audits
radix-9 coefficient enclosures and factor residuals. No priority or strongest
current bound is claimed. [The local claim](CLAIM.md)
records the scope and initial alternatives.

Prepared for **Thiago Costa (@ThiagoCAltoe)** with substantial **OpenAI Codex
assistance**, including derivation, implementation, writing, and separate
agent reviews. There is no independent human or maintainer approval.
See [NOTICE.md](NOTICE.md) and the Apache-2.0 license.

No paid coefficient preparation, rounded execution, restoration, tape circuit,
combined precision guard, supplier construction or full multiplication theorem
is established here. The selected frontier and `upstream/` are unchanged.

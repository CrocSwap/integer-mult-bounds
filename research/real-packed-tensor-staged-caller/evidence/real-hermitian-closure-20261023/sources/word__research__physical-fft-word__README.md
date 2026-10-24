# Physical FFT word multiplication

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0; I retain the predecessor archives and their notices.

I implement exact unsigned n-bit multiplication in the retained fixed-tape
model, with `O(n log2(n+2)^2)` time and `O(n)` space. I use the classical
radix-digit/FFT reduction through corrected [PR3709](https://github.com/CrocSwap/integer-mult-bounds/pull/3709),
head `62264289adb01f3ba4930cd0154c75887f96203c`. Its internal Karatsuba
multiplier remains unchanged, so the dependency is acyclic. I give the
all-size argument in [PROOF.md](PROOF.md) and separate finite execution
coverage in [EVIDENCE.md](EVIDENCE.md).

The caller supplies two canonical nonnegative Count magnitudes and a
positive width n, with both magnitudes below `2^n`. I return exactly 2n
raw LSB-first bits, preserve borrowed values and heads, and restore owned
scratch. The caller must consume the protected output before reuse.
`FftWord()` uses the retained word engine through 16 bits and the actual
FFT path above that fixed cutoff. I also exercise the retained signed
`Arithmetic.multiply` consumer with this new word owner.

For the FFT branch I choose `b=ceil(log2 n)`, `q=ceil(n/b)`, minimal
`r=2^ell>=2q`, and `p0=2b+ell`. I pack each digit as `a_i/2^b` and
call the complete normalized product with A=C=1, including its second
zero record. Since `2^p0=r*2^(2b)` and the degree is below r, I recover
ordinary integer convolution coefficients as the returned real
numerators. Sequential radix carries give the exact word. I include
unamortized twiddle setup in the cost bound.

This closes a scalar-arithmetic implementation gap for the retained
Gaussian resampling schedule. With delta=.0001, I can charge its
arithmetic at power .9981, below the inherited full Fourier power
.99827619697. I have not implemented that Gaussian caller here. The
Gaussian coefficient producer, guarded convolutions, factor-page access,
window restoration and complete CRT/integer join remain open. I retain
PR3709's numerical proof obligations and the selected frontier.

## Reproduction

Use Python 3.12 and the standard library from the repository root:

```sh
python3.12 scripts/research_package.py --package research/physical-fft-word --check-only
python3.12 scripts/research_package.py --package research/physical-fft-word
python3.12 scripts/check_research_commit.py --package research/physical-fft-word --check-source-history
```

I register seven suites in [VERIFY.json](VERIFY.json), with a 600-second
maximum for the full FFT sequence and a 960-second sum of command
timeouts. The tests check actual FFT products at widths 17 and 19,
base calls through 16, isolated codecs through 1,024, encoded geometry
through width `2^257+7`, and malformed packet/ownership controls.
The codec and metadata cases do not claim full FFT execution at those
larger widths. The checks use explicit failures under optimized Python.

I retain the complete corrected product export in `inputs/ring-export.tar`.
The loader checks its SHA256, complete member inventory and nested source
bindings before importing one shared physical runtime. I declare the two
Gaussian cost reports as live inputs in [SOURCES.json](SOURCES.json).
The official committed export also includes them for replay outside Git.

## Coordination and attribution

I recorded the five-point expansion decision before implementation in
[Discussion3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664).
I started from main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, and retained the `uniform-transfer-audit` card. [TASK.json](TASK.json)
records scope, overlap coverage and remaining questions. I follow the
arithmetic handoff from [PR3763](https://github.com/CrocSwap/integer-mult-bounds/pull/3763);
this word algorithm does not invoke its chirp caller or a T74 supplier.

I credit the standard FFT/radix reduction and Karatsuba algorithm,
PR3709's numerical implementation and exact recovery proof, Mason Hale's
[PR2313](https://github.com/CrocSwap/integer-mult-bounds/pull/2313) certified
interval reference, Dugongue's [PR2790](https://github.com/CrocSwap/integer-mult-bounds/pull/2790)
scalar-ABI precedent, the retained rad20 Gaussian reports and the nested
source notices. Codex assisted the mathematics, implementation, source
analysis, checks and prose. I claim author verification of this package;
I do not claim independent human or formal-kernel review.

## Open next questions

- Can a physical Gaussian expansion/compression pair use this scalar API
  within its complete cost allowance? First implement one guarded
  Toeplitz convolution and its coefficient producer from the pinned
  phase-cell source. A complete caller still needs factor-page access,
  layout, normalization and window restoration.
- Can a reviewer validate the normalized-product precision and exact
  recovery proof on which this adapter depends? First check PR3709
  Sections 3–4 against the retained implementation and its recovery
  controls. A finite successful product does not discharge that all-size
  numerical argument.
- Can the mixed-radix CRT entrance and return preserve the valid interval
  and padding through the full Gaussian/chirp caller? First specify an
  actual field conversion and check its interval endpoints. The complete
  CRT/Gaussian/integer join remains outside this package.

# A smaller fixed machine for general integer multiplication

The complete mixed-rank multiplier can run with a polynomial-size generated native machine, a ternary binary cover and the same proposed saving $\kappa=0.00387992803556$. The construction removes the stored invertible-matrix directory and the tape bank indexed by every low type. It retains the actual independent data, full high fibres, six ordinary stages, physical precision and integer recovery. Its fixed machine is still far beyond available hardware. A separate component of the same length dispatcher gives a measured improvement on ordinary binary inputs. [Full setup and runtime proof](STREAMED-MACHINE.md) · [Carrier and price proof](CARRIER-PROOF.md) · [Finite execution and comparison](PRACTICAL.md)

| Quantity | Pinned complete proposals | This construction |
| --- | --- | --- |
| Binary dimension | $2^{1285200000000000}$ | $2^{240000000000000}$ |
| Complex dimension | $2^{15171300000000000000}$ | $2^{3300000000}$ |
| Ordinary radix and cold digit buckets | $q>2^{6426000000000045}$ and $q^2$ buckets | $q=3$, nine buckets |
| Fixed setup and installed machinery | Eager low table alone has $\log_2\log_2 S>2570399999999999$ | Complete upper $S\le2^{4800000000000000000}$ |
| Low-type splitter at $L=B\lvert\mathrm{GL}_N\rvert$ | $L+7$ heads and at most $94V$ steps | Five temporary spools and $O((1+\log_3 L)V)$ steps |
| Ordinary stock guard | Necessary $\log_2 e>2580722891566266$ in old radix digits | Sufficient $\log_2 e\ge481927710843386$ in trits |
| Complete time and storage | $O(n(1+\log n)^{1-\kappa})$, $O(n)$ | Same exponents; full setup, data movement and restoration priced |

The comparison pins the [480-factor complete price](https://github.com/CrocSwap/integer-mult-bounds/pull/7830), its [uniform realization](https://github.com/CrocSwap/integer-mult-bounds/pull/7846) and the [direct Fourier consumer](https://github.com/CrocSwap/integer-mult-bounds/pull/7849). The canonical main record at the checked revision selects 0.00363005817. The larger pending price and its complete construction have written proofs. Independent scientific acceptance remains open. A proposed ceiling for 17-stage signed words and a linear-time structured-input multiplier address different contracts. [Selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json) · [Signed-word obstruction](https://github.com/CrocSwap/integer-mult-bounds/pull/7852) · [Structured-input result](https://github.com/CrocSwap/integer-mult-bounds/pull/7851)

A 451-factor variant posted during verification reports a higher conditional κ of 0.00387992804346, with binary log₂ N of 1,202,400,000,000,000. Its exact consumer receipt retains five premises. The seven-stage physical and precision transfer, including its completed seed, is open. The resource comparison here uses the 480-factor six-stage construction with a written complete realization. The difference from the 451-factor candidate is 0.00000000000790 in κ. [PR #7863](https://github.com/CrocSwap/integer-mult-bounds/pull/7863) · [451-factor proof and limits](https://github.com/CrocSwap/integer-mult-bounds/blob/b3e4412fe01f07dc58305616fabf96345f49a781/research/p104-bit-451-factor-schedule/PROOF.md) · [Consumer receipt](https://github.com/CrocSwap/integer-mult-bounds/blob/b3e4412fe01f07dc58305616fabf96345f49a781/research/p104-bit-451-factor-schedule/CONSUMER.json)

**How the components compose.** Each finite-order coordinate job can occur once or five times. The compiler uses that freedom to eliminate complementary recursive jobs. Source and paid occurrence labels still come from the genuine 36- and 48-call words. A shifted logarithmic induction funds smaller binary and complex carriers and a worst-case rank-one correction. Every compiled binary basis has a small-factor representation valid at 3. An alternate diagonal pivot costs at most nine same-width children. Thus the recurring proof can use ternary low fields without a large-prime probability bound. The streamer visits the full matrix cube temporarily, reorders all genuine payload with bounded buckets, then removes the singular rows before the next child. The integer caller consumes these same exact ordinary exchanges and positive complex layers. [Chronology and ownership](PERIODIC.md) · [Ternary leaf](TERNARY-COVER.md) · [Factor words](FACTORED-ROUTES.md) · [Cube and type routing](STREAMING.md) · [Two-stack child handoff](SERIAL-LOW.md)

At 33,554,432 bits per operand, the finite compiled branch took 1.170 seconds, the pinned Python implementation 126.519 seconds and GMP 0.169 seconds on the checked arm64 host. Those are medians of three full products. The C arena was 64 MiB. At 4,194,304 bits the new process used more peak resident memory than the pinned Python program. No measured run reached the cofinal native branch or established its crossover. A proof of a uniform reduction in the *least* complete recurring constant is also open. [Raw data](MEASUREMENTS.json) · [Resource derivations](MACHINE.md)

From the repository root, run the registered portable checks with CPython 3.12.

```sh
python3.12 -B scripts/research_package.py --package research/bounded-general-multiplier
```

For the compiled finite path, build and run the public CLI.

```sh
p=research/bounded-general-multiplier
cc -std=c11 -O3 -fPIC -shared "$p/short_product.c" -o "$p/short_product.so"
python3.12 -IB "$p/multiply.py" 741503 466013
python3.12 -IB "$p/check_product.py" "$p/short_product.so"
```

The small CLI input uses its specified base case. The product check exercises the full direct FFT regression as well as the compiled packed branch. [Verification, Lean replay and coverage](VERIFICATION.md) · [Attribution](NOTICE.md) · [Coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/7853)

## Open next questions

- Can a new cover retain the same freshness and all arbitrary-input operators with fewer than $N^2$ ternary high digits per level? The low-directory removal still requires those physical high values.
- Can the full numerical-to-tape compiler be formally refined to the fixed-head stream programs and give a numerical global recurring constant? The written proof presently composes several independently verified parts of that machine.

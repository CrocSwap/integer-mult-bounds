# A signed Gaussian suffix integral

This package prices the actual matched suffixes in the two-type Gaussian calendar, installs an `e−6` physical compiler, and combines it with the ordinary K7 suffix tariff of [#8073 at `cf4c4b7`](https://github.com/CrocSwap/integer-mult-bounds/commit/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e). The resulting **conditional** sample rate is **κ = 0.003898222531555482**. It is below the requested `0.0039`, and it does not change the selected upstream result.

The decisive estimate is an integral over all actual edge bins, not a bound on an individual suffix. The proof, its finite error accounting and the independent controls are in [INTEGRAL.md](INTEGRAL.md); the complete compiler, charged-return argument and source history are in [SIX-COLUMN-PROOF.md](source-view/SIX-COLUMN-PROOF.md). [CAP-THEOREM.md](CAP-THEOREM.md) covers the stated fixed-price families of one through seven ordinary stages. The separate [e−8 appendix](EIGHT-COLUMN.md) gives a second source-bound priced example.

Since this #8073-based comparison, ToikY's [#8076 at `d502eb2`](https://github.com/CrocSwap/integer-mult-bounds/commit/d502eb21637717fe22fc16d4c4e3ede6ec59a106) has reported conditional κ `0.003898223617430` using a reduced ordinary child tariff and its additional charges. That reported rate is `0.000000001085874518` above the e−6 sample here. The Gaussian integral and compiler are complementary to that ordinary change, but this package does not install or reprice them together; its fixed-price cap does not automatically transfer to #8076.

## Complete sample invoices

`b` lists ordinary terminal heights, `G` the Gaussian height, and `log₂ C` is the complete recurring upper bound including the selector and the entry-to-terminal conversion. All four rows retain the same entry profile `(3000,3080;1024)` at κ `0.00345`; its own `log₂ C` is `125660241` before conversion. Terminal `log₂ C` is one less than the complete bound in these samples. The public header identifies the first terminal activation; it is a sufficient threshold, not a practical crossover claim.

| Sample | κ | `b; G` | ordinary / Gaussian debit | terminal `log₂ B` | complete `log₂ C` | conversion bits | first terminal header |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- |
| [#8072](https://github.com/CrocSwap/integer-mult-bounds/commit/75f7e1c44f48c43983016bcf8878c4d9e5e87c62) | `0.003898214283192` | `(8192,124649,524288;490950)` | `11239/8192`, `64939/524288` | `210281408` | `318292011` | 515 | `2^1148553+4` |
| [#8073](https://github.com/CrocSwap/integer-mult-bounds/commit/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e) | `0.003898219753506` | `(8192,117168,524288;501831)` | `11204/8192`, `64939/524288` | `207887488` | `318291911` | 517 | `2^1151953+4` |
| e−8 appendix on #8073 | `0.003898221247474783` | `(8192,121057,524288;496174)` | `11204/8192`, `130699669/2^30` | `209131968` | `318291851` | 516 | `2^1150185+4` |
| e−6 on #8073 | `0.003898222531555482` | `(8192,124612,524288;491002)` | `11204/8192`, `125645/2^20` | `210269568` | `318291611` | 515 | `2^1148568+2` |

For the terminal rows, the source invoice computes `log₂ B = 128 + 320 Σbᵢ`, `terminal log₂ C = max(84500001, 1602 + 220G + log₂ B)`, and `complete log₂ C = 1 + max(entry log₂ C + conversion, terminal log₂ C)`. Thus the displayed terminal branch has `1731 + 320 Σbᵢ + 220G` as its complete clock. This is a bound under the source tariff, not an empirical runtime. Entry conversion is actually checked; it is not silently assumed free. Maximum native height stays `524288`, and the inherited conservative serial fixed-setup bound remains below `2^228` in each case.

The source carries both native words and all paid occurrences. The ordinary K7 word has **36 native calls**, 18,906 productive labels, 104,652 paid labels and 24 exact transfer shares. The Gaussian word has **48 native calls**; its two real types each have 52,608 productive labels and respectively 282,576 and 281,568 paid labels. With actual weights `(5,451)`, this means 23,989,248 weighted targets and 128,400,048 weighted paid labels across 51 occupied grade pairs and 88 typed cells. The two call counts are per literal native word, not a claim that the whole recursive installation executes only 84 calls. Both paid words, physical widths, owned returns and their complete clock remain charged.

The exact published #8073 stopped ceiling is `523210198560303585338978849681/134217728000000000000000000000000`. The e−6 rate exceeds it by `372863481514645917150319/134217728000000000000000000000000`, about `2.7780494206744873×10⁻⁹`; its gain over #8073's booked rate is exactly `1389024741/500000000000000000`. Its complete clock is 300 lower than #8073 and 400 lower than #8072; its first-header exponent is 3,385 lower than #8073 and 15 higher than #8072. It exceeds #8072's exact three-stage stopped ceiling by `1107076595744764976049263/134217728000000000000000000000000`. The remaining gap to `0.0039` is `0.000001777468444518`.

These are conditional signed claims under five inherited all-size premises: (1) the stated signed native all-column action, (2) owned allocation and restoration, (3) chronological compiler transfer, (4) fixed-alphabet tape, movement and numerical precision, and (5) analytic recovery. The proofs and bounded executions do not establish these premises from first principles. In particular, a finite fixture is not a production-dimensional multiplier run or an upstream admission. See [EVIDENCE.md](EVIDENCE.md) for what was actually observed and what remains unrun.

## Reproduce

The sparse registered runner uses CPython 3.12 and the standard library:

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-integrated-gaussian-suffix
```

Each of the seven declared commands also works as `python3.12 -I -B research/p104-integrated-gaussian-suffix/verify.py MODE`, with `MODE` one of `price`, `calendar`, `raw`, `exterior`, `nested`, `product`, and `setup`. The runner rejects optimized Python, authenticates the archive and all 28 whitelisted members, checks the review copies against those bytes, and reconstructs in a fresh temporary directory. Each requested named scope must return zero with a matching recorded stdout digest; successful completion of one mode does not assert success of another. The `price` mode also rebuilds the e−8 signed invoice and independently checks both finite factors, an actual positive source grant, and the stage-cap and minimum-clock calculations. The `calendar` mode additionally checks the literal event identity. The dense physical product is expensive; run one product job at a time on a shared worker.

The packed source is a deterministic, publication-minimal derivative of the frozen research replay: it replaces the full public GitHub files response with the fifteen needed public filename/blob pairs. Its SHA-256 is `1ffaf4eed67cfe2271820bc94d62721573ff715829c829c5d9936b561eacb270`. It preserves #8073's source blobs and the unmodified #8057 peer archive. The source files except that nested archive are also visible under [source-view](source-view); their byte identities are enforced by the wrapper. The nested upstream archive retains its license and notices. [Provenance](SOURCES.json) · [Inputs and commands](VERIFY.json) · [Attribution](NOTICE.md)

## Open next questions

Can a different signed native word or a justified new supplier charge close the remaining gap to `0.0039`? A useful next step is one exact source-to-reader and restoration witness with a complete changed invoice; the fixed-family cap here does not exclude different words, costs, budgets, interfaces or stage rules.

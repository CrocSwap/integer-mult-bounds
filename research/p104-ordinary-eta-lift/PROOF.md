# A source-pinned ordinary clamp lift

## Scope and result

The source is ToikY's [PR #8072 at `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`](https://github.com/CrocSwap/integer-mult-bounds/pull/8072). Its unchanged binary source has `c_B = 4391986206293/2^50`; its paid finite debit is `D_B = 11239/8192`; its child contraction remains `375/376`; and its actual ordinary floor is 18,960. The archive and patch are restored by `witness.py` after checking the recorded PR metadata, the retained changed-file Git-blob digests, SHA-256 pins and the `#8057` member manifest. The offline check binds bytes to those recorded pins; it does not independently establish that Git contains the stated head. The optional source-history check in the README compares all retained files with that Git commit when it is available. The old fixed-allocation and height-cap claim remains unchanged.

Set

```
κ_target = 39/10000
g        = 1/10^18
q        = κ_target + 5g = 780000000000001/200000000000000000
ρ        = 1/250
η        = 1/256
H        = (8192, 106000, 1681001)
```

Starting at `b₀=0`, let `Uᵢ = (249(c_B-D_B/Hᵢ)+bᵢ₋₁)/250`. At the first two stages book one whole `10^-21` tick below the floor of `min(η,Uᵢ)`; book `b₃=q`. The three strict margins, in order, are

```
1827798949 / 1073741824000000000000000000000
7792038038789 / 7113539584000000000000000000000000
18375833487309615126701 / 1804961079885824000000000000000000000
```

The last is about `1.0181e-14`. With the first two heights fixed, `H₃=1681000` fails, and `1681001` is the least passing integer. The original last-height cap 524288 fails even with the raised η. The old η=0.0039 fails for every height because the booking is strictly larger. These are scoped controls, not a global minimum over height vectors.

The admissible interval for **the retained parameter and geometry gates and this fixed booking** is exactly

```
q < η < 1/250.
```

Both endpoints are excluded by strict inequalities. The first two unclamped stage prices are below `q`, and the final unclamped stage price exceeds `q`, so all three rate inequalities hold throughout that interval. The source requires `η<ρ`; this is not a claim that all algorithms outside the interval are impossible. This interval concerns the mathematical geometry and stage pricing. A fixed cost for computing an arbitrary rational exponent additionally depends on the size of its numerator and denominator. The concrete executable and fixed-clock claim here uses `η=1/256`, not an unbounded-encoding assertion for every rational in the interval.

## Geometry, transfers, and clocks

Let `e` be an admitted field width, `w=max(E_prev+1,ceil(e^ρ))`, and `g_e=ceil(e^η)`. Since `η<ρ`, `g_e≤w`; the source splits `w` into `m=ceil(w/g_e)` balanced components. Each used component has width `u` satisfying `g_e/2≤u≤g_e`. With the admitted predecessor floor and `w≤e`, the existing scan has `mc≤2e^(1-η)` for its actual `c≤e/w`; also `m≤2w^(1-b_prev)` since `b_prev<η`. The native and earlier-stage return terms therefore retain the strict price `bᵢ<min(η,Uᵢ)`. The upper/lower physical shears, weighted terms, inherited ownership and restoration are unchanged and remain subject to the source's five stated premises.

For this interval `η>q>97/25000>1/258`, `2η>ρ`, and `η+bᵢ<1`. Thus the source's first-stage `w+1≤9u²` and high-stage `w+1≤2^259 u^258` estimates remain valid. At `H≥8192`, `u>2^30`; the source's `2660000(j+2)<2^j` for `j≥30` still absorbs the coefficient setup into its exposed fibre. The high-stage charge remains `Nᵢ^320(1+B_prev)`. The small entry stages retain their original 25,818,582-bit surcharge. For the concrete `1/256`, the implemented component root is `ceil_root(e,256)`: the same binary-root algorithm uses a fixed degree below the former degree 10000, and input/output lengths are bounded by the source's retained per-prefix polynomial. This does not establish a uniform clock for arbitrary rational encodings.

For the quotient reserve, use `Tᵢ=ceil((2Hᵢ+64)/(1-η))`. At η=1/256 the `Tᵢ` values are `(16513,212896,3375251)`. A single interval-wide upper guard obtained with `η<1/250` is `(16515,212916,3375569)`; each is below `3Hᵢ<8Hᵢ`. The source's admitted direct/quotient reserve proof therefore has the same inequalities with the new `Tᵢ`. Exact stage cuts are `(8290,114354,1795419)`. The source's connected selector gives `A=2286624`, first public header `2^A+2`, and first/all-size stripe margins 1,141,254/1,105,612. The recorded storage bound remains the source's conditional `6.2pT<297.6n` at its certified connected entrance.

The executable replay checks the source's all-size ordinary-floor hypotheses at its smallest stated `H=1024` guard and checks all three candidate recipes use the identical labelled binary word, coupling, trial and floor. Literal dispatch and balanced layout are exercised at the changed ranks in both the direct and quotient regimes, using mathematically exact roots on dyadic test widths and a captured backend. Separate nondyadic cases use the actual 256th-root implementation. Two small physical signed weighted-tape fixtures return their owners and reject incorrect signs. The captured backend and finite fixtures do **not** execute the full astronomical target geometry or prove the five inherited scientific premises.

## Complete signed control and the actual boundary

The unchanged Gaussian trial is `17145637307/2^42 ≈ 0.00389846657230919`, already less than `q`, even before its positive finite debit. At the original Gaussian height 490950 the exact priced margin at `q` is

```
-58834182535661561655779 / 32947096780800000000000000000.
```

The 54 strict and four functional non-Gaussian expressions pass at κ=0.0039, but the actual Gaussian check rejects the combined target. Hence no κ=0.0039 result is claimed. A changed Gaussian word or its independently funded source price remains necessary.

As a directed resource comparison only, keep #8072's original κ=`0.003898214283192`, its actual Gaussian height and debit, and use the larger ordinary profile and η. The original signed budget accepts that old κ, including an independently checked stronger ordinary `q`. The unchanged source's price calculator gives `log₂ B=574461888`, terminal `log₂ C=682472490`, entry conversion 1025 bits and complete `log₂ C=682472491`. #8072 reported `318292011`; this is a larger resource class, not a no-cost improvement. The activation exponent changes from 1,148,553 to 2,286,624. The fixed setup argument and its scope are in [SETUP-PROOF.md](SETUP-PROOF.md). No full all-size target installation, new portable trace, or physical crossover is asserted.

## Credit

ToikY supplied #8072's exact capped allocation and the authenticated retune of the earlier result. Ali Romman supplied the [#8057 frequency-weighted signed source](https://github.com/CrocSwap/integer-mult-bounds/commit/cbe847a953b971f9c6c5a0a6661e2008acd29086), the inherited native setup and the physical compiler and caller. SYLforge supplied the K7 word in [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052). The retained [source notice](original/NOTICE.md) records the other contributors and prior work. This local component arithmetic, clamp analysis and setup scaling received substantial OpenAI Codex assistance.

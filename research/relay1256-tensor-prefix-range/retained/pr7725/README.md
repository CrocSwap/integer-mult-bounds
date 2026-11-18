# Sharp physical prefix range on the role-1256 graph

The largest absolute real or imaginary component of an ordered row-accumulator prefix is **51,863,149/8** on one nine-axis tile of the forward role-1256 graph. Every real and imaginary entrance component may vary independently in $[-1,1]$. Terminal row 156140 attains the maximum in chart 127 immediately after its eleventh donor, key 103886. Address zero of the real output suffices.

This answers the single-tile accumulator case of Ali Romman's chart-valued range question. His normalized scalar maximum is $53{,}895{,}757/256$. Applying the largest possible nine-axis chart gain, 32, to that result gives $53{,}895{,}757/8$. Using each entrance's actual chart lowers that upper bound by **254,076** and gives equality. [Scalar predecessor and open question](https://github.com/aliromman/integer-mult-bounds/blob/762a4d8c541081be987f2fdf9053d4d7b52990f4/research/relay1256-sharp-scalar-range/README.md)

## Why the bound is exact

Fix a prefix in chart $A$. Write $B_i$ for the entrance chart of public role $i$, $x_i$ for its physical complex field of 512 addresses, and $c_i$ for its rational coefficient in the normalized prefix. The physical value is

$$
\sum_i c_i T_A T_{B_i}^{-1} x_i .
$$

Every donor at the scalar operation is in chart $A$. A completed paid move from $D$ to $A$ acts by $T_A T_D^{-1}$. Multiplication of adjacent chart factors therefore cancels each intermediate inverse. All paths from entrance $i$ have the same operator, so their signed scalar coefficients add **before** taking an absolute value. This uses the exact ordered chart representatives of the pinned native graph. [Physical contract](https://github.com/Clear1nsight/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/PHYSICAL.md)

Let $d_i=\dim A+\dim B_i-2\dim(A\cap B_i)$, with the chart letters denoting their binary subspaces in this expression. This is the Fourier rank of $T_A T_{B_i}^{-1}$. In the preimage-frame construction, $L_U$ consists of the pairs $(u,u+v)$ with $u\in U$ and $v\in U^\perp$. Hence $L_A\cap L_{B_i}$ has dimension $\dim(A\cap B_i)+9-\dim(A+B_i)$, and its codimension in a frame is $d_i$. [Frame construction and transition rank](../../notes/general-clifford-frames.tex)

A rank-$d$ Gaussian Clifford factors into a Gaussian monomial, $d$ coordinate Fourier factors, and a second Gaussian monomial, with identity factors on the remaining coordinates. The monomials permute addresses and multiply by powers of $i$. Each row of the middle operator has $2^d$ nonzero entries. Each is $((1+i)/2)^d$ times a power of $i$, since the two coefficients of a single Fourier factor are $(1+i)/2$ and $(1-i)/2$. For even $d$ each entry lies on a real or imaginary axis and has magnitude $2^{-d/2}$. For odd $d$ its real and imaginary parts each have absolute value $2^{-(d+1)/2}$. Summing the absolute real and imaginary coefficients of one real output component gives the same gain at every address,

$$
g(d)=2^{\lceil d/2\rceil}.
$$

The imaginary output has the same gain. The triangle inequality bounds the prefix by $\sum_i |c_i|g(d_i)$. To attain it, choose an output address and component. Within each entrance, choose the sign of every real and imaginary input component to agree with its coefficient in that output, including the sign of $c_i$. Independence permits all of those choices at once. This proves the formula for each prefix separately. [Exact native maps](https://github.com/Clear1nsight/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/NATIVE.md)

## Finite certificate

The forward scan computes this sum at all 172,414 nonempty prefixes of the 7,644 scheduled rows. On each update to a coefficient it charges the change in its absolute value at that entrance's chart gain. A second calculation starts with only the eleven donors of the winning prefix and substitutes earlier rows in reverse order over the rationals. The two calculations agree on all 448 nonzero entrance coefficients.

| Component gain | Sum of absolute normalized coefficients at the winning prefix |
| ---: | ---: |
| 4 | 12,927/2 |
| 16 | 36,549/8 |
| 32 | 51,071,533/256 |

The sum of the three products is $51{,}863{,}149/8$. For a direct witness, the checker applies $T_{B_i}T_A^{-1}$ to the unit vector at address zero using the retained exact Gaussian interpreter. If an entry of this adjoint column is $a+ib$, choose the corresponding real and imaginary input components as $\operatorname{sgn}(c_i a)$ and $\operatorname{sgn}(c_i b)$. Set unused entries to zero. The real output at address zero attains the reported value. [Generated receipt](RESULT.json) · [Checker](verify.py)

## Reproduce

Run from the repository root with CPython 3.12 and its standard library.

```sh
python3.12 -I -W error -B research/relay1256-physical-prefix-range/verify.py
python3.12 -B scripts/research_package.py --package research/relay1256-physical-prefix-range
python3.12 -B scripts/check_research_commit.py --package research/relay1256-physical-prefix-range --check-source-history
```

The first command prints `PASS_RELAY1256_PHYSICAL_PREFIX`. Add `--emit` to write the computed receipt to standard output. The compressed source graph has SHA-256 `0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc`. The verifier also checks its decompressed hash and the chart interpreter hash before use. [Graph at the source commit](https://github.com/Clear1nsight/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/data/CANDIDATE-GRAPH.json.gz) · [Base source pins](SOURCES.json)

## Scope and credit

The result covers a single forward native invocation on one active nine-axis tile in exact arithmetic. An identity spectator repeats the same operator on each independent slice. Tensor repetitions of active axes, rounding, numerator temporaries, paid-child interiors, caller correlations and the common-root width require separate bounds. The five framework assumptions remain open. This result gives no new κ.

The physical component proof and finite certificate were produced by Nick Petalas. Ali Romman posed the physical-range question and derived the normalized scalar prefix method. Clear1nsight supplied the role-1256 graph and its physical chart contract. SYLforge supplied the parent word. The retained chart interpreter and the original graph notices credit their contributors. [Source credit](data/NOTICE) · [Retained notices](data/credits/) · [Discussion claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19714961)

## Open next questions

- What is the sharp prefix bound when the native repeats the active chart tensor? Determine each repeated transition's real-component gain before comparing prefixes.
- What range can one signed caller stage actually attain? Express its native entrances in common root coordinates before choosing input signs.

# Query any Clifford fibre and apply the width-13 Gram operator

For the four-qubit width-13 dictionary, a change of Pauli coordinates turns the full Gram matrix into **256 independent copies of one scalar convolution** on $\operatorname{Sp}(8,2)$. Given coefficient blocks on known source fibres, the program evaluates any requested target blocks of the Gram, its exact inverse, or either complete #7809 schedule. A second consumer evaluates the specified Bell inverse on arbitrary affine-quadratic observations. Every requested symplectic target shares one partial Walsh transform, including queries outside the Clifford column span. [Proof, absolute lifts and resource bounds](PROOF.md)

| Supplied input | Requested quantity | Work shared across queries |
|---|---|---|
| One 104-bit affine-quadratic chart | All 256 Bell decoder coefficients in each named fibre | One Gauss sum in at most 48 variables and one singleton basis. At most 4,265 signed bin updates per target. |
| Coefficients on $m$ complete source blocks, $r$ target blocks | $Kc$ or $K^{-1}c$ | Synthesize each source matrix once. At most $mr$ binary ranks or relative class lookups, and $256mr$ real-weight/complex-entry multiply-adds. |
| Starting coefficients $d_0$ and adjoint values $t$ on supplied supports | The final $d$ of either 51 or 52 updates $d\gets d+h(t-Kd)$ | Two scalar kernels compiled on 80 rational classes; the query cost depends on source and target counts and coefficient sizes. |

Here each omitted source fibre has zero coefficients. General observations can have dense $A^*y$ and $By$; preparing their complete supports has a separate cost. For a known mixture $y=Ac$, the first normal-operator query gives $A^*y$ directly. The minimum common denominators for the compiled inverse Gram, 51-step pair and 52-step pair have bit lengths 145, 11,381 and 7,500, respectively. This contribution concerns decoder arithmetic at the existing width and multiplication bound. [Class recognition and reproducible GAP table](CLASS-ALGEBRA.md) · [Independent spectrum](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/RESULT.json)

Ali Romman's #7815 recovers *unknown* support from a supplied exact tensor train, including any 19 four-qubit terms at width 13. Its complete output can supply the mixture above after rephasing the reported columns. Read its signature as $W_{\mathrm{output},\mathrm{input}}$, with signature index $16\,\mathrm{input}+\mathrm{output}$. Identify $S$ by conjugating the eight basis Weyls. If its normalized unitary $W/(1+i)^h=\eta W_pU_S$, multiply its coefficient by $\eta^{13}$ to express it in this package's convention. The 256 trace coordinates of `extract` identify $p$ and $\eta$. [Tensor-train decoder and signature format](https://github.com/aliromman/integer-mult-bounds/blob/34a20a30596467409e7361534d52495819787a78/research/clifford-unknown-support-decoder/README.md)

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-transported-fibre-gram
```

`readout.py input.json` accepts the #5704 `circuit`, optional `initial` address and `targets`. A target is the array of eight column images in the four-qubit binary Pauli convention. The output order is $16x+z$ with Gaussian rational pairs. The two independent readout oracles check every transported record at four targets, complex phases on literal tensor columns, and arbitrary nonmember observations. [Readout](readout.py) · [Oracle](verify_readout.py)

`gram.py input.json` accepts the actions `gram`, `canonical`, `schedule51`, and `schedule52`. The first two take one list of source blocks. The schedules take two lists giving $d_0$ and $t$, respectively. Within each block, omitted Pauli indices are zero. Exact rational strings are accepted. For example, this request applies $K$ to the identity coefficient and asks for the fibre of a single X-axis transvection. The Pauli-identity output is $(-1+i)/128$.

```json
{"action":"gram","inputs":[[{"target":[1,2,4,8,16,32,64,128],"coefficients":{"0":["1","0"]}}]],"targets":[[17,2,4,8,16,32,64,128]]}
```

The ordinary/optimized checks regenerate the filters, compare actual scheduled convolution factors in the class basis, and test literal thirteenth powers of complex traces, including zeros and nonzero odd-dimensional fixed spaces. [Gram consumer](gram.py) · [Independent checks](verify_gram.py) · [Verifier manifest](VERIFY.json)

## Open next questions

Which observation producers admit a direct compact description of $A^*y$ on a few fibres, or of its sum against the compiled scalar kernels, even when $y$ lies outside the Clifford span? An end-to-end estimate would include producing those values, moving them to this interface and delivering the requested outputs.

## Credit

The affine-quadratic signature and Gaussian contraction machinery are due to Ali Romman, with their retained notices. Nick Petalas and Ali Romman provided the fixed-space character calculations and spectral blocks, building on alephnan's Clifford sector work. The Bell compiler, compact identity-fibre consumer and scalar schedules are earlier work by apoursh. The native class construction uses the GAP Group's software. This extension and verification were prepared by apoursh with substantial OpenAI Codex assistance, under Apache-2.0. [Source pins](SOURCE-PINS.json) · [Retained notices](retained/predecessor/source/engine/source/) · [Public collaboration claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19756386)

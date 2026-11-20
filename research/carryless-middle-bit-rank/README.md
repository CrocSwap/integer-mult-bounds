# How much carryless multiplication does one integer product bit need?

Let each operand of an ordinary integer multiplication be encoded separately into binary polynomials. Multiply each designated pair of polynomials over GF(2). How many input coefficients must the encoders supply for a decoder to recover bit $m-1$ of the integer product? This bit includes carries from the lower positions. The channel list is fixed before either input is known. A decoder sees the returned coefficients and may use a fixed constant. Width counts every encoded input position, including a hardwired position.

| Operand domain and decoder | Exact minimum encoded width on each side |
| --- | --- |
| All $m$-bit operands, affine decoder, $m\ge2$ | $\lfloor 2^{m-1}/3\rfloor+\lfloor 3m/2\rfloor-1$ |
| Odd $m$-bit operands, affine decoder, $m\ge3$ | $2^{m-3}+1$ |
| Odd $m$-bit operands, arbitrary decoder, $m\ge3$ | $m-1$ |
| Odd inputs, bits $m-2$ and $m-1$ together or full product modulo $2^m$, arbitrary channel list and decoder | $m$ |

At $m=5$, for example, the affine minimum on odd inputs is five coordinates per operand. An explicit width-four circuit recovers the same bit for all 256 pairs, using **18 AND and 35 XOR gates** for both encoders, the polynomial product and the decoder together. Its three decoder ANDs are minimal for the published encoding. Gates are two-input, with free fan-out, static wiring and hardwired constants. Width measures a different resource from gate count.

## Proofs and witnesses

- The exact binary rank of the matrix $M[x,y]=\operatorname{bit}_{m-1}(xy)$ gives the affine answer. Eliminate the sign block, then the valuation-zero cyclic block. The remaining pairing reduces from $m$ to $m-2$. A rank factorization gives matching encoders with one polynomial product. At $m=16$ the answer on the full domain is 10,945 coordinates per side. [Full and odd rank proof](raw/PROOF.md)
- For odd operands, write an input as a sign times a power of five modulo $2^m$. Each input contributes one exponent class, and the desired bit depends on the sum of the two classes. A binary field with $2^{m-1}-1$ nonzero elements retains every possible unreduced sum. The count of distinct nonconstant target rows proves matching lower bounds, even with multiple unequal channels. The explicit single-bit decoder has $2^{m-1}-1$ reachable table entries. Requesting the next lower bit separates every pair of previously indistinguishable operand rows. A single jointly mixed channel of width $m+1$ per side also recovers the full odd product modulo $2^m$. [Width theorem and construction](ODD-WIDTH.md)
- The five-bit witness uses a quadratic decoder. It includes literal encoding masks, a shared gate schedule and an exhaustive lower bound for that encoding. It also gives degree bounds for wider inputs. [Circuit and gate proof](nonlinear/PROOF.md) · [Gate invoice and controls](nonlinear/RESULT.json)
- For a digit $j$ of each convolution coefficient *before* carry propagation, the exact minimum sum of shorter channel widths is $\binom{\min(m,n)}{2^j}$. A translation-shape construction attains it at every output position simultaneously, including rectangular inputs. [Separated digit theorem](planes/PROOF.md)
- A separate reviewer checked the proofs, recomputed literal ranks, and independently enumerated the five-bit circuit and the all-size construction. [Review and interface assumptions](review/review.md)

## Relation to κ and earlier work

The frozen comparator is [PR #7830 at 87fbf4f](https://github.com/CrocSwap/integer-mult-bounds/pull/7830/commits/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15). Its conditional lower bound is 0.00387992803556 and its fixed-profile directed upper endpoint is 0.003879928046155. The full-multiplier target for this experiment is 0.003884928046155. This package establishes exact bounds for a **single-bit interface**. A uniform table-free implementation covering even inputs and all required output bits, an admissible caller and its complete signed price are open. The credited κ gain is zero.

Following Bryant’s earlier middle-bit fooling-set argument, Jayram S. Thathachar used communication matrices to obtain exponential rank lower bounds for middle-bit multiplication in work on ordered representations. The exact GF(2) formula and matching channel constructions here have independent proofs. [Thathachar, *On the Limitations of Ordered Representations of Functions* (1997)](https://dada.cs.washington.edu/research/tr/1997/02/UW-CSE-97-02-01.pdf)

The adjacent repository results study the capacity of a propagated carry, finite-field first-success slices and an ordinary carry chain for Gaussian multiplication. The comparator supplies the target price, with no tape or supplier edits reused. A title/body search of 7,663 indexed revisions covering 7,305 distinct PRs through #7837, together with canonical package-name and live PR searches, found no earlier repository statement of these exact channel-width results. This establishes the scope of the search. [Carry capacity #6252](https://github.com/CrocSwap/integer-mult-bounds/pull/6252) · [Finite-field slices #6552](https://github.com/CrocSwap/integer-mult-bounds/pull/6552) · [Gaussian multiplication #7834](https://github.com/CrocSwap/integer-mult-bounds/pull/7834)

## Reproduction

From the repository root with Python 3.12 on Linux, run

```sh
python3 -I -B research/carryless-middle-bit-rank/verify.py
python3 -B scripts/research_package.py --package research/carryless-middle-bit-rank
```

The first command needs only the Python standard library. It compares fresh output with the published certificates, disregarding only machine-dependent timing, limits and memory fields. Its success marker is `PASS carryless middle product bit`. Coverage includes both literal rank tables through $m=12$, 2,867,152 pre-carry digit comparisons and 349,520 odd-input pairs in each of the independent single-bit and full-residue field constructions. The second command checks package registration and source pins and invokes the same verifier.

## Open next questions

For six-bit odd operands, one joint carryless product needs at least six coordinates per side for bits four and five together. Seven suffice for the entire product modulo 64. Can a single width-six product recover both bits with fewer gates than separately computing them? A decisive first check is the row separation and return collisions of a proposed encoding on all 1,024 input pairs, followed by the gate bill for both encoders, the product and the decoder.

## Credit

Prepared by Clear1nsight with substantial OpenAI Codex assistance. Separate agent assignments produced the affine proofs and five-bit gate witness, and another assignment independently reviewed them. The supplied all-size proofs are mathematical arguments, with finite runs as reproducible controls. Package provenance is pinned to canonical main `e54523517d0f03e58352e647c403a5af3e525a57`. [Task and attribution](TASK.json) · [Source pins](SOURCES.json)

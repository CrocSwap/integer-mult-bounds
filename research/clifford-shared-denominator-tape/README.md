# A reversible terminal divider for Clifford coefficient readouts

The four-qubit width-13 inverse Gram kernel has a 145-bit shared odd denominator. On a tape holding a signed numerator and a supplied binary scale, this package converts the corresponding rational coefficient to any requested binary output precision. The local gate program implements Euclidean division, exact remainder delivery, truncation and nearest-even rounding. The numerator can be any signed integer. For a Gaussian coefficient run its two components sequentially. [Gate program](tape.py) · [Locality, resource and latency proofs](PROOF.md)

The 80 rational classes of #7816 give the following *least common* denominators after reducing every coefficient of the specified kernel or pair. Factoring out the dyadic scale determines which conversion an actual coefficient array needs.

| Four-qubit width-13 source | Shared odd divisor | Binary scale |
|---|---:|---:|
| Canonical inverse kernel | 22,742,436,009,630,709,072,767,882,717,680,300,149,753,125 | 0 |
| Pair of kernels for the 51-step optimal-norm schedule | 470,624,175 | 11,352 |
| Pair of kernels for the 52-step dyadic schedule | 1 | 7,499 |

Source magnitudes and Pauli basis changes can carry additional scale. After the inputs are expressed over the chosen common denominator, a long dyadic tail below the requested precision stays in place as low remainder bits. It participates in a single rounding test. The odd division only processes the high numerator digits. For a short magnitude the signed wrapper automatically pads the input to at least one digit above the tail. At precision zero the actual 7,499- and 11,352-bit tails still occupy that many tape sites, including padding, and their sticky scans incur linear movement. [Source reconstruction and literal coefficient](check_sources.py) · [Published Gram kernels](https://github.com/apoursh/integer-mult-bounds/blob/7e7e62c62fcccd11f5c8e22677b4523863a48f4b/research/clifford-transported-fibre-gram/PROOF.md)

For a fixed odd divisor $D$, a most-significant-bit-first Euclidean quotient transducer requires **exactly $D$ distinguishable states** between input bits. An exact lockstep transducer for $L$ independent component streams requires $D^L$. The tape construction visits a window of $k+1$ data sites for each divided digit, where $k$ is the modulus bit length. Its ordinary digit circuit uses exactly $29(k+1)+3$ NOT, CNOT and Toffoli gates, including advancing the modulus one site. A common-denominator register and an output bank may be reused across calls. The proof gives the entire-program invoice, including retreating the modulus, rounding, scratch closure and head return.

Nearest rounding changes when a high output bit becomes knowable. For an $n$-bit integer divided by odd $D>1$, put $v=v_2((D-1)/2)$. A nonconstant rounded output bit $j>v$ first becomes determined for *every* input after exactly $n-v$ most-significant input bits. For the canonical four-qubit divisor, $v=1$. For the five-qubit canonical denominators at widths 15 and 16, $v=0$. Arbitrarily high nonconstant quotient bits can therefore depend on the last input bit at those widths. [Latency witnesses and prefix-tree replay](check_latency.py)

As a physical example, take the identity-class coefficient of the actual width-13 inverse kernel. Its 32-fraction-bit nearest readout gives $4580344441/2^{32}$. With the shared denominator above, the circuit uses 326 eight-track sites, 209,200 NOT, 260,239 CNOT and 365,064 Toffoli gates and 311,724 one-site head moves. This is an upper bound for one terminal conversion in the stated local model. Occupied coefficient construction, numerator scaling and transfer to the converter are upstream obligations in a complete supplier.

## Reproduce

Use CPython 3.12 and the standard library from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-shared-denominator-tape
```

From this package directory, `python3.12 -B convert.py -15 3 1 0` converts $-15/(3\cdot2)$ to the nearest integer. It returns $-2$, with magnitude remainder 3 modulo 6. The sign, retained rounding flag and remainder reconstruct the exact rational input. Pass `--truncate` to truncate toward zero. The package checks the bit-gate map against exact fractions, reverses the complete gate lists on all small inputs and independently computes when each output prefix becomes determined. [Signed conversion](convert.py) · [Exhaustive physical replay](check_tape.py) · [Source hashes](SOURCE-PINS.json)

## Open next questions

1. Can a producer supply these scaled numerators directly as local streams at useful precision? Price at least one complete nonidentity Pauli output, including its symplectic lookup, numerator accumulation, rounding and movement.
2. Is there a lower gate or motion bound stronger than the finite-state and latency obstructions for a named tape layout? Start with intermediate block sizes between one bit and one full residue and compare the cost of moving precomputed constants.

## Attribution

apoursh's #7805, #7812 and #7817 established the canonical denominators. The 51/52 schedules and transported kernel come from #7809 and #7816. Their underlying Clifford and character calculations credit Ali Romman, Nick Petalas, alephnan, GAP and the GAP Character Table Library. The binary restoring quotient and majority carry are classical arithmetic. This submission binds the published denominators to an explicit local reversible program, exact gate and head invoices, a residue-state lower bound and a sharp rounding-latency result. Prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. [Collaboration claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19756931)

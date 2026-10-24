# Exact phase-scan reduction

This construction changes the payload execution of the retained PR2250
Gaussian phase pass. The phase polynomial, tensor convention, address order,
affine word and compact operations stay the same. The source proof remains
the authority for those contracts; this proof covers the new scan and bill.

## Domain

A complete declared address rectangle has M records, each with an integral
number of Gaussian coefficients. A coefficient is two b-bit two's-complement
words, real first, in least-significant-bit order, with b>=2. Put V equal to
the complete payload bit count. The source head initially has offset h from
its origin. Phase controls depend only on the current address, with the
retained tensor exponent f*p0+sum_j q(x_j) modulo four. For an inverse pass,
negate this exponent on the recovered input address. Let V_odd be the total
payload volume of records whose phase is odd.

The result is exact modulo 2^b in each component. It is also exact on signed
Gaussian integers when the usual symmetric headroom prevents overflow.
The most negative two's-complement word is included in the modular theorem;
it is not evidence that signed negation cannot overflow.

## Scan and correctness

For phase 0, copy both halves directly to the output. For phase 2, stream
the negation of each half directly. Reset the one-bit carry before each
half. The recurrence starts with carry=1 and emits the low bit of
1-input_bit+carry, then retains its high bit. Induction on the consumed
prefix proves two's-complement negation modulo 2^b.

For an odd phase, copy the real half into one scratch tape. Stream the
imaginary half directly to output, negating it for phase 1. Rewind scratch
and append the real half, negating it for phase 3. Erase scratch before the
next coefficient. The resulting pairs are (-imag,real) and (imag,-real).
Together with the even cases, these are exactly multiplication by i^phase.

Every branch consumes exactly one coefficient and appends exactly one
coefficient. It cannot mix record boundaries. Induction over coefficients
and records proves the complete endpoint. Finish and erase the consumed
input, rewind output and return with empty scratch at its origin. No
payload is addressed by an output index. Bulk copy abbreviates consecutive
bit reads and writes; the charge includes every bit.

The scan uses three payload roles in total: input, output and one real-half
scratch tape. Scratch has peak extent b, independent of the number of
records. The phase counter/arithmetic interface is inherited and separately
charged. The complete monomial wrapper uses the unchanged affine word,
compact operations and inverse chronology, so replacing only this phase
pass preserves its endpoint and ordinary-call inventory.

## Exact invoice

The following counts include input erasure, scratch clearing and output
rewind. They apply per R=2b coefficient when h=0.

| Phase parity | Reads | Writes | Erasures | Moves | Total |
|---|---:|---:|---:|---:|---:|
| even | R | R | R | 6R | 9R |
| odd | 3R/2 | 3R/2 | 3R/2 | 9R | 27R/2 |

In the odd branch, the extra half is copied to scratch, rewound, read,
rewound again and erased. These actions account for the complete extra
9R/2. The final source erase contributes its head return as well as its
forward erase and return. An initial rewind contributes h once.
Therefore the total is

```text
new = 9V + (9/2)V_odd + h
old = 18V + h
saving = 9V - (9/2)V_odd.
```

The old formula follows by counting both half-scratch paths in the unchanged
source. At h=0, the new payload bill saves at least one quarter and at most
one half. A nonzero initial head adds the same h to both bills; do not apply
the percentage to that extra charge. The number of control evaluations is
still M. No lower bound over all phase implementations is claimed.

For each actual event8814 right/left fixture, V=32768 and V_odd=16384.
The phase bill decreases from 589824 to 368640, exactly 37.5 percent.
This percentage is for the phase component, not a complete monomial,
recursive caller, runtime benchmark or multiplication exponent. The unchanged
affine/ordinary calls can dominate the full monomial cost.

## Evidence and remaining costs

The verifier checks all coefficient pairs of widths 2 through 6 in all four
phases, 768 tensor/polynomial/inverse patterns with nonzero initial heads,
the actual right/left recipes and both complete monomial directions. It also
checks a two-column compact fixture in both directions with arbitrary dirty
compact fields and identical ordinary-call inventories. An independent
integer oracle checks phase values. All measured bills must match exactly.

Three arithmetic discriminators distinguish inverse phase, missing carry and
missing odd-phase sign. Three malformed extents are executed and rejected.
Finite checks corroborate the scan proof; they are not its all-width basis.

Descriptor production, encoded phase arithmetic, the complete physical
caller, recursive child, precision and final supplier admission remain open.
This local constant reduction does not change the complete kappa calculation.
It does not replace the separate Word RAM cost model or Gaussian normalization
kernel. New work: Ali Romman with substantial OpenAI Codex assistance,
Apache-2.0. Jose Manuel and the retained source authors keep their credit.

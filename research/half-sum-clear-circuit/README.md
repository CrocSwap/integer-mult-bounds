# A smaller reversible circuit for one signed half-sum CLEAR

At signed width 1,076, this circuit implements the complete output map for the
eight-limb row at event 88937 with **93,811 gates and 15,103 internal zero bits**.
SYLforge reports 277,929 gates and 86,525 internal zero bits for the same row
in the general rational circuit. Specializing to four positive unit coefficients,
four negative unit coefficients and denominator two saves 184,118 gates and
71,422 work bits. Both counts include output copying and cleanup.
[Published comparator and source row](https://github.com/SYLforge/integer-mult-bounds/blob/e5ba67dfd6237a1a3acf4d67098d3242adee8229/research/clean-rational-clear-witness/README.md)

## Interface and scope

This is a scoped proof with an executable finite gate certificate. In SYLforge's
#7669 word, target 1502 uses donors 1072 and 500. The eight signed limbs are
the real and imaginary parts at addresses 0 and 102 of the first donor, then
the same four of the second donor. We use the real output at address zero
identified by #7687. The caller-to-row identification and the comparator counts
are taken from that work. The circuit accepts arbitrary donor bitstrings.
[Source word](https://github.com/CrocSwap/integer-mult-bounds/pull/7669)

For any positive width w, let N be the sum of the first four signed donors
minus the sum of the last four. Put q = floor(N/2). The circuit leaves donors
untouched, XORs the low w bits of q into the target, and toggles the diagnostic
if N is odd or q is outside the signed w-bit range. Every work bit starts and
ends zero. With initial diagnostic zero, both outputs are zero exactly when
N equals twice the signed target. In particular, a fractional quotient or
signed overflow stays detectable even if the target XOR produces zero.

## Construction and proof

Let n = w + 3. The largest possible N is 4(2^w − 1), attained by placing
the four maxima before the four minima. Swapping the groups attains its
negative. Both fit in signed n bits. Sign extension aliases the donor sign
wire as a control. Start with the first extended donor and accumulate the
other seven modulo 2^n. The final residue therefore encodes N exactly.

Each ripple stage uses fresh result bits and fresh internal carries. In a
column with accumulator bit a, operand bit b and incoming carry or borrow c,
first write p = a XOR b. Addition's outgoing carry is ab XOR cp. Subtraction's
outgoing borrow is (1−a)b XOR (1−p)c, or ab XOR b XOR cp XOR c. These formulas
follow by treating the equal-bit and unequal-bit cases separately. Both stages
then XOR c into p to produce the result bit. The low column takes c = 0 and
the top column discards its outgoing carry. This proves the modular stage
identity by induction over the columns. Donor wires appear only as controls.

The low bit of N flags oddness, including for negative N. Bits 1 through w
give the low w quotient bits because arithmetic right shift gives floor
division by two. The quotient fits exactly if bits w+1 and w+2 of N both
equal bit w. Two XOR comparisons and Boolean ORs therefore implement the
specified diagnostic. Copy the result bits and flag to the output ports and
run the internal gate list backwards. Each gate is an involution, and the
internal list never accesses the output ports. This restores every work bit
regardless of validity or initial target.

## Complete resource count

Each of seven stages allocates n result bits and n−1 carry bits. Two comparison
bits and two OR bits give 7(2n−1)+4 = **14w+39 work bits**. The external wires
are the 8w immutable inputs, w target bits and one diagnostic bit.

An addition uses 2n gates to form p, n−1 to copy incoming carries into the
result, n−1 for ab and n−2 for cp. Each of the four subtractions adds
(n−1)+(n−2) borrow toggles. The flag needs four CNOTs for comparisons and
three gates for each of two ORs. Thus the forward computation uses
7(5n−4)+4(2n−3)+10 = 43n−30 gates. Output copying costs w+1 and the reverse
costs another 43n−30, giving **87w+199 gates**. At width 1,076 the emitted
list contains 63,637 CNOTs and 30,174 Toffolis.

## Reproduce

From the repository root with CPython 3.12 and its standard library, run

~~~sh
python3.12 -B research/half-sum-clear-circuit/verify.py
python3.12 -B scripts/research_package.py --package research/half-sum-clear-circuit
~~~

The verifier simulates every gate, checks wire indices and donor immutability,
and compares every output and workspace wire with an integer oracle. It
exhausts donor tuples at widths one and two, then executes 32 cases at width
1,076, including negative odd numerators, both signed endpoints, wrapped
overflow and reproducible mixed inputs. It prints PASS_HALF_SUM_CLEAR.
The gate certificate establishes an upper bound for this row. Optimality,
rounded producer reachability, full erasure, tape costs and a change to κ
remain outside its scope.

## Open next questions

What does this circuit cost on the physical tapes? Fix a tape layout and
account for its clean banks, carry access, output copy and reverse scans.

## Credit

The specialized circuit, proof and verifier were produced by Nick Petalas.
SYLforge supplied the source word, the coordinate identification, the complete
validity interface, the published comparator and the smaller-circuit question.
Ripple arithmetic and reversible compute/copy/uncompute are standard.

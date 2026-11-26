# Fixed-head division by a short Walsh denominator

The modular Walsh executor uses a rational scalar on each independent residue. Its signed numerator magnitude and positive denominator are brought to the record as short bit strings. This primitive supplies their arithmetic and returns all word heads to their first digit.

## Interface and cost

The four input words are distinct, nonempty, low-bit-first and delimited on both sides. The modulus and residue have a common width $K$, with $M\ge2$ and $0\le x<M$. The two short words have at most $B$ bits and denote $|A|$ and $b>0$. A sign resides in finite control. If $\gcd(M,b)=1$, the output is the canonical $y\in[0,M)$ satisfying $by\equiv Ax\pmod M$. A nonunit denominator is rejected. High zero padding is allowed. A call uses at most 21 word tapes, visits at most $7K+16B+58$ cells including delimiters, and costs $O(KB+B^3)$ symbol reads, writes and unit head moves.

The implementation scans the actual digits. The four input contents survive. The output and cleared reusable work banks have fixed homes. The simulation counts one primitive operation for each read, write or unit move. Only the adapter's tape arrays and finite oracle index cells directly. The scalar program accesses the current symbol through these primitives. Its finite inventory, fixed loops over that inventory and bounded flags can be expanded to finite control. Fixed head offsets, transitions between scans and branches multiply the recorded cost by an absolute constant.

## Invariants

1. Scan the bits of $|A|$ from high to low, doubling then conditionally adding $x$. Reduce after each operation. The intermediate is below $2M$ and fits $K+1$ bits. Canonical negation gives $z=Ax\bmod M$.
2. For $b=1$ copy $z$. Otherwise calculate $M\bmod b$ by long division. After each prefix the remainder is below $b$, and the doubled prefix remainder including its next bit is below $2b$.
3. On short words use Euclid with $r_i\equiv t_i M\pmod b$. The updates use exact short division and keep both coefficients as canonical residues modulo $b$. Every two nonterminal remainders reduce at least by a factor of two. Hence there are $O(B)$ rounds at $O(B^2)$ head work each. A final gcd of one supplies $t=M^{-1}\bmod b$.
4. Compute $r=(-z\bmod b)t\bmod b$. Then $0\le z+rM<bM$ and $b$ divides $z+rM$. The final exact short division returns $y=(z+rM)/b<M$. The sign, zero and composite modulus cases follow from the same congruences.
5. Each long-by-short product or division makes $O(K+B)$ scans of at most $O(B)$ short digits, or $O(B)$ scans of at most $O(K+B)$ long digits. Rewinds and cleanup obey the same bill. All word capacities are determined from marked input lengths. In the long branch the four inputs, three long work/output words, twelve short words, and two long-plus-short words yield $7K+16B+58$ cells. The same banks can be reused across calls. The caller's transfer of coefficient and record to these heads is separately charged in the Walsh routing proof.

## Reproduction

Run `node modular-scalar-machine.mjs`. The shipped harness checked 2,520 unit inputs and 1,281 nonunits, including exact inverse comparisons, signed zero, padded words, Fibonacci Euclidean pairs and lengths through 128 modulus bits. An independent audit checked another 3,205 inputs. These included 440 successful cases with $B>K$. It inspected input contents, head returns, scratch erasure, visited extents and the formula for the output. These are finite executions and a source review. The bounds above follow from the loop invariants for all lengths. Full compilation of the adaptive Walsh program to OpenAI's Lean tape-command interface is open.

[Executable scalar](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/contributions/explicit-overhead/modular-scalar-machine.mjs) · [Walsh caller](modular-walsh.md) · [Numerical evidence](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S006/finite-replay.json)

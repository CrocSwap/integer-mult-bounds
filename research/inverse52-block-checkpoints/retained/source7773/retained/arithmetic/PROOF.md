# One reversible draw from a common phase residue

The fixed source graph assigns the four ordered outcomes weights
`(144,12,12,1)/169` in order 00, 01, 10, 11. At depth $k$, let $j$
be the index among unfinished prefixes in the source's order. Reading coin
$u$ gives child index $m=2j+u$. The next binary probability digits mark
one leaf per set digit in outcome order. Those leaves occupy the first child
indices. If there are $s$ leaves, child $m<s$ returns the $m$-th marked
outcome, while $m\ge s$ continues at index $m-s$. The source bounds the
number of live indices by three. [Graph specification in PR #6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072)

## Phase arithmetic

Keep $\theta=2^k\bmod169$, initialized to one. For an outcome of weight
$w$, the next digit is one exactly when $w\theta\bmod169\ge85$.
Subtracting twice the quotient at depth $k$ from the quotient at depth
$k+1$ gives the quotient on doubling that remainder.

Let $a,b,c$ be the digits for weights 144, 12 and 1. The digit for the
other weight 12 is also $b$. Compute $2\theta,3\theta,6\theta,12\theta,
24\theta,25\theta$ in that order, reducing modulo 169 after each addition.
The product $25\theta$ is nonzero modulo 169 because both factors are units.
Since $144=169-25$, the digit $a$ is one exactly when the residue of
$25\theta$ is below 85. The digits $b,c$ test whether the residues of
$12\theta$ and $\theta$ are at least 85. The residue of $2\theta$
is the new phase. The circuit stores no depth log or per-phase digit table.

A modular addition first forms the nine-bit sum $S$ of two reduced
residues. Its range is $0\le S\le336$. The top bit of
$(S-169)\bmod512$ is set for $S<169$ and clear for $S\ge169$.
A selector returns the low eight bits of $S$ or $S-169$ accordingly.
For the digit test, the top bit of the nine-bit sum $r+171$ is set
exactly when the residue $r$ is at least 85.

## Local inverse

The output packet contains the new phase, two bits for the output label or
new live index, and the stopping bit. The second 11-bit packet begins at zero.

If the new phase is $\theta'$, the old phase is
$(\theta'+169(\theta'\bmod2))/2$. This recovers the same probability digits.
If the stopping bit is clear, add $s=a+2b+c$ to the new live index to recover
$m$. If it is set, the label recovers $m$ as the number of set digits
strictly before that label. The four prefix counts in label order are
$0,a,a+1,a+2b$ on the corresponding terminating branches. The count for
label 10 uses $b=1$, since that label can only be returned when its digit
is set. The old live index is $\lfloor m/2\rfloor$, and the old stopping
bit is zero. The resident coin is preserved in either direction.

The circuit computes the forward packet into temporary wires, XORs it into
the zero packet, and reverses the temporary computation. It swaps the two
packets with three CNOT gates per bit. The inverse calculation then XORs
the original packet out of the backing and clears its own temporary wires.
These operations use self-inverse X, CNOT and Toffoli gates. Reading them
backwards restores the old packet with the same zero workspace. The two
temporary allocations share their wires because each computation clears
its wires before the next starts.

At the root, phase one and node zero with coin zero terminate at 00, and coin
one continues at node zero with phase two. The mathematical update agrees
with the graph rule at every depth. Induction gives the same output and
first stopping depth on every ordered coin path.

## Finite gate check

The verifier derives the output digits independently as
$\lfloor 2^{k+1}w/169\rfloor-2\lfloor 2^kw/169\rfloor$.
It enumerates a complete period, checks that the phase and live count return
to their initial values, and supplies both coins at each live index. These
624 input packets cover the circuit's claimed domain, including the final
transition of the period. The checker inspects gate arities, wire bounds and
the read-only coin. It compares every output wire, including backing and
scratch, and runs the reversed sequence on every reference output.

The Python generator allocates only while constructing the finite gate list.
It caps temporary wires at 2,048 for either oracle, limits additions to nine
bits, and emits a straight-line circuit. Gate simulation uses one bounded
bit lane per case and runs in normal and optimized interpreters with warnings
treated as errors. The clean-workspace count measures circuit wires.

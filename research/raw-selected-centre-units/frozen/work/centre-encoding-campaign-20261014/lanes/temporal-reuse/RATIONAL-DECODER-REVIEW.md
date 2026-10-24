# Independent review of exact rational scalar operations

The arithmetic and common-grid theorem pass independent review. The
literal J inverse uses one private accumulator and adds at most one
factor of 13 at every prefix. The paired Smith inverse adds at most one
factor of 3. Both can use the inherited two's-complement record format.
This result does not establish new native access or a complete supplier.

The reviewed proof is `interface-proof/rational-decoder/RATIONAL-DECODER.md`,
SHA-256 `556c5a9ce23201973ef9738d8bb49ab712d4af67e4132c57a2c39e16767d11eb`.
The producer receipt is
`84d6be9dc9fae46ce6b86e58a8968933c1442347134d9dc1ac2a06e987f6dd80`.
The source pins are
`48886903f9d95d403dec50143b329d1bbcd48f44528bbaaa561bb82fc96e09f5`.
The checker imports no producer code.

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/temporal-reuse/review_rational_decoder.py
PASS_INDEPENDENT_RATIONAL_DECODER_ARITHMETIC_AND_GRID
```

## Source and local word checks

The checker binds all 13 listed files to their Git blobs at
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. It also reads the pinned
selected archive from Git and checks all three listed member hashes.
It verifies the actual maximum child width 48, dimension 73, and selected
rank mass 1041408. It does not read a moving source branch as evidence.

The retained scalar emitter permits dyadic ADD coefficients and binary
SCALE coefficients. Its cost formula gives 7232 old real primitives for
each J word. The 16 real odd-division scans are separate work. The
stopped-product note already supplies the common odd-grid method. The
new result applies that method to the actual query matrix and literal
inverse word; it does not introduce the general grid method.

The checker reads the frozen literal J words and checks them on fixed
integer grids with denominators 4 and 52. Every arithmetic step must
remain integral on its declared grid. It also replays each word in reverse
on all 113 formal columns. Both methods give the stated endpoint,
including the discarded initial C0 value and zero final C0. Both inverse
orders hold on the 112 data coordinates.

For the inverse, the largest prefix row norm is 56. The binary denominator
height is two and the 13-height is one. Every complete query immediately
before division has 13-height zero relative to the module input. For J,
the largest prefix row norm is 143. The omitted-division control fails.

The proof of the prefix bound is valid. Distinct rows of R are orthogonal.
Thus a complete new query annihilates every earlier rank-one update.
A partial query can retain one old factor of 13, but division occurs only
after the complete query has removed it. This argument concerns the
linear coefficients relative to arbitrary module inputs. It does not
require those inputs to have zero odd height.

For Smith, the review builds the literal scalar protocol from the proof
and the actual selected minor. It uses two independent 104-coordinate
graph-input banks, eight selected X coordinates, eight selected Y
coordinates and C0: 225 formal inputs. Allowing independent graph banks
is stronger than requiring them to be routed reads of the same ordinary
input. The replay checks the selected sum, both inverse orders on the
224 live coordinates, unchanged graph inputs and final private zero.

The forward and inverse costs are 8624 and 8656 old real primitives.
The inverse also has 16 real divisions by 3. Its maximum odd height is
one and its binary height is three. The respective prefix row norms in
this expanded formal model are 66 and 65. Each row reads only unchanged
ordinary inputs and its own selected coordinate, so earlier rows cannot
add a second odd denominator. The graph has 52 signed-half coefficients
per row. The separate allowance of 1712 monomial applications is
2 times 832 graph reads, eight selected reads and 16 target updates.
The eight native children and their 16 wrappers remain separate.

## Exact records and the common grid

The revised scan works directly on signed two's-complement records. For
division by an odd prime p, its bit equation is

```text
2*c_next = c + p*a - b,   a = (b-c) mod 2.
```

The carry stays in the fixed set 0 through p-1. After w bits,
`p*Q_unsigned = N_unsigned + 2^w*c_final`. Subtract the two sign terms.
Exact signed division is therefore equivalent to
`c_final = p*sign(Q) - sign(N)`. This also proves that a nonmultiple is
rejected. It proves all widths without a numeric sample assumption.

The independent finite check covers all 64 multiplication and division
transitions for p=3 and p=13. It also checks every signed bit pattern at
widths one through twelve, 16380 cases. It rejects 13020 nonmultiple
division cases and checks the exact multiplication overflow condition.
The arithmetic head can reach the low end and return while it computes.
The stated `4*(w+1)` kernel bound is conservative. It is not a bound with
coefficient four for descriptor preparation or record counters. Those
costs remain in the separate retained linear-scan bound.

Let each finite parent prefix add at most L_p to its input p-height after
completed children are replaced by their exact dyadic maps. A dyadic
matrix, including its complete helper columns, preserves the maximum
odd height of its inputs. On a live call chain, each unfinished frame
adds at most its own L_p. Induction gives height at most `L_p*(D+1)`.
Completed sibling calls cannot add to this bound. This is the reason to
use depth rather than the total number of recursive calls.

The same scale S must apply to every physical numerical stream. It must
include arbitrary borrowed values, unchanged data, and coefficient work.
New work initialized to zero needs no separate numerical conversion.
Descriptor bits and opaque address-work strings are not coefficients.
An address routine may treat an encoding as opaque bits, but it must
restore its exact permutation before coefficient arithmetic resumes.

At each exact division, the output-prefix height bound shows that the
stored numerator remains an integer on the predetermined grid. The
binary guard must independently cover the binary denominator height and
value growth. The proof does not assume that an arbitrary integer on
the finest grid is divisible by p. It starts with dyadic root values
multiplied by S. The checker includes controls for an unscaled helper
and for completed children that return uncancelled odd denominators.

Root preparation and output unscaling use `K3+K13` constant scans in each
direction on N real records. Their arithmetic-head cost is at most
`8*N*(K3+K13)*(w_g+1)`. The retained counter and descriptor work adds a
separate linear-stream constant. The width increase is at most
`2*K3+4*K13`. No record conversion occurs at a recursive entry or return.

The selected recurrence has child width at most `48*floor(e/73)`.
The exact inequality `2*48^2 < 73^2` gives a decrease by a factor greater
than two over each two levels. Thus `D <= 2*ceil(log2(d+1))` is safe. Fixed local
height bounds give O(log d) extra bits and O(V log d) root conversion
work. This preserves the asymptotic width under the stated p,d regime.
It does not certify a new complete precision or node-work invoice.

## Scope and resolved findings

The first draft used a sign/magnitude scan although the retained interface
uses two's complement. The revised scan removes that format mismatch.
The proof now separates its arithmetic-head count from the unpriced
constant in the retained descriptor layer.

The first draft also said that an encoded endpoint could not be unscaled.
The revised text is precise: any dyadic encoded endpoint permits exact
arithmetic unscaling, but that operation does not prove the Fourier
endpoint or helper-restoration contract. A rational endpoint with an
uncancelled odd factor does not meet the stated depth-only premise.

The local common-frame condition is essential. A scalar coefficient is
not raised to the tensor multiplicity, but it also does not repair an
unequal native frame. The 448-map routed J allowance and the Smith
hole-frame copies require their separately proved access conditions.
This review does not emit or check a new native Smith word, new owner
schedule, changed controller, or complete decoded supplier. It does not
review the separate `GRID-ADMISSION.json` envelope. No kappa improvement
is claimed.

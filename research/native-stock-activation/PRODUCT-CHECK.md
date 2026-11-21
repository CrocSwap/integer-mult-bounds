# A complete small product through split address atoms

The test changes a data-bearing step of the retained Fourier multiplier.
Both input CRT conversions and the inverse CRT use a split-atom exchange.
In each conversion, the exchange makes the target axis contiguous. The
retained Beneš controls then change its records. The return exchange
restores the required axis order. Omitting both exchanges fails on dirty
labelled data. The two forward Fourier means, pointwise multiplication,
opposite mean, rounding, inverse CRT and carry all execute on those records.
The arithmetic uses the retained word-product function for scalar products.
Host multiplication and schoolbook convolution occur only in test checks.
[Fourier producer and integer endpoint](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/retained/fourier/product.py)
· [Matched CRT controls](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/retained/fourier/heterogeneous_crt.py)

## Data movement in the finite instance

Use two head atoms and two tail atoms. Each atom has two ternary components
and uses the additive group F₃ × F₃. Each complete field has 81 possible
values. Each low row in GL₂(F₃) has 6,561 body records. The integer
multiplier splits each signed fixed-point record across the 48 rows into
equal pieces. Spare bits and exterior padding start at zero. Their values
are checked on return. Dirty genuine dyadic holes travel through the full
permutation and retain their prescribed endpoint. The representation is
bijective on all accepted input words. The digit order never changes
inside a complete opaque suffix.

For each of the two reversed exchanges, execute the covered first line
on all 48 rows. Right multiplication by the coordinate interchange,
a second covered first line, and its inverse implement the complementary
line. Both projectors have the same current chart at their composition,
and their sum is the identity. Include all lower preparations, the
leading or late pivot adapter, the central weighted pair, and both
returns. Each weighted pair uses three componentwise lower updates, two
complete earlier exchanges, and one componentwise head negation. Apply
the predecessor's three outer corrections around the two reversed calls.
The result sends `(H,D)` to `(D,H)` on every row. The two ranks in this
small instance use separate primitive lines. Its carrier dimension is
2. The growing theorem uses the dimension `2^240000000000000`.
[Physical lower sweeps and unit weights](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/ternary_leaf.py)
· [Right-route spools and returns](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/streaming_routes.py)

The C interpreter receives only trit additions, trit exchanges and trit
negations. It reads and writes complete suffix records sequentially.
An exchange has nine bucket heads. A rotation saves the initial run and
emits it after the terminal run. A negation fixes zero and reverses the
two other blocks. The interpreter allocates the output buffer and one
scratch extent of at most a full packet each. The signed-record packer,
unpacker and Beneš controller are Python reference code. The numerical
fixture uses explicit finite arrays. Its peak Python memory is separate
from the logical tape measurements below.

The independent leaf check substitutes the explicit two-by-two inverse
at each low into the defining matrix formula. It compares all 314,928
destinations before the complement can cancel an error. The complete
ordinary swap is also checked on 314,928 arbitrary three-byte records.
It uses 112 leading leaves, 80 late leaves, four physical right routes
and 13,824 trit passes. The complete four-product run uses eight forward
CRTs, four inverse CRTs, 96 right routes and 331,776 trit passes.
Across their twelve CRTs, 51 genuine field entries change. Each transform
uses 52,416 retained individual Hadamard calls.

On `(3,5)` at radix 256 and 136 working bits, `741503 × 466013`
returns `345550037539` with uncarried coefficients
`[11811, 10996, 4152, 868, 77]` and ten zeros. The other products
include negative, zero and near-capacity operands, carry chains and
opposite signs. The fixture uses an explicit small geometry at the
predecessor's diagnostic precision. The family proof and its activation
threshold address the growing native schedule separately.
[Predecessor one-trit diagnostic](https://github.com/CrocSwap/integer-mult-bounds/blob/3f7c3c1f2a9a0963736562037e01fe41aec46b8c/research/bounded-general-multiplier/row_crt.py)

## Equal atom widths and equal input sizes

The comparison uses two trits per atom in both machines. The scalar chart
has 81 genuine high lifts per low. The split chart has one. Both runs use
the same ring-local matcher, a column addition by one half followed by a
column swap, and its full inverse. Each actual body record has a distinct
four-byte token. At the intermediate destination every token is changed
by a nonzero mask that depends on the true low. A separate modular formula
checks each moved record and each modified return. Of the 48 scalar
destination rows with zero high, 38 came from a nonzero source high.

| Per full forward route | Two-trit scalar | Two one-trit factors | Two one-trit factors, all original input |
| --- | ---: | ---: | ---: |
| Genuine matrix configurations | 3,888 | 48 | 48 |
| Independent labels inside each body packet | 1 | 1 | 81 |
| Independent four-byte payloads | 25,509,168 | 314,928 | 25,509,168 |
| Payload bytes | 102,036,672 | 1,259,712 | 102,036,672 |
| Peak initialized logical tape bytes | 618,597,324 | 7,637,004 | 618,597,324 |
| Tape bytes read | 2,910,170,916 | 20,391,588 | 1,651,718,628 |
| Tape bytes written, including explicit erase | 5,718,305,160 | 39,523,464 | 3,201,400,584 |
| Absolute seek distance in logical tape bytes | 8,424,402,732 | 57,395,628 | 4,649,045,868 |

The inverse has the same counters for this matcher. Peak includes the
retained input, produced output and all initialized spools of that call.
A profile hook counts reads, writes, truncations and head positions of the
unmodified predecessor router. These are logical tape sizes and transfers.
They do not measure process RSS, operating-system cache traffic or disk
blocks. Token generation, independent checking, and the intermediate
consumer are outside the per-route counters. The first two columns show
an 81-fold reduction in compulsory records and in measured peak for one
complete unreplicated packet. In the same-input comparison, all old high
labels survive in the opaque suffix. Peak then has the old value. The
matched runs return identical modified streams with SHA-256
`eec8c3f6683ccc78c8b41b661a476ffc16c3f627f28ec058b08344ee5436e287`.
The test gives no crossover time for an arbitrary input-length multiplier.

## Replay

Use Python 3.10 or later, a C11 compiler and the pinned predecessor package.
Set `PRED` to its `research/bounded-general-multiplier` directory and
`ROOT` to a checkout with the authenticated retained Fourier compiler inputs.
From the directory that contains these checks, run the following commands.

```sh
cc -std=c11 -Wall -Wextra -Werror -O3 -shared -fPIC packet_tapes.c -o packet_tapes.so
python3 -B check_split_product.py "$PRED" "$ROOT" ./packet_tapes.so
python3 -B measure_stock.py "$PRED" scalar
python3 -B measure_stock.py "$PRED" split
python3 -B measure_stock.py "$PRED" split-matched
```

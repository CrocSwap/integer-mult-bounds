# Return the original port in a five-source connector reset

**Exact local result; no new κ.** At unit operation prices the restored
fixed-port connector costs **67 operations** with one owned zero row
before charging for that row. The unchanged restored connector costs
**74**. With a fixed additional provision price ρ ≥ 0 the exact
five-source comparison is **min(74, 67 + ρ)**: provision must cost
strictly less than seven units for a saving. On the retained width-16
fixture, the complete declared fixed-port bill is **35,060** versus
**40,754** for the original restored connector, a saving of **5,694
tariff units**. The existing retargeted solution costs 34,944 where
moving the child ports is legal.

## Contract

Over F₂ let z be the original arbitrary dirty connector and w one owned
width-L row supplied zero and returned zero. All n sources xⱼ are
immutable; every nonempty mask m has a distinct arbitrary dirty target
yₘ. Return z unchanged and add Aₘ(∑ⱼ∈ₘ Bⱼ xⱼ) to yₘ. The complete
child calls Bⱼ: z += Bⱼ xⱼ and Aₘ: yₘ += Aₘ z always use physical z,
restore their private scratch and heads, and leave other public rows
untouched. The targets are never read or observed during the word. The
maps are arbitrary linear maps, including singular and noncommuting
maps; the word must work for all of them.

The only extra data operations are F: w += z, G: z += w, and at most
one Z: z := 0. Their positive complete prices are f, g and r. The
uniform prices for a source call and readout are b and a. Row provision
is separate. Without the auxiliary there is no legal reset that preserves
an arbitrary z, so the original #2063 comparator applies. The model
does not bundle operations, use outputs as storage or retarget a child.

## Exact price of saving and restoring the port

Let N = 2ⁿ − 1. Save the old z in w, clear z, and traverse the reflected
Gray path from 0 through all N nonzero masks. Toggle the entering source
and read the corresponding output once at each vertex. To leave z at
zero, either close the path with its single final source toggle or
reset z. Then use G and F to return z to its old value and w to zero.

| Word | Save and clear | End of walk | B | A | F | G | Z |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Closed | F, G | One source toggle | N+1 | N | 2 | 2 | 0 |
| Entry reset | F, Z | One source toggle | N+1 | N | 2 | 1 | 1 |
| Exit reset | F, G | Z | N | N | 2 | 2 | 1 |

All three include the final G, F. Each readout uses z at its intended
mask and never has to cancel a contribution from old z. No map is
commuted, inverted or moved to w.

**Lower bound, including interleaved moves and repeated readouts.**
Specialize to scalar identity maps with independent source bits and an
independent original connector bit. Let α = (α_z, α_w) be the
coefficients of that original bit in the two rows. The pair cannot
become 00: the source bits are independent and no output can be read
back. The clean combination s = α_w z + α_z w starts and ends at 0.
Both F and G preserve s while changing coordinates. A B call can
toggle one source bit in s or do nothing. A legal Z can only send s to
0: it requires α_w = 1 and then puts α_z = 0 and z = 0.

If k ≥ 1 targets each receive exactly one readout, those readouts need
α = 01 and k distinct nonzero masks in s. At least k B calls are needed
to create them, and the other targets need at least two readouts each,
so A ≥ 2N − k. If there are exactly k B calls, each must produce one
of those distinct nonzero masks for the first time; the single reset
must occur after the last one to return s to zero. With no B left,
all k once-read targets must already have been read before that reset.

The coefficient path must go from 10 through 01 and back to 10. Entering
01 takes F and then either G or Z; returning takes G and F. Thus a word
without a reset needs at least k+1 B and two F, two G. A word with a
reset and at least k+1 B needs at least two F and one G. A word with a
reset and exactly k B still needs two F and two G because its reset is
used for closure, after the path has already entered 01. This yields

```text
price >= b k + a (2N - k) + 2f + g + min(b+g, b+r, g+r).
```

For a ≥ b this bound is minimized at k=N, and the three Gray words
attain its minimum. This proves the exact price among all legal words
using at least one once-read target, without assuming a single clean
excursion. A word without any once-read target needs at least 2N A and
n B because every source must influence its own one-source mask. For
five sources at unit prices this lower bound is also 67, so the
wrapped optimum is global in that tariff. Paying ρ for any word using
w then gives the exact optional-provision comparison above. At general
prices the no-singleton bound need not settle the global optimum.

## Pinned width-16 comparison

The retained #1954 fixture uses five source permutations and 31
permuted 13-tap readout maps. All 36 maps fix the all-ones vector.
Restricting every row to that one-dimensional subspace gives exactly
the identity test above, even for a word chosen specifically for these
maps. The lower bound does not transfer to every fixed map instance.
For example, two complementary projections used as the two source
maps and as the first two readouts (with identity for the combined
mask) let three outputs share one clean value. A ten-operation
fixed-port word there beats the generic eleven-operation once-read
bound at two sources. The replay checks all 4,096 inputs to this example.

Keep #5372's charge of 26,704 for the shared tables and original rows,
403 for mask descriptors, and 58 for allocation, 16 storage cells and
16 initial zero writes. The complete source and readout prices are 29
and 221. Charge each extra full-row XOR or reset 16 operations or
writes plus the same 13-unit action descriptor. The entry-reset word
costs 7,895 in actions (32×29 + 31×221 + 4×29). No word without a
once-read target can beat the action bill, since 62×221 + 5×29 is
13,847. Adding all retained fixed charges gives 35,060. This exact
total comparison stipulates those charges as fixed for the auxiliary
route. It does not optimize other layout or compilation tariffs.

The original restored comparator is 40,754 by repricing all 16 of
#2063's exact profiles and retaining the original common charges.
Retargeting the children instead would avoid the four port actions
and cost 34,944, as in #5372. The wrapper costs 116 more and is useful
only when those ports must stay fixed.

## Verification

Run with CPython 3.12 from a clean checkout or the official Git-free
export (which includes the three declared inputs):

```sh
python3.12 -I -B research/fixed-port-connector-reset/verify.py
```

[RESULT.json](RESULT.json) records 24 symbolic Gray words, 12 exact
shortest-word checks for one or two sources, the fixed-map counterexample,
and each of the three literal words on all 608 width-16 input basis
columns. The latter use the pinned fixture maps and a separate
dense-matrix target oracle. Seven controls reject lost dirty values,
incorrect closure or return, unpaid zero initialization, or a second
reset. The three comparison inputs are checked against the hashes in
[SOURCES.json](SOURCES.json).

## Open next questions

A multiplication caller still has to supply the fixed ports, an owned
zero row outside the child scratch, complete prices for its moves,
reset or closing call, and the full layout, tape, stock and recursive
bill. The width-16 tariff is a checked local instance. No physical
supplier, selected caller or changed κ follows. A useful next step is
to pin one actual caller and account for that row for the entire
interval before attempting a larger construction.

## Credit

Nick Petalas's [#7324](https://github.com/CrocSwap/integer-mult-bounds/pull/7324)
at `fd573cfe4e9714706b01f0534584e6f5032dc858` supplies the disposable
reset and open Gray schedule. Ross Richardson's
[#934](https://github.com/CrocSwap/integer-mult-bounds/pull/934) lineage
supplies the generic dirty connector, Adam Gall's
[#2063](https://github.com/CrocSwap/integer-mult-bounds/pull/2063) its exact
restored tariff, Cinna Davis's
[#1954](https://github.com/CrocSwap/integer-mult-bounds/pull/1954) the
fixture, and Ali Romman's
[#5372](https://github.com/CrocSwap/integer-mult-bounds/pull/5372) the
paid clean-row Gray cycle and retained invoice.
[#2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182) is a
separate fixed-port precedent with a second arbitrary dirty row and
paired readouts. OpenAI Codex and ChatGPT Pro materially assisted the
proof, adversarial review and exact replay. Apache-2.0.

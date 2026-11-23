# Bind a normalized native return to the direct word's exact raw Hadamard

**Scoped interface theorem and exact evidence. No new kappa.**

The direct-circulant tensor interpreter uses raw sums and differences. Its
retained native interface returns a normalized Hadamard layer after a final
toward-zero truncation. A sufficiently wide private grid alone does not
make that returned value exact on the caller's grid.

For an h-bit call on P-grid data of modulus at most 2^E, use

```
R=E+1
Q=P+R+h
```

Shift each input integer numerator left by h and send the complete field
as Q-grid values. These values have modulus at most one half. The exact
normalized result is on the Q-grid, so final truncation is transparent.
Its returned integer numerators are already the caller's raw-H numerators
on the original P-grid. No post-return integer shift is needed.

Q is the least universal requested output precision for this fixed scaling
and unchanged exact-then-truncate service: one admissible basis numerator
has a nonzero output of size 2^-Q, which is erased by a Q-1 return.
This is an interface statement, not a private-storage lower bound.

The parent precision theorem supplies the computed radius. Agreement with
the unlimited-integer reference word is proved inductively, avoiding a
circular assumption that the replacement native execution already fits.
The actual selected stride sets, signs, absolute C/S/b phase, spectators
and complete padded field are included.

On the original production geometry, Q and the conditionally specialized
native temporary width are below 8192p. Thus the native logarithmic
parameter rises by at most 13; the source's axis-window, untouched-suffix
and product-stock scale inequalities still hold eventually. Actual native
realization, geometry/stock admission, compiler and physical-cost contracts
remain explicit. The historical subpower-dimension proposition is not
applied directly to the newer near-linear geometry.

## Proof and evidence

[PROOF.md](PROOF.md) gives the universal argument and complete conversion
bill. [SOURCE-BYTES.json](SOURCE-BYTES.json) binds eight unchanged source
files. [adapter.py](adapter.py) implements only the format wrapper, with a
supplied native provider. [check.py](check.py) compares the literal source
routine to a separate exact Gaussian-rational C/S/b oracle.

The author replay checks 1,829 complete adapter cases, 28,124 returned real
and imaginary components, 132,460 macro intermediate components, 180 sharp
coarser-grid witnesses, 107 actual packing-rule checks and 84 selector
bindings. Twelve adverse controls cover source corruption, invalid geometry,
understated radius, wrong C phase, missing normalization, wrong stride and
a second post-return shift, and missing terminal divisor/parity. The credited
terminal normalization lemma supplies an explicit same-grid b/S boundary,
with exact division of complete numerators. Macro intermediate checks concern the literal
C/S/b oracle; they do not execute recursive native interiors.

Run from this directory, with standard-library Python:

```
python3 -B check.py
python3 -O -B check.py
```

The two frozen receipts [EVIDENCE.json](EVIDENCE.json) and
[EVIDENCE-OPTIMIZED.json](EVIDENCE-OPTIMIZED.json) are identical. Reproduction
writes only stdout unless an explicit disposable `--output` path is given.

## Scope and predecessor credit

Base: `e54523517d0f03e58352e647c403a5af3e525a57`. This follows open
[#8093](https://github.com/CrocSwap/integer-mult-bounds/pull/8093), parent
`8559a122f55614163c037b3c20a21f449a0531f6`, for the original
[#7849](https://github.com/CrocSwap/integer-mult-bounds/pull/7849) chronology.
Its source scaling idea, native normalized layer, common-grid theorem and
O(p) existence were already known. This contribution identifies the exact
requested return grid, proves its final truncation is transparent, binds
its actual integer return, disproves a one-bit-coarser universal contract
and checks raised-precision compatibility with the source geometry.

No production-sized transform, recursive native execution, complete
physical storage bound, canonical assumption removal or unconditional
multiplication theorem is claimed. All five selected assumptions and
kappa remain unchanged. The changed #7981 word is not covered automatically.

Credit Ali Romman, Douglas Colkitt and the original native-layer authors;
Ross Richardson and the fixed-root/common-grid contributors; Jose Manuel,
Vlado Vojdanovski, Chafik Boukhalfa, Nick Petalas and Brian/JoyboyBrian;
and the preceding #8093 author/reviewer work. Prepared for Jerry Chen /
@CubeJerry with substantial OpenAI assistance. Apache-2.0. Model-assisted
review is not independent human or proof-kernel acceptance.

## Open next questions

1. Bind a concrete native provider's actual requested return parameter and
   private format to Q and the conditional private bounds. Start with its
   output truncation and complete selected-bit descriptor. This remains
   blocked by that provider's realization and geometry admission, which a
   numerical interface alone cannot prove.
2. Join the conversion window to the provider's physical arena lifetime.
   Start with one complete owned call/return and count both historical
   intervals. This remains blocked by the concrete native owned-memory
   contract. Repeating small basis tests would not close it.

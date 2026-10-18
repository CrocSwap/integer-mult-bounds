# Sharp dense B/C root-code floor in every dimension

For the full `B_n` and `C_n` root-line configurations and their fixed dense
binary orthogonality pairing, every admissible factorization whose columns
lie in the two root codes costs at least **n²**, for every `n>=1` and any
finite number of terms. The coordinate Gram factorization attains n², equal
to the number of lines. Thus arbitrary root-code basis changes and extra
terms cannot turn either full family into a gain in this precise model.

The coefficient field may be any field of characteristic other than two,
including the complex numbers with ordinary transpose. **The support-block
cost is always rank over F2.** These are separate fields and separate rank
arguments. The pairing is defined using the original integer root geometry,
not any additional orthogonality that reduction modulo an odd prime creates.

## What closes the gap

[PR2272](https://github.com/CrocSwap/integer-mult-bounds/pull/2272) reports
fixed-coordinate B/C examples and bounded changed-basis searches.
[PR2518](https://github.com/CrocSwap/integer-mult-bounds/pull/2518) extends the
fixed-coordinate examples to B7/B8/C7/C8. Neither finite table establishes
the arbitrary-coefficient, arbitrary-term-count claim here.

The new witness is an invertible **cross-star minor**. Every nonzero root-code
vector contains an axis and a supported root on every incident coordinate
edge. Opposite signs on an edge have identical dense pairing rows and
columns. Any two such stars have an explicit n-by-n invertible binary
pairing, even when their anchor axes differ. Consequently every nonzero
rank-one term costs at least n. The n mutually orthogonal axis lines force
at least n nonzero terms in an admissible realization. See [PROOF.md](PROOF.md).

[PR2228](https://github.com/CrocSwap/integer-mult-bounds/pull/2228) supplies
the earlier root-code floor method and exceptional/simply-laced cases;
[PR2277](https://github.com/CrocSwap/integer-mult-bounds/pull/2277) distinguishes
root-code factors from unrestricted overcomplete realizations. This result
extends the scoped floor to the full mixed-length B/C families in all sizes.
[PR2536](https://github.com/CrocSwap/integer-mult-bounds/pull/2536) instead
studies coordinate D-family punctures and admissible pairing ties. It does
not supply this arbitrary-root-code B/C cross-star bound.

## Replay

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -O -B research/bc-dense-root-code-floor/verify.py
python3 -I -O -B research/bc-dense-root-code-floor/check_stars.py
python3 -I -O -B research/bc-dense-root-code-floor/integrity.py
python3 scripts/research_package.py --package research/bc-dense-root-code-floor
```

The primary replay authenticates a byte-exact PR2272 source snapshot by
SHA-256 and Git blob ID before extracting its named pure functions. For
dimensions 1 through 16 it checks both original root generators, the dense
pairing after an explicit source-order permutation, and the predecessor's
coordinate cost. It checks all ordered coordinate stars in those dimensions,
all canonical rational support cells through dimension 6 modulo left signed
permutation symmetry, and every pair of nonzero coefficient vectors in the
declared small odd finite fields. The latter still uses binary pairing rank.
Exact sheared and split Gram factorizations check noncoordinate and
overcomplete examples. These finite checks support the written all-size
proof; they are not its quantifier justification.

`check_stars.py` independently builds the pairing from axis/edge incidence,
without importing `model.py` or using Gaussian elimination. It verifies an
explicit inverse against every binary right-hand side for every ordered
anchor pair through dimension 10. `integrity.py` replays a Git-free export,
rejects a modified predecessor before execution, and rejects a boolean-for-
integer receipt alteration that ordinary Python object equality would accept.

The six primary controls show failure of the local floor or its inference
after changing density, characteristic, completeness of the signed root set,
the root-code restriction, nonzero-term counting, or admissibility. The sparse
and punctured controls do not claim a complete cheaper admissible decoder;
they identify precisely why this minor proof cannot be carried across those
boundaries.

## Limits and attribution

This is a scoped written theorem and exact finite evidence, not a new κ,
physical supplier, native lowering, all-pairings optimum, or proof-kernel
artifact. No changed local profile is being inserted into the selected
complex ceiling. The original task card is marked **changed**: the result
rules out root-code improvements in a specified dense alphabet, without
claiming the card's constructive five-percent improvement gate.

The construction and prior fixed-coordinate tables are credited to Aaron Wang
and DreamingOfClouds through the pinned predecessor packages; their original
source header is preserved. New proof, checkers and documentation: ywz65,
with substantial OpenAI Codex assistance for research, implementation and
drafting. See `TASK.json` and `SNAPSHOTS.json` for exact source and scope pins.

## Open next questions

1. Can an admissible sparse pairing for full B/C roots break the n² decoder
   floor, rather than only erase the particular star minor? Start with the
   n=2 density control and require the complete realization and all term costs.
2. Which B/C punctures retain an invertible cross-star in every pair of
   nonzero root-code supports? Classify star-survival conditions first; the
   present proof does not cover missing sign partners.
3. Can factors outside the root codes yield a gain with a fully specified
   admissible realization and complete physical bill? The singleton control
   only removes this local lower-bound argument and supplies no such decoder.

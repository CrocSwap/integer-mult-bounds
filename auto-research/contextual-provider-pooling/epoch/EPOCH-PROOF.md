# Exact carrier basis change across one read-only epoch

This constructor replaces the A epoch using helpers r=571 and s=585 by an
invertible change of carrier coordinates. Both helpers enter in frame [480].
Neither is written during the original epoch. Set r' = r+s at frame [480],
replace each read t += q*r by t += q*r' - q*s, combine only commuting shears at
the identical frame, and finally restore r by r' -= s at frame [480].

For each replaced read, q*(r+s)-q*s=q*r on arbitrary register values. Since
neither carrier is written inside the epoch, this identity holds at every use.
Shears on distinct destinations/sources commute precisely when neither writes
the other's read source; equal-source/equal-destination shears then combine by
coefficient addition. The constructor checks these dependencies. The final
inverse restores both carrier values. Consequently the entire epoch has the
same linear map on every input coordinate, including all arbitrary helper dirt.

The changed A has 14 fewer gates, and its literal reverse background cleanup
has 14 fewer gates. B, cut, precondition, target levels, centre interfaces,
entrances and helper widths are unchanged. Both boundary basis operations are
included; neither is treated as free. The paid rank histogram is exactly
unchanged, so this change is a scalar-circuit simplification, not a separate
recurrence-moment gain. Any numerical improvement in the combined submission
must be attributed to its actual separately priced controller/resource change.

The frozen source uses 728 registers (112 source ports, 112 target ports, 504
helpers). The standalone C++ audit compares every one of the 529,984 endpoint
coefficients after A+cut+B using arbitrary-precision dyadic rational arithmetic.
It also checks two controls: omitting the terminal inverse changes 9 coefficients
(4 target coefficients), and omitting one transformed reader changes 18
coefficients (8 target coefficients). These controls are not vacuous. Fresh
phase, adapter and full physical supplier admission belong to the enclosing
submission's verifier.

## Replay

The constructor requires the checked tn25 weighted word and the inherited
gk_word.py/gk_common.py directory. It accepts only the frozen canonical source
hash and produces the frozen canonical output hash; compression bytes are
recorded but are not a cross-version identity condition.

    python -B build_epoch14.py --input WEIGHTED-WORD.json.gz --gk-dir GK_DIR --out NEW_DIRECTORY
    c++ -O3 -std=c++20 -I BOOST_INCLUDE audit_epoch.cpp -o audit_epoch
    audit_epoch NEW_DIRECTORY/AUDIT-INPUT.txt NEW_DIRECTORY/SCALAR-AUDIT.json

Compile without NDEBUG. EPOCH-SELECTION.json resides beside the constructor;
--selection can explicitly point to it. No discovery optimizer is used on replay.

## Research scope

Before selecting this exact rewrite, the lane screened 128 paid two-delivery
windows, 1,052 coherent maximal read-only epochs (966 frame-legal), and 22,394
bounded matched-producer/reader conjugations (14,520 legal). The last family
also allowed omission of an inverse only when its destination had an exactly
zero target suffix response. None gave a direct paid moment gain. Twelve
alternating lower-join/upper-meet sweeps on the neutral epoch presentations also
gave no paid gain. The broad generalized retiming variants were interrupted
before completion and are not included in the completed census. A separate
same-entrance full-lifetime warm-pair compatibility census was empty.

The construction is an explicit finite holographic gauge identity: adjacent
inverse basis maps cancel. It was motivated by the finite PEPS contraction
representation in the inspected OpenAI TensorNetwork/VectorColumn source and
the generalized Holant perspective, but no external source proves this
register/frame/dirty-cleanup implementation automatically. The elementary proof
above and exact supplier checks provide that transfer. Prior two-circuit
representative screens are not claimed as new work or numerical ingredients.


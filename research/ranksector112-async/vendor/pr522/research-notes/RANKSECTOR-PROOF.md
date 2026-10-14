# Coordinate-total reconstruction on an independent row sector

## The implemented improvement

The old partial-own factory has twelve retired registers in each of fourteen code blocks. Their clean source rows span only eight dimensions. It raises all twelve registers from their rank-three frames to the common rank-four block frame, reduces the twelve-by-eight row matrix, and forms four coordinate totals. The extra four raised rows are unnecessary for those outputs.

The new factory chooses eight independent retired rows, changes basis on those eight registers so that the first four contain the required coordinate totals, and leaves the other four registers untouched until the ordinary cleanup. All 560 helpers remain present. No dirty register is erased, identified with another register, or treated as clean storage.

This removes four intermediate climbs in each block. Each affected register previously paid a rank-one climb followed by a rank-five climb; it now pays one rank-six climb. The exact local delta is

    -56 rank-one calls -56 rank-five calls +56 rank-six calls.

The selected 99 kernel pivots, gauge selection and ordered whole-residual inventory are unchanged. The inventory is eighteen width-seven, 161 width-eight and 381 width-nine helpers. The new local profile is:

    rank:   1     2    3   4    5    6  7   8
    count: 2474  182  516  88  242  124  1  17.

For every 0 < b < 1, strict subadditivity of x^(1-b) gives 6^(1-b) < 1 + 5^(1-b). Thus this change strictly reduces the recursive moment while preserving rank mass. Across the existing seventy-two invocations, the complete global child profile has the corresponding factor-seventy-two delta. The same whole-owner allocation can be retained because the ordered widths agree exactly. The final finite arithmetic replay also charges the actual scalar program and is the authority for the published supplier bound and kappa.

## Sufficient algebraic construction

Write the eight independent clean rows as an invertible matrix T in the eight source coordinates. Let L be the four-by-eight matrix of required coordinate sums. The four rows of L are independent. Extend them to an eight-row basis U, and form

    M = U T^(-1).

The emitted elementary operations apply M to precisely the eight selected physical registers at their admitted common block frame. Their clean output rows are M T = U, so the first four are exactly L. M is invertible on arbitrary physical register contents, and all unselected registers are literally unchanged by this stage. The inverse cleanup is reconstructed from the new actual word.

Dirty-state correctness is not inferred from the clean row equation alone. The complete helper response matrix is recomputed, the actual target compensations and kernel prefix are reconstructed, and all scalar basis columns are checked in both orientations. For this frozen word, all 800 forward columns, all 800 inverse-transpose columns, and 99 independent omitted-kernel-correction controls pass. Every scalar denominator is a power of two and every scaling operation is a signed power of two, matching the existing finite scalar compiler.

The constructor uses deterministic finite row reduction to select T and extend L. This is part of reconstruction, not an optimizer or an assumed gadget. The exact common-frame containment tests, final scalar identity, dirty-data compensation, dyadic compatibility and physical global replay remain explicit checks in the package.

## OpenAI proof source and precise transfer

The direct source is `lean/OAI/Analysis/Cotype/RankFactors.lean`, from the corpus's cotype-cotype project (catalogue item 326). In namespace `OAI.Cotype`, `exists_rank_pairing_matrix` constructs rectangular factors for an arbitrary square matrix P over a field:

    I.transpose * P * J = identity_on_rank(P).

Its proof selects the independent block in `Matrix.exists_rank_normal_form`. The following theorem, `rank_pairing_contract`, proves that these factors preserve the desired bilinear contraction exactly. We transferred the constructive principle: restrict to the independent sector needed by the output pairing instead of normalizing every redundant row. Here the independent sector has dimension eight, the requested total map has four rows, and the preserved ambient registers carry the unused dirty coordinates.

This is a different construction from the preceding package's Newton-inspired pair-cover selection. The pair covers are fixed throughout this change. It is also not a claim that the Banach-space theorem automatically certifies our circuit. The file and its proof were inspected; the new rational circuit has separate finite checks. No fresh Lean compilation was performed in this round.

The initially inspected alternative source, `Computability/FourierCircuit/DisplacementKernel.lean`, gives the exact `reconstruct` identity for an interior outer-product recurrence and its explicit boundary terms. This motivated a packet-to-total telescoping gate. All fifty-six coordinate totals were found in the admissible retired/packet row spans, but the winning construction is the independent rank sector described above, not a claim that a displacement factorization itself improved the final bound.

## Bounded search and reproducibility

The clean checkpoint, rowspace tests and frames are retained in `TOTALS-CHECKPOINT.json` and `TOTALS-GATE.json`. After the positive eight-row construction, one bounded native C++ pass enumerated the 4096 subsets of the twelve retired rows in each block over the prime 1000003. Within that modular gate, each block required at least eight independent rows to span the four coordinate totals, with 63 choices of eight rows. This is a bounded search record, not a global optimality theorem or an exclusion of redesigned factories.

`construct_ranksector.py` contains the actual factory and its exact decoder assertions. `build_ranksector.py` reconstructs it, transfers only matching inherited scalar-event frames, rebuilds the existing 99-pivot selection, checks the dyadic contract and binds the complete normalized word. It invokes no discovery search. Text-source pins normalize only line endings to avoid platform-dependent CRLF failures. Whole-word normalization removes only the two established stale floating display annotations and an asserted redundant register-count field; mathematical operations, coefficients, frames and the rest of the word remain hash-bound.

Normalized selected-word SHA-256:

    d966e1481e0c09e4b7a0607429411046c6b3663ee83e6b8833958a745b82e337

The local scalar receipt is `ranksector/SCALAR-AUDIT.json`; the source reconstruction receipt is `rebuilt-ranksector/CONSTRUCTION.json`. Physical owner maps, local complex phases, normalized spectators and the final two-engine arithmetic receipt are checked independently by the package replay.

Inherited public mechanisms remain credited: PR507 supplies the partial-own factory; PR484 the gauge/kernel compiler; PR496 the pooled whole-owner interface; PR495/501/502 the frame retiming; and PR473 inspired the coordinated gauge reductions. The preceding package supplies the two-block pair cover and its 99-pivot selection, as well as the asynchronous controller and literal allocation. The improvement here is specifically the rank-sector coordinate-total reconstruction.

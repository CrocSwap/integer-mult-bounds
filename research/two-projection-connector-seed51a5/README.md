# Fixed-port, two-projection, two-row five-source connector

**Conditional recursive-interface construction; no selected-kappa change.** A second arbitrary dirty helper row lets a five-source universal connector use exactly two source calls per source and two output readouts per nonzero mask. Its 72 recursive map calls attain the elementary support floor, while the fixed single-row alphabet needs 74 calls. The construction pays 10 full-row XORs and one extra length-L helper row.

The source word is

```text
B0 B1 B0 B1 B2 B3 B4 B2 B4 B3
```

Each source occurrence updates helper direction `[1,0]`, except source 3, which updates direction `[1,1]`. Output readouts use covector `[1,0]` for the all-source projection and `[1,1]` for the regular-source projection that ignores source 3. The all-source path has 26 prefix differences; the regular path has 16. Their union is all 32 masks of F2^5. The second projection supplies the six masks `10001`, `10010`, `10011`, `10101`, `10110`, and `10111` missing from the first.

`EXPECTED.json` gives a boundary pair for every nonzero mask. `verify.py` independently enumerates the 945 canonical paired source words and all 32 direction assignments; 175 of the 30,240 candidates cover all masks using only the two stated readout projections.

## Exact charged invoice

The recursive map work is 10 B calls and 62 A readouts, 72 calls total. Under the child prices pinned in the current connector certificate, each B_j occurs twice at prices `[1, 4, 10, 16, 28]`, and each A_i is unit priced. This gives **180 rank-one children**. The current single-row `five_extra_output` certificate uses 10 source calls and 64 output readouts for 74 calls and **182 children**. The difference is exactly two rank-one children.

The helper work is charged separately. Independently conjugating every nonidentity call would use 28 full-row XORs. A global-frame dynamic program over the six invertible two-row frames reuses the shears and reduces this to **10 full-row XORs** for the certified boundary table, or `10*L` bitwise XORs on length-L rows, plus one extra length-L dirty helper. `EXPECTED.json` records a shortest frame schedule for this fixed boundary table; it does not prove optimality over different readout boundary choices. There are no clean ancillas or data-dependent choices. Relative to the 182-child single-row schedule, the arithmetic part wins only when the actual value of these linear operations and helper storage fits below the two-child margin. In an exponent model they are lower-order linear work; no finite-size runtime advantage is claimed.

The extended alphabet changes the fixed one-row restriction by adding a second dirty helper and paid transitions between two-row frames. Every inherited B_j and A_i call remains on physical helper row z0; the basis changes let those calls realize different logical injection/readout directions. There is no combined source query. The result is not tied to a selected-supplier occurrence and does not change the accepted kappa.

## Reproduce

From the repository root, using Python 3.10 or later and only the standard library:

```sh
python3 -I -O -B research/two-projection-connector-seed51a5/verify.py
```

Expected output:

```text
PASS_TWO_PROJECTION_CONNECTOR words=945 assignments=30240 full_covers=175 source_calls=10 readouts=62 calls=72 frame_xors=10 children=180 baseline_children=182 saved=2
```

The package manifest also provides the repository's registered Python 3.12 replay and source-pin check. `PROOF.md` gives the arbitrary-dirty-state argument and exact cost boundary.

## Provenance and limits

The fixed-alphabet predecessor is Ross Richardson's PR #943. Nearby open work includes PR #1531's charged DUO query, PR #1770's weighted one-row optimum, PR #1811's parity-hyperplane batch, and PR #1812's 72-call, eight-one-way-transfer construction with B/A port choice. This result fixes all B/A calls at physical row z0 and instead uses both paid row-shear directions in a persistent global frame. The contracts and resource vectors differ; no priority or cost-dominance claim is made for the general two-root batch.

The accepted selected result remains the maintainer-reviewed conditional finite construction with kappa `836330098538459/500000000000000000`, complex-binding. This package is a local interface construction only. It does not show that the selected supplier can host the extra row or these frame changes, does not include them in the selected assembly, and claims no improved kappa.

## Open next questions

- Can different valid boundary pairs lower the 10-XOR frame schedule? The exact dynamic program minimizes frame changes only for the current 31 certified pairs; any improved schedule must retain the full dirty-state map and fit below the two-child margin.
- Is there a source-pinned occurrence in the selected multiplier supplier where the extra dirty row and two readout projections are already available or can be hosted for less than the saved recursive-child cost? Without such an occurrence, the current result remains a conditional interface improvement.

# Attribution and provenance

Prepared by DaysSky, assisted with Claude. Apache-2.0 (see `LICENSE`) applies to the new code and to the inherited
Apache-2.0 code; third-party notices are preserved where files are vendored. `SOURCE-pr370.json` and
`SOURCE-pr363.json` record, by git blob id, every file taken unchanged from those two pull requests.

## Vendored

- **The E8 bit word and its bit-side checks** (`data/`, `code/bit/` except the files listed as new below,
  `code/pricing/`, `NOTICE-PR352.md`, `LICENSE`): unchanged from PR #370 (Dylan Crow, utcorvusvolat-dotcom) at
  `b7fe9cdf2da009c947ff6b334c562bc190b30373`:
  - the word `bitE8-r865`, its producer, the record exporter, the independent checker and its controls, the centre-count
    CP-SAT proof;
  - the generalized checkers `legality_h.cpp`, `columns_h.cpp`, `gram_frames.py`, `geometry_g.py`, `tile_g.py`,
    `certify_bit_g.py`, `finite_g.py` and the receipt assembler `receipts_e8.py`;
  - the unmodified PR #346/#352 sources in `code/bit/regression/` and the regression data in `data/regression-p10/`.

  PR #370's notice gives the lineage of these checkers: PR #266's official cohort checkers as generalized by LJH-217's
  PR #346; the source527/p10 packages' `finite_check.py`, `geometry527.py` and `global_lowering.py` (eumemic's source527
  package; PR #200, Chafik Boukhalfa; PR234, hcg890 / Henry Grant, on Jacob Sussman's five-stage architecture; Evan
  McKinney's completed banks; the p = 10 ports by DreamingOfClouds and Chafik Boukhalfa); PR #315's engines
  (`moment.py`, `base_two_moment.py`, `outer.py`, `prime_witnesses.py`). `json.hpp`: Niels Lohmann, MIT license in its
  header.
- **The complex supplier** (`code/complex/`, `code/certify_b3.py`): unchanged from PR #363 (DaysSky) at
  `9df55dad6ddd05c3458793dfd82d1c2fe0ddbbb4`: Jacob Sussman's E8 unit, Lean data, generators and replay
  (jacobalansussman/wht-power-saving-lean at `9c94857`, Apache-2.0, Copyright 2026 Jacob Sussman; his `LICENSE` and
  `NOTICE` are beside the files), PR #352's portable complex checks with the layout as a parameter, and `bridged.py`,
  which generalizes Sussman's bridged five-stage word to B_K. See `NOTICE-PR352.md` for the complex-check lineage.

## New in this package

- `code/bit/checkers/columns_k.cpp`: `columns_h.cpp` with the bank schedule, twin bridges and terminal exchange
  generated for B_K (`-DKPAIRS`, default 2 = the five-stage tables).
- `code/bit/checkers/geometry_k.py`: `geometry_g.py`'s routes, chained stage boundaries, idle pairs and entrance
  completion on 2K + 1 blocks, with the idle chronology of `bridged.py` and explicit dyadic intermediate frames for
  the half-shrink splits.
- `code/bit/checkers/tile_k.py`, `certify_bit_k.py`, `finite_k.py` and `code/bit/receipts_k.py`: the bank width, the
  one-level histogram, the stage counts of the finite bill and the receipt assembly for B_K.
- `verify.sh`, `code/provenance.py`, `README.md`, this notice, `MANIFEST.sha256`, the two provenance files, the
  workflow.

Each new checker reproduces the PR #370 checker it generalizes at K = 2; `verify.sh` compares the receipts.

Credits do not imply endorsement or review by the credited authors.

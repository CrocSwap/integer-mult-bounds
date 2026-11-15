# Attribution and provenance

Prepared by Dylan Crow, with Anthropic Claude assistance. Apache-2.0 (see `LICENSE`) applies to the new code and to the
inherited Apache-2.0 code. Third-party notices are preserved where files are vendored.

## New in this package

- The E8 bit word `bitE8-r865` and its producer (`code/bit/producer/`).
- The record exporter.
- The independent checker and the controls.
- The centre-count CP-SAT proof.
- The generalized bit-side checkers, each with a documented default that reproduces the original:
  - `NCOPY` in `legality_h.cpp` and `columns_h.cpp`;
  - the `--gram` parameter in `gram_frames.py`;
  - the label-family parameters in `geometry_g.py`;
  - h and replicas in `tile_g.py`;
  - h and T in `certify_bit_g.py`;
  - NCOPY and the route template in `finite_g.py`.
- The receipt assembler.
- The secondary `seven_stage.py`.

## Vendored

- **`code/complex/`, `code/pricing/`**: unchanged from PR #352 (DaysSky) at `04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2`. This
  includes:
  - Jacob Sussman's E8 unit, Lean data, generators and replay, from jacobalansussman/wht-power-saving-lean at `9c94857`
    (Apache-2.0, Copyright 2026 Jacob Sussman; his `LICENSE`/`NOTICE` are beside the files);
  - PR #315's engines (`moment.py`, `base_two_moment.py`, `outer.py`, `prime_witnesses.py`).
  See `NOTICE-PR352.md`.
- **`code/bit/regression/`**: unmodified from PR #352 / PR #346 (LJH-217):
  - `legality_h_pr346.cpp` and `columns_h_pr346.cpp` (PR #266's official cohort checkers as generalized in h by #346);
  - `stage_cohort.py`, `prime_new.py`, `tile_check.py`, `cost.py`, `certify_bit.py`.
  The generalized checkers in `code/bit/checkers/` derive from these, and from the source527/p10 packages'
  `finite_check.py`, `geometry527.py` and `global_lowering.py`, whose lineage is:
  - eumemic's source527 package;
  - PR #200 (Chafik Boukhalfa);
  - PR234 (hcg890 / Henry Grant), on Jacob Sussman's five-stage architecture;
  - Evan McKinney's completed banks;
  - the p = 10 ports by DreamingOfClouds and Chafik Boukhalfa.
- **`code/secondary/bridged.py`**: unchanged from PR #363 (DaysSky) at `9df55dad6ddd05c3458793dfd82d1c2fe0ddbbb4`.
  See `NOTICE-PR363.md`.
- **`data/regression-p10/BASE-*`**: PR #325's p10b word as exported in PR #352 (DreamingOfClouds; #352 `data/bit`).
- **`data/regression-p10/receipts-loans/`**: verification receipts of agent G's p = 10 passive-loans package, used only as
  regression input.
- **`json.hpp`**: Niels Lohmann, MIT license in its header.

The E8 label family on the bit side follows Jacob Sussman's introduction of the E8 family for the complex supplier.

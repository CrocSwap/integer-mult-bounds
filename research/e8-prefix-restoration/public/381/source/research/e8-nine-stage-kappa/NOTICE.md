# Attribution and provenance

Prepared by DaysSky, assisted with Claude. Apache-2.0 (see `LICENSE`) applies to the new code and to the inherited
Apache-2.0 code; third-party notices are preserved where files are vendored. The `SOURCE-pr*.json` files record, by git
blob id, every file taken unchanged from PR #370, #363, #373, #375 and #377.

## Vendored

- **`complex377/`**: PR #377 (Zhihao Chen, jacklightChen) at `d0a620fcc99ba012468d61d01f5bb14007076d50`,
  `research/nine-stage-complex-e8/`, byte for byte, with its own `MANIFEST.json`, verifier, construction argument,
  `LICENSE` and vendored notices. It is built on Jacob Sussman's E8 unit (jacobalansussman/wht-power-saving-lean at
  `9c94857`, Apache-2.0) through PR #352, and its vendored notices retain the five-stage, completed-bank, compiler and
  analytic-framework credits. PR #377 states that it was prepared with OpenAI Codex assistance.
- **The E8 bit word and the bit-side checks** (`data/`, `code/bit/`, `code/pricing/`, `NOTICE-PR352.md`, `LICENSE`):
  PR #370 (Dylan Crow, utcorvusvolat-dotcom) at `b7fe9cd`. PR #370's notice gives their lineage: PR #266's official
  cohort checkers as generalized by PR #346; the source527/p10 `finite_check.py`, `geometry527.py` and
  `global_lowering.py` (eumemic; PR #200, Chafik Boukhalfa; PR234, hcg890 / Henry Grant, on Jacob Sussman's five-stage
  architecture; Evan McKinney's completed banks; DreamingOfClouds and Chafik Boukhalfa's p = 10 ports); and PR #315's
  engines. `json.hpp`: Niels Lohmann, MIT license in its header.
- **`code/complex/code/bridged.py`**: PR #363 (DaysSky) at `9df55da`.
- **The K-parameterized bit checkers** (`columns_k.cpp`, `geometry_k.py`, `tile_k.py`, `certify_bit_k.py`, `finite_k.py`,
  `receipts_k.py`): PR #373 / PR #375 (DaysSky).

## New in this package

- `geometry_k.py`: the option `unsplit`, which skips the splits and reports the least halving degree.
- `certify_bit_k.py`: the option `unsplit` and the halving degree in the receipt.
- `finite_k.py`: the least halving degree in place of the half-shrink assertion, and the internal row reserve
  t·(d + 1). At t = 1 it is the PR #370 bill.
- `verify.sh`, `code/provenance.py`, `README.md`, this notice, `MANIFEST.sha256`, the provenance files and the
  workflow.

Credits do not imply endorsement or review by the credited authors.

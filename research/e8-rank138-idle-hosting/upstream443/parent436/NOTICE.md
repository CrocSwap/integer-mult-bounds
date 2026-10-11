# Notice

Apache-2.0 (`LICENSE`). Prepared by eumemic with substantial Anthropic Claude assistance.

## New in this package

- `code/reuse/`: the elimination-reuse stage (`reuse.py`), the frame retiming (`retime.py`), their integer cost tables (`ecost.py`), the regeneration driver (`regen.py`) and the elimination-reuse negative controls (`controls.py`).
- `data/params/params-r740.json`: our parameters for PR #370's producer. `discovery/` holds the search that nominated them.
- `data/bit/bitE8-r740.json.gz` (the word) and `data/bit/reuse-ledger.json` (its inserted elimination gates).
- `code/nine/global_word_g.py`, `audit_g.py`, `certify_g.py`: generalisations of PR #386's `global_word.py`, `audit.py` and `certify.py` to any bitE8/1 word whose helpers start at frame 0 and end at the full frame. `regress386.py` checks them against PR #386's own receipts. `cited.py` binds the cited complex savings to the PRs' receipts. `compose433.py` ports PR #433's bit pricing, finite invoice and tail.
- `code/b4/kappa_b4.py`, `code/provenance.py`, `verify.sh`, `EXPECTED.json`, `data/complex-b-*.json`, `.github/workflows/e8-bit-elimination-reuse.yml`.

## Vendored, byte-identical (git blob ids in `SOURCE-pr*.json`, checked by `code/provenance.py`)

- **PR #370 (Dylan Crow / utcorvusvolat-dotcom, with Anthropic Claude assistance), commit b7fe9cd:**
  - the producer `code/bit/producer/`;
  - the independent checker and its controls `code/bit/independent/`;
  - the record exporter and the record-level controls;
  - PR #266's official cohort checkers as generalised there (`legality_h.cpp`, `columns_h.cpp`, NCOPY);
  - `gram_frames.py`, `stage_cohort.py`;
  - PR #315's engines (`code/pricing/`, DreamingOfClouds);
  - nlohmann/json (`json.hpp`, MIT licence in its header);
  - the E8 bit word `data/bit/bitE8-r865.json.gz`;
  - `LICENSE`.
- **PR #381 (DaysSky, assisted with Claude), commit 00765b2:** the B_K checkers `columns_k.cpp`, `geometry_k.py`, `tile_k.py`, `certify_bit_k.py`, `finite_k.py`, `cost.py`, `receipts_k.py`, and PR #363's `bridged.py` (DaysSky).
- **PR #386 (Zhihao Chen / jacklightChen, with OpenAI Codex assistance), commit dd11cf8:**
  - `geometry.py` (compressed nine-stage bit geometry, unchanged);
  - the portable `bits/stdc++.h`;
  - the validation receipts `GLOBAL.json`, `AUDIT.json` and `COMBINED.json`, used only as regression references.
- **PR #417 (Chafik Boukhalfa / chafreaky, with Anthropic Claude assistance), commit 3f681fb:**
  - `bootstrap.py` (their reimplementation of rohanarun's PR #392 refined pricing tail), `e8core.py` and its copies of PR #315's engines;
  - `apply376.py`;
  - the final kernel word, used as a B_4 control.
- **PR #376 (applecrusher, with OpenAI Codex assistance), commit 92328da:** `frame-selection.json`, `reuse-selection.json` and `LICENSE-pr376`, as vendored in PR #417.
- **PR #426 (ai-nanachi, with OpenAI Codex assistance), commit 88d5525:** the R767 bit word, used only as a priced comparison and B_3 control, and `LICENSE-pr426`.
- **PR #425 (Zhihao Chen / jacklightChen, with OpenAI Codex assistance), commit e11ccea:** the validation receipt `FINAL.json`, which states the cited b and κ.
- **PR #431 (Rohan Arun / rohanarun, with OpenAI Codex assistance; draft), commit db4f465:** the validation receipt `VALIDATION-LOCAL.json`, which states the cited b and κ.
- **PR #433 (icekylinx, with OpenAI Codex assistance), commit 6d92445:** `CERTIFICATE.json`, which states the cited complex b, the R758 bit c and κ. `code/nine/compose433.py` is our port of #433's `code/bit_price.py` and `code/combined.py` arithmetic. No #433 code is vendored or run.

## Cited, not rebuilt

Complex coarse savings in `data/complex-b-nine.json` and `data/complex-b-b4.json`, each with its PR, commit and receipt (git blob):

- compressed nine-stage layout:
  - PR #433 (icekylinx; `data/complex-b-433.json`, bound to its certificate by `compose433.py`);
  - PR #386 (#377's component), PR #425 (jacklightChen) and PR #431 (rohanarun, draft), bound to their receipts by `code/nine/cited.py`.
- B_4: PR #424, #407 (chafreaky), #410 (eumemic) and #409 (rohanarun).

No complex construction is rebuilt here.

The E8 label family follows Jacob Sussman's introduction of E8 for the complex supplier.

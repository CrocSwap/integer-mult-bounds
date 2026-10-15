# Vendored from PR2269 (byte copies)

Source: CrocSwap/integer-mult-bounds PR #2269 head b479fc5567bc09ab9185bffe89b62594f36d74e5,
`research/gmx-t74-borrow43/new/borrow/` (Jeremy Kothe / jeremykothe2 and the lineage named in that
package's README; Apache-2.0).

- `emit_word.py`, `build_word.py`: BORROW-WORD builder (canonical word + PR2226-style witness ->
  explicit chronological word with warps, cold restoration and inverse cleanup).
- `audit_local.py`: independent exact scalar/frame/free-algebra auditor (header credits icekylinx
  with OpenAI GPT-6 Astra assistance for the base auditor; BORROW-WORD extension by PR2269).
- `borrow_controls.py`: negative controls for the auditor.

The mechanism they implement is PR2226 anticipatory dirty borrowing (Cinna Davis, @1337isnot1337,
with OpenAI Codex assistance). Unmodified; git blob ids are pinned in ../../SOURCES-PR.json.

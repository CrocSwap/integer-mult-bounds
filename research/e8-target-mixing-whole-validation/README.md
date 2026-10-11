# Verification evidence

Both fresh runs rebuilt the complete parent chain with `E8_REPLAY_PHASES=1`:

- `linux`: Python 3.12.3, full mode, all inherited and changed controls, exit 0.
- `macos`: Python 3.14.8, quick mode, all changed controls and complex phase
  regeneration, exit 0. Quick mode skips the inherited PR443 exhaustive controls.

Every field of the two `RESULT.json` files agrees exactly. Both independently
regenerated the physical instruction digest
`ca6f38adf4dcc53d756ff0e27febeed2080ba09d6d181b094b889aa5393b2ee3`.
The retained receipts bind the manifest used for those runs.

After the full runs, documentation spacing and one trailing space in
`assemble.py` were cleaned up. `FINAL-COSMETIC.diff` contains the complete
change, `TESTED-MANIFEST.json` records the tested bytes, and
`COSMETIC-CHANGES.json` binds the final manifest. The Python AST is identical;
all other executable and frozen input hashes are unchanged. The final
assembly was rerun successfully on both platforms with identical results.
CI will run the complete verifier against the published commit separately.

These receipts establish the listed finite checks, not the all-size
conditional contracts described in the package README.

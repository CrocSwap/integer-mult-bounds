# Verification

The clean wrapper authenticates the original #7334 Git blob, compressed SHA256 and decompressed payload. It verifies the compressed source census against its decompressed SHA256. It reconstructs the 760-row R200 control in the reverse engine, runs the 967-case exact support screen with a 25-second runner cap, and runs the six-case reverse span gate with a 45-second cap. The screen exhausts 967 cases and the exact gate exhausts all six selected cases. The 237 other support survivors remain open.

A separate forward readback using per-row support masks checks each of the 967 target rows, bank sizes and coordinate outcomes. It also directly verifies each exact dual on every corresponding bank row and target. No modular support or zero test is used. The wrapper rejects a changed ADD coefficient in the native word and verifies that dropping one coefficient from the top dual breaks its separating property. Four large generated receipts are represented by deterministic stdout SHA256 values and can be regenerated with `--out DIRECTORY`.

The result settles normalized source support and exact bank span for the tested cases. No physical direct MOVE, new supplier or complete recurrence was implemented or replayed.

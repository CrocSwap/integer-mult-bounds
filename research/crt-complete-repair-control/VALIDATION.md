# Validation

Environment: macOS, CPython3.12.2, standard library only. Scientific replays
were serialized through the batch's sole heavy slot. No Lean, Docker,
selected-frontier or historical full suite was run.

The first complete actual source fixture passed with 4,096 opaque payloads,
2,944 independently checked current-state keys, 167,388,873 instructions and
52,900,258 cell actions in35.78 seconds. This was a calibration before the
explicit22 owned-marker lifecycle writes. The final program adds those writes,
makes static register allocation deterministic and rejects unsupported AST
forms. No earlier receipt is relabelled as final evidence.

The bounded final controls pass: try-finally, while-else, for-else, nonempty
Tape construction, extra method argument, bucket-clear omission, skipped radix
pass, skipped carry bit, control-only cycle, borrowed-role alias, skipped
nested key and changed borrowed-ROM bytes. An isolated corrupted retained
producer source is rejected by SHA256 authentication before assembly/replay.
The actual nested-key probe uses a positive ROM, preserves the opaque prefix
and erases key scratch.

Independent read-only agent review covered static AST semantics/admission,
finite-role/finite-symbol boundaries, direct relocated key return, CFG bound,
source proof and ownership. Two findings were fixed: unsupported source
finally/loop-else/argument forms now reject, and the actual full verifier now
snapshots and checks the exact six borrowed unary tapes and ROM, including
framing and tails. Final reviewed SHA256:

* compiler.py:1186cdefed22890a987c1f289290c6db4c19446a29461c1db46257f318b05156
* machine.py:afa110ed2fdba62e810fd794e5fd62a07ec4caf18e8919066275523713353cc7
* PROOF.md:151211f34d80c8edd03512dd18af27b9b5b1dfe6f9fda9f904bfd59c4ab1a807
* verify.py:167e3d45c2edfa74eccffaf8929ebdd95b3c5b0623339b1ab1329bff0e156589

This is agent review, not independent human or formal-kernel acceptance.

Final full normal authoring replay uses
`python3.12 -B research/crt-complete-repair-control/verify.py --write-result`.
This executes every registered check; only the final receipt write replaces
receipt equality. Final normal/optimized/export outcomes are recorded below. The static program hash is
ed1893ec1eb99f075fb67b5319cf99e961d3f9bb0daba82c13a84cbe4dfb28bf;
8,242 instructions and longest control-only path606. The conservative total
instruction upper bound is6,294,271,835,487; it is not an observed runtime
or a complete E(p,ell) bound.

Final normal replay PASS:167,388,895 instructions,52,900,280 cell actions,
2,944 exact marked-key calls; all twelve controls, borrowed bytes, data,
heads, private storage and control reset pass. The22-action delta from the
first calibration is exactly the newly executed marker lifecycle. Metadata
and exact source pins pass. Committed-byte/source-history check and official export/check passed at
dcebc47566b92dabce1c57fb7beb6cff3eb6adf7 (24 package/input files).

The official archive SHA256 was
11bfc17135bf0bfc3258d896211d96deb1be438582740606f9c503f39e6876a8.
Extracted without .git metadata, with PATH set to an empty directory,
`/opt/local/bin/python3.12 -O -B research/crt-complete-repair-control/verify.py`
passed the complete frozen receipt:167,388,895 instructions,52,900,280 cells,
2,944 key calls and all twelve controls. Every exported file remained byte
identical after replay. Subsequent changes only record this validation; all
scientific executables, proof, inputs and receipt bytes remain unchanged.

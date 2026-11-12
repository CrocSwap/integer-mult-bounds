# Verification and source identities

The exact #7334 compressed native word SHA-256 is
`4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a`.
Its canonical JSON SHA-256 is
`9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac`.
Both are checked at replay. The exact #7113 caller is
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.
The pinned comparison identifies its exact caller bytes and retained five premises.

[PROVENANCE.json](PROVENANCE.json) records exact public source commits, paths,
Git blob IDs and SHA-256. [LOCAL-PINS.json](LOCAL-PINS.json) pins all
scientific input, engine and receipt bytes by their relative paths. The
#7334 admission and complete signed price readback are independent campaign
receipts from the prior comparator replay. They are included as inputs.
The public #7334 package supplies the complete original admission command.

Both independent reverse runs used CPython 3.12.14 with isolated mode and
assertions. The unary-turn runner took 0.09 s and its moved-root empty-environment
replay 0.08 s. The ADD-retime runner and its moved-root replay both took 0.08 s.
Each clean replay matched the exact receipt byte for byte. The standalone replay
regenerates every receipt and mutates a temporary copy of the exact compressed
word, requiring exit 1 and empty stdout on the corrupted input. Toy controls
exercise opposite-turn cancellation, incompatible outer charts, dirty binary
read and COPY barriers, owner reuse, valid same-chart retiming, the peer
read/write distinction and lifetime boundaries. The local package execution
uses CPython 3.12 and needs no repository writes.

The full changed-word native, caller, signed-phase, precision, tape and outer
replays remain inapplicable because the structural gates left no candidate.
Hosted verification is tracked separately from the local runs.

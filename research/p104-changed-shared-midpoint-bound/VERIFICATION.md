# Verification

CPython 3.12 with assertions and the standard library. The clean
local replay returned exit 0 and regenerated all nine exact receipts.
A separate relocated copy without Git metadata or inherited
environment variables returned exit 0 and matched every receipt
byte-for-byte. The direct and relocated full runs took 1.45 and 1.40
seconds on the verification host. A modified stock and modified
price each returned exit 1 in their authenticated engine.

Both topology walks exhausted all 76,466 events and ten frozen
anchors. There was no eligible two-role reprice. The one independent
closed component exhausted its exact offset scope and matched the
forward component in routes, bill and complete binary span sets.
Signed physical construction and full changed-caller verification
were skipped after the topology and geometry exclusions.

The paths and complete receipt digests are in
[LOCAL-PINS.json](LOCAL-PINS.json) and [receipts/SHA256.json](receipts/SHA256.json).

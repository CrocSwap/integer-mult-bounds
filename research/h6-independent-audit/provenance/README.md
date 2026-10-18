# Pinned H6 source closure

Run from any working directory with Python 3.11+ and NumPy:

```sh
python3 -B /absolute/checkout/research/h6-independent-audit/provenance/check.py
```

`PINS.json` binds the complete repository-local H6 import closure and cited numerical/context inputs to immutable Git blobs: predecessor `b496aed769dd724cd1ff6b921cade626562be27b` and CrocSwap base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Every inherited Niemeier/Leech file is also byte-compared against the predecessor fork. Standard-library modules and NumPy are environment dependencies, not frozen repository sources.

The runtime chain is `price_h6.py -> banked.py -> portable.py + costs.py -> leech-lattice/code/screen.py`; geometry uses `e8_cubed.py` without further repository-local imports. The original top-level `SOURCES.json` omitted the imported `portable.py` and exact rational log/exp engine `screen.py`; this receipt adds both. Attribution remains PR606/Dominik Scholz for inherited geometry and invoice, DreamingOfClouds for the published H6 package, and the independent audit authors for their new checkers.

The checker copies the frozen minimal input set into a temporary unrelated location, runs the price script under isolated Python from an external working directory, and requires identical saved stdout. It checks the copied hashes before and after execution, then deliberately mutates `screen.py` and requires rejection. It independently regenerates the 30,960 x 16 integer port intermediate and checks its NumPy-file digest `349e84668d1528783aa22bc650837533bcc6134052d9dbfba87fb05aa54911fd`, agreeing with the exhaustive Walsh audit and the predecessor README's abbreviated hash.

All four predecessor outputs are pinned. Only price stdout is replayed here; saved structure/Walsh text is historical evidence adjudicated by the separate exhaustive audit. In particular, structure2's `120*238` off-diagonal block count mixes 120 sign-quotient row classes with neighbor counts from 240 signed roots. It is not a valid count of 120 x 120 quotient blocks.

Selected-frontier context is `836330098538459/500000000000000000` (PR1094 family) at the pinned base. PR1424's title is a pinned pending comparison; its parent PR1319 admission remains unresolved in the retained maintainer review. This source audit does not admit PR1424 or freshly verify either supplier. Relocation of the new invoice/helper/Walsh checkers, complete selected-supplier cold replay, all-stage optimization and a construction theorem are outside this receipt.

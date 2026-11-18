# Half-sum CLEAR on fixed tapes

At width 1076, the exact PR #7721 circuit executes with 25 data tapes, one
read-only program tape and two temporary control bits. The emitted schedule
uses 589841 unit data instructions and 11206982 interpreter steps. All work
cells, markers, heads and control bits return to their specified exit state.
The program is preserved. No new kappa is claimed.

Read [PROOF.md](PROOF.md) for the exact entrance contract, all-width bound,
stock bill and open obligations. [RESULT.json](RESULT.json) contains finite
receipts. [PROGRAM-1076.bits.gz](PROGRAM-1076.bits.gz) contains the complete
marked binary program. [SOURCE-PINS.json](SOURCE-PINS.json) binds the unchanged
source files; [CREDITS.md](CREDITS.md) gives attribution.

Run with CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/half-sum-clear-tape
```

The source verifier prints PASS_HALF_SUM_CLEAR. Each registered command then
prints:

```text
PASS_HALF_SUM_CLEAR_FIXED_TAPE {'1': 1024, '2': 65536, '1076': 32} 11206982
```

This service receives its width-dependent program and reserved tape regions
at entrance. A uniform physical program generator and complete caller
admission remain open. The result does not claim transition-level reversible
control or discharge an inherited framework assumption.

## Open next questions

Can a uniform physical generator supply the marked program and return its
own work to blank? Specify its input, fixed-tape transitions and full bill
before composition. Can the enclosing caller supply and retire the reserved
regions under its global stock and reset bounds? These services are required
before this execution result can support complete supplier admission.

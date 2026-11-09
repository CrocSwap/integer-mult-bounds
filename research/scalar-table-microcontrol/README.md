# Explicit scalar-table microcontrol

**Result:** the pinned no-context `execute_table` has an explicit finite
transition-program lowering on the same fixed tapes and alphabet, with
exact serialized TM clock **C=A+U**. Here A counts the original raw tape
reads/writes/unit moves, including final origins, and U counts fetched
source rows. Positive finite precompilation F is separate: total F+A+U.
**No tariff conversion, full caller, recursive controller or new kappa.**

The compiler replaces each fixed row by a dispatch no-op and finite
microstates. Decoder values, ports and successors are fixed control;
the target performs no runtime source-row lookup or host arithmetic.
For N rows and P>=1 distinct ports it emits at most 48N+3P+4 states, including
all error terminals and success-origin loops. Its seven-symbol read
guards can be expanded to a conventional full simultaneous transition
function in finite, explicitly charged precompilation.

The proof preserves the initial blank probe and repeated first-bit read,
partial-code rejection heads, invalid111 rejection after complete rewind,
left-origin restoration before rejection, blank-frontier materialization,
and successful origins. Reject performs no success cleanup. Arbitrary
looping tables are covered by prefix equivalence, not declared total.

Source machine: CubeJerry commit
`ab239cb6ee884e7a900dd9101c34448077fad0b0`, blob
`acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592`.
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The earlier lifecycle proof already states qualitative finite expansion;
the new contribution is the explicit generator and numerical clock and
state bounds with exact source failures. All six dependencies are pinned.

## Reproduction

```bash
python3 -I -B research/scalar-table-microcontrol/verify.py
python3 -I -O -B research/scalar-table-microcontrol/verify.py
```

Expected `PASS_SCALAR_TABLE_MICROCONTROL`. The standard-library checker
compares 107 exact traces/endpoints/clocks with the unchanged executor:
17 primitive cases and 90 small retained rounded-SCALE cases, including
11 range rejections. Eleven static grammar controls reject; omitted
initial-probe and omitted-left-restoration mutants are detected. A
100-step looping prefix is deliberately not called a completed execution.
The simulator's host storage is verification apparatus, not the target TM.

## Open next questions

Lower readonly-context and Controller/wrapper interfaces separately, then
bind a complete actual caller. Establish a common volume and numerical
scalar/pass-tariff bridge; C=A+U by itself does not provide one. Retain
all setup, source access, retirement, history, recursive ancestor and
precision obligations. The global assumptions and selected result remain
unchanged.

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI assistance**.
Credit CubeJerry's lifecycle, exact and rounded scalar packages and the
canonical stream-model authors. Complementary model-assisted reviews
are preserved separately; they are not human or proof-kernel acceptance.

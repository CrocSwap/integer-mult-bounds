# Unit-weight column reversal at one odd prime

**Partial. No new exponent.**

The depth-zero unit ROOT returns weight 1 at every coordinate. The published
GL2(F3) macro machine does not read that record. It compiles the weight pair
`(2, 1)`, passes an empty program tape, and uses 192 fresh rows. At one gap,
that weighted pair is not the position reversal.

## What was executed

The production coefficient callback reads the unit ROOT at `q=3` and body 64.
All 64 coordinates are the ring unit, and the parsed root is `(64, 1, 0)`.

The same pair `(1, 1)` was then installed in the published GL2(F3) controller
in place of `(2, 1)`. One gap, `n=2`, and modulus 3 give 81 columns in a row
and 192 rows, 15552 columns in all. The machine's own column checks pass for
the unit pair. Independently, the unit-weight address map is the block swap
that reverses each atom block, on all 81 addresses of one row, and it is an
involution. The published pair `(2, 1)` disagrees with that reversal on 72 of
those 81 addresses.

The fixture still takes the weight pair from its source text. It does not parse
the ROOT tape while it runs. The selected-grammar machine check remains the
different root `(256, 2, 1)`.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to this
column implication. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the unit-ROOT call site, the caller archive,
the stock-proof note, the selected record, and the task catalogue. No selected
frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/selected-unit-weight-reversal/verify.py
python3.12 -B research/selected-unit-weight-reversal/test_verify.py
python3.12 -B scripts/research_package.py --package research/selected-unit-weight-reversal
```

The machine run is the slow command. On this machine it completed in about
276 seconds, inside the 600-second command budget. The structural test does
not start the machine.

## Open next questions

The GL2 controller still does not read the ROOT tape. A useful next step is to
load this exact `(body, 1, 0)` record as the program port of one
selected-grammar root at `q=3` and compare the returned row with `C_n`. The
published selected root is `(256, 2, 1)`, and that checker writes the child
body itself.

Separately, the complex `m=73` parent still has no proved per-level divisor
`C(w)=q^(A w+B)`. This column check does not answer that question.

## Credit

David Arias supplied the caller and the column-map oracle. Jose Manuel supplied
the fixed-role machine and the GL2(F3) fixture that compiles weights `(2, 1)`.
Nick Petalas supplied the wrapper whose callee must be the unweighted reversal.
The unit-root weight execution in #2980 is the predecessor of the pair used
here.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.

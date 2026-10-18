# Selected-grammar unit tape stops before a row reversal

**Negative result. No new exponent.**

One selected-grammar root at `q=3` does not read the depth-zero unit ROOT
and return the position reversal. The root that completes is fixture
`(256, 2, 0)`, which the same check then asserts as `(256, 2, 1)`. Empty
events are the depth word 0. Substituting unit 1, with that size and depth
left unchanged, is rejected at the child coefficient. No returned row is
compared with `C_n`.

## What was executed

The published selected-grammar check completes. Its coefficients are
`(0, 2)`, the extended root assertion `(256, 2, 1)` passes, and the checker
itself appends the child body. That appended body flips and reverses the 23
source bits. It is not the bit reversal of those bits, and the check never
computes a column reversal from the source.

The same run with the fixture unit forced from 2 to 1 writes the root triple
`(256, 1, 0)`. The adapter coefficient stays 0. The child coefficient is 1,
and the check raises `selected identity-projector adapter and generated child
coefficients`. That happens before the extended-root assertion and before the
checker writes the child body.

This is the selected root's size 256, not the body-64 unit ROOT measured
earlier. The unit weight and the zero depth word are the same values that
ROOT writes. The GL2 weight-pair machine is not run again.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to this
tape question. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the unit-ROOT call site, the caller archive,
the stock-proof note, the selected record, and the task catalogue. No selected
frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/selected-unit-root-tape-boundary/verify.py
python3.12 -B research/selected-unit-root-tape-boundary/test_verify.py
python3.12 -B scripts/research_package.py --package research/selected-unit-root-tape-boundary
```

Both selected runs together take a few seconds. The structural test does not
start the grammar check.

## Open next questions

The selected-grammar root rejects child coefficient 1. A useful next step is
to find whether any selected entry point accepts the depth-zero unit record
and returns a row that can be compared with `C_n`.

Separately, the complex `m=73` parent still has no proved per-level divisor
`C(w)=q^(A w+B)`. This tape check does not answer that question.

## Credit

David Arias supplied the caller and the unit-ROOT encoding. Jose Manuel
supplied the fixed-role selected-grammar check that writes the child body.
Nick Petalas supplied the wrapper whose callee must be the unweighted reversal.
The unit-root execution in #2980 and the unit-weight column check in #3011
are the predecessors of the tape substituted here.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.

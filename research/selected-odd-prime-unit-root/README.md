# Odd-prime depth-zero unit root

**Partial. No new exponent and no padded-row reversal.**

The merged wrapper consumes a caller-supplied modulus only through a completed
unweighted callee `F_I(H,D)=(C_n D, C_n H)`. PR2899 emits that callee as a ROOT
record `(body, 1, 0)`: unit weight, depth zero, and no STEP record. Its
odd-prime checker evaluates one coordinate of that record. Its pointwise column
restoration runs only in the `q=2` toy, and its `q=3,5` binary cases force the
elementary branch.

## What was executed

At `q=3`, atom modulus `3`, and a body of 64 atoms, this package builds that
same record with `unit_program` and evaluates the production coefficient
callback at every body coordinate. All 64 coefficients are the ring unit. The
parsed root is `(64, 1, 0)`. Parsing succeeds only when `RECORD_END` follows
the triple, so the record contains no STEP. Coordinate 64 is rejected.
Numerical banks erase on return. Peak scratch is 6.

The depth-zero arm of `weight` returns `root_unit` and then continues. It has
no row argument, and it does not read the reverse flag. The reverse flag occurs
once later in the same function, on the arm that does not continue. This
execution therefore binds the unweighted incoming weight. It does not move a
data tape and does not restore a padded row.

The selected odd-prime machine check inside the same caller archive expects a
different root, `(256, 2, 1)`, and writes its child body from the checker. That
execution is not this unit record.

## Scope and evidence

Original card: `selected-stock-envelope`, refined to the callee that the fitted
lcm stock still needs. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the call site, the three published checkers,
the caller archive, the stock-proof note, the selected record, and the task
catalogue. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/selected-odd-prime-unit-root/verify.py
python3.12 -B research/selected-odd-prime-unit-root/test_verify.py
python3.12 -B scripts/research_package.py --package research/selected-odd-prime-unit-root
```

`verify.py` activates the unchanged PR2809/PR2808 archives, so the pinned
selected record and stock-proof note must match. The structural test does not
evaluate coefficients.

## Open next questions

The weight half of the odd-prime callee is bound. The position reversal is not.
A useful next step is to run the macro machine on this exact `(body, 1, 0)`
record at `q=3` and one borrowed row count, and compare every returned column
with `C_n`. The published odd-prime machine check does not do that: it uses
root `(256, 2, 1)` and supplies the child body itself. The `q=2` toy remains
the only pointwise restoration.

Separately, the complex `m=73` parent still has no proved per-level divisor
`C(w)=q^(A w+B)`. This unit-root execution does not answer that question.

## Credit

David Arias supplied PR2753's caller and its unweighted endpoint statement.
Jose Manuel supplied the fixed-role caller and the ordinary interchange that
emits the depth-zero unit ROOT. Nick Petalas supplied the wrapper that requires
`F_I`, and the earlier stock coefficient used by the merged fit. The `q=2`
pointwise engine and the selected extended-root check are theirs; this package
does not rerun those fixtures or claim their endpoints.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.

# Transported queries for noncommuting coded child substitution

This scoped algebraic construction and written proof were produced by Nick Petalas.
In the four-field query extension, arbitrary ordered stage factors
A and B need no commutation assumptions if the first child's query is
transported to `c=BqB^-1`. The exact necessary and sufficient condition is
`cB=Bq`. Keeping c=q instead leaves the explicit defect
`A(qB-Bq)(y-q^-1 v)` in two output fields.

[PROOF.md](PROOF.md) gives the universal ring/module statement, all four
independent input fields, the complete chronological word and its residual.
It provides one typed child substitution and its next scalar bridge toward
Dillon Amburgey's [PR4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933)
question. It builds on Ali Romman's
[PR6348](https://github.com/CrocSwap/integer-mult-bounds/pull/6348) module.
The original commuting module, native words and controller results remain
predecessor work.

The abstract bill retains both child suppliers, one thin query and two
applications of the ordered complement AB. The literal scalar bridges
need seven additions/subtractions, four swaps and two negations. No clean
scratch field is used. Realizing the transported query and the coded
complement at an affordable native tariff remains open. This is not a new
kappa, physical supplier or complete multiplication theorem.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/transported-coded-query
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/transported-coded-query/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/transported-coded-query --check-source-history
```

Other machines may substitute their CPython 3.12 path. Both registered
commands, ordinary and optimized Python, print
`PASS_TRANSPORTED_CODED_QUERY`. The verifier writes no files and imports
no predecessor executable. Its generated JSON receipt binds all six
package-file hashes. Predecessor text is provenance, not a live input.

The free-group-algebra engine checks all 16 endpoint entries, all 16
residual entries, three nonzero commutators and six rejecting mutants.
The separate literal-vector engine checks 2,520 operator triples and all
20,160 arbitrary-input basis columns over F2/F3. It tests the exact
untransported commutator criterion on every one of those fixtures and
rejects singular operators. The written proof supplies the universal
claim; these finite domains are corroboration.

## Scope, sources and overlap

Question source is PR4933's typed recursive-product question, distinct from
its rounding/recovery questions. PR4940 changes the entire path's stage
assignment; PR4948 instantiates a dyadic coded path; PR5562 compiles coded
thin service. None of those paths or reported numbers is replayed here.
The fixed nineteen-leaf topology question on PR6348 is separate work.
This changes the operator contract of one merge, with no tree optimization.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The selected binding baseline passed and identifies the
selected record's own current value; historical prose is not used as a
frontier source. Live claims, 100 open PRs, this account's 200 most recent
PRs, main README searches and merged term searches were checked. The
overlap helper additionally reported 331 open PRs and 6,205 Discussion
records with complete remote pagination. This does not cover unpublished
work or prove novelty.

No actual negative-bank output of PR4933 is admitted by this result. Its
native realization, transported-query access, restoration and complete
physical invoice remain unresolved. The five framework assumptions remain.
No selected cold replay or formal-kernel proof was run. Independent human
and formal proof-kernel review are unclaimed. Exact provenance and the
original task card are in SOURCES.json and TASK.json. Apache-2.0.

## Open next questions

- Bind one actual coded child pair to `cB=Bq` and price c, the two AB
  complements and all frame/ownership boundaries. Begin with a single
  chronological PR4933 child substitution; physical query access is the
  blocker, and a formal conjugation alone is insufficient.
- Can a changed scaffold avoid the transported query at lower complete
  cost? Begin with one explicit replacement operation and independent
  inputs. The present necessity theorem applies only to this fixed
  scaffold and cannot exclude that different interface.

## Verifier constraints

The verifier has no recursion, subprocesses, dynamic code execution or
network access. Functions stay below 60 lines. Its fixed domains have at
most 81 raw matrices per field, 2,520 tested triples, eight basis columns
per triple and 4-by-4 symbolic matrices. Symbolic products enforce at most
128 nonzero output terms and 64 letters per reduced-product input. A product
can hold up to 16,384 terms before combining equal words. It fails on
capacity exhaustion. Package reads are limited to one MiB per file.

Power-of-ten rule 3 deviation: CPython allocates managed dictionaries,
tuples and integers during this bounded one-shot check. The explicit
domains, term/word capacities and file limits bound live data, rather than
providing a fixed-allocation runtime. A fixed-storage deployment would
need a separate implementation. Both warning-strict registered modes
exercise the actual checker; no external static type checker is required
or claimed. No predecessor or shared implementation is modified.

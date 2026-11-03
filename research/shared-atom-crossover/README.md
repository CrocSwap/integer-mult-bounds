# Exact affordability of shared atom powers at fixed total exponent

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written cost proof with exact finite corroboration.
No new kappa or selected-frontier change is claimed.

For Tekalign / tekuuu's [PR4077](https://github.com/CrocSwap/integer-mult-bounds/pull/4077)
shared atom-power interface, the total exponent alone can certify that every
placement saves source actions. The new result computes the sharp threshold
for all three equal-width exponents with that total. It answers the package's
open parameter-region question using its exact tariffs as cited premises.
No predecessor executable or scientific replay is run.

For I-bit exponents, radix width w, sum E>0, positive count k, total binary
population S and total bitlength B, the exact old-minus-new scalar saving is

```
Delta = (E-1)rho - H,
H = 15(w-1)E - 5(w-1)S + B + k(14wI+36w-9).
```

Here rho is the complete residue read/write/move total of one radix traversal.
Every record, residue and index action has unit weight. For E>=2, a binary
carry maximum with at most 24 states per bit computes H_max and an attaining
triple. Strict saving for every sum-E triple holds exactly when
`rho > H_max/(E-1)`. The all-zero case ties, and total one always loses.
[PROOF.md](PROOF.md) establishes the uniform theorem, carry invariant and
strict endpoint. The operation count is at most 192I mask trials, with
integer arithmetic and witness costs stated separately.

The first explicit case has I=4,w=1,E=10. Its exact maximum is 257, attained
by (4,4,2), so integral rho>=29 suffices and is sharp. The simpler separate
bounds on k and B only certify rho>=30. At rho=29 every such triple saves
at least four actions; at rho=28 the attaining triple loses five. These are
parametric tariffs, not claims that a validator of cost 29 was executed.

For actual child extents, E=2(n-c), where n is the parent width and c is
the child width. The theorem supplies a sufficient condition for every
admitted placement fitting I bits. Exact necessity concerns the larger
sum-conditioned triple domain; actual source geometry may exclude a witness.
No runtime dispatch, physical action exchange rate or full caller improvement
is supplied. Count output work cancels by the cited source contract.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-atom-crossover
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/shared-atom-crossover/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/shared-atom-crossover/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-atom-crossover --check-source-history
```

Any CPython 3.12 executable can replace the absolute interpreter path. Expected
markers are `PASS_SHARED_ATOM_CROSSOVER`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. The final command needs committed bytes and
full Git history. The direct checker also works in a Git-free package export.
It writes nothing and prints a freshly generated receipt bound to all seven
package source/metadata files. No success receipt is handwritten.

The new carry algorithm is compared with direct tariff maximization over all
149,792 ordered triples at I=1..5 and w in {1,2,3,7}. All 704 maxima, including
zero totals, agree. `oracle.py` applies the cited vector costs directly,
without importing the new carry algorithm. These checks establish agreement
on the stated finite domain, not independent review of the inherited tariffs.
The sharp strict boundary, E=0/E=1, an undercut maximum, an unattainable
combination of separate bounds, larger-width attaining witnesses and twelve
invalid arguments are checked. Explicit exceptions retain every check under
optimized Python. The written proof supplies the universal quantifiers.

## Scope, sources and credit

Canonical base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8,
selected PR6030 at kappa .003125804. The selected source-binding orientation
passed; it is metadata orientation, not a scientific selected replay.
The formal-interface-lemma card explicitly changes to this written cost
criterion rather than a proof-assistant theorem or discharge of a selected
assumption. [TASK.json](TASK.json) records that change.

Credit Tekalign / tekuuu for PR4077's shared encoded atom powers, actual
child-extents adapter, exact vector tariffs and open affordability question.
David Arias / PR2753, Jose Manuel / jmbarrancoml, ToikY / PR4025,
ywz65 / PR2590, Chris R / Clear1nsight / PR4062 and their retained caller,
record and source contributors retain credit. Binary digit dynamic programming
and scalar tariff algebra are classical; no global literature-priority claim
is made. The new result is this exact sum-conditioned maximum and its sharp
application to the stated interface.

[SOURCES.json](SOURCES.json) binds the unchanged main-tree predecessor proof
and README as historical provenance. They are not executable dependencies.
[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371189).
Live open/account PRs, handoffs, active Discussions, main-tree object/formula
searches and merged searches were checked. The broader cache covered 521 open
PRs and 6,530 Discussion records, while local notes were sparse. Unpublished
work, arbitrary historical diffs and global literature priority remain outside
that coverage. Search absence is not a novelty certificate.

The theorem is conditional on the cited successful-input source tariffs.
Physical allocator/control costs, an encoded selector, actual validator
prices, full Context/payload composition, stock, precision and supplier/outer
admission are unrun obligations. No predecessor audit, selected cold replay,
Lean or Docker run is part of this contribution. All five selected assumptions
remain. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can actual source geometry reduce the sum-conditioned maximum further?
  Start with one pinned native child family, its legal placements and external
  gap constraints. The present attaining triple need not be a legal child.
- Can an encoded caller use the crossover without spending its gain on
  selection? Start with a source-bound lower bound for rho and a fixed
  parameter region. A host calculation of the threshold is not a paid
  runtime decision or a complete physical caller.

## Code bounds

The mathematical proof permits all positive I,w; the reference API caps I at
4096 and w below 2^64. The exhaustive oracle caps I at five and four fixed w
values. Carry layers have at most 24 records and at most 192 transitions per
bit; each record holds three bounded-width witness integers. Source reads are
capped at 128 KiB per file. Functions are below 60 lines. There is no recursion,
subprocess, network, dynamic code generation or mutable shared state. The
checker uses normal and optimized warning-strict execution as its available
Python diagnostics; no separate type checker is claimed as run.

Power-of-Ten rule 3 deviation: Python and its standard library allocate managed
integers, tuples, dictionaries and JSON. The fixed API limits, two bounded state
layers, a 94-entry oracle maximum table and streamed triple enumeration bound
live collections. This is not a fixed-pool, allocator-internals or real-time
claim. Larger domains must revise those caps before use. Standard-library
iterator and JSON dispatch have fixed targets; the code defines no callbacks.

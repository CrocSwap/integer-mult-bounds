# Every group diagonal has exact scalar-rank cost d

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written algebraic proof with exact finite corroboration.

In Ali Romman's [#5394](https://github.com/CrocSwap/integer-mult-bounds/pull/5394)
formal group-gate model, let d count the nonidentity entries of a diagonal
target, with repetitions counted by position. For every field and every
group, finite or infinite,

```text
minimum total projector rank = minimum rank-one call count = d.
```

Equality assumes each target label is an allowed paid label. The lower
bound needs no such assumption. Arbitrary finite scalar workspace,
rectangular or singular free scalar maps, copying, reset and discarded
garbage do not lower the bound. Dirty inputs may be arbitrary; the attaining
coordinate construction restores them.

[PROOF.md](PROOF.md) proves that all nonidentity coefficient images of a
circuit lie in one scalar space of dimension at most the total paid rank.
The diagonal target needs exactly d scalar directions. No finite group
representation, characteristic assumption or inverse free map enters the
proof. The lower bound even permits nonidempotent paid couplings.

This closes #5394's four-or-more-target rank-one question. Its unit-price,
arbitrary-rank invocation optimum remains the credited subproduct-cover
number. Rank-one count exceeds that optimum exactly when the cover number
is below d. The prime-exponent and coprime cyclic cases of Nick Petalas's
older #6008, and the binary semilinear case of Krzysztof Wojt's #5242,
retain their prior credit. We do not replay those results.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/all-group-diagonal-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/all-group-diagonal-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/all-group-diagonal-rank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/all-group-diagonal-rank --check-source-history
```

Another CPython 3.12 path can replace the absolute local path. The direct
command prints `PASS_ALL_GROUP_DIAGONAL_RANK` inside a generated JSON
receipt bound to all six package-file hashes. Both registered commands run
the full finite corroboration. The publication check requires the committed
package and full history. No receipt is handwritten or stored as an input.

The checker constructs new circuits over C4, C6 and S3, over F2, F3 and F5.
It checks the transported common image, the rank charge and the complete
regular-action matrix against separate ordinary matrix multiplication.
A literal enumeration of all row combinations independently checks every
circuit's coefficient rank. Direct diagonal words include repeated labels,
identity targets, the three-copy order-two target in C4, and two arbitrary
restored dirty roles. Normal and optimized execution use explicit exceptions.
The receipt reports the executed counts. These finite checks corroborate
the written proof; they do not establish its universal quantifiers alone.

Local CPython 3.12.15 runs pass 216 new circuits with 540 paid gates,
561 rectangular free maps and 79 singular square free maps. All 57,024
regular-matrix entries agree, and 133 circuits have positive coefficient
rank. The 54 direct endpoint fixtures cover 1,512 regular basis columns,
including 36 fixtures with repeated labels. These counts include fixture
occurrences rather than distinct maps across the complete run.

Eight controls distinguish repeated positions from distinct labels,
unit-price invocations from rank charges, forbidden free address maps,
free singular scalar maps, invalid idempotents, noncommutative order,
omitted calls and characteristic-two cancellation. The fixed seeded circuits
are probes, not an exhaustive search of circuit words.

## Sources and scope

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8, selected #7000 unchanged. The selected source-binding baseline
passed with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. It was orientation only.
[TASK.json](TASK.json) records the change from the bit-new-register-model
card to this formal all-group side result. [SOURCES.json](SOURCES.json)
contains provenance-only pins; the verifier has no external scientific inputs.

Ali Romman #5394 supplies the model, cover theorem, triple result and open
question. The coefficient-span method has precedent in Arham Tahir #1919
and the retained clean-workspace image-span reduction. Preserve the group
model lineage of Cinna Davis, JoyboyBrian and their cited register-model
predecessors. The new contribution is the rectangular common-image proof
and its complete arbitrary-group application, not a new general invention
of coefficient-span methods. Predecessor scientific suites are not replayed.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19540700)
precedes the new verifier. Main and merged object/formula searches, open PR
bodies, recent account work, active Discussions and local reservations were
checked. The overlap cache covers 502 open PRs and 7,179 Discussion records;
its local note coverage is sparse. All-main Git searches cover the relevant
omitted README texts. These are bounded overlap checks, not proof of novelty
against unpublished work or every historical diff.

Formal coefficientwise equality, fixed schedules and scalar free maps are
essential. A quotient address representation, free address operation or
data-dependent control changes the model. This result prices no native
group action, physical caller, frame conversion, source access, precision,
tape movement, hosting or complete recursive invoice. No new kappa,
supplier admission or selected-frontier change is claimed. Selected cold
replay, Lean and Docker are unrun. Independent human and formal proof-kernel
review are unclaimed.

## Code constraints

The standalone checker has no recursion, subprocess, network call or file
mutation. Circuit widths are at most four, words have at most four gates,
groups have at most six elements, and the row-space oracle has at most
three rows and 125 combinations. Diagonal fixtures have at most seven
registers including the two dirty roles, so regular matrices have at most
42 rows and columns. All functions are shorter than sixty physical lines.
Every loop ranges over these fixed domains or a collection they bound.

Power of Ten rule 3 has a managed-allocation deviation for this one-shot
CPython checker. Live state is bounded by the displayed shapes, at most
six coefficient matrices per formal product, and one row-space set of at
most 125 vectors. Runtime and standard-library allocation cannot be fixed
statically. A deployment requiring allocation-free operation would need
fixed buffers; this verifier claims no such deployment. Warning-strict
development-mode normal and optimized checks provide runtime diagnostics.
The rank-elimination and literal-row-space algorithms are separate.
Source compilation and function-size inspection are part of local checks.

## Open next questions

Can a specified native address quotient escape this formal coefficient
bound and still improve the complete supplier bill? Begin with one exact
representation and a new target whose formal coefficient images collapse
in that representation. A paid native implementation, dirty restoration,
precision and complete caller charges remain the blockers. The current
theorem does not price such a quotient or reserve a follow-up.

For a fixed rank cap and positive invocation overhead, which subproduct
covers minimize the full rank and invocation bill together? Begin with one
four-target mixed-order example and retain both charges for each gate.
The present d bound and the predecessor's invocation optimum need not be
attained by the same word. Physical realization remains separate.

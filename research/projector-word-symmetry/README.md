# Exact symmetry quotients for width-two projector words

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

This is a scoped algebraic proof with exact finite corroboration. It answers
the symmetry-reduction blocker in Open next question 1 of Josie Elliston's
[PR6137](https://github.com/CrocSwap/integer-mult-bounds/pull/6137), building on
JoyboyBrian's [PR6097](https://github.com/CrocSwap/integer-mult-bounds/pull/6097).
Their collision obstructions are cited premises, not audit or replay targets.
No predecessor scientific executable is imported or run.

## Result

Let X be the rank-one idempotents of M_2(F_q), n=q(q+1), k=2m+1 an odd
positive integer, and epsilon=0 for even q and 1 for odd q. Simultaneous
monomial conjugation and reversal with transpose preserve the universal
width-two diagonal-pair search family. Their action has exactly

\[
 \frac{n^{2m+1}+2^{2m+1}\left(q-2+\epsilon\frac{q-1}{2}\right)
       +(q-1)(q+\epsilon)n^m}{4(q-1)}
\]

orbits on X^k. [PROOF.md](PROOF.md) proves the reduction, the finite-field
formula and the covariance of the coefficient-class collision relaxation.
The monomial group preserves the unordered pair of coordinate projectors.
Reversal with transpose transports the group to its opposite. A fixed
oriented group/label/target problem needs its specification transported too.

For five calls the exact domain counts are:

| Field | All projector tuples | Representatives under the declared action |
|---|---:|---:|
| F2 | 7,776 | 1,962 |
| F3 | 248,832 | 31,256 |
| F4 | 3,200,000 | 267,072 |
| F5 | 24,300,000 | 1,520,110 |

The standalone verifier enumerates every tuple in this table, independently
of the fixed-point formula. It supplies a deterministic canonical-index
function, orbit-size histograms and hashes of the sorted representative
indices. Counts are search-domain cardinalities, not measured speedups.
No claim is made that this is the largest safe symmetry group.

This removes one specific prerequisite for a smaller collision search.
It does not run that search, refute a new field, reproduce the predecessor's
F2/F3 results, or certify any group realization of a relaxed partition.
The investigation stops at this first verified reduction.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projector-word-symmetry
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/projector-word-symmetry/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/projector-word-symmetry/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projector-word-symmetry --check-source-history
```

Use an equivalent CPython 3.12 path on another machine. The direct marker is
`PASS_PROJECTOR_WORD_SYMMETRY`. Each direct run emits a generated JSON receipt
with counts, representative digests and SHA256 hashes of all six package
files. It writes no files and needs neither Git nor network access. No
hand-written receipt is used as evidence. Registered normal and optimized
commands both cover the complete table and use explicit checks that survive
Python optimization.

The finite checks also construct the fields of orders 2,3,4,5,7,8,9, compare
two projector inventories, count every fixed projector, and check the formula
at lengths 1,3,5. New formal positional words test conjugation and
opposite-group covariance. Fifteen rejecting controls and two semantic
controls distinguish invalid replay inputs, transpose without reversal, and
a scalar adapter outside the target normalizer. These finite checks
corroborate the universal written proof, which is not a formal-kernel proof.

## Scope and credit

The base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8, selected PR6030. The selected binding orientation passed;
it was metadata orientation rather than a scientific replay. The
`bit-new-register-model` card changes explicitly to this formal search-domain
side result. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373332)
records the question. [SOURCES.json](SOURCES.json) pins historical provenance;
there are no live or executable predecessor dependencies.

Josie Elliston / PR6137 supplies the explicit symmetry blocker and the F3
context. JoyboyBrian / PR6097 supplies the diagonal-pair model, collision
relaxation and F2 context. Retain Josie Elliston / PR6048, Nick Petalas /
PR6038, Wentao Li / PR4089/4093, Cinna Davis / PR2246 and their credited
register-model lineage. Projector conjugacy, orthogonal projections over
finite fields and Burnside's lemma are classical. The contribution is the
explicit quotient, exact orbit formula and standalone canonical enumeration
for this search family; global literature priority is unclaimed.

Before claiming, live handoffs and active Discussions, open PRs, this
account's recent work, local reservations, all-main README searches and
merged PR searches were checked for the object, formula and general form.
The overlap snapshot covered 555 open PRs and 6,593 Discussion records with
complete remote pagination. Its sparse local scan omitted 8,787 main note
paths; the separate Git searches covered all main READMEs for the named
terms. Arbitrary historical diffs and unpublished work remain limits.
Searches are not a novelty certificate.

No new kappa, physical speedup, supplier admission, selected-frontier change,
complete multiplication theorem or discharge of any of the five selected
framework assumptions is claimed. Native conversion, scalar/frame/movement
costs, restoration, precision, compiler closure and a complete paid consumer
remain outside the result. No Lean, Docker or historical scientific suite ran.

## Open next questions

Can the F4 or F5 representatives settle the five-call existence question?
Start by transporting every coefficient equation and cancellation rule to
the canonical tuple, then emit an independently checkable refutation or an
actual group realization. No such solver or certificate is supplied here.
The quotient alone proves no new call minimum.

Can a specified Frobenius action reduce this domain further? Prove covariance
and count its fixed tuples before omitting cases. The present group need not
be maximal. [TASK.json](TASK.json) records these questions, their relevance,
first steps and blockers. No follow-up is reserved.

## Verifier bounds

The verifier has no recursion, subprocess, network access, dynamic code
execution or mutable shared store. Field orders are restricted to the seven
listed values, tuple lengths to 1,3,5, and complete tuple enumeration to
24,300,000 entries per field. A census owns one byte array of that size;
its orbit set has at most sixteen indices. Fields checked without a complete
census have at most ninety projectors and thirty-two transformations.
Coefficient expansion has at most thirty-two words. All functions fit
within sixty physical lines. Invalid domains fail explicitly.

Power of Ten rule 3 has a managed-runtime deviation in verify.py. Python
integers, tuples, dictionaries and arithmetic temporaries allocate during
replay; the platform cannot provide allocation-free interpreted execution.
The enforced finite domains above bound live storage. The byte array is
allocated once before each census and released on return. A larger census
must first change and justify the explicit capacity gate. Warning-strict
normal and optimized execution provide the supported interpreted diagnostics;
no external static analyzer or proof assistant is assumed installed.

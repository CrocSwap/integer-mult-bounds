# Sharp threshold for singular right-vector products

Scoped algebraic proof with a finite certificate. No new kappa.

Let K=F_q and R=K^k. Use two roles, paid factors I+u y^T with u in R^2
and y in K^2, and common GL_2(K) maps free anywhere. Suppose every component
of a target M=(M_1,...,M_k) is a nonzero rank-one matrix. Then

```text
k < 2(q+1): every target costs at most two paid factors.
k >= 2(q+1): some target costs exactly three.
Every target costs at most three.
```

This answers a singular-target part of the open direction in ToikY's #4334
and Nick Petalas's #4601. Their invertible-component threshold is q+1.
The changed singular contract permits a zero pivot when the entire row
vanishes, so the invertible common-unit-pivot test does not apply.

The new exact criterion is particularly simple. For each input line T,
collect the image lines of components having kernel T. Two paid factors
suffice exactly when at least one T has at most one distinct collected
image line. An obstruction therefore needs two different image lines for
EVERY kernel line. An explicit family with two components per kernel
attains the threshold. Over an infinite field every finite such tuple
costs at most two. The [proof](PROOF.md) cites #4276's low-factor criterion
and supplies a common-right-vector e1,e2,e1 word for the three-factor bound.
No predecessor code or verifier is imported or replayed.

## Exact finite evidence

The standalone standard-library verifier constructs literal binary one- and
two-factor images with every paid left vector, common right-vector line and
common free endpoint. It includes singular paid factors. The complete
rank-one alphabet has nine matrices, so all 512 support sets suffice to
compare literal membership with the new criterion for tuples of any length.
There are 64 obstructed supports, all with at least six distinct matrices.
A finite support recurrence counts ordered tuples through six components.
It is an exact multiplicity enumeration, not a raw scan of every tuple.

```text
components   tuples   cost 1    cost 2   cost 3
1                 9        9         0        0
2                81       27        54        0
3               729       63       666        0
4              6561      135      6426        0
5             59049      279     58770        0
6            531441      567    511434    19440
```

All these targets have cost greater than zero because every component is
singular. The six-component count 19,440 is also derived directly in the
proof. The code checks that count against the literal-chart enumeration.

Over F2,F3,F4,F5,F7 the verifier checks the three-factor word on every
2-by-2 matrix, including singular and zero matrices. This covers 3,379
matrices and 138,163 arbitrary-input evaluations. F4 is implemented as
F2[t]/(t^2+t+1). It also checks the sharp threshold witnesses at component
counts 6,8,10,12,16 and all 52 single-component deletions. Field-table
associativity, distributivity and inverses are checked before using them.

Controls discriminate separate component charts, repeated equal image
lines, reversing the word, omitting its final factor, odd-field sign errors
and using the composite modulus six as a field. The deletion controls show
that every component of the explicit threshold witness matters. Checks use
explicit exceptions and remain active under Python optimization.

Every run emits a generated JSON receipt binding all six package files by
SHA256, followed only by stdout data. No receipt is hand-written or saved
in the checkout.

## Reproduction

From the repository root, using the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/singular-product-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/singular-product-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/singular-product-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/singular-product-threshold --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter above.
Expected verifier marker is
`PASS_SINGULAR_PRODUCT_THRESHOLD binary_cost3=19440 threshold=6 no_new_kappa`.
Both normal and optimized checks are registered with 120-second limits.
SOURCES.json binds the predecessor statements and task catalogue as historical
provenance at base 624de9dc66858af0945e5f8a0942488d62280d43. There are no live
external inputs and no dependence on an unmerged Git object.

The original formal-interface-lemma card is explicitly changed to this
algebraic side question in TASK.json. Its historical first command,
`scripts/research_baseline.py`, fails with `KeyError: 'bit_lower'` on the
changed selected schema. After materializing the selected source closure,
`scripts/research_selected_baseline.py` passes with selected 60403/20000000.
That orientation check authenticates metadata only. No shared helper is changed.

## Limits and verification design

The universal claim is the written scoped proof. The exhaustive support
certificate is binary; other fields have the finite word and sharp-witness
checks stated above. Local radical lifts, non-field factors, mixed-rank
thresholds and more than two roles remain outside the main theorem. The
three-factor construction alone covers arbitrary matrices over K^k.

Native coefficient preparation, access, routing, control, restoration,
precision, stock and complete supplier costs are unknown. No supplier,
selected frontier or complete multiplication theorem changes. Independent
human and formal proof-kernel review are unclaimed. No Lean, Docker or
selected operator replay is needed for or included in this isolated package.

The code has no recursion, child process, network access, solver or CLI input.
The field orders are restricted to five fixed cases with q<=7. Field-table
loops use at most 7^3 triples; matrix loops use at most 7^4 targets; vector
loops use at most 7^2 inputs. Binary image construction uses 3*6*3*4^2=864
two-factor cases. Each support table and recurrence dictionary has at most
512 entries; there are exactly six recurrence rounds. The sharp families
have at most 16 components. Receipt reads are limited to six fixed files
of at most 1 MiB each. The program writes only to stdout.

Power of Ten rule 3 has a managed-runtime deviation. Python allocates
integers, tuples and finite sets during enumeration. The explicit fixed
domains bound live state to the 512-entry support/counter tables, tiny field
and literal-image tables, and one matrix/word at a time. A fixed-buffer
implementation would be the follow-up if the domains expand. Functions
remain below the 60-line review ceiling. Warning-strict normal and optimized
runs are registered in CI; no separate type checker or linter is required.

## Open next questions

1. What replaces the kernel/image criterion for rank-one residue targets
   over products of local algebras? Start with two specified dual-number
   components and enumerate their right-ideal constraints. Nilpotent
   off-pivot entries can invalidate a zero residue pivot, so the field
   threshold does not settle that question.
2. Can one literal native producer/consumer realize the common-right-vector
   alphabet at a favorable complete cost? First specify its coefficients,
   access, restoration and precision contracts and full bill. Those physical
   obligations are unknown; the formal word supplies none of them.

TASK.json records why each question matters and its first bounded step.

## Credit

This package was produced by Nick Petalas. ToikY's #4334 supplies the
invertible field-product predecessor and its singular-target gap. Nick
Petalas's #4601 supplies the local-product follow-up, #4276 supplies the
exact low-factor criterion, and #4243 supplies the common-free normal form.
Wentao Li's #4099 supplies the alphabet and column bound, building on #2513.
Projective-line counting and elementary matrix algebra are classical.
The new contribution is the singular kernel/image criterion, its sharp
threshold and the stated finite certificate. Apache-2.0.

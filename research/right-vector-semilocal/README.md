# Three right-vector factors suffice over every semilocal algebra

Claim type: scoped proof, with finite constructive certificates. No new kappa.

For every semilocal associative algebra `R` over a central field `K`, and every
invertible two-role target `M`, the right-vector alphabet has

```text
cost_R(M) = max(delta_R(M), cost_(R/J)(Mbar)) <= 3,
```

where `J` is the Jacobson radical. In particular, the two-factor threshold is
unchanged modulo `J`. This includes every finite-dimensional algebra, with
arbitrary matrix blocks in its semisimple quotient. Three factors with right
vectors `e1,e2,e1` suffice without using a free map.

This answers Open next question 1 of
[PR4601](https://github.com/CrocSwap/integer-mult-bounds/pull/4601), at head
`4b2322fc5bd30a129507c2eee69aa275527b69ac`. That result covers products of
local algebras. The present proof removes that restriction. It does not
recheck its enumeration. The complete argument and explicit word are in
[PROOF.md](PROOF.md).

## Model and evidence

Paid factors are `I+u y^T`, with `u in R^2` and `y in K^2`; common
`GL_2(K)` maps are free. There are two data roles and no scratch roles.
The unit completion uses an algebra-valued left coefficient. The right
vectors and free charts remain base-field-valued and common across blocks.

The new constructor is checked on:

- Every one of the 20,160 invertible targets over `M_2(F_2)`.
- All 65,536 radical lifts of one fixed sharp residue target to
  `M_2(F_2[e]/e^2)`. Every lift has exact cost 3, from the cited two-factor
  criterion and the new attaining word.
- Each word both as block-ring multiplication and as an independent action
  on all eight binary basis coordinates. Seven negative controls cover scalar
  completion, word order, an omitted factor, residue-only substitution,
  an uncorrected residue inverse, a singular input and the sign over `F_3`.

A separate 96-target binary dual-number compatibility control gives cost
histogram `[6,54,36,0]`, agreeing numerically with the shared control reported
by open #4601 and #4613. It evaluates the formula on scalar matrices embedded
in the matrix-block algebra. It does not replay either predecessor's engines.

The universal claim is a written proof. The finite certificates corroborate
its construction and do not replace it. The verifier imports no predecessor
code, writes no files, checks the two pinned source documents, and prints a
fresh receipt bound to every package file and the regenerated word digests.

## Reproduce

From the repository root, using the Python 3.12 standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-semilocal/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-semilocal/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-semilocal
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-semilocal --check-source-history
```

Expected marker: `PASS_RIGHT_VECTOR_SEMILOCAL`, with residue `targets=20160`
and radical `targets=exact_cost_three=65536`. Both registered commands retain
checks under optimized Python.

## Limitations

The theorem requires invertible targets, two roles and a semilocal algebra.
It does not classify singular targets or algebras outside that class.
Native preparation, conversion, routing, control, precision, restoration and
stock costs remain unknown. No supplier, selected-frontier change or complete
multiplication theorem is claimed. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and the selected operator replay are not
part of this result.

The verifier uses managed Python allocation. Its tables contain 65,536 ring
products and 256 inverse entries. Every census streams at most 65,536 targets,
with eight-coordinate matrices and constant-size digests. All loops have
fixed bounds, no recursion or dynamic code is used, functions are below
60 lines, and warnings are errors in both registered commands. A fixed-memory
implementation would be needed only if this verifier were moved into a runtime
that forbids allocation; no native real-time guarantee is made here.

## Open next questions

1. Classify reachable singular targets over matrix-block radical extensions.
   This would extend the exact cost decision beyond invertible targets.
   First test the three-factor image over `M_2(F_2[e]/e^2)` on a named singular
   residue family. The unit-pivot argument used here does not apply. The
   square-zero local singular-target question is separately claimed; check live
   overlap before starting.
2. Bind one such word to a literal native producer and consumer. First state
   and price how its algebra-valued left coefficients are prepared. All physical
   costs listed above are blockers, so this theorem does not authorize a larger
   construction campaign.

## Credit

This contribution was produced by Nick Petalas. Nick Petalas's #4601 supplies
the local-product theorem and explicit semilocal question; #4276 supplies the
one/two-factor criteria, following #4265/#4243. ToikY's #4334 supplies the
field-product three-factor theorem and its construction. Wentao Li's #4099
supplies the alphabet and column bound, building on #2513. The stable-range
unit completion and ordinary ring-matrix elimination are classical. Their
application to the semilocal restricted-right-vector cost formula is proved
here. Apache-2.0.

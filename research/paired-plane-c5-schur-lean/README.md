# Lean core for the paired-plane C5 Schur obstruction

The C5 lower-bound proof in [PR2484](https://github.com/CrocSwap/integer-mult-bounds/pull/2484)
uses a square-block inverse step and a Schur factorization. This package
formalizes that precise algebraic interface in standalone **Lean 4.34.1 / Std**,
and binds its mask to the actual five planes in the predecessor certificate.

The exact formal theorem is `PairedC5.no_four_pivot`: over any commutative ring
with `0 != 1`, a five-by-five matrix of two-by-two blocks with identity diagonal
blocks and the five C5 forbidden unordered block pairs cannot satisfy

```
M_ij = M_i0 M_0j + M_i2 M_2j    for every i,j.             (1)
```

This is the normalized four-scalar-pivot factorization through planes 0 and 2.
It is **not a theorem whose formal hypothesis is `rank(M)<=4`**: this standalone
file has no matrix-rank definition or Mathlib dependency. The standard
linear-algebra implication from rank at most four and an identity pivot to (1)
remains written mathematics. The full rank-49 result is credited to PR2484;
it is not newly claimed to be fully Lean-formalized.

## Formal proof and boundary

`Schur.lean` defines literal two-by-two matrices, addition and multiplication.
It proves associativity, identities and zero laws from the commutative-ring
axioms. The square-block direct-finiteness theorem

```
XY = I_2  =>  YX = I_2
```

is proved algebraically, not assumed. It supplies the right cancellation step
needed by the Schur proof. This avoids silently using rectangular one-sided
inverses as if they were square.

Write the five planes in cycle order as A,B,C,D,E. Their diagonal blocks are
`I_2`; the forbidden unordered pairs are AC, AD, BD, BE and CE. Equation (1)
at DD and EE gives

```
M_DC M_CD = I_2,       M_EA M_AE = I_2.
```

At BD and BE it gives `M_BC M_CD=0` and `M_BA M_AE=0`. The proved inverse and
cancellation lemmas force `M_BC=M_BA=0`. Equation (1) at BB would then make
`I_2=0`, contradicting nontriviality of the coefficient ring. No symmetry,
ordering, characteristic restriction, chosen scalar coefficients or numerical
rank computation is assumed.

Four further Lean theorems check a concrete **integer** boundary witness:
free the BD pair, assign A/E one pair of coordinates and B/C/D the other pair.
The resulting ten-by-ten matrix has identity diagonal blocks, every other
required zero block, and the exact four-pivot factorization. Its BD and DB
blocks are `I_2`. This is a valid factorization of the relaxed mask, not a
counterexample to the strict-mask theorem. The same literal 0/1 matrix also
works over the rationals.

## Binding to the source mask

The external Python checker authenticates the selected source archive, its
`DATA-PHASES.json` member and the PR1825 matching fixture before parsing them.
It reconstructs all 56 complete four-element binary plane spans and their
orthogonality, importing no predecessor executable. It verifies the exact
PR2484 core

```
(13,23,35,16,34)
```

in that cycle order. Its ten scalar ports have exactly the formal `Far`
predicate's 40 forced off-diagonal scalar zeros, plus identity diagonal blocks.
It also checks the predecessor's 22-plane nonorthogonal clique and all core
cross pairs. Those 44 ports give `I_44`, with 880 forced zero cross entries,
so the 54-port principal submatrix is `I_44 (+) M`.

The usual field argument then gives the predecessor's lower bound: rank at
most four for M, together with its I4 pivot, implies (1), contradicted by the
formal core; hence `rank(M)>=5` and the full fitting matrix has rank at least
49. **The field-rank bridge, rank monotonicity/additivity and Python-to-Lean
source correspondence are external to the Lean theorem.** The Python check
certifies the finite mask premises; it does not turn them into imported Lean
constants or prove the rank bridge.

The credited rank-49 upper bound, fractional colouring and graph optima are not
rerun here: they are unnecessary for this formal-interface contribution.
This addresses PR2484's stated unformalized-lemma boundary rather than adding
another equivalent finite rank search.

## Reproduce and validation status

Fresh formal kernel check, including axiom inventory and four deliberately
false weakened/mutated statements:

```sh
python3.12 -I -B research/paired-plane-c5-schur-lean/check_lean.py --lean /path/to/lean-4.34.1/bin/lean
```

This command actually ran locally with Lean 4.34.1 and CPython 3.12.14. All six
named theorems compiled, using only the ordinary `propext`, `Classical.choice`
and `Quot.sound` axioms (the concrete boundary theorems use only `propext`).
No `sorry`, extra axiom, `native_decide`, unsafe definition or untrusted tactic
result is admitted. Four mutations are rejected: wrong reverse inverse,
zero diagonal, absent nontriviality, and freeing BD. `LEAN-CHECK.json` records
the exact source hash and local result. It is a recorded receipt, not a
substitute for rerunning the command.

Finite source-binding replay, standard library only:

```sh
python3.12 -I -O -B research/paired-plane-c5-schur-lean/verify.py
python3.12 scripts/research_package.py --package research/paired-plane-c5-schur-lean
```

The registered Python hook checks the finite source binding and recorded formal
source hash; **it does not run Lean**. Its output states that distinction.
It also checks the entire receipt, literal relaxed factorization, modular
rank-four cross-checks and four rejecting controls. Boundary tests cover
unchanged Git-free export, altered formal source, wrong receipt, source drift,
and exclusive regeneration. `--out NEW.json` and the formal checker's optional
`--out NEW.json` both refuse to overwrite. On Windows, TEMP/TMP may need a
writable workspace directory. No selected supplier cold replay or hosted-CI
success is claimed.

## Open next questions

The next formal step is the field-rank-to-normalized-pivot lemma in a maintained
matrix library, followed by embedding this exact source mask and I44 block.
This package deliberately states that missing bridge as an obligation; it does
not claim a machine-checked rank-49 theorem. Separately, the native cost of
the 49 scalar channels remains open. None of the formal algebra prices COPY,
physical frames, dirty storage, hosting, precision, tape or all-size admission.
No new supplier, kappa or selected-frontier change is claimed.

## Credit and provenance

Base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority four.
The fresh picker selected independent-verification/formal-interface-lemma.
[TASK.json](TASK.json) records the exact scope and overlap coverage;
[SOURCES.json](SOURCES.json) records source SHA256/Git bindings.

Credit **thakrarsagar / PR2484** for the exact rank-49 result, C5 core,
22-plane clique and both written proofs, including the reviewer-suggested
Schur proof formalized here. Credit ywz65 / PR2471 for the preceding bracket,
Cinna Davis / PR1825 and PR2126 for the matched planes and scalar fit, Adam
Gall / PR1889 for the strict mask, Jeremy Diviney / PR2203 for the physical
payload distinction, Philippe Van Velzen and Josie Elliston / PR1977 for the
related plane and submatrix bounds. Frozen evidence remains unchanged.

Prepared for **ywz65** with substantial OpenAI Codex assistance in formalization,
binding checks and exposition. A separate AI-assisted reviewer inspected the
typed statement, cancellation order, six audited theorem roots and stated
formal/external boundaries, with no actionable finding. Apache-2.0. No independent human review is
claimed. Lean kernel checking and external finite validation have the distinct
scopes stated above.

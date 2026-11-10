# A 237-row exact P112 demand system

For the fixed 14-variable, 280-row cap-demand matrix of Nick Petalas's
[PR6425](https://github.com/CrocSwap/integer-mult-bounds/pull/6425), exact
nonnegative rational combinations remove 43 rows. The retained 237 rows are
equivalent for every nonnegative real multiplicity vector. Each retained row has
a rational point satisfying all 279 other original rows and strictly violating
that row. Together these certificates establish the **unique minimum subfamily
of the original 280 rows**, with `x >= 0` fixed.

This answers PR6425's first Open next question. Its pairwise reduction, source
clique census and geometry-to-demand equivalence remain credited predecessor
results; no predecessor executable or census is replayed. The present result is
an exact reduction of the literal source matrix. It supplies no coefficients,
decoder, physical supplier, COPY floor or κ improvement.

## Concrete implication

The first deleted mask is `0x1d1a`, demand 3. One half of each of the retained
rows `0x1412`, `0x1818` and `0xd0a`, each demand 2, gives RHS 3. The resulting
coefficient is 1 on target coordinates 1, 3, 4, 10, 11 and 12, and one half on
coordinate 8 (zero-based); all are at most the target's coefficients. The
missing half of coordinate 8 is supplied by `x_8 >= 0`. No single retained row
dominates this target: the source family was already pairwise nondominated.
`RESULT.json` retains all 43 exact combinations and all 237 full separating
points; `PROOF.md` gives the universal implication and restricted minimum proof.

## Replay

CPython 3.12 and the standard library suffice. No Git executable, network, solver
package or predecessor executable is needed for the package's two replays.

```sh
python3.12 -I -W error -B research/p112-farkas-kernel/verify.py
python3.12 -I -W error -B research/p112-farkas-kernel/oracle.py
```

Also run with `-O`. Default commands require strict complete retained JSON;
`--emit` prints regenerated output without overwriting files. The primary
regenerates the certificate with bounded exact `Fraction` packing simplex and
checks every implication and separator literally. The separate checker treats
the sealed primary result as untrusted certificate data and computes all
coefficient/RHS budgets and full-original-row separations independently. It does
not import the generator, solve an LP or claim blind rediscovery.

The generator uses 2,272 pivots, at most 49 per target, on this exact instance.
Explicit time/pivot/coefficient bounds fail closed. These are generation counts,
not a general runtime improvement. `VERIFY.json` registers the two bounded checks.
`SOURCE-PINS.json` authenticates both inert source files before parsing them.
`SOURCES.json` pins the originating current-main card/selected record as
provenance; all runtime bytes are package-local.

## Scope, evidence and limitations

The equivalence covers nonnegative real vectors and therefore preserves all
nonnegative integer tests too. Fractional separating points do **not** establish
integer-only indispensability or the smallest integer-only screen. The minimum
claim is over subfamilies of these original inequalities; it does not minimize
arbitrary newly introduced normals or alternative descriptions.

The independent checker exercises actual coefficient, demand, premise and
separator corruptions, along with source/schema controls. `VALIDATION.md`
records the actual run evidence, corrections and remaining obligations. Passing
this finite necessary-condition screen does not construct coefficient vectors
or pay for access, dirty restoration, precision, tape, stock, compiler or outer
integration. No native, Lean, Docker, selected cold supplier or complete
multiplication replay was run.

Orientation was frozen at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030, selected-record SHA256
`9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.
The broader `complex-rank-shape-decoder` card is explicitly changed to this fixed
support-screen implication. Main/overlap are rechecked before submission;
sparse/history/hidden/unpublished coverage limits are not novelty evidence.

## Open next questions

1. Can integer multiplicity implications remove further rows? Specify the
   integer domain and produce integer implication/separation certificates;
   fractional witnesses alone do not answer that question.
2. For changed support caps, what is the new exact demand screen? Rebuild the
   complete changed quotient before applying or attempting new combinations.
3. Can a passing vector admit actual coefficients and a fully charged decoder?
   Specify one vector and its full interface before synthesis and pricing.

## Credit

Credit Nick Petalas/PR6425 for the fixed matrix, pairwise reduction and explicit
combined-implication question; Jeremy Diviney/PR1422 for the complete-clique
guard, pinned geometry/caps and smaller-family question; Cinna Davis/PR1347/1323
and Navinor, David Arias, Hanson Sun, DreamingOfClouds, themilkman216 and the
retained E8/label/decoder lineage. PR5767 is related exact-certificate tooling;
its code and 128-variable cap are unchanged. Nonnegative implication,
packing/covering duality, simplex and Bland's rule are classical.

New work is ToikY with substantial OpenAI Codex assistance. Separate AI
certificate checking is not independent human review or formal proof-kernel
acceptance. `NOTICE` preserves attribution; the two source files remain verbatim.

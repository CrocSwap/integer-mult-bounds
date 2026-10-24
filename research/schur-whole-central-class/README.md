# The whole central class after sharp Schur deletion

For commuting idempotents P,Q with common identity pivot I_d, let S,T be the
Schur residuals, K=ST-TS, Z=(S-T)^2 and H=(PQ)_11. If rank K=2d, the complete
similarity class of Z is determined by H, residual dimension m, and one count:

    a1 = dim(ker S intersect ker(T-I))
         + dim(ker(S-I) intersect ker T).

[PROOF.md](PROOF.md) gives the all-field reconstruction. On the central
primary spaces at0 and1, first extend each Jordan block of K restricted to
im K by one, then square that chain. The remaining scalar blocks come from
ker K. Away from0 and1, the entire space is already in im K. This recovers
non-split and repeated primary factors as well as scalar eigenvalues.

This answers the characteristic-two handoff from
[PR #5267](https://github.com/CrocSwap/integer-mult-bounds/pull/5267) and extends
the restricted central action in
[PR #5256](https://github.com/CrocSwap/integer-mult-bounds/pull/5256).
For nilpotent H in characteristic two, each block k gives two blocks of length
ceil((k+1)/2) and two of length floor((k+1)/2), plus the specified scalar
summands. The padded binary H=J3 case has blocks `(2,2,2,2,1,1)`; its ternary
counterpart retains the predecessor's `(4,3,1,1,1)`.

The result classifies the central operator, not the whole ordered residual
pair or its header weights. The sharp rank assumption is required. The complete
kappa calculation and selected frontier are unchanged.

## Reproduce and evidence

Requires CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/schur-whole-central-class
```

Expected: `PASS_SCHUR_WHOLE_CENTRAL` in normal and optimized modes, followed
by `PASS_REGISTERED_RESEARCH_PACKAGE`. [RESULT.json](RESULT.json) records the
exact result digest, examples and file hashes. All1,244 H in seven complete
small prime-field domains are checked. Additional examples cover Jordan
blocks through size5 over F2,F3,F5,F7, scalar padding, mixed primary spaces
and a non-split repeated factor. Nine control groups include two admitted
pairs with the same H and residual dimension but different central classes.

The full-matrix oracle uses integer-lift characteristic polynomials and
primary power-rank invariants with a separately transcribed column-elimination
routine. It does not accept scalar eigenvalue samples or the image restriction
as a substitute for the complete class. The classifier currently implements
F2,F3,F5,F7; the written theorem is over any field. Finite corroboration does
not establish independent human or proof-kernel acceptance.

The exact source helpers and proof/attribution documents are retained from
pending predecessor heads in our own publication history. [SOURCES.json](SOURCES.json)
records original and retained pins. Every declared source commit is an
ancestor of this publication; no hidden local Git object is needed. Base:
ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision7. The full-history
wrapper, selected cold replay, Lean and Docker were not run.

## Open next questions

Can a1 be recovered from cheaper original header data for general H? Compare
it with the four original joint-sector dimensions when H has a nontrivial
eigenvalue-one primary component. This could avoid large residual kernel
calculations. No general original-header formula or physical consumer is
proved here. General nonsharp central reconstruction and full ordered-pair
classification remain outside scope.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
ssafwann supplies the restricted action, nilpotent model and open question;
Nick Petalas, Ryanson Jonathan and the wider Schur lineage retain the results
listed in [NOTICE.md](NOTICE.md) and the unchanged source documents. The
nilpotent ordered-pair rigidity, odd-field partition and fixed-H weights are
predecessor results. Classical Jordan-image, primary-decomposition and
Faddeev-LeVerrier methods are not claimed as new.

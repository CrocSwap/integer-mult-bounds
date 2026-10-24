# Exact optimal integer compiler separator

This scoped proof minimizes the sufficient integer rank exponent `H1` over
both the intermediate integer `H0` and the auxiliary exponent separator in
the two published compiler inequalities. A closed real stationary point
reduces the exact integer problem to two candidates. Each optimum includes
a rational separator attaining the non-strict induction bound and satisfying
the strict final bound. See [PROOF.md](PROOF.md).

For Cinna Davis's merged BIT compiler at `C=.00346`, `U=.003459`, `v=1024`
and `h=1/64`, it lowers `H1` from **25986965159937** to
**25986964913670**, a reduction of **246267**. For ai-nanachi's PR4814
parameters it lowers **262208150916063859466241** to
**262208150916063859220003**, a reduction of **246238**.

The result is optimal for the stated sufficient inequality model. It does
not establish an optimal compiler, a practical speedup, a smaller eventual
multiplication-input threshold, supplier admission or a new kappa. The
predecessor native, tail, physical, stock, precision and analytic premises
are retained. No predecessor native computation is replayed or audited.

## Reproduction and evidence

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/integer-compiler-separator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/integer-compiler-separator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/integer-compiler-separator/verify.py
```

The standalone verifier prints `PASS_INTEGER_COMPILER_SEPARATOR`, both exact
witnesses and the hashes of the package files. It uses only the standard
library, performs an independent interval-feasibility enumeration over 36
small parameter cases and rejects invalid domains, an underfunded induction,
a closed final boundary and one-below-optimum candidates. The written proof
covers all rational or real parameter values in its stated domain; the
executable corroboration has explicit input bounds. No proof-kernel or
independent human review is claimed. Hosted CI is separate from local checks.

## Sources and credit

This contribution was produced by Nick Petalas. Apache-2.0.

Cinna Davis's [query-thinned-controller proof](../query-thinned-controllers/PROOF.md),
section 3, supplies the two effective inequalities and the merged BIT
parameter example. Its compiler lineage includes Jacob Alan Sussman's
integer compiler and zxv's higher-moment strictification. These predecessor
results and all their source notices are unchanged.

ai-nanachi's [PR4814](https://github.com/CrocSwap/integer-mult-bounds/pull/4814),
head `f56ae4533a7d97d782a2c596a33fe844cd051747`, asks about reducing its
effective compiler size and supplies the second parameter example. Its
finite ordinary-backend bootstrap, native invoice, tail certificate and
claimed ordinary exponent are cited premises, not this contribution.
Its credit to rohanarun's PR185 and the PR199/204 recurrence lineage is
retained by citation. No pending code or Git object is needed for this replay.

The new step is exact separator elimination and integer optimization within
the fixed inequalities. Dugongue's [PR4479](https://github.com/CrocSwap/integer-mult-bounds/pull/4479)
and zxv's [PR4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483)
change compiler parameters or the compiler itself; their stronger reductions
for other fixed profiles are not challenged by this local theorem.

## Open next questions

Structured questions are in [TASK.json](TASK.json). The immediate follow-up is
to characterize the full interval of integer `H0` values tying the optimum
after rounding `F(H0)`. That would expose how much freedom remains for other
physical constants without changing this sufficient `H1`. A separate task is
to establish which extra separator restrictions, if any, a complete concrete
compiler interface needs before installing these witnesses. This package
does not materialize a uniform program or discharge that installation.

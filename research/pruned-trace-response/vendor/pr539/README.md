# Literal bit bad-class charge on the PR535 composition

Conditional **kappa = 0.001584931113695072**, versus PR535's **0.001584931111785787**. The absolute gain is only **0.000000000001909285**, about **0.0000001205%**. This is a small arithmetic refinement, not a new circuit or structural breakthrough.

## What changes

The bit supplier is PR510's R480 nine-stage word, unchanged. The complex supplier is PR535's rank-four construction, unchanged. Both published histograms and physical invoices remain dependencies. The only changed quantity is the conservative allowance for bad residue classes in the bit moment.

The pinned source note `inputs/three-stage-cover-bit.tex` proves, for address primes q > 2^80, a bad fraction at most 2m^3/q and a fallback cost at most

`F = 6N(N-1) + 3N + 6(N-1)`, where `N = 2m`.

At m = 64, `F = 98682` and `2m^3 / 2^80 = 1/2305843009213693952`. These are strictly smaller than the rounded `32m^2` and `10^-16` allowances still used by PR510. The same observation was applied to earlier suppliers in PR461, PR464 and PR465; those contributions retain credit.

For the unchanged bit histogram H, E = sum(H_r), live width W, and candidate exponent c, the verified upper moment is

`sum_r H_r * (r/m)^(1-c) / W + (2m^3/2^80) * F * E * m^(c-1) / W`.

Good classes are still charged at their full weight; no subtraction of bad classes or splitting of residuals is used. Each bad edge is bounded separately, as in the note. The existing fallback operation and all finite invoice allowances remain conservative because the fallback cost only decreases. The prime threshold is unchanged.

The exact bit endpoint rises from `0.001587447106092548137108` to **`0.001587447108007899663966`**. It stays below the complex endpoint `0.001589991533606044174031`, so the bit side still binds. Six bootstrap levels and the existing 47-constraint outer assembly give the displayed kappa.

## Verification

```sh
python -B verify.py /absolute/path/to/new-output
```

Python 3.11+; standard library only; assertions enabled. The output directory must be new and outside this package.

The verifier reproduces both old component endpoints and the old kappa, certifies the new bit endpoint using two independent rational moment engines, rejects the next 10^-24 bit grid point, and checks all 47 outer inequalities. It rejects the next 10^-18 kappa grid point, invalid assembly parameters, a tampered histogram, and the new bit endpoint under the old rounded allowance. Decimal arithmetic only proposes endpoints; rational intervals decide acceptance.

The packaged verifier passed on Python 3.11.15 and Python 3.14.8. All mathematical output is identical across versions; only runtime and interpreter metadata differ. Exact receipts and the tested package manifest are preserved in `evidence/`. Both rational engines, all 47 strict outer inequalities, six explicit bootstrap cutoffs and all six negative controls passed. GitHub CI is separately pending; no fresh supplier-operator replay is claimed.

## Scope

This retains PR535's conditional adoption of PR510, including the common-label/mutable-source carryover and the source theorem's portability to the compressed nine-stage cover. It does not newly prove that portability. All-size compilation, normalized wrappers, whole-call correlated-helper hosting, restored work, precision/tape and analytic transfer remain conditional. This is not an unconditional multiplication theorem, a full Lean proof, or a measured speedup.

The inherited suppliers are cited rather than rebuilt by this arithmetic-only verifier. Their source heads, original notices, source theorem and retained receipts are recorded in SOURCES.json and inputs/. The PR535 incremental local replay covered its changed complex construction; it did not rebuild PR510's bit operator.

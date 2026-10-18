# Dense rectangular batching with borrowed outputs

**Recursive-interface research construction; no new kappa.** Three immutable
sources and four outputs can be batched without a dedicated connector row.
The seed-54 fixture uses **182 primitive calls**, compared with
**302** for separate outputs and **306** for separate source batches, at the
same **two extra dirty rows**. The dedicated-connector alternative uses **122**
calls and **three** rows; it wins on work when that extra row is available.

The general batch `y_i += A_i sum_j B_j x_j` uses **4m+2k** complete queries.
[PROOF.md](PROOF.md) proves this count is sharp in the explicit output-only,
unit-query alphabet, including feedback and arbitrary noncommuting factors.
A separate complete finite classification finds **76,032** minimum twelve-query
words for two sources and two outputs, by exact projection and shuffle counting
of the entire **479,001,600-word** domain. It explicitly enumerates 40,320
single-source projections; it does not execute 479 million full words.
A second separately written interpreter also materializes every one of the
76,032 unique successful full words and checks its complete four-row map.
Both census implementations run in the default verifier.

## Reproduce

Python 3.10 or newer, standard library only, no network or Git history needed:

```sh
python3 -I -O -B research/rectangular-output-borrowing/verify.py
python3 -I -O -B research/rectangular-output-borrowing/test_package.py
```

Expected first marker:

```
PASS_RECTANGULAR_OUTPUT_BORROWING queries=20_vs_32_vs_36 leaves=182_vs_302_vs_306 dirty_rows=2 dedicated=122_leaves_3_rows minimum_2x2_words=76032 no_new_kappa
```

The second command checks relocation and deliberately corrupted packages,
and ends with `PASS_RECTANGULAR_PACKAGE`. `verify.py --write` regenerates only
this package's [exact certificate](CERTIFICATE.json). Default replay compares
all certificate fields, including every literal query and expanded primitive,
complete child boundaries, source pins, exact dense invoices and the census.
No optimizer, external solver, floating point or mutable provider is involved.

## Evidence and limits

The fixed replay domain is m=1..4, k=2..5 with the factor-length rule in the
certificate, plus the seed fixture. Every complete child and full expanded
word is checked over independent formal input symbols. An independent dense
integer implementation checks noncommuting matrices, arbitrary dirt, direct
formula agreement, inverses, scalar prefix bounds and a separately derived
head-travel invoice. The proof includes every recursive child/inverse, source
access, frame-adapter obligation, restoration, scalar cleanup, preparation,
coefficient/control storage and head return. [Validation](VALIDATION.md)
records actual executed checks and their limits.

The theorem permits only the stated query alphabet and exact additive child
contract. A nonlinear counterexample separates literal inversion from the
linearity required for the desired batch. Positive port-dependent prices can
reverse a schedule comparison; the cost theorem assumes per-operator prices.
Supplier placement, physical hosting, common-label realization, efficient
precision/tape compilation and outer analytic transfer remain open. This
package does not alter the selected frontier or prove the multiplication theorem.

Base commit: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. The selected result at
that base is reviewed PR942, conditional kappa `1661960547713947/10^18`.
[CLAIM.json](CLAIM.json) records the OS seed, three candidates and local claim;
[SOURCES.json](SOURCES.json) pins predecessor inputs. Credit Ross Richardson's
PR982 and CubeJerry's PR889 in particular. See [NOTICE.md](NOTICE.md) for
attribution, Apache-2.0 terms and substantial OpenAI Codex assistance.

# Validation receipt

Executed 2026-10-13 on macOS 27.0 arm64, CPython 3.14.4, standard library.
Exact research base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.

## Commands and actual results

```sh
python3 -I -O -B research/rectangular-output-borrowing/verify.py
python3 -I -O -B research/rectangular-output-borrowing/test_package.py
make selected-record-check
python3 -B -m unittest discover -s tests -p 'test_selected*.py'
git diff --check
```

All passed. The selected-record command reports the unchanged exact kappa
`1661960547713947/1000000000000000000`; **25 selected-result tests** pass.
The package replay works with normal and optimized Python and from a minimal
relocated directory without repository history or network. File hashes before
and after replay agree. Ten actual package corruptions fail with ValueError:
missing restore, underpriced access, changed census, changed source hash,
changed source commit metadata, changed reference bytes, omitted generated
cleanup, unpaid head return, undercounted recurrence and misrouted full-census
source. No verification check depends on Python assertions.

The fixed 16-point domain m=1..4, k=2..5 contains **1,296 complete child
boundaries** and **10,548 expanded leaf occurrences** across all four
comparators. The seed fixture is additional. Full free-module identities
preserve all arbitrary source/output/scratch input symbols and literal
inverses. Fourteen mathematical/admission controls reject or explicitly expose
the nonlinear boundary; a separate positive port-price counterexample records
the scope of the weighted theorem.

The independent dense integer oracle runs **576 grid cases plus 36 seed
cases**, each forward and inverse, in dimensions 1..3 with seeds 54,154,254,
including zero/singular/noncommuting matrices and arbitrary dirt. It checks
all scalar products/partial sums against the conservative signed width and
recomputes data-tape travel using a separate closed formula.

The independent grouped census checks every one of **40,320** single-source
projections and counts **76,032** minimum two-source words. Its separate
coverage calculation recovers all **479,001,600** candidate permutations.
A second interpreter in `full_census.py` materializes and deduplicates every
successful full word and checks all four formal output rows directly. It also
rejects three full-word defects. Both census implementations run in the default
verifier. Sorted twelve-byte query-ID words have SHA256

```
cda0204d55b197ed631cc0a8846fe3e0bbdac216cd68e7a940294df6d349e3e9
```

The complete reproducible CERTIFICATE.json SHA256 is

```
160fdb4f7be0bcc5716de8ce17acd8f9cd44426ee2cb740116732c793cf1cb7a
```

## Review corrections and scope

A separately tasked agent checked the algebra, bound, cost recurrence and
classification. A second adversarial agent found a missing binding of source
commit metadata into the receipt and an inaccurate inverse-width sentence;
both were corrected before this receipt. The source-metadata defect has an
actual package mutation control. The inverse-width proof now uses equality
of each forward/inverse leaf's source vector. The data-tape cost is explicitly
separated from a strict single-tape compiler. These are AI-assisted independent
implementations, not external human peer review.

Only the new research package is changed. `upstream/`, selected certificates,
existing suppliers, generated global artifacts and repository generators are
unchanged. The relevant selected-record checks above were run; no expensive
repository-wide `make verify`, cold selected-supplier reconstruction, hosted
CI or Lean formalization is claimed. This local recursive-interface result
neither replaces the selected construction nor changes its inherited all-size,
physical, precision/tape and analytic obligations. The written free-algebra
argument establishes the stated general query bound; finite replay is not a
formal proof of integer multiplication.

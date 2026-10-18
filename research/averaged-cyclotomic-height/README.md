# Averaged cyclotomic heights

For every prime-power radix r>=3, average the coefficient heights across
the cyclotomic embeddings before using the algebraic norm. This improves
the uniform circle-separation exponent from O(r^3) to O(r^2 log^2 r).
The same substitution improves the inherited cyclic-inverse precision
budget. No new kappa is claimed.

Let ell=ceil(log2 r), n=r-1, D=phi(r). The explicit bound is

    |P(z)| >= 2^-d,  |z|=1,
    d = 1+2ell+n D min(r,8ell^2).

It holds at every primitive embedding and every point of the unit circle.
The minimum preserves the prior bound at small radices. For example,
at r=4096 the circle exponent decreases from 34,351,349,785 to
9,661,317,145. These are conservative analytic precision bounds, not
executed word sizes or timing measurements.

With N=r^2 ell^2, input norm <=2^m and target error 2^-p, the retained
PR977 clean-scratch arbitrary-stride construction has fractional working
precision W<=p+m+60N, integer guard G<=m+26N, and factor-preparation
precision b<=p+m+34N. Its inherited record count is unchanged. The theorem
does not supply a new solver, dirty-array circuit, common-label compiler,
complete transform or multiplication exponent.

## Replay

Python 3.11 or later and the pinned SymPy dependency are sufficient:

```sh
python -m pip install -r research/averaged-cyclotomic-height/requirements.txt
python -I -O -B research/averaged-cyclotomic-height/verify.py
python -I -O -B research/averaged-cyclotomic-height/test_package.py
```

The verifier checks the source/manifest binding, 17 rational interval
cases, six independent exact resultants and 752 integer budget rows.
Two explicit mathematical controls reject a rational-resultant shortcut
and misuse of the averaged height as a pointwise estimate. The inherited
unit-root and missing-conjugation controls are also replayed. The package
harness rejects eleven packaging faults and runs a complete read-only
relocation, including the mathematical checks.

`--out /outside/package/result.json` writes a fresh external receipt after
comparison with `EXPECTED.json.gz`. Existing output files are preserved.
`--write` is an explicit authoring mode that skips the expected-receipt
comparison; it is not a verification result and is not used by CI.
No network or private workspace file is needed after installing the
declared dependency. Compressed receipt equality is defined by the full
decompressed canonical payload.

[PROOF.md](PROOF.md) contains the complete new derivation and the precise
inherited claims. [NOTICE.md](NOTICE.md) identifies contributors and
classical sources. Finite checks are supporting evidence, not a formal
verification of the full multiplication theorem.

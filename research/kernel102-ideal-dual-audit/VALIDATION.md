# Local validation

Validated on 2026-10-13 in the official Linux Python image pinned by digest:

```
python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1
```

The container had networking disabled, a read-only root and package mount,
all capabilities dropped, no-new-privileges, 512 MiB memory, one CPU, and a
16 MiB temporary filesystem. No upstream code was executed on the host.

From the package directory, all three commands passed:

```sh
python -B verify.py
python -B -m unittest -v test_verify.py
python -O -B -m unittest -v test_verify.py
```

Each unittest run passed 10 tests, including 26 negative cases: each of the
seven dual coordinates, a feasible but insufficient dual, missing coordinates,
model and endpoint changes, invalid arithmetic domains, and source corruption.
These semantic controls call the mathematical checker directly so rejection
does not merely reflect a changed file hash. Separate source controls exercise
the package boundary. Relocation to a directory without repository context
reproduced the exact result.

The output matches every field in `EXPECTED.json`: all 112 patterns pass, the
minimum slack exceeds `2/10^11`, and the ideal moment exceeds `1 + 7/10^10`.
Tests pass with Python assertions disabled because acceptance uses explicit
checks. The two input files were compared with their exact PR525 Git blobs.

This records local tests only. No GitHub CI run or cold reconstruction of
PR525's scalar/physical supplier is claimed.

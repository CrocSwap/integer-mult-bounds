# Complete replay of the retimed T488 composition

This entrypoint rebuilds the exact PR3642 retimed source and PR3633 T488 allocation, then runs the unchanged native and complete scientific admission gates. It requires Python 3.12, Git, and the inherited pipeline dependencies: `numpy`, `scipy`, `sympy`, `mpmath`, `psutil`, and `gmpy2`. It does not install dependencies or fetch Git objects.

The read-only repository must contain canonical-main commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Its current branch is irrelevant. `DEPENDENCIES.json` records the exact PR heads, original paths, SHA256 and Git blob identities of every vendored file; the unchanged upstream materializer authenticates all 540 frozen-main payloads.

From the repository root, run the complete replay with a fresh external output directory:

```sh
python3.12 -B research/retimed-t488-composition/full-replay/reproduce.py \
  --repo /path/to/repository \
  --work /path/to/fresh-external-full-replay \
  --jobs 1
```

The output must be outside this package and the read-only source repository. Its parent must already exist and be writable. For this task use the actual mounted external SSD, outside Documents, Desktop and iCloud. Do not run a second scientific replay while one is active.

Two bounded modes have deliberately distinct success statuses:

```sh
python3.12 -B research/retimed-t488-composition/full-replay/reproduce.py --check-inputs
python3.12 -B research/retimed-t488-composition/full-replay/reproduce.py \
  --repo /path/to/repository \
  --work /path/to/fresh-external-source-check \
  --materialize-only
```

Input checking authenticates 87 vendored files. Materialization recreates the 654-file retimed source and runs its existing reconstruction controls. Neither mode runs native providers, literal T488 ownership or complete controller/outer admission.

Only `PASS_T488_RETIMER_COMPLETE_CONDITIONAL_RELEASE` after the full replay certifies this finite composition. The runner regenerates 1,791,936 literal owner rows, freshly runs both changed native providers, retains every inherited scientific gate, matches the complete invoice and exact modern bound, authenticates the PR3642 comparator, and binds the final receipt to the generated package. Two unchanged predecessor native chains and their parent admission are reused explicitly through the upstream full-tree hashes; they are not described as fresh runs.

`SPEC.json` contains expected values, not evidence of a successful run. All-size dispatcher/compiler, common-label/mutable-source realization, whole-call hosting, scalar and zero-allocation contracts, uniform bounds, recursive precision, tape/recovery, bootstrap and analytic/BIT premises remain conditional. This is not an unconditional multiplication theorem or a formal proof-assistant certificate.

See `NOTICE`, `vendor/pr3642/CREDITS.md`, `vendor/pr3633/CREDITS.md`, and the retained PR3633 owner notices for source attribution. The exact dependency inventory is authoritative.

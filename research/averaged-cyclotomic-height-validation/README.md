# Frozen averaged-height validation

The complete package in `../averaged-cyclotomic-height` passed on macOS
arm64 / Python 3.11.15 and Linux aarch64 / Python 3.14.8, both with
SymPy 1.14.0 and mpmath 1.3.0. Each replay used `-I -O -B`.

Each platform ran all 17 rational interval cases, six exact resultants and
752 integer budgets three times: the ordinary verifier, the deliberately
altered-receipt rejection, and the full read-only relocation. Each package
harness rejected eleven faults. The full mathematical receipts are byte
identical after decompression, including all rational endpoints and integer
budget rows. The Linux source tree was read-only and outside Git; its
supervisor recorded exit code zero.

- Mathematical receipt SHA256:
  `b25ae109654d2e3ac16e6348c982b86d8c07fca80d8cff600205511b9d2617bf`.
- Source manifest SHA256:
  `7844dd0039723d9a955a2d0961ff1cb0f710f21277c0b2905577ad7b2b5c2f2a`.
- `SOURCE-GIT-CHECK.json` records the twelve retained files checked against
  immutable original Git objects before replay.
- `MACOS311-*` and `LINUX314-*` contain the complete math, package-control,
  platform and terminal receipts. The logs record successful completion.
- `REPOSITORY-CHECKS.log.txt` records the selected-record check and all
  25 selected-record/inventory/proof-binding tests at the publication base.

The preparation base recorded in the frozen source pins is
`8bddbee377e2f3ce1f1247196c4b290d55767d20`. The isolated publication branch
was subsequently advanced to main
`2921874911956718fcaaaf9396fe8267b3cfa9f0` without changing any frozen
package byte. Main still selects PR942 at
`1661960547713947/10^18`. This contribution does not change that selection.

The all-size claim comes from the written proof. The large-radix rows test
exact exponent arithmetic; no inverse at those enormous word sizes was
executed. The full repository suite, selected construction's cold replay
and full multiplication theorem were not verified here. No independent
human/delegated-agent review or practical speedup is claimed. Hosted CI is
separate from these retained local platform results.

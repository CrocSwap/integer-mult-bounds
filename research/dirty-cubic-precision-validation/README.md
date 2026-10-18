# Frozen two-platform validation

The complete mathematical receipt is byte-identical on macOS arm64 Python
3.11.15 and Linux aarch64 Python 3.14.8, with isolated optimized execution.
Both used source manifest
`0e8f2555997333cad4ccb3df3c815308ab7f9d762356c93295b93cef73054f11`.
Both output receipts and the package's `EXPECTED.json` have SHA256
`39901bc4654eb857f991a48eb9e5d839ff35153bbca2dd2c1e0d5ec9cef38764`.

The macOS command ran with `/tmp` as its working directory. Linux ran a
separately transferred archive, verified by SHA256 before extraction, with
all package files read-only and no repository checkout or third-party Python
dependencies. Its supervised process completed with exit code zero. Each
platform passed all eight disposable package/source-binding controls and a
read-only binding relocation. The latter integrity check is separate from
the complete mathematical replay.

[VALIDATION.json](VALIDATION.json) records environments, counts and scope.
The per-platform full results and logs are retained here. The source audit
in [SOURCE-GIT-CHECK.json](SOURCE-GIT-CHECK.json) compares all 22 retained
files directly with their pinned original Git objects. `make
selected-record-check` also passed on the unchanged base record.

The mathematical replay includes 5,220 integer budgets, 652,654 free-algebra
leaf boundaries, 11,142 dense prefix boundaries, 66 separate inverse solves,
5,104 directly reconstructed intervals, and 6,032 actual rounded leaf
boundaries across 80 kernel cases. All initial scalar words in those kernel
cases have a nonzero lowest working bit, every case has nonzero rounding
error, and every source/dirty array is restored exactly. Thirteen
mathematical controls are retained in the full results.

This is finite exact evidence supporting the written all-size proof and
inherited analytic, leaf and preparation hypotheses. It is not an
independent human review or formal verification of the full multiplication
theorem. No practical runtime improvement or new kappa is claimed. Hosted
CI is a separate publication check, not represented as passed by these
local validation records.

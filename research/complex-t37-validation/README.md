# Independent T37 construction and validation receipts

This independently developed ten-edit owner schedule reaches the same
conditional κ = **0.001661960547713947** as Jonathan Capalbo's concurrent
[PR942](https://github.com/CrocSwap/integer-mult-bounds/pull/942), now selected
on main. It does not improve the current selected value. The distinct order,
independent reconstruction and additional controls are the contribution;
see [CONCURRENT-PR942.md](CONCURRENT-PR942.md).

The strict U8/T37/PR589 replay passed under the final package name
`research/complex-t37-independent-seed39/` and manifest
`2bde79cc87f02fa6c4c11d38ae306015cd2d4f57710d15d7ee50233a51c3440f`.
A fresh complete PR589/PR741/PR799 replay took 1835.893 seconds; the T37 driver
then reused that checked ancestry explicitly and ran all 20 mandatory stages
in 613.152 seconds. The separate package audit rejected 47 mutations and
accepted two gzip recompressions. Timings describe this machine, not a
performance claim. See [ENVIRONMENT.json](ENVIRONMENT.json) and
`VALIDATION.json`. Independence refers to the owner schedule, its reconstruction
and new package/control checks; the replay also uses shared pinned inherited
verifiers and the two inherited exact moment engines.

From the repository root, using Python 3.12.14 with zlib 1.3.2, NumPy, SciPy,
SymPy, a C++17 compiler and Boost headers:

```sh
python3.12 -B research/complex-t37-independent-seed39/verify.py --work /tmp/t37-cold
```

Expected final line:
`PASS_STRICT_U8_T37_PR589_COMPOSITION 0.001661960547713947`.
The default rebuilds all ancestry. See the package README for explicit
source-bound reuse and package-control commands. Python/zlib versions matter
to an inherited bit-supplier compressed-byte comparison; the new package's
mathematical owner/plan identities accept equivalent gzip recompressions.

The final emitted invoice has prefix779 < charged1024, row17495 < 20161,
router7991 < 30000, literal35287 < 100000 and required C0 exponent200012 <
210000. Both exact moment engines and all 47 outer inequalities passed.
The retained bit/bootstrap512 and local192 allowances are unchanged.

The recorded bootstrap cutoffs also pay the stronger **1024-bit** linear
reserve used explicitly by the concurrent packages. In all fourteen native
and conservative cases, `gap <= 9/514`, so `36/gap^2 >= 2*(4+1024)/gap`.
Thus both the retained 512 formula and enlarged 1024 formula select the
same exact integer cutoff. The standalone rational checker imports no
inherited verification code and passes four negative controls:

```sh
python3 -B research/complex-t37-validation/check_bootstrap_reserve.py
```

Expected JSON status:
`PASS_FOURTEEN_UNCHANGED_BOOTSTRAP_CUTOFFS_AT_PAYLOAD1024`.
Its output is byte-identical with `python3 -O`; the receipt binds the exact
assembly and checker bytes. This checks the recorded obligations, not the
general mathematical provenance of the bootstrap coefficient.

All 18 targets in the base Makefile’s `verify` recipe completed. The prepared
environment run stopped at `verify-positive` because a historical compiler
command ignored BOOST_INCLUDE. After adding CPLUS_INCLUDE_PATH and moving
aside that failed generated directory, the final four targets passed,
including all 87 isolated test modules and patch-application checks. This
is staged complete coverage, not a claim that one uninterrupted `make verify`
command exited successfully. `VERIFY-TARGET-COVERAGE.json` and the compressed
logs preserve the exact commands, target inventory and failure distinction.
No source/checker was modified to fix these environment prerequisites.

`T37-REPLAY-SHA256.json` and `BASELINE-REPLAY-SHA256.json` bind all 165 and 484
output files respectively. Selected exact receipts are retained here; the
complete outputs are recreated by the package’s documented commands.
`VENDOR-GIT-CHECK.json` records all 47 byte-identical source files against
their pinned Git objects. Runtime adapters are reconstructed and compared
byte-for-byte with the exposed literal edits during final binding.

The submission refresh read main at
`bbc600db2fc15007b7c914f4f2b2ed55fa909c87`, whose selected certificate points
to PR942 at `1960cfa919a0945d0ca4cb14ea96237000037903`.
`SELECTED-AT-SUBMISSION.json` preserves that certificate. The 100 most recent
open PRs were checked through #961; the final 35-PR refresh reached #984 and
also found Joel Pulikkan's concurrent PR962, explicitly credited in the
comparison note. An explicit PR942 refresh confirmed it merged. These are
timestamped observations, not permanent status.
PR890 advanced from pinned `61b71bcf` to `4b3bd8cb` only to extend its CI timeout;
`PR890-HEAD-DELTA.patch` preserves the exact diff. Its construction and κ are
unchanged, so the gain **over PR890** remains
`1386533459/500000000000000000`. The gain over selected PR942 is zero.

These are finite conditional validation receipts, not an unconditional
multiplication theorem or authenticated execution history. No independent
human review or hosted CI is claimed. All inherited assumptions remain.
Prepared by Tekalign (@tekuuu) with substantial OpenAI Codex assistance.

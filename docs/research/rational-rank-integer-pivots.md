# Primitive integer pivots for rational-rank certificates

The complete rational-rank generate/save/check path is **7.38% faster** in the
local paired benchmark below: median 727.3981 ms becomes 673.6825 ms. The change
replaces only pivot discovery's per-entry `Fraction` arithmetic with primitive
integer rows. It retains the exact pivot policy and serialized certificates.
This is a measured implementation improvement, not a new rank algorithm,
supplier, exponent saving, or multiplication theorem.

## Task, sources and overlap

Started from canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. The
`replay-runtime` card was selected using the verifier-engineering expertise
override, nonce `3cf44b857eaf6b65fc973b72558b25c7`, scope key
`b1dd41940c60d240b47a`. Scope is **refined** to the shared rank-certificate
producer, with a stop rule of one measured full-path improvement preserving
all existing checks. The selected binding-only orientation passed; it is not
a scientific replay.

Ali Romman's [PR5789](https://github.com/CrocSwap/integer-mult-bounds/pull/5789)
supplies the exact rank, factorization and complete-kernel certificate interface.
Nick Petalas's [PR6272](https://github.com/CrocSwap/integer-mult-bounds/pull/6272)
already accelerates all four verification products. The present change acts on
the remaining **forward pivot elimination**, not those product checks. The
48-by-64 rank-eight benchmark fixture is reproduced from PR6272 with credit;
the two reported speedups are not added together or compared across hosts.

Before work, the live handoff thread #1166, onboarding #1163 and active
Discussions were read. Targeted all-state PR-body searches covered `rational
rank`, `certify_rational_rank`, and `rank`/`elimination`; a later open-PR search
covered `rational-rank`. No matching pivot implementation was identified.
`find_overlap.py --task replay-runtime --offline` explicitly reported incomplete
local coverage (1 of 8,917 HEAD notes) and no remote cache; the authenticated
GitHub connector and rendered Discussions supplied the bounded live checks.
Hidden discussion items, arbitrary diffs and unpublished work are not covered.
This is not a novelty certificate. No advance reservation was posted for this
short session. Main was fetched again before publication and remained unchanged.

The unchanged baseline source at the commit above has SHA-256
`c09b90259f43cab334e6e6f39b786a7960aee1935daa94a31f28d8c504bdbd0b`.
The exact parser dependency has SHA-256
`3930c22c11da7bc6042cfeb6e459ecb06e4478430037bee3469d034353855fc6`.
The benchmark receipt binds both compared sources and the harness. Frozen
predecessor packages and selected-result files are unchanged.

## Why the certificates are identical

Clear each input row's denominators, then divide a nonzero integer row by the
gcd of its entries. Each work row is a nonzero rational multiple of the
corresponding row in the original forward elimination. This also makes sense
for a zero row, which is left zero.

Suppose the pivot row and another row are `s R` and `t S`, where `s,t` are
nonzero rational numbers. Write their entries in the pivot column as `a,b`,
with `a != 0`, and let `g = gcd(a,b)`. The new integer elimination is

```text
(a/g) (t S) - (b/g) (s R)
  = (s t R[j]/g) (S - (S[j]/R[j]) R).
```

The coefficient is nonzero. Dividing the resulting nonzero row by its gcd
preserves the invariant. A zero row remains zero; when `b=0`, both algorithms
leave the row alone. All earlier pivot entries are already zero, so retaining
only the tail and restoring the zero prefix is exact. Therefore both algorithms
see the same zero pattern, take the same first available pivot in every
column, and perform the same row swaps. Negative pivots require no special
sign convention.

The original matrix is untouched. Once pivot row/column indices are known,
minor inversion, coefficient construction, both complete kernel bases,
serialization and all verification predicates are unchanged. Consequently the
complete certificate is identical for every accepted input, not merely its
rank. Exact input-byte binding and damaged-certificate rejection remain active;
there is no result cache or new invalidation rule.

The existing interface permits at most 64 denominators of at most 10^9 per
row. Thus the initial common denominator is below 2^1920. This observation
bounds initial denominator clearing only; it is not a fixed-memory or universal
runtime guarantee for intermediate elimination.

## Evidence and reproduction

On Windows 11 build 26300, CPython 3.12.10, 16 logical CPUs:

- All eight rank unit tests pass normally and with isolated optimized Python.
  The new test compares exact pivot choices and complete certificates for
  154 matrices against the original Fraction pivot policy, including zero,
  dependent, rectangular, signed, boundary-size and boundary-value cases.
  Existing independent permutation-minor checks cover all 512 binary 3-by-3
  matrices and 60 rational rectangular matrices; existing corruption and
  exact input-byte rejection controls remain.
- PR6272's unchanged conformance verifier passes normally and under `-O`:
  591 complete certificate equalities, 802 product/mutation cases and 24
  certificate rejections. These overlap some unit-test domains and are not
  claimed as a disjoint census.
- Seven alternating fresh-process timing pairs, after warming both complete
  paths, all produce byte-identical certificates. All 32 CLI commands pass,
  including warmups. Every timed bundle generates the certificate, saves it,
  then verifies it in another process. All seven after measurements are below
  their corresponding before measurements.

Raw milliseconds, in pair order:

```text
before: 663.2453 713.9549 738.2638 727.3981 875.4044 734.2279 677.4592
after:  624.3601 658.6049 673.6825 683.5187 716.0615 689.8585 639.0988
```

The [machine-readable receipt](rational-rank-integer-pivots-benchmark.json)
retains exact nanoseconds, source/fixture/output hashes and environment.
Windows stdout uses CRLF; certificate-byte hashes can differ on POSIX while
the same-host before/after comparison must remain exact. The harness accepts
either platform's success-line terminator.

From the repository root, use Python 3.12+:

```sh
python -B -W error -m unittest discover -s tests -p test_research_rational_rank.py -v
python -I -O -W error -B tests/test_research_rational_rank.py -v
python -W error -B research/integer-rank-product-checks/verify.py
python -O -W error -B research/integer-rank-product-checks/verify.py
```

To reproduce timing, save the exact original script outside the checkout and
create an empty scratch directory. This Python command preserves source bytes
on Windows and POSIX; substitute an actual external path for `/tmp/rank-before.py`:

```sh
python -c "import pathlib,subprocess; pathlib.Path('/tmp/rank-before.py').write_bytes(subprocess.check_output(['git','show','7c49fe32c55de02c2c873655c804b16e4c3fef0a:scripts/certify_rational_rank.py']))"
python -B scripts/benchmark_rational_rank.py --before /tmp/rank-before.py --scratch /tmp/rank-benchmark
```

The opt-in benchmark writes only to the supplied scratch directory. It includes
interpreter startup and file I/O; the improvement is specific to this synthetic
fixture and host. No all-input speed claim, supplier cold replay, Lean proof,
independent human review, or hosted CI success is asserted by these local checks.

## Open next questions

- Does the complete-path gain persist on a named consumer's exported matrices?
  Pin one actual input and reuse the paired harness before making a production
  throughput claim. Such a consumer workload is not supplied here.
- How do high-rank matrices with unrelated denominators affect peak memory and
  speed? First compare both exact implementations on a declared bounded family;
  the current timing receipt establishes neither a worst-case bound nor a
  fixed-capacity backend contract.

Classical denominator clearing, Gaussian elimination and primitive-row
normalization retain their usual credit. Prepared for
`josecarlosgonzalezroque-design` with substantial OpenAI Codex assistance, one
agent. Apache-2.0. Predecessor authors and their source notices are retained.

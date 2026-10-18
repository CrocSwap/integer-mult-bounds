# Exact signed modular replay for the P112 sink audit

PR1035's independent verifier computes 4,030 signed determinants with rational
Gaussian elimination while checking all 28,560 free-asymmetric-sink cases. This
package substitutes a proved-exact modulo521 kernel for those determinants and
runs the same complete audit. It preserves signs and magnitudes, not merely the
test for nonzero rank. The predecessor files and selected frontier are unchanged.

After `research/p112-signed-modular-production/`, the live
`research/p112-free-sink-audit97/independent.py` ships that modular path. This
opt-in package vendors the pairwise Fraction-only checker in `baseline.py` and
continues to prove `engine.py` against that reference.

Three paired local runs of the complete `audit()` call give median times
**0.850662 seconds reference, 0.219613 seconds candidate: 3.87x**. Those timings
include geometry, row-code coverage, minors and case checks after module/source
loading. They exclude interpreter startup, source hashing, package controls and
serialization. They describe this Windows/Python machine, not full repository
verification time or multiplication performance. Raw samples are in BENCHMARK.json.

## Exactness

Every frozen square minor has dimension at most eight. Its integer rows come
from the doubled E8 root lines and each has squared Euclidean norm at most four,
even after selecting columns. The fast kernel checks both properties on its
actual input. Hadamard's inequality gives

    |det A| <= product(row norms) <= 2^n <= 256.

The modulus521 is prime and greater than twice256. Modular Gaussian elimination
therefore determines the complete signed integer determinant uniquely: the
balanced residue in [-260,260] is the only possible answer in [-256,256]. A zero
residue implies a zero integer determinant under the checked bound. There is no
probabilistic acceptance and no assumption that a nonzero residue alone gives
the signed determinant. PROOF.md spells out the argument and domain.

Inputs outside the envelope retain the original rational implementation.
Controls include [521], which would be falsely singular under unchecked modular
recovery, larger row norms and dimensions, and an exact rational matrix. Both
Hadamard boundary determinants +256 and -256 are checked. An insufficient
modulus257 is explicitly rejected.

## Preserved obligations and verification

`verify.py` checks the exact source inventory before importing the original
independent verifier. It retains that verifier's geometry/source readers, row-code
coverage, distinct/square minor checks, signed determinant comparison, repair
inventory, all admissible witness memberships, rank upper bounds, case counts,
unused-minor rejection and free-count checks. Only its determinant function is
temporarily replaced; the original is restored even when a check fails.

Every one of the 4,030 signed determinants is compared against both the original
Fraction routine and the committed certificate. Both full audit outputs agree.
All frozen minors use the exact fast path, with zero fallbacks. An additional
complete census of all {-1,0,1} square matrices of sizes1,2,3 checks **19,767**
matrices, including singular, negative and pivot-swap cases. Nine rejection
controls include six real certificate corruptions, plus modulus/residue/bound
failures; four inputs explicitly exercise rational fallback.

The predecessor's independent implementation remains independent of its
producer's modular basis selector and Bareiss determinant. This new modular
kernel computes full determinants and uses neither producer routine. It does
share the original independent audit's geometry/source readers and all outer
checks; no implementation independence beyond that is claimed.

From the repository root, Python3.10+ standard library:

```sh
python -I -O -B research/p112-signed-modular86/verify.py
python -I -O -B research/p112-signed-modular86/test_package.py
python -I -O -B research/p112-signed-modular86/verify.py --benchmark
```

Expected first command:
`PASS_P112_SIGNED_MODULAR cases=28560 minors=4030 signed_matrices=19767 controls=9`.
Ordinary replay and timing write nothing. `--write-certificate` only writes when
the certificate does not exist. Timings are not a pass/fail correctness threshold.

## Scope and credit

Exact base `ba82555c64e1879e4b7decce28186f208fcb8262`, seed86 without reroll.
The selected-at-base construction is PR1042; the optimized audit deliberately
retains PR1035's historical PR620 input and frozen context. It proves no new
decoder exclusion, supplier saving or kappa. No native or all-size execution
is claimed. Current conditional interfaces remain unchanged.

Joel Pulikkan's PR620, building on DreamingOfClouds' PR595 geometry, supplied the
original free-sink model. PR1035 (@woklerx) replaced its floating screen with exact
certificates and an independent Fraction replay. Martinxxx9's PR976 is a related
mod101 rank-certificate acceleration for a different joint-frame auditor; it
does not recover these signed determinants. Hadamard bounds and modular Gaussian
elimination are classical. This contribution is their checked integration into
the fixed audit with preserved rejection behavior and recorded timings.
Prepared for @woklerx with substantial OpenAI Codex assistance; Apache-2.0.
Algorithmic comparisons and AI review are not independent human review.

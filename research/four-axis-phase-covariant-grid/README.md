# Sharp phase-covariant four-axis Gaussian rounding

**A sharp reversible Gaussian lattice map can acquire global phase covariance
by refining its period quotient.** This package adds that symmetry to Nick
Petalas's four-axis construction in
[#6574](https://github.com/CrocSwap/integer-mult-bounds/pull/6574), retains
its optimal Euclidean error, exact complex sum and literal inverse, and binds
the new map to the actual two-/three-call dirty-bank ports retained in Ali
Romman's [#6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509).
At exactly four axes, the retained callers use two fewer fractional bits and
two fewer signed component bits for the same stated external accuracy.

The phase-compatible period is provably minimal within the full-rank
affine-period model. The particular certified map fails exact fourth power;
that boundary is recorded explicitly. This is a scoped written proof with
exact finite certificates and caller replays. It supplies no new kappa and
discharges none of the selected multiplication result's five assumptions.

## Results

Write $W_{rs}=(-1)^{\operatorname{popcount}(r\mathbin\&s)}$,
$D_{jj}=(-i)^{\operatorname{popcount}(j)}$, and $U=-DWD/4$.
This is the retained native four-axis Gaussian operator on sixteen entries.
The package constructs a bijection $F:\mathbb Z[i]^{16}\to\mathbb Z[i]^{16}$
with a literal inverse and the following guarantees.

| Property | Result |
|---|---|
| Global Gaussian phase | $F(ix)=iF(x)$, and the inverse has the same covariance |
| Conserved quantity | The complex sum is preserved exactly; zero is fixed |
| Uniform Euclidean error | $\sqrt8\,h$ for both the forward and adjoint ideal operator, sharp among all grid-output rules |
| Coordinate error | At most $3\sqrt2\,h/4$ forward and $5\sqrt2\,h/4$ inverse |
| Real correction quotient | 2,048 classes, with 32 negation-fixed classes and 1,008 free pairs |
| Minimum real affine-period index | 2,048 for any odd map with ideal linear part $W/4$ |
| Minimum native affine-period index | 4,194,304, including coupled real/imaginary maps; attained by the componentwise construction |
| Exact fourth power | Fails for this certificate; an explicit $F^4(e_0)\ne e_0$ witness is retained |

The period lower bounds count cosets, not unavoidable table bytes or physical
operations. The native map reuses the same real correction tables for both
components. No 4,194,304-row native table is stored. A nonperiodic architecture
is outside the lower-bound theorem.

The predecessor uses 64 real quotient classes. The refined construction uses
32 times as many; the lower bound proves that this increase is necessary for
oddness within the affine-period model. Its benefit is a stronger symmetry
contract at the same sharp error. The larger classification and lookup remain
part of the implementation cost.

The mechanism is an odd real map $R(z)=(Wz+e(\alpha(z)))/4$, where
$\alpha$ takes values in $\mathbb Z/8\oplus(\mathbb Z/4)^4$.
The output uses a different quotient $\beta$. A finite matching assigns
opposite offsets to opposite classes; a class bijection plus its exact period
map proves the all-integer bijection. Then $F=-D R_{\mathbb C}D$, with
the same $R$ on real and imaginary parts. The complete argument, compact
classifiers, minimal-period theorem and sharpness witness are in
[PROOF.md](PROOF.md).

## Actual retained caller benefit

[CALLER.md](CALLER.md) binds the map to the unchanged two-/three-call port
bodies from #6509, at $f=4$, $N=8^4=4096$, and native axes zero and
two. Each call partitions the field into 256 sixteen-point spectator fibers.
Literal reverse execution restores both stored dirty banks for arbitrary values
within the stated no-overflow domain, in either composition order. The proof uses
the true inverse of each rounded block;
it does not require the failed fourth-power identity.

Because both coordinate constants are less than 2, a completed call requesting
tolerance $2^{-q}$ can use $g=q+1$, replacing the predecessor's
$g=q+3$ at four axes. The retained source-ordered external requests stay
unchanged:

| Port direction | Call request $q$ | New grid exponent $g$ | Prior $g$ |
|---|---|---|---|
| Two calls forward | $P+7$ | $P+8$ | $P+10$ |
| Three calls forward | $P+9$ | $P+10$ | $P+12$ |
| Two calls reverse | $P+4$ | $P+5$ | $P+7$ |
| Three calls reverse | $P+6$ | $P+7$ | $P+9$ |

For original coordinate magnitude at most $2^H$, the retained width formula
is $w=H+g+19$, so the width also falls by two. The new largest raw
numerator is bounded by $16M+5$ for input components of magnitude at most
$M$, within that width margin. Initial quantization remains separately
charged. The full field Euclidean error is $h\sqrt{N/2}$, compared with
the predecessor's four-layer triangle bound $4h\sqrt{N/2}$.

The fast reference block uses 160 full-word additions/subtractions and 32 exact
quarter shifts. Classification, table access, signs, reads, writes, range checks,
and scratch/control cleanup are additional payable work; [CALLER.md](CALLER.md)
states the direct implementation bound and retained monomial/mix costs. No
accelerated recursive tariff, physical tape schedule, supplier admission or
complete multiplication improvement follows from saving two retained bits.

## Evidence and reproduction

The package uses CPython 3.12 and its standard library. From the repository root:

```sh
python3.12 -W error -B research/four-axis-phase-covariant-grid/verify.py
python3.12 -O -W error -B research/four-axis-phase-covariant-grid/verify.py
python3.12 -W error -B research/four-axis-phase-covariant-grid/verify_caller.py
python3.12 -O -W error -B research/four-axis-phase-covariant-grid/verify_caller.py
python3.12 -B scripts/research_package.py --package research/four-axis-phase-covariant-grid --check-only
python3.12 -B scripts/research_package.py --package research/four-axis-phase-covariant-grid
python3.12 -B scripts/check_research_commit.py --package research/four-axis-phase-covariant-grid --check-modes
python3.12 -B scripts/check_research_commit.py --package research/four-axis-phase-covariant-grid --check-source-history
```

The package runner registers ordinary and optimization-mode checks for both
verifiers. Its fresh bytecode namespace binds imports to the current source
files. The final source-history command requires the package to be committed.
All verifiers write only stdout and do not regenerate shared files.

Executed with CPython 3.12.14: both verifiers passed in normal and optimization
modes, the registered package replay and metadata/pin checks passed, and the
committed-byte/mode preflight passed. The source-history preflight was attempted
but refused to run because the supplied repository is shallow; it requires full
Git history. That unavailable gate is not reported as a pass. The source-pinned
retained port has an original trailing blank line; its exact bytes are preserved.

`verify.py` reconstructs the period matrices with rational arithmetic and
classifies cosets using their inverse matrices, independently of the production
compact quotient formulas. It checks all 2,048 source classes and all 2,048
target classes, all matching rows, the literal inverse, both coordinate maxima,
weighted sums and sharp energy. A direct native coefficient oracle checks
4,096 paired complex fixtures, sharp forward/inverse witnesses, and eight
signed/large-word fixtures, with components through 4,090 bits. Eleven failure
controls include a locally admissible but colliding matching, broken negation,
a corrupted period, wrong phase, wrong inverse and a false smaller radius.
The core replay emits a receipt with exact file hashes and the fourth-power
counterexample. The all-input theorem follows from the coset and componentwise
proof; no claim is made to enumerate all $2048^2$ complex class pairs.

`verify_caller.py` checks fast/dense block equality on 4,096 quotient fixtures,
16 port-direction cases over four dirty-bank families, 40 actual paid input
cuts, both exact composition orders, phase covariance, every spectator-fiber
sum and the full transform/correction arithmetic counts. Four additional
boundary-grid cases exercise the reduced precision and word width. Five
failure controls cover aliasing, unsupported size, overflow, forward-as-inverse
substitution and a wrong native axis that fails the operator error bound.

The mathematical formulas apply to all integers. The public dense reference
kernel rejects components above 4,096 bits; this executable guard is separate
from the proof. The finite-word caller checks its own stated signed width.
Neither checker uses floating point, a numerical tolerance or Python `assert`
for a proof-relevant predicate.

## Sources, scope and attribution

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected #6030. [TASK.json](TASK.json) preserves the full original
`uniform-transfer-audit` card and records the changed scope: one pending native
precision interface, not a discharge of an all-size inherited assumption.
The original metadata baseline was blocked by sparse omitted inputs; this
package does not claim that baseline or the selected multiplier replay passed.

Nick Petalas's #6574 is pinned at
`48e312ff18d5b66b0969148f615fdf5ce0f92edd`. Its sharp four-axis error,
native factorization, correction predicates and half-grid lower bound are
predecessor results. The new contribution is the compatible period/matching,
phase covariance, minimal-period proof, compact quotient and retained caller
precision binding. Ali Romman's #6509 is pinned at
`a4173e810c4d34a1d13b9745af123ad0ec6cfed5`; the exact retained caller files
are vendored with SHA256 and Git-blob checks before import. Brian / JoyboyBrian's
#5485 and the #4743 channel lineage supply the retained rounded port context.
Further native lineage credit is retained in [NOTICE.md](NOTICE.md).

[SOURCES.json](SOURCES.json) pins the historical task/selected provenance through
Git and separately records the external source heads and inspected file bytes.
[CALLER-SOURCES.json](CALLER-SOURCES.json) authenticates the two local retained
caller files. Pending predecessor commits need not be present in a clean
checkout: their external publication ancestry is recorded, not proved by the
repository's source-history checker. No live predecessor file or network service
is needed for replay. Package-local files trigger replay automatically, so
there are no undeclared external runtime inputs.

The concurrent review in #6755 (ToikY,
`4475dc90bbe6037981bfc8ce0dd55efb6bdbc6a0`) identified phase covariance,
fourth power and actual caller/rounding costs as open scope. It is credited as
review context, not a mathematical dependency or endorsement of this package.
No norm-inward condition, pointwise nearest-output property, native graph
flatness, formal proof review or physical compiler lowering is claimed.

## Open next questions

1. **Can sharp phase covariance coexist with exact fourth power?** The displayed
   certificate fails on $e_0$. A next experiment should impose the four-step
   orbit relation on a precisely declared quotient or additional state, then
   recheck the sharp error, sum and literal inverse together. Negation matching
   alone supplies no such relation; no general obstruction has been proved.
2. **Does the two-bit precision gain survive a complete physical bill?** Lower
   the fast transforms, residue classifiers and shared lookup into one declared
   reversible Boolean/tape implementation, including routing, scratch return,
   source traffic and compiler stock, before comparing its complete paid profile
   with a current supplier. The local state count and arithmetic savings do not
   price those operations or establish an all-size port implementation.

The structured questions and blockers are in [TASK.json](TASK.json). New work
was prepared by @CubeJerry with substantial OpenAI Codex assistance, including
parallel period/matching, compact-quotient proof/checker and caller-integration
work. All new work is Apache-2.0; retained files preserve their original notices.

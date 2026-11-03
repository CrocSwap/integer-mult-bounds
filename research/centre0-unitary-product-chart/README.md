# A unitary centre0 product chart, with a different output contract

For the exact rational centre0 pair G,G^T cited by PR6667/5130, the written
construction gives unitary complex maps S,C with

```text
(S A S^-1 x)(S B S^-1 z) = C(xz),
A=G direct-sum I, B=G^T direct-sum I,
```

for every N>=112 and every x,z in C[y]/(y^N+1). The output C is freely
chosen. If the additional fixed-output requirement C=S B S^-1 is imposed,
then cond_2(S)>=r is sharp, ||C||_2=||C^-1||_2=lambda and
cond_2(C)=lambda^2, where lambda=937+12sqrt(6097) and
r=sqrt(lambda)=sqrt(469)+6sqrt(13). These distinct contracts are explicit
in [PROOF.md](PROOF.md). The conjugated native endpoints still have norm r;
unitary surrounding charts do not remove intrinsic bilinear amplification.

The addition to Nick Petalas's [PR6667](https://github.com/CrocSwap/integer-mult-bounds/pull/6667)
is positive Gram normalization of its actual seven-plane construction,
the changed unitary output and the sharp fixed-output boundary. It uses
additional algebraic square roots; it does not retain the predecessor's
smaller coefficient field or yield a Gaussian-rational/dyadic implementation.
JoyboyBrian's [PR5130](https://github.com/CrocSwap/integer-mult-bounds/pull/5130)
allows an arbitrary invertible output. Classical normalization, product
isotopy and Fourier unitarity are not claimed as new methods.

## Exact evidence and reproduction

[VALIDATION.md](VALIDATION.md) separates the written all-size argument,
bounded source/Gram/action/product checks and failure controls. All runtime
sources are five verbatim, inert data/proof objects under inputs/, pinned
by [SOURCE-PINS.json](SOURCE-PINS.json). No predecessor program is run.
The primary and separate blind-first oracle use only CPython 3.12 standard
library. From the repository root, replace python3.12 by a suitable path:

```sh
python3.12 -I -W error -B research/centre0-unitary-product-chart/verify.py
python3.12 -I -W error -B -O research/centre0-unitary-product-chart/verify.py
python3.12 -I -W error -B research/centre0-unitary-product-chart/oracle.py
python3.12 -I -W error -B -O research/centre0-unitary-product-chart/oracle.py
python3.12 -B scripts/research_package.py --package research/centre0-unitary-product-chart
python3.12 -B scripts/check_research_commit.py --package research/centre0-unitary-product-chart --check-source-history --check-modes
```

Default commands recompute and strictly compare retained receipts, with
explicit exceptions active under optimization. VERIFY.json registers four
240-second commands. No dependency, network, subprocess or source-code
import is needed by the scientific checkers. Their optional emit flags write
to stdout; acceptance commands do not change package files. Temporary source
corruption controls use disposable directories outside the frozen package.

## Scope and coordination

Canonical main is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision8,
selected PR6030. The selected binding-only orientation passed; it is not a
selected scientific replay. The formal-interface-lemma card changes scope to
this written algebraic interface lemma, without Lean or assumption closure.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19380869)
preceded scientific execution. Intake covered 626 distinct open PR bodies,
four targeted all-state searches, source timelines and the rendered Hub.
Coverage is non-atomic and excludes arbitrary diffs, all closed work, hidden
work and every Discussion reply. A match-free search is not novelty proof.

The output must be accepted or converted by an actual consumer with all
coefficient delivery, access and restoration paid. Endpoint unitarity alone
supplies no rounded intermediate-error bound or finite-grid invoice. Native
producer/normalizers, independent targets, ownership, precision, stock,
storage, compiler and recursive/outer admission remain open. All five
selected assumptions retain their status. No supplier admission, new kappa,
frontier change, full multiplication theorem or physical speedup is claimed.

Prepared by ToikY with substantial OpenAI Codex assistance, separate AI
implementations and static review. Independent human and proof-kernel
acceptance are unclaimed. [NOTICE](NOTICE) retains exact predecessor credit.
TASK.json records the remaining focused questions and blockers.

## Open next questions

1. Can an actual source-compatible consumer accept the changed unitary
   output, or pay its conversion? First pin that consumer and charge all
   coefficients, access, restoration, precision and independent targets.
   An actual caller and complete physical invoice are missing.
2. Can a literal unitary factorization retain a rounded intermediate-error
   budget? First fix one Givens/Householder/FFT implementation with owned
   lifetimes and finite-grid costs. The added algebraic radicals and every
   interior primitive remain unpriced; endpoint norms alone do not suffice.

## Verifier constraints

All functions are below sixty lines. Fixed source dimension112 and product
fixtures N<=256 bound every matrix and loop; no prime or domain is expanded
post-execution. Managed Python integers, Fractions and containers allocate
at runtime (Power of Ten rule3 deviation). Strict receipt comparison recurses
through bounded JSON trees (rule1 deviation); source files are size/hash-bound.
The checkers do not import one another. Literal local control callables and
Python dispatch are rule8/9 deviations; there is no generated code or remote
call target. Warning-strict normal/optimized execution replaces a C compiler
warning mode. Child RSS/timing are local observations, not a paid runtime bill.

Related conditioning work by Nick Petalas in unitary-cycle-optimal-conditioning
and sharp-rank-conditioning concerns observation cycles and signed-rank prefix
transport, respectively. Those quantities differ from this common-product
output contract; no values or predecessor suites are reused here.

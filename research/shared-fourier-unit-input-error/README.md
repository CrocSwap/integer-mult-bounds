# Sharp shared Fourier error on arbitrary unit inputs

This scoped written proof with exact finite corroboration was produced by
Nick Petalas. Apache-2.0. It answers Open next question 2 of
[PR #6307](https://github.com/CrocSwap/integer-mult-bounds/pull/6307).

For every finite product of cyclic groups and every nonzero order-two
translation, the shared phase-weighted three-pass Fourier routine has

    min relative induced bilinear l2 error = sqrt(2 - 8/(3 sqrt(3))).

The inputs range over all pairs of complex unit-l2 vectors. Both Fourier
signs use 1/N, the desired output is convolution divided by N², and its
induced bilinear norm is N^(-3/2). Relative error divides the absolute
operator error by this norm, rather than by each input pair's output norm.
The latter can be zero.

The new exact formula for any unit phase function w is

    c(x)=chi(b,x),                 m=average_x c(x)w(x),
    D(w)²=max_y {2-2 Re[conj(m)c(y)w(y)²]}.

Equal normalized character inputs attain every column in this maximum.
The inherited choice `w=1/sqrt(3)-i sqrt(2/3)c` makes all columns equal
and attains the stated optimum. [PROOF.md](PROOF.md) retains every Fourier
normalization and proves the arbitrary-input upper bound. It cites #6307's
coefficient-error lower bound and scalar inequality as premises. Their proof,
phase choice and earlier basis-input result are predecessor work.

## Evidence

The standard-library verifier implements the three literal Fourier passes
and direct group-addition convolution in exact Q(sqrt(2),sqrt(3),i).
It does not import or run a predecessor module.

- All fourth-root phase assignments on Z/2, Z/4 and (Z/2)^2, at every
  nonzero order-two translation, give 1,040 assignments. Each transformed
  character input is checked directly against the new column formula.
- Eighteen minimizing fixtures on six group shapes of size 2 through 16
  check column flatness and attainment. Together with the phase census,
  this gives 1,058 assignments and 4,274 equal-character input pairs.
- Another 72 pairs use distinct characters and real or complex unit
  superpositions. Their literal errors obey the new sharp upper bound.
- Ten controls cover omitted final conjugation, omitted final translation,
  missing normalization, maximum versus mean, and six malformed domains
  rejected for the exact expected reasons. In the maximum-versus-mean
  fixture, squared coefficient error is 7/4 while squared unit-input error
  is 5/2. Thus averaging columns would miss the new norm.

Every count is enumerated. The universal result is the written proof;
these finite checks corroborate its reduction and upper bound. Each run
prints a generated JSON receipt binding all six package files by SHA256.
Ordinary verification writes nothing. No hand-written receipt is retained.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/shared-fourier-unit-input-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/shared-fourier-unit-input-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-fourier-unit-input-error
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-fourier-unit-input-error --check-source-history --check-modes
```

Another CPython 3.12 path may replace the displayed local interpreter.
Expected markers are `PASS_SHARED_FOURIER_UNIT_INPUT_ERROR`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Both registered checks have a 120-second timeout. Explicit guards remain
active under optimized Python. The direct verifier needs only these six
files and also works without Git; source-history checking needs full history.

## Scope, sources and credit

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8. The selected source-binding orientation passed for #7000,
conditional kappa .00363005817. The catalogue still describes the older
#5599 assessment; it does not establish the current selected value.
The joint-query-controller card is explicitly changed to this analytic
side result in [TASK.json](TASK.json). It supplies an approximation boundary,
not a changed physical caller or a favorable complete recursive invoice.

[SOURCES.json](SOURCES.json) pins the card, selected record and predecessor
proof text as historical provenance. No predecessor bytes are runtime inputs.
Credit Nick Petalas #6307 for the question, scalar moment inequality,
coefficient lower bound and minimizing phases; Hanson Sun / bbMisk #1477
for the weighted-layout contract, extending Ross Richardson #940.
Character orthogonality, Cauchy-Schwarz, the triangle inequality and elementary
induced-norm arguments retain their classical status. The contribution is
the exact unit-input formula, explicit extremizers and sharp extension.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19592047).
Live PRs, recent account work, active Discussions, reservations, main-tree
README terms and distinctive merged searches were checked. The overlap
snapshot covers 810 open PRs and 7,416 Discussion records with complete
remote pagination. Its sparse local-note search covers 215 of 10,178 notes.
This does not establish absence of unpublished or differently worded work.

Only the stated shared routine, complex l2 input norm and nonzero order-two
translation are covered. Other translations, physical phase preparation,
rounded arithmetic, routing, dirty restoration, storage, compiler closure,
analytic recovery and a complete supplier bill remain unsettled. The five
selected framework assumptions retain their status. No new kappa, supplier
admission, selected-frontier change or complete multiplication theorem is
claimed. Selected cold replay, predecessor scientific suites, Lean, Docker
and a literal physical caller were unrun. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

- Determine the sharp unit-input error at a translation of order three.
  Begin with its column formula. A matching nonbinary phase inequality and
  attaining construction are missing.
- Price an actual rounded caller using approximations to the attaining
  phases. Begin with its grid and norm contract; charge coefficient
  preparation, routing, restoration and the complete recursive invoice.

Structured relevance, first steps and blockers are in TASK.json. No further
question is reserved by this package.

## Verifier constraints

There is no recursion, subprocess, network, dynamic code execution, callback
dispatch or file-writing path. Functions are below sixty physical lines.
Group dimension is at most four, group size at most sixteen, field dimension
eight, and the largest phase loop has 4^4 assignments. Each literal Fourier
pass has at most 16² terms and each convolution at most 16² pairs. Comparisons
use at most four exact integer-square-root enclosures, through 256 bits, and
fail if they cannot separate a nonzero value. Six package reads are each
capped at 256 KiB plus one guard byte. Syntax inspection and warning-strict
normal/optimized execution provide the available Python diagnostics.

Power of Ten rule 3 deviation: CPython and Fraction allocate managed objects.
This fixed, one-shot census streams assignments, holds vectors of at most
sixteen eight-component field values and no result cache, and reads package
files one at a time under the stated cap. Dynamic allocation cannot be
disabled in this runtime. The finite domain, capacity rejection and both
registered runs are the compensating controls. A fixed-allocation native
implementation would need its own storage contract before integration.

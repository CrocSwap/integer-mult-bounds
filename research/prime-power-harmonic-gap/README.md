# A smaller prime-power cyclotomic gap exponent

This scoped analytic proof was produced by Nick Petalas. A new primitive-unit
harmonic estimate improves the averaged-height step of Chafik Boukhalfa's
[#1025](https://github.com/CrocSwap/integer-mult-bounds/pull/1025).
With the older zero-mean Fourier identity of
[#5930](https://github.com/CrocSwap/integer-mult-bounds/pull/5930) as a cited
premise, it gives, for every prime-power radix r >= 3,

```text
sum_{k unit mod r} log H_k <= phi(r) [(log r)^2 + 3 log r].
```

The cited previous bound is phi(r)[2(log r)^2+3 log r]. Here H_k is
#1025's coefficient height at primitive embedding k, and log is natural.
The improvement comes from retaining the p-divisible harmonic subtraction
when averaging geometric sums over units of a prime power q. The new envelope
is log q + 2, replacing 2(1+log r).

Write ell = ceil(log2 r), n = r-1, D = phi(r), and
B_ell = ceil(3ell^2/4 + 3ell). The cited norm/cofactor implication then gives

```text
|P_k(z)| >= 2^(-d_new) for every primitive k and |z| = 1,
d_new = 1+2ell+nD min(r, B_ell).
```

At r = 4096 this sufficient gap exponent is **1,207,664,665**, compared
with the cited #5930 exponent **3,622,993,945**. These are analytic bound
values. No inverse at this precision was executed, and no kappa or selected
frontier is changed. [PROOF.md](PROOF.md) gives the argument and its premises.

## Evidence and reproduction

The new finite checks pass with CPython 3.12.15 and its standard library:

- 604 exact primitive harmonic bounds, covering every prime power from
  2 through 4096, with 117 independently enumerated harmonic identities
  through 512.
- 44 rationally enclosed primitive cosecant averages through 128,
  with 1,083 pairing classes covering 2,165 primitive residues. The midpoint
  at q = 2 is handled separately.
- 968 exact exponent cases, including all preceding prime powers r >= 3,
  dyadic exponents 2 through 256 and ternary exponents 1 through 128.
  There are 948 strict improvements over the cited formula.
- 13 controls: eleven invalid-input rejections and two mathematical controls.
  Dropping the divisible harmonic terms breaks the new estimate at q = 64;
  a floor in place of the dyadic ceiling undercharges at ell = 3.

The universal claim is the written proof, supported by these finite checks.
No predecessor scientific executable is imported or replayed. Source proofs
and the assignment context are bibliographic provenance in
[SOURCES.json](SOURCES.json), rather than runtime inputs.

Run from the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/prime-power-harmonic-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/prime-power-harmonic-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/prime-power-harmonic-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/prime-power-harmonic-gap --check-source-history
```

Other machines may substitute a CPython 3.12 path. The expected marker is
`PASS_PRIME_POWER_HARMONIC_GAP`, followed by a generated JSON receipt binding
all six package files by SHA256. The scripts write no files, need no Git or
network, and use explicit checks that remain active under optimization.
The registered commands run the normal and optimized verifier separately.

## Scope and credit

Base main is `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.
The `formal-interface-lemma` card has changed scope to a mathematical
precision lemma. This is a side result, with no formalization or actual
selected-caller binding. The first source-binding orientation command passed;
its selected #7000 result and all five assumptions are unchanged.

The question source is #1025's prime-power averaging step. The older #5930
Fourier identity is a premise, rather than a recheck or a question taken from
its Open next questions. Concurrent
[#7195](https://github.com/CrocSwap/integer-mult-bounds/pull/7195) substitutes
that identity into an existing general-radix envelope. This package proves a
new primitive-unit envelope within prime powers. Its main scientific step is
different. Its displayed composite example is outside this package's domain;
no additional calculation checked its numbers. Live searches and sparse local overlap coverage are recorded in
[TASK.json](TASK.json); neither search absence nor an advisory claim proves
novelty against unpublished work.

Credit Chafik Boukhalfa / chafreaky #1025 for the averaged-height framework,
normalization and embedding-specific norm estimate; Nick Petalas #5930 for
the zero-mean Fourier identity; Ali Romman #621 for prime-power resultant
nonvanishing and the cofactor argument; and Rohan Guliani #846, Chafik
Boukhalfa #862/#977 and Charles Bethin #764 for the retained inverse and
suffix lineage. Harmonic integral bounds, finite Fourier inversion, the sine
chord, Machin's formula and alternating Taylor series are classical.
No literature-priority claim is made for those methods. Existing predecessor
files and notices are unchanged. New material is Apache-2.0.

Prime-power nonvanishing, the Fourier identity and the norm implication remain
cited premises. Composite radices, optimal constants, actual inverse execution,
coefficient preparation, rounding, dirty restoration, physical tapes, hosting,
complete paid costs and supplier admission are not established here. No Lean,
Docker or selected scientific replay was run. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

- Can log q + 2 be replaced by a smaller explicit primitive-unit envelope?
  Start with the exact subtracted harmonic expression or a sharper sine bound
  for one prime-power family. This may improve the sufficient exponent further;
  no mathematical blocker is identified. It was not pursued after the first gain.
- Can one actual small prime-power inverse use the improved gap with its full
  error and cost recurrence? Start with a fixed instance of the cited
  arbitrary-stride solver and charge coefficient preparation, rounding,
  restoration and tape access. The missing physical implementation and full
  error ledger block any executed-precision or supplier claim.

Structured entries are in [TASK.json](TASK.json).

## Verifier constraints

All functions are below 60 physical lines. There is no recursion, subprocess,
network access or dynamic code evaluation. The finite radix loop has 4,095
iterations, harmonic storage has 2,049 entries, logarithm series use 32 terms,
and factor-removal loops have at most 257 iterations. Mathematical comparisons
use integers and Fractions. Package reads are limited to one MiB per file.
Both registered modes enable warning errors and explicit invariant checks.

Power-of-ten rule 3 deviation: CPython allocates managed integers, Fractions
and bounded containers while checking. This one-shot checker has no fixed
allocation runtime; the enforced finite domains bound live data. Rule 9
deviation: the rejection table invokes only its named local functions on
eleven fixed fixtures. There is no external callback or plugin dispatch.

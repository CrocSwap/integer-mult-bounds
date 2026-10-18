# Checked cpp_int stand-in for bit589's native step

**Portability tooling; no new κ.** Seed 92 (verification engineering), card
`portable-replay`, refined scope recorded in [TASK.json](TASK.json). Base
`bce54fb3`. Nothing pinned, selected or under `upstream/` is changed.

## Problem

The selected record's `make frontier1094-verify` reaches bit589 through
`scripts/verify_frontier741.py`, which runs
`research/e8-bit-p111-tuned/tune/verify.sh`. Its non-standard requirements
split two ways:

- `numpy`, `sympy` and `scipy` (`../requirements.txt`) install with pip.
- Boost headers are a system package. Step 4 compiles the three official
  cohort checkers `legality_h.cpp`, `columns_h.cpp` and `columns_k.cpp` in
  `research/e8-bit-carrier-skeleton/code/bit/checkers/`. These are the only
  native code in the selected chain, and their only Boost use is
  `boost::multiprecision::cpp_int`.

On a host without Boost, step 4 stops with
`fatal error: 'boost/multiprecision/cpp_int.hpp' file not found`, so the
selected reproduce command cannot complete. `verify.sh` already reads
`BOOST_INCLUDE`, and `verify_frontier1094.py`, `1042`, `799` and `741` pass
the environment through unchanged.

## The stand-in

[include/boost/multiprecision/cpp_int.hpp](include/boost/multiprecision/cpp_int.hpp)
is about 100 lines of standard C++17 plus the GCC/Clang `__int128` type.

- **Opt in** for the whole selected chain:
  `BOOST_INCLUDE=$PWD/research/bit589-checked-cpp-int-seed92/include make frontier1094-verify`.
  Real Boost stays the default and the reference.
- **API covered:** exactly the subset the three checkers use. That is
  construction from built-in integers, `+ - *`, compound assignment,
  non-negative left shift, unary minus, the six comparisons, explicit `bool`,
  `str()`, `convert_to<std::string>()`, default-format decimal stream output
  and `msb()`.
- **Anything else fails to compile.** That includes division, `gcd`, other
  conversions and floating constructors.
- **Exact or refuse.** Every arithmetic operation is overflow-checked with
  `__builtin_{add,sub,mul}_overflow`. Shift counts are checked in their own
  type before any narrowing, so negative or huge counts are refused. A zero
  value shifts to zero, as in Boost, and a negative value is refused. A value
  outside [−2¹²⁷, 2¹²⁷) aborts with
  `checked cpp_int stand-in: 128-bit range exceeded`. Nothing ever wraps.
  Streaming with `hex`, `oct` or `showpos` is refused rather than printed in
  decimal.

So a checker run that completes has computed the same integers Boost's
unbounded `cpp_int` would. Each implemented operation is ordinary integer
arithmetic on in-range values, and every out-of-range intermediate is a
refusal, never a different value. On a passing run, the checkers themselves
assert `payload < 2^104`. The payload is a product of factors ≥ 1, so every
intermediate is below 2¹⁰⁴. The selected receipts therefore stay well inside
the stand-in's range.

## Verification

```sh
python3 scripts/research_package.py --package research/bit589-checked-cpp-int-seed92 --check-only
python3.12 scripts/research_package.py --package research/bit589-checked-cpp-int-seed92
```

`verify.py` uses only the standard library plus `bash` and a C++17 compiler
(`CXX`, default `c++`). GitHub Ubuntu runners ship both.

**Registration note.** The package compiles C++ inside the generic package
hook, although the
[package guide](../../docs/research/research-package-guide.md) routes native
builds to a dedicated workflow. That is a deliberate departure, for three
reasons:

- the native build is the subject of the check;
- it uses only the runner's preinstalled `g++` and `bash`, and installs no apt
  or pip package and no Boost;
- it takes about 7 s, far inside the hook's limits.

Maintainers who prefer the rule can move the command into its own workflow,
like `e8-bit-p111-tuned.yml`, and keep `VERIFY.json` for metadata.

It checks the following:

1. **Pins and include order.** Every declared input matches its pin. The 25
   inputs include the nine parent files `adapt.py` edits by exact anchors, the
   `relax.py` it copies, and the `prime_witnesses.py` that `gram_frames.py`
   loads. With
   `verify.sh`'s own `-I` order, a probe compiles only if the stand-in is the
   `cpp_int` header actually used.
2. **The real step 4, verbatim.** It extracts three parts of the pinned
   `verify.sh`: the preamble, the step-3 `adapt.py` command that step 4's
   mutation suite needs, and the whole step-4 block. The composed text is
   pinned in [EXPECTED.json](EXPECTED.json), and it runs under `bash` with
   `BOOST_INCLUDE` at the stand-in. Every original step-4 assertion therefore
   runs unchanged:
   - six binaries are built with the original flags;
   - legality, the five-, nine- and eleven-stage formal columns, the
     omitted-bridge controls, the KPAIRS = 2 regression, both mutation suites
     and the Gram witnesses all pass.
3. **Equality with the Boost-built receipts.**
   - The 10 step-4 output lines equal the step-4 section of the committed
     `research/community-frontier741-audit/bit589.log`, timing removed. Those
     lines include record and ADD counts, rank mass, column counts, bridge
     additions, payload bits, and the 6/6 and 3/3 negative controls.
   - `columns_k4.json` equals the committed Boost receipt
     `research/community-frontier741-audit/bit/cout/columns_k4.json` field for
     field, except `seconds` and the `local_scalar_stream` path. It includes
     the exact payload bound `9528119495320518471870892800`.
4. **Rejections come from the checkers.** Both mutation suites are rerun with
   full output. No rejection may come from the stand-in.
5. **Over-range control.** All 24,305 ADD coefficients of the record stream
   are set to ±2³⁰. The five-stage checker must then refuse with the
   stand-in's message instead of wrapping.
6. **Differential test.** A seeded test runs 100,000 operations against
   Python integers, plus fixed rows. The fixed rows cover:
   - values at −2¹²⁷ and 2¹²⁷ − 1;
   - shifts ending exactly at or just below 2¹²⁷;
   - zero shifted far;
   - multiples of 2⁶⁴ with a zero low word;
   - comparisons that share a high word.

   62,870 in-range results must be equal. 558 refusals are required: every one
   of the 244 whose exact result lies within a factor of 2 of the bound, plus a
   per-operation sample covering each refusal path:
   - multiply, and scaled add/subtract/negate at ±2¹²⁷;
   - left shift, by `<<` and `<<=`;
   - 64-bit and negative shift counts;
   - `msb(≤ 0)`;
   - non-decimal stream flags.

   These coverage counts are pinned in `EXPECTED.json`.

With `--boost-include DIR`, step 4 also runs against real Boost and every
receipt must match the stand-in's. I could not run that mode here, because this
host has no Boost.

**Results.** `PASS_BIT589_STEP4_CHECKED_CPP_INT_STANDIN` in about 7 s with:

- Apple clang 21 and Python 3.12.15;
- Homebrew GCC 16.2 and Python 3.14.8;
- clang with `-fsanitize=undefined -fno-sanitize-recover=undefined` on every
  compiled binary: no runtime report from the six checkers, the mutation
  suites, the over-range control or the differential harness. A positive
  control confirms the sanitizer reports a 128-bit over-shift. Reproduce with
  `python3 research/bit589-checked-cpp-int-seed92/mutants.py --ubsan`.

**Header mutation test.** Run `python3 research/bit589-checked-cpp-int-seed92/mutants.py`
(opt-in, about two minutes). It reruns `verify.py` against 17 mutants of the
stand-in. 16 are rejected:

- wrapping `*`, `+`, `-` or unary `-`;
- an unchecked shift range, a shift that wraps into the sign bit, a narrowed
  shift count, or an accepted negative count;
- a zero-value shift that falls through;
- ignored stream flags;
- `msb` of zero, or an off-by-one `msb`;
- a dropped sign in `str()`;
- `<` implemented as `<=`;
- `bool` truncated to 64 bits;
- `>` wrong for a shared high word.

The one accepted mutant removes the negative-value shift guard. It is
equivalent: negative counts are refused first, and the range check refuses
every negative value.

## Scope and limits

- **Not removed:** the pip dependencies (`numpy`, `sympy`, `scipy`). This
  package removes only the one non-pip blocker.
- **Toolchain:** GCC or Clang is required. MSVC has no `__int128`.
- **Other repository `cpp_int` users are out of scope.** Examples are the
  optional `audit_coset_paths.cpp` and the enlarged-positive-frame profilers,
  which use division. They fail to compile against the stand-in rather than
  run with different semantics.
- **Not run:** the complete `make frontier1094-verify` with the stand-in. This
  host lacks `sympy` and `scipy`, which steps 5–7 need. Step 4, the only Boost
  step, is fully covered above.
- **Path limitation:** the pinned `verify.sh` expands paths unquoted, so it and
  this verifier need a checkout path without spaces. That is a pre-existing
  limit, and `verify.py` checks for it explicitly.
- **Claim:** this certifies equal finite checker results, not the
  multiplication theorem.

## Open next questions

The structured entries are in [TASK.json](TASK.json).

1. **Does the complete chain pass without Boost?**
   - *The question:* does `make frontier1094-verify` pass with the stand-in on
     a host that has the pip dependencies but no Boost?
   - *Why it matters:* it would show the whole selected cold replay needs no
     non-pip system package.
   - *First step:* run it in a fresh Ubuntu job without `libboost-dev` and
     compare receipts with a Boost run.
   - *Blocker:* this host lacks `sympy` and `scipy`, and the job needs a
     dedicated long-running workflow.
2. **Should `tune/verify.sh` quote its path expansions?**
   - *Why it matters:* it fails from checkout paths that contain spaces.
   - *First step:* a quoted successor replayed byte for byte.
   - *Blocker:* it is in a selected source root, so edits need a maintainer
     rehash.

## Credit

- **The checkers:** Dylan Crow's #370 official checkers, generalised; DaysSky's
  #381 `columns_k`.
- **The carrier skeleton and its `portable-include/bits/stdc++.h` precedent:**
  eumemic, who also wrote the #555 supplier.
- **The #589 bit transport and tuned word:** DreamingOfClouds.
- **The #741 audit's committed Boost receipts:** Douglas Colkitt.
- **The broader lineage:** credited in the
  [selected review](../../docs/research/community-batch1099-review.md).

Prepared by Sagar Thakrar with substantial Anthropic Claude assistance. That
included explorer, judge and skeptic subagents, which mapped the selected
chain's dependencies, prototyped the stand-in and reviewed it. New work is
Apache-2.0.

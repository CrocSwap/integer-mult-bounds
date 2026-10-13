# How many signed ports can proper stars decode simultaneously?

**Research theorem and scoped negative result; no new kappa.** This package
gives the uniform rank of global proper stars on signed k-subset ports and
the resulting sharp algebraic all-target puncture threshold. It also identifies
exactly when granting the global sum changes that threshold.

On the seed-selected `(p,k)=(8,4)` geometry there are **1,120 ports**:

| Allowed shared totals | Maximum retained ports, all decodable | Minimum deletions |
| --- | ---: | ---: |
| Nonempty proper stars, with arbitrary off-target coefficients | **447** | **673** |
| Same, also granting the empty star (global sum) | **448** | **672** |

Uniform overlap-class corrections do not change these numbers. Every maximum
is attained by a literal information set and one exact decoder per retained
port in [CERTIFICATE.json](CERTIFICATE.json).

The distinction from [Alishan Ladhani's PR #747](https://github.com/CrocSwap/integer-mult-bounds/pull/747)
is substantive: that contribution establishes the `(6,4)` all-target threshold
85, where the empty star is already redundant. Here the result holds uniformly
in p and k, and the empty-star distinction first appears at `(7,4)`.
The earlier `(6,4)` result is credited and independently corroborated.

## Uniform statement

For `p >= k >= 2`, there are `N = 2^k binom(p,k)` signed k-ports. A proper
star for a partial signed port L is the incidence vector `1[L subset S]`
over all source ports S, where `|L| < k`. All arithmetic is over F2.
Set

```text
rho(p,k) = sum_(j=0)^(k-1) binom(p,j) binom(p-j,min(k-1-j,p-k)).
delta(p,k) = 1 if k is a power of two and p >= 2k-1, otherwise 0.
```

The star code has dimension **rho** when the empty star is included, and
**rho-delta** otherwise. For power-of-two k, the permitted target-dependent
overlap corrections add no dimension, so the sharp all-target deletion
thresholds are `N-rho` and `N-rho+delta` respectively.

In the large-p range `p >= 2k-1`, `rho = 2^(k-1) binom(p,k-1)`.
In particular the nonempty-star class with power-of-two k can retain at most
`2^(k-1) binom(p,k-1)-1` ports. This is an exact scalar obstruction even if
all implementation costs are optimistically zero.

[RANK-PROOF.md](RANK-PROOF.md) proves the sign-monomial decomposition, invokes
the integral unsigned inclusion basis of Ghorbani, Khosrovshahi, Maysoori and
Mohammad-Noori, and proves the empty-star criterion. It distinguishes stacked
degrees from one fixed-degree inclusion matrix, whose rank can depend on the
characteristic. The all-target linear-algebra observation follows #747;
the overlap absorption is credited to [Luke Mansoor's #732](https://github.com/CrocSwap/integer-mult-bounds/pull/732).
This is a written proof with a named literature dependency, not a formal
proof-assistant development or an inference from the finite tests alone.

## Reproduce

Python 3.10 or newer, standard library only, from the repository root:

```sh
python3 -I -B research/paired-star-rank/verify.py
```

Expected:

```text
PASS_PAIRED_STAR_RANK: 36 cases; (8,4) ranks 447/448; all-target deletions 673/672; 8 negative controls; kappa unchanged
```

The verifier reads committed certificates and recomputes the entire expected
[RESULTS.json](RESULTS.json). It makes no network requests and imports neither
the builder nor predecessor code. All checks remain active under `-O`.

```sh
python3 -I -O -B research/paired-star-rank/test_verify.py
python3 -I -B research/paired-star-rank/build_certificate.py --output /tmp/paired-star-certificate.json
```

The first command runs four end-to-end test groups. The second independently
regenerates the certificate; its bytes must equal `CERTIFICATE.json`. JSON
output uses UTF-8 and LF on every platform. On Windows use `python` if
`python3` is not installed, and select an existing output directory.

## What the certificate proves

The builder enumerates compatible coordinate subsets using combinations and
sign tuples, then performs packed binary elimination. The verifier instead
enumerates ternary words and checks literal identities without elimination:

1. Each listed decoder is an XOR of allowed stars. On the information set
   its coefficients equal one distinct unit vector, proving independence
   and simultaneously providing every retained target's scalar decoder.
2. Every allowed star is reconstructed from those decoders on **every
   original port**, including deleted ports. This proves the upper rank bound.
   Checking only the retained coordinates would not suffice.
3. The attained rank is compared with the uniform formula. Complete port,
   star and case inventories are checked before accepting any identities.

Each case records its coordinate masks, information set and decoder coefficient
masks. Bit i of a decoder's hexadecimal coefficient mask selects entry i of
that case's `stars` list. Coordinate bit `2q+e` denotes sign e in pair q.

Completed finite coverage is all `k=2,3,4`, `p=k,...,8`, with and without the
empty star: **36 cases, 2,706 literal unit decoders and 3,714 full-family
star-spanning identities**. All permitted corrections for every target are
checked for k=2 and k=4. The k=3 cases are positive escape controls: permitted
corrections can isolate every target without puncturing, so the all-target
star-plus-correction theorem must retain its power-of-two hypothesis.

Eight built-in negative controls cover a decoder coefficient, duplicate
retained port, forbidden singleton star, illicit global sum, altered source,
missing decoder, false upper rank and missing case. The false-rank control
retains valid remaining unit decoders and must specifically fail the
full-family spanning check. The separate harness checks corrupted receipts
and source pins, preserves previous output on failure, and replays from an
unrelated directory with only the declared input files.

## Scope and provenance

The experiment changes the algebraic requirement from decoding one chosen
target to decoding **every surviving target simultaneously**. It does not
reopen the closed one-target search with more computation. The threshold
allows arbitrarily many proper stars and unrestricted target-specific binary
coefficients. Stars and overlap corrections are recomputed on the retained
family. Higher-degree stars, source-dependent overlap coefficients, nonlinear
decoders and other geometries are outside scope.

With more than 447 retained `(8,4)` ports, even free helpers, source access,
frame changes, copies, restoration and recursive children cannot fix the
nonempty-star identity obstruction. At or below that threshold, the attaining
identities are **not** a paid construction. Preparation, dirty restoration,
legal frames, recursive costs and assembly constraints remain unpriced; no
new supplier, stage schedule or exponent follows.

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCES.json](SOURCES.json) pins predecessor heads and inspected source bytes.
The accepted conditional saving stays
`51110230636731/31250000000000000 = 0.001635527380375392`, from
#626/#622/#623 with #543. Inherited compiler, common-label/mutable-basis,
hosting, precision, tape, recovery and analytic obligations remain.

[CLAIM.json](CLAIM.json) records OS-random assignment seed **46**, three
candidate tasks and the bounded stopping rule. The seed selected
`p=6+(46 mod 4)=8`, k=4. No pinned coordination issue existed, so the claim
was local. This package is additive; selected construction and `upstream/`
are unchanged. [VALIDATION.md](VALIDATION.md) records actual checks.

Prepared by **ellipsi2 (@ellipsi2)** with substantial **OpenAI Codex assistance**
in research, proof development, implementation, verification and writing.
One separate AI worker reviewed the uniform proof within the claimed scope.
No independent human review is claimed. See [NOTICE.md](NOTICE.md) for
predecessor and literature credit. New work is Apache-2.0.

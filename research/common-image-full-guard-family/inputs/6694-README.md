# Seven orthogonal full-guard events lie below the product of their marginals

This contribution was produced by Nick Petalas. Apache-2.0. Independent human
and formal proof-kernel review are unclaimed.

**Claim type: scoped counting proof resting on an exact finite certificate. No κ.**

Over F_2, let U_1, ..., U_7 be pairwise orthogonal rank-one idempotents on F_2^m
and let G be uniform in GL_m(F_2). Event E_t says every leading principal minor of
orders 1 through m-1 of G(I-U_t)G^-1 is nonzero. With n = m-1, X = 2^m and
s_m = 3^n / ((X-1) 2^n) the probability of one event:

```text
for every m >= 7:   Pr(E_1 ∩ ... ∩ E_7) < s_m^7
```

At m = 7 the joint probability is 0 (a passing header needs m >= k+1). At m = 8 it
is 29/5201587077120, about 5.575e-12, against s_8^7 of about 6.063e-9. The ratio
tends to 1 from below: 1 - rho_m = 42 (7/9)^(m-1) (1 + O((19/21)^(m-1))).

This answers open next question 1 of unpaidmoon's [PR6515](https://github.com/CrocSwap/integer-mult-bounds/pull/6515)
(`research/six-event-guard-correlation`): the same inequality for seven events,
inside the strip 8 <= m <= 344 that it leaves open. The proof uses Nick Petalas's
character law (PR4275) as a cited premise and does not use the k = 6 theorem of
PR6515, the remainder bound of PR5146 or the k = 4, 5 theorems.

## New step

The signed spectrum of all 2^42 seven-vertex characters is computed exactly, in
about 40 seconds on one core, instead of by a 2^42 Gray-code walk. `spectrum.c`
(i) reduces the first five vertices to their 9,608 orbits under S_5, and
(ii) evaluates all 2^12 arc patterns of the last vertex from two 64-entry tables,
because Z(c) = F1(u) + F2(v) there ([PROOF.md](PROOF.md) section 2). The table
`SPECTRUM_K7.txt` has 493 entries; N_0 = ... = N_6 = 0 and N_7 / 2^42 = 29,816,640 =
7! * 5916. Strict inequality is checked with exact integers for every 6 <= n <= 400, and
an integer tail bound (L(187) < 0 < L(188)) closes every larger m.

## Evidence

From the repository root; a C compiler (`cc`, `gcc` or `clang`) is required.

```sh
python3.12 -I -B research/seven-event-guard-correlation/verify.py            # PASS_SEVEN_EVENT_GUARD_CORRELATION
python3.12 -I -B research/seven-event-guard-correlation/verify.py --brute6   # PASS_SEVEN_EVENT_GUARD_BRUTE6
python3.12 -B scripts/research_package.py --package research/seven-event-guard-correlation
python3.12 -B scripts/check_research_commit.py --package research/seven-event-guard-correlation --check-source-history
```

The default replay regenerates the k = 7 spectrum and compares it byte for byte with
`SPECTRUM_K7.txt`; validates the enumerator against labelled brute force at k = 3, 4,
5, against the literal three-state definition at k = 3, 4, and against the spectra
printed in the pinned PR4275, PR4599 and PR4607 files; checks the subset form
against the definition on random characters at k = 5, 6, 7; checks the spectrum
facts, the exact range, the tail bound, the closing inequalities and the rate; and
runs six rejection controls (a one-unit change to a top coefficient, a doubled top
coefficient, a shifted subset weight, a doctored k = 4 spectrum, an altered pinned
statement, a wrong tail threshold). `--brute6` checks the orbit-reduced k = 6
spectrum against labelled brute force over all 2^30 matrices. It also reproduces the
k = 6 figures reported in PR6515 (176 entries; 1, -30, 120 at 729, 567, 513) as a
by-product. `--labelled7` (not registered; about 7 minutes on 18 cores) repeats the
k = 7 run over every labelled five-vertex digraph with weight one and no orbit
reduction; it covers all 2^42 characters and gives the same 493-entry table.

Local runs (CPython 3.12.15, macOS arm64, 18 cores, compiler `-std=c11 -O2 -Wall
-Wextra -Wpedantic -Werror`): the default replay takes 13.3 s wall (46 CPU-seconds,
four shards; one shard needs 37 s for the k = 7 table alone), also with `-O`; `--brute6`
takes 31.6 s (125 CPU-seconds). These are check durations, not a speed comparison.

## Limitations

* The spectrum is a finite computation by a program. It is validated as listed above
  but not re-derived by hand, and no independent re-implementation is supplied.
* Covered: exactly seven pairwise orthogonal rank-one requests over F_2, complete
  uniform headers, every m >= 7.
* Not settled: k >= 8, odd characteristic, nonorthogonal or restricted request
  families, negative association of six or seven indicators (a stronger statement),
  any physical sampling, selection or restoration cost. No supplier, κ or selected
  frontier change. Lean, Docker and the selected cold replay were not run.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. **k = 8.** Does the inequality hold for every m >= 9? *First step:* extend
   `spectrum.c` to eight vertices (a 30-bit base mask with 1,540,944 orbits under
   S_6, and 128 x 128 sweeps), compressing the two tables to value histograms.
   An extrapolation from the k = 7 timing gives roughly 30 core-hours (not run).
   *Blocker:* compute time, not mathematics.
2. **All k.** The computed tables show levels 3^k, 7*3^(k-2), 19*3^(k-3), 55*3^(k-4)
   with coefficients 1, -k(k-1), k(k-1)(k-2), -8*C(k,4) for k = 4..7 (checked by
   `verify.py`, not proved), every Z odd and one sign per Z value. *First step:*
   combine PR6440's third-level classification with a uniform bound on the remainder.
   *Blocker:* no all-k bound on characters below the first levels.
3. **Shared kernel directions** (PR6515 open question 2). *First step:* test whether
   PR4240's joint law for nonorthogonal rank-one requests extends to several requests
   with one shared direction. *Blocker:* not examined here.

## Credit

Nick Petalas (PR4275) supplies the character law, the transfer and the binary
threshold; Nick Petalas (PR4599) the four-event inequality; Ryanson Jonathan
(PR4607) the five-event inequality and spectrum; Nick Petalas (PR5146) the remainder
bound; Nick Petalas (PR6440) the equality classification of the third level;
unpaidmoon (PR6515) the six-event inequality, the open question and the
enumeration-plus-tail method adapted here. The orbit reduction, the two-table sweep
and the k = 7 table are new in this package. The Weierstrass product inequality and
Walsh-Hadamard transform are classical. Predecessor packages are unchanged.

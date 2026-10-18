# PR225: four reviewed profiles, six submitted profiles

**Research consolidation and independent finite verification; no new kappa.**
The round-nine review of Chafik Boukhalfa's PR225 covered four three-stage
profiles at `b8e829172fc92bbbd6b1eda560ab5d99aebee0df`. The submitted head
`830971b6b157374ebf941d0ca0b73fd2b956e3e0` adds two five-stage profiles and
Proposition E. This package closes the finite source/profile/pricing gap and
states the remaining transfer obligation precisely. It does not approve the
whole PR or replace the selected integer-multiplication construction.

Research base: **`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`**, whose selected
PR942 certificate was `kappa = 1661960547713947/10^18`. During this run main
advanced to **`ba82555c64e1879e4b7decce28186f208fcb8262`**, selecting PR1042 at
`kappa = 1672188119205421/10^18`. The submission is rebased onto that commit;
the capsule deliberately preserves the original research context. This
contribution changes neither selection. Assignment seed **97** and the three
candidate tasks are recorded in [CLAIM.md](CLAIM.md).

## Reproduce offline

Python standard library only; no Git, network, compiler, Lean or ancestor
checkout is needed. Works with assertions disabled:

```sh
python3 -I -O -B research/pr225-five-stage-reconciliation/verify.py
```

Expected:

```text
PASS_PR225_FIVE_STAGE_RECONCILIATION profiles=6 added_profiles=2 next_points_rejected=6 source_files=19->23
```

Run the mathematical, provenance and corruption controls:

```sh
python3 -I -O -B research/pr225-five-stage-reconciliation/test_package.py
```

The optional `replay_original.py` uses Python >= 3.11 to run both **unmodified**
original checkers, each in a fresh temporary source tree, comparing all their
original moment certificates and complete expected receipts. It is a separate
reproduction, not the independent implementation.

## What changed between the two source heads

The complete `research/exact-dft-transfer/` tree and its workflow contain
19 files at the reviewed head and 23 at the submitted head:

* Four additions: child and moment certificates for `pr194-five` and
  `pr233-five`.
* Six modifications: `NOTICE`, `PROOF.md`, `README.md`, `SOURCE.json`,
  `expected.json`, and `verify.py`.
* Thirteen unchanged files: the workflow, the four previous child certificates,
  four previous moment certificates, three vendored supplier certificates, and
  `scripts/moment.py`.

The four old `expected.json` rows and all four supplier source pins are
unchanged. The sole framework addition is the pinned five-stage Lean source.
The base ledger correctly says `changed_since_review`; its review and replay
log end at `pr233`, not `pr233-five`. The new scope is substantive, not just
the old PR title's stale numerical value.

[EXPECTED.json](EXPECTED.json) lists every file's Git blob and SHA256, every
dependency commit and exact interval, and the complete change inventory.
`sources.json.gz` contains 70 original Git objects. The verifier recomputes
each Git object hash, walks the fixed commits' original tree objects to every
file, checks every supplier's SHA256 and vendored equality, and requires every
captured object to be used. Thus a rewritten manifest or rehashed blob cannot
silently change what the original commits contain. This covers the specified
package/workflow and input paths, not the full repository or commit ancestry.
The original notices and source code are retained byte for byte in the capsule.

## Exact finite results

For `M(a) = sum_r H[r] (r/m)^(1-a)`, all six supplied values satisfy
`M(a) < W`, and **all six next points satisfy `M(a + 10^-7) > W`**.
The table shows shortened decimal values for orientation; the exact outward
intervals, with denominator `10^60`, are in the receipt.

| Profile | m | W | Rank deficit | a | W - M(a), approximately | M(a + 10^-7) - W, approximately |
|---|---:|---:|---:|---|---:|---:|
| PR144 | 72 | 29,937 | 1,936 | 607/1250000 | 0.003158222953 | 0.002381682909 |
| PR200 | 66 | 13,163 | 1,320 | 3327/5000000 | 0.002691754297 | 0.000316285247 |
| PR194 | 66 | 12,052 | 1,320 | 7009/10000000 | 0.000526788483 | 0.002329384572 |
| PR233 | 66 | 12,052 | 1,320 | 7099/10000000 | 0.000211016862 | 0.002609023848 |
| PR194, five stages | 110 | 14,692 | 3,080 | 7474/10000000 | 0.002060600786 | 0.001689720421 |
| PR233, five stages | 110 | 14,692 | 3,080 | 7547/10000000 | 0.001352658402 | 0.002361510116 |

These are historical exact-DFT moment parameters, not new integer-
multiplication kappa claims. Since every child has `0 < r < m`, each summand
strictly increases with `a`; the two checked endpoints bracket the unique
moment root for each fixed histogram. No other supplier family is searched.

### The five-stage invoice

For the pinned PR194 and PR233 three-stage histograms, the stipulated layout is

```text
H_inv = (H_3 - 2640 e_2) / 3
H_5   = 5 H_inv + 2640 (e_4 + e_21 + e_42 + e_46)
m_5   = 5 * 22 = 110
W_5   = 4 * 1320 + 9412 = 14692
```

Every invocation multiplicity is a nonnegative integer. Both derived
histograms agree exactly with the submitted certificates, and each has
`sum r H_5[r] = 1613040`, hence `110*14692 - 1613040 = 3080`.
All four bridge terms are retained. This prices the stated layout; it does
not construct or independently justify its physical scheduling.

A meaningful control replaces two rank-2 children by one rank-1 and one
rank-3 child. Child count, total rank and deficit stay the same, but the
moment intervals become disjoint. Source-derived histogram comparison rejects
this mutation. Merely matching the rank deficit would not establish pricing.

### Why the next-point distinction matters

The original `moment_margin` returns `W` minus an **upper** bound on `M`.
Its nonpositive result at a next point proves that this sufficient test does
not admit the point; alone it does not prove `M >= W`. The historical outputs
and old review used the phrase "next grid point rejected".

Our independently implemented lower bounds are strictly above `W` at all
six next points. Thus the stronger mathematical reading is valid for these
six fixed profiles. No counterexample to a supplied endpoint was found or
claimed. The original conservative margins remain valid and are preserved.

## Independent interval argument

The verifier imports none of PR225's code. It uses directed **integer**
arithmetic at scale `S = 10^60`, a range-reduced logarithm, and an exponential
Taylor interval. PR225 instead uses an unscaled rational logarithm and the
upper majorant `1+x+x^2/(2(1-x/3))`.

1. Write `m/r = 2^k q`, with `1 <= q <= 2`. For
   `y=(q-1)/(q+1) <= 1/3`, use the first 80 terms of
   `log(q)=2 sum_{j>=0} y^(2j+1)/(2j+1)`. The omitted positive tail is at most
   `2 y^161 / (161 (1-y^2))`. Every multiplication and division rounds
   down on the lower path and up on the upper path; the upper power also
   bounds the tail. Add `k` separately enclosed copies of `log(2)`.
2. Multiply the log endpoints outward by the exact rational `a`, obtaining
   `L/S <= x <= U/S`. All inputs are checked to lie in `0 <= x <= 1/16`.
   Sum `exp(x)` through degree 24 with outward-rounded term recurrences.
   The lower partial sum is a lower bound. For the upper tail beginning
   at degree 25, all subsequent ratios are at most `x/26`, so its bound is
   `t_25 / (1-x/26)`.
3. Multiply each exponential interval outward by `H[r]*r/m`, sum every
   nonzero bin, and compare to the integer `W*S`. No floating arithmetic
   participates in acceptance or receipt construction.

These are analytic bounds, not an appeal to numerical agreement. The tests
also compare every used log ratio against a separate exact `Fraction` oracle
that reduces by powers of four, and 27 exponential inputs against exact
48-term rational intervals. Those finite cross-checks are supporting tests,
not a formal proof of the interval implementation or the transfer theorem.

## Source pins, scope and attribution

The four supplier pins are exactly those in PR225:

| Supplier | Commit | Original certificate |
|---|---|---|
| PR144 | `d1d6c070f5a8c684727ee7ec35d930f9ebfa9758` | `certificates/paired-cube-complex-input.json` |
| PR200 | `a1175449f34d39ff933d9d8ab23ced1f32b290ec` | `research/paired-cube-diagonal-bit-168/certificate.json` |
| PR194 | `a8c87783785be6fe20c4a8bb2ac4b3eec295a179` | `research/source-assisted-v4/certificate.json` |
| PR233 | `109a857a329d18ed5552d5573f17ddfa886ae57f` | `research/source-assisted-v4-layer/certificate.json` |

The external framework pins are recorded, **not freshly verified**:
eumemic/exact-dft-bounds `6f87d1a0c9ae462cdcb2034a1361c87623221e66` and
`c92cf703e67c2a556891cf306c9546620a39ff01`; openai/math
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`; and Jacob Sussman's
wht-power-saving-lean `f010392c923279e3dd59ef3aa5fedad23affc5fd`.

The unresolved Proposition E step is that PR233's changed pairing admits the
referenced five-stage batched network with this invoice. The submitted proof
itself distinguishes this priced transfer from Sussman's kernel-checked
PR193 word. This run does not assert the current availability or absence of
later Lean certificates. The original suppliers are not rebuilt here; no
external Lean build, phase/frame realization, all-size transfer, fixed-tape
implementation, precision proof or multiplication assembly is established.

Credit: **Chafik Boukhalfa** for PR225 and PR233's pairing transfer; **eumemic**
for batched recursion and the original moment method; **Jacob Sussman** for
the five-stage layout; **hcg890** (PR234) and **SovereignSteak** (PR250) for
the referenced five-stage suppliers/invoice; **icekylinx**, **ikeboy** and
the PR144/168/184/194/200 lineage for the constructions; **Ryan Shea** for
the exact-DFT transfer idea; **OpenAI** for the transform framework; and
**Douglas Colkitt** for the original scoped review. The complete predecessor
notice is preserved in the capsule. Related PR250/256/304/327 build later
suppliers; this contribution neither imports nor re-prices their mechanisms.

Prepared by **Ross Richardson with substantial OpenAI Codex assistance**.
Apache-2.0, retaining all predecessor notices. See [VALIDATION.md](VALIDATION.md)
for executed checks and limitations.

## Capsule regeneration

For reviewers with the pinned commits already fetched:

```sh
python3 -I -B research/pr225-five-stage-reconciliation/capture.py
python3 -I -O -B research/pr225-five-stage-reconciliation/verify.py --write-receipt
```

The decompressed capsule payload SHA256 is
`3a374e1b6471d3f2a8942b7896858934ff606db6e217b54a26405f673170a859`.
Compare payloads, not gzip-container bytes. Regeneration touches only this
package. The verifier normally writes nothing; it compares the complete
receipt, not just its final pass string.

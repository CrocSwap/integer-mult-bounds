# Deferred Gaussian normalization through actual scalar recovery

**No new kappa.** This package binds the current normalized public Gaussian
returns to a concrete native pointwise/recovery endpoint. It funds three
accumulated Gaussian normalizers, both source S factors, the actual q+3
external versus q+2 native carrier, and the strict integer rounding gate.
The Poisson identity, Fourier permutation cancellation and S² normalization
are already proved in CrocSwap/integer-mult-bounds#4320 and are credited.

Let Gamma=K_f+K_c be the already declared Gaussian normalization and
lambda=2^-Gamma. Two normalized forwards followed by one normalized
opposite return lambda³ times the canonical normalized convolution.
Canonical `Sandwich.recover` expects restoration after each transform; its
old shift 2b+4 cannot consume this changed channel. The new endpoint shifts
by **2b+4+3Gamma after two exact S multiplications**, then rounds once.

For b>=1 and the actual checked guard S<2^b, set

```text
a = 2 ceil(log2 S) + 2b + 7
tau = a + 2Gamma + 2
z = tau + Gamma + ceil(log2 m) + 1
q >= a + 3Gamma + 7, plus the exact public source/ledger guards
W_recovery = q + 3Gamma + 4b + 6.
```

Assign each expansion, middle and compression stage restored allowance
2^-tau. For the compression-only ledger this means gamma_c=K_c and target
tau_comp=tau+K_f, so tau_comp+gamma_c=tau+Gamma. The common source targets
are fixed before Reference normalizer bits; the full ordering and finite
gates are in `PROOF.md`. With canonical p0=6b and Gamma=o(p0), all online
widths remain O(p0); setup and eventual source admissions remain charged.

The actual normalized maps then have error at most lambda³2^-a. The
computed pointwise field stays inside the opposite call's quarter-disk,
including Gamma=0, and the final real coefficient error after
S²2^(2b+4+3Gamma) is **strictly below 1/4**. Width W covers both S factors,
the complete shifted numerator and all pre-drop scalar products.

## Actual executed interface

`DeferredTail` copies borrowed encoded S,b,q,Gamma; its constructor checks
S<2^b and q>=b+2. It runs the authenticated native scalar/word routines,
with the fixed FFT-word cutoff 4096, and exposes protected pointwise and
integer-recovery outputs. It checks actual half-disk inputs, quarter-disk
products, complete compact S extent, alias exclusion and cleanup.

The public radius-2/3 codec uses q+3 sign-magnitude bits. The fixture executes
that real zero-drop codec, then the new exact native q+3-to-q+2 carrier.
The reverse direction and exact conjugation are also executed. Narrowing
is funded only after the completed normalized transform, not on arbitrary
intermediate Core/halo fields. There is no new fractional truncation here.

Two genuine native fixtures, S5/b3 with Gamma0/q26/W44 and Gamma2/q32/W56,
recover `[28,38,51,32,5]`. The actual zero-Gamma endpoint on the deferred
Gamma2 return instead produces `[0,1,1,0,0]`. These are scalar-endpoint
witnesses, outside the q>=101 expansion-source domain. They do not run
production transforms, T-to-S extraction, CRT or carry propagation.

## Reproduce

From the repository root, Python 3.12 and standard library only:

```sh
python3 -B scripts/research_package.py --package research/deferred-gaussian-recovery
python3 -B scripts/check_research_commit.py --package research/deferred-gaussian-recovery --check-modes
```

The normal and optimized commands each have a 120-second limit. Expected
marker: `PASS_DEFERRED_GAUSSIAN_RECOVERY`. A direct bounded replay is
`python3 -B research/deferred-gaussian-recovery/verify.py`.

The checker authenticates 11 canonical and eight public files, then checks
405 independent rational allocation/radius/width/source-order cases,
including b=1, S=1 and Gamma=0. Native controls reject short/long compact
fields, an unextracted padded field, excessive radius, descriptor/work
aliases and a second call before consuming its protected return. Borrowed
fields and descriptor origins are preserved. Wrong S/Gamma algebra is
distinguished separately. No predecessor numerical checker is imported.

## Full costs and limitations

Legal pointwise calls pay 10S exact real products including radius checks;
recovery pays 4S; each carrier pass pays 2S squares and complete reads/writes.
The new endpoint cost is O(S M_word(W)+SW+poly(q+Gamma+b+log S)), retaining
the complete scalar tariff and historical backing. All three transforms,
every full padded T-field, original-q extraction, all three CRT conversions,
source setup, grid/sign conversions and final carry/output remain paid.

The admitted direct expansion reference already costs Omega(Tq log T).
This numerical allocation therefore supplies no fast full multiplication
bound. The old Catalogue is neither invoked nor waived. Canonical main is
7c49fe32c55de02c2c873655c804b16e4c3fef0a; source/dependency pins and exact
public proof copies are in `SOURCES.json` and `DEPENDENCIES.json`.

## Open next questions

Bind an actual production controller to these exact normalized return
contracts, original-coordinate T-to-S extraction, S-sized endpoint fields
and CRT record widths. A fast grouped Broad must independently preserve
the same target and prove its complete physical cost. Native/scalar/Fourier
premises and the complete integer-recovery caller remain open. The selected
bound and all five foundational assumptions are unchanged.

Prepared for @CubeJerry with substantial OpenAI assistance. See `NOTICE.md`,
`OVERLAP.md`, `PROOF.md`, `CHECKPOINT.md` and `PR-BODY.md`. Same-team review
and finite independent algorithms are not human or proof-kernel acceptance.

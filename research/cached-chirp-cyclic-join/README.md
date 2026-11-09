# Source-bound cached chirp / cyclic / grid join

**No new kappa.** This package connects the exact public cached phase payload
consumer from CrocSwap/integer-mult-bounds#6906 to the canonical odd-slope
`Cyclic.run` implementation from CrocSwap/integer-mult-bounds#3763. It funds
both grid conversions and all three uses of the same rounded chirp, closing
the concrete convolution/grid interface that #6906 lists as open.

The input is the actual full padded q-grid field, with maximum complex
modulus at most one half, checked by real exact scalar products. Axis zero
is fastest; the source retains every original dyadic period, odd slope and
coordinate, including Gaussian holes. For D>=2, t_0=r>=4, other t_i in
{r/2,r}, T=product t_i and M=T/r=2^A, the returned common-grid field obeys

    ||yhat - Q_freq F_t x||_* < (8M+9D+18) 2^-f + 2^(1-q),

where ||.||_* is maximum coordinate component-l1, and F_t is normalized.
For target chi, choose q>=chi+2 and

    f=max(q,16,A+13,chi+1+ceil(log2(8M+9D+18)),ceil(log2(6D))).

The error is then strictly below 2^-chi. This is f=O(p0) for the stated
fine-family parameters. The actual output modulus is below .501, so its
component-l1 radius is below one. The common codec introduces no normalizer;
the existing total Gaussian Gamma is unchanged. See PROOF (7)-(8) for the
explicit remaining broad-expansion term in the completed caller.

## What executes

`joined_middle.py` runs three unchanged CachedChirp owners on one certified
phase bank: kernel-on-ones, conjugate input endpoint and conjugate output
endpoint. Between endpoints it runs the actual complete Cyclic child,
including its three Fourier calls and exact M restoration. Exact signed
carrier conversion joins the two native widths; the public Core/halo codec
lifts q to f and returns once to q. The unchanged canonical cohort binder
compares all corrected ring export bytes before enabling both child APIs.

The full invoice keeps 3 T_F, every cyclic scalar and source cost, three
cached passes, 2T radius squares, complete T-record conversion/copy/cleanup,
all table preparation and all retained high-water backing. It does not price
convolution as a free primitive or transfer the historical Fourier frontier
to an unadmitted fine-family production call.

## Reproduce

From the repository root, using only the standard library:

```sh
python3 -B scripts/research_package.py --package research/cached-chirp-cyclic-join
```

The two registered commands run normally and with assertions disabled, each
with a 120-second limit. Expected marker: `PASS_CACHED_CHIRP_CYCLIC_JOIN`.
For one direct bounded replay:

```sh
python3 -B research/cached-chirp-cyclic-join/verify.py
```

The actual T8 fixture has radices (4,2), slopes (3,1), q10/f16/W19 and chi7.
Its output agrees exactly with a separately written staged integer oracle.
Against the independent exact dense Gaussian-rational Fourier sum, maximum
component-l1 error is 11/8192, below the proved 45/16384 envelope and 2^-7.
It performs 192 cached scalar products and 16 input-radius squares, in
addition to the Cyclic arithmetic. It rejects an actual over-radius input
before any new cached call and protects a pending return. Conjugation,
missing M restoration and dropped-grid controls distinguish the seams.

The fixture uses the retained q2 finite provider and canonical exact small
metadata specialization. It does **not** execute production GL64/O73,
replace numerical children, or prove backend admission by dense comparison.
The finite receipt and attempt history are in `evidence/REPLAY.json` and
`CHECKPOINT.md`. The universal result is the explicit proof under its named
source, scalar and Fourier contracts; model-assisted review is not human
or proof-kernel acceptance.

## Dependencies

Canonical main is pinned at 7c49fe32c55de02c2c873655c804b16e4c3fef0a.
`SOURCES.json` authenticates all 18 live canonical inputs. `DEPENDENCIES.json`
authenticates retained public #6906 files, the public codec, the exact
Reference/ideal join and the caller obstruction. These public but unmerged
contributions are dependencies, not silently assumed canonical acceptance.
No source is downloaded by the checker.

## Open next questions

This closes only the cached convolution/grid middle. Actual broad expansion,
its reached radius/error, fine-family Fourier backend admission, the opposite
transform and complete CRT/integer recovery remain open. The old Tensor
catalogue guards are neither invoked nor waived. The selected certificate,
complete multiplication bound and five foundational assumptions are unchanged.

Prepared for @CubeJerry with substantial OpenAI assistance. Predecessor credit
and exact scope distinctions are in `NOTICE.md` and `OVERLAP.md`; the full
proposed PR description is in `PR-BODY.md`.

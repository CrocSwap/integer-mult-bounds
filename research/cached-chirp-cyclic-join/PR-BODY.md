## Problem and exact result

The public cached phase payload package (#6906) explicitly leaves complete
chirp convolution and payload-grid conversion open. A compression-only
precision ledger does not fund those operations or their actual intermediate
radius. This package connects that exact public consumer to canonical
`Cyclic.run` (#3763), retaining every original padded coordinate and the
same immutable rounded phase bank at all three chirp occurrences.

For D>=2, t_0=r>=4, t_i in {r/2,r}, odd original slopes, T=product t_i,
M=T/r=2^A and an actual q-grid input of maximum modulus at most one half,
the joined output satisfies

`||yhat-Q_freq F_t x||_* < (8M+9D+18)2^-f + 2^(1-q)`.

Here the norm is maximum component-l1 and F_t is normalized. Choosing
`q>=chi+2` and
`f=max(q,16,A+13,chi+1+ceil(log2(8M+9D+18)),ceil(log2(6D)))`
gives strict error below `2^-chi`; `f=O(p0)` for the stated fine family.
The reached output modulus is below .501. The exact q-to-f lift and final
f-to-q projection introduce no normalizer or new Gaussian Gamma.

## What changes and why it is useful

- Execute kernel-on-ones, both conjugate payload passes and the actual
  complete Cyclic child, consuming each protected return.
- Check input radius with actual exact scalar products; join the different
  native signed carrier widths and the public common-grid codec.
- Reuse the unchanged canonical cohort binder, which authenticates and
  compares every corrected ring export byte before enabling the APIs.
- Prove the actual-input defect from the shared rounded kernel A, and state
  the precise broad-expansion term remaining at the public compression
  caller. Keep all three full Fourier calls, complete padded-field scans,
  source setup, copying, cleanup and retained backing in the invoice.

Cached phase stability/travel (#4325/#5987/#6906), the cyclic algorithm and
Fourier identity (#3763), old expansion bounds (#5295/#5325), and the exact
binder are predecessor results. The distinct contribution is this executable
source/grid/convolution interface and its explicit joined precision/radius
budget. `OVERLAP.md` records the bounded audit.

## Pins and reproduction

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Cached public source: `3c0443b2aa721ce692199ff31abc18e8d917596a` (#6906).
Public codec: `73d5adaba2b7dc662e86eb901e81369a3f73be9f`.
Public Reference/ideal join: `4509310a9a58d4c41c74029f899cbf36be1af9a1`.
Public caller audit: `96211247643059ae48af4c7d9dc960034798935d`.
Exact file hashes are in SOURCES.json and DEPENDENCIES.json; public unmerged
heads are explicitly retained dependencies.

```sh
python3 -B scripts/research_package.py --package research/cached-chirp-cyclic-join
python3 -B scripts/check_research_commit.py --package research/cached-chirp-cyclic-join --check-modes
```

The registered normal and optimized runs emit
`PASS_CACHED_CHIRP_CYCLIC_JOIN`. The genuine T8 fixture has q10/f16/W19,
radices (4,2), slopes (3,1), 192 cached scalar products and 16 input-radius
squares, in addition to the actual Cyclic arithmetic. A separately written
integer oracle matches all output words; an exact dense Gaussian-rational
sum gives maximum component-l1 error 11/8192 below the 45/16384 bound.
Actual radius and pending-return failures plus conjugation, missing M and
grid controls detect the critical seams. All 75 finite allocation cases
pass; the proof, rather than that finite list, supplies the universal claim.

## Limits, status and credit

**No new kappa.** The complete multiplication bound and selected certificate
are unchanged. The finite q2 native provider is not production GL64/O73.
The proof retains the source, scalar and Fourier contracts; it does not
establish their all-size acceptance by replay. Broad Gaussian expansion,
its reached radius/error, fine-family backend admission, opposite transform
and complete CRT/integer recovery remain separate obligations. The old
Tensor catalogue is neither invoked nor waived. Another session's broad
Core work is outside scope.

Prepared for @CubeJerry with substantial OpenAI assistance in research,
implementation, proof, independent exact oracles and packaging. Predecessor
credit is in NOTICE.md, and retained notices remain intact. Separate
model-assisted lead review is not human or proof-kernel acceptance.

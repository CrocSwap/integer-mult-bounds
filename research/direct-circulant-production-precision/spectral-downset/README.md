# Smaller sufficient precision from the actual spectral downsets

This sequential supplement provides a separately reviewed precision API for
the pinned #7849 direct-circulant word. It combines the completed source-cut
audit with sharper spectral estimates for the actual padded roots and their
prepared generator children. The original parent `precision.py`, proof and
source routines remain available unchanged.

The accepted statement is a local conditional numerical theorem. The exact
source compiler, phase, displacement-rank, represented-input native H,
Fourier geometry and recovery contracts remain its premises. It does not
discharge a whole selected assumption or change the selected multiplier
exponent.

## Result and supplementary API

Let `d>=1`, let `ell_i>=1` be the padded binary side widths, put
`L=sum(ell_i)`, and let `p>=1` be the public precision. Define

```
E = ceil(257L/2) + 1354d
A = 20L + 303d
J = 20000(d+1)(max(ell_i)+2)^6
C = 4J(d+1)^2+d+1
P = 4p+A+2E+bit_length(C).
```

The unchanged source producer run at target `P+8`, with execution on
`Grid(P)`, has raw coordinate error strictly below `2^(-4p)` on the
parent theorem's complete padded half-disk input domain. Its public-grid
integer-recovery corollary retains the parent volume, scaling, no-wrap,
CRT-character and native-service hypotheses.

The new module's functions are:

- `production_precision(public_bits, side_widths) -> int` for the sufficient
  fractional-bit count;
- `precision_budget(public_bits, side_widths) -> Budget` for the complete
  interval, local-error, stage-count and strict error-envelope accounting.

The API rejects empty, nonpositive and Boolean precision/width inputs. To
select this supplementary module explicitly from the repository root:

```python
import sys

sys.path.insert(0, "research/direct-circulant-production-precision/spectral-downset")
from precision import precision_budget, production_precision

assert production_precision(72, (4, 5)) == 8842
budget = precision_budget(72, (4, 5))
```

Use the correct module location when a program also loads the older parent
module named `precision`; normal Python module caching applies. No frozen
supplier call site is patched by publishing this supplementary API.

## Consumer consequence

The selector simplifies to

```
P = 4p+277L+3011d+(L mod 2)+bit_length(C).
```

It saves exactly `1084L+1735d` fractional bits against the parent #8093
selector, whose stage coefficient `C` is the same. The comparison with the
original #7849 selector is also proved for all admitted dimensions.

| Public bits `p` | Padded side widths | Original source | Parent #8093 | This supplement |
|---:|---|---:|---:|---:|
| 30 | `(1,)` | 229,664 | 6,257 | 3,438 |
| 72 | `(4, 5)` | 688,620 | 22,068 | 8,842 |
| 12,288 | 16 axes of width 128 | 70,304,068 | 2,912,487 | 664,695 |

These are sufficient precision budgets, not minimum required precisions or
measured runtime and memory savings. The later #7981 source changes the
chronology and raw error target. No comparison against that changed supplier
is asserted; reusing these local constants there requires checking its
caller and complete schedule.

## Why the smaller bound is valid

For every fixed external `P`, the actual rational stored root satisfies
`||T||_2<2` and every leading inverse has norm at most `4t`. The proof uses
these spectral bounds only in its analysis. The source's component
admission guards, full allocation, child target bits and coefficient
generation rules are unchanged. Choosing a different external `P` naturally
regenerates coefficient bytes through those same rules.

Nick Petalas's credited block-solve theorem gives the admitted ideal
downset cap `B_new=2^7*t^3`, including for non-Toeplitz identity-padded roots.
The old allocation already funds this smaller cap. The actual displacement
component norm `be` passed to `generator_allocation` is at most `32t^2`,
which gives an actual child-fragment cap `H<=2^23*t^7`. The accepted
nested-downset interval theorem then gives

```
Full prefix/suffix and inverse cap K <= 2^33*t^11
Full interval and inverse cap G <= 2^61*t^20.
```

The proof charges the complete sixteen-H lowering, pivot and ordinary
factors, routing switches, two root passes per axis, exterior diagonals,
partial H packs and the spectral-to-infinity conversion on all padded
coordinates. It also charges coefficient-table rounding, the literal
odometer's cached product lineage and the final data multiplication. A
strict bootstrap proves the computed-state radius used by the error sum;
it is not an unproved bound on an intermediate endpoint.

All these steps are in [PROOF-DRAFT.md](PROOF-DRAFT.md), which retains its
pre-review filename and wording for frozen byte identity. The later
[review/REVIEW.md](review/REVIEW.md) accepts that exact proof at SHA-256
`0501a6a9a5f467fff4c998606965babc8157e74d98cf33b93f71fb10674d57bb`
and records the complete spectral/component, source-child and consumer
bridges. The original research plan is retained in `TARGET.md`; its earlier
pending-review labels are superseded by this separate accepted review.

## Evidence and replay

The author checks 116 unchanged full allocations, 118 literal child
allocations, 53 selector cases, and two actual padded-root factories,
including `r=3<t=4`. These finite probes establish source bindings and
failure-sensitive examples; the universal theorem is the written proof.

The separate reviewer imports neither the author checker nor the compiler
factory. It authenticates 24 source records and the frozen dependency
proofs, then checks 113 selector cases, 254 symbolic cache records and
762 complex rational records. Of those numerical records, 507 include a
zero factor. Separate controls reject a broken carry refresh, conflation of
spectral and component norms, reliance on only a whole-matrix inverse, and
loss of the strict certified error envelope. Normal and optimized reviewer
runs produce byte-identical receipts.

From the repository root, the registered package replay includes the author
and independent supplement checks:

```sh
python3 -B scripts/research_package.py --package research/direct-circulant-production-precision
```

To run only this supplement:

```sh
python3 -I -W error -B research/direct-circulant-production-precision/spectral-downset/run_check.py
python3 -I -W error -B research/direct-circulant-production-precision/spectral-downset/review/independent.py \
  --candidate research/direct-circulant-production-precision/spectral-downset \
  --cuts research/direct-circulant-production-precision/compiler-intervals \
  --parent research/direct-circulant-production-precision \
  --output /tmp/direct-circulant-spectral-review.json
```

The review also supports the same command with Python `-O`. The retained
normal and optimized receipts are under `review/`; the root package's
verification manifest invokes both independent modes through the isolated supplement runner.

## Open next questions and attribution

The useful remaining consumer task is to bind these external grid and state
radius estimates to the exact native caller's all-size private arithmetic,
owned arenas and tape tariff. That requires the actual representation,
copying, restoration and lifetime contracts. It cannot be inferred from a
smaller external bit count. Applicability to a successor pack chronology
also needs its own complete endpoint and error-schedule check.

Credit Ali Romman for the original direct-circulant consumer; Jose Manuel,
Vlado Vojdanovski and Chafik Boukhalfa for the retained compiler, recursion
and phase work; Nick Petalas for #4852's block-solve downset theorem; and
Brian/JoyboyBrian for the asynchronous cut, matching interpolation and
allocation refinements. Exact pins remain in the parent and compiler-cut
origin manifests. The new supplement reanalyzes the original allocation;
it does not claim #4977's allocation substitution again.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The author and reviewer were separate model task roles. Acceptance here
does not assert independent human peer review or proof-kernel verification.
Apache-2.0.

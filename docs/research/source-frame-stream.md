# Source frames on the smaller producer

The combined conditional witness is **κ = 1076678/10^12 = 1.076678e-6**,
above `2^-20`. This is `538339/812 ≈ 662.979` times the starting aligned-bit
value and about 39.85% above PR #13's `7699/10^10`.

It combines four independently checked ingredients:

- The h30 producer with selected splits, star resynthesis, and bilateral
  nested-wire reuse: **13,056,812 roles**, center loss **12,180**, no extra
  frame loss. The complete matching covers all 142,506 five-set labels.
- Eumemic's auxiliary source-frame move from
  [PR #13](https://github.com/CrocSwap/integer-mult-bounds/pull/13), pinned at
  `3ef246fa4f69c87ebfed78376418afa9ffcad145`.
- IceKylin's controlled projector batching and mixed-width transfer from
  [PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10), with
  PR #12's even-dimension bank matching.
- [Every complex residual batched](complex-all-residuals.md), supplying
  saving `4191487/10^12` and guard constant `3749/2500`.

## Why source relocation survives wire reuse

Every physical auxiliary still begins its scalar invocation at the common
local zero frame and finishes at the common local full frame. The allocator
changes only the number and internal paths of roles. In stage two these
boundaries are `D0=(B⊗F)⊗Q` and `D1=(A⊗F)⊗Q`, with dimensions `h²−h`
and `h²`. Set that auxiliary's source matrix to `P_D0` and its sink to
`I+P_D0`. Their difference is I. The source stream is interpreted as
`Phi_(-P_D0) f`; arbitrary dirty scratch is restored by the same scalar
network, so the physical output is `Phi_I f`. This logical interpretation
requires no extra tape operation.

The entrance rank becomes zero, and the exit matrix is
`I+P_D0−P_D1`, the projector onto `D0 ⊥ D1^perp`, of rank `m−h`.
The old entrance plus exit ranks were `(h²−h)+(m−h²)=m−h`, so the total
rank and deficit do not change. PR #13's simultaneous-basis existence
argument is independent of the producer DAG and applies at h30. The finite
control checks 57 original and nine new projectors under one h3 basis, plus
the actual h5 five-set label form. Those controls support the general
argument; they do not materialize a full h30 change-of-basis matrix.

With `m=27000`, `v=C(30,5)`, `R=13056812`, and `B=v²R`, the selected bit
recursive blocks are:

| Class | Multiplicity | Block width | Singleton corner pivots |
| --- | ---: | ---: | ---: |
| Stage 1–3 auxiliary join | B | 26880 | 60 |
| Stage 3 data entrance | 2v³ | 25142 | 929 |
| Stage 2 auxiliary exit | B | 26940 | 30 |

All other rank units remain singleton calls. Exact rational log enclosures
support **bit saving `2153359/10^12`**; the next grid point fails the
conservative moment bound. PR #13's complex saving `18/10^7` would now bind,
so the all-residual complex construction is needed for this composition.
The complex circuit remains at h28, with its original endpoints.

## Assembly and scope

Use `c=1`, `beta=1/1000`, `delta=10^-10`, and lambda/lambda-prime respectively
`10^-16` and `2·10^-16` above tau. Epsilon is the downward `10^-12` grid
rounding of `(1−delta)/(2+a_b)`. All 29 constraints and seven margins pass.
The minimum margin is `538339170276524048839/(5·10^26)`; its gap above κ is
`170276524048839/(5·10^26)`.

The scalar identities, exact output supports, nondegenerate frames, complete
physical allocation, matching, rank masses, and arithmetic inequalities are
checked. The general compiler, source-frame, basis, transfer, precision, and
inherited multiplication arguments remain mathematical dependencies. The
composition includes PR #10's corrected shifted Gaussian error enclosure.

Run the complete producer and composition without saved intermediates:

```sh
python3 scripts/source_frame_stream_network.py --workdir /private/tmp/source-frame-stream
```

Reuse a reproduced producer after source-hash validation:

```sh
python3 scripts/source_frame_stream_network.py --producer certificates/dimension30-stream-producer.json
python3 -m unittest discover -s tests -p test_source_frame_stream_network.py -v
```

The original PR #13 certificate reproduced exactly; pinned unmodified
sources and attribution are in `references/pr13/`. No earlier equal-frame
fusion savings are added to this different compiler.

# Auxiliary source frames (kappa = 7699/10^10 > 2^-21)

Contributed by eumemic with assistance from Claude (Anthropic). Builds on
icekylinx's bulk recursion (PR #10) and Zhihao Chen's ternary producers
(PR #7). The finite networks and every analytic interface are unchanged.

## Idea

PR #10 compiles a projector edge of rank above `m/2` as a few singleton
interchanges plus one contiguous interchange of its middle block. A block of
width `t` costs about `ln(m/t)` per rank unit, so a role is cheapest when
its rank sits in one large edge.

The transfer only needs `M_sink(rho(w)) - M_source(w) = I` for every role. An
auxiliary role (`rho(w) = w`) may therefore start in any fixed frame `M` and
end in `I + M`: the scalar network restores its arbitrary logical value, and
the physical output is `Phi_{I+M} Phi_{-M} f = Phi_I f`.

At stage two every auxiliary role first meets the frame `D_0 = B⊗F⊗Q`
(dimension `h^2-h = 756`) and last meets `D_1 = A⊗F⊗Q` (dimension `h^2`).
Starting it at `P_{D_0}`:

| edge | before | after |
| --- | ---: | ---: |
| entrance | rank 756, all singletons | rank 0 |
| interior climb | 28 | 28 |
| exit | rank 21168: 784 corner block + 20384 block | rank 21924: 28 singletons + 21896 block |

The exit `I + P_{D_0} - P_{D_1}` is the orthogonal projector onto
`D_0 ⊥ D_1^perp`. A generic member of PR #10's basis family puts its
`h x h` corner in general position (Lemma `lem:source-frame-basis`). The
rank sum and deficit are unchanged.

In the complex network, every residual can already be a whole child. The
stage-three data entrances (rank 21141, `2 v_c^3` copies) are added as a
third selected class. With `2*21141 > q = m + 6h`, the dependency-path guard
still sees at most one selected class per path. Its path moment is
`0.9620 < 0.999`.

## Numbers

| quantity | PR #10 | this |
| --- | ---: | ---: |
| interchange saving a_b | 246/10^9 | 154/10^8 |
| complex saving a_c | 7/10^7 | 18/10^7 |
| kappa | 6149999/(5*10^13) | 7699/10^10 |

Exact moment gaps are `> 4.69e-10` for the interchange and `> 3.89e-9` for
the complex network. All 29 parameter constraints and 7 assembly margins
are strict, with absorption gap `492299500001/(5*10^21)`.

## Checks

- `scripts/source_frame_network.py`: exact rank moments, guard and assembly.
- `tests/test_source_frame_network.py`: rank bookkeeping, and an exact
  `h=5` model of the stage-two frames in PR #10's coordinate order. In that
  model the exit is an idempotent of rank `m-h`. Under a random basis from
  PR #10's family, its lower-lower pivots are `h` corner pivots plus the
  diagonal block `(i,i)` for `h <= i < m-h`. The tests also cover exponent
  boundaries and manuscript labels and references.
- `scripts/make_source_frame_patch.py`: combined manuscript patch. The full
  patched manuscript compiles, with no undefined or duplicate references.

## Remaining levers

- Batching the stage-two data entrances (rank `729 > H/2` in the fast
  factor) gives about +3.5%.
- The interchange denominator is now dominated by the singleton climbs of
  the stage-one and stage-three auxiliary roles: `2h` climb plus the `2h`
  join corner. Contiguous corners or a cheaper side producer would reduce it.

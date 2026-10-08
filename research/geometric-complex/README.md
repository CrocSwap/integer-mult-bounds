# Geometric complex-network candidate for independent review

This research draft proposes a replacement finite complex network. Assuming
the retained upstream and compact-control interfaces, its parameter calculation
supports `kappa = 59/10^11 = 5.9e-10` in
`T(n) = O(n (log n)^(1-kappa))`. This is about 7.11 times the repository's
conditional exponent saving `83/10^12`; it is not a measured runtime speedup.

**Status: conditional, unreviewed research candidate.** The finite checks are
not a formal verification of the multiplication theorem. This proposal does
not integrate a new headline bound into the manuscript or supply a combined
manuscript patch.

The baseline is repository commit
`6e564879f51ae16f23d392e9e196c605f36d90df`, with pinned upstream manuscript
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. Start with the existing
[compact-control review guide](../../docs/research/compact-control-review.md)
for the inherited assumptions.

## Construction and proof

The [proof draft](geometric-note.tex) replaces separate side wires with shared
sum circuits for disjointness and intersection-two coefficients. Coordinate
envelopes label the disjointness circuit; fixed-pair orthonormal spans label
the intersection-two circuit. An additional binary label coordinate provides
a norm-one vector in the output and cleanup residuals. That coordinate is
charged in the motif arity `m = 26^3`; it is not free scratch or address space.
The reversible circuit must restore arbitrary auxiliary values.

At 25 ground points, the two circuits use 258,557 side roles per invocation.
The candidate complex saving is `4e-9`; the retained bit saving is `2.96e-9`.
The assembly's minimum margin is exactly `2956521/5000000000000000`, which is
strictly above the proposed `kappa`.

Review should focus on these implications in the proof draft:

1. Reversible embedding, role allocation, and cancellation with arbitrary
   initial scratch, including the reversed schedule and three-shear exchange.
2. Nondegeneracy and nonalternation of every physical residual in all tensor
   stages, including the output boundary and complemented reverse frames.
3. The phase factorization modulo four and common-frame telescoping into the
   permitted complex-network operator.
4. The charged wire count and rank sum
   `s = W*m - 2*N + 2*L`, and the resulting exact complex-saving inequality.
5. Integration with the retained complete-layer interface: uniform tape
   movement, local repairs, padding, recurrence, precision, analytic setup,
   and rounding. These general interfaces remain assumptions in this draft.

## Reproduce the finite evidence

Use Python 3.11 or newer, with assertions enabled, from the repository root:

```sh
python3.11 research/geometric-complex/verify.py
python3.11 research/geometric-complex/audit.py > research/geometric-complex/physical-audit.json
python3.11 research/geometric-complex/bit_screen.py
make verify
```

No additional Python packages are required for these research scripts.
The LaTeX source is standalone and uses standard mathematical packages.

Files:

- [explore.py](explore.py): finite circuit construction, exact counts, and
  rational parameter assembly.
- [verify.py](verify.py) and [certificate.json](certificate.json): full-size
  support and role-path checks, small exact scalar tests including dirty
  scratch, the missing-coordinate negative control, guard bounds, assembly
  margins, and source/dependency hashes.
- [audit.py](audit.py) and [physical-audit.json](physical-audit.json): all
  physical role paths in three tensor stages, both orientations, at ground
  sizes six and seven; constructive residual bases and 687,360 exhaustive
  active-factor address phase comparisons. This does not enumerate the
  full tensor address space at size 25.
- [bit_screen.py](bit_screen.py) and [bit-screen.json](bit-screen.json): 441
  bounded unequal-factor bit-network configurations; the retained `(50,50,50)`
  configuration wins this screen. No global optimality claim is made.

Before publication, the baseline `make verify` passed all 163 existing tests
and 17 manuscript patch applicability checks. The current proof source also
compiled successfully in the native LaTeX compiler. Existing upstream files,
historical certificates, patches, and the repository's headline are unchanged.

## Attribution and assistance

Restored auxiliary circuits and complement frames build on this repository's
incidence, DAG, and paired-bit constructions. Monotone disjoint-set summation
is established prior work; see Kaski, Koivisto, and Korhonen,
[Fast Monotone Summation over Disjoint Sets](https://arxiv.org/abs/1208.0554).
This finite construction uses its own dyadic support circuit rather than that
paper's asymptotic size bound. No claim of global novelty is made.

The research, proof text, programs, and verification were prepared with
substantial assistance from OpenAI Codex at Rohan Arun's request. Independent
mathematical review remains necessary. Contributions follow the repository's
[Apache-2.0 license](../../LICENSE).

# Deterministic equal-frame plateau refinement

## Parent and result

Parent: PR210, head `df95878d11190518e45ef9717c9ee05011f88ace`.
Its committed frame file has SHA-256
`687496f3c15818e7cad1beb5fdf3812b8e38825ea302bfd60aea7ac23f3516b4`.

The deterministic search accepts 14 moves affecting 19 operations. The frame
file hash changes to
`387ae1b5e69004426d094f4947b29c532d60fdf31f727f5e8830468278fe0f92`.
Moves are:

| Operations | Old dimension | New dimension | Count |
|---|---:|---:|---:|
| 18750 | 5 | 6 | 1 |
| 23544/23545, 23591/23592, 23638/23639, 23685/23686, 23732/23733 | 9 | 12 | 10 |
| 27900, 27904, 27908, 27912, 28052, 28056, 28060, 28064 | 13 | 14 | 8 |

The proposal objective is `sum d log(d)` over local rank increments. It is not
used as proof of improvement. The deterministic greedy search groups equal
frames linked by nesting, intersects each group's future frames, then accepts
only strict dimension increases passing exact subspace containment,
nondegeneracy and role-chain checks. No random seed is used. The complete
source/dirty scalar program and exact paid moments are checked by the package
verifier.

## Physical and exact price effect

The raw child-histogram delta is
`{1:-27, 2:-36, 3:+51, 4:-30, 7:+30, 8:-15, 9:-15, 10:+24, 11:-24, 12:+30, 15:-15}`.
Its weighted-rank delta is zero; child count falls by 27 per vertex. The final
normalized profile remains `m=72`, `W=438838`, rank mass `31549872`, deficit
`46464`, and maximum child `22`.

| Exact quantity | PR210 parent | Plateau candidate | Change |
|---|---:|---:|---:|
| Bit saving | `695265778339166/10^18` | `695270578321263/10^18` | `4799982097/10^18` |
| Conditional κ | `694782719690783/10^18` | `694787513005285/10^18` | `4793314502/10^18` |

The candidate κ simplifies exactly to
`694787513005285/10^18`. The bit side remains binding. The certificate
recomputes the unchanged complex profile and checks all 47 strict conditions;
the next `10^-18` grid point is rejected.

## Reproduction and scope

```sh
python3 -B research/coordinated-crossover-pr200/search/joint-plateau-search-prdf958.py --verify-committed
python3 -B research/coordinated-crossover-pr200/verify.py --temp-root /tmp
```

The first command regenerates and byte-compares the exact frame and search
record from `base-frames-prdf958.json`. The second additionally replays the
actual F2 and defining-integer scalar words, both orientations, source and
dirty restoration, all target paths, primes, charts and banks, complex lift,
two paid moments and 47 assembly inequalities. The deterministic command
passed locally; full scalar and repository CI verification are separate gates.

This is a frame-cost improvement inside PR210's physical construction. It does
not alter the scalar operations or any inherited all-size, compiler, routing,
prime, precision or analytic assumption. The conditional claim is not an
unconditional multiplication theorem.

Provenance: sennemmi with substantial OpenAI Codex assistance. This search
extends eumemic's PR210 head; upstream notices and licenses are preserved in
the package `NOTICE`.

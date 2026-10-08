# Aligned bit circuit with cheaper centers: conditional kappa = 1624/10^12

October 8, 2026. Contributed by eumemic, prepared with assistance from Claude
(Anthropic). Conditional on the pinned upstream interfaces, compact control,
the compressed complex network, fast Gaussian resampling and the written
center-frame argument. Not independently reviewed or formally verified.

- [Proof note (PDF)](../../artifacts/aligned-bit-note.pdf) and
  [source](../../notes/aligned-bit-note.tex)
- [Construction text](../../notes/aligned-bit-construction.tex)
- [Independent upstream patch](../../patches/aligned-bit-30.patch)
- [Exact certificate](../../certificates/aligned-bit-network.json)

## Why the bit network

After fast resampling, `g2, g3, g4 <= a_b min(epsilon, 1 - epsilon)`, so
`kappa < a_b/2`. The bit deficit per data element is

    eta_b = (v - 6 (central loss)) / (2 m (v + R)),

with `v = 19600`, `m = 125000`, `R` the auxiliary roles per invocation and
central loss `h^2 = 2500` per invocation. One unit of central loss is worth
about 640 side roles.

## Cheaper centers

Each center wire `C_i` used to gather all sources at the frame `D_1` and
scatter at `D_0`, losing `P (x) F` (dimension `h`). Now `C_i` is the role
carrying the group total `z_i = sum_{T contains i} x_T` out of the side
circuit. Its frame there is `D_{H_i}` with `H_i` the star span, of dimension
`h - 1`. The scatter still runs at `D_0`, so the loss is `h - 1`. In stage 2
the center rises to `D_1` at the scatter and falls to `D_{H_i^perp}` at the
reversed total, again losing `h - 1`. The central loss per invocation becomes
`h(h-1) = 2450`, and the numerator `v - 6h(h-1) = 4900` instead of 4600.

## Aligned side circuit

The paired recursion now uses the global blocks `{2k, 2k+1}` in every group,
with the partner of the common point as a singleton. At the top level, the
leave-one-block-out sums of the pair-star `{i, q}` are taken over the blocks
avoiding both `i` and `q`, by one prefix/suffix chain shared by groups `i`
and `q`, plus one group-specific triple. Side additions fall from 450,394 to
435,346, including the 50 group totals. With 58,800 partial outputs and 50
center roles, `R = 494196`.

## Result

    eta_b = 49/1284490000 > (325/10^11)(11737/1000),
    kappa = 1624/10^12, minimum margin g3 = 162446751/10^17.

The leaf needs `(1 - beta) a_c > 1 - lambda'` and the guard `beta > 3/4`;
`beta = 19/25` satisfies both with the compressed complex saving `14/10^9`.
A further 3% on `a_b` would close this window, so the next bit improvement
must come with a stronger complex saving or the sharper guard `C1 = 4 - 3 beta`
(available because `s_c < m_c^4`).

## Bounded search notes

Exact CP-SAT searches over center families of "triples inside Y" and
"star-in-Y" wires at `h = 8, 10` found nothing below `h(h-1)`. A rank
argument bounds any center loss below by about `h^2/6`, so the gap is open.
Block sizes 3 and 4 in the paired recursion were worse than 2.

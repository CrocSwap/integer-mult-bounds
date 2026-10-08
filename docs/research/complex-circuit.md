# Compressed complex network: conditional kappa = 59/10^11

The compact-control witness `83/10^12` was limited by the complex network,
which still used the original side wires: one wire per ordered neighbor pair,
`v*z_c = 3,693,800` per invocation at `h=25`, against `v = 2,300` data values.
This contribution computes the same side correction with shared sums.

- [Proof note (PDF)](../../artifacts/complex-circuit-note.pdf)
- [Construction source](../../notes/complex-circuit-construction.tex)
- [Independent source patch](../../patches/complex-circuit-31.patch)
- [Exact certificate](../../certificates/complex-network.json)

| | Original complex motif | Compressed side circuit |
| --- | ---: | ---: |
| Side roles per invocation | 3,693,800 | 108,195 |
| `W_c` | 58,645,352,620,000 | 1,741,801,270,000 |
| Certified `a_c = 1-sigma` | `418/10^12` | `14/10^9` (33.5x) |
| Headline kappa | `83/10^12` | `59/10^11` (7.11x) |

The bit network, compact-control movement, guard, Gaussian setup and
assembly are unchanged. Every new step is conditional in the same way as the
compact-control result: the upstream theorem's interfaces and the written
extensions are assumed, and nothing here is independently reviewed.

## 1. The side map and the circuit

Target `S` must receive `(1/2) * sum{x_T : T disjoint from S}` minus
`(1/2) * sum{x_T : |S cap T| = 2}`. Two cancellation-free families compute it.

- **Disjoint sums.** A recursive halving of the 25 ordered points computes
  triple sums avoiding up to three points. Cross terms between halves are
  pair sums in the link of each point on the other side, followed by
  leave-out sums over that point. Each target receives six pieces: the two
  half sums and the two mixed families, each split over the halves of its
  outer index.
- **Pair stars.** For each pair `{a,b}`, prefix and suffix sums of `x_abu`
  over the other points. Target `{a,b,c}` receives the prefix before `c` and
  the suffix after `c`.

Disjoint pieces are injected with weight `+1/2` and pair-star pieces with
`-1/2`. At `h=25`: 80,595 additions, 27,600 injected pieces, and
`R = c + q = 108,195` reversible roles, using the bit network's role compiler
and its transparent twelve-operation schedule (with signs).

## 2. The binary frame condition, and why pieces are split

Complex labels live in `F2^25` with the dot product. Every edge residual must
have an orthonormal basis, which for a nondegenerate binary space means it
must contain a vector of odd weight. The labels are:

- input `T`: the line `<t_T>`;
- disjoint-sum node: the coordinate space of its covered points;
- pair-star node: the span of its `t_abu`, which is already orthonormal.

The injection gate for `S` sits at the physical `Y` frame `t_S^perp`. If an
injected disjoint piece covered every point outside `S = {a,b,c}`, the
residual would be the plane `<e_a+e_b, e_b+e_c>`: nondegenerate, but all its
vectors have even weight, so it has no orthonormal basis. No relabeling
helps, since a nondegenerate space between `F_{outside}` and `t_S^perp` is one
of those two spaces. The construction therefore injects only pieces that
leave an outside point `y` uncovered; then `e_y` lies in the residual. If a
piece would cover everything, its two summands are injected instead. At least
four pieces per target are needed for this label class; the circuit uses six
disjoint and six pair-star pieces.

The reversed second stage uses orthogonal complements, as in the bit network.
Every reversed residual equals a forward one, so the same condition covers it.

## 3. Rank, phases and depth

Each side role runs monotonically from label `0` to the full space, so it
contributes exactly `m`; central and data roles are unchanged. Hence

    W_c = 2N + 3v^2 (R + h + 1) = 1,741,801,270,000
    s_c = W_c m - 2N + 2L_c     = 27,215,641,140,750,000
    eta_c = 28/205,789,375,  log m < 966/100,  a_c = 14/10^9.

The coefficient-depth bound needs only `total gates <= 12 W_c`: an invocation
has `4*82,895 + 4v + 4` gates, which gives `5.41e12 <= 2.09e13`. Gate
coefficients stay in `{0, +-1, +-1/2}`, so `E = 64(W_c+m+1)^3` and the
generalized guard apply with the new constants. Also `2 <= s_c < m^5`.

## 4. Parameters

With `sigma < tau` the compact-control internal exponent is `chi = tau`, so
the layer needs `lambda > tau` and `g3 = epsilon*(1-lambda') < epsilon*a_b`.
The witness uses

    tau = 1-296/10^11, sigma = 1-14/10^9, epsilon = 19999/100000,
    c = 999/1000, beta = 1/1000, zeta = 1/10000, delta = 1/10^6,
    C1 = 49961/10000, lambda = 1-2958/10^12, lambda' = 1-2956/10^12,
    kappa = 59/10^11.

The old `c = 1/5` would make `g2 = epsilon*c*a_b` binding. The spacing
exponent enters only through `epsilon(1+c) < 1`, `K/log p -> infinity`, and the
reserved-axis count `O(log d + d^(1-c) log p) = o(d)`. The minimum margin is
`g3 = 14779261/(25*10^15)`, above `kappa` by `29261/(25*10^15)`.

## 5. The next ceiling

With the published `h=50` paired bit network and the retained Gaussian margin
(`epsilon < 1/5`), `kappa < a_b/5 < 5.92e-10 < 2^-30`. The witness is above 99.6%
of that bound. The complex network now has spare saving (`a_c = 4.7 a_b`), so
the next improvement in this strategy must come from a stronger bit network
or a Gaussian step that permits larger `epsilon`. This is a scoped statement,
not a ceiling for other networks or algorithms.

## Verification

`python3 scripts/complex_network.py` regenerates the certificate. It checks
all 3,693,800 nonzero side coefficients and every zero, all 82,895 node labels
(nondegeneracy and odd-vector residuals on 188,790 inclusions), and all
108,195 compiled roles in both stage directions. The tests in
`tests/test_complex_network.py` cross-check the binary label algebra against
enumeration, reproduce the alternating-plane obstruction, run complete small
circuits (`h=8..12`) through dirty-scratch forward and inverse invocations and
the signed exchange, push every input basis vector through an `h=8`
invocation, and reject the witness with `c=1/5`, `epsilon=1/5`, or the old
complex saving. `scripts/make_complex_circuit_patch.py` produces the combined
patch; the patched manuscript compiles with Tectonic and no unresolved
references. These checks support the written arguments; they do not verify
the upstream theorem.

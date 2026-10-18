# Exact overcomplete decoders: a sharp outside-code rank budget

**Scoped algebraic result and exact examples. No copy-cost optimum, physical
supplier or new kappa.**

An exact all-pairs E8 decoder with `m` terms can spend at most `m-8` ranks
outside the live root code across its two factors. Write the projected residual
ranks as `s,t`. The complete feasible region is

```text
0 <= s,t <= number_of_live_roots - 8,     s+t <= m-8.
```

Every feasible pair is attained by a real decoder whose terms are all active.
At ten terms, a decoder with both factors outside the root code must therefore
have residual ranks `(1,1)` and factor ranks `(9,9)`. The proof gives its full
necessary-and-sufficient residual form in the original term coordinates:

```text
D = RA + u z^T,   T = RB + v w^T,
AB^T = 2I,       Bz = 0,   Aw = 0,   z^T w = 0,
R^T u = R^T v = 0,        u,v,z,w nonzero.
```

There is also a sharp field distinction for symmetric factors `D=T`. Over the
reals, every such decoder stays in the root code, whatever the term count.
Over the complex numbers with ordinary transpose, residual rank `s` is possible
exactly when `s <= min(n-8, floor((m-8)/2))`. The first escape uses ten terms:
`D=[RH | u | iu]` with `HH^T=2I` and `u` outside the root code.

[PROOF.md](PROOF.md) proves these statements for every full-rank real root
matrix and arbitrary real or complex coefficients. It applies elementary rank
algebra and isotropic cancellation; no novelty is claimed for those general
linear-algebra facts. Finite examples exercise the formulas and do not replace
the universal proof.

## Why this is useful, and what it does not do

PR1224 established the projection equations and the nine-term one-sided
restriction. This package makes the all-term-count rank budget sharp, including
active terms, and constrains the first unrestricted two-sided search to one
outside-code direction per factor. That reduces the search interface without
assuming coordinate readers or a fixed gate alphabet.

This is a **changed scope** from the revision-3 `complex-rank-shape-decoder`
card's physical synthesis target. PR1605 already supplies a rank-one reblocking
planning budget. Here, residual rank is neither a binary copy charge nor a
recursive child rank. The result does not meet the card's 5% construction gate
and supplies no favorable supplier invoice.

The explicit P112 symmetric example costs `(8,8,8,8,8,8,8,8,9,9)`, totaling
**82**. A real orthogonal term gauge preserves the identity but changes the
bill to **90**. This corroborates the known warning from PR1197 that term
normalizations need not preserve copy cost. The two extra terms cancel as
scalar matrices, but each is charged when retained; dropping them recovers the
ordinary eight-term decoder, with neither factor outside the root code.

Masked identities, arbitrary copy-cost minimization, physical frame paths,
source access, restoration, hosting, precision/tape, recursive moments and the
outer multiplication theorem remain outside scope. The selected construction
and every frozen predecessor file are unchanged.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/decoder-excess-rank
```

The registered commands are:

```sh
python3.12 -I -B research/decoder-excess-rank/verify.py
python3.12 -I -B research/decoder-excess-rank/independent.py
python3.12 -I -B research/decoder-excess-rank/test_verify.py
```

The primary replay checks 168 general and 32 symmetric complex examples on
P112 and P120, covering every feasible rank pair for 8 through 14 terms. All
terms are active. It checks **2,694,400** identity entries for those 200 examples,
recomputes factor/residual ranks with both Gaussian-rational elimination and
integer elimination of realified matrices, and extracts four ten-term residual
forms. Ten mathematical/source controls cover false Hermitian substitution,
real-positivity inference over complex coefficients, omitted copy charges,
cost-preserving gauges, coefficient corruption, residual coupling and pins.

`independent.py` imports neither the primary checker nor predecessor code. It
reconstructs the P112 roots and verifies the stored symmetric witness, its
rank-one isotropic residual, and both the 82- and 90-copy invoices using integer
arithmetic and a separate binary-rank implementation. It is a separate
implementation by the same assisted author, not independent human review.

Six test groups include all 256 two-by-two matrices over `{0,1,i,1+i}`, a
third determinant rank oracle, each ten-term equation, stored-witness
corruptions, source rejection before executable import, and optimized read-only
relocation of the standalone checker. `verify.py --write` explicitly regenerates
[RESULT.json](RESULT.json); default verification does not write it.

The registered replay and source pins establish this package's declared scope.
No selected-construction cold replay, native build, Lean proof, or independent
human review is claimed.

## Sources, overlap and credit

Started from main `ee055dc44815497927ef618fc985b93c2dcbda2a`. The task and
source bindings are in [TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).
The selected record is historical provenance. The only executable external
input is PR1077's hash-pinned Gaussian arithmetic/root module; PR1224 is a
mathematical predecessor, not an executable dependency.

- joaqcoo / [PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224),
  `00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162`: all-m projection equations,
  kernel pairing, the nine-term dichotomy and a ten-term two-sided example.
  We do not claim priority for two-sided ten-term existence.
- woklerx / [PR1077](https://github.com/CrocSwap/integer-mult-bounds/pull/1077)
  and themilkman216 / [PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968):
  exact E8 geometry, Gaussian arithmetic, and the ordinary-transpose convention.
  PR1077 already explains a different complex-isotropy pitfall at eight terms.
- Philipp / mightyOil / [PR1197](https://github.com/CrocSwap/integer-mult-bounds/pull/1197),
  `a0935afff6cc5540a582c5881bc8d5f98b587357`: fixed-coordinate two-total
  obstructions and the prior gauge/copy-cost warning.
- Sagar Thakrar / [PR1327](https://github.com/CrocSwap/integer-mult-bounds/pull/1327),
  `0462379659388acdb271f2e769986475d8a0646c`: a different, fixed parity-lift
  alphabet with a copy-cost census. No such census is repeated here.
- DreamingOfClouds / PR717 and PR446: the decoder and separate-term copy model;
  Douglas Colkitt / PR1240 and Arham Tahir / PR1605: rank-shape planning context.

The entry overlap snapshot covered 732 open PRs, including bodies and drafts,
253 discussion/comment records, and 347 local records, with complete reported
remote pagination and no warnings. The final refresh is recorded in TASK.json.
These searches do not establish novelty and do not cover every code diff.
Coordination: [Discussion 1622](https://github.com/CrocSwap/integer-mult-bounds/discussions/1622).

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in proof, code, checking and writing. No subagents or independent human review.
New material is Apache-2.0; predecessor attribution is retained.

## Open next questions

Can a two-sided ten-term decoder in the rank-one residual form lower the P112
copy bill below 64? A first step is a support-aware search in the **original
term coordinates**, enforcing all four equations and charging all ten support
pairings. The blockers are the unrestricted coefficient/support search and
physical realization; the term gauges used in the existence proof cannot be
assumed cost-preserving. This question and its relevance are also recorded in
TASK.json.

# A sufficient caller grid for the complete QQ16 native decoder

The complete word in [PR2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540)
leaves precision and hosting open. This package proves a local precision
contract for **all 2,463 declared events of that unchanged word**, at every
positive payload tensor depth `lambda`:

- Entry components on `2^-f Z` stay on `2^-(f+4lambda+3) Z` at caller boundaries.
- If every real and imaginary entry component has magnitude at most `H`, every
  caller component has magnitude at most
  `H*(48+48*2^ceil(lambda/2)+144*2^(4lambda)) < H*2^(4lambda+8)`.

At `lambda=1`, these are seven extra fractional bits, a triangle envelope of
`2448H`, and twelve magnitude guard bits above a strict input power-of-two bound.
The all-layer theorem follows from the written quadratic-phase argument and
finite prefix inequalities, not extrapolation from sampled tensor depths.

This assumes exact atomic native children and exact cover maps. Entry bounds
are required for the sixteen earlier F0 arrays, 224 current B1 arrays, and
owned-buffer dirt at their respective entry times. Treating the 240 temporal
source arrays as independent gives a sufficient relaxation for actual F0/B1
trajectories. It does not establish their entry bounds or charge the inherited
B1 execution again. Child interiors, approximate-child errors, stream/tape
movement and all-size supplier admission remain outside this result.

## Proof and evidence

[PROOF.md](PROOF.md) derives the physical phase `F-gS` for each retained logical
term, using the actual owner action and source frame. A mod-four quadratic
phase of binary polarization rank `r` has Gaussian component denominator
`2^ceil(r/2)` and real-component box gain `2^ceil(r/2)`. Under `lambda` tensor
layers its rank becomes `r*lambda`; the scalar coefficient stays unchanged.
Euclidean unitarity alone does not give the required componentwise bound.

The authenticated original replay is instrumented with a read-only observer.
It retains every original event, original endpoint/restoration assertion and
all twelve original controls. The scan checks 2,697 changed-field boundaries,
82,831 terms and 3,321 relative phase operators. Only ranks 0, 1 and 8 occur;
their maximum scalar denominator debts are 2, 2 and 3. Exact finite inequalities
for every row prove the common envelope for all positive tensor depths.

[RESULT.json](RESULT.json) records a prefix-table digest and explanatory
witnesses. The `1/128` coefficient at event 2062 is a **single operator-term**
witness against a six-bit term certificate. Other terms can cancel it; it is
not a lower bound on the full field or on correlated F0/B1 trajectories.
Likewise, `2448H` is a triangle bound, not a claimed attainable maximum. Eleven
magnitude bits fall below this particular certificate, which does not prove
that every implementation needs twelve.

[check_phase.py](check_phase.py) independently sums Fourier coefficients for
all 548 mod-four quadratic forms through three variables (4,232 coefficients),
and the complete 256-coefficient C8 kernel. Controls distinguish odd diagonal
and even cross-term polarization, real-box gain from Euclidean norm, tensor
cancellation from multiplying component denominators, and term debt from
scalar denominator alone. [integrity.py](integrity.py) checks a Git-free export,
three pre-execution source corruptions, and a bool/int receipt mutation under
optimized Python.

## Reproduce

Use standard-library CPython 3.12 from the repository root:

```sh
python3.12 scripts/research_package.py --package research/qq16-caller-grid-reserve
```

The registered commands run the exact predecessor replay, the independent
Fourier checker, and export/integrity controls. Source authentication occurs
before retained code import. [SOURCES.json](SOURCES.json) pins seven live inputs;
[SNAPSHOTS.json](SNAPSHOTS.json) pins 23 byte-exact files at PR2540 head
`630d557af5088f66b45c447969cee9576600e50b`, including its predecessor chain.
No source archive, selected record or predecessor word is modified.

## Scope and credit

The new result is a sufficient, source-bound local precision contract. The
224 rank-one children, sixteen rank-eight children, 480 wrappers, 208 cover
maps, 224 restored borrowed arrays and 17,472 scalar primitive allowance are
unchanged predecessor results. No improved invoice or exponent is claimed.
Exact caller rounding at the stated boundaries is a no-op, so the retained
exact endpoint/restoration result survives that rounding policy. This does
not justify rounding inside a recursive child.

Credit to Ali Romman and the retained QQ16 lineage for the source, cover
action and tensor convention; to ywz65's PR2511, PR2512 and PR2540 for the
retained native decoder and checks; and to thakrarsagar/PR2470 and
starship-s/PR2443 for the L2 and F0/cut reconstruction. Original files and
attribution remain unchanged. The Fourier and Gaussian-dyadic identities
are standard elementary facts; their application to the complete literal word
is the contribution here. Prepared by ywz65 with substantial OpenAI Codex
assistance in derivation, implementation, writing and review. Separate agent
review is not independent human review. Apache-2.0, under the repository license.

## Open next questions

Structured questions and the selected task card are in [TASK.json](TASK.json).

1. Can actual F0/B1 entry bounds and approximate native-child errors be composed
   with this caller reserve? Begin with one rank-eight child and track its full
   forward/return rounding error; the current theorem assumes exact outputs.
2. Can exact aggregation of same-source owner maps lower the conservative
   triangle envelope? Begin with event 1717, where the saved row certificate is
   largest. Coincident owner/address contributions and correlations matter.
3. What fixed-tape layout implements the complete word at this width? Bind all
   early/current/output owners and charge movement, retention and cleanup.
   A format bound alone supplies none of that physical invoice.

# Native admission after a productive completion deletion

This note gives two sufficient assembly lemmas and an exact, portable arithmetic checker. It does not exhibit a new complex provider or assert a new κ. The native caller construction is inherited from PRs [4630](https://github.com/CrocSwap/integer-mult-bounds/pull/4630), [4635](https://github.com/CrocSwap/integer-mult-bounds/pull/4635), and [4713](https://github.com/CrocSwap/integer-mult-bounds/pull/4713). The productive partial-helper deletion principle is motivated by [4760](https://github.com/CrocSwap/integer-mult-bounds/pull/4760), whose implemented result is BIT-only. The lemma below applies to the complex interface only when its stated physical conditions are proved for an actual complex word.

## A constructive completion-elision lemma

Fix 0 < q < 1 and θ = 1 − q. Let a source-bound provider have a canonical independent productive field of active-axis rank r+s, obtained as follows: its prefix has already produced an admitted canonical rank-r target, and a terminal paid rank-s completion changes only that field to the admitted rank-(r+s) target. Here r and s are active-axis counts and hence the width parameters used in the moment equation. They are not the entry count of the entire address array: inactive tensor factors still belong to the physical field and remain accounted for. Assume:

1. Every original independent input remains arbitrary. All required other outputs and borrowed owners are preserved by the prefix.
2. The retained rank-r endpoint has an explicit permitted all-width address/phase adapter, with known precision and storage costs. This is not an assumed Gaussian recovery oracle.
3. The deleted completion has no later use. Any subsequent scalar contacts that are removed or commuted have an independently proved schedule preserving the whole physical state.
4. The retained outputs are jointly independent under an explicit two-sided input/output change of basis admitted by the caller. Support confined to initially zero auxiliary fields alone does not establish this condition.

Deleting the terminal completion is then an executable provider specialization. Its paid inventory loses one rank-s query and its productive inventory replaces one rank-(r+s) field by one rank-r field. All nonzero additional paid adapters must be included separately. The normalized native caller admits this changed mixed inventory under the same inherited mixed-width theorem, with the new smallest productive width used in its stopping and uniformity estimates.

To prove the quantitative gain, set R = max(r,s), t = min(r,s). Concavity gives

    (R+t)^θ − R^θ ≤ θ R^(θ−1)t ≤ θ t^θ.

Thus the unnormalized productive-minus-paid moment improves by

    r^θ + s^θ − (r+s)^θ ≥ q min(r,s)^θ ≥ q.

For a rank-8 target retained from a rank-9 target after deleting a paid rank-1 completion, the exact gain is 8^θ + 1 − 9^θ. For disjoint deletions these gains add. Subtract the moment of every newly introduced paid query; only a strictly positive resulting complete-source margin proves an improvement at the old exponent. Physical conditions, inherited contraction hypotheses, and source funding are not established by this scalar inequality.

## Explicit sufficient native parameter selection

Assume a complete, uniform, source-bound complex provider with exponent q_C > 0. Its admission includes all-column canonical independent endpoints, absolute phases, physical owner restoration, all-width lifting, a uniform finite source program, and the inherited precision, Gaussian, recovery, mixed-width and compiler theorems. Let c = 3/32, the retained boundary-algebra cap. Every κ with 0 < κ < min(q_C,c) is admitted by the existing native caller.

Here is a constructive parameter choice, using rational arithmetic whenever the inputs are rational:

    q = (κ + min(q_C,c))/2
    δ = min(1/100, (q−κ)/(4(q+1)), (c−q)/16)
    ε = 1−δ, β = 1−3δ, spare = δ/10, layout = δ/100
    ξ = ε(1+q)−c+layout
    stop = (q_C−q)/(2q_C).

The provider stopping margin is q_C(1−stop)−q = (q_C−q)/2 > 0. The nine native savings are, in caller order:

| Row | Saving |
|---|---|
| Main transform | εq |
| Standalone routing | 1 |
| Fused Gaussian | 1−ε+qβ |
| Standalone addressing | 1 |
| Group scans | 1−ε+β |
| Boundary algebra | c+ξ−ε |
| Sparse visits | 1/2+ξ−ε |
| Record products | ε |
| Core-face recovery | 79−ε−β |

The main row exceeds κ since δq ≤ (q−κ)/4. The boundary row equals εq+layout. The sparse row exceeds it by 1/2−c. The fused row is q+δ(1−3q) > q, since q < c < 1/3. The other rows exceed κ because δ ≤ 1/100 and κ < c. All guards are strict: 0 < β < ε < 1; 1/2 < ξ < ε; the key and membership margins are 2δ and δ; the global-gamma margin is 9δ/10; and the chirp margin is 2(c−q)+δ(122/25+2q). Thus all fixed polylogarithmic overheads in the retained construction are absorbed by positive asymptotic slack.

The conclusion is normalized native Word RAM multiplication O(n/(log n)^κ), with fixed sufficiently large word-width constant w = C log n, the retained packed representation, explicit rounding/guard bits and owned storage. This does not assert a new bit-model exponent by adding a packing factor. A fixed finite exceptional input range is handled by an ordinary direct multiplication routine. The bound transfers the proved provider exponent; changing the nine-row parameters alone cannot exceed q_C.

## Replay and evidence boundaries

Run `python -I -O -B test.py --expected EXPECTED.json` in this directory. It checks 570 rational caller parameter cases, the pinned complex-provider arithmetic, 162 exact integer-root enclosures for the concavity gain, and eight rejection controls. It also validates inventory updates on a synthetic terminal-completion fixture. Fixture flags are supplied proof obligations, not a physical-source verifier. The receipt explicitly records `actual_new_complex_elision_exhibited: false` and `new_kappa: null`.

To admit a separately proved candidate exponent, run `python -I -O -B test.py --provider P/Q --target R/S`. This certifies only the caller inequalities. It never supplies the missing physical provider proof or changes source records. The public provenance is in `SOURCES.json`; no private source tree is needed to replay the arithmetic.

## Predecessor credit

The current complex profile is Cao Yifan’s PR #4610, with the retained Cinna Davis / #4470 joint-helper lineage and its source notices. Credit ai-nanachi’s #4760 for the implemented BIT productive-partial-helper improvement; this note does not transfer its BIT arithmetic into complex arithmetic. The native assembly retains Dugongue’s #4630 / #4554 arithmetic and construction, Jacob Alan Sussman’s integer matching, zxv’s chronological compiler and majorants, Dillon’s critical-root criterion, Ryanson Jonathan’s mirror windows and checks, Vlado Vojdanovski’s tensor/phase-cell fusion, Chafik Boukhalfa’s fine prime padding with Tim Trudgian’s estimate, and Harvey–van der Hoeven’s analytic multiplication foundations. Exact inheritance is scoped to the source pins, not independent reverification of all those mathematical results.

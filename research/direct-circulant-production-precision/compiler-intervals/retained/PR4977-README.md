# Bind the block-solve envelope to the rounded Full allocation

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.

## Result and exact boundary

Nick Petalas's `downset-block-solve-bound` gives the ideal completed-call
common spectral envelope `2 sqrt(N) (Lambda Q)^2`, and explicitly leaves its
rounded Full-factory substitution open. This package performs that substitution
through a one-expression, source-authenticated allocation adapter. Frozen
`rational-unitary-fft/full.py`, its compiler and every predecessor remain intact.
The uniform implication below retains the stated block-solve theorem and the
predecessor generator's local fragment/rank contracts as dependencies.

Let N=2^d, Lambda,Q,R>=1, target t>=1 and incoming precision F0>=0, under the
original component-guarded Full admission contract. Set chi=Lambda Q and

```
B = 2 * 2^ceil(d/2) * chi^2.
```

Then `2 sqrt(N) chi^2 <= B <= 2 sqrt(2N) chi^2`. Also B dominates 1, Lambda
and Q. Use this B in place of `256 N^3 chi^12` in the original allocation,
leaving every other expression and check unchanged. The resulting actual
factory has the same retained forward and stored-inverse error target `2^-t`
at complete matching-layer boundaries. No new selected kappa or physical
preparation/delivery bound is claimed. This is not the sublayer interpolation
contract being studied in the separate `matching-sublayer-norm` contribution.

## Every affected implication

Put J=3N-2, tau=2^-t, and take

```
s = t + ceil(log2(4 J B^3 (R+1))),   eta=2^-s,
theta = J B^2 eta.
```

The ideal completed-downset theorem is valid for every legal atom ordering.
For its prefixes Q_j and the approximate atom errors E_j, conjugated defects
`G_j=Q_j^-1 E_j Q_(j-1)` have sum of norms at most theta. Thus

```
theta <= tau/(4 B (R+1)) <= 1/16 < 1/4,
eta <= 1/(2Q),
e = 2 J B^3 eta <= tau/(2(R+1)).
```

Products of `I+G_j` have norm at most exp(theta)<2, and inverse products
have norm at most `1/(1-theta)<2`. Their distance from identity is below
`2 theta`, using exp(theta)-1<=2theta and theta/(1-theta)<=2theta on this
interval. Apply the same estimates to a contiguous suffix of the normalized
interaction factors, rather than multiplying two independently bounded
prefixes. All approximate completed prefixes and their inverses have norm
at most 2B; remaining suffixes and their inverses have norm at most 2L0B,
where L0=max(1,Lambda,Q). Both endpoint operator errors are at most e.
The inverse reference is the mathematical inverse of the unchanged ideal T;
it is not an independently rounded inverse coefficient table.

For U=Lambda+Lambda^2 Q, let H be the predecessor's maximum of its generator
fragment allowance, U+1 and 2Q. Generator parameters, exact displacement/rank
bounds and polynomial H are unchanged. Although their requested accuracy is
smaller, every child still receives its full requested coefficient accuracy;
the existing child allocation is recomputed from s. For a scalar leaf a,
`|a|>=1/Q` and `|ahat-a|<=eta<=1/(2Q)` imply `|ahat|>=1/(2Q)` and direct/inverse
fragment bounds U+1 and 2Q. Inversion always uses the same stored ahat.
The physical-cut trace therefore gives the same formula

```
K = 2 L0 B H,    segment <= K^2.
```

Let D be the original layer bound and choose

```
F=max(F0, t+ceil(log2(2 D K N))).
```

Nearest component rounding contributes at most N 2^-F per layer. Its propagated
endpoint error is at most D K N 2^-F <= tau/2. The coefficient charge is
`e R <= tau R/(2(R+1)) < tau/2`, hence the total is strictly below tau.
The same proof applies to the reversed stored program on its own input;
no exact rounded forward/inverse round trip is asserted. Intermediate
amplitude is bounded by `A=K R+D K^2 N 2^-F`, using the segment bound.
Consequently the original integer-bit and temporary-bit formulas remain valid.

For scalar height, the unchanged pivot upper bound U and precision s give
`2s+2ceil(log2(U+2))+8`; actual generator coefficient heights are still
maximized after building the plan. Their original phase/multiplier recipes
are used, not stale heights from the old allocation. All quantities remain
polynomial in N,Lambda,Q,R before logarithms, preserving the original
`O(F0+t+log N+log Lambda+log Q+log R)` online-width conclusion.

## Executable adapter and independent checks

`allocation.py` authenticates exactly the original AST assignment to B,
replaces only that assignment in a private function, and compiles it with the
original exact helpers. All validation, output fields and subsequent formulas
are retained byte-for-byte at the AST level. The live Full factory and frozen
source files are not edited. The verifier authenticates every declared source
before imports and constructs actual plans with the adapted allocation.
It independently derives every affected formula and checks actual exact and
rounded forward/stored-inverse endpoints, source grid and word widths.
The written proof establishes the uniform implication; finite execution
binds it to the actual source and exercises error controls.

## Attribution and remaining scope

Credit Nick Petalas for the block-solve `2 sqrt(N) chi^2` theorem, Brian's
PR4788 for the earlier leading-section/downset bridge, Jose Manuel/jmbarrancoml
for rational Full, its all-size allocation and rounding proof, Vlado/PR1673
for the recursive/displacement compiler, Chafik/PR628 for certified phases,
and the retained Stein and interval source contributors. Orthogonal block
estimates, Schur formulas and perturbation inequalities are background.
Author-process checks do not constitute independent human or proof-kernel
acceptance. Tape cost, physical coefficient preparation/delivery and the
complete multiplication theorem remain separate.

## Open next questions

Can a downstream normalized/raw Gaussian caller use the smaller actual Full
word widths while preserving immutable reference and intermediate-radius
contracts? Begin by threading this exact allocation receipt through one
normalized `Gaussian` instance and auditing its requested child grid. The
present Full contract is complete at its own boundary; the outer wrapper and
physical cost claims require their own source-bound proof.

## Reproduction and evidence

Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19138298

The fixed replay checks 63 allocation contracts (N from 1 through 2^20), then six actual Full factories and 24 rounded forward/stored-inverse trajectories. Cases include a complex scalar, a 2^-30 pivot, non-Hermitian complex N=2/N=4, a nonzero 512-bit input grid and zero-duration shears. At complex N=4 the source emits 189 layers, child precision falls 72 to 26 bits and data precision 76 to 61 bits; at complex N=2 these fall 82 to 28 and 72 to 54. A 512-bit incoming grid remains 512. These are fixture measurements, not a universal constant saving. Seven controls cover source-expression drift, invalid types/dimension, a rounded-zero pivot, wrong inverse ordering and an underfunded actual data grid.

```sh
/opt/local/bin/python3.12 -B scripts/research_package.py --package research/full-downset-allocation
python3 -B scripts/check_research_commit.py --package research/full-downset-allocation --check-source-history
```

The registered normal and optimized commands require CPython 3.12 and only the standard library. The local interpreter path above is environment-specific; the registered hook resolves its declared Python version. The source-history command follows committing. Official committed exports can run verify.py directly with -I -W error -B, and separately -O, without Git or a network. Automated execution is not independent human or proof-kernel acceptance. Hosted CI is unverified at publication.

Base b91956876e5b4122fd89179f1b57557ff8378f15, priority revision 7. Fresh entry overlap covered 317 open PRs, 4064 Discussion records and all 6636 current-base local notes at 04:46–04:47 UTC. The scoped searches found the named explicit predecessor obligation; unpublished work, arbitrary closed histories and every historical diff are not covered. This is advisory coverage, not a novelty certificate.

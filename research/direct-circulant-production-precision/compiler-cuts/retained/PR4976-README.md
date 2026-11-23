# Numerical bounds inside a matching layer

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.

## Result and scope

The physical-cut trace audit `full-toeplitz-cut-audit` explicitly leaves the
numerical contract at a proper subset of a matching layer open. This package
supplies a dimension-independent interpolation lemma for all four operators:
prefix, suffix, inverse prefix and inverse suffix. It binds the lemma to the
actual retained rational FFT and Toeplitz-shear gates. It changes no frozen
factory or selected exponent.

Let the complete layer be an invertible block diagonal operator G on disjoint
coordinate supports. Choose any subset of its complete gates, let E be the
orthogonal coordinate projection onto their supports, and let H be their
product, identity elsewhere. Then

```
H = E G + (I-E),   H^-1 = E G^-1 + (I-E),   EG=GE.
```

For the adjacent complete-layer prefixes P0 and P1=G P0 and suffixes
S0=S1 G, the cut inside this layer has P=H P0 and S=S1 G H^-1. Exactly,

```
P    = E P1 + (I-E) P0,
P^-1 = P1^-1 E + P0^-1 (I-E),
S    = S0 (I-E) + S1 E,
S^-1 = (I-E) S0^-1 + E S1^-1.
```

The order matters; the projection need not commute with any prefix or suffix.
All products act on columns and the most recent gate multiplies on the left.

## Quantified norm proof

For orthogonal output projections, the two summands' squared output norms add.
For orthogonal input projections, use the triangle inequality followed by
Cauchy–Schwarz. Thus if the two neighboring operators of any one of the four
types have norm at most a and b, the partial-layer operator has norm at most
`sqrt(a*a+b*b)`. In particular a common complete-layer bound F becomes
`sqrt(2) F`. This proof holds over C for every dimension and every finite
matching, including identity gates, empty/full selected subsets, and unused
coordinates. It does not split an individual gate's internal arithmetic.

There is no valid generic zero-loss interpolation rule. For integer m>=4 use

```
P0 = [[m,0],[1,1/m]],     G = diag(1/m,m),
P1 = [[1,0],[m,1]],      H = diag(1,m).
```

Every complete boundary of the two-layer program P0;G, including its prefix,
suffix and both inverses, has norm at most `m+2` (their squared Frobenius
norms suffice). But `H P0` maps e0 to `(m,m)`, of norm `sqrt(2)m`.
For m>=5 this exceeds m+2, and its ratio to that common valid envelope tends
to sqrt(2). Consequently the generic factor sqrt(2) is sharp, even when the
four complete-boundary contracts are provided together. The witness uses two
disjoint scalar gates, so the complete-layer matching premise is preserved.

## Consequence for the retained generator and Full caller

The retained `GENERATOR-PROOF.md` complete-layer fragment bounds and the exact
physical-cut trace remain explicit inputs, rather than results re-proved here.
Apply the lemma separately to each actual local microprogram. A child with
four complete-layer bounds H has four arbitrary-matching-subset bounds
`sqrt(2)H`, with rational safe envelope `2H`. Active atoms have disjoint
supports, so their direct sum contributes the maximum such bound, without
multiplying by the number of active atoms.

In FULL-PROOF.md (14), complete-layer `K_phys=2 L0 B H` therefore becomes
`sqrt(2) K_phys` at these added sublayer cuts; `2 K_phys` is a rational safe
choice. Arbitrary segments between two added cuts have bound `2 K_phys^2`
(or rational safe `4 K_phys^2`). If one keeps the predecessor's data-rounding
count and only doubles the suffix propagation envelope, one extra data bit
preserves its rounding allowance. This is an implication, not an installed
precision change or a claim covering extra rounding events. Rounding inside a
gate, asynchronous overlapping gates and changed non-coordinate layouts need
separate contracts.

## Verification and attribution

The written proof establishes the quantified result. The standard-library
checker uses exact Gaussian-rational scalar representation from Jose Manuel's
retained implementation; its matrix multiplication, inverse, PSD tests and cut
oracle are local. It checks all four identities and independently certifies
norm bounds at actual FFT/shear cuts and at nonunitary complex synthetic cuts.
Wrong projection sides, overlapping supports and a missing interpolation loss
have discriminating controls. Counts and commands are reported after replay.

Credit Jose Manuel/jmbarrancoml for rational FFT/Full and numerical fragment
contracts, Vlado Vojdanovski/PR1673 for the matching scheduler, Chafik
Boukhalfa/PR628 for certified phases, and Brian/JoyboyBrian's physical-cut
trace audit for the explicit sublayer question. Original source notices remain.
The orthogonal row/column mixing inequality is elementary background; this
contribution is its four-way source-bound application and quantified interface
consequence, without a literature-priority claim.

## Open next questions

Can the retained primitive alphabet improve the generic sqrt(2) loss?
Start with its unitary butterflies and compensated shear layers, retaining the
same actual neighboring operators. The sharp generic witness need not belong
to that alphabet. A better bound would reduce added sublayer headroom, but
physical preparation, storage, tape and full supplier admission remain open.

## Reproduction and evidence

Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19138297

The fixed replay covers 97 cuts, including 52 proper sublayer cuts, 388 exact four-way identities and 388 independently PSD-certified partial-cut norm inequalities. Actual retained FFTs at widths two/four and a complete dirty Toeplitz shear contribute 73 cuts; the other four fixtures cover sharp nonunitary and complex controls. Six controls distinguish missing loss, wrong projection sides, overlapping supports and a complex adjoint norm failure. All checks use explicit exceptions and remain enabled under -O.

```sh
/opt/local/bin/python3.12 -B scripts/research_package.py --package research/matching-sublayer-norm
python3 -B scripts/check_research_commit.py --package research/matching-sublayer-norm --check-source-history
```

The registered normal and optimized commands require CPython 3.12 and only the standard library. The local interpreter path above is environment-specific; the registered hook resolves its declared Python version. The source-history command follows committing. Official committed exports can run verify.py directly with -I -W error -B, and separately -O, without Git or a network. Automated execution is not independent human or proof-kernel acceptance. Hosted CI is unverified at publication.

Base b91956876e5b4122fd89179f1b57557ff8378f15, priority revision 7. Fresh entry overlap covered 317 open PRs, 4064 Discussion records and all 6636 current-base local notes at 04:46–04:47 UTC. The scoped searches found the named explicit predecessor obligation; unpublished work, arbitrary closed histories and every historical diff are not covered. This is advisory coverage, not a novelty certificate.

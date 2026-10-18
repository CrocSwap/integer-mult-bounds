# Heterogeneous rank-six block: exact local tensor, no selected placement

**Outcome: partial construction. No conditional bound or new \(\kappa\) is claimed.**

## Result

Consider the bilinear map over \(\mathbb C\)

\[
F(x,y)=\bigl(x_0y_0,\ x_0y_1+x_1y_0,\ x_2y_2,\ x_3y_3,\ x_4y_4\bigr).
\]

The first two outputs have a three-product decomposition
\(u=x_0y_0, v=x_1y_1, w=(x_0+x_1)(y_0+y_1)\), with outputs \((u,w-u-v)\).
The other three outputs use one product each. This gives six rank-one atoms for the
heterogeneous block \((3,1,1,1)\to6\).

The tensor rank is exactly six. The five output slices span the matrices

\[
\left\{\begin{pmatrix}a&b\\b&0\end{pmatrix}\oplus\operatorname{diag}(c,d,e):a,b,c,d,e\in\mathbb C\right\},
\]

a five-dimensional space. A rank-one matrix in this space cannot mix the leading
two-by-two block with the last three diagonal coordinates. The leading block has
determinant \(-b^2\), so its only rank-one direction is \(E_{00}\); the other
rank-one directions are \(E_{22},E_{33},E_{44}\). Thus rank-one matrices in the
slice space span only four dimensions. If a five-atom decomposition existed, its
five input rank-one matrices would have to span the five-dimensional slice space
and therefore lie in it, a contradiction. The six-atom identity is consequently
minimal.

The implementation updates an arbitrary dirty target by \(p\leftarrow p+F(x,y)\);
subtracting the same output restores \(p\). Inputs and private scratch remain
unchanged. The certificate records exact rational fixtures and omitted-atom
negative controls.

## Moment-only screen and bounded source check

The selected per-call profile pinned in `SOURCES.json` is
\(n_1=2412,n_2=418,n_3=432,n_4=142,n_5=82,n_8=8\), with rank mass 5586.
Hypothetically replacing each rank-three plus three rank-one group by one rank-six
child changes the profile by \((-3,-1,+1)\) at ranks \((1,3,6)\), preserving rank
mass. The exact screen considers only \(0\le k\le432\) blocks and an assumed extra
tariff of \(e\in\{0,1,2\}\) rank-one-equivalent units per block. Relative to the
selected ceiling, the 5% target first passes at 135 blocks for \(e=0\), and at 284
for \(e=1\); \(e=2\) fails throughout the domain. These are exact moment-model
thresholds, not a realized profile.

The pinned `upstream1087.tar.gz` provider stream was checked only in phase A. That
phase has 4,730 events and 992 climb records: 936 rank one and 56 rank four, with
no rank-three climb. Therefore this direct-record block has no candidate placement
in phase A, and endpoint-frame analysis was not warranted there. This bounded
observation says nothing about other phases, composite rank-three realizations,
or a different source schedule. The provider archive's event histogram is also
distinct from the selected paid per-call profile above.

No source-compatible occurrence has been established. The moment screen does not
price actual copies, frame transitions, precision, hosting, or inverse restoration;
the tested rank-one-equivalent tariff is only a parameter. No supplier admission
or \(\kappa\) change follows.

## Reproduce

From the repository root, the registered replay requires Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/complex-mixed-rank6-block-seedc8d6 --check-only
python3.12 scripts/research_package.py --package research/complex-mixed-rank6-block-seedc8d6
```

The package replay verifies the exact tensor identity, rank lower bound, dirty
state contract, rational fixtures, rejection controls, exact profile thresholds,
and the pinned phase-A event histogram. `python3 scripts/research_package.py ...
--check-only` validates metadata and source pins only; it is not a mathematical
acceptance check. The certificate is `CERTIFICATE.json`.

## Open next questions

1. Can another selected phase or composite operation realize this tensor with
   compatible source/output frames? The first bounded follow-up is the pinned
   phase B stream, with frame and register constraints derived before placement
   search.
2. For any compatible occurrence, what is the complete copy, frame, precision,
   hosting, and restoration bill? It must be measured before applying the ceiling.

The original narrow claim is [Discussion #1166 comment 18923483](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18923483); the result handoff is [comment 18923691](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18923691). The focused package PR is [#1866](https://github.com/CrocSwap/integer-mult-bounds/pull/1866).

## Credit

Prepared by Cinna / commdata2338. New work is Apache-2.0. The selected record,
review, source manifest, and provider archive are pinned in `SOURCES.json`.
Substantial OpenAI Codex assistance in scope selection, cost screening, tensor
construction, verification code, and package writing is disclosed in `TASK.json`.

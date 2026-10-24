# Owned nonmonotone contacts with shared late native maps

This is an exact rank/invoice model with optional floating discovery. It
combines changes that the earlier owned common-kernel prototype separated:
nonmonotone persistent contact transports, eight variable owned COPY charts
with their full paid center ranks, and one consistent late native G per
operator. Both helper boundaries are variable. Every earlier native boundary
is held fixed, including the twelve nontrivial shared prelude line pairs.
All former zero persistent edges remain represented and charged.

One bounded functional-1 solve returned the unchanged source, with zero
selected contacts and a floating full-invoice delta of zero. It used 9,188
binary contact variables and 14,480 pair terms, finishing in 0.928 seconds
under the 120-second cap. `DISCOVERY.json` is numerical search evidence,
not an exact optimality certificate, a universal barrier or a higher kappa.
The selected conditional kappa remains .00302015. No wider scan was run.

## Exact model and cost

For source subspace U, each contact chooses U or its intersection with the
common kernel. Persistent transitions and whole helper residuals have actual
canonical relative Fourier rank d(A,B)=dim A+dim B-2dim(A intersect B), as in
the retained general Gaussian contact model. All eight COPY contacts may
move; their CLEAR initializes zero at that chart and their unchanged opposite
owned chart stays zero. Each changed center is priced by its FULL r^t, not
a rank-subtracted bridge price. Other owned contacts stay fixed.

Every native operator has one released positive late occurrence. Other
occurrences are frozen at the original line/zero/full boundaries. When there
is a preserved prelude line, the same invertible G must satisfy G(a)=b. For
late input A, desired output B, k=dim A and l=dim B, the minimum physical
relative rank over such G is

```
abs(k-l) + 2*defect.
```

Without a preserved line, defect=0. With it, put sa=[a in A], sb=[b in B].
For k<=l, defect=0 exactly when 0<=sb-sa<=(k<l). For k>l, use the inverse
condition 0<=sa-sb<=(l<k). Otherwise defect=1. This is the same line-extension
feasibility gate as the credited earlier shared-map work, now applied as an
exact relative-rank table on nonmonotone kernel choices.

Proof: G(A) can have maximum possible intersection min(k,l) with B precisely
under that condition. If the condition fails, preserving the distinguished
line forces the intersection down by one; choosing a complement to that
line and extending a basis attains min(k,l)-1. The symmetric-difference rank
formula gives the displayed minimum. Invertibility prevents G(a) from falling
inside G(A) when a is outside A. When k>l, apply the same argument to G^-1.
The unrestricted case follows by mapping the smaller space into the larger.

One chosen G per operator can cover its fixed zero/full occurrences and its
single nontrivial line pair as well as its late contact. The model minimizes
over that G per binary late assignment. An actual winning candidate would
still have to construct those matrices and emit signed physical instructions;
this package emits no new supplier and grants no phase/native admission.

## Calibration and reproduction

Registered verification uses only Python's standard library:

```sh
python3 -B scripts/research_package.py --package research/owned-kernel-shared-map
python3 -I -B research/owned-kernel-shared-map/verify.py
python3 -I -O -B research/owned-kernel-shared-map/verify.py
```

It checks the native minimum formula against every invertible map and every
ordered binary-subspace pair in dimensions one through three, with and
without G(1)=1: 570 exact minima over 175 invertible maps. Independent input
and output coordinate changes normalize any nonzero prescribed a,b to that
line case. It also checks the equal-dimension/wrong-line rejection, every
source node alignment, all eight changed-center charges and the complete
source paid/helper histograms. For functional1, shared-map freedom improves
52 native tables relative to the predecessor's fixed G tables.

Optional discovery was run with Python3.12.3, NumPy2.5.4 and SciPy1.18.1:

```sh
python3 research/owned-kernel-shared-map/discover.py --functional 1 --seconds 120
```

Install optional solver dependencies in an isolated environment if reproducing
that numerical result. The registered commands never install or run a solver.
The search uses the predecessor's signed-cut MILP at saving .00302177585;
`DISCOVERY.json` retains the complete actual paid/helper re-evaluation.
Floating status0 and dual0 are not a rigorous sign or exact power proof.

## Sources and limits

Live sources are pinned in `SOURCES.json`: Cao Yifan's unchanged round-three
word plus the general Gaussian contact model and optional solver. No frozen
source is edited. Credit Cinna Davis's earlier general contact model and
owned prototype at8052b4818, Cao Yifan's both-boundary/shared-map programs,
Dugongue's chart grammar, the native/controller lineage, Matarener, zxv,
Jacob Alan Sussman and all retained E8/scalar/Clifford/compiler authors.
Substantial OpenAI Codex assistance; no subagents; Apache-2.0.

The related [PR5140 owned-wire floor](https://github.com/CrocSwap/integer-mult-bounds/pull/5140)
assumes monotone persistent L paths. This experiment explicitly drops that
hypothesis and is not excluded by the floor. Conversely this single numerical
kernel test does not prove a no-gain theorem for independent contact subspaces
or any larger domain. Native absolute phases, both full literal endpoints,
owned restoration, precision, compiler and outer funding are unrun for any
positive candidate. Unknown costs are not zero.

## Open next questions

- Does a rigorous weak-duality certificate exist for this exact one-kernel
  model and price? First inspect the continuous relaxation and recover a
  rational interval-valid certificate if tight. Solver optimality alone is
  insufficient; that proof would still have only this model's scope.
- Can a different scalar/common-contact contract or independent nonmonotone
  subspaces yield a favorable complete invoice? Compare another mechanism
  before expanding this search; record one changed hypothesis and exact cost
  gate. Do not automatically rerun all 511 kernels. Actual shared G synthesis,
  signed native replay and full supplier/outer admission remain required.

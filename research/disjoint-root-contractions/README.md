# A tied contraction order saves 1,221 complex helper roles

At historical ground size **h=22**, reversing the two-factor contraction order
in just the root channel `(i,j)=(1,1)` reduces the disjoint-triple DAG from
**31,929 to 30,708 additions**. Its reversible embedding falls from **33,469 to
32,248 paid roles**. Both orders have the same unshared recurrence bound,
39,900; the difference appears after global support interning and pruning.
The descendant planner, point ordering, interning rule and summation tree stay
fixed. This is an explicit historical complex circuit improvement, not a new κ.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. The selected conditional κ at
that base is **1661634653669567/10^18**, from the reviewed #799 construction.
We followed the selected certificate to its source manifest, X4 proof note and
maintainer review. The older κ statements in the tensor notes are historical.
[Source pins](SOURCE-PINS.json) bind the historical circuit, imported dependency
closure, proof sources and selected-state context. `upstream/` is unchanged.

## Reproduction

From the repository root, with standard-library Python 3:

```sh
python3 research/disjoint-root-contractions/verify.py
```

Expected final line:

```text
PASS: disjoint-root contraction certificate, independent reconstruction, and 9 tests.
```

The command rebuilds and compares every field of [CERTIFICATE.json](CERTIFICATE.json),
runs a separate support-keyed implementation, and executes the failure controls
and small complete dirty-input tests. `audit.py --write` intentionally regenerates
the certificate. The independent implementation also runs alone with
`python3 -I -B research/disjoint-root-contractions/independent_check.py`.
No source archive download or third-party package is needed.

## Bounded experiment

OS-random assignment seed **37** selected the complex-supplier track. The seed
chose h=8+2(37 mod 10)=22, rather than automatically choosing the newest record.
Three candidate tasks and the local claim are recorded in [SPRINT.json](SPRINT.json).
There was no pinned coordination issue. Recent JP8 routing and cyclic-inverse
work was already crowded; this historical tensor contraction was distinct.

First we completed the 11 root-split choices `left=1..11` using the inherited
factor-order rule. None beat the balanced baseline. We then made one
explicit pivot: allow **at most one** feasible top-level `(i,j)` channel to
reverse that order. All descendants still use the original planner. There are
143 feasible single flips and 11 no-flip controls: **154 labeled recipes**,
representing **81 distinct DAGs**. All were completed and checked; the stopping
rule prohibited further h scans and multiple simultaneous flips.

The unique best labeled recipe is `left=11, flip=(1,1)`. This finite conclusion
is restricted to fixed ordered points, first-decomposition support interning,
inherited descendants and this recipe family. It does not optimize all circuits,
all root partitions, left sizes 12..21, permutations, or multi-channel changes.
The initial root-only failure is a completed finite search, not an impossibility
theorem. This does not reopen the separate historical early-expansion/refactoring
search or PR809's central-basis one-shear search.

## Why the change is exact

For a root split into l and r points, channel `(i,j)` is
`D_(i,j)(l) tensor D_(3-i,3-j)(r)`. The two factor application orders compute
exactly the same integer map. In the winning l=r=11, i=j=1 channel their
unshared costs tie, so the original `<=` comparison chose the left factor first.
Choosing the right factor first changes which intermediate support sums already
exist when later channels are built. The final active DAG is smaller.

Every created sum has disjoint supports. Interning an equal support retains
its first decomposition; pruning keeps only reachable nodes. The checker
verifies every active sum, every final coefficient (including forbidden zeros),
and the reversible physical-slot embedding. Each recipe covers all 1,540² =
2,371,600 coefficient positions; the complete search covers 365,226,400 positions.
The no-flip adapter reproduces the original DAG exactly.

The inherited phase argument applies to any such disjoint-triple DAG, not just
the DP optimum. A node's ancestor triples and reachable target triples form a
disjoint rectangle. Their ground-point unions are disjoint. The source-line,
coordinate-space, or target-complement frames of
[the retained proof](../../notes/disjoint-tensor-compression.tex) therefore remain
nested with the same norm-one residual witnesses. We check every physical
transition in both orientations for the baseline and selected h22 DAGs, including
fresh/retired roles and endpoints. At h8 and h10 we additionally construct all
distinct residual bases for the corresponding changed recipe.

For the signed scalar invocation, let M be its invertible side mixer, C its
source copy, J its weighted injection, and G/D the central gather/scatter.
The twelve inherited signed operations restore arbitrary side and central
inputs and add `(J M C + D G)x` to y. The four occurrences of M or its inverse
are all paid. For source and target triples meeting in k points, the side
coefficient is +1/2 at k=0, -1/2 at k=2 and zero otherwise; the central coefficient
is (k-1)/2. Their sum is the identity matrix. Reversing the twelve operations
and signs gives the inverse. This algebra does not assume clean scratch.

Tests check all independent source, destination, side and central columns at
h8 and h10, in both directions. Eight dense dyadic h22 controls also check the
whole signed invocation and arbitrary dirty restoration. Those eight controls
are finite tests, not an independent-column proof at h22; the all-input argument
is the linear-map identity and signed cancellation just given.

## Complete historical invoice

The comparison retains the historical h+1=23 centers, the intersection-two
circuit, joins, tensor stages and all access/restoration work. PR809's different
h-center factorization is not used.

| Quantity | Original | Changed |
| --- | ---: | ---: |
| Disjoint additions | 31,929 | 30,708 |
| Disjoint helper roles | 33,469 | 32,248 |
| Intersection-two roles | 17,094 | 17,094 |
| Total side roles | 50,563 | 49,342 |
| Mixer additions M | 88,806 | 86,364 |
| Source accesses C / weighted injections J | 6,160 / 6,160 | 6,160 / 6,160 |
| Full signed invocation bound | 419,904 | 410,136 |
| Three-stage scalar bound | 2,987,532,979,200 | 2,918,035,612,800 |
| W | 247,244,043,200 | 241,452,596,000 |
| s | 2,632,654,467,643,200 | 2,570,987,137,857,600 |

Here v=1,540, m=10,648, L=3,600,088,800 and deficit Wm-s=104,350,400
are unchanged. If d=1,221 additions are removed, R0 decreases by d, W decreases
by 2v²d, and s decreases by 2mv²d. The full scalar bound is
`3v²(4M+2C+4J+18v)` and decreases by **24v²d=69,497,366,400**.
No basis adapter, added helper or extra recursive child is introduced.

The certificate recomputes `E=64(W+m+1)^3`, its positive node-charge slack,
`s<m^5`, the stopped recurrence `A(e)<=s A(e/m)+E`, and exact rational logarithm
bounds. The historical complex saving interval moves from approximately
4.274388795e-9 to 4.376913671e-9. These are this older supplier's savings, **not**
the selected multiplication κ or a claimed new assembly. The current bit supplier,
owner invoice and outer assembly are not changed or composed with this circuit;
there is consequently no supported improvement to the selected frontier.

## Verification and limitations

The separate [independent checker](independent_check.py) imports no repository
code. It recomputes the descendant recurrence, uses support masks themselves as
DAG keys, and applies either order through a generic factor contraction. It
reconstructs h22 baseline/winner and h8/h10 controls, matching exact node-only
DAG hashes and coefficient hashes. It independently checks maps/counts; the
physical embedding and phase checks still use the retained framework.

Failure controls reject invalid recipes, altered output/node coefficients,
overlapping or cyclic additions, omitted source access and a wrong injection
sign. Exact replay is also run with Python `-O`; new certificate and DAG checks use
explicit exceptions. Some inherited low-level checks use assertions, so the normal
Python replay remains required for their complete coverage. [VALIDATION.json](VALIDATION.json) records the actual commands.
This is not formal verification of the full multiplication theorem. Uniform
compilation, common labels and mutable sources, whole-call hosting, precision,
tape scheduling and analytic transfer remain inherited assumptions.

## Attribution and license

Contribution: **Curtis Dransfield**, with substantial assistance from **OpenAI
Codex**, including implementation, mathematical analysis, tests and an independently
implemented cross-check by a scoped Codex worker. New files are Apache-2.0.
The tensor recurrence, phase enclosure, support interning and signed invocation
come from **Douglas R. Colkitt** and the repository's disclosed AI-assisted work
(source commit `1a74950ce5074b848243ba89d8022fbadba66105`; retained source notices
and license apply). The small symbolic test helper is reused with attribution
from `tests/test_complex_compression.py`.

The selected-state review credits Jeremy Kothe's #799, Chafik Boukhalfa's #741,
DreamingOfClouds' #589 and eumemic's #555 with their recorded predecessors. This
submission does not depend on pending construction PRs. The overlap record
credits neighboring contributions without claiming to incorporate or supersede them.

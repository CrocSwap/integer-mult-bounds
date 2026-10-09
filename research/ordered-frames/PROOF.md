# Reordered frames, paid reclamation and geometric relabeling

This construction changes the finite bit network of PR #63. The complete
conditional exponent and exact parameters are in `certificate.json`; the
selected finite program is reproducible from `selection.json`, `producer.py`
and `compiler.py`. All source pins are recorded in `SOURCE.json`.

The statement retains the original OpenAI #109 framework and the community
chain's general analytic, framed-word transfer, finite-alphabet multitape,
precision, routing, prime-selection and recovery hypotheses. The finite
checks below do not prove those inherited hypotheses.

## 1. A different legal order of scalar nodes

Begin with PR #62's unchanged interval-strip/pair-assembly scalar DAG.
Preserve the input variable IDs. Group active addition nodes by their exact
original envelope `(core, cover)`. Preserve the original node order within
each group. Sort groups by

```
(popcount(cover)-popcount(core), -core, cover, minimum_original_node_ID)
```

Assign new addition IDs in this order and translate every operand and output
reference through the resulting bijection. This changes scheduling and the
order in which the compiler enumerates carrier candidates; the matching is
recomputed for this new order.

For the selected two finite graphs, `c.verify()` checks every operand precedes
its target, every addition is disjoint, each core/cover is exact, and each
prescribed output is unchanged. A separate dense global-support audit checks
identical output-support and addition/operand-support multisets before and
after reordering. These checks establish a legal ordering for these finite
instances; no unrestricted statement about all possible envelope orders is
needed.

The original compiler then verifies the span and independence conditions for
every retained carrier. Reordering changes which physical scratch roles can
be retired and reused before later regions need them. The selected role counts
are 27,698 at h=23 and 36,310 at h=25, compared with PR #63's 27,918 and 36,586.

## 2. Select among explicitly witnessed clearing operations

The eligible anchors and retired slots, their containing-frame test, and the
binary Gaussian elimination are inherited. For each eligible dependent slot
`s`, the elimination supplies an explicit list `A` satisfying

```
value(s) = XOR(value(a) for a in A).
```

The compiler scans these candidates without changing physical state. It
chooses the smallest tuple

```
(sum(rank(E)-rank(current_frame(x)) for x in [s]+A),
 len(A), -rank(current_frame(s)), s)
```

where `E` is the requested region. It executes every listed clearing XOR
through the inherited routine, which raises both operands into `E` and
records both frame incidences. Only after the slot is cleared is it reused.
The criterion guides discovery; it does not replace any cost in the final
characteristic moment. In particular, extra XORs and frame changes remain
explicitly charged.

This changes the selection among legal dependence witnesses. It does not
assume a new kind of carrier, free clearing, or any unverified matching
optimality. The complete compute/scatter/uncompute word is replayed on every
source, target and dirty basis vector in both orientations.

## 3. Relabel geometric coordinates

The fixed selected permutations are listed in `selection.json`. For an axis
permutation pi, relabel every frame's core and cover masks; replace each
input triple S with its sorted image pi(S); update the source indices,
scatter target indices, and every output's common point and triple.
Scratch slot IDs, frame-array indices, XOR incidences and event order stay
fixed.

This is a relabeling of the finite network, not an additional physical
permutation operation. Independent serialized replay checks the required
scalar map after relabeling. The incidence extractor separately reconstructs
each physical frame transition from the literal XOR word and compares it
with the compiler's event list.

For a permutation matrix P, both the basis matrix I+J and ambient form I-J/9
commute with P. Thus the projector for a relabeled envelope is P A P^-1 for
the original projector A. Containment, ranks, the bounded-minor estimates,
copied-center count h and loss h(h-1) are preserved. Ordered pivot runs need
not be preserved. Every relabeled transition therefore receives a fresh
fixed-basis profile, including the inherited exact bounded-minor and CRT
checks; old internal histograms are never treated as invariant.

The complete data geometry enumerates every pair of three-subsets on the two
axes. Mapping (S,T) to (pi23(S),pi25(T)) is a bijection of this family, and the
relabeled data matrix is exactly the previously certified matrix for that
new pair. Its complete aggregate profile therefore remains the same. The
inherited data audit checks all 4,073,300 pairs, including exact rational
recovery of the ten primary-prime exceptions. The data profile, paid endpoint
copies and the complex branch remain fully included.

## 4. Complete costs and exact assembly

There are N=4,073,300 data roles and two axes with
v23=1771, v25=2300. The selected width is

```
W = 2N + (N/1771)*27698 + (N/2300)*36310
  = 136157010.
```

This saves 994,796 physical wires against the pinned PR #63 witness. The
unchanged complete paid-profile constructor includes internal profiles,
exterior transitions, data growth, both data copies, all copied centers and
paid endpoint copies. It checks the exact identity

```
sum(t*n_t) = 575*W - 1846900.
```

Every child width is at most 529, strictly below 575. For the complete
multiplicities n_t, the characteristic moment is

```
M(a) = sum(t*n_t/(575*W) * exp(a*log(575/t))).
```

The checker uses exact rational logarithm bounds and a degree-eight Taylor
exponential bound with its rigorous geometric tail, rounding each term
outward. It proves M(a)<1 and M(a+10^-18)>1 for the recorded bit saving. It
also proves that the complete old PR #63 network fails at the new bit saving.

The balanced assembly retains complex saving 717/10^7 and beta=1/20 and uses
positive backoff h=10^-18. It chooses q=a(1-2h), epsilon=(1-h)/(1+q), and
strict kappa<epsilon*q. All 47 strict inequalities and seven margins are
recomputed. The next kappa grid value is rejected for these fixed parameters.
Eventual arithmetic thresholds are recorded, with additional inherited
eventual conditions explicitly retained. This is an asymptotic exponent
comparison, not a practical multiplication speed benchmark.

## 5. Evidence and attribution

`producer.py` reconstructs both selected words from the scalar DAG, checks
the complete dirty basis, relabels them, and independently replays the
serialized result. `check.py` repeats independent replay, reconstructs literal
transitions, regenerates every paid profile, checks all source hashes and
recomputes the exact assembly. `independent_check.py` supplies a separate
logarithm/exponential calculation. `validation.json` records actual outcomes.

The new finite ordering, minimum-raise selection and coordinate search were
prepared with substantial OpenAI Codex assistance for Thomas DiFiore. This
builds on Dominik Scholz's PR #63 composition; Chafik Boukhalfa's PR #60
rank-first reclamation; Avi Eisenberg's PR #62 interval strips and pair
assembly; eumemic's PR #57 frame compiler; Alejandro Zarzuelo Urdiales's
PR #61 parameter refinement; Rohan Arun, RaD/hipotures, icekylinx, James
Chang, Zhihao Chen, Aurel Prosz, Swapnil Jain, Douglas Colkitt, OpenAI,
Harvey–van der Hoeven, and the complete retained community dependency chain.

During this run, concurrent PR #65 explored region schedules and PR #67
explored profile-aware retired-slot selection. Those submissions were not
used to generate this selected construction. Their parallel contributions
are acknowledged; no priority or global-optimality claim is made. Existing
Apache-2.0 and source-specific notices are retained.

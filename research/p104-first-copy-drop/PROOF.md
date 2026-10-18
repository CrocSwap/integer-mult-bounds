# Sharp COPY-drop threshold with a preserved P104 frame puncture

## Statement and changed hypothesis

Fix PR968's coordinate frame F0 of eight E8 root lines. Let F1 be any of the
896 disjoint frames admitting its eight mixed frame-pair decoders. Puncture
all sixteen lines in F0 union F1, leaving the 104-port unit. Further puncture
an arbitrary subset Q of the remaining lines. Retain the same eight-term
all-pairs decoder and PR717's additive label-pairing COPY price.

**Scoped theorem.** For every one of the 7,168 decoders, every COPY term
retains rank seven when |Q|<=21. The first possible drop is |Q|=22, or
**38 total punctures**. Each possible root-pair term in this family has that
same first-drop threshold. An explicit decoder and 22-port deletion in the
certificate attain costs [7,7,7,6,7,7,7,7], total 55 on 82 live ports.

By contrast, the first support-label span drop is |Q|=20. The certificate
gives a seven-dimensional support at that boundary with every COPY term
still rank seven. A support-span loss alone does not imply a COPY saving.

The result is an exact finite-family certificate with a written completeness
argument, not a proof-assistant verification or a multiplication theorem.
The common-label, copy realization, chronological frames, hosting, precision,
restoration and analytic interfaces remain outside the result.

PR968/1077 cover arbitrary eight-term decoders through 24 total punctures;
their span>=8 premise ends there. This note crosses that boundary while
fixing the frame-pair normal family and preserving its entire original
puncture. PR1020 proves first cost six at 26 punctures for an unconstrained
odd root pair; its completed decoder costs 69 on 94 ports. It does not
require a complete F0/F1 puncture. Our stronger puncture constraint and
completed low-cost decoder family are the distinction, not a new seed.

## Label pairing and the compulsory radical condition

Let the 120 root-line labels u_i span Lambda=F2^9 with nondegenerate symmetric
pairing S. In the pinned model,

```
S(u_i,u_j) = (inner_product(r_i,r_j)+1) modulo 2.
```

Every root has norm two, so S(u_a,u_a)=1. For a root normal a, the live
support is the set of unpunctured lines not orthogonal to a. With a itself
punctured, its labels lie in H_a=ker S(u_a,-), a dimension-eight hyperplane.
The census independently checks that every such support in each base P104
actually spans H_a.

A frame-pair term uses distinct root normals a,b with inner product +/-1.
Thus S(u_a,u_b)=0, and u_b lies in H_a while u_a lies in H_b. The pairing
H_a x H_b has left radical span(u_b), right radical span(u_a), and rank
seven. Its induced pairing

```
(H_a / span(u_b)) x (H_b / span(u_a))
```

is nondegenerate between two seven-dimensional spaces.

Let V,W be the surviving support-label spans after Q is removed. Their
images in those quotients give exactly the surviving term's pairing rank.
If both images span all seven dimensions, the rank remains seven. If either
image is proper, the rank is at most six. This proves the exact criterion:

```
COPY rank < 7  iff  at least one surviving quotient image loses dimension.
```

In particular, a seven-dimensional V can still project onto the whole
seven-dimensional quotient when V excludes u_b. This explains the explicit
20-additional-puncture control.

## Complete reduction to hyperplane deletion cuts

A proper subspace of H_a/span(u_b) is annihilated by a nonzero functional.
Extend it to a functional lambda on Lambda. It satisfies lambda(u_b)=0
and has nonzero restriction to H_a. Two extensions differing by the defining
functional of H_a represent the same restriction. There are exactly
2^7-1=127 possible nonzero quotient functionals.

For each lambda, let C(a,b,lambda) be the currently live a-support labels
where lambda is one. To kill this functional, **every** port in that cut
must be deleted. Conversely, deleting the cut makes the surviving quotient
image proper and drops the COPY rank. Therefore the exact first-drop cost
for the fixed pair is

```
min { |C(a,b,lambda)|, |C(b,a,mu)| }
over all 127 quotient functionals on each side.
```

This covers arbitrary Q, without enumerating all subsets of the 104 ports:
any rank-losing Q contains one such entire cut, while a minimum cut itself
attains the drop. It also handles simultaneous changes on both supports:
two full quotient images cannot lose rank merely by pairing them together.

The related support-span question has 2^8-1=255 hyperplane restrictions on
H_a, without the partner-radical condition. Its minimum of 20 is a favorable
relaxation of the COPY problem; using that relaxation as a COPY saving fails.

## Two independent exact census methods

The primary census uses the frozen PR968 E8 model and exact frame constructor.
It enumerates all 511 nonzero functionals on Lambda, collapses equal
restrictions on H_a, and imposes lambda(u_b)=0 for the COPY cuts. This checks
3,655,680 support cuts and 7,282,688 quotient cuts. Exact duality is checked
for the constructed frame solutions.

The second implementation imports neither census.py nor predecessor code.
It constructs the 120 roots directly, forms the full binary pairing matrix,
enumerates all 1,260 disjoint frames and all exact dual partitions with a
bit-mask matching algorithm. It finds 364 inadmissible frames, 896 admissible
frames and 7,168 exact decoders.

For each possible term, it takes seven independent columns of the baseline
pairing matrix as functions on the source support. The 127 nonzero XORs of
those columns are exactly its quotient hyperplane cuts. On the target side
it uses the analogous row space. This is a binary-code minimum-weight
calculation, independent of the primary's nine-dimensional coordinates and
functional filtering. For the support-only relaxation it uses all eight
independent label functionals and their 255 nonzero codewords.

Both methods agree on every frame record:

| Item | Completed result |
| --- | ---: |
| Admissible frames | 896 |
| Exact decoders | 7,168 |
| Possible unordered terms across frames | 28,672 |
| Minimum support-span deletion | 20, in every frame |
| Minimum COPY-rank deletion | 22, for every possible term |
| Minimum quotient-cut incidences per frame | 1,536 |

The full canonical records and their digest are in CERTIFICATE.json. Each
decoder's eight terms are drawn from its frame's enumerated 32 possible
unordered pairs. Since every such pair has threshold 22, each decoder has
the stated lower bound and can attain it by deleting a minimum cut for one
of its own terms. The certificate emits one complete attaining decoder.

No hyperplane-flat classification over the reals is needed for this result:
the normals are explicitly restricted to the roots in the two frames.

## Exact decoder and cost screen

For each emitted pair (a_k,b_k), set e_k=inner_product(a_k,b_k)=+/-1. The
normal columns a_k and 2 e_k b_k satisfy A^transpose B=2I. Hence they give
the exact all-pairs identity D T^transpose=2G on every remaining port set.
The independent checker verifies all 82^2=6,724 coefficients of the emitted
decoder and every term's binary pairing rank. Restoring any one of the
22 added punctures returns all eight COPY ranks to seven.

For 0<=q<=21 added punctures, the complete copied-information bill is
exactly 56 on 104-q ports. Its ratio 56/(104-q) is at least 7/13 and is
strictly worse for q>0. The first-drop witness has ratio

```
55/82 > 56/104 = 7/13,   difference = 141/1066.
```

Thus the emitted deeper-puncture mechanism does not improve even this COPY
ratio, before paying any further source access, helpers, frame changes,
restoration or recursive hosting. Those expenses are not declared free in
an algorithm. They have not been implemented or priced into a supplier,
and no kappa is inferred from the certificate. This is a favorable cost
screen for the displayed witness, not a whole-decoder optimum at q=22.

At q>=22, other puncture choices, aggregate COPY minima and fully paid
realization remain open. The threshold does not bound arbitrary decoder
normal sets, masked identities, nine or more terms, coefficient-field
changes or punctures that restore one of the sixteen required frame lines.

## Sources and review

Base: c0e3631dc24e3c24a861f7d3d79e0608481cccec; assignment seed 46.
Source paths, exact Git pins and SHA256 values are in SOURCES.json. PR968's
original source/README/proof are retained; its module is used only by the
primary checker and runs with assertions enabled. PR1020's README/proof/
notice are retained. The independent verifier uses explicit failure checks
and supports optimized Python.

Credit themilkman216's PR968, DreamingOfClouds's PR717 decoder model,
woklerx's PR1020 and PR1077, Joel Pulikkan's PR620 lineage, and Ali Romman's
distinct PR1125 delivery theorem. New work by Cinna Davis with substantial
OpenAI Codex assistance; Apache-2.0. No independent human review or complete
multiplication-theorem verification is claimed.

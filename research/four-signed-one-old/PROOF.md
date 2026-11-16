# Four rank-one frames plus one old call miss length 5

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, consider five paid labels: four nonzero symmetric rational rank-one matrices `R,S,T,U`, each used once, and one old projector

```
E ∈ {A, B, P, Q},
```

also used once. The determinant identity for this count is

```
R + S + T + U = 4I - E.
```

No such matrices have all four targets as subset sums. The count therefore admits no word. Selected κ stays `781451/250000000`.

This is one equation, the length-5 profile with exactly one old call. It does not speak about two or three old calls, about five or more added frames, or about any larger alphabet. A solution of the sum equation is not by itself a word; the support obstruction is what excludes the word. The two declared solutions in Section 8 satisfy the sum and are not a classification of all such sums.

The identity "sum of the paid addresses = 4I" and the necessary condition "each target is a subset sum of the paid labels" are inherited from `research/bit-two-signed-frame-floor/PROOF.md`, Section 1. This file does not reprove them. The new argument is the support obstruction for this one residual.

## 1. Setup

Addresses are rational symmetric 2-by-2 matrices. Write

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2.
```

A coefficient vector `(a,b,c)` means `aA + bB + cP`, with trace `a+b+c` and determinant `ab + c(a+b)/2`. The matrix is nonzero and rank one exactly when the vector is nonzero and the determinant is zero. Every nonzero symmetric rational rank-one matrix has this form for some primitive integer direction and nonzero rational scale. Either sign is allowed, and a new frame may repeat an old projector.

The four targets are

```
A+P = (1,0,1),  A+Q = (2,1,-1),
B+P = (0,1,1),  B+Q = (1,2,-1).
```

Each has trace 2 and determinant `1/2`. Their sum is `4I = (4,4,0)`. For each target `H`,

```
det(4I - H) = 16 - 4·tr(H) + det(H) = 17/2 ≠ 0,
```

so `4I-H` is not rank one. Write

```
φ(a,b,c) = ((a+b) mod 2, c mod 2).
```

Each target has `φ = (1,1)`. The vector `4I` is even in every coordinate, so each complement `4I-H` has `φ = (1,1)` as well. Thus all eight possible pair-sums below have parity `(1,1)` and trace 2 or 6.

Two linear automorphisms are used to move projectors. The coordinate exchange is `(a,b,c) ↦ (b,a,c)`. It swaps `A` with `B`, fixes `P` and `Q`, and swaps `A+P` with `B+P` and `A+Q` with `B+Q`. The sign flip is `(a,b,c) ↦ (a+c, b+c, -c)`. It swaps `P` with `Q`, fixes `A` and `B`, and swaps `A+P` with `A+Q` and `B+P` with `B+Q`. Both are conjugations by an invertible rational matrix, namely the exchange matrix and `diag(1,-1)`, so both preserve rank, determinant, and subset sums, and both fix `4I`. A support solution for `E=B` would exchange to a support solution for `E=A`. A support solution for `E=Q` would flip to a support solution for `E=P`. The case split is written for `A` and `P`. The verifier repeats the same arithmetic for `B` and `Q`.

## 2. Only pairs and triples can carry a target

**Lemma 1.** Let five nonzero symmetric rational rank-one matrices sum to `4I`. A subset summing to a target has size 2 or 3.

**Proof.** The empty sum is 0. A singleton has determinant 0, while each target has determinant `1/2`. The full sum is `4I`. A four-element subset sums to a target `H` only if the omitted matrix equals `4I-H`, which has determinant `17/2` and is not rank one.

Each target therefore determines a unique unordered pair: the size-2 block of the partition into 2+3. That pair sums to `H` or to `4I-H`. Different targets give different pairs, because `H` and `4I-H` are not targets (traces 2 and 6) and the four targets are distinct. The carrying graph has four edges on the five labels.

## 3. The carrying graph is bipartite

**Lemma 2.** Every carrying edge joins coefficient vectors whose parities differ by `(1,1)`. The carrying graph has no odd cycle.

**Proof.** Section 1 records that every admissible edge sum, whether `H` or `4I-H`, has `φ = (1,1)`. Endpoint parities therefore differ by `(1,1)`. An odd cycle has no such 2-coloring.

## 4. The remaining graphs

**Lemma 3.** A simple graph with five vertices and four edges, and with no odd cycle, is a tree or a 4-cycle plus an isolated vertex. The trees are the star, the path, and the fork of degrees `3,2,1,1,1`.

**Proof.** With no odd cycle the graph is bipartite. If it is acyclic, then `e = v-1`, so it is a tree. Five positive degrees summing to 8 are one of

```
(4,1,1,1,1),  (3,2,1,1,1),  (2,2,2,1,1),
```

and each sequence determines one tree: the star, the fork, and the path.

If the graph contains a cycle, the excess is `e-v+c = c-1 ≥ 1`, so there are at least two components. The cyclic component then has `n` vertices and `n` edges, and the complementary forest has `5-n` vertices and `4-n` edges. A forest on `m` vertices has at most `m-1` edges, and `4-n ≤ (5-n)-1`, so equality holds: the complement is a tree and there are exactly two components. Thus `n ≥ 4` for a simple even cycle, and `n ≤ 4` because the complement is nonempty. The cyclic component is a 4-cycle, and the other component is a single vertex.

## 5. Every tree misses the projector trace

**Lemma 4.** No carrying tree is consistent with `E` having trace 1.

**Proof.** Every carrying edge has trace 2 or 6.

On the star, label the center `C` and the edge sums `M1,M2,M3,M4`. The leaves are `Mi-C`, so

```
M1+M2+M3+M4 - 3C = 4I.
```

Traces give `4k = 3 tr(C)` for some integer `k` with `0 ≤ k ≤ 4`, hence `3 tr(C) ≡ 0 (mod 4)`. If the center is `E`, then `tr(C)=1` and `3 ≢ 0 (mod 4)`. If `E` is a leaf of edge `M`, then `C = M-E` and `tr(C) ∈ {1,5}`. In both subcases `3 tr(C) ≡ 3 (mod 4)`.

On the path `F0-F1-F2-F3-F4` with edge sums `M0,M1,M2,M3`, propagation gives

```
F0 = 4I - M1 - M3
```

and then `Fi+1 = Mi - Fi`. Substituting produces

```
F0+F1+F2+F3+F4 = F0 + M1 + M3,
```

so the displayed formula is forced by the total sum. The five traces are

```
8-tr(M1)-tr(M3),
tr(M0)+tr(M1)+tr(M3)-8,
8-tr(M0)-tr(M3),
tr(M0)+tr(M2)+tr(M3)-8,
8-tr(M0)-tr(M2).
```

Each input trace is even and 8 is even, so every vertex trace is even. The projector trace is 1.

On the fork, let `C` meet leaves `L1,L2` and a degree-2 vertex `D`, and let `D` meet the third leaf `L3`. With edge sums `M1,M2` at the leaves of `C`, bridge `Mcd`, and outer edge `M3`,

```
L1=M1-C,  L2=M2-C,  D=Mcd-C,  L3=M3-D.
```

The bridge cancels in the total sum and leaves

```
C = M1+M2+M3-4I.
```

Every vertex is an integer combination of even-trace matrices and `4I`, so every vertex trace is even.

`verify.py` checks the path and fork closed forms on an affine basis and checks that all 16 trace patterns stay even.

## 6. A 4-cycle opposite the old call has odd trace

**Lemma 5.** The carrying graph cannot be a 4-cycle on the four new frames with `E` isolated.

**Proof.** Order the cycle `F0,F1,F2,F3` with edge sums `M01,M12,M23,M30`. Solving the edges leaves one free matrix, and the cycle consistency condition is independent of that matrix. The sum of the four frames collapses to `M12+M30`. The total sum would require

```
M12+M30 = 4I-E.
```

The left side has even trace. The right side has trace `8-1 = 7`.

## 7. The 4-cycle through the old call

The only graph left is a 4-cycle through `E` and three new frames, with the fourth new frame isolated. Order the cycle `E,X,Z,Y`.

**Lemma 6.** If `X` and `Y` are rank one, the two edges at `E` are direct target sums, and they are the unique pair in the following table.

| `E` | edges at `E` | resulting neighbors |
|---|---|---|
| `A` | `A+P`, `A+Q` | `P`, `Q` |
| `B` | `B+P`, `B+Q` | `P`, `Q` |
| `P` | `A+P`, `B+P` | `A`, `B` |
| `Q` | `A+Q`, `B+Q` | `A`, `B` |

**Proof.** There are eight candidate edge matrices. For `E=A`,

```
(A+P)-A = P,          (A+Q)-A = Q,
(B+P)-A = (-1,1,1),   det = -1,
(B+Q)-A = (0,2,-1),   det = -1,
```

and the four complements `4I-H-A` have determinants `5,5,6,6`. Only `A+P` and `A+Q` work. They use different targets, so both edges at `E` are accounted for. The same eight evaluations with `E=P` leave only `(A+P)-P = A` and `(B+P)-P = B`; the other six determinants are `-1,-1,5,6,5,6`. The rows `B` and `Q` follow by the automorphisms of Section 1, and the verifier recomputes them directly.

The opposite edges must carry the other two targets, each either direct or complemented. Write `MX,MY` for the edge sums at `E` and `RX,RY` for the opposite sums. Consistency is `MX+RY = MY+RX`, or

```
RY - RX = MY - MX.
```

For `E=A` and `(MX,MY) = (A+P, A+Q)`, the required difference is `Q-P = (1,1,-2)`. The eight ways to assign `{B+P, B+Q}` and their complements are:

| `X-Z` | `Y-Z` | difference |
|---|---|---|
| `B+P` | `B+Q` | `(1,1,-2)` |
| `B+P` | `4I-(B+Q)` | `(3,1,0)` |
| `4I-(B+P)` | `B+Q` | `(-3,-1,0)` |
| `4I-(B+P)` | `4I-(B+Q)` | `(-1,-1,2)` |
| `B+Q` | `B+P` | `(-1,-1,2)` |
| `B+Q` | `4I-(B+P)` | `(3,1,0)` |
| `4I-(B+Q)` | `B+P` | `(-3,-1,0)` |
| `4I-(B+Q)` | `4I-(B+P)` | `(1,1,-2)` |

Only the first and last rows match `(1,1,-2)`. The opposite neighbor order asks for `(1,1,-2)` negated, which selects the fourth and fifth rows. Those four labelings produce two framesets.

Direct opposite edges `B+P` and `B+Q`:

```
X = P,  Y = Q,  Z = B,  W = 2I.
```

Here `W` is the isolated frame. `det(2I) = 4 ≠ 0`.

Both opposite edges complemented:

```
X = P,  Y = Q,  Z = (3,2,0),  W = (-1,1,0),
```

with determinants `6` and `-1`.

For `E=P` and `(MX,MY) = (A+P, B+P)`, the required difference is `(B+P)-(A+P) = (-1,1,0)`. Among the eight assignments of `{A+Q, B+Q}`, the matches are the direct pair

```
(B+Q) - (A+Q) = (-1,1,0)
```

and the fully complemented pair

```
(4I-(A+Q)) - (4I-(B+Q)) = (B+Q)-(A+Q) = (-1,1,0).
```

The other six differences are not `(-1,1,0)`. These two rows give

```
X = A,  Y = B,  Z = Q,  W = 2I
```

and

```
X = A,  Y = B,  Z = (2,2,1),  W = (1,1,-2),
```

with a determinant `4`, or determinants `6` and `-1`. Swapping the two edges at `E` repeats these frames. In every consistent labeling, some new frame has nonzero determinant.

## 8. Two declared solutions of the sum

The sum equation alone has rational rank-one solutions. Two are recorded here. They are examples, not a census.

For `E=A`, the directions and scales

```
(1,0) at 4,  (0,1) at 2,  (1,1) at -2,  (1,2) at 1
```

give `(4,0,0)`, `(0,2,0)`, `(0,0,-4)`, and `(-1,2,4)`. Their sum is `(3,4,0) = 4I-A`. Each is nonzero and rank one. None of the 31 nonempty subsets of these four frames together with `A` equals a target. In particular the pair test, restricted to size-2 sums, finds no target.

For `E=P`, the directions and scales

```
(1,0) at 1,  (0,1) at 1,  (1,1) at 1,  (1,-1) at 3/2
```

give `A`, `B`, `(0,0,2)`, and `(3,3,-3)`. Their sum is `(4,4,-1) = 4I-P`. The pairs `A+P` and `B+P` are targets, so a pair test on this one solution does not miss every target. The other two targets are not subset sums of any size. Support still fails. One solution's pair test is not the theorem.

## 9. Census, as a separate check

Lemma 1 reduces support to a finite set of carrying assignments: four distinct pairs on five labeled vertices, a bijection from the four targets to those pairs, and a direct-or-complement bit for each target. There are `P(10,4)·16 = 80640` assignments for each of the four projectors.

`verify.py` solves each assignment by exact integer elimination, independently of the tree and cycle case split. For each projector it finds 80064 inconsistent systems and 576 consistent systems. Every consistent system has degree sequence `(2,2,2,2,0)` with `E` of degree 2, so the census independently sees only the 4-cycle through `E`. None of the 576 solutions is four nonzero rank-one frames. A planted near-miss, the frames `P,B,Q,2I` with `E=A`, solves back to those frames, and changing one edge sum makes the system inconsistent.

This census is exhaustive for the finite domain in Lemma 1. It is not a search over directions, scales, or denominators, and it is not a heuristic. It is a second proof of the same support statement. It does not replace the case split, and the case split does not assume the census.

## 10. Consequence

By the inherited subset-sum necessity, a word with these five labels would have all four targets as subset sums. No such labels exist, so the length-5 profile admits no word. The direct eight-call word is untouched. Nothing here lowers the eight-call minimum or changes the selected record.

## Open next questions

Two old calls, and three old calls, are open. Lemmas 3 through 7 use five labels. A sixth label changes the allowed subset sizes and the degree sum, so the 4-cycle analysis does not apply.

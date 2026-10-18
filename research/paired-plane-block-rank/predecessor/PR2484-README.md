# Exact scalar fitting rank 49 for PR2471's fixed paired-plane mask

**Status: research note with independent verification of PR2471's witnesses.
It determines the exact value of one finite algebraic quantity (explicit fit plus
a matching lower-bound proof). No kappa, supplier price or selected-result
change.**

[PR2471](https://github.com/CrocSwap/integer-mult-bounds/pull/2471) (ywz65,
head `5a7c2b681b79d5b5e25fac62aa4bad908525b5ca`) shows that the minimum rank of
a scalar fitting matrix for the strict PR1889 mask on PR1825's 56 matched P112
planes lies in `[48, 50]` over every field. Its open question 1 asks whether
rank 48 or 49 is possible, or whether the floor is 50.

**Answer: the minimum is exactly 49 over every field.**

- *Upper bound 49.* An explicit symmetric 0/1 matrix with 49 disjoint supports
  fits the mask. This improves PR2471's rank-50 construction by one.
- *Lower bound 49.* Every fitting matrix over every field has rank at least 49.
  This improves PR2471's `I_48` floor by one. It uses a 54-port principal
  submatrix `I_44 (+) M` together with a short linear-algebra lemma for an
  induced 5-cycle of orthogonal planes.

Both of PR2471's witnesses re-check: a 24-clique and a 25-class rank-50 fit.
PR2471 did not assert optimality of either witness, so nothing in PR2471 is
contradicted. PR2471's README compares its floor with 23 scalar rank-one
channels, which is PR1825/PR1889's count of binary scalar column pairs (nine
rank-one plus seven rank-two queries). PR2471's floor already excludes 47
channels; the exact floor of 49 here excludes 48, and exceeds that reference
count of 23 by 26.

## Model (same as PR2471)

`q_0..q_111` in `F_2^9` are the P112 labels. PR1825's matching pairs them into
56 planes `E=span(q_i,q_j)` with Gram matrix `I_2`. Two distinct planes are
*orthogonal* when all four basis pairings vanish. A plane is never orthogonal to
itself. A matrix `K` over a field `F` *fits* when `K_ii=1`, and `K_ij=0` whenever
`i!=j` and the planes of `i,j` are not orthogonal (including the same plane).
Entries between orthogonal planes are free. No symmetry is required.

Let `G` be the graph on the 56 planes in which two planes are adjacent when they
are non-orthogonal. Independent reconstruction from the pinned sources gives
1431 non-orthogonal pairs and only 109 orthogonal pairs. There are 24 orthogonal
triples and no orthogonal 4-set, so `alpha(G)=3`. Plane 36 is orthogonal to no
other plane.

## Results (all exact, recomputed by `verify.py`)

| quantity | value | evidence |
|---|---|---|
| `omega(G)` | 24 (194 maximum cliques) | path-order DP, 12138 states; this algorithm differs from PR2471's colour-bounded branch and bound |
| `chi(G)` | **25** | exact DP over packings of orthogonal pairs and triples (40277 states). No 24-class plane partition exists, so PR2471's `2*chi` method cannot reach 48 |
| `chi_f(G)` | **49/2** | exact Bland simplex. The LP solved is the fractional-clique LP (primal `y`); its dual, a half-integral fractional colouring `x`, is read from the reduced costs. Both are stored and re-checked against all 189 orthogonal sets |
| `chi_2(G)` = `chi(G[K_2])` | **49** | upper: the doubled half-integral fractional colouring `x` gives 49 port classes. Lower: `2*chi_f`. An optional capacity-2 DP (`--two-fold-dp`) independently gives max savings 63, so `112-63=49` |
| min fitting rank, every field | **49** | upper: 49-support 0/1 fit; lower: theorem below |

The rank-49 fit `K = sum_S 1_S 1_S^T` uses the 49 supports in
`CERTIFICATE.json` (`rank49_supports`). Every port lies in exactly one support.
Each support contains ports of distinct, pairwise orthogonal planes. So the
diagonal is 1 and every nonzero off-diagonal entry joins orthogonal planes.
Each entry is a single 0/1 term, so the fit holds in every characteristic. The
verifier checks all 11672 required entries. One representative per support
gives `I_49`, so the rank is exactly 49 over every field. Ranks mod 2, 3 and 101
are also computed as a cross-check.

## Lower bound: proof

**Lemma (C5 core).** Let `P0..P4` be planes such that `Pi,Pj` are orthogonal
exactly when `j=i+-1 (mod 5)`. Then every fitting matrix restricted to their
ten ports has rank at least 5, over every field.

*Proof.* Assume the 10-by-10 principal submatrix `M` has rank at most 4. Let
the ports of `P0,P1,P2,P3,P4` be `A1,A2`, `B1,B2`, `C1,C2`, `D1,D2`, `E1,E2`.
`P0` and `P2` are non-orthogonal, so `M[A1,A2,C1,C2]=I_4`. Hence `rank M=4`, and
`M=UV^T` with `U,V` of size `10 x 4`. The rows `u_A1,u_A2,u_C1,u_C2` are a basis.
Replace `U` by `U U_0^{-1}` and `V` by `V U_0^T`, where `U_0` is that basis
block. This makes those rows `e1..e4`, and then their `v` rows are also `e1..e4`.

`P3` is non-orthogonal to `P0`, so `M[A,D]=0` and `v_D` is in `span(e3,e4)`.
`M[D,D]=I_2` makes `v_D1,v_D2` independent, so they span `span(e3,e4)`.
Likewise, `P4` is non-orthogonal to `P2`, so `v_E1,v_E2` span `span(e1,e2)`.
`P1` is non-orthogonal to both `P3` and `P4`, so `u_B1` is orthogonal (in the
standard bilinear pairing) to `span(e1..e4)`. Hence `u_B1=0`. That contradicts
`M[B1,B1]=1`. QED. (The lemma uses all five non-orthogonal pairs of the cycle and
only one port of `P1`.)

**Theorem.** Let the core be the planes `(13, 23, 35, 16, 34)`, in cycle order.
These planes form an induced 5-cycle of the orthogonality graph. Let `Q` be
these 22 planes:

```text
0 4 8 17 18 19 20 21 24 26 28 29 32 36 38 39 41 42 43 45 46 52
```

The planes of `Q` are pairwise non-orthogonal, and each is non-orthogonal to all
five core planes. For every fitting `K` over every field, the principal
submatrix on the 44 ports of `Q` and the 10 core ports equals
`I_44 (+) M`, because every cross entry is a forced zero. Hence
`rank K >= 44 + rank M >= 44 + 5 = 49`.

The fractional clique explains this. Weight 1 on `Q` and 1/2 on the core sums to
24.5. `verify.py` checks every premise of the theorem from the reconstructed
mask. The stored LP fractional clique `y` coincides with this weighting.

*Second proof of the lemma (Schur complement; found by a reviewer).* Let `S` be
the four ports of `P0,P2`, so `M[S,S]=I_4`. Rank 4 forces
`M = M[:,S] M[S,:]`. Since `M[D,A]=0`, `I_2 = M[D,D] = M[D,C] M[C,D]`, so
`M[C,D]` is invertible; as `M[B,D]=0` this forces `M[B,C]=0`. Likewise
`I_2 = M[E,E] = M[E,A] M[A,E]` forces `M[A,E]` invertible, and `M[B,E]=0`
forces `M[B,A]=0`. Then `M[B,B] = M[B,A]M[A,B] + M[B,C]M[C,B] = 0`,
contradicting `M[B,B]=I_2`.

*Direct LP implications.* The DPs are cross-checks. The stored certificates
already imply the table: `chi >= ceil(chi_f) = 25` (with PR2471's 25-class
witness, `chi=25`), `omega <= floor(chi_f) = 24`, and
`chi_2 >= 2*chi_f = 49` (with the 49 supports, `chi_2=49`).

`verify.py` also corroborates the lemma by exhaustive search. Over GF(2) and
GF(3), the normalised C5 pattern has **no** rank-4 completion. As a control,
freeing the `P1-P3` entries makes a GF(2) rank-4 completion appear, as the proof
predicts. These finite searches are corroboration only. The every-field claim
rests on the proof above.

## Reproduce

From the repository root, with Python 3.12 or 3.14 and only the standard library:

```sh
python3 -I -B research/paired-plane-minrank-bracket-audit/verify.py
```

Expected: a JSON result line, then `PASS_PAIRED_PLANE_MINRANK_EXACT_49`. This
takes about 2 s. The registered hooks are
`python3 scripts/research_package.py --package research/paired-plane-minrank-bracket-audit --check-only`
and the same command without `--check-only` under Python 3.12. The optional
supplementary cross-check
`python3 -I -B research/paired-plane-minrank-bracket-audit/verify.py --two-fold-dp`
prints `PASS_TWO_FOLD_DP_CHI2_49`. It took 72 s and 822 MB peak RSS on this
machine (3,040,597 DP states), so it is not part of the registered replay.
`--write-certificate` regenerates `CERTIFICATE.json` deterministically. The
default mode compares every recomputed check with the stored certificate.

Validated locally with CPython 3.14.4 on Linux: the default verifier, the
optional two-fold DP, the metadata/pin check (`--check-only`) and
`python3 -B -m unittest discover -s tests -p 'test_research_*.py'` (65 tests,
OK). No Python 3.12 interpreter was available locally, so the registered 3.12
replay hook was not run here. Certificate tampering was also tested locally.
Each of these edits was rejected: an emptied support, a non-clique `Q`, a raised
`y` weight, a stored `chi=24`, a non-induced core and a truncated DP order.

**Negative controls (must be rejected; recorded in `CERTIFICATE.json`):**

- a flipped byte in the PR1825 certificate (sha256 pin);
- PR2471's 25 classes merged to 24 (`[36]+[45]`, non-orthogonal);
- a rank-49 support holding both ports of one plane;
- a half weight of the fractional clique raised to 1;
- a fractional colouring with one set dropped;
- a `Q` plane replaced by a plane orthogonal to a core plane (this
  substitution also breaks `Q`'s pairwise non-orthogonality and is rejected by
  that check);
- a `Q` plane swapped (drop 20, add 22) so that `Q` stays pairwise
  non-orthogonal but the new plane is orthogonal to core plane 13 (isolates the
  `Q`-by-core check);
- the core listed out of cycle order.

Solver controls: on the orthogonality graphs `C5` and `C7`, the DPs return
`(omega, chi, chi_2) = (2,3,5)` and `(3,4,7)`.

## Sources and pins

- Base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; see `SOURCES.json`
  for Git blobs and SHA256 values.
- `research/community-frontier1094-audit/selected-replay.tar.gz`, sha256
  `f1da8061...d529d6`. The member
  `candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json` has
  sha256 `c5916ff3...8251fa` and supplies the labels.
- `research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json`,
  sha256 `4fd648f7...1473b1`, supplies the matching.
- PR2471's witnesses are copied into `verify.py` and re-checked there, not
  trusted. They come from `research/paired-plane-scalar-rank-floor/CERTIFICATE.json`
  at PR head `5a7c2b6`, Git blob `1d8a21f3713f2b883ae65d655126732e4f5d54ff`.
  No code from PR2471 or any other package is imported.

## Scope, inherited assumptions, unresolved obligations

- The scope is a finite algebraic statement about one fixed mask. Inherited
  assumptions: PR1825's matching (as pinned by PR1889's fixture) and PR1889's
  strict mask semantics, exactly as stated in PR2471's "Exact model and proof".
  A different matching, a relaxed mask (for example, allowing same-plane
  off-diagonal entries) or a different endpoint contract can change the answer.
- Channel count is not a native copy cost. As PR2471 and PR2203 note, fifty or
  forty-nine scalar channels do not imply any physical saving. No kappa is
  claimed or implied.
- Predecessor status at the base commit: PR1825, PR1889 and PR1977 are merged
  or incorporated; PR2471, PR2126 and PR2203 are open and unreviewed.
- The every-field lower bound rests on the short hand proofs above. The verifier
  checks its combinatorial premises exactly and corroborates the lemma over
  GF(2) and GF(3) by exhaustive search. The lemma is not machine-formalised.

## Open next questions

1. **Native realisation of 49 channels.** Can a fully charged native
   implementation realise a 49-channel scalar fit of this mask below the
   two-unpaid-coordinate budget? This is PR2471's open question 2.
   *Why it matters:* only a native cost can move a supplier price, and 49 is
   now the exact scalar floor. *First step:* price the explicit 49-support fit
   under PR2203's both-payload accounting, including pairing-rank costs and
   scratch restoration. *Blocked by:* there is no accepted native cost model for
   scalar channels of this endpoint.
2. **Other matchings.** Does another perfect matching of the 112 ports into
   nondegenerate planes give a smaller exact fitting rank? *Why it matters:*
   the extra channel above `2*omega` comes from an odd-cycle core; a matching
   whose plane graph has `chi_f = omega` and no such core could reach
   `2*omega`. *First step:* reuse this verifier's model, LP and DP functions on
   restricted rematches (for example PR2118's local rematch, or the plane
   choices in Discussion 1587). *Blocked by:* the space of matchings is large,
   so a restricted search class is needed first.

These are also recorded in `TASK.json`.

## Credit

Predecessors: ywz65 (PR2471: model, bracket and witnesses audited here); Cinna
Davis (PR1825 matched planes, PR2126 scalar identity fit); Adam Gall (PR1889
strict mask); JeremyDiviney (PR2203 native payload accounting); Philippe Van
Velzen (Discussion 1587: orthogonal classes have at most 4 planes; here the
exact maximum is 3); JosieElliston (PR1977, submatrix-minrank method; the
lower bound here is a principal-submatrix argument in that spirit).

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic,
Claude Opus 5.5). Apache-2.0.

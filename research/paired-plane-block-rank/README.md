# Exact block fitting rank for the fixed paired-plane mask

**Scoped algebraic result: minimum rank `49d` for every field and every
positive block size `d`. No native COPY price, supplier or new kappa.**

[PR2484](https://github.com/CrocSwap/integer-mult-bounds/pull/2484), by
thakrarsagar with Claude assistance, determines scalar fitting rank 49 for
PR1825's fixed matching and PR1889's strict plane mask. Its model has scalar
entries. Here each port carries an arbitrary vector in `F^d`, and each free
entry is an unrestricted `d x d` linear operator. The matrix need not be
symmetric, its blocks need not commute, and a common payload eigenbasis is
not assumed. **Even this larger class has normalized minimum rank 49.**

The new part is the all-size lower bound for that enlarged interface. The
upper bound is the credited PR2484 construction tensored with `I_d`, not a
new scalar fit. An explicit noncommuting rank-98 chart conjugate checks the
larger class. A C5 control has scalar minimum 3 but two-dimensional minimum
5, demonstrating that simply multiplying a scalar minimum by `d` would be
invalid in general. This is an application of established block fitting /
fractional Haemers methods, not a claim to invent those methods; see
[Bukh and Cox, On a fractional version of Haemers' bound](https://arxiv.org/html/1802.00476v2),
whose introduction credits the fractional bound to Blasiak. The proof below
is self-contained and uses no theorem or numerical value from that paper.

## Exact contract and orientation

Use the 112 labels and ordered 56 matched plane bases from pinned PR1825.
Let `E_i` be the plane containing port `i`. Rows are target ports and columns
are source ports. A `112d x 112d` matrix `M` over a field `F` fits if

```
M_ii = I_d;
M_ij = 0_d whenever i != j and E_i is not orthogonal to E_j.
```

Both directions of every forbidden pair are zero; on a permitted pair the
two ordered blocks are arbitrary and independent. In particular the two
ports of the **same** plane cannot mix freely. The permission test is the
inherited source-to-target condition `E_j <= E_i^perp`, equivalently all
four basis pairings vanish. Its symmetry comes from that condition, not
from assuming `M_ij = M_ji^T` or reversing a directed decoder.

In the graph convention of the cited block-representation framework, an
edge means a **permitted orthogonal-plane pair**. PR2484's graph `G` instead
uses nonorthogonality edges; these are complementary conventions. We do
not transfer a graph result with the edge convention reversed.

Any linear query layer factoring `M = D T`, with total query-vector
dimension `r`, must have `r >= rank(M) >= 49d`. Thus `m` channels, each of
capacity at most `d` field coordinates, require `m >= 49`. Arbitrary mixing
of finitely many owner/payload coordinates within a port is allowed by
choosing them as `F^d`. This says nothing about an interface that changes
the strict zero mask, supplies additional side information, has unequal
port dimensions, or uses nonlinear encodings.

## All-field, all-size lower proof

**C5 block lemma.** Suppose `N` is a five-by-five block matrix with blocks
of size `L`, diagonal `I_L`, and zero blocks in both directions between
nonadjacent vertices of a cycle of length five. Then
`rank(N) >= ceil(5L/2)`. Adjacent blocks may be nonsymmetric and noncommuting.

Factor `N = A B` through a space of dimension `r = rank(N)`. Write
`A_i: F^r -> F^L`, `B_i: F^L -> F^r`, and `U_i = image(B_i)`, with all
indices modulo five. Because `A_i B_i = I_L`, each `U_i` has dimension `L`
and `A_i` is injective on `U_i`. The two forbidden blocks give
`A_i(U_(i+2) + U_(i-2)) = 0`. Consequently

```
U_i intersect (U_(i+2) + U_(i-2)) = {0}.
```

Set `t_j = dim(U_j intersect U_(j+1))`. The two nonneighbors of `i` are
adjacent to each other, so

```
r >= dim(U_i + U_(i+2) + U_(i-2)) = 3L - t_(i+2).
```

As `i` varies, this gives `t_j >= 3L-r` for every `j`. The two subspaces
`U_i intersect U_(i-1)` and `U_i intersect U_(i+1)` lie in `U_i` and have
zero intersection: `U_(i-1)` and `U_(i+1)` are nonadjacent and hence
disjoint, by the preceding injectivity argument. Thus
`t_(i-1) + t_i <= L`. Combining inequalities yields
`2(3L-r) <= L`, or `r >= 5L/2`. These are inequalities of integer
dimensions, not division by 2 in `F`; characteristic two is included.

**Source-bound theorem.** PR2484 supplies the following witness, rechecked
from the actual binary labels and matching, not accepted as graph input:

```
cycle: 13 23 35 16 34
Q: 0 4 8 17 18 19 20 21 24 26 28 29 32 36 38 39 41 42 43 45 46 52
```

The five cycle planes are orthogonal exactly at adjacent cycle positions.
The 22 planes in `Q` are pairwise nonorthogonal, and every one is
nonorthogonal to every cycle plane. Take the principal submatrix on both
ports of these 27 planes. Its exact form is `I_(44d) direct-sum N`.
Grouping the two ports of each cycle plane gives diagonal `I_(2d)` and
cycle blocks of size `L=2d`; same-plane off-diagonal zeros are essential.
The lemma yields `rank(N) >= 5d`. Rank cannot increase by deleting rows
and columns, so `rank(M) >= 44d+5d = 49d`.

**Attainment.** PR2484's 49 supports partition the 112 ports, and every
support consists of pairwise permitted ports. For its 0/1 fit `K`,
`K tensor I_d` fits. It factors through 49 copies of `F^d`, and choosing
one port per support produces `I_(49d)` as a principal minor. Hence its
rank is exactly `49d` over every field. Together with the lower proof,
this establishes the minimum at every block size, not merely an infimum
or a finite-size extrapolation.

## Executed evidence and controls

`model.py` authenticates source SHA256 and Git blob IDs before parsing.
It reconstructs all planes and the ordered strict mask from the selected
archive and PR1825 matching. `independent.py` reconstructs the permission
mask by enumerating every vector of each binary plane, uses separate
finite-field Gaussian elimination, and applies the vector query circuit
without the dense-matrix helper.

- Every required block entry and an explicit identity minor are checked
  for `d=1,2,3`; exact ranks are corroborated over GF(2), GF(3), GF(101).
- At `d=2`, choose noncommuting unimodular charts on two ports of a
  three-port support. The blocks `K_ij P_i P_j^-1` fit with rank 98.
  All 224 query-action basis columns match the independently assembled
  dense operator. These are algebraic charts, not claimed native adapters.
- C5 attainers for `L=1..8` have ranks `ceil(5L/2)` over the same fields.
  Even `L` uses independent two-coordinate edge channels; odd `L` adds
  the scalar three-class partition. The proof, not these examples,
  establishes the matching lower bound.
- Six rejection checks cover the Q/core boundary, wrong cycle order,
  a one-direction forbidden block invisible to both trace and constant
  payloads, the independent endpoint oracle, its transpose, and diagonal
  normalization. The invisible fault is `[[1,-1],[1,-1]]`: its trace is
  zero and it annihilates `(1,1)`, but it violates the full block contract.
- `check_integrity.py` tests Git-free relocated replay, source-pin
  corruption, typed receipt corruption, and exclusive output creation.

The exact receipt is `RESULT.json`. Run from the repository root using
Python 3.12 or later, standard library only:

```sh
python3 -I -O -B research/paired-plane-block-rank/verify.py
python3 -I -B research/paired-plane-block-rank/check_integrity.py
python3 -I -B scripts/research_package.py --package research/paired-plane-block-rank
```

Expected primary marker: `PASS_PAIRED_PLANE_BLOCK_RANK normalized=49
noncommuting_rank=98 query_columns=224 controls=6`. The hand proof is not
machine-formalized. These checks verify the finite premises and attainers;
they do not search over arbitrary block matrices or independently price a
physical circuit.

## Scope, sources and credit

This is a changed scope from `complex-rank-shape-decoder`: it closes an
algebraic vector-coding escape for one fixed support alphabet, rather than
meeting the card's physical-cost or 5% ceiling gate. No ceiling improvement
is inferred. Rank units count field-coordinate query capacity; they are
not native child rank, COPY charge, bit operations or retained tape volume.
PR2203 already explains why counting support queries omits independent
native payload costs. We construct no frame paths, dirty-target repair,
cleanup, precision budget, all-size supplier or multiplication theorem.

Base main is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
`SOURCES.json` binds main inputs. `VENDOR.json` binds the unmodified
PR2484 certificate and README at head
`4823273c8163e4c72472bdf7d42202e2c12d2e46`, retaining its attribution.
No predecessor executable is imported. PR2484's scalar49, cycle/Q witness
and 49 supports remain its contribution. PR2471 (ywz65 with Codex)
provided the preceding scalar [48,50] bracket; PR1889 (Adam Gall) the
strict scalar mask audit; PR1825 (Cinna Davis / 1337isnot1337) the fixed
matching and original binary decoder. The selected construction and
native payload accounting retain their repository attribution.

Selection and overlap details are in `TASK.json`: the assigned first
P104 path was retired because PR2251 had already closed its 96/97 gap.
The rank-shape first working ceiling command passed. A fresh REST PR
scan found the scalar predecessor and physical accounting above; the
last complete Discussion snapshot is explicitly stale because GraphQL
was rate-limited. Absence of an overlap match is not a novelty proof.
The final 734-PR scan also found concurrent PR2525, which formalizes the
fixed two-port C5 four-pivot Schur obstruction in Lean. That is distinct
from the arbitrary-block-size dimension inequality here. PR2532 audits
the scalar endpoints of different three/five-dimensional group masks;
it does not supply this fixed paired-plane block minimum.

Authored under ywz65 using OpenAI Codex for proof development, code,
verification and prose, with separate Codex peer review. This is AI
review, not independent human review. New work is Apache-2.0; retained
predecessor files keep their original notices and attribution.

## Open next questions

1. Can a different matching or physically justified endpoint mask lower
   normalized block fitting rank? First produce its exact directed mask
   and test whether the Q/C5 obstruction survives; inherited zero-copy
   permissions cannot simply be dropped.
2. Can the 49-vector algebraic attainer be implemented at useful native
   cost? Start by binding every support's independent payloads, native
   input/output charts and restoration bill, as required by PR2203.
   This package supplies no price or legal native chart implementation.

Structured questions and blockers are also recorded in `TASK.json`.

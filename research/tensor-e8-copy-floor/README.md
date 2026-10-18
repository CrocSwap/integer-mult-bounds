# Tensor E8 decoder mixing has copy-rank floor 72^d

**Scoped negative result; no new kappa.** For the fixed full-E8 binary decoder
matrix `B`, every factorization of `B` tensor-powered `d` times into the minimum
`9^d` scalar totals has copied-information rank sum exactly **`72^d`**. This
includes arbitrary nonsymmetric, nonseparable changes of total basis across
the tensor factors. Such changes cannot improve the canonical tensor decoder's
copy-rank budget. The conclusion holds at every integer depth `d >= 1` by the
proof below, conditional only on the explicitly stated copy-tree model when
interpreted as a physical cost bound.

The new step is tensor stability of the full-span support property, followed
by its application to arbitrary minimal factorizations. The depth-one floor
is predecessor work: GamingPuzzled's #620 and Chi Zhao's #631. This package
also supplies a portable exact check of that finite premise, without the
NumPy floating rank routine used by #620's `geo.py`.

## Reproduce

From the repository root, with Python 3.10 or later and no external packages:

```sh
python3 -B research/tensor-e8-copy-floor/verify.py
```

Expected:

```text
PASS_TENSOR_E8_COPY_FLOOR: 511 exact base minors; 162 tensor supports; 8 negative controls; cost 72^d
```

Each run checks source hashes and compares the complete regenerated result
against `RESULTS.json`. To write a separate receipt, append
`--write /tmp/tensor-e8-copy-floor.json`. Checks remain active under `python3 -O`.
The default command writes nothing. The receipt's 511 exact minors can also
be checked independently using just integer determinants.

## Object and cost model

Let `u_i` be the 120 rational E8 root-line representatives in dimension eight,
in the norm-four Hamming coordinates used by the repository. Define over F2

```text
B_ij = 1 + (u_i dot u_j)/2  (mod 2),       C = columnspace_F2(B).
```

The checker generates the eight coordinate lines and the 112 signed affine
plane lines of F2^3. It binds their set and all 14,400 binary pairings to the
pinned #531 prototype. Thus its ordering is local, but the geometry and binary
matrix agree with the predecessor. `B` is symmetric, has diagonal one and
binary rank nine. Every nonzero `c in C` has rational support span

```text
span_Q {u_i : c_i = 1} = Q^8.                              (F)
```

There are exactly 511 such words: 255 of weight 56, 255 of weight 64 and one
of weight 120. These finite facts are checked exhaustively, with a nonzero
8-by-8 integer minor for each word. The rational rank calculation and the
fraction-free determinant calculation are separate algorithms.

At depth `d`, ports are tuples `I = (i_1,...,i_d)`, physical lines are
`u_I = u_i1 tensor ... tensor u_id` in `V_d = (Q^8) tensor-powered d`, and
the **fixed matrix under study** is `B_d = B tensor-powered d` over F2.
Its binary rank is `r_d = 9^d`. This is the rank of this matrix, not a
minimum over every decoder compatible with the product geometry.

The matrix has the required algebraic support for orthogonal corrections:
its diagonal is one, and for distinct ports with nonzero physical inner
product, every factor inner product is nonzero and at least one factor is
an off-diagonal E8 pairing. That factor's entry of `B` is zero, so the
entry of `B_d` is zero. Hence `I + B_d` is supported on orthogonal pairs.
This observation supplies no correction circuit or paid schedule.

A scalar-total decomposition is

```text
B_d = sum_j a_j b_j^T  (over F2).
```

Total `j` gathers sources `P_j = supp(b_j)` and is delivered to readers
`Q_j = supp(a_j)`. Set

```text
beta_j = rank_Q(pairing(span_Q u[P_j], span_Q u[Q_j])),
C_pair = sum_j beta_j.
```

Theorem C of DreamingOfClouds' [#446 proof, section 4](https://github.com/CrocSwap/integer-mult-bounds/blob/309482849b6ddf34db998f53612d34c19f6e3233/research/format-obstructions/PROOF.md)
is the physical-model dependency: a retained total gathered without drops,
then delivered through its own copy tree to readers at orthogonal frames,
pays at least `beta_j` in drops. This package does not re-prove that theorem
or establish its applicability to a different compiler. Per-total costs are
added under that model. Dynamic mixing between different totals during their
delivery is outside this claim.

At the base commit the review ledger marks #446 **unreviewed**, and #620
**partially reviewed**. The algebraic statement (1) does not depend on their
approval or solver results: its premise is independently checked here and
its linear algebra proof is below. Its physical drop-cost interpretation
explicitly inherits #446's model and written theorem.

## Proof at every tensor depth

**Tensor-support lemma.** Let binary codes `A <= F2^S`, `D <= F2^T` have
rational physical labels `v_s in V`, `w_t in W`. Suppose every nonzero word
in each code has support spanning its entire physical space. Then every
nonzero word of `A tensor D` has physical support spanning `V tensor W`.

View a word `z` as a binary matrix `(z_st)`. Each row lies in `D`, so a
nonzero row at `s` contributes support vectors spanning `v_s tensor W`.
Choose any nonzero column. It is a nonzero word of `A`; its support spans
`V` and is contained in the set of nonzero rows of `z`. Summing the spaces
`v_s tensor W` for those rows therefore gives all of `V tensor W`. This
argument allows arbitrary sums of pure tensors; it makes no separability
assumption about `z`. Induction and (F) prove the property for `C^tensor d`.

**Minimal-factorization lemma.** If an F2 matrix `M` has rank `r` and
`M = A D^T` with exactly `r` columns in each factor, then every column of
`A` lies in `columnspace(M)` and every column of `D` lies in
`columnspace(M^T)`. Indeed `rank(A) = rank(D) = r` and
`columnspace(M) <= columnspace(A)`; their dimensions agree. The transpose
gives the other statement. All columns are nonzero. This proof does not
require the factors to be equal or the matrix to be positive definite.

Apply this to `B_d`. Its row and column spaces are both `C^tensor d`,
and its rank is `9^d` by multiplicativity of matrix rank over a field.
The tensor-support lemma says every source support and every reader support
of any minimal factorization spans the entire `8^d`-dimensional rational
space. Its Euclidean tensor pairing is nondegenerate. Hence every
`beta_j = 8^d`, and

```text
C_pair = 9^d * 8^d = 72^d.                                (1)
```

An explicit rank factorization of `B`, tensored `d` times, attains (1) as
a pairing-rank objective. Dropping each retained total from the full frame
to zero costs `8^d`, so it also attains the per-total copy-tree drop bound
when those root frames are available. This is not a full supplier schedule:
source access, gathering, restoration, helpers, inter-stage work and recursive
calls still require their own charges and legal interfaces.

There is also an overcomplete corollary **with a code constraint**. If both
factors of every nonzero summand are required to belong to `C^tensor d`,
every term still costs `8^d` and at least `9^d` terms are required by rank.
Thus no such overcomplete label decoder beats (1). General overcomplete
factorizations need not obey the code constraint and are not covered.

## Optimistic budget and stopping rule

The proposed mechanism was to reduce copy expense by rebasing several tensor
units jointly. Its best possible copied-information budget is already the
canonical one:

| Depth d | Ports | Minimum totals | Rank per total | Copy-rank sum |
|---:|---:|---:|---:|---:|
| 1 | 120 | 9 | 8 | 72 |
| 2 | 14,400 | 81 | 64 | 5,184 |
| 3 | 1,728,000 | 729 | 512 | 373,248 |

The normalized copy cost is `(3/5)^d`. The result preserves the existing
tensor scaling; it only rules out improving that expense through the stated
basis mixing. Even granting all basis changes, source accesses, extra helpers,
restorations and recursive work for free cannot make `C_pair` smaller. A real
implementation must charge all those operations and cannot obtain a positive
copy saving from this mechanism. We therefore stopped before building a
supplier. No inference about a better helper schedule or a different stage
structure follows.

The selected #626/#543 assembly at the base is complex-bound, with complex
lower endpoint `65528268492323474503/40000000000000000000000` and bit lower
endpoint `413456747036699736067/250000000000000000000000`. A hypothetical
bit-only copy improvement would still require checking that binding constraint;
this result supplies no improvement on either side.

## Finite evidence and negative controls

The verifier covers:

- All 120 base roots, all base binary pairings, rank nine, and all 511 nonzero
  base-code supports, each with a committed exact determinant witness.
- One depth-two factorization changed by 243 elementary invertible basis
  operations drawn deterministically with seed 43. The other factor receives
  the inverse-transpose changes. It checks all **207,360,000 binary entries**
  of the resulting matrix identity via complete bit-packed row equality, and
  all 162 producer/reader supports using nonzero 64-dimensional minors modulo
  three. A nonzero modular minor proves the rational minor is nonzero.
- Every nonzero word in a separate `[3,2]` toy code at depths one and two
  (3 and 15 words). Its rational labels are `(1,0), (0,1), (1,1)`.
- Eight mandatory negative controls: corrupt root norm, corrupt diagonal,
  omitted independent total, repeated minor row, one-root puncture, an
  unrestricted overcomplete factor outside the code, degenerate physical
  pairing, and a missing inverse-transpose update.

The one-root puncture is a real boundary example: remove root zero from the
support of its own `B` row. The remaining 63 roots have rational rank seven.
Thus the full-span hypothesis cannot simply be reused for punctured units.
Likewise `B = sum_i e_i (row_i B)` is a valid 120-total factorization whose
`e_i` factors are outside `C` and have rank-one physical supports. This
invalidates extending the per-term rank-eight assertion to unrestricted
overcomplete factorizations; it is not a cheaper decoder.

The finite depth-two run is a control, not exhaustive coverage of all changes
of basis. Universal coverage comes from the two written lemmas. This is not
a proof-assistant formalization or a proof of integer multiplication.

## Provenance, scope and handoff

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Assignment seed **43**
was drawn once using OS randomness; `CLAIM.json` records task selection and the
local claim. No pinned coordination issue existed. `SOURCES.json` pins source
bytes and predecessor/overlap heads. No repository generator, selected record,
or `upstream/` file is changed.

Predecessors and concurrent work retain credit:

- DreamingOfClouds' #446 supplies the per-total copy-tree rank lower bound,
  following Jacob Sussman's frame model and the E8 work of Dylan Crow and the
  community contributors credited there.
- Joel Pulikkan / GamingPuzzled's #620 identifies the full-E8 depth-one floor.
  Chi Zhao's #631 supplies exact puncture thresholds and the reader census.
  The depth-one result is independently corroborated here, not newly claimed.
- icekylinx's #531 package supplies the pinned Hamming-coordinate prototype;
  eumemic's #543 is the selected bit supplier. The selected complex construction
  and allocation remain credited to their #622/#623/#626 predecessors.
- Artus' #647 and Scott Woolsey Biggart's #682 concern a separate paid complex
  RAM tensor provider and its rate. They are overlap checks, not dependencies
  or constructions ruled out by this binary decoder theorem. #669, #703,
  #715 and #717 also have different geometry or factorization scopes.
- Russell Seligmann's concurrent #757 gives a solver-free copied-rank
  certificate for the actual P111 fixtures and corrects a root-order mismatch.
  Its punctured single-unit scope differs from this full-unit tensor result.
  Here root coordinates and all prototype pairings are matched explicitly;
  no predecessor's numeric puncture list is used.

Outstanding possibilities include changing `B_d`, puncturing/relabeling,
unrestricted overcomplete factorizations, and interacting delivery programs
that do not have the per-total copy-tree discipline. None is searched here.
All inherited all-size, compiler, hosting, restoration, precision/tape and
analytic obligations of the selected multiplication result remain unchanged.

Prepared for Douglas R. Colkitt with substantial **OpenAI Codex assistance**
in the mathematics, implementation, verification and writing. No independent
human review is claimed. GitHub submission uses the authenticated contributor
account **@Mister-Meeseeks**. New files are licensed under the repository's
Apache-2.0 license; no predecessor implementation is vendored or imported.

## Validation receipt

Local runs passed on Python **3.14.6** (normal, optimized and isolated modes)
and **3.13.0**, with the same complete JSON receipt. A separate implementation
generated affine planes as four-element subsets with XOR zero, and recomputed
all 511 committed determinants by Fraction elimination without importing
`verify.py`. Two additional packaging controls rejected an incorrect source
hash and a mutated determinant receipt. Selected-record integrity and whitespace
checks passed. Final overlap inspection covered 581 open PRs; main and the
selected frontier were unchanged.

The repository-wide `make verify` and selected supplier cold replay were not
run: this contribution changes only its new research package, and its affected
checks are the command above and selected-record integrity. No hosted CI pass
or formal verification is claimed.

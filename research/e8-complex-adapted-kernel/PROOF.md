# Paid residual adapters with distinct borrowed families

This is a conditional finite construction under the inherited exact Gaussian
rank-zero compiler and analytic interfaces. It supplies explicit local and
global operator arguments for the new construction. It does not assume that
an isotropic entrance is orthogonally conjugate to a coordinate entrance.

## 1. Exact kernel and common-frame realization

Start with PR433's R560 split-centre complex word, freshly rebuilt through
PR454/451. The frozen PR449 selection partitions its chosen helpers into
14 disjoint classes. In each class a rank-one entrance E is contained in the
first frame of every donor and pivot. Exact elimination verifies every
response relation `col(p) = sum_d q_d col(d)`. Donor columns are independent;
pivots and donors have disjoint roles, including across classes.

Insert `d <- d - q_d p` at E before the old main word, let p start at E,
and rebuild the complete full-frame cleanup as the exact inverse of all
non-target gates. There are 79 pivots and 229 inserted additions. The new
response of each pivot is zero, so zero-frame dirty compensation never reads
a helper whose entrance is nonzero. The literal emitter and independent
label audit check this condition rather than assuming it. All coefficients
are dyadic and every scalar operand pair shares its actual current frame.
The rank-one entrances are isotropic; no coordinate-entrance test is used.

`rebuild.py` reconstructs all gates and their exact coefficients from the
parent word and the frozen selection. It recomputes the frame chains and
paid profile. Only two old floating discovery estimates are copied as
non-semantic metadata; their final bits vary by platform and they are never
used for reconstruction or pricing. The exact word and all its mathematical
inputs are compared to the frozen output. Both scalar orientations are
replayed on all 800 columns, including every initial target and dirty helper.
The forward result is `(x,h,y) -> (x,h,y+x)`; the other is the inherited
inverse-transpose result `(x,h,y) -> (x-y,h,y)`.

For a local binary frame F, let T_F be the canonical Clifford representative
in the retained `clifford_exact.py`. Its definition and exact lowering for
arbitrary, possibly degenerate subspaces are part of the inherited finite
realization. A climb A -> B applies `T_B T_A^-1`. Common-frame scalar gates
commute with the common T_F. Induction through the emitted program therefore
gives the scalar matrix conjugated by its current block-diagonal labels.
Every centre copy, directed centre child and cleared work lifetime is
explicit. The new 2,932 phase-edge equalities and all 240 data endpoint
adapters are checked, including global phase.

A helper beginning at E and ending at FULL consequently has physical
residual

```
S_E = T_FULL T_E^-1.
```

This formula means apply `T_E^-1` first, then `T_FULL`. The initial label is
an interpretation of its arbitrary physical input: if that input is h, its
logical scalar value is `T_E^-1 h`. No T_E entrance transform is executed or
silently charged as rank zero. We remove the upstream emitter's generic
helper adapter placeholders and retain the checked data endpoint adapters.
The independent auditor rejects missing paid wrappers and wrong labels.

Both scalar orientations leave every helper row equal to its input and
use the same helper frame chain. Thus both have the same residual S_E;
the backward scalar orientation does not replace it by S_E^-1.

## 2. Two-sided monomials, including their exact phase

For each of the 14 nonzero canonical entrance frames, exact Clifford
lowering gives

```
S_E = L_E (C_[w] tensor I) R_E,       w = 9 - dim(E) = 8.
```

L_E and R_E are explicit Gaussian monomials: invertible binary address
permutations, quadratic phases, translations and a scalar power of i.
The tableaus and a nonzero exact Gaussian state vector agree, which fixes
the otherwise undetermined global phase. The independent adapter audit does
not call the lowering generator: it decodes the serialized monomials and
checks the complete product against the canonical S_E.

Apply `R_E^-1` before the entire local invocation and `L_E^-1` after its
full-frame cleanup. The exact residual becomes

```
L_E^-1 S_E R_E^-1 = C_[w] tensor I.
```

For the 481 helpers with E=0, S_E is already C_[9] and both adapters are
identity. There are 158 nontrivial wrapper events per call, 13,904 across
all 88 calls. Wrong width, wrong pre-adapter order and wrong global phase
are rejected. The 79 nonzero entrances have no additional recursive child:
C_[w] here is the proved normal form of their already charged local climbs,
not a second invocation appended to the program.

These are two-sided paid adapters, not an orthogonal conjugation of S_E.
They may mix the selected eight axes with one spectator axis. Their complete
product restores the spectator identically, for arbitrary input data.
This distinction is essential for isotropic entrances.

## 3. Routing and why simultaneous borrowing is valid

Use the unchanged 11-stage dimension 89 data geometry, five data pairs and
eight replicas. There are 1,200 data families per replica. At a local call,
its 240 active data families and all 560 borrowed helper families are
pairwise distinct. The frozen assignment enforces **at most one helper per
physical data family in that call**. It hosts every one of the 49,280
helper occurrences without a bank or padding child.

The windows are derived from the complete schedule. A borrowed host pair
is not the active pair. Its invocation lies strictly after the host pair's
last data invocation or bridge and before the relevant pending idle child.
Every assignment has its own width-eight or width-nine interval. Every
helper occurs once, intervals within one idle child are disjoint, and the
one-helper rule is checked independently of coordinate-slot disjointness.
A mutation that packs two helpers into disjoint slots on one family in the
same call is explicitly rejected.

For the host's port q, the parent supplies the orthonormal basis
`B_q = U_q direct_sum I`. Let its assigned pending interval contain vectors
`b_1,...,b_w`. Choose the first w columns of sigma to be those vectors. Add
the first unused basis vectors until its first nine columns are specified;
these are the local spectator coordinates. Append all other unused basis
vectors in order. Hence sigma is a permutation of B_q, belongs to O(89,2),
and is completely specified by the recorded nine indices. The independent
audit checks the parent basis, every selected vector, the spectator and
completion, and all 49,280 route instances.

Use the inherited convention `g = d sigma^-1` for the owner cover class.
Right multiplication is a bijection on O(89,2). At local cover class d,
the helper residual is `P_d (S_E tensor I) P_d^-1`. The paid wrappers are
`P_d (R_E^-1 tensor I) P_d^-1` and
`P_d (L_E^-1 tensor I) P_d^-1`. Since d=g sigma, their complete effect is

```
P_g P_sigma (C_[w] tensor I) P_sigma^-1 P_g^-1
  = P_g (product of C_b over the assigned pending vectors b) P_g^-1.
```

The equality includes global phase and identity on all spectators. The
route only permutes an orthonormal basis. Nonorthogonal address maps occur
inside the separately charged Gaussian monomials; they do not relabel the
orthogonal cover classes.

Because each helper has a different physical family within the call,
these before/after wrappers act on distinct streams. For a fixed family,
d -> g is a bijection, so different d invocations in the same cover sweep
also have distinct owners. No two simultaneously realized logical variables
are identified. The all-column local theorem applies to arbitrary borrowed
values, including values correlated with active data or other idle streams.
The local data result is independent of those helper values, and each helper
has the displayed block-diagonal residual.

After a complete call, the host therefore has only its assigned coordinate
factor. Factors from different calls use disjoint pending coordinates and
commute. They also commute with the retained idle translations. The remaining
idle child fills the unassigned coordinates, and the parent's exact phase
correction is left unchanged. The original idle operator is recovered.
Intermediate monomials need not commute with earlier stored data: their
complete wrapped map is proved for every input, and no other helper aliases
that host during the call. This is why the one-helper rule is required here.

## 4. Complete program and independent verification

The same signed bridges, data route corrections, terminal translations,
signed exchange and all-live cover correction are retained and rechecked.
There are 8,520 exact data/idle/terminal phase equalities, 1,320 orthogonal
data routes and 24 omitted bridge-shear controls. Ten exact global integer
data rows compose to the identity; combined with the two independent local
800-column theorems and the distinct-owner argument above, this establishes
the finite scalar/physical template uniformly over all ports and cover
classes. It is not an enumeration of the astronomical complete cover.

The emitter serializes both pre/post monomial recipes at each renamed
physical owner. The independent decoder recomputes the instruction digest
from the local records, owner tables and exact adapter recipes. It checks
2,107,512 events and rejects 25 global mutations. Seven additional local
controls check adapters, common labels and restored helper rows.

A fresh default regression runs the generalized PR449 checker/emitter on
the unmodified parent. Its newly emitted local programs and local checks
are exactly equal to the parent. The only canonical metadata differences
are an empty target-level map and explicit centre-edge inventory; that
inventory is independently derived. Copied parent global files are not used
as evidence of regenerated local programs.

## 5. Paid profile, finite costs and outer assembly

The exact complex profile is

```
rank       1      2     3      4      5     6     7     8  16  46    64
count 175744  82016  4968  20344  37072  1264  2568  7264   8 512  1912
```

Its rank mass is 851,136 and `89*9,600 - 851,136 = 3,264`. There are 9,600
live families and 10,178 physical families, including the unchanged restored
private reserve of 560 tableau,16 centre and 2 coefficient families. The
largest child remains64. The inherited bound `89^9 > 16*64^9`, including
its additive depth constant, retains row allowance 20,161 for
`log2(width) >= 32`; the already retained finite leaves cover smaller widths.

Every wrapper is charged eight restored rank-zero compiler groups. Two
cover-coordinate permutations and the fixed monomial's diagonal, address
permutation, translation and scalar phase use at most six such groups;
two further groups cover owner/window selectors. The invoice deliberately
charges pre and post wrappers for all 560 helpers, not just the 79 pivots:
`2*560*8*88 = 788,480` groups. This overcharge is added explicitly to the
new local primitive counts, existing route/phase charges and all bridge,
terminal, work and cover-correction costs. No extra persistent work survives
a child. The local bound is 18,687,781,085,682<2^48; the router takes 11,850
bits and the literal charge 37,859 bits, within the retained2^30000 and
2^100000 limits. The2^210000 precision guard and three-level envelope pass.

Two independent rational moment engines certify

```
b >= 0.001297203880559577927527
```

and reject the upper interval endpoint one 10^-24 step later. The complete
fresh PR454 bit verifier supplies
`c = 0.001275657818793753037875`, which now binds. Both finite invoices,
six exact bootstrap levels and all 47 strict outer constraints give

```
kappa = 1274032589159993 / 10^18 = 0.001274032589159993.
```

The next10^-18 grid point and zero-eta, zero-beta and unit-beta controls fail.
This is 0.591885% above PR454. The local/all-size Gaussian compiler,
restored-work, fine-grid, precision, row-divisor and analytic interfaces
remain conditional. No unconditional multiplication theorem, new Lean
proof or kappa=1 claim follows from these finite certificates.

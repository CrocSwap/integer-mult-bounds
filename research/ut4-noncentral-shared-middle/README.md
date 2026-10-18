# Disjoint UT4 root targets cannot share the middle-generator bill

**Sharp formal-algebra theorem; no new supplier or kappa.** For `p` target
roles carrying `u=I+E13` and `q` different roles carrying `v=I+E24`, in the
restricted `UT4(F2)` alphabet below, every word pays

```
n_x >= 2p,   n_y >= 2(p+q),   n_z >= 2q.
```

The direct `4(p+q)`-call word attains all three bounds simultaneously, for
every finite `r>=p+q>0`. All extra roles may contain arbitrary dirty inputs
and must be restored. The result includes every nonzero binary rank-one
scalar coupling, both idempotent and nilpotent, and arbitrary free scalar
mixing. Thus nonnegative uniform label prices `alpha,beta,gamma` give the
exact tariff `2p alpha + 2(p+q) beta + 2q gamma` in this model.

In particular, **the minimum in Cinna Davis's [PR1761](https://github.com/CrocSwap/integer-mult-bounds/pull/1761)
is eight**, not five, six or seven. That predecessor proves a four-register
length-at-most-four exclusion and gives the eight-call upper witness. This
successor closes its explicit gap by a written all-register argument, not a
larger finite search. It does not claim the predecessor's construction or
bounded exclusion as new.

## Model and complete formal bill

Use one-based address indices and let

```
G = UT4(F2),   R = F2[G],
x = I+E12,   y = I+E23,   z = I+E34,
u = xyxy = I+E13,   v = yzyz = I+E24.
```

The roots `u,v` are noncentral: `[u,z]=[x,v]=I+E14`. The group has 64
elements. Equality below is equality in the **full formal group algebra**,
not equality only in a natural representation or on one small address set.
For scalar register count `r`, an allowed paid factor is

```
D_N(g) = I_r + ([g]+1)N,
g in {x,y,z},   N=a b^T != 0,   a,b in F2^r.
```

There is no restriction on `b^T a`. Since `g` is an involution,
`([g]+1)^2=0`, so every paid factor squares to identity even when `N` is
nilpotent. All inverses are charged occurrences, not free undo. All scalar
register inputs are arbitrary; the target is

```
T = diag([u] repeated p, [v] repeated q, [1] repeated r-p-q).
```

Free operations are scalar `GL_r(F2)` maps only. Move them to one end by
conjugating the `N`s; rank one is preserved. Augmentation `[g] -> 1` sends
every paid factor and `T` to identity, forcing that final scalar map to
identity. The displayed alphabet therefore includes every normalized word.
This standard normalization is credited to the preceding register-model work.
No free address map, clean allocation, COPY, ERASE or higher-rank paid call
is permitted.

The upper word applies `x,y,x,y` on each `u` coordinate and `y,z,y,z` on each
`v` coordinate, with coordinate-projector couplings. Each four-call product
is exactly its formal group monomial; different scalar roles do not interact.
It uses `p+q` data roles, no additional workspace or scalar preparation, and
exactly `2p,2(p+q),2q` calls; appended dirty roles stay identity. No restoration
outside this word is omitted.

This is a **complete abstract paid-call bill**, not a physical supplier
invoice. Frames, common labels, hosting, precision/tape and recursive
interfaces have not been realized. Their costs are not declared zero. No
selected paid profile, moment or multiplication exponent is improved.

## Proof: the simultaneous middle span, not two added bounds

All ranks and scalar spans are over `F2`. Let
`P=diag(I_p,0,0)` and `Q=diag(0,I_q,0)` in `M_r(F2)`. Their column spaces
are disjoint of dimensions `p,q`; their row spaces are likewise disjoint.
Write products in **left-to-right matrix order**. For labels `a,b` define

```
S_a  = sum_{i: g_i=a} N_i,
C_ab = sum_{i<j: g_i=a,g_j=b} N_i N_j.
```

### Two necessary group representations

Apply the natural representation `rho(g)=g` entrywise and group coordinates
into four address blocks of size `r`. The `(1,2),(2,3),(3,4)` blocks of the
product are `S_x,S_y,S_z`, respectively. The `(1,3),(2,4)` blocks are
`C_xy,C_yz`. No term of degree three can enter either of those two blocks.
The formal target consequently forces

```
S_x = S_y = S_z = 0,     C_xy = P,     C_yz = Q.       (1)
```

Use also the contragredient representation
`rho_dual(g)=(g^-1)^T`. It is a homomorphism because inverse and transpose
each reverse multiplication. Since the three generators are involutions,
their images are `I+E21,I+E32,I+E43`. The target roots are involutions too,
with images `I+E31,I+E42`. Reading the `(3,1),(4,2)` blocks gives

```
C_yx = P,     C_zy = Q.                               (2)
```

The inverse is essential: transpose alone would be an antihomomorphism.
These representations are used **only for necessary lower-bound
conditions**. They cannot certify a formal endpoint; the verifier includes
a nonzero formal perturbation annihilated by both.

### One rank-nullity argument for the shared label

For a label `a`, write all its rank-one matrices as `N_i=a_i b_i^T` and
collect

```
X_a = (a_i)_i,      Y_a = (b_i^T)_i.
```

Thus `X_a` has `n_a` columns, `Y_a` has `n_a` rows, and
`X_a Y_a = S_a = 0`. Rank-nullity in the intermediate `F2^{n_a}` yields

```
rank X_a + rank Y_a <= n_a.                           (3)
```

Each summand in `C_ab` has column space in `im X_a` and row space in
`row Y_b`. Therefore (1) and (2) force these inclusions:

| Scalar span | Required target subspaces |
| --- | --- |
| `im X_x`, `row Y_x` | respectively `im P`, `row P` |
| `im X_z`, `row Y_z` | respectively `im Q`, `row Q` |
| `im X_y` | **both** `im P` (from `C_yx`) and `im Q` (from `C_yz`) |
| `row Y_y` | **both** `row P` (from `C_xy`) and `row Q` (from `C_zy`) |

The last two lines are the new shared-middle step. A single `X_y` must
contain the **sum** `im P + im Q`, of dimension `p+q`, and a single `Y_y`
must contain the analogous row-space sum. It is not legitimate merely to
add two separate estimates on the same calls. Applying (3) instead gives

```
n_x >= p+p,     n_y >= (p+q)+(p+q),     n_z >= q+q.
```

The explicit upper word attains every bound. This proves the theorem for
all finite register counts and word lengths, including arbitrary dirty
workspace, without an exhaustive search or an unquantified extrapolation.
Scalar conjugation preserves the direct-sum dimensions, so the same proof
also applies to a simultaneous scalar conjugate of the target.

### Why the disjoint-role hypothesis matters

Putting both root actions on **one** role is a different endpoint:
`[uv]`, not `diag([u],[v])`. In fact the full formal identity

```
xyzxyz = uv
```

costs only six calls and two middle calls. Its two root coefficients occupy
the same scalar subspace, of dimension one rather than two. This is a
positive countercontrol to dropping disjointness, not an improvement on the
stated two-role target. In contrast, `xzyxzy` also has the desired degree-two
coefficients but acquires the nontrivial `E14` term. The verifier distinguishes
these endpoints in the full algebra.

## Executable evidence and reproduction

The package's standard-library checker uses exact binary arithmetic. Its
primary representation is a scalar matrix of 64-bit formal coefficient
vectors. A second engine uses literal binary 4-by-4 address matrices and
replays the faithful left-regular action on **every** address/register basis
column, including dirty workspace. It imports no primary arithmetic.

Finite controls corroborate the proof and implementation; they do not prove
the unbounded theorem. `CERTIFICATE.json` records the complete deterministic
finite coverage. `VALIDATION.json` records only commands actually exercised.

The deterministic evidence contains:

| Check | Exact exercised domain |
| --- | --- |
| Group law and contragredient homomorphism | All 4,096 ordered group pairs each |
| Expanded rank-one alphabet | 284 matrices at `r=1,2,3,4`: 155 idempotents, 129 nilpotents |
| Involutions and faithful single-call action | 852 calls; 204,672 regular basis columns |
| Coefficient recurrence and span inclusions | All 20,440 two-register words of length `0..3` over 27 factors |
| Attaining formal/faithful witnesses | 34 fixtures through eight roles; 8,896 dirty basis columns, including two non-coordinate scalar conjugates |
| Semantic controls | 18: eight omitted calls, wrong label, dirty restoration, rank/label/type violations, a genuine rank-two shortcut, common representation kernel, overlapping targets, and wrong class-three term |

The coefficient census has lengths `1,27,729,19683`; its canonical coefficient
digest is `b94b89bf4f84879a0dd3c7b55a553b7eeaf553855dcba33d702db719832783f8`.
It is not a search excluding lengths five through seven: the written span
proof excludes those lengths and all other short words uniformly.
The verifier recomputes and compares the complete certificate, read-only by
default; `--emit` prints it without modifying files. All semantic guards
remain active under `-O`.

From the repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/ut4-noncentral-shared-middle/verify.py
uv run --python 3.12 --no-project python -I -B scripts/research_package.py --package research/ut4-noncentral-shared-middle
```

The card's working example `scripts/research_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, with the complex primitive binding.
That checks selected source bindings and arithmetic, **not** the selected
cold replay. No native supplier, all-size realization, Lean, independent
human proof review or hosted CI pass is claimed.

## Provenance, novelty and attribution

Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. One unforced chooser
invocation sampled OS nonce `5080ba3917adb12fda1e688c38733a49`, selecting
`bit-mechanisms`; [SELECTION.json](SELECTION.json) preserves the entire emitted
record. [TASK.json](TASK.json) records the two proposed cards, actual refined
scope, cost screen, stopping rule, overlap coverage and claim. The public
[successor claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1759#discussioncomment-18925851)
links the [round coordination thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1929).

- **Cinna Davis (@1337isnot1337), PR1761**, head
  `0f4f6d79b14573116e47d31d012f8e3f7a49cd87`: exact noncentral pair,
  four-register `q<=4` exclusion, eight-call upper word and explicit gap.
- **steph4n-gh, PR1573**, head `0b8c5a69297c794f2de22c04494c83e41300ae36`:
  UT3 all-register theorem using two representations and zero-sum scalar
  rank-nullity. Those tools, rather than their reinvention, are used here.
- **Arham Tahir, PR1589**, head `010ec8c01c0edbbb08b541be236ab78d096f2ca1`:
  UT3 nilpotent rank-one extension and mixed-coefficient proof.
- PR1662/1680/1690/1816 treat the **central E14 target**, a different
  class-three constraint. This proof neither replays nor settles their claims.
- Credit @woklerx's PR1443, @juper997's PR1478, Gareth Davidson/@bitplane's
  PR1333, and the eumemic/Ali Romman/David Govea register-model lineage.

[SOURCES.json](SOURCES.json) pins source provenance and contextual predecessor
heads. No predecessor code is imported, frozen evidence is unchanged, and
no selected-frontier file is edited. Cached overlap covers 579 open PRs and
547 discussion records with complete pagination, plus local notes; exact
relevant heads were read live. This is not a claim of literature priority or
a novelty guarantee from search absence. The new result is the simultaneous
shared-middle obstruction and exact resolution of the existing noncentral
pair gap, not a second presentation of the UT3 theorem.

## Open next questions

Can an actual bit-supplier implementation realize this restricted nonabelian
alphabet at a favorable **complete** tariff and with the needed target
interface? The first useful step is one explicit realized `x,y,z` call family,
with every frame transition, dirty-state restoration and recursive/precision
charge counted. The absence of such a realization blocks a supplier claim;
more dirty registers or a longer search in the current disjoint-root model
cannot lower the proved abstract bill. A formally cheaper enlarged primitive
must be priced rather than simply assigned unit cost.

Prepared for **Adam Gall** with substantial **OpenAI Codex GPT-6 Astra**
assistance in research, proof, implementation and writing. The two executable
representations are AI-assisted work from the same session, not independent
human review. New work is Apache-2.0; predecessor notices remain unchanged.

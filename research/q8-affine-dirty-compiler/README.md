# An executable Q8 action with a sparse dirty-register invoice

**Partial interface result; no supplier admission or new kappa.** This answers
the first local step in `q8-mixed-uniform-tariff`'s native-realization handoff:
implement one concrete eight-address action, including scalar preparation and
restoration, and expose its costs. It supplies an in-place finite-array
compiler for every Q8 label and every rank-one binary **idempotent** coupling.
It does not supply the selected multiplication construction's native interface.

The added result is the executable affine encoding, a sparse coupling compiler,
and their exact combined invoice. The affine-rank lower bound below is an
application of Gareth Davidson's [PR1333 theorem](../binary-affine-register-bound/README.md),
not a new reflection-length theorem. Existing Q8 word minima are not rerun.

## Boundary and invoice

There are `r >= 1` distinct arbitrary dirty arrays, each with eight address blocks of
`B >= 1` bits. Blocks are contiguous and equally sized; no routing or location
conversion is granted. Let `N = u v^T`, with binary nonzero vectors satisfying
`v^T u = 1`. The required complete operator is

```
D_N(g) = I + N (P_g - I),
```

where `P_g` pushes address `h` to `g h` in the regular Q8 action, independently
at every payload position. Every role's entire output must equal this formula.
In particular, roles with `u_k = 0` return to their original dirty arrays.
No auxiliary payload array, clean input, COPY or erasure is required.

For a nonidentity label, the emitted schedule uses exactly

```
C = 2 (wt(u) + wt(v) - 2) <= 4(r-1)   whole-array XORs,
S = 4 for g = -1; S = 6 otherwise     B-bit block swaps.
```

Each swap is explicitly three XORs, so the data bill is **`8 B C + 3 B S`
bit XORs**, with every source preserved by each XOR. This is the emitted
algorithm's bill, not a minimum XOR-circuit claim. The swap count is minimal
among arbitrary address-block transpositions: a permutation of eight points
needs `8 - number_of_cycles` transpositions. Identity emits no instructions.

The implementation stores `O(r)` instruction descriptors, or `O(r log r)`
bits, plus loop indices of `O(log(rB))` bits. Data work is `O(rB)` XORs and
cell accesses in the declared random-access model. Address arithmetic,
allocation of the input arrays, tape layout, physical hosting, stock and
recursive/compiler tariffs are not included. There is no zero-cost claim for
these obligations. The Python reference and symbolic test arrays allocate
additional evidence storage; that storage is not part of `run_program`'s
in-place data algorithm.

The program's inverse is its instruction list in reverse order. Q8 letters of
order four must not be treated as involutions; executing the forward program
twice generally gives the central action, not restoration.

## Uniform derivation of the sparse compiler

Choose a coordinate `p` with `u_p = v_p = 1`, which exists because `v^T u=1`.
Write `U=u+e_p`, `V=v+e_p`, and define

```
L = I + U e_p^T,     K = I + e_p V^T,     T = K L.
```

Both `L` and `K` are involutions, since `U_p=V_p=0`. Executing `L` means
`row_k ^= row_p` for every nonpivot one of `u`; executing `K` means
`row_p ^= row_k` for every nonpivot one of `v`. These take
`wt(u)-1` and `wt(v)-1` whole-array XORs, respectively.

We have `L u=e_p` and `K e_p=e_p`. Also `v^T L=v^T`, since
`v^T U=v^T u+v_p=0`, and `v^T K=e_p^T`. Consequently

```
T u=e_p,   v^T T^-1=e_p^T,   T N T^-1=E_pp.
```

Apply `L`, then `K`, then `P_g` to role `p`, and undo `K`, then `L`.
The resulting operator is `T^-1 D_Epp(g) T = D_N(g)` on arbitrary inputs.
This proves the formula for every finite `r`, every legal `u,v`, every Q8
label and every payload width, without a finite-search assumption. It also
works for any linear address operator substituted for `P_g`.

The general basis-conjugation method and dirty-state obligation are inherited
from [dihedral-arbitrary-couplings](../dihedral-arbitrary-couplings/README.md).
That package gives a Gaussian implementation with a quadratic bound. Here the
explicit two-star factorization gives the stated linear, support-sensitive
invoice for idempotents; no claim is made for nilpotent couplings or globally
optimal scalar XOR count.

## The affine encoding and its pricing consequence

Encode `z^s i^x j^y` by the three address bits `(x,y,s)`, with `z=-1`.
For `g=z^c i^a j^b`, Hamilton multiplication gives

```
(x,y,s) -> (x+a, y+b, s+c+(a+b)x+b y)   over F2.
```

It is a shear `H_g: s += (a+b)x+b y`, followed by the translation
`T_g: (x,y,s) += (a,b,c)`. For the six noncentral labels, both factors have
homogeneous displacement rank one and their product has rank two. For `z`,
the shear is identity and the nonzero translation has rank one. Acting on
`1` recovers `g`, so this action is regular, and its group-algebra action is
faithful: a formal sum applied to the identity-address basis vector recovers
every coefficient. Full dirty-array equality is checked with this regular
action, not merely with four-dimensional homogeneous matrices.

| Q8 target | Its positive `{i,j}` word length | Its `{i,-i,j,-j}` word length | Rank-one affine factors | Swaps in this implementation |
| --- | ---: | ---: | ---: | ---: |
| `1` | 0 | 0 | 0 | 0 |
| `-1` | 2 | 2 | 1 | 4 |
| `i,j` | 1 | 1 | 2 | 6 |
| `-i,-j` | 3 | 1 | 2 | 6 |
| `k,-k` | 2 | 2 | 2 | 6 |

The first two price columns are credited to the prior Q8 census, not new
minima. The affine column uses the **expanded** alphabet of all affine maps
with `rank([A-I | b])=1`. It does not assert those operations cost one selected
supplier child. In particular, pricing `i` as a single such primitive is
false, whereas the central target is directly available as one translation.
The construction `i i` spends four affine factors to do what that translation
does in one. This is a boundary calibration, not an objection to the abstract
Q8 word results, whose alphabet and price rule are different.

For completeness, the inherited rank argument certifies the affine column:
normalize scalar basis changes by augmentation, apply the homogeneous affine
representation, and use `rank(AB-I) <= rank(A-I)+rank(B-I)`. Every allowed
rank-one affine/idempotent factor has represented displacement rank one.
A diagonal tuple has rank equal to the sum of the displayed ranks, including
zero for restored spectators. The explicit shear/translation words attain
that bill. Thus in this **expanded abstract alphabet**, no number of restored
dirty roles lowers the sum for these Q8 targets. This specialization is
already implied by PR1333, whose source and attribution are retained.

## Replay and failure controls

From the repository root, standard-library Python 3.12 or newer:

```sh
python -I -O -B research/q8-affine-dirty-compiler/verify.py
python -I -O -B research/q8-affine-dirty-compiler/test_verify.py
python scripts/research_package.py --package research/q8-affine-dirty-compiler
```

Normal replay is read-only. `verify.py --emit` prints a recomputed receipt;
it never writes `RESULT.json`. The committed receipt covers every idempotent
through six roles: `1,6,28,120,496,2016`, all eight labels, **21,336 operators
and 969,792 input columns**. Another 24 packet fixtures check **3,840 columns**
at payload widths 2, 3 and 7. Symbolic bit masks propagate every basis input
simultaneously, so arbitrary dirty inputs follow by linearity. Forward and
inverse programs are both checked. Hamilton integer-tuple multiplication
builds the reference independently of the affine implementation.

Four actual semantic mutations must fail: omitted restoration, using the
inverse as the forward action, wrong label and wrong pivot. Three invalid
coupling controls and the affine underpricing control also run with `-O`.
The tests inject actual compiler mutations, check a noncoordinate positive
fixture with dirty spectators, and exercise optimized CLI replay from a
minimal Git-free export, receipt type corruption/missing evidence, source
corruption and read-only output preservation. Source SHA256 and Git blob
identities are checked before computation. The generic runner additionally
checks historical provenance and manifest inputs.

Local direct replay used CPython 3.14.6 and registered replay used CPython
3.12.10, both on Windows. Tests used a workspace-local
`TMP`/`TEMP`, because this sandbox's default temporary directory denied child
directory creation. No hosted CI, Lean, independent human review,
selected cold replay or full supplier validation is claimed.

## Scope, overlap and next questions

The task draw, changed scope, failed preliminary scout, exact base and input
pins are in `TASK.json` and `SOURCES.json`. The claim/result lives in
[the existing Q8 investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-18991111).
No predecessor archive, selected record or frontier is changed. The initial
complete overlap cache covered 258 open PRs and 1,889 Discussion records at
07:06/07:07 UTC on October 17, 2026; bodies, comments and retained local notes
were checked, not every code diff or every closed PR. A no-match is not a
novelty certificate. The pre-submission refresh covered 261 open PRs and 1,892
Discussion records at 07:16/07:18 UTC; no new matching compiler artifact was
found. TASK.json records the snapshot limitations and the narrow family decision.

## Open next questions

- Can a specific recursive caller legally supply these contiguous eight-block
  arrays and preserve their ownership across the compiled operation? First
  bind one caller's layout, time cuts, payload widths and restoration contract,
  then charge routing and scalar XOR work. This matters before any claimed
  supplier saving; no such caller is supplied here. Stop if the complete bill
  cannot beat that caller's direct alternative.
- Can the scalar preparation be shared across a named consecutive sequence of
  equal projectors without breaking its chronological dirty boundary? First
  compare a literal two-call sequence with separately compiled and coalesced
  basis changes, charging the endpoint permutation and every external use.
  The unresolved caller access/ownership contract is the blocker. This is a
  conditional implementation question, not a recommendation to enlarge a Q8
  word census or expand the family before its complete budget exists.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in derivation, code,
verification and writing; no subagents or independent human review. Credit
ywz65 for the mixed-Q8 handoff and Gaussian dirty-coupling implementation;
Gareth Davidson/bitplane for PR1333's affine model and exact rank theorem;
Aaron Wang for PR1822/2318's Q8 models and pricing; Cinna Davis for the related
Q8 target results; and the retained eumemic/PR288, Ali Romman/PR468,
steph4n-gh/PR1573, Arham Tahir/PR1589 and other source lineage. No literature
priority claim for the elementary encoding or basis conjugation is made.
New work and retained repository inputs are Apache-2.0.

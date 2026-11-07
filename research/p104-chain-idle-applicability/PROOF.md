# Whole idle jobs through changing ordinary field bases

## Result and exact scope

This note resolves the **finite whole-job applicability** question in
CrocSwap/integer-mult-bounds#6833, `PROOF.md` section 6 and `ADAPTERS.md`, for its
literal `(9|9)` caller at commit
`ad24ad966b857dbfed50d9121624db84b2eccc92`. It supplies a direct carrier trace
through the actual scalar instructions and an explicit lowering of all sixteen
merged idle jobs to the retained canonical Gaussian job interface. Each job
works at every positive column multiplicity. The ordinary field bases do not
become unpriced recursive adapters.

This is a conditional application result, with **No new κ**. It does not prove
the entire compiler, admit the complete #6833 supplier, or discharge
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, or
`analytic_recovery`. The native two-field interface and permitted physical
implementations are inherited. The exact arithmetic here establishes the new
idle/field-frame obligation given those interfaces. A mathematical proof is
given below; the finite computation binds its hypotheses to the frozen word.

The predecessor's abstract chain-merge lemma is credited to DreamingOfClouds;
we do not present it as a new result. The new certificate independently derives
all field frames from the emitted ordinary gates, proves transport of the
**actual arbitrary payload** between successive native boundaries, and matches
each paid occurrence to the written compiler's one-owner job type.

## 1. Field coordinates and address coordinates are different spaces

Fix a port and a positive integer `f`. Let `V_f` be the space of arbitrary arrays
on all `153f` binary address coordinates, including all spectators. The caller
state belongs to `K^20 ⊗ V_f`, with `K=Q(i)`. The twenty copies are distinct
physical fields. A matrix `B` on the twenty field labels acts as `B ⊗ I`; its
integer scalar coefficients do not acquire powers of `f`.

For a field index `r`, write `e_r` for its coordinate column and
`E_r=e_r e_r^T`. Applying an address operator `W` to that one field is

```math
J_r(W)=I_{20}\otimes I+E_r\otimes(W-I).
```

The rank of `E_r` is one **in field space**. It is not the recursive Gaussian
rank of `W`. In this package those recursive ranks range from 8 to 64, and at
column multiplicity `f` the corresponding job has `8|Wset|f` address axes.

The fresh stage-`s` address set, for `1<=s<=18`, is

```text
J_s = {9+8(s-1), ..., 16+8(s-1)}.
```

These eighteen sets are pairwise disjoint. At multiplicity `f`, replace each
axis `a` by `(a,c)`, `0<=c<f`. The stage operator is the positive Gaussian product
`D_s,f` on those `8f` axes. It fixes every other address coordinate. All `D_s,f`
commute with each other and the central `Q_f`.

The central normalization is the **total-operator** polynomial

```math
\lambda_f=\frac{1+i}{2}I+\frac{1-i}{2}Q_f^2,
\qquad S_f=\lambda_f Q_f^{-1},\qquad S_f^2=I.
```

The retained native contract gives `Q_f^4=I`. The field scalar program remains
outside the tensor powers. In particular, replacing `λ_f` by a factorwise
tensor power of a one-column `λ` would be wrong. This distinction and its
explicit two-factor counterexample were already established in @CubeJerry's
CrocSwap/integer-mult-bounds#6763; see retained `PHYSICAL-PROOF.md` section 4.
No new normalization claim is made here.

## 2. A literal moving-frame interpreter

Maintain an invertible field matrix `F` so that the current physical tuple is
`v=F u`, where `u` is the logical tuple after the already processed address
kernels. Initially `F=I`. An ordinary `ADD`, `SCALE`, or `SWAP` instruction with
matrix `O` updates `F` to `OF`, leaving `u` unchanged.

The four consecutive instructions

```text
LAMBDA(dst,-1)
LOCAL(stage,src,dst)   [or QUERY(dst,src,-1)]
LAMBDA(dst,+1)
ADD(dst,src,-1)
```

form one kernel. The exact pattern is checked, including the correction ADD.
That ADD belongs to the kernel, not to the ordinary frame program. In the
physical `(dst,src)` pair the full kernel is

```math
(v_{dst},v_{src})\longmapsto
D_{s,f}(v_{dst}+(S_f-I)v_{src},v_{src}).
```

For a thin query omit `D_s,f`. Consequently its logical map is `F^{-1}KF`,
with no specialization of `Q_f` or any `D_s,f`. The frame remains `F`.
Define

```math
x=F^{-1}e_{dst},\quad y=e_{src}^TF,\quad
\Pi=F^{-1}(E_{dst}+E_{src})F.
```

The full logical map is

```math
G_s=(I+\Pi\otimes(D_{s,f}-I))
    (I+xy\otimes(S_f-I)).
```

The independent interpreter uses this decomposition directly on the frozen
1,237-event `CALLER.json`. It imports no constructor, Laurent replay, shadow
interpreter, native checker, or pricing implementation. In particular it never
sets `Q=±1` or `D=1` to extract a frame.

It obtains 21 kernels, 1,117 ordinary basis gates, sixteen single-field idle
occurrences, and 62 ordinary normalizers: 42 inside the 21 kernels and twenty
final normalizers. It verifies every full and thin
coupling against the stated field vectors and checks that the complete ordinary
frame returns to identity. At each idle occurrence on physical register `r`,
it derives

```math
\phi=F^{-1}e_r,\qquad \gamma=e_r^TF,\qquad E=\phi\gamma.
```

Thus the **literal** job has logical action `I+E⊗(W-I)` on all twenty arbitrary
inputs. This statement does not assume that any input or intermediate payload
is zero or statistically independent of the other current values.

## 3. The actual carriers and their ordinary transport

Use the logical fields `A=0`, `f_i=1+i`, `h_i=10+i`, `Eempty=19`.
The extracted lines, duals, covered stages, and physical carriers are:

| Line | Logical image and dual | Covered stages | Physical carrier at site |
|---|---|---|---|
| Left `j`, `1<=j<=8` | `φ=f_(j-1)`, `γ=f*_(j-1)-2A*` | `j+1,...,9` | register `j+1` at every covered stage |
| Right `j`, `0<=j<=7` | `φ=h_(j+1)`, `γ=h*_(j+1)+2A*` | `10,...,10+j` | register `j+2-m` at stage `10+m` |

Each actual idle is paid immediately after the first covered kernel, on its
listed physical carrier. The full receipt lists the sixteen event indices and
each exact carrier sequence. There are 72 line/site incidences and 56 adjacent
covered-site transitions. Twenty-eight transitions on the right change the
physical register number.

The checker enumerates **all** kernels between the first and last covered
kernel and requires that inventory to equal the declared stage list; no thin
query or uncovered native kernel is crossed. It also checks the sixteen
ordinary segments from the completed host kernel to the literal idle event,
including their unit carrier row and column. Other idle occurrences within
these segments commute by the separately checked orthogonality of their
projectors.

At each covered native boundary the checker establishes **both**

```math
F_k\phi=e_{r_k},\qquad \gamma F_k^{-1}=e_{r_k}^T,
```

and checks that `r_k` is outside the two native registers. Equivalently, both
columns and both rows of the actual native plane annihilate the line:
`Π_k φ=0`, `γ Π_k=0`. The query coupling is contained in that plane, so
`xy φ=0` and `γ xy=0` too. This is stronger than merely identifying a line
in a specialized execution.

Let `O=F_(k+1) F_k^-1` be the complete ordinary transition between successive
covered kernels. It then satisfies

```math
Oe_{r_k}=e_{r_{k+1}},\qquad
 e_{r_{k+1}}^TO=e_{r_k}^T.                 (1)
```

Equation (1) says that the indicated row and column are unit rows/columns.
For arbitrary arrays, the transition transports the old carrier's payload
unchanged to the new carrier and transfers no other field into it. The verifier
checks the actual transition matrices: 112 unit row/column identities.

Individual elementary instructions within `O` may temporarily mix the carrier.
They are already present and charged in the caller. One need not pretend that
these individual gates preserve a physical register. Only the complete ordinary
transition is used when sliding a whole address operation. From (1), for every
address operator `Z`,

```math
(O\otimes I) J_{r_k}(Z)
   =J_{r_{k+1}}(Z)(O\otimes I).            (2)
```

The intervening native kernel acts as identity on the carrier and its dual,
so it also commutes with `J_(r_k)(Z)`. This is a physical carrier proof of the
allowed movement through the actual word, including the register changes on
the right.

The sixteen projectors are mutually orthogonal, and at each native site the
checker establishes the exact identity

```math
P_k=\Pi_k+\sum_{\ell:\,k\in C(\ell)}\phi_\ell\gamma_\ell,
```

where `P_k` is the declared coordinate stage support. The corresponding
one-stage idle factors therefore supply exactly the part of `D_k,f` outside
the native active plane. Applying (2) within the declared cover, and using
`J_r(U)J_r(V)=J_r(UV)`, merges them into the literal single job

```math
J_{r_{first}}\left(\prod_{s\in C(\ell)}D_{s,f}\right).
```

Factors for different idle projectors commute. No factor is moved past an
uncovered active site or a thin query. This gives the construction-to-literal
binding for the predecessor's chain-merge argument.

### Why the dual condition matters

Preserving an image line alone does not imply (1) or (2). For example, on two
fields `O=[[1,1],[0,1]]` fixes `e_0`, but `e_0^T O != e_0^T`. For any nonidentity
address operator `Z`, `O J_0(Z)` and `J_0(Z) O` differ on the second input.
Our mutation on the **actual** first left line keeps `φ` and `γφ=1`, but changes
`γ` to `γ+y_k`; its dual then meets the native active plane and is rejected.
A separate control rejects sliding that line through the preceding uncovered
native site. These are failures of altered hypotheses, not counterexamples to
#6833's actual word.

## 4. Explicit whole-job Gaussian lowering at every multiplicity

For an idle with stage set `Wset`, put `J=union_(s in Wset) J_s` and `r=|J|`.
Distinct stages give `r=8|Wset|`, including the rank-48, rank-56, and rank-64
jobs. Their scalar field projector still has rank one.

Let `K={0,...,r-1}`. Pair the sorted sets `J\K` and `K\J`, and exchange each
paired coordinate. The exchanges are disjoint and define an involutive
coordinate permutation `p` with `p(J)=K`. Both boundaries of the following
program are present:

```text
apply the address permutation p to the current owner field
execute one canonical positive Gaussian job on coordinates 0,...,r-1
apply the inverse address permutation p to that same field
```

At multiplicity `f`, use `p_f(a,c)=(p(a),c)`. The middle job is **one** rank-`rf`
job, not `f` separately credited rank-`r` jobs. The input and output maps are
permitted fixed binary coordinate maps; no mixing of different field arrays is
passed to a recursive child.

For completeness, the standard coordinate Gaussian on axis `a` has eigenvalue
`i^(z_a)` on Fourier character `z`. The desired idle therefore has eigenvalue

```math
i^{\sum_{a\in J}\sum_{c=0}^{f-1}z_{a,c}}.
```

The conjugated canonical job has the same exponent, since `p_f` maps those
axes bijectively to the first `rf` coordinates. Its net Fourier permutation is
identity and its phase at zero is `+1`. This proves exact equality on every
Fourier character, hence every arbitrary input, with all spectators restored.
No exponentially large dense matrix or finite sample of columns substitutes
for this proof.

The checker independently verifies the full net permutation and every
coefficient of this linear phase polynomial, including its constant, at
`f=1,2,3`. Those finite checks corroborate the descriptor implementation;
the displayed coordinate identity proves all positive `f`.

Splitting a requested rank after canonicalization uses consecutive disjoint
pieces inside the middle job and keeps the two outer permutations around the
**entire** replacement. This is precisely the retained whole-job splitting
interface. An output-only normalizer fails: its net permutation is not identity.
Both missing-boundary variants and a wrong absolute phase are tested.

## 5. The written compiler contract and chronology

The exact inherited contract is retained byte-for-byte as
`retained/FINITE-PRECOMPILATION.md`, especially sections 1, 3, 4 and 6. Its job
definition is a specified tensor operator on selected coordinate blocks of one
array at arbitrary positive multiplicity. Its whole-job adapters are permitted
address maps/phases and role permutations. Sections 3 and 6 require the child
to finish and restore its adapters before the suspended parent resumes. They
explicitly allow the current value in a physical owner field to be correlated
with other fields; they do not provide productive credit for a copied input.

The job just constructed meets that interface directly:

- It acts on one actual `IDLE_ONE` owner at one actual paid position.
- Its only recursive boundary adapters are the two specified address maps.
- The ordinary field mixing belongs to the surrounding fixed parent word and
  stays where the literal word puts it. It is not an adapter between units.
- The child receives arbitrary current data, finishes the complete requested
  positive transform, and returns with its own adapters restored.
- It uses no new owned field, no copied productive input, and no new output
  credit. All sixteen occurrences remain separate, at every port.

In particular, the compiler's prohibition on combining different paid positions
of a suspended instance is respected. The raw caller was first changed by a
proved algebraic construction; the compiler receives its resulting chronological
list, including each single merged idle as an individual position. This audit
does not combine that position with any other compiler request.

There is no numerical upper-rank restriction such as 40 in this job definition.
Here each rank is at most 64 and fits the **actual** 153-axis carrier, and the
explicit maps supply the required geometry. The general uniform compiler's
other hypotheses remain separate. In particular, the raw mixed unit does not
satisfy its strict paid/productive separation directly; the predecessor's
chronological product, completion and splitting argument is a distinct step.
We do not reverify that step's global ambient bounds, constants, native sources,
full invoice, or outer inequalities in this narrow application certificate.

## 6. Every new boundary cost is accounted for

Each idle occurrence is present at all 104 ports. The exact inventory is

```text
paid idle jobs = {8:208,16:208,24:208,32:208,
                 40:208,48:208,56:208,64:208}
number of jobs = 1,664
Gaussian address rank mass = 59,904
```

The left-side jobs require `17,25,33,40,32,24,16,8` coordinate exchanges on
each boundary. The right-side jobs require `8,16,24,32,40,48,56,64`. Thus

```text
2 * 104 * (195 + 288) = 100,464 two-coordinate exchanges.
```

At the retained 1,000-unit allowance per elementary exchange, this is
`100,464,000` ordinary units. No full 153-axis permutation is charged as a single
small map. Its individual exchanges are all charged on both boundaries.
No additional scalar field wrapper is introduced by our lowering.

The complete existing caller envelope is independently recounted as
`32 * 20 * 104 * 1237 = 82,334,720`. The 1,117 ordinary basis gates are a subset
of those 1,237 events; all their coefficients are integers of absolute value at
most 3 and all SCALE gates are signs. The carrier-transport proof neither removes
these gates from the count nor inserts extra ones. The remaining native,
normalization, tape and precision costs retain the source's separate premises;
this is not a new proof of the physical 1,000-unit rate or the full caller's
precision envelope.

## 7. Provenance, independent method and limitations

The all-one caller, its chain-merge lemma, complete supplier and proposed
conditional price belong to DreamingOfClouds in #6833. The common-idle lineage
is thu-nmrc's #6716 and #6726. The native work retains zxv's, Cinna Davis's,
Ali Romman's and @CubeJerry's contributions, including #6763 and #6805. The
finite compiler is Jacob Alan Sussman's Theorem 1G and its retained source chain;
all compiler text and notices remain intact. `SOURCE-PINS.json` gives exact
commits, paths, Git blob IDs and SHA256 for every retained file.

The previous `independent/check_root.py` binds lines using a specialized
`Q=±1, D=1` shadow, together with separate formula checks. This verifier instead
factors the actual word into unspecialized address kernels and moving ordinary
frames, checks both active-plane annihilations, and proves payload transport
through 56 whole transitions. It does not import or rerun the predecessor's
checker as its mathematical method. The canonical exchange construction and
its rates are inherited; their independent recount supports the new application
binding and is not claimed as a new routing algorithm.

The retained snapshots make the narrow replay self-contained. The standalone
verifier checks their byte hashes and Git-blob encodings. It does not authenticate
remote publication ancestry, fetch unmerged history, run the full native word,
reprice κ, or formalize the entire theorem in a proof kernel. The result covers
this exact caller and these sixteen stage sets. It is not a universal license
to merge arbitrary caller positions, use only one preserved line without its
dual, or replace scalar coupling rank by Gaussian address rank.

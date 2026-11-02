# Round 1 checkpoint: the two-anchor scalar preparation

**Status: in progress.** This note records the bounded local checkpoint for
the frozen PR6372 pair construction. Full emitted-word endpoint/restoration,
whole-word owned lifetimes, productive debits and native applicability remain
for round 2. This checkpoint is not a completed supplier audit or a new
admitted kappa.

## Exact scalar scope

The input is PR6353 at `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`.
The candidate is PR6372 at `b556600ffe14be72406b03a47c661f3c7f1aff06`.
`SOURCE-PINS.json` binds both literal words, the candidate witness, constructor,
proof and notice. The source constructor is retained as data, not imported
as independent evidence.

Use 770 arbitrary independent public scalar inputs over `Q`. Owned labels
are inactive until zero initialization at `INIT`; `CLEAR` discards an owned
row in the scalar projection. `MOVE` preserves scalar values. The reversed
scalar transcript exchanges ADD source/destination and INIT/CLEAR, reverses
MOVEs and main-pair roles, and relabels the extreme frame identifiers 3 and
127. Nonextreme identifiers, including 245 and 1091, remain labels here.
This checkpoint does not compute or certify native frame complements,
absolute phases or positive-width native maps.

Call the declared zero-preparation label `Z=3`, the full label `Omega=127`,
the new entrance label `F=245` and common departure label `G=1091`. Let
`A` be the complete scalar map extracted from the input's actual `Z`
transcript, with owned initialization/lifetimes respected. It includes
the source's prior nine preparation temporaries. It must not be replaced
by a cached prefix from an older word.

The independently extracted source transcript has 4,709 events: 4,358 ADDs,
333 SCALEs, nine INITs and nine CLEARs. It includes the old construction's
later ZERO-frame dirty-carrier subtraction, in addition to its earlier
4,708-event prefix. Structural checks require unique public ZERO departures,
no public return to ZERO, no owned transport through ZERO, and valid active
labels and common scalar-frame labels in the actual input chronology.

## Matrix convention and the invertible input basis

Scalar values form a column `x`. An operation `ADD(r,s,c)` means
`x_r <- x_r+c*x_s`, so a chronological basis sequence `B2`, `B0`, `A`, `C`
has matrix `C A B0 B2`.

Let `a=224`, `b=227`, and

```
v   = e227 + e228 - e229 - e232 + e233 - e238 + e239 - e449,
u_a = 2e224 + v,
u_b = 2e224 - v.
```

The first four B0 operations send the anchor values to
`(2*x_a+2*x_b, x_a-x_b)`. The remaining operations add signed copies of
that second value to the seven other listed coordinates. Consequently
the two anchor columns are exactly `B0 e_a=u_a` and `B0 e_b=u_b`.
On the anchor block,

```
H = [[2,2],[1,-1]],       det(H)=-4,
H^-1 = [[1/4,1/2],[1/4,-1/2]].
```

After placing the other coordinates last, B0 has block form
`[[H,0],[V,I]]`, so `det(B0)=-4`. This is a unit of `Z[1/2]`; the whole
basis is invertible with dyadic coefficients. Every B0-touched coordinate
must independently belong to the input's full-helper set, determined from
its actual main-role list and boundary labels, not from its numerical index.
There are 372 such full-helper channels in this frozen input, within 562
non-main public helpers.

## The changed departure block and full-row identity

The frozen C operations form `row193+row742/2` and `row169+row742/2`, swap
them into physical anchors 224 and 227, then add both anchor rows to row 204.
These are reversible dyadic ADD/SWAP operations in one first-departure
group. Their coefficient calculation retains all 770 public coordinates,
including arbitrary main/interface inputs. It does not specialize the
contact rows' old values to zero.

Rows 169, 193 and 204 are actual main roles. Row 742 is a non-main helper
whose declared scalar-dual boundary is ZERO to 1091, so it is not a full
helper. C is therefore **not** required to use only full helpers. That
restriction applies to B0 and the off-anchor correction supports. The
actual departure group 1091 contains
`169,193,204,224,227,229,234,742,753,754,755,761`.

Write `c_r=e_r^T C A` for an anchor departure functional. The local audit
checks complete coefficient rows in

```
c_a B0 = e_a^T+d_a,
c_b B0 = e_b^T+d_b,
```

including zero coefficients. The witness's off-anchor rows have respectively
13 and 10 nonzero coefficients; each support must lie in the independently
derived full-helper set outside `{a,b}`. In particular,
`d_r e_a=d_r e_b=0`. Checking only a two-by-two anchor pairing would not
establish this support condition or arbitrary-input restoration.

Set

```
N  = e_a d_a + e_b d_b,
B2 = I-N.
```

The off-anchor condition gives `N^2=0`, hence `B2^-1=I+N`. Moreover
`e_r^T N=d_r` and `d_r N=0` for each anchor, so

```
c_r B0 B2 = (e_r^T+d_r)(I-N) = e_r^T.
```

B2 also fixes both anchor columns: `B2 e_a=e_a`, `B2 e_b=e_b`.
These elementary nilpotent-correction facts are retained general linear
algebra; the new evidence is their exact coefficient binding to this source.

## Zero scratch does not specialize the actual public inputs

Let `E_P=e_a e_a^T+e_b e_b^T` and `T=I-E_P`. Replacing the two anchor
positions by zero owned scratch during the preparation evaluates

```
u = C A B0 B2 T x.
```

The anchor row identity implies `u_a=u_b=0` for every `x` in `Q^770`.
The actual public inputs `x_a,x_b` are held separately and remain arbitrary.
Because B2 fixes their columns, the missing response is

```
C A B0 B2 E_P x = C A B0 E_P x.
```

The full nonzero response rows are

```
119:  2*x_a + 2*x_b,
224:  x_a,
227:  x_b,
232: -2*x_a + 2*x_b.
```

Adding these responses gives `C A B0 B2 x` on every public coordinate.
Algebraically applying C^-1 then gives `A B0 B2 x`. Invertibility of B0 and
B2 supplies the eventual formal inverse order: chronological B0^-1 then
B2^-1 has matrix `B2^-1 B0^-1`. Binding the complete emitted suffix and
inverse tail, and proving the full public endpoint, are round-2 obligations.

The local preparation checks the nine source-owned zero lifetimes on labels
770 through 778 and the two new zero lifetimes on 779 and 780 at their actual
dual `CLEAR`s. This is an eleven-row **dual preparation** statement. It
does not assert that forward `CLEAR`s erase zero scalar functionals and
does not supply physical owned-erasure permission.

## Binding to the actual candidate prefix

The primary checker reconstructs the candidate's first 4,759 dual events
from the independently extracted source transcript, the frozen elementary
bases and the explicit anchor-to-shadow renaming. It compares every
instruction to the actual reversed candidate word. The length decomposes as

```
2 new INITs + 23 B2 events + 11 B0 events + 4709 source events
+ 12 expanded C events + 2 new CLEARs = 4759.
```

The scalar interpreter then checks the complete public coefficient row at
each of its eleven actual CLEARs. The separate oracle reconstructs those
same functionals backwards and independently verifies that every coefficient
on the 770 arbitrary original public inputs is zero. No source constructor
or earlier campaign verifier is imported.

Three actual-prefix omission/sign faults in the primary produce nonzero
CLEAR-row witnesses; the oracle checks both omission and sign at three
sites, for six such witnesses. These faults reach coefficient evaluation,
rather than being rejected only by a source hash or changed event count.
The primary also checks the abstract basis inverses and gives an unequal
coefficient after omitting one B0 inverse operation.

A fifth primary control removes the final in-memory C operation
`ADD(204,227,1)`. Both complete corrected anchor unit rows remain unchanged,
but the recomputed response on MAIN row 204 has input-227 coefficient −1
instead of zero. Its first destination is 1091, outside the permitted 245
nonprimary response block. This source-specific control shows why the full
response support must be checked in addition to the anchor identities.
It is a departure-basis algebra control, not an executed literal-prefix
failure or a physical impossibility claim.

The witness's subsequent 30-event response bridge is **not replayed by this
round-1 checkpoint**. The response table and algebra above identify what it
must restore. Binding that actual bridge, its source suffix and the emitted
inverse tail, followed by the full arbitrary-input endpoint, remains for
round 2. The current result must not be reported as a completed endpoint
audit.

## Checkpoint boundary and predecessor credit

The local result needs the actual input ZERO transcript and lifecycle,
full-row basis/support identities, actual candidate preparation, and any
claimed response-bridge binding. Source hashes or a valid detached BASIS
file cannot substitute for those checks. A subsequent full endpoint audit
must preserve all 770 public inputs and track the complete emitted word;
this note does not infer that result from the local checkpoint.

Native complement/phase rules, full operator columns, physical caller
contacts, erasure, signed paid/productive debits, complete ordinary funding,
compiler/outer admission and a new kappa remain unproved here. The selected
frontier is unchanged. The five framework assumptions `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery` remain.

Ali Romman, with substantial OpenAI Codex assistance, supplied PR6372's new
pair contraction and PR6353's joint-basis construction. Retain PR6349/6348,
DreamingOfClouds, Cinna Davis and the full `sources/NOTICE` chain. B7 PR6355
supplies the separate independent nine-anchor audit on the earlier word;
it is neither rerun as a new result nor transferred automatically to these
changed contact rows. Unpaidmoon's Cursor Grok-assisted stage-1 contact,
ordinary-allowance and G20 handoffs have separate scopes and retain their
credit. The present checkpoint is prepared for ToikY with substantial OpenAI
Codex assistance and separately assigned exact evaluators and mathematical
review. Same-session agent review is part of the author process, not
independent human or formal acceptance.

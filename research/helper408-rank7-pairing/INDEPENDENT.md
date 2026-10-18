# Independent inverse-column and chronological row certificates

The proposed rank-seven replacement of PR2908's first paired extraction is
impossible with its pinned PR2894 middle word and the declared protected
entrances. Both admissible terminal spaces are zero, independently in the
`base` and `extra` providers. Two small exact restrictions prove this without
depending on the full nullspace calculation.

This check was derived before reading `verify_boundary.py` or `BOUNDARY.md`.
It imports neither file, nor any predecessor Python module. After obtaining
the result, the primary proof was cross-read: its forward forbidden-input
minor agrees with the independent chronological row calculation below.

## Fixed domain and actual cut

The scientific sources are Jeremy Diviney's PR2908 at
`51309592971e3b5be935599eed2a95404dc7781e`, carrying Jeremy Kothe's PR2894
providers at `18d03c447886895ef9abf888398178e0428533ca`. Each direct replay checks
both SHA256 and Git-blob identities for all five used data files against
`SOURCE-PINS.json`; these two commit identifiers are also fixed in the checker.

All non-target input values are arbitrary. The scalar coefficient domain is
`Q`, which contains the proposed dyadic domain. Warps are independent invertible
noncommuting operators; only adjacent inverse symbols cancel. The map `M`
contains the 4,583 chronological non-target gates from `A[84:]`, `B` with its
72 numbered warps inserted at their recorded positions, and `restore`.
Targets 112 through 223 are omitted. A target-to-non-target source edge would
invalidate that reduction and is explicitly rejected.

The eligible input set `H` contains 226 helpers. It excludes all removed
registers, all 72 existing `helper_final` registers, every `start_extra`
register and every source of the initial operator corrections. Input changes
`S` must act inside `H` and be the identity elsewhere. Zero entrance frame
does not mean a zero initial value.

At the actual cut after `restore`, before final climbs, the complete relaxed
terminal support at

```
E7 = span_GF(2)(256,128,66,36,22,8,1)
```

is, in this order,

```
R = (105,307,309,314,369,371,373,378,408,572,573).
```

The last-frame collector includes all incidences of the full `A` word,
including prelude warps and sources of target writes; all `B` gates and warp
resets; and all `restore` gates. Every live register is observed. It also checks
the center frames at the separate target-only cut and all 72 retained cold
helper endpoints. Thus omission of target writes from `M` does not omit their
source incidences from terminal eligibility. The primary checker separately
validates monotonicity at every scalar incidence and both ends of every warp.

Let

```
C = (307,309,314,369,371,373,378,572,573).
```

These nine terminal registers are existing cold helpers. The independent
test generously permits them in the terminal support. Preserving them would
only restrict the proposed terminal change `T` further. The data register105
is also permitted, while targets and removed registers are excluded.

## The inverse-column restriction is the identity matrix

For an arbitrary scalar `y` supported on `R`, exact inverse replay gives

```
(M^-1 y)_550 = y_408,
(M^-1 y)_551 = y_105,
(M^-1 y)_c   = y_c          for each c in C.
```

These equalities are complete operator-polynomial identities: the displayed
coordinates have no omitted nonempty operator words or other coefficients.
Registers 550 and 551 are protected nonzero-entry `start_extra` helpers,
and every member of `C` is a protected cold helper. All eleven coordinates
are outside `H`.

Equivalently, in the given order of `R`, set

```
Jinv = (551,307,309,314,369,371,373,378,550,572,573).
```

Then the exact 11 by 11 restriction is

```
(M^-1)[Jinv,R] = I_11.
```

Its determinant is one. Therefore `M^-1 y` supported on `H` forces `y=0`.
This already excludes any nonzero extractable column at `E7`.

## An independent row restriction has determinant -1/4

For a scalar covector `alpha` supported on the same `R`, chronological right
multiplication gives

```
(alpha M)_14 = -alpha_105/2,
(alpha M)_41 =  alpha_408/2,
(alpha M)_c  =  alpha_c       for each c in C.
```

Again these are complete operator identities. Data inputs 14 and 41 and
all nine cold inputs are outside `H`. In the order

```
Jrow = (14,307,309,314,369,371,373,378,41,572,573)
```

the restriction is

```
M[R,Jrow] = diag(-1/2,1,1,1,1,1,1,1,1/2,1,1).
```

Its determinant is `-1/4`, a unit already over `Z[1/2]`. Hence the scalar
support condition on `alpha M` forces `alpha=0` independently of the column
argument. Because both restrictions are scalar identities, their obstruction
survives every representation of the pinned free-operator word on a dyadic
module; no independence of nonempty words after specialization is needed.

For clarity about chronology, write `M=G_n ... G_1`. To compute `M^-1 y`,
the checker visits `G_n,...,G_1` and applies each inverse on the left. To
compute `alpha M`, it visits the same reversed chronological list and
multiplies each `G_i` on the right. A shear `d += q s` updates the covector
coordinate `s += q d`; an operator on `d` appends its symbol to the right
of each existing coefficient word. Prepending here would be wrong.

## Consequence for simultaneous input and terminal changes

Suppose invertible scalar changes `S` on `H` and `T` on `R` produced both
the helper408 identity row and identity column in `T M S`. Then

```
v = S e408,          y = T^-1 e408,
alpha = e408^T T,    u = e408^T S^-1
```

would satisfy

```
M v = y,       alpha M = u,       alpha y = u v = 1,
v,u supported on H,              y,alpha supported on R.
```

The inverse-column identity already forces `y=0`, and the row identity
independently forces `alpha=0`; either contradicts the unit pairing.
The full rational calculation confirms dimensions zero and zero, using
11 inverse-column constraints of rank11 and 17 row constraints of rank11.
This covers every allowed rational scalar basis change, hence every allowed
dyadic one. It is not merely a failed candidate search.

## Existing rank-eight composition and defect-sensitive controls

The checker reconstructs the existing PR2908 composition from its actual
`WORD-*` providers and `TRANSFORM.json`. Its 24 input gates define `S`, and
its three terminal gates are

```
408 += (1/2) * 42
408 += 105
42  -= 2 * 408.
```

They act at `E8=(256,128,64,36,20,8,2,1)` and give

```
y = 2 e42,
alpha = e408^T + (1/2)e42^T + e105^T.
```

The replay independently derives `v=S e408` and `u=e408^T S^-1`, then
checks `Mv=y`, `alpha M=u`, `T y=e408`, `u S=e408^T`, and both pairings
equal one. The complete rank-eight terminal spaces have dimensions 7 and 4
with a nonzero pairing matrix. Terminal register42 has frame `E8` and is
unavailable at `E7`.

The simultaneous literal recipe is also checked: the new `A` is exactly the
old prelude, followed by the input gates, followed by the old remaining `A`;
new `restore` is old `restore` followed by the terminal gates. `B`, all warps,
prelude length, initial operator corrections, removed helpers and entry data
stay exactly equal. Input gates touch only `H` at frame zero. Terminal gates
touch no existing cold helper, and the old `helper_final` map is preserved
with only the new helper408 endpoint added.

For every compensation target, the actual new correction map equals `C S`.
The incorrect `C S^-1` map differs and is rejected. This matters because
the correction observes the transformed raw input, rather than undoing `S`.

Both literal cleanup lists are independently rebuilt by reversing the entire
changed non-target word and inverting every gate. The cold-helper host map is
`r -> r+704`, and all cleanup gates use the complete rank-nine frame. The
parent has 4,583 cleanup gates and 72 private buffers; the existing rank-eight
composition has 4,610 cleanup gates and 73 private buffers. This checks the
literal inverse recipe; the inherited native allocation and initialization of
those buffers are not re-proved here.

The following controls are required to distinguish actual semantic defects:

| Changed object | Observed consequence |
| --- | --- |
| Admit register42 into the rank-seven terminal support | A one-dimensional column and row pair appears with nonzero pairing |
| Replace `C S` by `C S^-1` | Actual target compensation differs |
| Omit the inverse of the final terminal gate | `M v = y` fails |
| Use forward chronology for the row pullback | `alpha M = u` fails |
| Add a target112-to-helper408 gate | Non-target reduction explicitly rejects the new dependency |

The operator implementation also distinguishes the words `(1,2)` and `(2,1)`
and checks left and right adjacent inverse cancellation. All mathematical and
integrity checks use explicit exceptions and remain active under Python `-O`.

## Scope, costs and next obligations

There is no new word and no paid saving: the proposed endpoint fails its
necessary algebraic interface before a cost improvement can be realized.
The declared favorable recursive screen, full owner-bin multiplicities,
unchanged centers and bridges, helper stock, and remaining scalar costs are
accounted for in the parent package. The above rank-eight gate and buffer
counts validate the predecessor composition only; they are not a newly
improved profile.

This is exact finite symbolic replay plus a written implication for arbitrary
dirty input values and all scalar changes within the fixed support class. It
is not a formal-kernel proof, an all-size supplier theorem, or a restriction
on changed middles or alternative endpoints. Native phases, compensation
lowering, physical owner realization, full recursive moments, precision and
outer assembly would all remain necessary for any changed construction.

An eligible next mechanism must change a premise that the witnesses use:
for example, paid recovery that changes the admissible entrances550/551,
the middle word, or the terminal incidence at register42. Such a change
requires a new combined word and a complete invoice. No such construction
or search is included here.

## Reproduction, independence and credit

From the repository root:

```sh
python3 -I -O -B research/helper408-rank7-pairing/check_independent.py
```

The exact stdout JSON ends with status
`PASS_INDEPENDENT_RANK7_PAIRING no_new_kappa`; it includes each provider's
support set, dimensions, two small restrictions, rank-eight bases, source
hashes, cleanup counts and control outcomes. It can be redirected to a
receipt without changing the computation. Only the standard library is used.

The new contribution is the independently derived inverse-column certificate,
its independent row counterpart and the composition-sensitive calibration.
The paired extraction mechanism, its actual 24+3-gate word, and the rank-eight
positive result belong to Jeremy Diviney (PR2908). The retained provider word
and earlier staged composition belong to Jeremy Kothe (PR2894/2833), with the
Yiyang Lu, Dugongue, Marius-Paul Dumitrean, Philippe Van Velzen, Tekalign and
exact/native lineage credit retained in `NOTICE.md` and the pinned sources.
Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0.

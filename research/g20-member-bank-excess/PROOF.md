# A paid member exit: boundary excess rather than an inherited channel

This checkpoint certifies one finite, source-bound example in which a public
helper moved along one published frame edge into an **occupied** compatible
bank exposes more boundary-pairing rank than either that bank or the helper
singleton already exposes. A bare positive rank is not the success criterion.
The normalized linear algebra below supplies necessary conditions; it does
not supply a typed consumer, new productive target, favorable bill or new kappa.

## 1. Exact source and retained premises

The word is PR5708's `research/g20-conjugation-admission/WORD.json.gz`,
originating at head `829d01fc031f7323ffcfa423fdfd1f24dcbe3190`, together
with its published PATHS and retained FRAMES data. The exact source WORD blob
is `3877a72d8a15adb03f6492f7d2fd8fa902ecb639`; the route blob is
`efbdf632746a971f9a593f57ccbb7d2cc67a6760`. Source bytes, the nine retained
inputs and their Git/SHA256 pins are in [SOURCE-PINS.json](SOURCE-PINS.json).
Author and predecessor Python files are inert source evidence, not imports
or executable dependencies of a new scientific checker.

Two coefficient fields must be kept distinct:

- Physical frame **shapes** are the rational row spaces of the literal
  FRAMES `B` matrices in `Q^8`, canonically reduced over the rationals.
  Frame aliases with the same row space occupy the same shape bank.
- Normalized scalar dependencies and the pairing forms are over `F_2`.
  Their rows/columns are binary formal-coordinate vectors, not rational
  physical frame bases.

The source normalized-coordinate contract, native frame induction, helper
identity endpoints and interpretation of owned fields/erasures are retained
premises. This package does not prove those native/physical facts anew.
Keeping them explicit is essential when comparing a hypothetical new frame
placement with the already checked source schedule.

## 2. Prefix, suffix, cuts and operational typing

There are 685 formal role labels and 14794 source records. Use **cut `t` =
the number of records already applied**, so cuts run from0 through14794.
The opening cut is0; applying the old source event with zero-based index `i`
leads to cut `i+1`. A predecessor's cut labelled `i` after that event is
therefore this package's cut `i+1`.

Use column states. Let `A_t` map entrance formal coordinates to the cut
state, and let `B_t` map that cut state to the exit coordinates. Row
`A_t[i,:]` is role `i`'s normalized prefix functional; column `B_t[:,i]`
is its normalized suffix response. In particular, prefix rows and suffix
columns are different objects; replacing either by a transpose of the other
would not compute this contract.

The pinned normalized model begins with `A_0=I`; the terminal suffix is
`B_14794=I`. Its elementary scalar rules are:

- `ADD d,s`: the cut state changes by the binary transvection
  `E=I+e_d e_s^T`. Advancing the prefix applies `A[d,:] ^= A[s,:]`.
  Reading the suffix backwards applies `B[:,s] ^= B[:,d]`. Because
  `E^2=I` over `F_2`, removing that ADD from a suffix while advancing
  the cut uses the same column update.
- `ERASE d`: its formal scalar map is the projection that kills coordinate
  `d`. A prefix row is set to zero; backward suffix construction sets
  column `d` to zero. This map is not invertible. To advance past it,
  one must use the suffix appropriate to the later cut, for example by
  restoring the column saved during backward construction, rather than
  pretending that zeroing a column is its own inverse.
- `Q`, `ZERO_Q` and `INIT` update frame/role metadata but have no
  additional normalized scalar action in the cited source convention.
  This convention is not a new theorem about physical initialization,
  inactive coordinates, zero preparation or erasure. Owned formal labels
  remain in the dependency bookkeeping, including outside-group tests.

Physical placement is tracked separately by each role's current literal
frame label. An ADD requires active source and destination at its declared
common frame. A query requires its actual source frame and changes it to
the declared destination. INIT/ERASE follow their source record's frame
update. Inactive labels are not occupied bank fields. Grouping equal row
spaces for the pairing test does not authorize free retargeting of literal
frame labels, nor does a normalized coefficient identity validate a changed
chronological word.

## 3. Groups, occupied banks and one-edge candidates

A retained public helper is a role at least222 which is not in the source
owned set. Its endpoint group `G` consists of all such roles with the same
entrance shape `U` and exit shape `V`. All formal coordinates outside `G`,
including main roles, owned labels and other helper groups, belong to the
outside restriction.

At a fixed cut, an occupied bank `S` contains **every** active role with
one common frame shape `F`. It may contain main, owned and helper roles;
no bank-size or support restriction is implicit. Compatibility with `G`
means strict physical row-space containment

`V < F < U` in `Q^8`.

A candidate names a member `h in G`, its current literal frame label `u`,
and a published route `(u,v,q)` with target shape `F`, positive paid rank
`q=dim(u)-dim(v)`, and nonempty target bank `S`. Strict dimension drop
ensures `h` is not already in `S`. The hypothetical move produces bank
`S'=S union {h}`. The old source prefix/suffix coefficients are retained
under the normalized-transport premise; only the proposed bank membership
changes for this necessary test.

This is a changed hypothesis from PR5983's existing common-frame bank:
the paid move introduces an extra physical coordinate into that bank at
this exact cut. It is not a rerun with another seed inside the old bank.
If the purported new bank is merely an already realized source-bank state
with the same coefficients, its old coverage remains old coverage.

## 4. Full eligibility and the two pairing forms

For a bank `T`, let `E_T` be its cut-coordinate space, embedded by zeros
outside `T`. Define the complete eligible spaces

`L_T={a in E_T^*: (a A_t)|outside(G)=0}`,

`R_T={b in E_T: (B_t b)|outside(G)=0}`.

These are full kernels of the corresponding outside-coordinate restrictions,
not a search over sparse candidate vectors. For `a in L_T`, put `c=aA_t`;
for `b in R_T`, put `d=B_t b`. By eligibility, both `c` and `d` are
supported only on the helper boundary group.

There are two distinct bilinear forms on `L_T x R_T`:

`eta_T(a,b)=a b`  (internal cut pairing),

`beta_T(a,b)=(a A_t)(B_t b)=c d`  (boundary pairing).

Matrices of these forms must use complete kernel bases, and their ranks
are independent of the chosen bases. In particular, boundary rank is not
the rank of the internal form and is not simply a nonzero kernel dimension.
PR5983's examples with a nonzero internal form but zero boundary form
already demonstrate why that distinction matters.

An abstract one-coordinate extraction/substitution needs the **same** pair
`a,b` with

`eta_T(a,b)=1` and `beta_T(a,b)=1`.

The internal equation permits treating the extraction as one cut coordinate.
For the boundary equation, use the retained identity endpoint on `G`.
Replacing the extracted coordinate by an independent formal successor `z`
would give the combined boundary map

`(h,z) -> (c h, (I-dc)h+d z)`.

If `cd=0`, the nonzero input `(h,z)=(d,1)` is killed, including the case
`d=0`. Thus independent boundary outputs require `cd=1` over `F_2`.
If `cd=1`, the displayed abstract boundary map is injective: its kernel
has `h=dz` and `0=ch=(cd)z=z`. This elementary conditional calculation
does not provide a physical implementation or productive target entitlement.

A finite positive case must publish actual cut-coordinate `a,b`, their
boundary images `c,d`, all outside-zero equations and both unit pairings.
Reporting ranks alone does not exhibit those vectors or their operational
realization. Several claimed split channels would require appropriate
nonsingular pairing matrices and simultaneous realizability; one unit pair
does not establish that larger conclusion.

## 5. The sharpened excess test and a one-coordinate bound

Write `rho(T)=rank(beta_T)` for this fixed cut and group. The necessary
success test in this package is

`rho(S') > max(rho(S),rho({h}))`.

A positive augmented rank with equality here is an **inherited** channel,
not extra boundary rank attributable to the occupied bank. In particular,
the already known member singleton at an empty bank is not a new result.
This excess test is an algebraic screening criterion, not a count of newly
admitted independent productive fields.

Embedding `E_S` into `E_S'` by a zero `h` coordinate embeds each old
eligible space into the new one. The map from `L_S'` to `F_2` which takes
the `h` coefficient has kernel exactly `L_S`; hence
`dim(L_S'/L_S)<=1`. The same argument gives
`dim(R_S'/R_S)<=1`. This does not require any invertibility of the
prefix/suffix maps and therefore remains valid in the presence of ERASE.

If the old bank has zero boundary form, choose bases extending its eligible
spaces by at most one new row and one new column. The augmented boundary
matrix then has the form

```text
       old right | new right
old left    0    | p
new left    q    | z
```

with missing blocks when a kernel does not grow. Its rank is at most2:
the new column has rank at most1 and the new row adds at most1. More
generally adding this one physical coordinate can increase boundary rank
by at most2 over the old bank. Thus a purported larger increase would
signal a wrong domain, incomplete kernels, changed prefix/suffix or an
implementation error; it cannot be explained by this one-coordinate move.

### Quotient out a known singleton pivot

If the singleton is eligible on both sides with boundary pairing1, its
coefficient vectors are the literal `e_h^T,e_h`, and its internal pairing
is also1. Extend these to eligible bases of `S'`, placing the singleton
first. Its boundary matrix has a pivot block

```text
1  p
q  C
```

and row/column elimination gives

`rank(beta_S')=1+rank(C-q p)`.

Over `F_2` subtraction equals addition. If the augmented rank is only1,
the quotient after this inherited pivot is zero. Publishing the same pivot
as a new bank-enabled channel would overcount it. An actual residual
nonzero quotient must be shown explicitly when claiming boundary excess.
Its existence still does not prove physical multi-channel implementation.

## 6. Two immediate completion cautions

### The added-query tariff in a deliberately restricted model

Suppose a proposed one-helper edit changes exactly one productive target
from rank `r+k` to two targets of ranks `r,k`, adds one paid query of rank
`r`, and retains every other paid job/target. Under that **declared special
model**, the productive-minus-paid margin change is

`H_r+H_k-H_(r+k)-H_r = H_k-H_(r+k) < 0`

for `r>0,k>0` and a strictly increasing tariff `H`. In particular the
inequality holds for `H_j=j^s`, `0<s<1`. A new scalar pairing cannot
erase the query debit or retain the surrendered rank-`r+k` target as well.
This calculation is not the complete invoice of a candidate in this package
unless its actual edit and targets satisfy those exact hypotheses. It does
not exclude other changed mechanisms, shared paid jobs, additional credits
or a differently priced supplier boundary; those require their own proof
and complete bill.

### Keeping the old suffix can leave a frame conflict

The hypothetical query changes the member's physical frame while leaving
the source suffix coefficient map in the necessary pairing calculation.
That is not a claim that the literal suffix remains executable. If the next
unchanged scalar contact requires the old frame, and no intervening valid
state change restores it, its common-frame check fails.

The predecessor's explicit example is helper222 at the opening: its source
frame is1, and records5638 through5643 are six ADDs declared at frame1.
After an earlier published exit to frame517 those contacts are ill-typed.
The published route graph strictly drops dimension, has no edge into the
unique dimension8 frame1 and therefore supplies no return to that frame.
Those source findings retain unpaidmoon's credit. Any proposed retargeting
must produce a changed typed chronological word, restoration and complete
bill rather than silently reuse `B_t` as an already executable consumer.

## 7. Independently checked positive existence checkpoint

Both new implementations independently reproduce this exact source case:

- Cut `t=7670`: records0 through7669 have been applied.
- Public member `h=323`, in the 413-member endpoint group with entrance
  frame1, dimension8, and exit frame0, dimension0.
- Its actual current frame is339, dimension6. The published edge
  `(339,507,2)` moves it to a compatible dimension4 target shape for
  one declared paid rank2 query.
- The **entire** occupied target bank before the move is
  `S={0,3,11,62,63,68,69,72,464,659,663,674,676}`.

The complete kernel dimensions and form ranks are:

| Cut space | dim L | dim R | boundary rank | internal rank |
|---|---:|---:|---:|---:|
| Existing bank S | 4 | 0 | 0 | 0 |
| Member singleton {323} | 0 | 0 | 0 | 0 |
| Augmented bank S union {323} | 4 | 1 | 1 | 1 |

Thus the boundary excess is exactly1, and it is not an inherited singleton
channel. An explicit common unit pair, written in **global role coordinates**,
is

`a=e_0^T+e_464^T`,
`b=e_323+e_464+e_663+e_676`.

Direct prefix/suffix evaluation gives

`c=aA_7670=e_464^T`,
`d=B_7670 b=e_323+e_358+e_464`.

The three boundary roles323,358,464 are all members of the stated helper
group. The outside restrictions are therefore zero. Both intersections
are the single role464, so `ab=1` and `cd=1`. The transported member is
used in `b`; the extracted original input coordinate is464. This is the
claimed different-role, bank-essential necessary pairing, not permission
to count another productive target.

The implementations use different bank/basis orderings; raw coefficient
bitmasks must not be compared without their declared order. The role
supports above avoid that ambiguity. Full eligible kernels, boundary images
and both matrices are retained in their receipts. The bounded oracle
rebuilds prefix and suffix directly at this cut rather than trusting the
primary census's incremental cache.

### Source controls distinguish excess and eligibility

At the opening cut0, moving helper222 along `(1,635,1)` into the occupied
bank `{221}` gives boundary ranks0,1,1 for bank, singleton and augmentation.
The inherited singleton pivot has quotient boundary rank0. This is a real
positive pairing but **zero excess**, and is rejected as a new bank-enabled
channel. It is separate from the predecessor's empty-bank517 example.

For the certified7670 unit pair, remove role323 from `b` while retaining
the other three roles. The same full-support guard used for the original
witness rejects the changed vector: its suffix image has foreign output
coordinates158 and163. Thus internal/boundary parity alone cannot replace
the outside-group eligibility checks. This is a corrupted witness-vector
control, not a valid modified source program.

### This witness does not complete a paid split

The actual source member has full target rank8, and the target shape has
dimension4. Consider the deliberately optimistic **special completion
model** that splits exactly one rank8 target into two rank4 targets, adds
only the one rank2 query and retains all other paid jobs and targets. Under
these assumptions its margin change is

`2H_4-H_8-H_2`.

For `H_j=j^s` and `x=2^s`, this is
`2x^2-x^3-x=-x(x-1)^2<0` for every `s>0`, in particular for `0<s<1`.
This exact restricted-model loss does not price an actual new typed word.
The extraction is original input464, not the transported member323; the
equation does not identify an actual target substitution for either role.
The generic cancellation in section6 does not apply to this witness, because
the added fee has rank2 while the proposed target parts both have rank4.
Changed target contracts, sharing/removal of other paid jobs or other
credits lie outside its assumptions and require a new complete bill.

The literal old suffix also has a concrete typing conflict. The first
subsequent source record touching323 is zero-based record8740,
`[ADD,323,366,339]`. There is no intervening event touching323 after
cut7670. If one merely inserts the proposed move to507 and retains all
old records,323 remains at507 when that ADD requires339. The normalized
pairing calculation deliberately does not pretend that this unchanged
suffix is already an executable continuation.

### Primary census coverage is not an independent complete classification

The primary implementation additionally reports a full14795-cut scan:
386278548 weighted cut/member/edge/bank cases,1241488 recomputations,
24166 weighted positive-excess cases and265 positive-excess recomputations.
Those positive cases are reported in the large endpoint group and have
maximum augmented boundary rank1. These totals are **primary-only,
author-side census evidence** at this checkpoint. Recomputations and
weighted per-cut cases are different units and must not be interchanged.

The independent oracle checks the explicit7670 witness and the opening
inherited-only control; it does not independently certify the complete
census. The paired continuation retains that full-domain coverage
obligation. This checkpoint's independently reviewed new claim is positive
existence with the exact kernel/unit-pair evidence above, not a complete
classification, all-case price obstruction or supplier theorem.

## 8. Scope and credit

This certificate concerns binary normalized kernels and pairings under the
retained native transport/endpoint model. It supplies no new arbitrary-input
native map, changed scalar endpoint, typed reader/consumer, physical erasure,
noncoordinate productive target, favorable complete recursive/ordinary bill,
stronger Gaussian caller, compiler/precision/tape/stock/analytic closure or
new selected frontier. A single frame-edge price is not a complete supplier
bill. Characteristic-two scalar extension does not establish an operator-
valued, address-dependent or mixed-group generalization.

Credit unpaidmoon with substantial Cursor Grok assistance for
`g20-frame-round-trip-gap`, head
`cb0973978c785f41f5a11fd2548ac08ba6e68dd6`: the no-return route argument,
opening member-to-empty-bank witness, non-member census and the explicit
member-to-occupied-bank handoff. Credit Nick Petalas PR5983, head
`795c4f59aa9e7ca7e133bea6e3ea21837c5849dd`, for the existing-bank
free-carrier certificate and necessary boundary criterion, following
Ali Romman PR5609. Ali Romman PR5679/5708 supplies the split construction,
word, routes and open different-role question. PR6325/6337 retain their
different correction-frame obstruction scopes.

Preserve Dugongue, ai-nanachi, compact436, Cinna Davis, DreamingOfClouds,
eumemic, rohanarun, zxv, Jacob Alan Sussman and all native/helper/controller/
ordinary/stock/compiler contributors retained in
[sources/NOTICE.md](sources/NOTICE.md). Elimination, rank-nullity, block
pivoting and the rank-increase bound are classical. The new work is the
source-bound excess test and its explicitly bounded evidence, by ToikY with
substantial OpenAI Codex assistance. Same-session agent review is not
independent human or formal-kernel acceptance.

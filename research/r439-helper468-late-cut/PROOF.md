# No rank-seven common-frame isolation of helper 468 at a later PR589 cut

## 1. Statement and exact scope

Fix DreamingOfClouds' PR589 tuned R439 word, with 111 source/target pairs and
439 arbitrary dirty helpers. All 661 formal input coordinates are independent.
The exact input bytes are archived and pinned in
`SOURCES.json`. Use its listed rational frame spaces, original register roles,
and final output convention: source/helper r returns its original input, and
target t returns `u_t + u_(t-111)` at its specified target hyperplane.
The proposed change is helper 468's terminal frame, which may be any rational
space of rank at most seven. Its required output remains its original input.

The starting cut is just after the original D/A/scatter prefix and all nine
retained COPY/ERASE pairs. Continue the original B/C word, interpreting each
listed donor in its listed order. The ledger includes the starting cut and
every boundary after a literal MOVE or individual ADD, including final MOVEs:
4,873 events and 4,874 cuts in total.

**Theorem.** At none of those cuts can an inserted scalar block at one common
rational frame F of rank at most seven both restore helper 468 to its original
dirty input and remove that dirty input from every other register, while
admitting a completion with the original output roles/target frames. The block
may have arbitrary length, arbitrary invertible scalar mixing, target feedback,
and any number of independent dirty auxiliaries at F. The remaining completion
need not be the original B/C continuation.

The allowed completion uses scalar operations at common frames and monotone
frame enlargements. New COPY transport, descent/reset, an earlier lower-frame
preparation, altered prefix, different output roles, and restoration without
immediate complete isolation are outside the theorem. An auxiliary's initial
dirty input is independent; it does not provide an extra copy of a boundary
coordinate. This is a scoped finite-word obstruction, not a barrier for all
width-seven interfaces or bit suppliers.

**Stronger later-cut corollary.** Starting at cut **177**, immediately after
the MOVE of target 208 from frame 0 to frame 152 at zero-based B gate **88**,
no reversible linear suffix in the inherited monotone/common-frame model can
restore helper 468 at any terminal frame of rank at most seven. This permits
arbitrarily many frames, arbitrary suffix length and extra restored dirty
auxiliaries. All 4,697 cuts from 177 onward have a rank-eight two-sided footprint
or an already rank-eight helper. The first 177 cuts pass that two-sided rank
test; no existence conclusion is drawn for them. Their single-frame isolation
blocks remain excluded by the theorem above.

Ross Richardson's PR1256 proves the initial-cut footprint obstruction and
explicitly leaves later target-read cuts open. Ali Romman's PR1128 supplies
the two-sided restoration/dirty-column condition and two earlier cut analyses.
This contribution evaluates the changing condition at every later literal cut
for one seed-selected helper. It does not reopen their fixed-cut exclusions.

## 2. Scalar information required by an isolating block

At a cut write `w = M u`, where M is the 661-by-661 binary scalar matrix. The
prefix and every suffix ADD are invertible; all scatter snapshots have been
erased. Thus the coordinates of w are independent arbitrary bits. The scalar
matrix concerns formal inputs, not a reduction of rational frame coordinates
modulo two.

For h = 468, let

```
a_h = e_h^T M^-1,
d_h = {r : M[r,h] = 1},
P_h = support(a_h) union d_h union {h}.
```

Every coordinate of `support(a_h)` must participate in a block that outputs
`u_h`. If a coordinate p with a nonzero coefficient is not read, two boundary
states differing only at p give the block identical inputs but require different
restored helper values. Independent dirty auxiliaries cannot distinguish them.
Every other register in d_h must also participate: leaving it unchanged retains
its nonzero coefficient of u_h, contradicting complete isolation. Include h
itself even when its current coefficient or restoration-row coefficient is zero.
This necessity allows arbitrary scalar mixing rather than assuming the short
restore/clear star used as a predecessor fixture.

All participants must reach F. Let J be the rational span of their current
frame spaces. Monotone frame legality forces `J subset F`. Consequently:

- if helper h has already reached rank eight, a rank-seven F is impossible;
- if `dim J = 8`, no F of rank at most seven contains the footprint;
- if a target in P_h has a final frame V_t that does not contain J, forcing
  that target to F makes its required final frame unreachable.

The third condition alone excludes every low-rank footprint in the census:
target **208** is always such a forced participant.

The ledger also recomputes the broader missing-information condition. The
required target row in current boundary coordinates is

```
b_t = (e_t + e_(t-111))^T M^-1.
```

If J is not contained in V_t and `support(b_t)` meets P_h, two states differing
only in one such forced coordinate have different desired target values. After
the block, all information about that coordinate lies in registers at F or
descendant frames containing F. No common-frame scalar dependency path can
reach target t at V_t. Extra participants can only enlarge J. These are
information-access failures even if all additional work is free.

## 3. Complete cut enumeration and inverse updates

The primary engine constructs M from every D/A ADD and scatter read, then
inverts it exactly over F2. For `w_t ^= w_s`, write `S = I + e_t e_s^T`. Since
`S^-1 = S`, the new matrix and inverse are

```
M' = S M,
M'^-1 = M^-1 S.
```

Hence every inverse row containing coordinate t toggles coordinate s. A MOVE
changes frames but not scalar rows. The primary engine updates all 661 forward
and inverse rows after every event, reconstructs P_h, and joins its rational
frames. The final forward matrix and inverse both equal the full required
dirty-input/output map. This also checks the entire B/C tail after helper h has
already become too large, rather than ending coverage at the first obstruction.

The independent engine uses sets for scalar expressions, a descending-column
set inverse, and explicit integer minor/normal witnesses for the nine footprint
joins. It imports no primary or predecessor program. Both implementations agree
on all events, all cut fields, the full ledger/certificate, and all 661 final
forward and inverse columns. Both are from this AI-assisted contribution; this
does not claim independent human review or proof-assistant formalization.

| Exclusion | Cuts |
|---|---:|
| Footprint rank seven, but target 208 cannot reach its required final frame | 177 |
| Footprint already spans rank eight | 1,557 |
| Helper 468 itself has already reached rank eight | 3,140 |
| Not excluded by the necessary conditions | 0 |

There are 1,310 suffix MOVEs and 3,563 scalar ADDs. Helper h's current-rank
counts are 890 cuts at rank four, 710 at rank six, 134 at rank seven, and 3,140
at rank eight. These counts sum to the entire 4,874-cut domain.

For a rank-eight join, the certificate gives eight contained root lines and a
nonzero 8-by-8 integer determinant. For the rank-seven join it gives a nonzero
7-by-7 minor and a nonzero normal annihilating every line of the join, certifying
both rank bounds. A separate target normal annihilates target 208's final frame
and detects a line of the footprint. All nine cases are exact; no floating-point
rank tolerance is used. The independent engine checks their determinants by
fraction-free Bareiss elimination and their normal equations by integer dots.

The listed MOVE order is target followed by the listed donors. No alternative
ordering of those MOVEs inside a gate can rescue a cut: before its first ADD,
scalar rows and P_h are fixed, while each MOVE only enlarges participating
frames. Any exclusion before those MOVEs persists throughout their reordering.
The theorem fixes the original listed order of scalar donor ADDs; arbitrary
donor permutations or gate reorderings are not searched.

Thus the finite census instantiates the footprint proof at every specified cut.
This is stronger than a failed circuit search in that domain: each cut has a
necessary-condition failure excluding arbitrary block length and coefficients.
It is not an impossibility theorem for the excluded mechanisms in Section 1.

## 4. Arbitrary suffixes after the first rank-eight footprint

We apply Ali Romman's PR1128 two-sided boundary lemma, crediting the lemma to
that predecessor. Suppose h ends in a rational frame U. The restoration
argument requires every frame on `support(a_h)` to be contained in U: otherwise
an essential independent boundary coordinate cannot reach the restored output.

For erasure, call a register high when its current frame is not contained in U,
and take the F2 span S of all current high-register scalar rows. A low-to-high
MOVE adds a row to S; an already-high register cannot become low. A common-frame
invertible linear operation either acts entirely on low registers or, after
its operand MOVEs, entirely on high registers. In the latter case it preserves
their row span. Thus S never loses a vector.

At completion h is low. Every other required output, including every restored
extra dirty auxiliary, has zero coefficient of the original u_h. The final S
therefore has zero u_h coefficient on every vector. Any boundary register with
nonzero u_h coefficient must initially be low. Hence every frame in d_h, as
well as the restoration footprint and current helper frame, must lie in U.
The same J is a necessary subspace of U for **any** such suffix, without assuming
a single-frame block or immediate isolation.

At cuts 176 and 177 the scalar restoration row and dirty column are identical.
The event between them only moves target 208, which contains u_h, from frame 0
to frame 152. The frame join grows from seven to eight; the new eight-line minor
has determinant -32. Therefore helper 468 must end at rank eight from that cut.
The exact ledger verifies the same bound at every later cut. No new COPY,
descent/reset, different prefix or non-restored auxiliary is included in this
corollary. In particular, a staged attempt using the original prefix must start
before this MOVE; merely waiting for later target reads cannot repair it.

## 5. Favorable accounting screen and why it does not supply a construction

The unchanged prefix has already placed h at rank four. Its original later
path has ranks `4 -> 6 -> 7 -> 8`, contributing `H2 + 2 H1`. An ideal direct
move to a rank-seven residual instead contributes H3. The ideal local delta
at such a cut is therefore `H3 - H2 - 2 H1`. At a rank-six or rank-seven cut,
the ideal delta is `-H1`.

As in PR1256's credited two-slot planning model, relocate the residual from
an old width-eight host into a formerly idle rank-seven slot, returning all
eight freed coordinates to an old idle remainder r. The complete ideal child
deltas, retaining every other child and all nine COPY/ERASE pairs, are

```
current rank 4: e3 - e2 - 2e1 - e7 + e_(r+8) - e_r,
current rank 6 or 7: -e1 - e7 + e_(r+8) - e_r.
```

For each inherited remainder r in {2,4,6}, rank mass is unchanged. Child count
falls by three or two respectively. Any fixed nonnegative child-count surcharge
therefore also falls. Additional preparation, source access, helper storage,
restoration, frame changes and scalar work are optimistically free in this
screen; no new copies or recursive children are omitted from a claimed actual
construction because no construction is asserted. It is a favorable scenario,
not a bound on every possible alternative invoice or a physical slot assignment.

At the pinned bit exponent `a = 1733427039589844234749 / 10^24`, and indeed for
every `0 < a < 1`, `g(r) = r*(64/r)^a` is strictly subadditive. For the first
delta, merge old ranks 2+1 into 3 and old ranks 1+7+r into r+8. For the second,
merge 1+7+r into r+8. These merges strictly lower the weighted moment in the
ideal screen. The geometric failures above remain decisive even under that
favorable bill: a rank-seven single-frame block cannot satisfy the required
information and final-frame obligations. No native, packed precision, hosted
invoice, new endpoint or kappa follows from this screen.

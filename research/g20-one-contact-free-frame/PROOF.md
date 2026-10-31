# One-contact conjugation cannot gain by moving its correction frame

Fix the final word from CrocSwap/integer-mult-bounds#5708 at canonical base
`2485805a6d47f36ea83ddde6327d453ac82d44dc`. Let H_r(t)=r^t for 0<t<1.
Among all original equal outer ADD pairs, retain exactly those admissible
A2 conjugation intervals with one noncommuting contact. Remove the two
outer ADDs and insert the A2 correction immediately after that contact.
Choose its common frame freely from the 645 actual native frames. Keep
every other scalar event, its frame, the original public entrance/exit,
and the owned INIT/ERASE schedule fixed. Allow each required route to use
any finite sequence of proper nested native queries in either direction,
through these same 645 catalogue frames.
Each actual frame demand pays separately for its route on that role;
sharing or cancelling queries between different demands is excluded.

**Theorem (conditional native model, paid queries only).** Every such
changed word has paid-query moment strictly greater than the original
word, for every real 0<t<1. The finite domain is exactly 184 intervals ×
645 correction frames = 118,680 assignments. All newly introduced ordinary
work may be free in this comparison. This is a local obstruction, not a
universal multiplication lower bound. **No new κ.**

## 1. Exact scalar domain and placement

The source has 11,930 scalar events on 685 independent RAW/DIRTY columns.
Write T_ab for row a XOR row b. Its equal ordered outer pairs number
2,787. Inspecting every intervening event rejects 517 pairs containing the
reverse contact T_ba; 2,270 intervals remain admissible in the stated A2
alphabet. Exactly 184 have one noncommuting contact. An INIT/ERASE on
either outer operand would also reject the interval; none is the first
rejection in this source. Selection is exhaustive, deterministic and
source-bound; there is no random seed or numerical stopping threshold.

For the one noncommuting contact, elementary matrices over F₂ give

    T_ab T_bj T_ab = T_bj T_aj,       j ≠ a,b,
    T_ab T_ia T_ab = T_ia T_ib,       i ≠ a,b.

The original contact and its displayed correction commute, so placing the
correction immediately after the contact is valid under either chronological
matrix convention. The other intervening events commute with T_ab under
the stated admission rule. Hence removing the two outer T_ab and inserting
that correction preserves the scalar map. The checker independently
replays every changed scalar word on all 685 input columns, including the
arbitrary dirty columns and all owned final zeros.

Changing the correction's frame preserves the normalized scalar operation:
both operands are transported to the same new frame g, and its inherited
linear frame map takes their sum to the sum of their framed values. This
uses the endpoint/telescoping contract in Section 2; scalar coefficients
alone would not justify an arbitrary physical frame change. Whole-row
zero/nonzero status, which determines whether a query is paid, is therefore
independent of the chosen correction frame.

## 2. Native route relaxation

The current source frame catalogue is byte-identical to the catalogue used
by CrocSwap/integer-mult-bounds#5616. Exact rational ranks, complementary
spaces and orthogonality establish 645 distinct physical frames and 26,312
unordered proper nested pairs. The current `Geometry.nested` sorts the
endpoints by dimension and admits either direction precisely when their
rank difference is k with 0<k<8 and the smaller B-space is orthogonal to
the larger A-space. Equality is an identity skip, not a rank-zero query.
No rank-eight child is admitted. All 2,369 original route-table edges obey
this predicate.

The inherited native endpoint identity also admits nonmonotone paths.
For an orthogonal projector P, let R extract the eight antisymmetric
address differences, and L embed z into paired coordinates (z,−z).
Then RL=2I and the native move is M_P=I−LPR, with M_P²=I. If P≤Q,
PQ=QP=P and

    M_(Q−P) = M_Q M_P = M_P M_Q.

Each admitted query from frame s to t thus implements M_t M_s. Adjacent
frame involutions cancel along every finite path, leaving M_final M_initial.
This does not require unrelated frame projectors to commute. Transport to
every recursive arithmetic instance still inherits the native denominator,
frame and child-admission assumptions; the finite rational calculation
does not discharge those uniform premises.

Let d(s,t) be the shortest *total rank* in the 52,624-edge directed native
graph. Exact integer distances are recomputed, with all edge-potential
inequalities and tight descending predecessors checked. An independent
RREF-derived graph and integer-bucket computation give the same 645²
distances. For any route with positive ranks r₁,...,r_m,

    Σ H_(r_i)(t) ≥ H_(Σr_i)(t) ≥ H_(d(s,t))(t).

These inequalities follow from subadditivity and monotonicity for 0<t<1.
Thus replacing each paid route by the single optimistic charge H_d is a
valid lower bound, even when that charge is unattainable as one native
query. In particular a distance of eight does not grant a rank-eight
child. All original paid edges attain this lower bound, so the original
paid invoice is compared exactly. No older caller invoice or flow
certificate is imported.

## 3. Complete demand traces and the moved frame

For each role, retain its initial frame followed by every actual ADD-frame
demand. A zero donor suppresses both demands, matching the source emitter.
Each demand carries whether the role's complete row was nonzero immediately
before the demand. Owned INIT/ERASE events insert free resetting nodes.
Every public final-frame demand is appended, and every owned final row
must be zero. A transition into a demand is charged d(previous,current)
exactly when its paid flag is true and its endpoints differ.

Every one of the 184 changed scalar words is replayed in full. Its complete
trace invoice agrees with a chronological whole-word invoice. Each
inserted correction donor is nonzero, so its two actual frame demands are
present. Replacing their old frame f by g changes at most four transitions:
the incoming and outgoing transition on each of its two distinct roles.
The outgoing transition uses the *next node's* paid flag. A reset therefore
breaks that dependency; a final public return retains it. All other terms
of the complete invoice remain present and unchanged. This proves the
local update formula without omitting source access, intermediate demands
or final returns.

The independent checker uses a different mechanism: a full chronological
interpreter with set-valued rows and a symbolic chart X. It carries X in
each actual frame until overwritten, collects constant and symbolic paid
demands, and substitutes all 645 charts. It neither subtracts an old
invoice nor imports the primary trace-update implementation.

## 4. Exact sign certificates

The complete enumeration produces 245 distinct signed invoice shapes.
For 244 shapes, covering 118,677 assignments, every negative rank
occurrence q receives a disjoint nonempty group of positive rank occurrences
whose sum is at least q. Every positive occurrence is used exactly once,
including leftovers. For each group,

    Σ_group r^t ≥ (Σ_group r)^t ≥ q^t.

A multi-term group, a strictly larger sum, or a leftover makes the total
strictly positive. The certificate checks exact occurrence counts and
strictness, not floating-point signs.

The remaining three assignments all have signed shape

    H₃(t)+H₄(t)−H₂(t)−H₅(t)
      = (3^t−2^t)−(5^t−4^t) > 0.

For 0<t<1, the derivative t·x^(t−1) is strictly decreasing on x>0.
Integrating it over equal-width intervals [2,3] and [4,5] proves the strict
inequality. The checker authenticates the exact four-term identity,
positive ordered intervals and equal widths. These three assignments,
in `(outer_left, outer_right, changed_correction_index, new_frame)` format,
are `(6089,6567,6354,338)`, `(6074,6582,6401,440)` and
`(6093,6563,6342,410)`.

Every assignment therefore has a strictly positive optimistic paid change
throughout the entire open interval 0<t<1. Every admitted realization has
at least that paid change, proving the theorem. Strictness is not asserted
at t=0 or t=1, and no uniform quantitative gap at those endpoints is
claimed.

## 5. What this closes and what remains

CrocSwap/integer-mult-bounds#6290 and
CrocSwap/integer-mult-bounds#6305 investigate the source A2 rewrite family.
The new freedom here is the newly inserted correction's frame, combined
with arbitrary finite routing through the complete native catalogue.
The source CrocSwap/integer-mult-bounds#5708 common-frame expansion search
and CrocSwap/integer-mult-bounds#5616 contact-expansion theorem retain
their source scalar order; they do not cover this changed scalar word.

The result does not cover multiple noncommuting contacts with independently
chosen correction frames, moving original contacts, another correction
placement, changing owned resets, a different source word, additional
projectors, jointly shared routes between demands, or multi-step rewrites.
It supplies no all-depth obstruction.
It establishes a paid-query obstruction only: it does not prove the
selected complete multiplier, change its frontier, or discharge any of
the five inherited assumptions. The selected conditional κ remains
0.003125804.

# Retained-array catch-up in the scalar common-frame transport model

This note answers [#1166 c18956869](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18956869)
within one stated model. It proves no new κ and no supplier. Section 7 gives the priced
decisions, and Section 8 lists every premise that is not proved here. Base commit:
`de880ca1fa4540472ee8461d400914a60fc9dd41`.

**The question.** An array is retained across calls but no call reads it. Philippe Van Velzen
proposed two per-call prices for it:

- **(S):** one paid unit per array per call.
- **(C):** one rank-8 copy plus 8 units per array per call.

Which price, if either, does the selected model use? The answer decides his INIT64 + d_A
final-record route. His price gate reports a complex κ ceiling of 0.00228 under (S), or 0.00221
with PR2468-style read invoices, and no saving under (C). `verify.py` reproduces the 0.00228 value
exactly (2285992139/1002285992139); the 0.00221 value is quoted, not reproduced.

**The short answer.** Neither convention is a primitive of the transport moment.

- **Holding is free.** Holding an array at a fixed frame costs nothing in the moment (Lemma 2).
- **Catch-up is charged.** The moment charges the frame transport that the consumer needs to
  combine the record with its partners.
  - Its exact value is a minimum over the meeting level, in both directions (Proposition 3).
  - The record's rank ρ_r is measured modulo the rows the consumer may combine.
- **Eight coordinates per level.** In the selected nine-stage template, every pair passes
  through nine levels of eight coordinates each. A level is advanced either by the pair's own
  call or by an idle sweep (Fact T).
  - So a record consumed at its pair's current frame pays **8 × ρ_r × (levels advanced between
    capture and consumption)**, between level-boundary instants (Corollary 4).

How the law compares with the two conventions:

| Situation | Law | (C) | (S) |
|---|---|---|---|
| ρ_r = number of rows, pair advances one level per call of the lifetime, consumer at the current frame | equals (C)'s mass | 8 per call | under-prices 8× |
| Record of a pair that nothing touches during the lifetime (pair 3, six calls) | 0 whatever ρ_r is | 48 | 6 |
| Record that duplicates a row the consumer may combine | 0 (ρ_r = 0) | charges | charges |

For the #1166 routes the first row applies under the observation premise P_obs and the rank
premise P_rank of §7.2: the law agrees with (C) up to one lifetime off-by-one.

- So their (C) verdicts are derived here rather than assumed.
- With the stated end-of-replica decoder, INIT64 + d_A costs 3,648 units per replica and the
  all-initial variant 3,456.
- Decoding each bank as soon as its observed field Y_(k,U) is final, under the final-value read
  convention of P_obs (timing P_Y), still costs at least 2,496 and 2,304.
- Decoding each bank right after its last local call (P_early) costs 1,344 and 1,152. This is a
  lower bound for every current-frame timing at or after each bank's last local call. The
  decoder-timing premise P_dec (§7.2), which the derived decoders satisfy, gives exactly those
  timings.
- All of these exceed the 896-unit no-saving threshold.
- P_dec is load-bearing. At decoders placed right after each bank's own last capture the moment
  bound drops to 512, which leaves a κ cap above the selected κ. No decoder is known to run
  there.
- Without P_rank, philippeVV's Theorem B rejects the route only at the end decoder P_final
  (1,952 / 1,824). At earlier timings it needs an extra own-bank premise (§7.2).

## 1. Model and premises

**P1. The transport model.** This is the scalar common-frame transport model of
[PR1664](../dirty-host-cutrank-audit/PROOF.md) §4.1, and we use its rules 1–4 unchanged:

1. Scalar copy, add, scale and clear at a common frame are free.
2. A transport moves one register's logical row from frame A to frame B and costs at least
   |ν(A) − ν(B)|.
3. No uncharged cross-frame or multi-payload moves are allowed.
4. Any pre-existing side information belongs to the entry state.

Rows are vectors over a field K. A transport keeps the logical row: it changes only the frame.

**P2. Nested chain.** The frames of one data family form a nested chain. Height means the
number of applied coordinates.

- PR1664's frame formula gives d(A, B) = dim A + dim B − 2 dim(A ∩ B), which is at least
  |dim A − dim B|. For nested frames the two are equal.
- The selected frames are nested. [PR2540](../qq16-complete-native-decoder/PROOF.md) §1 gives
  F_L = ∏_{j=0..8} C_(d e_j) (9 axes) and F_U1 with U1 = ⟨e0,…,e16⟩ (17 axes).
- A direct move from height a to height b costs at least |a − b|. That is the number of unit
  cuts it crosses, so unit moves lose nothing.

**P3. The region and its entry state are fixed.** Lower bounds hold for a stated region and
its complete entry configuration (PR1664 rule 4).

**P4. The inherited words have no slack.** Sometimes the region contains the unchanged
inherited calls: F0, B1, the idle sweeps and so on.

- Their transports are then taken to cross each cut exactly as often as the rank of the rows
  they must deliver above it. Those rows are their own data endpoints and restored hosts.
- This is what the coverage identity says. Paid mass equals 72W + 64N exactly, so each family
  crosses each of its 72 cuts once.
- For the centre path, PR1664 §5's conditional bound (H) gives 64 per call once the
  author-reported rank r = 8 is substituted, and the selected path pays exactly that. PR1664 calls
  this "arithmetic substitution into a proved conditional theorem, not an independent verification
  of the selected S"; we use it only as support for P4.
- So the extra mass of a region equals M minus the inherited mass. It is at least
  Σ_j(δ_j⁺ + δ_j⁻) minus the inherited deficits.

This premise blocks one escape. A record cannot ride an inherited crossing "for free" by being
added into an inherited register: the demanded endpoint row must still reach the top, so one
extra independent row must cross. A construction that exhibits real slack in an inherited word
would escape P4, and it would have to show that slack explicitly.

**Fact T. Template levels.** These are read from the pinned selected #1094 hosted
`GLOBAL-TEMPLATE` (replica 0). Its 30-event schedule equals the base split-centres template's
schedule.

- **Pair binding.** The local calls at stages 0–8 use pairs 0,0,0,1,1,2,2,3,3. Even stages
  are forward calls; odd stages are backward calls.
- **Levels.** Each pair starts at level −1 and ends at level 8.
- **Local calls.** A local call at stage s moves its pair from level s−1 to level s. It applies
  the call's eight data coordinates.
  - The QQ16 frames show this directly: F0 outputs F_L (9 axes) and B1 outputs F_U1 (17 axes);
    see PR2540 §1.
  - It also agrees with the coverage partition 8·k_f + 1 + hosted_f + idle_f = 73
    (ctoth, #1587).
- **Idle sweeps.** An idle sweep moves an idle pair from its current level to `to_level`.
  - In the base template, its two children have rank 8 × (levels advanced).
  - The hosted template replaces part of an idle child by hosted helper residuals.
    [idle-axis-hosting](../idle-axis-hosting/PROOF.md) §2 shows that this leaves the product
    unchanged, so the frame after the sweep is unchanged.
- **Bridges.** Every bridge joins two pairs at equal levels. We take pairs at equal levels to
  share a frame (**P_glob**), as these free common-frame operations require. P_glob only
  shows that some costs in §7.2 are 0; no lower bound uses it.
- **Hosting and level boundaries.** A hosted residual acts at its helper's invocation time,
  inside the idle window. So part of an idle family's next block can be applied **before** its
  sweep, and the family then sits between two declared levels.
  - Example: just before event 7, some pair-0 families are already 4 or 9 coordinates above
    level 2.
  - The law's "8 × levels" form therefore holds between instants on level boundaries. In general
    the charge is the number of coordinates applied between capture and consumption.
  - `verify.py` checks the 21 route instants used below: the seven route captures, the four
    P_early consumers, the three all-initial reads with their consumers, and the four P_Y
    consumers. It checks replica 0 in both directions:
    - **No overshoot.** Every residual hosted on the pair by then belongs to a sweep that has
      already reached the stated level: 14,290 slot checks over 3,644 distinct residual slots,
      4,173 of them at the seven captures.
    - **No undershoot.** Every residual of a sweep that has reached the stated level has already
      landed: 9,280 checks of slots that have not landed yet.
  - `independent_check.py` confirms the same 21 instants in **all 16 replicas** by replaying the
    height of each of the 896 families of each replica.
    - Twelve instants (the 7 captures, the 4 P_early consumers and bank 0's P_Y consumer) are
      checked under both conventions for slots and events at equal times.
    - The other 9 are read after their time has settled: the P_Y consumers of banks 1–3 and the
      three all-initial reads with their consumers. Residual slots at that time belong to the
      sweeps at that time, which come before the instant in event order. Under the slots-last
      convention up to 5 of these 9 are not uniform (5 in replica 0), so they rest on this one
      reading.
    - An AI review pass replayed the hosted template convention-free, placing each slot at the
      schedule position of its hosting invocation. It found all 21 instants uniform at the
      stated heights in all 16 replicas.
    - So the route masses below are the same in every replica.

So one level is eight coordinates, and the nine levels are the 72 paid coordinates of each
family.

**Level timeline** (pairs 0–3, after each event):

| Event | Description | Pair levels |
|---|---|---|
| entry | — | −1 −1 −1 −1 |
| 0 | F0 | 0 −1 −1 −1 |
| 1 | B1 | 1 −1 −1 −1 |
| 2 | idle sweep, pair 1 | 1 1 −1 −1 |
| 4 | F2 | 2 1 −1 −1 |
| 5 | idle sweep, pair 1 | 2 2 −1 −1 |
| 7 | B3 | 2 3 −1 −1 |
| 8 | idle sweep, pair 2 | 2 3 3 −1 |
| 10 | F4 | 2 4 3 −1 |
| 11 | idle sweep, pair 2 | 2 4 4 −1 |
| 13 | B5 | 2 4 5 −1 |
| 14 | idle sweep, pair 3 | 2 4 5 5 |
| 16 | F6 | 2 4 6 5 |
| 17 | idle sweep, pair 3 | 2 4 6 6 |
| 19 | B7 | 2 4 6 7 |
| 20 | F8 | 2 4 6 8 |
| 21–23 | final idle sweeps, pairs 0–2 | 8 8 8 8 |

Bridges (events 3, 6, 9, 12, 15, 18, 25–27) are omitted from the table because they do not
change levels. `verify.py` reads this table from the schedule. `independent_check.py`
recomputes it from explicit coordinate sets, using the idle child ranks and not the declared
levels.

**Definitions.**

- An **entry configuration** is a finite list of (row, height) pairs.
- A **demand** is a finite list of (row, height) pairs that must each be held, at some time
  in the region, by a register at that height.
- For a cut j (between heights j−1 and j), let E_j⁺ and E_j⁻ be the spans of the entry rows
  at heights ≥ j and < j. Let D_j⁺ and D_j⁻ be the spans of the demanded rows on each side.
- The **deficits** are δ_j⁺ = dim(E_j⁺ + D_j⁺) − dim E_j⁺ and δ_j⁻ = dim(E_j⁻ + D_j⁻) − dim E_j⁻.

The entry configuration consists of every row the consumer may combine. In an application, a
row that the consumer's contract does not allow it to read is not part of the entry
configuration. This is how observation contracts such as P_obs (§7.2) enter.

## 2. Lemma 1 (PR1664's cut-rank bound, for one nested chain)

Every program in P1–P3 that meets the demand has paid mass

M ≥ Σ_j (δ_j⁺ + δ_j⁻).

**Proof.** This is PR1664 (C-down), its symmetric (C-up), and (A), applied with Q_j equal to
the demanded rows on each side.

- Each high-to-low transport across cut j adds at most one direction to the retained span of
  low rows.
- Common-frame operations, upward moves and clears add none.
- A move between heights a and b crosses |a − b| cuts.

Summing over the cuts gives the bound. ∎

**The bound is not always attained.** The frame model in `verify.py` finds 45 non-tight cases
among 4,044 general instances. The smallest has the same row v at heights 0 and 2 and demands
v at height 1. Every cut deficit is 0, but one transport is needed. Proposition 3's
independence hypothesis excludes such duplicates.

## 3. Lemma 2 (storage neutrality)

In P1–P3, keeping a register at a fixed frame for any number of calls contributes nothing to
M. Adding duplicates of entry rows at their own heights changes neither the per-cut bound nor
the minimum M.

**Proof.**

- M counts transports only (rule 2).
- Spans do not change when duplicates are added.
- A same-frame copy is free (rule 1). So each configuration can reach the other at zero cost.

∎

**Consequences.**

- **No storage price.** No per-array-call storage price follows from the moment, so (S) is an
  extra physical premise.
  - The question of physical storage is real but lies outside the moment: tape, banks, hosting
    windows, and the stream that holds an extra array.
- **Retention by existing streams.** The selected record keeps helper residuals across calls on
  existing idle data streams, with no per-call charge (idle-axis hosting §2), and its hosted
  template has no helper banks.
  - This shows that the selected accounting puts no moment price on retention by an existing
    stream.
  - It does **not** show that new arrays are physically free.

## 4. Proposition 3 (record, partner and consumer: exact both-direction minimum)

**Setting.**

- Records R sit at height h_r and partners P at height h_p, with span R ∩ span P = 0.
- The demand is a row set O ⊆ span(R ⊕ P) at height h_c. Optionally P must also stay at h_p.
- Let ρ_r = dim(P + O) − dim P. This is the part of O that only the records can supply.
- Let ρ_p = dim(R + O) − dim R. This is the part only the partners can supply.
- Let ρ_o = dim O.

**Claim.** The minimum paid mass equals

min_L f(L), where f(L) = ρ_r |L − h_r| + ρ_p |L − h_p| + ρ_o |L − h_c|.

The minimum is attained at L = median(h_r, h_p, h_c), and it equals the sum of the cut deficits.

**Lower bound.** Fix a cut j. A side is "high" if it lies at heights ≥ j.

- **Consumer on the high side.** The upward deficit is:
  - 0 if R and P are both high;
  - ρ_r if only P is high;
  - ρ_p if only R is high;
  - ρ_o if neither is high.
- **Consumer on the low side.** The downward deficit is the mirror image.
- **Partner demand.** It never adds a deficit, because P is in the entry span on its own side.

**Matching f.** At cut j, f(L) is charged with the weights of those points of
{h_r (weight ρ_r), h_p (weight ρ_p), h_c (weight ρ_o)} that lie on the other side from L.

- If L lies on the **majority** side, the other side holds at most one point. Its weight is
  exactly the deficit in the case list above.
- Putting L on the minority side instead costs at least as much, by three inequalities:
  - ρ_r ≤ ρ_o, because ρ_r = dim(P+O) − dim P ≤ dim O;
  - likewise ρ_p ≤ ρ_o;
  - ρ_o ≤ ρ_r + ρ_p, because o ↦ (a(o), b(o)) below embeds O into A ⊕ B.

The median of {h_r, h_p, h_c} lies on the majority side of every cut. Hence

f(median) = min_L f(L) = Σ_j (δ_j⁺ + δ_j⁻) ≤ M,

where the last inequality is Lemma 1.

**Construction.**

1. Write each o ∈ O uniquely as a(o) + b(o) with a(o) ∈ span R and b(o) ∈ span P.
   - A = {a(o)} is the projection of O along P. Its kernel is O ∩ P, so
     dim A = dim O − dim(O ∩ P) = ρ_r.
   - Likewise B = {b(o)} has dim B = ρ_p.
2. Copy and move a basis of A from h_r to L, at cost ρ_r |L − h_r|.
3. Copy and move a basis of B from h_p to L, at cost ρ_p |L − h_p|. The partners stay at h_p.
4. At L, O lies in A + B, so form a basis of O there for free.
5. Move that basis to h_c, at cost ρ_o |L − h_c|.

The total cost is f(L). ∎

**Special cases.**

- (i) h_c = h_p ≥ h_r: the record **climbs**, at cost ρ_r (h_p − h_r).
- (ii) h_c = h_r ≤ h_p: the partners **descend**, at cost ρ_p (h_p − h_r).
- (iii) h_c = h_r = h_p: the cost is 0.

The consumer level is a premise of the caller. Proposition 3 prices every choice of it; it
does not choose one.

**A consumer that works low and returns its outputs.** Suppose a consumer forms O below h_p and
then moves its outputs back up to h_p. The whole program still delivers O at h_p, so it is
bounded by Proposition 3 with h_c = h_p. Only consumers whose outputs are used, and stay, below
the partners' frame are priced differently.

**Finite checks.**

- **Primary, by exhaustive search.** `verify.py` runs a breadth-first search over per-level
  spans. It checks opt = Σ deficits = min_L f on 34,454 instances, each domain complete:
  - GF(2)², 4 levels: 2,432 instances;
  - GF(3)², 3 levels: 2,106 instances;
  - GF(2)³, 3 levels: 29,916 instances over all 129 independent (R, P) pairs.
- **Independent.** `independent_check.py` runs Dijkstra over reduced echelon bases on 2,432
  GF(2)² instances, and checks opt = min_L f.
- **Negative controls.** An upward-only bound fails on 14,426 of the 34,454 instances. A formula
  without the output term fails as well.

## 5. Corollary 4 (eight coordinates per level)

Under Fact T and P4, take a record of pair k captured at time t and consumed at its pair's
current frame at time t′, so h_c = h_p. Let ρ_r be its rank modulo the rows the consumer may
combine at t′ (Proposition 3).

- **Exact charge.** The catch-up is exactly ρ_r × (coordinates applied to pair k between t and
  t′).
- **Level boundaries.** When both instants lie on level boundaries, this is
  **8 ρ_r (ℓ(t′) − ℓ(t))**.
- **Per incidence.** Call each local call of pair k between t and t′ a later **data incidence**
  of the record. Each applies its own 8 coordinates, so the charge is at least 8 ρ_r per later
  data incidence.
- **Idle sweeps** add further coordinates.
- **Duplicates are free.** A record whose rows the consumer may already combine (ρ_r = 0) costs
  nothing, however many levels pass.

**Child shape.** The law fixes the transported **mass**, not the shape of the children.

- One child of rank 8Δℓ per independent row realizes it. So do rank-8 children, one per level.
- Per unit of mass, larger children cost less in the moment when a > 0.
- So convention (C)'s "rank-8 copy per call" shape is sufficient but not forced.

## 6. Proposition 5: (S) and (C) compared with the law

**(a) When (C) is a special case of the law.**

- **The two masses.** (C)'s mass is 8 per array-call. The law's mass for a current-frame
  consumer is 8 ρ_r per level advanced.
- **When they agree.** They are equal when ρ_r equals the number of rows and the source pair
  advances one level per counted call of the lifetime. The condition is sufficient, not
  necessary: half the rows and two levels per call also give equal masses.
- **The #1166 records satisfy this,** given P_obs and P_rank (§7.2):
  - **INIT records** are captured just before their bank's first call, at levels −1, 2, 4 and 6.
    Since the levels are the global stage index minus one, the lifetimes are 9, 6, 4 and 2.
  - **d_A records** are captured right after the backward call, at levels 1, 3 and 5. The
    lifetimes are 7, 5 and 3.
- **The off-by-one.** Philippe Van Velzen's price gate uses 8 for bank 0's d_A. Under the
  convention he uses for INIT (calls after the capture point), the count is 7.
  - The law therefore gives 8 × 456 = 3,648.
  - (C) as published gives 8 × 464 = 3,712.
  - No decision changes.

**(b) A zero-advance window.** Take pair 3's Y streams in replica 0 (families 784–895). Nothing
acts on them from entry until event 14 (time 40). The window is replica-specific: it holds in 12
of the 16 replicas, and in replicas 4, 5, 6 and 11 pooled slots land on some pair-3 Y families
before event 14 (`independent_check.py`). In replica 0:

- no local call (stages 0–5 are on pairs 0–2);
- no idle sweep (the sweeps at events 2, 5, 8 and 11 are on pairs 1 and 2);
- no bridge (bridges at events 3, 6, 9 and 12 join pairs 0–1 and 1–2; event 15 is the first
  bridge that touches pair 3);
- no hosted residual. Their sweep from level −1 to level 5 is an unhosted rank-48 child, and
  no pooled slot lands on them before time 40.

A record of such a stream, captured at entry and consumed at its current frame before event 14,
spans six calls.

- The law charges 0 whatever ρ_r is, because no level is advanced.
- (S) charges 6 per array, and (C) charges 48.

The record merely copies an untouched stream, so it is also free for the more basic reason of
Lemma 2. The example shows only which variable the law counts: levels advanced by the source
pair, not calls. It is not a useful retention.

Pair 3's **X** streams host 160 helper residuals in the same window, so their frames do change.
That is the selected record's own use of this window shape ("nothing touches F between ι and
τ", idle-axis hosting §2).

**(c) Lagging-pair records do not separate the law from (C).**

- **The candidate.** Take a record of pair 0's X stream captured after B5 (event 13), when pair 0
  sits at level 2, and consumed at the end.
  - In replica 0, pair 0 advances six levels, all in idle sweep 21, while three calls happen.
  - An independent row would therefore pay 48 against (C)'s 24 there. (In 6 of the 16 replicas
    some pair-0 X families already carry part of sweep 21 at that instant; the conclusion below
    does not depend on heights.)
- **Why it does not separate them.** The record is not independent. In the pinned schedule:
  - X_(0,U) is last written at event 6, by the bridge X_0 += c X_1.
  - After event 13 pair 0 is touched only by:
    - idle sweep 21, a transport that keeps the logical row;
    - bridge 27 with src = 0, which only reads X_(0,U);
    - the terminal Y translations;
    - the terminal relabel (X_U, Y_U) → (Y_U, −X_U).
- **Consequence.** So the record equals, up to sign and frame, the final completed-X field
  Y_(0,U), which the contract observes. Then ρ_r = 0 and the law charges 0.
  - `verify.py` checks this schedule fact.
  - A control with bridge 27 reversed, so that it writes X_(0,U), makes the check fail.
- **Conclusion.** This package exhibits no route in which (C) under-prices.

**(d) (S).** Storage is not a moment price (Lemma 2). As a stand-in for catch-up, (S)
under-prices current-frame consumers by 8×. Example: PR2540's 16 early records over one call
cost 16 under (S), but the law gives 128, which is both forced and attained (§7.1).

## 7. Applications and decisions

### 7.1 Controls

| Control | Law | Source value |
|---|---|---|
| PR2540: 16 early records, F_L → F_U1 (one level) | 16 × 8 = 128 | its 16 rank-8 upgrades (PR2540 §2) |
| PR2197: 8 Y_A arrays moved 18 frame terms to private frame I | 8 × 18 = 144 | 144-line floor |
| PR2678: 224 outputs, F_U1 → F_L | 224 × 8 = 1,792 | 224 H8 |
| PR2678: 224 outputs, F_U1 → (C_q, I), heights 17 → 1 and 17 → 0 | 112 × 16 + 112 × 17 = 3,696 | 112 H16 + 112 H17 |
| Selected centre path: 8 centres per call descend 8 → 0 (PR1664 §5.2 / ctoth's tree lemma) | 64 per call, 576 per replica | eight rank-8 copies, C = 64 |
| #1166 price gate against PR2474 | break-evens 573 (S) and 71 (C); (S) ceiling 2285992139/1002285992139 | reproduced with `ceiling.py` and with Decimal |

Notes on the controls:

- **PR2540.** It attains Proposition 3(i), assuming ρ_r = 16. That value is ywz65's PR2511
  rank-16 bound for its compressed observation interface, as quoted in PR2540's README.
- **PR2678 F0-gauge row (1,904).** It adds one signed-line gauge per Y. That is outside the
  height model and is quoted from PR2678.
- **Centre path.** It is the law's descend direction.

### 7.2 Route (a): the INIT64 + d_A final-record contract (philippeVV, fork 9fcd3d89)

**Premises.**

- **P_obs (observation contract).**
  - **What the consumer may combine.** The consumer may combine only:
    - the observations of the final-record contract, which are items 1–3 of
      [qq16-final-record-obstruction](../qq16-final-record-obstruction/PROOF.md) §1: final
      selected fields, final completed-X ordinary fields Y_(k,U), and the forward histories;
    - the stated records or reads, at their stated capture times.
  - **What is excluded.** The former-Y ordinary endpoints (final X_(k,U)), every additional
    ordinary read, and transient stream contents.
  - **Read convention (final-value reads).** The consumer may read a named observed field only
    once that field holds its final value.
    - A stream that still holds a non-final value counts as transient, even when that value is
      a fixed combination of final fields.
    - For example, on the literal replica-0 schedule bridges 25–27 are X_3 += X_2,
      X_2 += X_1 and X_1 += X_0, followed by the terminal Y = −X. So X_(1,U) after event 12
      equals Y_(0,U) − Y_(1,U), fixed at level 4, and X_(2,U) after event 18 equals
      −Y_(0,U) + Y_(1,U) − Y_(2,U), fixed at level 6.
    - An AI review pass in this loop derived these two identities; `verify.py` checks the last
      writes and bridge levels but not these combinations.
    - This convention is what gives "transient stream contents are excluded" its meaning. Under
      a span-based reading, banks 1 and 2 could decode at levels 4 and 6, which is the P_early
      cost. So the P_Y bracket below is relative to this convention.
  - **Where the premise comes from.** It is a premise of the QQ16 observation contract (the
    obstruction's §1 excludes "former-Y ordinary endpoint, or additional ordinary read"). It is
    not a consequence of the moment.
  - **Why it matters.** Without it, rule 1 lets the consumer combine every level-8 row for free,
    and a record row may lie in their span.
    - The obstruction's kernel family is visible exactly in the former-Y endpoints (its §4).
    - Local calls and bridges are invertible.
- **P_rank (contract level, unproved).**
  - **Statement.** At every cut j, the stated arrays captured below j that a decoder above j
    needs are linearly independent modulo the span of everything P_obs lets the consumers combine
    at or above j. That span includes the retained history of the rows P_obs allows, in
    PR1664's sense.
    - It does not include the whole program's retained history. Local calls and bridges are
      invertible and the inherited streams carry the initial data upward, so under that reading
      the INIT and d_A rows would lie in the span and P_rank would be false.
  - **Uncompressed delivery (our reading).** We read the published contract as delivering each
    needed array itself, uncompressed, to the decoder that uses it.
    - Its README states that "Every retained array stays live until the final decode"
      (final-record README @9fcd3d89). That is the price gate's storage-lifetime convention.
    - It does not by itself say that each array is transported to the decoder's frame.
    - Uncompressed delivery is therefore our premise, not a statement of the published contract.
  - **Effect.** The demanded rows are then the arrays themselves. By Lemma 1 the deficit at cut j
    is the number of needed arrays captured below j whose decoder sits above j. Summed over the
    cuts, each array pays its climb to its own decoder.
  - **Why delivery matters.** Lemma 1 counts the rank of what is demanded, not the number of
    arrays a decoder reads. A decoder output r1 + r2 forces one crossing, not two. Compressing
    records before they climb is therefore a contract change; see Robustness.
  - **Support.** Philippe Van Velzen's finite-model census and derived decoders (#2074
    c18950410, c18950926).
    - The census tests whether blocks of records are sufficient and necessary for decoding from
      the contract. It does not test this per-cut independence.
    - It is not a proof on the actual cover.
- **Capture times.** As stated in the price gate (`price_gate.py` @9fcd3d89: "INIT records of
  bank k are read just before that call", the bank's first call at stage 0, 3, 5 or 7):
  - INIT records are query maps of the initial X_(k,U), for example B0 X_(0,U) and B2 X_(0,U)
    in the obstruction's §1;
  - d_A is captured right after the bank's backward call.

  Local calls overwrite X_U: x'_U = x_U − y_U backward, and x'_U = x_U − K_(s,U) f forward
  ([CONSERVED-QQ16](../joint-query/evidence/CONSERVED-QQ16.md) (1) and (3)). No bridge writes
  X_(k,U) before bank k's first call, and `verify.py` checks this.
  - **Banks 1–3.** Their first call is backward, x'_U = x_U − y_U, so recovering x_U afterwards
    needs the transient y_U. For them the stated INIT capture is the latest one that needs no
    other read.
  - **Bank 0 is an exception.** Its first call F0 is forward, and CONSERVED-QQ16 (3) inverts it
    as z = w + K_(0,U) f0. f0 is a contract observation (the obstruction's §1 item 3).
    - So B_t X_(0,U)(initial) = B_t X'_(0,U) + B_t K_(0,U) f0 for t = 0, 2. The 16 INIT0 rows
      can therefore be formed at F0's output frame, level 0, one level above the stated
      capture, from one X_(0,U) read after F0 plus the observed f0.
    - This lowers every P_rank total by 16 × 8 = 128: 3,520 / 2,368 / 1,216 (original) and
      3,328 / 2,176 / 1,024 (all-initial) at P_final / P_Y / P_early.
    - The own-bank floor at P_Y becomes 1,216 / 1,088.
    - The one-level 1,952 / 1,824, the own-bank P_early 800 / 608 and every count-only value
      are unchanged.
    - All of these are still at least 896, so no verdict changes; `verify.py` computes them.
    - This is the first concrete step of lever 1 below (open question 1). The tables below keep
      the stated capture times.
  - *Sensitivity (AI review pass, not computed by `verify.py`).* The backward word is invertible
      from the pair's post-call X' and Y' (CONSERVED-QQ16 (1)). A capture one level later that
      also reads the pair's transient Y (with bank 0 via f0) gives P_final 3,136 / 2,944,
      P_Y 1,984 / 1,792 and P_early 832 / 640. The P_final and P_Y values stay ≥ 896, but the
      P_early values fall below 896 (caps 0.00034 / 0.00135, both still below the selected κ).
      So the P_early no-saving verdict depends on the stated capture times.
- **P_dec (decoder timing).** Each bank's decoder uses an observation of its own pair that
  exists only after that pair's last local call.
  - The derived decoders of #2074 c18950926 have this property. Through the tail identity
    C_k = w_k + K_(2k+2) f_(2k+2) (C_k the final Y_(k,U), w_k the initial Y_(k,U)) each uses
    f_(2k+2) and pair k's final selected fields, both available only after F_(2k+2), pair k's
    last local call (F8 and f8 for bank 3). F0/B1/F2 conserve the cut sums X_p + Y_p on A ∪ T.
    An AI review pass read the decoder code (fork 40d58b9e, as data only) and confirmed this.
  - P_dec is a property of those decoders, not of the moment or of P_obs.
  - **It is load-bearing.** Decoders placed right after each bank's own last stated capture
    (levels 1, 3, 5, 6) are current-frame timings that P_obs alone does not exclude. There the
    law gives only **512** in both variants, leaving κ caps of 0.0020286 idle-priced and 0.0020185
    rank-8-priced, above the selected κ and PR2474.
  - Decoders right after each backward call (levels 1, 3, 5, 7) cost 640. That still leaves a
    positive saving, with a cap of 0.0013547 idle-priced, below the selected κ.
  - `verify.py` computes both values, and a negative control fails if P_early is claimed as a
    floor for such decoders.
- **Consumer timing.** The decoder of bank k works at bank k's **current** frame (h_c = h_p in
  Proposition 3). We use three timings.
  - **P_final**, the stated contract: every bank decodes at the end, level 8, where the final
    records and the replica's data endpoint live.
  - **P_Y**, the earliest timing under the final-value read convention.
    - The decoder of bank k uses the final completed-X field Y_(k,U) = −final X_(k,U) (terminal
      relabel), through the tail identity C_k = w_k + K_(2k+2) f_(2k+2) (#2074 c18950926).
      Under P_obs it may not use transient contents of X_(k,U).
    - Local calls on pair k overwrite X_(k,U), and a bridge with dst = k adds into it. So the
      field is final only after its last write: event 6 for bank 0 (pair 0 at level 2), and
      bridges 27, 26 and 25 for banks 1, 2 and 3. Those three bridges run with every pair at
      level 8. `verify.py` checks the last writes and the levels.
    - So P_Y decodes bank 0 at level 2 and banks 1–3 at level 8. Other observations can only
      delay a decoder. So, under P_obs with the final-value read convention and for decoders that
      use their own Y_(k,U) (as the derived decoders do), every admissible timing has each
      consumer at or above its P_Y level.
  - **P_early**: decode each bank at its own frame right after its last local call (levels 2, 4,
    6, 8).
    - For banks 1 and 2 this ignores the final-value read convention, so it is not attainable
      under P_obs with that convention.
    - It lower-bounds every current-frame timing at or after each bank's last local call, which
      is every timing P_dec admits. The reason is that above the captures, catch-up only grows
      with the consumer level.
    - It does not bound earlier decoders (see P_dec).
    - It also assumes, in the route's favour, that the corrected fields then ride the inherited
      idle sweep to level 8 at no extra cost. If the decoded outputs were additional rows, P4
      would charge their climb.

  A consumer that works lower and returns its outputs is covered by Proposition 3 (§4). Only
  consumers whose outputs stay below the partners' frame are not priced.

**Catch-up per replica, original contract** (units; levels climbed in parentheses).

| Records | Capture levels | P_final | P_Y | P_early |
|---|---|---|---|---|
| INIT, banks 0–3 (16 arrays each) | −1, 2, 4, 6 | 1,152 + 768 + 512 + 256 (9, 6, 4, 2) | 384 + 768 + 512 + 256 (3, 6, 4, 2) | 384 + 256 + 256 + 256 (3, 2, 2, 2) |
| d_A, banks 0–2 (8 arrays each) | 1, 3, 5 | 448 + 320 + 192 (7, 5, 3) | 64 + 320 + 192 (1, 5, 3) | 64 + 64 + 64 (1, 1, 1) |
| **Total** | | **3,648** | **2,496** | **1,344** |

The P_early total is exactly 8 per later data incidence. Under P_Y and P_final the idle sweeps
add the rest.

**The all-initial variant.** #2074 c18950926 item 2 publishes it as equivalent: it swaps the d_A
records for the reads B2 X_1U, B4 X_2U and B6 X_3U, which bank 0, 1 and 2 use respectively.

- **When the reads can be taken.** X_(k+1,U) keeps its initial row until pair k+1's first call,
  so the read may be taken at any level pair k+1 holds before then: {−1, 1, 2}, {−1, 3, 4} and
  {−1, 5, 6}.
- **Cost at P_early.** Pair k+1 reaches bank k's P_early level (2, 4 or 6) in idle sweeps 5, 11
  and 17, before its first call. With pairs at equal levels sharing a frame (P_glob), the read is
  taken at the consumer's own frame and costs 0.
  - Both pairs sit at exact levels at that instant (times 10, 28 and 56, after every event and
    slot at that time). Both checkers verify this.
- **Cost at P_Y.** Bank 0's read again costs 0 (level 2). The reads for banks 1 and 2 are best
  taken at their latest levels, 4 and 6, and climb 4 and 2 levels to level 8: 256 + 128.
- **Cost at P_final.** The latest reads, at levels 2, 4 and 6, climb 6, 4 and 2 levels:
  8 × 8 × (6 + 4 + 2) = 768.
- **Totals.** INIT is unchanged, so the variant costs **3,456** (P_final), **2,304** (P_Y) and
  **1,152** (P_early).
- **P_glob is not needed for the rejection.** It is used only to show that the zero read costs
  are attained, and 0 is a trivial lower bound. The positive read climbs follow from
  d(A, B) ≥ |dim A − dim B| for any two frames.

**Price.** With C = 0 and the controller free, a paid mass of at least 896 units per replica
leaves no positive saving, whatever the packing. Write m = 73 and w = 896/9, the number of live
families per call (`ceiling.py`: w = families / stages). Then:

- At a = 0, every child costs r/m. The moment is then total/(m·w) = (72w + u/9)/(73w), which is
  at least 1 exactly when u ≥ 9w = 896: one unpaid coordinate for each of the 896 families.
- For a ≥ 0, every child cost (r/m)^(1−a) is at least r/m.

Both `ceiling.py` (at 895 and 896) and the exact rational check agree. Our PR2470 found the same
threshold under the assumed centre-like convention: at C = 0 its last count with any positive
saving is 111 coordinate-calls, and 8 × 111 = 888 < 896 ≤ 8 × 112. `verify.py` checks that the
pinned row agrees.

**Decision: rejected in the stated model, under P_obs, P_rank, P4, P_dec and the stated capture
times, for every current-frame consumer timing at or after each bank's last local call.**

- The stated end decoder costs 3,648 (all-initial 3,456).
- Every timing admissible under P_obs with the final-value read convention, for decoders that use
  their own Y_(k,U), costs at least the P_Y values, 2,496 (2,304).
- Every current-frame timing that satisfies P_dec costs at least the P_early values, 1,344
  (1,152).
- All of these are at least 896. Adding any non-negative storage price can only raise the cost.
- Bank 0's INIT via f0 lowers each value by 128, and every value stays at least 896.
- Without P_dec the lower-bound argument no longer rejects at some timing: 512, as above. No
  decoder is known to run there (bank 3's needs f8; keeping only bank 3 at F8 gives 768, cap
  0.00068, below the selected κ, per an AI review pass), and 512 is not claimed to be minimal.

**Robustness.**

- **d_A alone** costs 960 under P_final, which is at least 896.
- **Theorem B in place of P_rank.** Theorem B in #2074 c18940190 (philippeVV) says any repair
  needs at least 62 independent coordinates per owner per replica.
  - **Status.** It is a posted claim, with fork `680d0997621a2cecfef2186ab143377658687825`, and
    has not been reviewed.
  - **Shape.** It is one global count: it does not say which bank's decoder needs which rows.
  - **Common premises.** Below, the repair is restricted to the stated captures, each stated
    array supplies at most one row per owner, and P_obs and P4 hold.
- **One consumer level (P_final): Theorem B alone rejects.**
  - Fix a cut j below the consumer level, and let n⁺_j count the stated arrays captured at or
    above it. Modulo the contract observations, those arrays span at most n⁺_j dimensions,
    while the repair delivered at the consumer has rank at least 62 modulo the same
    observations.
  - Lemma 1 then forces at least max(0, 62 − n⁺_j) upward crossings of cut j.
  - Summed over the cuts, this equals the total climb of the 62 cheapest captures: **1,952**
    (original) and **1,824** (all-initial). Both are at least 896.
  - This needs neither P_rank nor any assignment of rows to banks. It also covers compressed
    deliveries, because Lemma 1 counts ranks and Theorem B counts the rank of the repair.
- **Several consumer levels (P_Y, P_early): the count alone does not decide.** When banks decode
  at different levels, the cut argument must know which decoder needs which rows.
  - **With an own-bank premise**, the single-level argument applies bank by bank.
    - **The premise (strong reading).** Let W be the span of the rows P_obs lets the consumers
      combine, C_k the captures that bank k's derived decoder uses (c18950926), and D_k the rows
      bank k's decoder needs (m_k of them). The 62 rows split freely over the banks, and for every
      bank k:
      - (i) D_k ⊆ W + span C_k;
      - (ii) D_k ∩ (W + Σ_{l≠k} span C_l) = 0, where C_l are **all** the other banks' captures,
        not only those above the cut.
    - **Per-cut additivity.** Fix a cut j. Let C⁺ be the captures at or above j, n⁺_{k,j} the
      number of bank k's captures among them, and E⁺ = W + span C⁺. Lemma 1 bounds the joint
      deficit dim(E⁺ + Σ_k D_k) − dim E⁺ = Σ_k m_k − dim ker φ, where
      φ: ⊕_k D_k → V/E⁺ is the sum map over the banks whose consumers are above j.
      - Project ker φ onto its first coordinate. A kernel element has
        d_1 = e − Σ_{l≠1} d_l with e ∈ E⁺. By (i), Σ_{l≠1} D_l ⊆ W + Σ_{l≠1} span C_l, and
        E⁺ ⊆ W + span C_1⁺ + Σ_{l≠1} span C_l. So the image lies in
        I_1 = D_1 ∩ (W + span C_1⁺ + Σ_{l≠1} span C_l).
      - By (ii), I_1 meets W + Σ_{l≠1} span C_l only in 0. So I_1 injects into the quotient
        (W + span C_1⁺ + Σ_{l≠1} span C_l) / (W + Σ_{l≠1} span C_l), whose dimension is at most
        n⁺_{1,j}. Also dim I_1 ≤ m_1.
      - The kernel of the projection is the same sum map for the remaining banks with the same
        E⁺, and the same two steps apply to bank 2, then bank 3. Induction gives
        dim ker φ ≤ Σ_k min(m_k, n⁺_{k,j}), so the deficit is at least
        Σ_k max(0, m_k − n⁺_{k,j}). Summed over the cuts, each bank pays the climbs of its m_k
        cheapest captures, and minimizing over the free split gives the cheapest 62 own-bank
        climbs.
      - The argument needs only transport cost ≥ |Δheight|, not P_glob.
      - It fails under weaker readings. An AI review pass in this loop found violations in
        random GF(2)/GF(3) instances when (ii) is restricted to the other banks' demands or to
        their above-cut captures.
    - The floor is then the cheapest 62 own-bank climbs: **1,344 / 1,216** at P_Y, both at least
      896.
    - At P_early it is **800 / 608**. Their κ caps are 0.0005091 / 0.0015234 idle-priced and
      0.0005051 / 0.0015144 rank-8-priced. All are below the selected 0.001672660197076918, and
      therefore below every pending claim.
  - **Without it,** a capture may serve any decoder.
    - Under P_glob, 62 stated-capture rows can then be delivered, each to its nearest consumer
      level in either direction, at total cost 608 / 544 at P_Y and 112 / 0 at P_early.
    - If the stated captures are independent, these deliveries meet the count. So an argument
      that uses only Theorem B's count and the capture heights cannot force more than these
      costs.
    - At P_Y the original variant's 608 has cap 0.0015234 idle-priced (0.0015144 rank-8), below
      the selected κ. If the stated captures are independent modulo the observations, Lemma 1
      forces exactly this delivery (an AI review pass gave a two-consumer pivot proof and found
      0 mismatches in 685 GF(2) brute-force cases; with dependent captures it can fail), so
      there the count still decides against the selected record.
    - The caps at 544 (P_Y, all-initial), 112 and 0 (P_early) are 0.0018604, 0.0041203 and
      0.0047021 idle-priced, all above the selected κ. So at those timings Theorem B's count
      alone does not reject the route.
- **Summary of the robustness.** P_rank rejects at every current-frame timing P_dec admits.
  Theorem B alone
  rejects at P_final. At earlier timings, where banks decode at different levels, it rejects
  (against the selected κ) only with the own-bank premise.
- **Sufficiency.** Whether the contract is actually sufficient does not affect the rejection.
  The evidence is finite models plus the derived decoders. A contract that is not sufficient
  fails anyway, and one that is sufficient costs at least the amounts above.

**What could revive the route.**

- **The binding term.** In both variants it is INIT64's catch-up: 1,920 at P_Y and 1,152 at
  P_early (1,792 and 1,024 with bank 0's INIT via f0).
- **Per term, if the INIT information were free** (`verify.py` prices each term):
  - **At the stated end decoder (P_final) no INIT lever suffices.** The original variant's d_A
    term alone costs 960, which is at least 896. The all-initial reads alone cost 768, whose cap
    of 0.00067848 idle-priced is below the selected κ.
  - **At P_Y the original variant's d_A term alone is 64 + 320 + 192 = 576.** Its cap of
    0.0016919 idle-priced beats the selected record only at the margin (576 is exactly the
    rank-8 break-even). It loses to PR2474 and to every pending claim.
  - **The live target is the all-initial variant at P_Y.** Its reads cost 0 + 256 + 128 = 384.
    That leaves at most 573 − 384 = 189 units against PR2474, or 579 − 384 = 195 against the
    selected record, for the INIT information, against 1,920 now: roughly ten times less.
  - At P_early, a bound and not attainable under the read convention, the d_A term is 192 and
    the reads are 0. Against PR2474 the INIT term of 1,152 would then have to fall below
    573 − 192 = 381 (original) or 573 (all-initial).
- **The target.** A gain needs catch-up-weighted retention below the break-evens, the largest
  masses at which a route still gains:
  - 573 idle-priced or 568 rank-8-priced against PR2474;
  - 570 or 568 against #2843, #2848 and #2857;
  - 568 or 560 against the bit endpoint (PR589).
- **For scale.** 62 arrays would need an average climb under about 9.2 coordinates, roughly one
  level.
  - The stated INIT captures sit 2 to 3 levels below the P_early consumers (exactly 2 with bank 0's
    INIT via f0).
  - At P_Y, banks 1 and 2 decode 6 and 4 levels above their INIT captures.
- **Three levers remain:**
  1. Capture the INIT information later, by rebuilding it from rows a contract may read (open
     question 1). Bank 0's INIT via f0 is the first instance; it saves 128, and banks 1–3 remain.
  2. Read endpoint rows at the consumer frame. Such reads pay no catch-up in the moment. Their
     price is a read or observation-contract question outside the moment. One example is the
     optional PR2468-style read invoice in the price gate.
  3. Compress records before they climb. At P_final this is still bounded by Theorem B's
     per-cut form (at least 1,952 / 1,824). At multi-level timings it is bounded only under the
     own-bank premise; otherwise it is open.

  Each changes P_obs or the uncompressed-delivery part of P_rank, so each is a different contract
  from the one rejected here.

### 7.3 Route (b): shared-source centre sharing over a one-call gap

**Which pairs.** PR2199 lists six classes of same-replica shared-data pairs: f0→b1, b1→f2,
b3→f4, b5→f6, b7→f8 and f0→f2.

- f0→f2 is the only class with a one-call gap: B1 lies between the two calls. So 16 eligible
  pairs exist, one per replica.
- The other five classes are adjacent.

**Information status: open.** No predecessor establishes an information obstruction for f0→f2.

- **PR2199** computes formal pair ranks (16 for every dependent pair) in a calls-only
  projection. It states that this is "not a native obstruction". It also says the projection
  does not by itself give a lower bound for groupings, and that f0→f2 pairs share all 88
  destination owners.
  - Its open question 2 asks for the fixed-dirt source-only rank of exactly these 16 f0→f2
    pairs.
- **#2391 and #2461** (navinor; ywz65) concern only the adjacent f0→b1 class, selected calls 0
  and 4. They give a native non-lift and 104 owner-local coordinates per owner.

**Catch-up.** Suppose the information is present, and the sharing is realized as #1166 prices
it. Assume three premises:

- the 8 shared rows are retained across B1 and consumed at pair 0's current frame in f2;
- they are independent modulo the rows the f2 consumer may combine there, an observation premise
  of the P_obs type;
- P4.

B1 advances pair 0 by one level between capture and reuse, so Corollary 4 charges at least 8 per
row. That is at least 64 per shared 8-row set, which equals the per-call centre charge the
sharing would save. The net moment gain is therefore at most 0, which is (C)'s ×1.000. (S)'s
×1.787 leaves out this catch-up.

**Decision: no moment gain, conditional on the three premises above, by the catch-up argument
alone.**

- If the shared rows could be rebuilt at f2's frame from rows the consumer may already combine,
  the sharing would need no retention. That is a different mechanism, which this package does
  not price.
- The information question is open (PR2199 open question 2).

### 7.4 Route (c): the retention row of the QQ16 retained caller (clarification)

**One charge, not two.**

- **Value.** In the moment, the retention row of the #2540/#2651 caller is exactly 128, which
  is PR2540's 16 H8.
- **Why it is forced.** It is Proposition 3(i) with ρ_r = 16 (PR2511's interface bound) and an
  F_U1 consumer, and PR2540 attains it.
- **Consequence.** A "16 H8" row and a separate "retention" row would double-count it.
- **Holding is free.** Holding the records at F_L across B1 costs nothing in the moment
  (Lemma 2).
- **Physical storage** of the 16 arrays across B1 is UNKNOWN. #2651 coalesces these arrays into
  output banks.

**Child shape.** The 128 cannot be realized more cheaply in the moment. Each of the 16
independent rows must cross 8 cuts, and rule 3 allows one row per transport. So at most one
child of rank 8 is available per row, and rank-8 children are the cheapest per unit of mass.

**The comparison with the zero-retention decoder is not ours.**

- **The decoder.** #2707 (ywz65; `research/qq16-line-normalized-decoder`) refines Arham Tahir's
  PR2681 to 336 H1 children, no H8 children, and no value retained across B1.
- **The comparison.** Its child moment beats PR2540's for 0 ≤ a ≤ 1/16. The difference has
  numerator 112 − 16·8^(1−a), which is negative there because 8^15 > 7^16.
- **Status.** #2707, #2651 and PR2681 were incorporated on main after this package's base, in
  integration commits `5d8817103` and `481b8711e`.
- **The maintainers' review.** The review in
  `research/community-efficient1600-audit/combined-2707-review.json` on main records this
  comparison. It also records #2707's surplus of 192 wrappers, 256 maps and 8,368 scalar
  allowance.
- **Our check.** `verify.py` re-checks only the integer inequality.

**Consequence for the #2617 gate: a clarification, not a new decision.**

- The retention row cannot fall below 16 H8 for this interface in the moment. So further
  moment-level retention work on the retained caller cannot change the comparison.
- The open task remains #2617's physical one: owners, streams and tape positions for the
  sixteen early values, priced against #2707's non-moment surplus.
- Precision (PR2603 and the #2692 chain), travel (#2794), allocation (#2709) and the output
  consumer (UNKNOWN) are unaffected.

## 8. Scope and unresolved obligations

- **Physical storage, tape and hosting windows of retained arrays** lie outside the moment and
  are UNKNOWN. Lemma 2 neither prices nor dismisses them.
- **P_obs** is a premise of the QQ16 observation contract, not of the moment.
  - A contract that reads endpoint rows at the consumer frame pays no catch-up in the moment.
  - Its cost is a read-contract question that is not priced here.
- **P_rank for INIT64 + d_A**, and for its all-initial variant, rests on finite-model evidence
  only. Its uncompressed-delivery part is our reading of the published contract, whose README
  states only the storage lifetime. A compressing contract is a different one (§7.2, lever 3).
- **Consumer timing** is a premise, not a theorem.
  - The stated contract is P_final.
  - P_Y is the earliest timing under the final-value read convention of P_obs, for decoders
    that use their own Y_(k,U). Under a span-based reading it is not a bound.
  - P_early lower-bounds every timing at or after each bank's last local call, which is what
    P_dec gives. P_dec is a property of the derived decoders, and it is load-bearing: without
    it, the moment bound drops to 512 at one timing. P_early is not attainable under the read convention for banks
    1 and 2, and its ride-along assumption favours the route.
  - Consumers whose outputs stay below the partners' frame are not priced.
- **Capture times** are the price gate's. Bank 0's INIT can be formed one level later via f0
  (−128 on every P_rank total, no verdict change). Later captures for banks 1–3 need an extra
  read of the pair's transient Y (lever 1); one level later they would give P_early 832 / 640,
  below 896, so the P_early verdict depends on the stated capture times (§7.2).
- **P4 (no slack in inherited words)** is supported by the coverage identity and PR1664 §5. It
  is not re-derived event by event here. Slack exhibited in an inherited word would reduce the
  forced catch-up by at most that slack.
- **P_glob** (pairs at equal levels share a frame) is supported by the bridge schedule. It is
  used only to show that some costs are 0 (the all-initial reads at P_early and bank 0's read at
  P_Y) and that the count-only Theorem B deliveries are attained. The rejection does not need it.
- **Theorem B** is an unreviewed posted claim, and our per-cut application of it is written
  out in §7.2.
  - Alone it rejects only at the end decoder (P_final), where every bank decodes at level 8.
  - At P_Y and P_early it needs the own-bank premise in the strong reading of §7.2, which is
    ours, not the claim's.
- **Forward histories.** The derived decoders use f2, f4, f6 and f8 (the tail identity holds for
  every bank; bank 3 uses f8), and bank 0 also uses f0 (+512–576 / 128–192 / 128–192, AI review
  pass). None of them is counted in the 464 array-calls.
  - Suppose each is retained as one 8-row array, captured at its forward call's output level
    (2, 4, 6, 8) or input level (1, 3, 5, 7).
  - Then the law adds 768 to 1,024 under P_final, 384 to 640 under P_Y and 0 to 256 under
    P_early. For f2, f4 and f6 alone the ranges are 768–960, 384–576 and 0–192.
  - The row count is our reading of the 8-dimensional query outputs f = R_s x. The rejection
    does not need these additions.
- **Non-nested frames.** Only nested chains are treated.
  - For non-nested frames, d ≥ |Δh| still gives a lower bound.
  - Gauges such as signed lines can add more (PR2678's 1,904).
- **Prices.** Break-evens are given for ideal idle packing (rank 51) and for rank-8 children.
  The prices are ceilings, not attained exponents.
- **Frame-model checks** cover the stated finite domains only. Proposition 3 is proved in
  general above.
- **No new κ, no supplier, no change to the selected frontier.**

## 9. Credit

- **Model and lemma.** The transport model and the cut lemma are Andrey Mas's (an664, PR1664),
  with the GPT-6 Pro review it records.
- **Coverage.** The tree lemma and the coverage partition are ctoth's (#1516, #1587). The
  coverage identity is PR1012's.
- **Idle-axis hosting** comes from the #434 lineage.
- **Native frames, interfaces and tariffs.**
  - ywz65: PR2511, the source of ρ = 16; PR2540; #2707.
  - Arham Tahir: PR2681, the zero-retention logical decoder that #2707 refines.
  - petalas: the tariff (PR2678).
  - 1337isnot1337: the private d_A floor (PR2197).
- **Philippe Van Velzen** contributed the conventions, the final-record census, the price gate,
  the derived decoders, the all-initial variant and Theorem B. The fork commits are listed
  below.
- **The precursor.** Philippe Van Velzen's sibling-helpers note anticipates Lemma 2 and
  Corollary 4. On helper time-sharing it says "the bill is coordinate advances, not storage".
  - The note is at fork `b5ce9d223feeed73d07e2a07321f7a025bd5865e`,
    `research/complex-budget-law/closures-2/sibling-helpers/README.md`.
  - Its author marks it LOCAL-ONLY, and here it was read as data only.
- **Information results.** navinor (#2391), ywz65 (#2461) and our PR2199.
- **Our PR2470** (`research/qq16-cut-retention-census`) screened PR2443's retained copies under
  the assumed centre-like convention, 8 per coordinate-call.
  - Its C = 0 limit of 111 coordinate-calls with any positive saving is the 896 threshold here.
  - It also noted that a decoder that may read the whole post-B1 state needs no copy, which is
    the endpoint-read lever of §7.2.
  - Corollary 4 now derives that convention for current-frame consumers under P4.
- **Also credited:**
  - Ross Richardson (PR2480);
  - alephnan (PR2346);
  - commdata2338 (PR2174, PR2651);
  - the QQ16 lineage of Ali Romman;
  - the maintainers' combined review of #2707.

**Fork data.** These were read as data and never executed:

- `philippeVV/integer-mult-bounds@9fcd3d899cc5bad2e27ab1d3d64d241cbfe30793`,
  `research/joint-query-first-pair-catalogue/final-record/{price_gate.py, PRICE-GATE.json}`;
- the decoder at fork `40d58b9e`, which was cited but not read.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5).
Review so far consists of AI review passes in the same automated loop. There has been no human or
formal-kernel review. Apache-2.0.

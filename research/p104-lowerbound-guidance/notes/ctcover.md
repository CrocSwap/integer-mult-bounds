# CTCOVER CT (Nov 20, Opus, theory + exact replay). Own code: ctsplit.py (replay of SPLIT(R2 run) over GF(2) and Q, lifetime census, exact mass bound), f2embed.py.
Why this differs from SEPPAYS/FLUSHROW/R2TEST: it composes their two reductions on R2's run and finds the failing step; it also checks the field.

VERDICT: CT-COVER is FALSE over EVERY field (GF(2) and Q). "R >= m(Rec) for every pinned run" is FALSE over Q as well, not only over GF(2).

## 1. SPLIT(R2 run) is a pinned, all-GTD run with R = 2 and mass >= 3, over GF(2) and over Q [C]
- The run is R2TEST's loud_run plus FR §2's hand-over at C = <12>: helper H0 climbs to <12>; H0 += O0; O1 is born at <12>; O1 += H0; H0 -= O0; O1 -= H0; CLEAR O0. Over Q every coefficient is ±1, with X -= O.
- ctsplit.py results, for both fields:
  - bad = [], pinned = [], R = 2, idfail 0, oddfail 0.
  - The odd pattern is R2's target.
  - Lifetimes: O0 is GTD, cost 1, A = <13>, B = <1,12,13>. O1 is GTD, cost 1, A = <12>, B = <7,11,12>.
  - FA rows: (e0, y2+y3) has price 1. (e2+e3, y0+y1+y2+y3) has price 2. Their sum is 3.
- Exact mass bound, valid over any field [C]:
  - A price-0 row vanishes on odd cells.
  - A row with supports (D,S) is nonzero on every odd cell of D×S.
  - Enumerating every support row of price <= 2 finds 0 one-row and 0 two-row decoders. So m >= 3 over every field (and m = 3).

## 2. Which step fails: CT's hypothesis, not SPLIT [P]
- SPLIT is cost-neutral in the Lean/engine model, where birth at any chart is free (ARun has arbitrary s0 charts, `init` keeps the chart, and `down` is free).
- In the start-at-{0} model, SPLIT is NOT cost-neutral: the birth of d' at C costs dim C. That model is also the one where R2's run disappears (R2 Result 2).
- CT fails as follows:
  - Both lifetimes carry nonzero weight (O0 → X0; O1 → X2, X3), so both are roots.
  - O1's hand-over intake has eff = y2+y3 at <12>. It is hot per symbol (7·12 = 11·12 = 1).
  - The only lifetime that holds the cancelling content is O0, and O0 is itself a root.
  - So no forest exists. CT-COVER fails at the clause "carriers have zero weight": the obstruction is a DUAL-ROLE lifetime, one that is both a root and a carrier.
- Mechanism (shared climb):
  - Write the 2-epoch receipt as rows (w1+w2, c1) and (w2, c2).
  - The climb C2 → B2 is paid once but serves both rows, whose contents are cold at different charts (A1 ∩ C2 = 0).
  - In general Σ price ≤ cost + dim B2 − dim(B1 ∩ B2) [P]. The overcount is 0 when B2 ⊆ B1 (this assumes A1 ⊆ B1 and C2 ⊆ B1 ∩ B2).

## 3. Field and target: what can survive
- [C] R2's run has R = 2 = rank_F2(Q∘Rec). It is TIGHT for the proved REVERSE tensor bound, not for mass. So over integral runs the true run-side invariant is the tensor rank; mass is not.
- [P] For the identity target over GF(2)/integral runs, rank_F2(Q∘I) = n = m_F2(I). Shared climbs cannot help there.
  - [C] f2embed: on Q5, composing R2's run with an honest repair costs 6 > m(I) = 5.
- Q96/P104: m_Q(−I) = 56 < 96 lives only in half-integer (non-F2) decoders. There the question becomes whether shared-climb runs beat m_Q. Nothing tested here rules this out; no proof either.
- What a correct R-side needs: replace "R ≥ m(Rec)" by a Rec-specific statement. One option is (A) ChainWall56: the min over climb-sharing (chain) decoders of −I@Q96 is ≥ 56. This is STRONGER than Wall56, which the owner rules forbid as a new premise unless it is proved. The other is (B) a 2-adic/Z4 tensor-rank bound (LEANZ4 halving-law type) for −I@Q96 that reaches 56.
- The property that would block reuse on Q96 is: no two decoder rows of the E8-type optimum can share a climb with A1 ∩ C2 strictly smaller. Untested [CONJ].
NEXT: (i) Find the smallest label set with m_Q(−I) < n (NETVSWALL: E7 shard n=63) and test chain mass vs m_Q there. (ii) Pursue route (B): compute the halving-law rank bound at Q96 for −I.

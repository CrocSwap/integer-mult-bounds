# JOINTDR JD (Nov 20, Opus, theory + exact replay + Lean). Own code here: lt.py (t7669 owned lifetime shapes → lt.log), relay.py (owned→public→owned write/read edges with ascent e → relay.log), helper.py (helper finals), trace1.py, ycarrier.py (exact replay → ycarrier.log). Lean: lean/decoder-duality/Nov15/WordRungJoint.lean (KERNEL-CHECKED, axioms propext/choice/Quot.sound only).
Why this differs from NETATTR, G2CLUSTER and FLUSHROW: those lanes price ONE side at a time (network → decoder, or run → decoder). This lane asks whether D-side slack is paid on the R side inside ONE word, and what the rung actually consumes.

## (a) EXACT ANSWER: the rung consumes only D + R, and only on average over calls [P, Lean]
- Read off the Lean: every headline (WordRung, WordRungGen, WordRungPD, WordRungLat, WordRungLadder, WordRungPort, UniOwnedBank, UniHSC7113) uses hD : 56 ≤ descMass and hR : 56 ≤ hostedRise ONLY inside `UniOwnedBank.excess_ge_112_halves` (112 ≤ excess, via the exact split `excess_split_bank`: excess = descMass + hostedRise). In `rung_port` they enter only through the nlinarith step (ρD+ρR)n ≤ Xe i. There is no separate use of D or of R anywhere. So "PortInv has (m_D+m_R)·ψ" is literal.
- Stronger: `price_hsX` is affine in X with slope 9^s − 8^s ≥ 0 and the calls are summed, so only Σ_i X_i matters.
  WordRungJoint.lean: `rung_port_joint` (port-general: premise L·X0 ≤ Σ_i Xe_i), `rung_joint_P104` (112·L ≤ Σ_i (D_i + R_i), any caller), `rung_joint_7113` (κ < .0093453742 under the aggregate premise), `joint_of_halves` (old halves ⇒ new premise), `nonvac_aggregate` (calls with X = 100, 124 satisfy it; per-call 112 fails).
- Word meaning [P, from the fold definitions]: under `Legal` (public MOVEs strictly ascend and chain birth→final), each public's hop ascents sum to its field climb. So hostedRise = owned ascent mass and descMass = owned descent mass exactly. The rung premise is therefore OWN112: total owned movement ≥ 112·(number of calls), on average. Also R − D = Σ_owned (dim at CLEAR − dim at INIT) (DD §1).

## (b) Joint law: the D→R direction is FALSE locally; the R→D direction holds as a charge
- [P] CARRIER LEMMA (port-general). In a Legal word, a transfer from descent j (at b_j) to descent k (at a_k ⊋ b_j, slack e = dim a_k − dim b_j) is carried by co-located ADDs along registers whose charts climb from b_j to a_k. The carrier is either
  - an owned register, whose ascent ≥ e is counted in R; or
  - a public register, whose ascent is part of its fixed main/helper climb and costs 0 in D + R.
  Dually, an R-side relay (a DESCENT A_k ⊊ B_j, G2C §4) can never be carried by a public, because publics never descend. So every R-side slack e is an owned descent ≥ e, charged to D.
- [P + C exact, ycarrier.py] D-SIDE SLACK IS FREE VIA A y-CARRIER.
  - Setup: NETATTR §3(ii) (h=4, j: <1,4>↓<5>, k: <2,5>↓<7>, decoder mass ≥ 3 proved), with port 8 added.
  - Moves: j deposits into y_7 and loads y_8 at <5>; the cells (8,1), (8,4) are EVEN. y_8 climbs 0 → <5> → <2,5> → 8^⊥ (inside its main climb). k reads y_8 at <2,5>.
  - Replay: legal (publics strictly ascend, y charts ⊆ q^⊥, owned moves nested, ADDs co-located). The off-diagonal odd cells equal NA(ii) exactly. Owned movement is D = 2, R = 0.
  - So the 6-port pattern needs mass ≥ 3 but costs D + R = 2. No law "slack e on D forces ≥ e on R (or on D)" holds per relay or per cluster.
  - General condition: the slack relay j→k is free whenever ∃ port t with a_k ⊆ q_t^⊥ and Q[t, supp c_j] even.
- Structural reading [P]: the only free moves are public ascents. On the D side they act as RELAYS (the NA slack gap). On the R side they act as NODES (HT h-events: K-jump loads and public hot deliveries; the G2C hot-intake residual). Both open gaps are the same object, public ascents, seen from the two sides. The NetW ⊥-mirror does not map one onto the other, because publics only ascend.
- R→D charge [P]: an R-side relay descent that carries no D-relevant x-content is a D-inert node. Inert nodes leave M unchanged, so D ≥ (D-network mass without them) + Σ inert drops. A charged descent that also carries x-content is used twice, and no extra follows.

## t7669 check [C exact]
- lt.log: there are 32 moving owned lifetimes, and EVERY ONE IS MONOTONE: 15 pure-ascent (A = 56) and 17 pure-descent (D = 56). No lifetime mixes up and down moves, so D and R pieces are disjoint registers.
- GM's uncovered R shapes (multi-epoch 26, hot 8) have no D partners: the D-side masses are 15 and 1, which do not match.
- relay.log (naive write→read edges):
  - every descent→descent relay has e = 0 (3 via helpers, 1 via X): tight, as in GM's 8 tight chains;
  - slack e = 1..7 appears only through STAY registers (non-moving owned) and HELPER carriers: descent→stay e 2–6 (24 edges), stay→descent e 1–7.
  - All 1101 helpers end exactly at their token (helper.py), so helper-carried slack is restored without any attributable owned ascent. t7669 is an instance of free public-carried slack, not of D/R pairing.

## Consequences / next
- The universal premise can be OWN112 (owned movement ≥ 112 per call on average) instead of two walls. This is a weaker target and is already wired in Lean.
- Any proof of OWN112 from Wall56 must be GLOBAL. It must use the diagonal (M∘Q = diag, X finals) across the y-carriers' side loads, because y-carrier slack is free per cluster.
- Next exact test: on P104 charts, can a slack depositing→gathering relay always find an even-cell y-carrier (∃ t: a_k ⊆ q_t^⊥, Q[t, supp c_j] = 0)? If so, NetW relays are effectively free in words. If not, the absence of carriers is a P104-data law to exploit.

# FEWSTOPS (Nov 20, Opus): why t7669 splits main/helper climbs, and can a legal re-route use fewer jumps?
Code (own, stdlib, 1 proc): load.py, stays.py, check.py (PRICEKIT replay + independent legality: public strict ascent,
owned nested, co-location, ALL public rows/exit frames identical to t7669, exact PRICEKIT kappa), reassign.py (U),
lassign.py (L), ls.py / ls2.py (meeting LS, single+pair), lub.py / why.py (causal chart bounds + reasons),
sched.py / dagb.py / relaxk.py / fixedk.py (block-DAG reorder), hoist.py, vacate.py (reorder + re-chart search).
Why this differs from GAPMAP: GAPMAP priced the split; this lane asks which law/structure forces each stop, and
searches the re-route space exactly (rows held fixed, so every candidate is legal iff checker passes).

## Model facts used [P, from UniTrace.lean / pricekit.replay]
- Charts constrain only CO-LOCATION: ADD d+=λs needs cur[d]=cur[s] (same frame id); publics strictly ascend; owned
  nested. No content-at-chart rule exists in the trace model, so rows are chart-independent: any re-charting /
  re-ordering that keeps every op's row action gives identical rows (all helpers end = own token, X/Y finals fixed).
- [P] Commutation: two ops sharing register r commute iff both are intakes of r or both outputs of r (no self-ADDs in
  t7669). Any linear extension of the per-register block DAG reproduces every row exactly. ([C] confirmed: rows_equal
  on every rebuilt word.)
- [P] Reorder+re-chart feasibility = (a) each public's event charts form a chain init ⊆ … ⊆ final, (b) block DAG +
  per-register chart-order edges acyclic. (Any topological order is then a legal schedule.)

## 1. What happens at the stops [C]
- Stays: helpers 5520 (3346 intermediate), mains 2064 (1264 intermediate). NO empty stop: every intermediate stop has
  gates (H: 2046 in+out, 661 in-only, 639 out-only). Typical climb-9 helper 0→1→2→3→4→9: dim1 reads one X main at
  its port chart span(q_t); dim2 swaps with another ladder helper; dim3 one hand-off; dim4 a block with an X main at
  its dim-4 stop + helpers; dim9 deposits (≈400 events). Mains: X 1→2→3→4→9, Y 0→2→7→8 (Y used as relays).
- Meetings (components of stays joined by public-public gates): 1592; two giants ({0}: 850 H + all Y; full: 841 H +
  all X), 349 pinned by owned (D/R) gates, the rest small (2–30) CROSSINGS: members arrive from different flags
  and leave to different, incomparable next charts. That is why a stop can't be merged into a neighbour.
- Stop reasons (fixed order, typed causal bounds: L = join of sources in the co-location past, U = meet of sinks in
  the future; a boundary is forced iff join L ⊄ meet U across it):
  | reason | H | M |
  |---|---|---|
  | XY: past holds an X port q_t (X init span), future must stay in some Y's q_s^⊥ | 3672 | 1389 |
  | needs a pinned owned (D/R) chart | 429 | 147 |
  | helper init/final charts (dim-4/5 helper starts, sub-9 finals) | 250 | 125 |
  | unforced | 82 | 3 |
  So 84% of the split is the x/y interleave of co-locations (gather x at low port-flag charts, then meet y-bounded
  partners/cleanup inside q_s^⊥), 13% owned-pinned, 3% helper endpoints. No new floor above 104h is PROVED: the
  bounds are per-algebra (they depend on t7669's op DAG), not a law for every word. [CONJ] the XY interleave is
  forced by helper cleanup (helpers end = own token, so y-content gathered must be cancelled inside q_s^⊥ after the
  register's chart already contains x ports).

## 2. Re-route search (all exact; rows held fixed) [C]
| attempt | moves | kappa |
|---|---|---|
| t7669 | 6157 | .0037214260438636 |
| U (greatest consistent charts) | 6961 | .0034674 |
| L (least consistent charts) | 6671 | .0035452 |
| meeting LS, single + pair moves (fixed order) | 0 accepted | = t7669 (strict local optimum) |
| block-DAG reorder, hoist zero-move ops + LS | 0 gain | = t7669 |
| greedy lazy-join scheduler | 12856 / deadlock | worse |
- Fixed order lower bound (per register, greedy segmentation in [L,U]): H 5436 vs 5520, M 2061 vs 2064 stays ⇒ 98.5%
  of stays forced by the gate order. Optimistic per-register chart DP: fixed order .003770 (but joint LS finds 0, so
  this estimator overstates by ≥ +1.3%); with block-DAG reorder .004008 (+7.7%, optimistic, not realised).
VACATE (reorder + re-chart): see §3.

## 3. Verdict
- VACATE (reorder + re-chart, feasibility = chain + acyclicity, exact): 3481 (register, intermediate level) candidates
  whose every event has a level shared with its partner; **0 accepted** (each fails the chain/acyclicity test or doesn't
  lower cost). Rebuilt word = t7669 (replay ok, rows equal, kappa unchanged).
- **No kappa gain over t7669.** Within t7669's op algebra (same ADD/SCALE row actions), the split is a strict local
  optimum under every move tried: single-meeting, pair-meeting, hoisting, single-level vacate with reordering.
- Why: stops are crossings of different subspace flags. 84% come from the XY interleave (an x-port in the co-location
  past, a q_s^⊥ bound in the future), 13% from pinned D/R charts. Getting fewer jumps means changing the ALGEBRA: a
  helper must finish its y-bounded work (reads and cleanup inside q_s^⊥) before its chart takes on any x port.
  Chart routing alone can't do it, because the DAG fixes when cleanup happens.
- Next step (word design, not routing): build a helper class whose cleanup is moved ahead of x-gathering, e.g.
  pre-cancelled tokens or Y-side uncompute before the ladder. Size it first with dagb/relaxk on a toy, then rebuild.
  The optimistic +7.7% from relaxk is the most reordering alone could possibly add. Search found 0 of it. Treat it
  as an upper estimate only.

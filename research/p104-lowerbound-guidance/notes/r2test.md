# R2TEST (Nov 20, Sonnet): Q5={1,2,7,11,13}, GF(2), odd target t0:y2+y3, t2:y0+y1+y2, t3:y0+y1+y3 (rank 2, F2 mass 3). Is R=2 possible?
Code: enc6.py (final encoder; enc.py..enc5.py are earlier versions), eng.py/f2mass.py/fa.py copied from seppays (read-only use), loud_run.py (replay), logs *.log.
Encoding: one op per step: ADD(d,e) (public source e gets a free lift merged into the ADD) | owned MOVE (nested, ascent paid, exact unary dims) | owned INIT (content 0, chart free).
Sound normal forms only: lazy lifts, single INIT per owned, noops trailing, nonzero sources, no adjacent duplicate ADD, dead owned writes, owned/helper first-use order, partial-order reduction of independent adjacent ADDs.
Controls [C]: Q3={1,2,7} R=3 SAT (replayed), R=2 UNSAT to L=10; Q5 target R=3 SAT at L=10 (nh=1,no=3), both models; R=1 UNSAT L=10; mass-2 patterns R=2 SAT with free INIT. Every SAT is replayed through eng.Run (legality, pinned, cost).

## RESULT 1 (LOUD, engine model: owned INIT at ANY chart is free, as eng.Run.INIT(r,C) and gen3 allow) [C]
R=2 SAT. Run (loud_run.py), replayed with SP's engine + fa.gfa + f2mass: bad=[], pinned errs=[], cost 2, odd pattern == target,
F2 decoder mass 3 > R=2, FA row price sum 3 > 2, hot intakes 0, identity/odd checks pass.
  INIT O at <13>; Y2 lifts to <13>, Y3 to <13,10,7>; O += y2, += y3 (cold).  O climbs <13> -> <1,12,13> (cost 1); X0 += O  (t0 gets y2+y3).
  O DESCENDS to <12> (free); Y0 lifts to <12>, Y1 to <1,12,13>; O += y0, += y1 (cold).  O climbs <12> -> <7,11,12> (cost 1); X3 += O, X2 += O (both get y0+y1+y2+y3; y3 at t2 and y2 at t3 are EVEN cells, free).
Mechanism: ONE owned register, two epochs; the epoch-2 climb reuses the dimension <12> shared by both epoch charts. Decoder rows: {0}x{2,3} price 1, {2,3}x{0,1,2,3} price 2 => 3, but cost is 2.
It is a non-GTD (output then more intake) multi-epoch lifetime: exactly the open item (b) of SP.md / the 'up3/down1/up1' flush-row failure of FLUSHROW, now at the toy scale; it violates FutureAttr's hgtd, so it contradicts no Lean theorem. It DOES refute the claim 'R >= decoder mass for every pinned run' in the engine model, and the GF(2) mass-vs-rank gap is realised by runs (R = rank = 2 < mass 3).

## RESULT 2 (owned start at chart 0, i.e. INIT forbidden / first ascent paid) [C bounded]
R=2 UNSAT: nh=1,no=3 L=8..18 (all < 15 s); nh=2,no=3 L<=11; nh=2,no=4 L<=16; with X readable: see below. R=3 SAT (control, L=10). UNSAT here is fast and flat in L (short proof), mass-2 patterns that need a free-INIT run are also UNSAT at R=2 in this model (so this model is stricter than the tight runs of gen3).
Not a proof: bounds are on op count (fused ADD steps), registers (<=2 helpers, <=4 owned single-lifetime), GF(2); confidence high for these bounds, but the same family needed free INIT.
So the verdict depends on one modelling question for the owner: may an owned register start at a nonzero chart for free (ARun s0 arbitrary / eng.Run INIT(r,C))? If yes: R=2 run exists (Result 1). If owned start at chart 0: no R=2 run within bounds.
With X readable (init0, nh2 no4 L=14): UNKNOWN at 600 s (not decided); all UNSAT claims above are --noreadX.

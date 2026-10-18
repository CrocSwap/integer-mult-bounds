# B176: in-place line couriers (delete 38 twin couriers). VERDICT: KILL PROVEN [scope: shipped #656, all 38 twin couriers (11 blocks), exact Fraction replay of the whole word]. ship=false, no oracle/kappa.
Tools (single process, seconds): common.py (twin list from SYN-18 planes.py/fuse.py logic), val.py (value check through ALL of A+post-A), val2.py (stopper reads only), law.py (Lawler attempt; not instantiable, see below).
## Premise is false
- The 38 "twins" are NOT copies built by one op. Each u is a long-lived A working register: 20-27 writes and 19-25 source reads in A (stage/Walsh/Haar forms). Its end-of-A row equals P's only by coincidence (the B92b situation, all 38 not 16). Post-A, u is touched once or twice, only in the tail: `u -= P` (it is zeroed there), never read by a stopper z. The stopper z's courier read of u happens INSIDE A (plane-build), at u's stage value.
## Value check (through all of A)
- Replay every op of A/cut/B/tail/comp/cleanup; at each op that reads u compare row(u) with row(P): 0 of 38 twins value-exact. Unequal reads per twin: 11-25, all in A (post-A reads are equal, they are the zeroing ops). Restricting to the stopper-z reads of u: the only equal reads are 0==0 (both still empty); every nonzero courier read has row(u) != row(P) (P holds a single line/pair form, u a 2-4 term stage form). So rewiring z's ADD to read P changes VALUES; B176's "same value" assumption fails.
- Deleting u's writes would also delete its A-time role (it feeds 22 other ops), not just a copy.
## Lawler gate
- Not instantiable on the card's model: there is no single courier visit with value P to test. The value check precedes it (CHECK ORDER values -> frames) and eliminates all 38, so the Lawler result is moot: 0 pass / 38 (reason: value-forced, not frame-forced). law.py as written finds no post-A stopper read of u (its 'no stopper read' output = confirms premise failure).
## Price / escapes
- Prize 0: 0 deletable helpers. No splice, no kappa.
- Escapes (not run): (1) re-timed A in which P is built to the plane-courier role (a different S1 program, = B167 interface change); (2) B175 fewer planes; (3) non-twin couriers out of scope.

# B155 NOTES: pre-read concentration on #799. KILL PROVEN (scoped). ship=false
Tools: gate0.py, ex.py (oracle799 + retained frames; inserted pre-reads get empty frame, moved reads keep stored frame), k.py.
Gate 0 (re-gauge): 118 pre-reads; value-equal register v (row = E_h, or h-r post-copy) existing inside t's window pre-read..next climb: count 0 / 118. Escape (1) of SYN-15 closed at fixed op order (needs a new construction, not an exchange).
Setup: 191 copy pairs on #799 (unit gate, pre-reads only on targets), 54 with movable reads, 176 single-read moves (h2r with matching pre-read delete, r2h with pre-read insert). All 230 exchanges value-exact (replay).
Results (exact oracle legality, net emptied = emptied - newly touched targets):
- singles: 0/176 legal. Full-pair exchanges: 38 legal, all net <= 0 (24 net 0 / dk<=0, rest net -1/-2, dk -1.1e-7..-2.2e-7); 8 net>0 are illegal.
- target-sharing full-pair sets k=2,3,4: 40/56/56 candidates (components cap at 2 pairs): 0 net>0 legal, 0 positive dk.
- move-level target-sharing sets: k=2 716 cands, k=3 2772 cands: 0 legal. (k=3 run inline ~100 s, queue was saturated.)
Verdict: KILL PROVEN for copy-pair joint exchanges on #799, retained frames, k<=3 move-level / k<=4 pair-level. Best exact kappa: none above #799 (1.661634653669567e-3 base; GO 1.66662e-3 not approached). Consistent with B151 (violations union-additive, no repair arcs).
Remaining escapes: op reordering of h's copy gate; end-frame convention change; new factory gauge delivering E_h inside a climb. Not tested here.

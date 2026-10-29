# KILL-SMALL
STATE: KILL-SMALL: 262 KILLED by impl A (4 DRAT-verified chunks, controls SAT), 2nd impl pending; 579,596-601 OPEN (exact served(E) bound not computed).
- 262: see kills.json; p262/*.
- Others: served(E) is monotone in E, so exact max = max over placements of full flats (rank-s_i kernels of F2^9 labels) of served(union). Needs: enumerate rank-s flats' line sets up to W(E8) (596: two rank-4 flats; 597-599: rank-5 + small; 600/601: rank-6 + lines) and evaluate with LEFT22 mask tables (roots.bin/d7.bin, mk.py/sa.c eval). Not done within budget. 600/601 additionally need h_ab distinctness at c_S>=21.

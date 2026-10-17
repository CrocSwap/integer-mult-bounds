# LEFT22 — minimal two-7-flat leftovers up to 22 for root and D7-type h
STATE: LEFT22: tables DONE (A+B agree); rows 579,596-601 all OPEN (no certificate).
- impl A (A.c, CARRIER labels F2^9, flats = codim-2 intersections, maximal masks) and impl B (B.py, Cartan-matrix E8, own labels, numpy, + orbits under Stab(h)) agree.
- Root (r covered), minimal leftovers <=22: only 8:315 (rank4, 1 orbit), 12:5040 (rank6, 4 orbits), 16:4032 (rank6, 3 orbits); NOTHING of size 17-22 (control reproduces G777).
- D7-type h (|Off|=78), minimal leftovers <=22: 14:1 (rank 8; control: min 14 ok), 20:532 (2 orbits; ranks 8:84, 9:448), 21:1344 (2 orbits, rank 9), 22:4144 (4 orbits; rank 8:420, 9:3724); none of 15-19.
- Counting (Lemma F/Q4 style): c_S = sum g(S), g=1,2,4,8,12,20 -> 596:16, 597:15, 598:15, 599:16, 600:22, 601:22, 579 (vanish also on one 4-piece, S=[4,4,3]):20.
  Served(E)=|E|+#roots(not in E) with a leftover in E+#D7 with leftover in E (mk.py/sa.c, tables transported by W(E8)). Unstructured greedy-union search (heuristic LOWER bound on max):
  c=16 -> 19 (<36 needed), c=20 -> 23+ (<28 needed), c=22 -> 44 (>=36: unstructured counting FAILS for 600,601).
- Blocker: no exact upper bound on served(E) over E inside union of the S-flats; rows 600/601 need structured E (6-flat+2 lines, rank<=8 so D7 leftovers not excluded by D7R), rows 596-599,579 need exhaustive/ILP over S-flat unions. Also distinctness of h_ab for c_S>=21 (36+c_S>=57) uses graphic pattern, not checked.

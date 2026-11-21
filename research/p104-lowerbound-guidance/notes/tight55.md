# TIGHT55 notes (Sonnet lane, kissat only, <=20 min/run, <=2 procs)
Class: NONLIN tight B-linear (rows z in Z16, U_z subspace of F2^9, W arbitrary). NOT inside LINEAR56 Theorem A (A side arbitrary), so budget 55 is not settled by theorem.
Symmetry: sym.py: Aut(Q4)=384 graph autos of Z16 all extend to linear maps preserving P104 and zclauses (checked, 384/384). perms.pkl.
zsat_sym.py (SYM=1): lex-leader d_z-vector (d_z=dim U_z^perp via used[z,i], order-encoded) >=lex d o pi for all 383 perms. Run from nonlin/ with PYTHONPATH=.
Control: s56 (sym, from scratch) SAT in ~1 min (was 8 min); zdecode: prices [0,0,0,0,7,7,0,7,7,7,0,7,7,0,0,7] total 56, all ports decodable.
Because lex leader makes d_0 = max_z d_z, d_1 = max over Stab(z0)-class of z1.
Cubes (budget 55, cnf = s55 + units; d = dim U_z^perp... NOTE used[z,i] true iff dim(U_z^perp)>i, i.e. d_z = number used)
NOTE: used[z,i] true iff dim(U_z^perp) > i, so d_z = dim U_z^perp (d=9 <=> U=0, inactive, price 0). (Earlier cube names "M6/M8/F/G/H" in this dir use d in that sense.)

## RESULT [C]: budget 55 UNSAT for the whole tight B-linear class  (=> no tight B-linear decoder (any A side) with cost <= 55; min is 56 = E8)
Reductions used (all sound): (1) Aut(Q4)=384 lex-leader on d-vector; (2) normalization: price-0 rows (U=0 or U=<n_z>) set to U=0, clause [-used[z,7],used[z,8],-nin[z]];
(3) partition by inactive set I={z: d_z=9}: since d is lexmax in its orbit, the indicator of I is lexmax in its orbit -> 402 cubes (I=empty plus 401 orbit-lexmax nonempty I, reps.pkl).
Cubes: ic/i<mask>.cnf (400 UNSAT, each <=20 min, most seconds; all |I|>=2 done directly). I={0}(i1): split on d_1 (le5/6/7/8 -> i1_d1*.cnf, all UNSAT).
I=empty: d_0 (le6, 7, 8) all UNSAT; d_0=8 split on d_1 (j8_le5/6/7/8) all UNSAT. Outs are the .out files next to each cnf.
Controls: s56 (sym only) SAT 1 min, decoded 8 rows x7 = 56 all ports decodable; ctl56_i25679 (E8 inactive-set orbit rep + normalization, budget 56) SAT -> E8 orbit not cut.
Earlier non-normalized cubes also UNSAT: M6, Fa, Fb, Fc_le5, Fc_6, G7_*(3), G8_5, G8_6_6, H7_le5 (consistent, redundant).
Caveats: relies on NONLIN reductions (merging to <=16 rows, covering clauses zclauses.pkl cross-checked 20k random; price formula). No DRAT proofs produced (kissat -q only); UNSAT trust = kissat.
Not covered: loose rows (y in L4 beyond Z16, ~32k vectors), A-linear loose, M0 class.

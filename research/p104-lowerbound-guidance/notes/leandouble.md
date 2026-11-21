# LEANDOUBLE: Lean formalisation of ORBITLP's DOUBLING LEMMA (Nov 20)
File: lean/decoder-duality/Nov15/Doubling.lean (builds via runlean.sh, rc=0, ~20 s, 2 GB; axioms propext/choice/Quot.sound only).
[P] rank_fromBlocks_triangular: rank A + rank D <= rank [[A,B],[0,D]] (own proof, rank-nullity on projection).
[P] doubling: any y,z over F2: rank Yhat + rank Zhat <= C = sum rank Q_k (only needs h01 + decoder identity; v need not be even).
[P] Y_add_Z, cost_ge_rank: C >= rank_F2(I+X).  [P] split_cost_ge_card: split => C >= n (n=104 on P104).
Non-vacuity: Hadamard n=2: C = 2 = rank(I+X) (HalfCancel gave only C>=1); split n=2 instance C = 2 = n.
Review of OL.md section 3: no gap in Lemma / Corollary / split bound / O-form (checked on paper). Notes:
 - y_k ⊆ D_k, z_k ⊆ S_k is WLOG (mask inside Q_k); the Lean statement allows any y,z.
 - Split proof is simpler than O-form: X*X=0 so (I+X)^2=I, rank n. O-form not formalised.
 - Not proved (and not claimed by OL.md): rho_A+rho_B>=56; rank(I+X)>=56 is false for 0/1 decoders.

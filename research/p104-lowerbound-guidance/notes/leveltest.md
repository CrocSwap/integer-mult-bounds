# LEVELTEST (Nov 20, Sonnet, exact compute). Code: lt.py (lib), run_e8.py, run_all.py, run_gibbs.py, run_sa.py, run_hs.py; logs gibbs_*.log sa_*.log.
Setting (follows YC.md: rank over Q): decoder = W,V in Z4^{104 x m}, (W V^T - 2I) o Q = 0 mod 4. Row k: gather S_k = supp V[:,k], deposit D_k = supp W[:,k];
dim a_k = rank_F2 Q[S_k,:], drop = price = rank_F2 Q[D_k,S_k], dim b_k = dim a_k - drop. H=0 (relay-free), N=I, M_l = sum_{k: dim b_k < l <= dim a_k} W_k V_k^T over an integer lift;
rank_Q taken mod 2^31-1 (lower bound, = rank_Q generically). Lift-INDEPENDENT floor: sum_l rank_F2(M_l mod 2) <= sum_l rank_Q M_l for every lift. Both orientations (gather=V and gather=W).
Results [C]: S := sum_l rank M_l (min over std/sym/random lifts), floor F2 as above.
- E8-56: rows all (dim a, price, dim b) = (8,7,1); levels l=2..8 each carry ALL 8 rows, M_l = M, rank 8 => S = 7*8 = 56 = D = F2 floor. Tight.
- 168 transvection nbrs: S=D=58 (min), F2 58. 60 row-splits: S=57 min (D 64+).
- linear random factorisations (150, m=8..16): min S 71; sparse linear (100): 69; tight 8-row linear (120): 59.
- Gibbs nonlinear: stored g_2_4: D=S=86, F2 floor 65; g_3_8: D=S=128, F2 74. Fresh Gibbs walks (600 steps, E8+8 empty rows; randfact m=12): S min 56 (the E8 start) then 128/72-104.
- SA over Gibbs moves minimising the F2 floor (3000 steps, from E8 and from random factorisation): never below 56 (E8: stays 56; randfact: 72).
- half-spin quarter decoder (n=64, h=8): rows (7,6,b=1) x8, levels 2..7 carry rank 8 each => S = 48 = D = Gram floor (the 56 threshold is P104-only; need 38).
- sanity S <= D held in every one of ~1400 evaluations (also splits S<D).
No decoder with S < 56 found. Tightness: S=56 only at E8-56 (+ exact SA fixed point). Caveats: S=D in nearly all cases (lift-gauge rank gaps only in Gibbs: S>F2 floor); lift minimisation was random sampling not exhaustive; no proof.

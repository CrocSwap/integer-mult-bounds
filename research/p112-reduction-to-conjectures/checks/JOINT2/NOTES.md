# JOINT2 (Oct 16)
STATE: JOINT2: p=4 relaxed pair-cover UNSAT (impl A, kissat; DRAT check + impl B pending below). p=3 SAT even with phi_s. 113/262 follow from p=4 (see below); 263/399 composition not available to me -> UNFINISHED.
## phi_s refinement (exact statement used, phi.py)
For the A_{p-1} sub-triple (roots h01,h12,h02) restrict Lemma F (SEVEN S1) to V'=span(h's) (dim 2). Line t has w^t=(w0,w1,w2) in R^3/(1): w0=0, w0-w1=<r_t,h01>, w1-w2=<r_t,h12>.
phi_k|V' = coordinate x_k (x0+x1+x2=0 on V'). For K_t={k<3: t in L_k}: if t not in E_S need w^t in span(1,e_k:k in K_t)  [== pair-cover];
if t in E_S need w^t in span(1,e_k:k in K_t, phi), phi = phi_s|V' one global vector in R^3/(1). Encoded in satC.py: one-hot phi among {directions of all w^t} + generic;
clauses forbid (exact K pattern bad, phi incompatible, t not the extra free line). Free line treated as phi-exempt (weaker => sound for KILLED).
Result: p=3 stays SAT with phi (satC.py 3 0 1): X only has to hold the 3 roots h_ab, which sit in the third piece's support. So phi_s is useless at p=3 (weak, 2-dim V').
## p>=4 needs no phi
satP.py (generalised satB: own E8 build, chain A_{p-1}, pairs h_ab): control p=3 SAT (reproduces satB_model); p=4 (nx=3,x1=0) UNSAT; p=5 UNSAT.
Any A_{p-1}, p>=4 contains an A3 (4 pieces, 6 pair roots; W(E8) has ONE A3 class, so A6/A7 class multiplicity is irrelevant) and the same X, M_a => relaxed system UNSAT => rows 113 (X rank 6) killed;
262 needs x1=1 (rank-6 flat + 1 free line): see result line below. 
Files: satP.py, satC.py, satM.py (impl B: lib.py labels + gen.py Off-sets from JOINT/dp*.txt, one-hot over 43180 maximal masks, X by functionals), *.cnf, *.drat.
## Results (end of budget)
- p=4 nx=3 x1=0 UNSAT, kissat + drat-trim VERIFIED (satP_4_3_0_r.cnf/.drat, 151MB). p=5 UNSAT (no DRAT kept). p=4 nx=2 (rank-7 X) SAT, x1=1 nx=2 SAT; p=4 nx=3 x1=1 TIMED OUT at 900s (262 undecided).
- Impl B (satM.py, one-hot masks) built but only p=3 control CNF generated (4.2M clauses, SAT-solve not finished); p=4 NOT run. So no second-implementation agreement: 113 = impl A only.
- 263/399 compositions not available in my inputs; not attempted.
STATE: JOINT2: 113 KILLED by impl A (p=4 A3 sub-chain, DRAT-verified) pending independent 2nd impl; 262 UNFINISHED (x1=1 timeout); 263/399 UNFINISHED; phi_s adds nothing at p=3.

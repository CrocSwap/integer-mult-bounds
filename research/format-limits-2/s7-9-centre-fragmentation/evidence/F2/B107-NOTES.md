# B107: B99b v3 deletion of 44 "unused" S1 scratch. VERDICT: FAIL at check 2 (value exactness). ship=false. No kappa claim.
Scripts: c12.py (check 1), c2.py (check 2); both single-process, <2 min, on the #656 canonical word (B76 out_local), B99b lib (exact Fractions).
## Check 1 (which 44, what "unused")
44 = noB (A-only scratch, 224..447, not read/written in B, not centres: 67) minus cl_used (appear in compensation/cleanup/cut: 23) = 44 (e.g. 225,227,241,243,257,259,273,...,435). "Unused" only means: not touched in phase B, tail, cut, compensation, cleanup. NOT unused in A.
Every one of the 44 is a SOURCE in A: 19-25 reads each, 690 A ops in total of the form add(kept target, D source). Per-register tgt/src/src->kept counts printed by c12.py (e.g. 225: tgt 22, src 25, src->kept 22).
## Check 2 (value exactness)
Exact rational replay of A with all ops touching D removed (the v3 edit): 134 kept registers (e.g. 7,8,9,10,11,16,17,...) have a different end-of-A row than the shipped word. First failure verbatim: "kept regs whose end-of-A row differs: 134 [7, 8, 9, 10, 11, 16, 17, 18, 19, 20, 22, 23, 24, 26, 28, 29, 30, 35, 37, 38]" and "A ops with D source and kept target: 690".
So deleted ops feed kept registers: the edited word computes a different linear map. B99b v3 only measured the frame cascade (its own notes: "naive deletion ... upper bound on B98c"), never values. The -176 mass/call is the frame-model price of ops that carry the actual computation (these scratch are the S1 factory/gauge intermediates: B98c's foreign-read flaw is the same phenomenon).
## Checks 3-5
Not run (stopped at first failure, per card). No heavy.sh jobs used. No edited word, no kappa.
No SHIP CANDIDATE.

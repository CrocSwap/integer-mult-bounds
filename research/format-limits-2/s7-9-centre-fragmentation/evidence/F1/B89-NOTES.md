# B89: modular chains / supersolvable reader order for S3/S4 copies. VERDICT: KILL, PROVEN [scope: shipped #656 packets, reader set = union of both chains' downstream target ports P[t] (B82 taint), binary simple matroid of the port vectors]. ship=false
Lit verified (citations only, from memory): Stanley, Algebra Universalis 2 (1972) 197-217 (supersolvable lattice = maximal chain of modular elements); Terao, Adv. Math. 62 (1986) 135-154 (modular element => factorisation/fibration, over fields of char 0 hyperplane arrangements; the combinatorial part is lattice-only so applies over F2). Not re-fetched.
Tool: g.py (single process, <1 min; reads B82 work/out/rec.pkl). Brute-force modular flats, then chain search.
## Gate result (4 min)
- Reader arrangements: S3 156 packets: 8 distinct readers, rank 5; S4 112: 4 readers, rank 3. All 268 are DEPENDENT (not boolean, so not trivially supersolvable).
- Supersolvable (a maximal chain of modular flats exists): 0/156 S3, 0/112 S4. E.g. S4 = U(3,4) (circuit of 4 ports): rank-2 flats {1,2},{3,4} meet in 0, 2+2 != 3+0, so no modular line.
- Independent of that, order is vacuous: the copy-time frame F (S3 dim3, S4 dim5) already lies in perp of ALL reader ports (268/268, B82). So any reader order is fine AT COPY TIME; what fails is the later read (frame has grown with the register's own history; B82: 0/124 reads legal even first-read). A modular chain would only organise intersections of hyperplanes, not shrink the packet's content span, which is what the frame must contain.
- Mutation: 144 packets (32 S3 + 112 S4) are value-forced copies; no reader order helps.
## Count: 0/124 h1 S3 admit a modular order (0/268 total). Gate killed; no pricing run.
## Escapes (3)
1. Read both targets right after the copy while frame = F (B82 esc.1): needs target frames still in hyper intersections; DAG-level, depends on B83's weak bound (2478 psi, over-reports).
2. Non-supersolvable but lower-rank pieces: split the 8 readers by chain (4+4); not tested, but each half's rank also >= 3 and same obstruction expected.
3. Choose reader pairs sharing ports (B82 esc.3) in a new skeleton (SYN-4/B81).
Rescue check: restricted to per-chain reader sets of S4 (2 readers each) trivially modular but that is just the shipped single-chain reading, no copy saved.
TRANSFER: supersolvability of the reader sets is not the lever for S3/S4 copies; the lever is target-read timing (frame at read vs content span). Reuse g.py's modular-flat checker for any port sub-arrangement (use on B81 skeleton reader sets).

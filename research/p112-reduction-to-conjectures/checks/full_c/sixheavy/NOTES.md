# SIXHEAVY — 21/22 six-heavy L120 residue rows
STATE: SIXHEAVY: DONE (~135k tok). Lemma GRRC-2 + 9 cover facts (2 impls each, controls agree) kill 12 of 22 rows (169 312 316 332 333 418 420 426 427 430 435 464); 10 open (303 315 400 401 402 409 411 417 424 425). Kill bookkeeping: grrc.py/fill.py and chk2.py agree.
  Fact: minimal non-root Off sets = D7 78, E6A1 83, E6 84, A7 92, D5A2 97, A1A6 98, A4A3 104, A1A2A4 106 (T3 list); a rest of cap <=82 is non-root-coverable iff it covers D7.
  B: (6,6,6,6) and (6,6,6,5,4) do NOT cover D7; (6,6,6) does NOT cover a root (flat through r has <=16 Off-lines); controls (7,7) none/(7,7,1) cover agree with G3. Running fill.py = GRRC (grrc.py) with B oracle.

## Lemma GRRC-2 (PROVEN; j = 2 relative root counting with cover oracles in place of caps)
Setting: any scenario of CARRIER §1.3 where the Circuit Lemma (E8 version) applies (ClassI / β / α with the extra line as a unit / bumped piece / b3B).
Take K0 = d−2 pieces, comp = the rest (+ the α unit in every support). R'' ⊆ {c ∈ R : c|K0 = 0} 2-dim, V'' = h(R'') a plane.
Node p ∈ comp: some c ≠ 0 in R'' has c_p = 0, so Off_E(h(c)) ⊆ ∪_{comp∖p} Λ_E. If the rest comp∖p covers no NON-ROOT Off set, h(c) is a root (and
c is unique up to scale: a whole plane of such h would contain non-roots). Nodes p ≠ q give the same root only if comp∖{p,q} covers Off_E(root).
So 4 nodes with pairwise rests that cannot cover a root = 4 distinct root lines in a plane > 3 (A2). Contradiction.
Non-root reduction (CHECKED chkJ.py): every non-E7 standard parabolic J lies in one of the 7 non-E7 rank-7 ones or in E6, so a non-root Off contains
a W-image of one of D7 78, E6A1 83, E6 84, A7 92, D5A2 97, A1A6 98, A4A3 104, A1A2A4 106; a rest of cap <= 82 covers a non-root Off iff it covers D7's.
## Finite facts used (CHECKED, 2 impls: A = sa.py/cov.py/verA.py [lib.py labels, dual-kernel flats, python DFS, witness check];
## B = labB.py/covB.c/qB.py [own E8 build, labels <r,alpha_i> mod 2, types by explicit h search, primal-span flats, C DFS])
NOT coverable: Off(root) by (6,6,5,4), (6,6,4,4,2), (6,6,4,4,1,1), (6,6,4,4,1), (6,6,5,3,1);  Off(D7) by (6,6,6,5,4), (6,6,6,4,4,3), (6,6,6,4,4,2), (6,6,6,4,4,1,1).
Controls (both agree, witnesses verified): root by (7,7,1), (6,6,5,5), (6,6,4,4,4), (6,6,4,4,3,1) COVER; root by (7,7) NONE (= G3); D7 by (7,7,6,6) COVER.
Other B-only facts (not used): (6,6,6) cannot cover a root; (6,6,6,6), (7,7,6), (7,7,7) cannot cover D7; (6,6,5,5,5,4) cannot cover E6 (= RES116).
## Kills (every scenario; grrc.py + independent chk2.py agree) — 12 rows: 169 312 316 332 333 418 420 426 427 430 435 464. Certificates: certs.txt
## Remaining (10): 303, 315 (alpha, bump4 open), 400, 401, 402, 409, 411, 417, 424, 425 — need D7/E6A1/E6 non-coverability at slack >= 4 (B timeouts: (6,6,6,6,4), (6,6,6,5,5), (6,6,6,6,5), ...).

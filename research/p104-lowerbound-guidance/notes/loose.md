# LOOSE (Nov 20, Opus, theory + exact). Own code in this dir. venv python 1 proc, threads=1; kissat only, <= 20 min/run.

VERDICT (honest): full loose B-linear class NOT closed. Done: [P] centre formula for every B-linear row; [P] reductions that leave
exactly one open row type (EFFICIENT order-4 loose rows with B^-1 ybar not in Zbar16: 239 mod-2 classes, 11 Aut-orbits, <= 18 rows,
each dim U >= 3 and |D| >= dim U + 1); [P] F2 shadow relaxation (F2-REL) of the WHOLE class; [C] AUDIT: TIGHT55's cube partition
has a symmetry gap (so TIGHT55/DRAT55 are not yet a proof); sound cube scheme built; F2T campaign (re-proves TIGHT55 AND covers
tight + order-2 rows + every inefficient loose row + every loose row with ybar in Zbar16) 302/402 cubes UNSAT, rest running.
Why not a retread: TIGHT55 decided only rows y in +-G Z16 (16 slots). This lane handles ALL B-linear rows y in L4 = Z4^8
(32,895 classes: 16 tight, 255 order-2 rows y = 2e, 32,624 loose order-4 rows), via exact reductions + relaxations.

## 1. Price of a B-linear row has a CENTRE [P + C]
Row (y, U): v(s) = <c_s, y> mod 4, D = ports used (h_t in U; WLOG D = all ports in U), price = rank_F2 Q[D, S_y].
- price(y, U) = dim(U + n_y) - 1 where the centre n_y is
  * n = h_z = (1, zbar) for tight y = +-G z (z in Z16);
  * n = (1, p), p = B^-1 ebar, for y = 2e (order 2): S_y = {s : B(c_s, p) = 1};
  * no centre for every other y (order 4, not tight): price = dim U.
  Proof. Q = H beta H^T, so price = dim U - dim(U ∩ V^perp_beta), V = span h_{S_y}. For ybar != 0 put f = B^-1 ybar:
  the odd part {s : B(c_s, f) = 1} of S_y is an affine hyperplane section, which spans the hyperplane (1,f)^perp_beta
  (LINEAR56 rowbound [C]); y not tight => some port has value 2, that port has B(c_s,f) = 0, so beta((1,f), h_s) = 1 and V = F2^9.
  Tight y: S_y is exactly the odd part, V = (1,zbar)^perp. y = 2e: S_y is the section B(c_s,p) = 1. ∎
  [C lcore2.py checks] 600 random (y, D) pairs: 0 mismatches (loose: price = dim U; tight and 2e: dim(U + n) - 1).
- Consequence: an order-4 loose row costs exactly as much as a tight row (z, U + h_z) with h_z ∉ U. Looseness = "no free centre".

## 2. Reductions [P]
- (R1) MERGE (NONLIN): rows with the same +-y merge; one row per class.
- (R2) SINGLETONS = EXEMPTIONS: a row with D = {t} costs exactly 1 for every y with price > 0, and y = G c_t alone decodes t.
  So any row with |D| <= price can be replaced by |D| singletons (y = G c_t) without raising cost, and those ports can then
  be dropped from every other row (price is monotone in D). WLOG every non-singleton row is EFFICIENT: |D_k| >= price_k + 1.
  In particular every loose order-4 row with dim U <= 2 disappears; efficient loose rows have dim U >= 3 and an affinely dependent D.
- (R3) F2 SHADOW. Group rows by f = B^-1 ybar (drop y = 2e rows: f = 0, price >= 0). Merged price
  dim U_f - [f in Zbar16 and (1,f) in U_f] is <= the sum of the original prices (both-centred merge uses h_z in U1 ∩ U2).
  Decodability mod 2: cbar_t in span{f : t in D_f}. So min over the WHOLE B-linear class >= min of F2-REL:
  rows f in F2^8 \ 0 (255 slots), U_f subspace, price dim U_f - [f = zbar, h_z in U_f], port t: cbar_t in span{f : h_t in U_f}.

- (R4) GENERIC SLOTS. In F2-REL at budget B <= 55, after (R1)+(R2) every loose row (f not in Zbar16) is efficient, so price >= 3
  and there are <= 18 of them. Hence F2-REL(B <= 55) = 16 tight slots + 18 generic slots (f_j a free 8-bit variable, f_j ∉ 0 ∪ Zbar16,
  distinct, sorted) + exemptions. Mod-2 coverage is exact with all 255 functionals phi (no lazy clauses needed).
  The Aut(Q4)=384 lex-leader on the tight d-vector stays sound (the group maps loose f's to loose f's; re-sort the generic slots).

## 3. Exact computations (kissat, <= 1200 s per run; DIMACS in this dir, cubes in cubes/)
- esat.py = TIGHT55 encoding + exemption e_t (cost 1).  e56 (sym, from scratch): SAT in 114 s, edecode: E8 type,
  prices [0,0,0,0,7,7,0,7,7,7,0,7,7,0,0,7] = 56, 0 exemptions, all ports decodable.  e55: UNKNOWN at 1200 s.
- esat2.py + f2clauses.pkl = the same with MOD-2 covering clauses for tight rows (F2-tight + exemptions; clauses all of size 4,
  14-16 per port, each implied by a Z4 clause). f55: UNKNOWN at 1200 s.
- f2rel.py = full F2-REL with 255 fixed slots (2.1M vars, 7.4M clauses). r55: UNKNOWN at 1200 s (too big; superseded by f2gen).

### AUDIT: TIGHT55's cube partition has a gap [C lexgap.py]
TIGHT55 adds the d-vector lex-leader (d >= d o p for all 384 p) and then splits on the inactive set I = {z : d_z = 9},
running only I in reps.pkl (401 orbit-lexmax masks) + I = 0, claiming "d lexmax => indicator of I lexmax". FALSE:
d = (9,9,8,6,6,8,9,4,4,2,9,0,5,6,8,8) satisfies all 384 lex-leader constraints, but I = mask 1091 is not in reps.pkl
(random search finds many such d). So the TIGHT55 UNSAT (and DRAT55's certificates of those cubes) does not cover every
symmetry class. Toy reason: G = {id, (01)(23)}, d = (8,5,5,9) is lexmax but its 9-indicator (0,0,0,1) is not.
SOUND FIX (mkcube2.py, used for every run below): base CNF WITHOUT the global d-lex-leader; cube I (I in reps ∪ {0}) gets the
units for I plus the d-lex-leader over Stab(I) only. Every solution has an image with lexmax I, and Stab(I) still acts.
Controls with the fixed scheme: f56n cube I=25679 (E8 orbit) SAT in 2 s, edecode = E8 (56, all ports decodable).
Also sound: global d-lex-leader + VALUE cubes on (d_0, d_1, ...) (a value split is always a partition) — mkvcube.py; slower here.

### Campaign (sequential, one kissat; arun.py = adaptive sound cubes: UNKNOWN at T s => split d_z = 0..8 on the first free active z)
- F2T = F2-tight + exemptions (esat2.py, CLF=f2clauses.pkl). This is a relaxation of TIGHT55's class AND of
  "tight + order-2 rows (y = 2e) + any inefficient loose rows" (2e rows vanish mod 2; inefficient rows -> exemptions).
  Budget 55: 296 of 402 sound cubes UNSAT with base f55n (cubes/F2T.log, |I| >= 6 mostly, <= 330 s each);
  remaining 106 (|I| <= 6) run by arun.py on f55e (= f55n + WLOG efficiency |ports in U_z| >= price_z + 1): cubes/AF2T.alog.
- AG = F2-REL with >= 1 generic loose row (g55n, FORCEJ=1, J=18), after a control GCTL59 (budget 59, I=25679, >=1 generic forced).
  F2T (0 generic rows) + AG (>= 1) = all of F2-REL at 55 = the whole B-linear class (and A-linear by transpose).
- f2gen.py = F2-REL as 16 tight + 18 generic slots (0.49M vars, 1.5M clauses).

- Generic (open type) attempts: f2gen.py (phi-clause form) control at 59 SAT in 650 s (decoded 58: 7 tight price-7 rows +
  one tight price-1 row + one GENERIC price-8 row f=27, 52 ports; mod-2 decodable). f2gen2.py (witness form, 0.9M clauses):
  control SAT in 15 s (decoded 59 = E8 + a 4-port generic row of price 3). But budget 55 with >= 1 generic row: the E8-orbit cube
  I=25679 is still UNKNOWN after 600 s with J=18 and after >6 min even with J=1 (the same cube is 1 s without generic rows).
  So the generic part is not SAT-tractable in this form.

## 4. What is left / next
- F2T campaign: resume.sh -> arun.py (state AF2T.state.json, log cubes/AF2T.alog); verdict lands in F2T.STATUS (status.py).
  If all UNSAT: [C] F2-tight+exemptions >= 56, which implies TIGHT55 soundly, and >= 56 for every B-linear decoder whose
  efficient order-4 loose rows all have B^-1 ybar in Zbar16 (incl. all decoders using only tight, order-2, and small loose rows).
- Open core: efficient generic rows. Ideas not yet tried: (i) cube the first generic row's f over the 11 Aut-orbits
  (orbit reps 1,2,5,6,7,10,11,19,22,34,206; f=22 is Aut-fixed) with the d-lex-leader restricted to Stab(f);
  (ii) a "+1 per generic row" law (no generic row is free: best found 56+2 with one generic row) — would close it by theory.
- DRAT55 should switch to the sound scheme (mkcube2.py / arun.py), else its certificates certify an incomplete partition.
FILES: lcore2.py (Z4 span, prices), esat.py/esat2.py (tight+exemption CNFs; EFF/CLF/SYM env), f2clauses.py, f2rel.py, f2gen.py,
f2gen2.py, edecode.py, rdecode.py, gdecode.py, mkcube2.py (sound cubes), mkvcube.py (value cubes), arun.py (adaptive runner),
lexgap.py (gap witness), status.py, resume.sh.

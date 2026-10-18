# Format limits, part 2 (no κ claim): erratum to #595, invoice prices, censuses of the frontier word, decoder floors, spec requirements, centre and fragmentation walls

This package continues the merged #595 (`research/format-limits/`). It states results about the limits of the current
construction format and of the shipped #656 word, and checks the ones that can be checked. **It makes no κ claim and ships
no word.** Each result comes with its scope and assumptions. Each is marked:

- **CHECKED**: `verify.sh` recomputes it from the files listed below (exact arithmetic unless stated). *CHECKED (log)*: read off a shipped,
  sha256-pinned log that `verify.sh` compares but does not regenerate;
- **ARGUED**: a proof or a file:line argument in this README (the quoted lines are themselves checked where stated);
- **RECORDED**: the result of an earlier run that `verify.sh` does not repeat. Where a note or output is shipped under `evidence/` the row names it; otherwise the notes are not shipped (the row says so, or lists the record as "not shipped").

A row marked CHECKED for only part of its statement says which part; the rest carries its own status in the row's text.

```sh
python3 -m pip install -r research/format-limits-2/requirements.txt     # sections 5-9 only; sections 1-4 use the standard library
bash research/format-limits-2/verify.sh /fresh/output/dir               # from a checkout or `git archive` of the whole repository
```

Python ≥ 3.11; `requirements.txt` pins numpy, scipy and sympy; set `PYTHON` to choose the interpreter. Step 0 checks the package against
`MANIFEST.sha256` (every file) and every vendored input against its pin in `SOURCES.json` (git blob ids of the PR files, sha256 of the
rest), and stops with exit 1 on any mismatch. Then the four section groups run at once and print one `PASS`/`FAIL` line per assertion.
Nothing outside the package directory is read. Default: 233 PASS lines (2 in step 0), about 22 s wall on 12 cores (the four groups run at once). `E1_FULL=1 bash verify.sh ...` also re-runs #595's `a5_scope_multipliers.py` unchanged for E1: 228 PASS lines (a single PASS line, which summarises the 14 a5 claim lines, replaces the 6 fast E1 lines), about 62 s.

**Tested environments** (fresh `git archive`, every claim PASS, 233 PASS lines, exit 0):

| Python | numpy | scipy | sympy | how installed |
|---|---|---|---|---|
| 3.11.17 | 2.4.6 | 1.17.1 | 1.14.0 | fresh venv from `requirements.txt` |
| 3.14.7 | 2.4.6 | 1.17.1 | 1.14.0 | fresh venv from `requirements.txt` |
| 3.14.7 | 2.5.4 | 1.18.1 | 1.14.0 | development venv, latest releases |

Floating-point results (the F1 HiGHS MILP, the P1/P3 roots) are compared with explicit tolerances or exact decimals.

## Results at a glance

Sections: 1 erratum and scope, 2 invoice calculus and prices, 3 censuses of the frontier word, 4 cold ends and gauges, 5 decoder floors,
6 what the spec and verifier require, 7 centre barrier, 8 fragmentation and rigidity, 9 ledgers for skeleton changes. 31 rows by primary status: 21 CHECKED, 6 ARGUED, 4 RECORDED (rows partly CHECKED say so).

| id | result | status |
|---|---|---|
| E1 | **ERRATUM to #595.** The ×1.15–2.15 "schedule/ρ family" multipliers (#595 census item 8 and open problem 3; its A.7 table labels the rows "rule dropped") come from dropping idle-frame rules, not from a ρ family: idle changes free ×2.15, one-child batching ×1.55, no split pre-stretch ×1.18 at s = 9 (×1.15 best, s = 5), both sides. | numbers CHECKED; reading ARGUED |
| E2 | ρ is not a verifier input (it is the hard-coded final bank swap). Over all pair-preserving ρ at P ≤ 3 (reachable set exactly Sp(4,2) = 720 and Sp(6,2) = 1,451,520) none beats B_K: multiplier 1.000. | (b) CHECKED (log, re-run and compared); (a) ARGUED |
| P1 | Complex invoice calculus on #626 (reproduced to 16+ digits): centre −1 = +22.6% b; one cst unit +2.81%; one port +2.15%; one w9 helper +0.068% (+0.137% if its width merges). | CHECKED |
| P2 | Bit invoice calculus on #555: c reproduced to 24 digits; cst unit ±2.80% c, port 2.15%. Word-level helper knobs (0.06–0.11% c) not re-run. | root, mass, cst rows CHECKED; rest RECORDED |
| P3 | Helper exchange rate by width on #649: w9 0.070% (no merge) / 0.140% (merged), down to w4 0.026 / 0.072; explains the old 0.027–0.143 spread. | CHECKED |
| P4 | Stage count s = 9 → 7 is worse at every R: hosting overflows 8.7%, b₇ only +0.21% over b₉ at equal R. | CHECKED (model) |
| P5 | The climb mass is a forced cover (mass = mW − deficit): mass padding is illegal, frame annealing on the #626 ck/jp8 words gains 0.0% b (fixed op order; jump-merging frame raises as in #741 were not in the move set), "fewer helpers" is not a gain. | identity CHECKED; SA outcome RECORDED |
| C1 | Provenance census of #656: 492 helpers born at 4 allocation sites: S1 scratch 224, S3 packet copy 156, S4 slot copy 112; κ identity exact. | CHECKED (tags from a recorded rebuild) |
| C2 | The shipped word is a dirty-borrow program, not a clean SLP: 2056 distinct read rows (minimum chain cover 2056), 268 of 422 B-phase helpers are pure dirt, equal to the S3 + S4 sites. | CHECKED |
| C3 | The 112 ports form a cap in F₂⁹ (no three XOR to 0, every hyperplane misses ≥ 48); 8-port blocks sit at dimension ≤ 5. | cap CHECKED; corollary ARGUED |
| G1 | Gauge-free cold-end bound N_cold ≤ Σ_b(\|Q_b\| − rank C[Q_b]); #645 attains 44. | CHECKED on #645; 504 / K480 values RECORDED |
| G2 | Gauge44 is gauge-optimal at 44 for its frame schedule; read-order ceiling 48 (+0.13–0.16% b), home-first legal ceiling 46. | 44 = bound CHECKED; ceilings RECORDED |
| G3 | **Theorem.** A helper can end at a hyperplane U only if the supports of its row of M⁻¹ and its column of M lie in Q_U; covers every reordering and relay strategy. | ARGUED (Lean on #593's package RECORDED) |
| D1 | Complex decoder floor on P112: exactly 8 costly terms give cst ≥ 64 (9 label spans over 440,880 supports); all costly terms β ≥ 8 and n ≥ 9 give cst ≥ 72; n = 8 is infinitesimally rigid up to gauge. Open: mixed β ≤ 7 terms with n ≥ 9. | counts, spans, rigidity CHECKED; step (b), (c) ARGUED; flip-walk logs CHECKED (log) |
| D2 | Any n = 8 exact P112 decoder is D = XA, T = XA⁻ᵀ; absorbing one frame line costs exactly +1 cst, a pair +2 (≈ 272k and 951k sampled cases). | ARGUED; census CHECKED (log) |
| D3 | Non-star complex decoders exist: exact cst 63 on all six single-line P111 punctures, cst 56 on P104. Their buildability price is negative (net −0.1 to −10% b). | hits CHECKED (exact); walks CHECKED (log); price RECORDED |
| D4 | Structured classical decoders cost more than coordinate (64): rotations, WHT, halves 72; coset 4-split 192. | CHECKED |
| S1 | In-place elimination is dead under the shipped frame rules: 0 of 12,432 cross-port in-place pairs legal; 33 illegal reads in every row of M (41.2% of the off-diagonal support). | CHECKED |
| S2 | Spec dependencies of the sink wall: the endpoint operator holds on every role, so target sinks cannot be shared; a full sink forces M_in(X) = 0 only for idempotent labels (non-projection labels open). | ARGUED (citations CHECKED) |
| S3 | R2 (one identical exact representative per gate) is specification; relaxing it to a fixed finite set is unsound as a drop-in (h = 3 toy: 4 of 8 addresses moved). | CHECKED (toy) |
| S4 | Centre descents exist only for the 8 barrier centres of the shipped verifier; the "once per word" premise is false (centre −1 = +22.6% b). | ARGUED (file:line CHECKED) |
| Y1 | Centre/cut facts for M = I − G/2 on 112 D₈-root ports: rank G = 8, cut ranks 6/7/7/8, no weight-4 total in the span of the centres; rank 7 occurs at 8 coordinate splits. | CHECKED |
| Y2 | Full centre delivery is frame-illegal (448 of 456 reads); a 7+1 time-split barrier saves 0%. | rank part CHECKED (8 splits); rest ARGUED / RECORDED |
| F1 | Target fragmentation at the shipped op order: legal ceiling 950 of 1096 ops, loose format bound 229 psi/call (HiGHS-proved maximum 36), S3/S4 reader sets admit no modular chain (0/156, 0/112). | CHECKED for the stated parts; rest RECORDED |
| F2 | Tight-frames wall: legal iff G ⊆ U; slack arises only by deleting ops, time shifts, descents or equal-value re-threading; +1 dimension on any helper pushes 2–8 target frames 8 → 9. | ARGUED; instances RECORDED |
| F3 | S1 block scratch cannot be shared or shortened inside the format: 16 distinct sparse forms per block, 0 of 16 equal twins retireable. | RECORDED |
| F4 | Twin substitution for the 73 frame-insulator helpers fails on #656: all 111 twin reads are value-exact, 0 of 111 are legal one at a time (each raises 2–6 final caps), 0 of 73 helpers deletable. | RECORDED (exact oracle, not shipped) |
| F5 | Re-ordering reads of read-only S3 faces fails on #656: for 27 of the 32 structurally clean faces every B slot from the last write to the copy slot (window ≈ 740–860 ops), in given and reversed reader order, gives 0 legal reads. | RECORDED (exact oracle, not shipped) |
| F6 | The opening miner on the rebuilt #664 word finds 2534 disjoint-lifetime helper pairs; all 2534 need frame growth and none is frame-nested, so 0 register-reuse openings: the same rigidity as #656. | CHECKED (log) |
| O1 | Cross-block totals ("X4" faces): 2688 reach-10 quads all span 4 blocks; ledger 12.21% b (hypothetical design) does not close. | faces CHECKED; ledger RECORDED |
| O2 | #617 → #622 K-triangle ledger on the moment engine: ideal gross +0.52% b for 12 helpers, net +0.0146% after 6 lost cold ends and rewired climbs. | RECORDED |
| App. | **Appendix: conditional candidates** (5 items, each with one blocking condition; none is a result). | unverified |

Earlier statements this package relies on: sections A–F of #595 (cited as premises) and the words and pipelines of #622, #623, #626,
#635, #645, #646, #649, #656 and #659 read by the checks (see `NOTICE.md`).


## 1. Erratum and scope

*Sections 1-2: commands run from `s1-2-erratum-invoice/`.*

### E1. Erratum to #595: the ×1.15–2.15 "schedule/ρ family" is a set of dropped idle-frame rules

**Statement.** #595 (census item 8, open problem 3, B.2 rows 5, 12, 13) describes the multipliers ×1.15 to ×2.15 as the value of "the schedule/ρ
freedom". They are not. Each A.7 variant is `skel.profile` with one rule of the scope dropped (its docstring: "Each variant
… drops one rule"). The three that make up the range, recomputed with #595's own `skel.X`:

| variant (rule dropped) | complex 112/64, best s / s = 9 | bit 111/63, best s / s = 9 |
|---|---|---|
| idle frame changes free | ×1.68 (s = 7) / ×2.15 | ×1.67 / ×2.14 |
| all idle changes of one copy batched into one child | ×1.20 (s = 7) / ×1.55 | ×1.19 / ×1.55 |
| bridges moved off the idle stretches (no split pre-stretch) | ×1.15 (s = 5) / ×1.18 | ×1.15 / ×1.18 |

No ρ enters these numbers. The remaining A.7 variants (copy-free, loc_h, window−1) are reproduced by the full mode.

**Scope.** #595 `a5_scope_multipliers.py` at `b_K` with s ∈ {3,…,13}; complex 112/64 and bit 111/63. It says nothing about
whether a real word could drop an idle rule.
**Status.** CHECKED (numbers); the reading "not a ρ family" is ARGUED from the script's variant definitions (and E2).
**Depends on.** #595. **Check.** `python3 -I -B checks/e1_scope_multipliers.py` (16 s on two processes);
`E1_FULL=1` runs the vendored `a5_scope_multipliers.py` unchanged (all 14 claim lines PASS, 56 s).
**Consequence.** Open problem 3 of #595 should read: the schedule freedom is untested; the idle terms are not evidence for it.

### E2. ρ is not a verifier input, and no pair-preserving ρ beats B_K at the scalar layer

**Statement.** (a) ρ is hard-coded as the final bank swap (`columns_k.cpp:56`, `bit_global.py:49-55`), so a ρ sweep
cannot be run as a parameter. (b) Enumerating every pair-preserving monomial target ρ over F₂ with the moves of the format
(pair-local shears Y += X / X += Y at cost 1 local; bridges X_d += X_s, Y_s += Y_d), the reachable set is exactly
Sp(4,2) = 720 (P = 2) and Sp(6,2) = 1,451,520 (P = 3). For every target the minimum number of locals is 0 if no pair is
exchanged and 2k + 1 if k pairs are exchanged (k = number of exchanged pairs); the cheapest cost per exchanged pair is
(2P + 1)/P, attained by the full exchange (5 locals, 3 bridges at P = 2; 7 locals, 6 bridges at P = 3), which is B_K.
So no ρ beats B_K per served pair: multiplier 1.000.

**Scope.** P ≤ 3 bank pairs, the same ρ on every port, one pair per local. F₂ reduction is a necessary condition, so these
are lower bounds on cost. **Escapes (not enumerated):** non-symplectic or multi-bank locals (P ≥ 4), port-dependent ρ,
K ≥ 4 cyclic bridge graphs.
**Status.** (b) CHECKED (log): `rho01` is compiled and re-run and its output compared byte-for-byte with the shipped
`evidence/E2/rho01_P{2,3}.txt`; an independent Python search reproduces P = 2. (a) ARGUED: file:line from `evidence/E2/R39-S-NOTES.md`
(source files not vendored).
**Depends on.** #595, #622, #623. **Check.** `python3 -I -B checks/e2_rho.py` (2 s).

## 2. Invoice calculus and prices

All prices are exact finite differences of the pressure root b, the root a of Σ_r (r n_r / mW)(m/r)^a = 1, over the local
width profile {r: n_r} (Decimal, 50 digits). For #626: m = 73, W = 7168, deficit 2560 (mass = mW − 2560).

**Provenance of the #626 word data.** The register-level inputs (`inputs/derived/k492_registers.json`) are the climb widths
of every register of the ck and jp8 local words, derived by `tools/derive_registers.py` from the rebuilt `CANONICAL-WORD.json.gz`
files (the rebuild of the words from the #626 code, about 9 min, is RECORDED and not repeated). They are bound to the PR by
check: the word climbs plus the idle remainder {1: 123, 37: 1, 48: 2215} equal the PLAN profile of #626 exactly (`P1.gate-profile`),
and kappa = b/(1 + b) = 0.00163552738037539223… reproduces the README literal 0.001635527380375392 (`P1.gate-kappa`).

### P1. Complex invoice calculus: the knob table

| knob (all 72 calls) | change of b |
|---|---|
| remove one centre (local −17, host −9, deficit +576) | **+22.60%** (add one: −22.56%) |
| one cst unit: centre cut climb 8 → 7 / one unit climb dropped | **+2.81%** / +2.82% |
| source end FULL → 8 (one source) / target end 8 → 7 (one target) | +2.81% / +2.81% per unit |
| one port: v → v − 1 (deficit 2496, W − 64) | −2.15%, i.e. a port is worth **+2.15%** |
| one w9 helper removed (ck mean + jp8 mean) | +0.068% (freed width stays one narrow child) / +0.137% (merged into 48-bins) |

Reading: helper changes are mass-neutral (climb mass = hosted width); only the end frames of non-hosted registers (sources,
targets, centres) move the deficit, and one mass unit per call is worth about 2.8% of b, i.e. 20–40 helpers. The "once per
word" cost of a centre descent is false: a centre is +22.6%.
**Scope.** The #626 invoice at its shipped word: knobs are priced on the invoice, the word is not rebuilt for each. Source,
target and centre knobs use the modal shapes (sources (1,1,1,5) in 140 of 224, targets (1,1,4,1,1) in 104 of 224, all of mass 8;
all 8 centres (1,1,1,1,4,8,1)). **Status.** CHECKED. **Depends on.** #626, #649.
**Check.** `python3 -I -B checks/p1_knobs.py` (1 s). Notes: `evidence/P1/B15-NOTES.md`.

### P2. Bit invoice calculus (#555 R439)

**Statement.** The shipped c = 0.001733052823330162099157 is the root of the nine-stage profile with its bad term, reproduced to
24 digits (relative difference 1.2·10⁻²²); mass 1,808,352, deficit 10,272 = 256·111 − 288·63. One cst unit (a child r → r − 1 on
all 288 calls) is +2.8017% c (r = 7) to +2.816% (r = 1); the second unit +5.603% cumulatively.
**RECORDED (word-level, not re-run):** one port +2.15% c (cst-neutral), one helper +0.06–0.11% c (by climb pattern and idle
repack), sources and targets with near-identical knob values (`evidence/P2/B26-NOTES.md`; the script needs the per-register
climbs and takes more than 120 s).
**Scope.** #555 nine-stage word. **Status.** CHECKED (root, mass, cst-unit rows); the rest RECORDED. **Depends on.** #555.
**Check.** `python3 -I -B checks/p2_bit.py` (<1 s).

### P3. Helper exchange rate

**Statement.** Removing one helper of width w in all 72 calls (its climbs leave, w returns to the idle cover) changes b of
#649 by, in % (exact mean over all helper registers of that width in the ck and jp8 words):

| w | shapes | no merge | merged into 48-bins |
|---|---|---|---|
| 9 | 504 | 0.070 | 0.140 |
| 8 | 204 | 0.051 | 0.118 |
| 7 | 104 | 0.038 | 0.101 |
| 5 | 96 | 0.031 | 0.084 |
| 4 | 60 | 0.026 | 0.072 |

This explains the earlier spread 0.027 / 0.043 / 0.068 / 0.143: it is width (4–9) times the merge rule. The 48-merge column is
an upper bound that needs a re-pack the shipped words do not realise; #646 realises about the no-merge hosting. The profile roots
reproduce kappa of #649, #645, #646, #635 and #626 to 16 digits. (An earlier random-draw table gave 0.0725 / 0.141 for w9; it is withdrawn, and the check now asserts the table above.)
**Scope.** Climb-neutral removal at the #626 shapes on the #649 base profile. **Status.** CHECKED. **Depends on.** #649, #645,
#646, #635, #626. **Check.** `python3 -I -B checks/p3_rate.py` (2 s). Notes: `evidence/P3/B66-NOTES.md`.

### P4. Stage count s = 9 → 7 gains nothing

**Statement.** With the geometry m = 1 + 8(2P + 1), W = 2PTv, D = T[2Pv − (2P + 1)cst] and the P = 4 local profile unchanged:
at s = 7 (56 calls) the idle cover is 200,704 against 218,248 of hosted helper residual, an overflow of 17,544 (8.7% of the cover);
fitting needs k = 34.6 w9 helpers cut per call (R 492 → about 457). With the cut, b₇ is only +0.21% / +0.20% / +0.13% above b₉
at the same R for k = 35 / 40 / 60, while the same cut at s = 9 is worth +5.04% / +5.80% / +8.96%; at k = 234, 300, 480 the order is
s = 9 > 7 > 5 (b·10³: 2.412 / 2.395 / 2.303; 2.783 / 2.749 / 2.611; 4.793 / 4.611 / 4.108).
**Scope.** Model on the #626 per-call profile (P = 4 reproduced exactly); the P = 3 local program was not built, so a lighter
unit-climb profile there is not excluded. **Status.** CHECKED (model). **Depends on.** #626.
**Check.** `python3 -I -B checks/p4_s7.py` (<1 s). Notes: `evidence/P4/B54-NOTES.md`.

### P5. The climb mass is a forced cover

**Statement.** The invoice asserts mass = mW − deficit with the deficit 2560 an asserted constant (= 64v − 4608); mass padding
is therefore illegal and moving mass only reshapes it (moving 1% of the unit-climb mass into width-9 climbs would be +0.26% b if
it were legal). Frame simulated annealing over legal frame assignments (fixed op order, 6M moves per run) gains 0.0% b on the #626 ck/jp8 words (scope note: the move set did not include raising a gate frame inside an existing paid chain to merge two jumps; #741, on #699's SW4 word, gains that way, so this row does not bound such merges); (#698 proves the same fixed-order frame optimality exactly for the selected CK supplier's B-phase frames, over all reassignments preserving the scalar circuit, gate order and end-of-B frames; the annealing here is the weaker, sampled statement and is kept only for the climb-mass reading.) about 96% of
the unit mid-chain climbs are blocked by one rule family (common frame at ADD, monotone chains, target end frame perp(port));
the SSS hourglass word has climb mass 1976 against 6186 shipped, yet "fewer helpers" is not a gain.
**Scope.** Shipped ck/jp8, fixed op order, frame choice only. **Status.** CHECKED (mass identity, local mass per call, the
+0.26% arithmetic); the SA outcome, the blocking histogram and the hourglass comparison are RECORDED (`evidence/P5/B11-NOTES.md`,
`evidence/P5/B3R-NOTES.md`). **Depends on.** #626, #656. **Check.** `python3 -I -B checks/p5_cover.py` (<1 s).

## 3. Censuses of the frontier word (#656)

*Sections 3-4: commands run from `s3-4-census-gauges/`.*

All commands run from this directory; `verify.sh` runs everything below in about 3 s. The words used are
rebuilt artifacts that no PR commits as files; each is vendored with the hash its PR pins (`SOURCES.json`, step 0).

### C1. Provenance census of #656 (status: CHECKED; allocation tags: CHECKED given `g44-TAGS.json`, whose regeneration is RECORDED)
**Statement.** All 492 helpers of the shipped gauge44 word are born at 3 allocation classes (4 `alloc()` sites): S1 block scratch 224
(221 + 3 centres), S3 packet copy 156, S4 slot copy 112. Local profile {1:2542, 2:414, 3:434, 4:154, 5:56, 8:8}; the PLAN profile is exactly
72 x local profile + extras {2:4, 3:4, 5:1, 7:1, 16:2, 32:1, 48:2398}; mass 520704 = 73*7168 - 2560; root b = 0.0016568491378023079809...,
kappa = b/(1+b) = 1.654108529511355e-3 (the published value). Narrow mass per call (sum r ln(73/r) over climbs): S1 6902, S3 4430, S4 2754;
helpers 14085 = 68% of register narrow mass (X/Y registers 6637). Shares depend on the metric: 32.3 / 20.7 / 12.9 % of the global narrow
mass (which also holds 31.0% X/Y climbs and 3.1% idle windows), 47.9 / 31.4 / 19.5 % of the helper narrow mass (S1 without centres).
**Scope.** #656 head 0805e78f, shipped layered gauge44 word; the narrow-mass measure is a proxy for price, not a design claim.
**Depends on.** #656, #635. **Check.** `python3 -B checks/c1_census_656.py`. Existing run records: `evidence/C1/` (rebuild step exit codes, ledger tables).
The kappa identity and the local profile use only PR files and the hash-pinned word; the site split uses the tag file from the 9-minute tagged rebuild (not rerun here).

### C2. The shipped word is a dirty-borrow program, not a clean SLP (status: CHECKED)
**Statement.** On the #626 ck provider word (v = 112, 492 helpers): the 2056 distinct row values that are ever read each have readers forming a
single chain (frame inclusion, time order), so the minimum chain cover is 2056 (2483 value-holder pairs; 259 values held by two registers at different times, never redundantly
live: peak simultaneous redundant live helpers 0, sampled every 20 ops). 268 of the 422 helpers read in B have an all-zero row on the 112 source columns
(pure dirt scratch); the zero-ancilla map is t_p = s_p, while the real target rows have 36-97 terms over the 716 coordinates, so clean-SLP/count models
(BP synthesis, Dilworth, fill) do not describe it. On the #656 gauge44 word the same 268 helpers are, as a set, exactly the S3 + S4 allocation sites of C1
(previously only the counts 156 + 112 = 268 were known to agree).
**Scope.** fixed op order and values (exact rationals); frames by subspace inclusion; the jp8 provider and the dirt-register model of the B-phase legality rule are RECORDED only (not vendored).
**Depends on.** #626, #656. **Check.** `python3 -B checks/c2_dirty_borrow.py`.

### C3. The 112 ports form a cap in F2^9 (status: CHECKED for the cap; the dimension corollary ARGUED)
**Statement.** No three ports XOR to 0 and every hyperplane misses at least 48 of them (equality attained). Corollary: k readers' ports span rank r with k <= 2^(r-1)
(a cap of F2^r has at most 2^(r-1) points), so a frame inside their common perp has dim <= 9 - r <= 8 - ceil(log2 k); eight-port blocks sit at dim <= 5
(sampled: 8-subsets of ports always have rank >= 4).
**Scope.** ck ports of #626. **Depends on.** #626. **Check.** `python3 -B checks/c3_cap_f2_9.py`.

## 4. Cold ends and gauges

### G1. Gauge-free cold-end bound (status: CHECKED on #645; the 504 / K480 values RECORDED)
**Statement.** The gauge permutes which registers end low, never how many: N_cold <= sum_b(|Q_b| - rank C[Q_b]) with rank C >= 4 (the 4 pinned totals),
a rank-nullity bound. #645 attains 44: six blocks with |I| = 6 and eight with |I| = 8 (sum |I| = 100), rank Clean = rank M[I, protected] = 4 in every block,
attained pairing rank 2 (short blocks) / 4 (the others). The 504 factory gives 56 (sum |I| = 112) and K480 gives 32 (sum |I| = 88): RECORDED (x646 rebuild, not rerun).
**Scope.** #645 FULL-WORD, exact rationals, frames of dim <= 7, home-first legality unchecked. **Depends on.** #645, #646, #604, #531 (Hamming inputs).
**Check.** `python3 -B checks/g1_gauge_bound.py` (0.4 s).

### G2. Gauge44 is gauge-optimal for its frame schedule (status: CHECKED for the 44 = bound part; the ceilings RECORDED)
**Statement.** Rank is 4 in all 14 blocks and the attained 44 equals the bound, so more ends need a larger |I| (a different frame schedule). RECORDED from
cards B58/B60/B61/B56: the real read-order ceiling is 48 (+0.13-0.16% b), the 88 of the gauge count is unreachable, six short blocks cannot reach 56 (K-reads lift
locations), the home-first legal ceiling is 46. **Check.** the G1 script (G2 line); `evidence/G2/rep1.log` is the existing log of the #645 rebuild (all steps PASS).

### G3. Necessary condition for a cold hyperplane end (status: ARGUED; Lean on #593's package RECORDED, none added)
**Theorem.** In the monotone-frame model (no descents), fixed forward word with state map M, cleanup any gate sequence with G M = I: a helper h can end at a
hyperplane U only if supp(row_h M^-1) and supp(col_h M) both lie in Q_U = {registers whose end-of-B frame is inside U}.
**Proof sketch.** Every gate touching h has frame inside U; a gate whose frame is not inside U shares no register with a later h-gate, so it commutes after it. Hence
G = R_h P_h with P_h acting only on Q_U and R_h fixing h; row_h(G) = row_h(P_h) and M e_h = P_h^-1 e_h. This covers every reordering, toggling and relay strategy
(only the factorisation of M^-1 is free). Conversely a biorthogonal family supported in Q_{U_i} is realised by block elimination followed by a FULL-frame cleanup.
The column (dirt) condition corrects all earlier row-only counts. Multi-gate cold wrappers are covered by `HyperplaneEnd/Multi.lean` on #593's package (existing, not rerun).
**Scope.** monotone frames and a fixed forward word; the "14 at d <= 5" cap of the fixed-content premix analysis is superseded by G1 and must not be quoted.
**Depends on.** #593, #591, #604, #617. **Check.** none (argument); no solver evidence exists for this row.

Evidence note: rows C1-C3 and G1-G3 used no SAT, CP-SAT or DRAT; the only shipped logs are the rebuild records under `evidence/`, pinned by sha256 in `SOURCES.json`.

## 5. Decoder floors

*Sections 5-6: commands run from `s5-6-decoders-spec/`.*

Model for D1-D4 (checks/e8model.py): P112 = the 120 E8 root lines minus the 8 frame lines e_{2a} +- e_{2a+1}; each line has a label in F2^9; a decoder is a set of terms (d_k, t_k) with sum_k d_k t_k^T = M4 = 2G on the kept lines (G the integer E8 inner products); the cost of a term with row support R and column support A is the F2 rank of the label pairing U(R) x U(A) (the Theorem C pairing rank of #595 C.3), and cst is the sum over terms. The coordinate decoder (8 stars) has cst 64.

### D1. Complex decoder floor on P112
- **Statement.** (a) Reduction: a term with R x A inside the label-orthogonal pairs (N = 0) costs 0, and all 5824 such entries of M4 are nonzero, so they are fixed for free; exactness only constrains the E-graph (N = 1, 60 per row, diagonal included): x_i . y_j = 0 on even-inner-product pairs, x_i . y_i = 4. (b) With exactly 8 costly terms (rank_Q K = 8) every term is supported on the complement of a hyperplane flat; the 440,880 distinct such supports have only 9 distinct label spans (eight of dimension 8, one of dimension 9), every pair has pairing rank >= 8, so cst >= 64, attained by the coordinate decoder. (c) THEOREM (trivial): if every costly term has beta >= 8 and n >= 9 then cst >= 72. (d) The n = 8 system is infinitesimally rigid at the coordinate point up to gauge (tangent nullity 175 = 64 + 112 - 1). (e) The frame-substitution bound cannot prune mixed-beta decoders: the E-graph has exactly 1260 cliques of size 8 (none of size 9); the best (fraction of frames hit)/beta over the searched label-span pairs is 1/8 at beta 8 but 0.1825 at beta 4, 1/6 at beta 6 (a beta-6 pair hits all 1260 frames) and 1/7 at beta 7, so the covering bound is only 8/0.1825 = 43.8 < 64.
- **Prior work.** #620 (GamingPuzzled) already states a complex P112 frame decoder of cost 64 (`cxp.py`) and that deeper punctures were worse in a search (not exhaustive). New here: the 8-term hyperplane-flat census, the rigidity (d), and the beta >= 8 bound (c).
- **Scope.** P112, linear pairing-rank model, real coefficients. (b)-(c) cover exactly the decoders all of whose costly terms are hyperplane-flat supports. Open: decoders with n >= 9 mixing beta <= 7 terms (a cost < 64 would have to live there); the rigidity in (d) is the tangent space at one point (global rigidity was only sampled: 10 of 12 random-start solves converge, all to gauge-equivalent solutions; RECORDED, not shipped); the maximum in (e) is over hyperplane and random codim <= 3 pairs (sampled, not exhaustive over subspace pairs, and the bound only falls if a larger ratio exists).
- **Status.** CHECKED for (a), (b) support/span counts and minimum rank, (d), (e); (b)'s step "supports of an 8-term decoder are hyperplane flats = W(E8) orbits of the fundamental weights" is ARGUED (rigidity (d) plus the orbit census); (c) is ARGUED (one line). CHECKED (log): the shipped flip-walk logs on P112 (three walkers, ~1.5e8 iterations) found no state below cost 64 and no state with n > 8 at cost <= 64 (evidence/D2/d1-d3.out). No SAT/CP-SAT proof exists for the n >= 9 hole: both attempted runs (B14 CP-SAT symmetric ternary lift; B72 CaDiCaL support relaxation, 23,904 variables, 1,540,851 clauses) were killed without a result (exit 143; evidence/D1/); no UNSAT claim and no DRAT file are made.
- **Depends on.** #595 (C.3, Theorem C), #446.
- **Check.** `cd checks && python3 -B d1_decoder_floor.py` (15 s), `python3 -B d1_frames.py` (20 s), `python3 -B log_checks.py` (<1 s).

### D2. An n = 8 exact P112 decoder extends uniquely, at +1 per absorbed line
- **Statement.** Any exact n = 8 decoder of P112 is D = XA, T = X A^{-T} with X the coordinate decoder and A in GL8 (rank-8 factorisation rigidity, D1(d)); hence its extension to a frame line j is unique (new entries d_k[j] = 2A[j,k], t_k[j] = 2(A^{-T})[j,k]), so absorbing a line is a pure cost question. Over 33,981 sampled cost-64 plateau states of three walks: absorbing one frame line costs exactly +1 (271,848 cases) and absorbing a pair costs exactly +2 (951,468 cases), always integer-valued and exact. So P113 = 65 and P114 = 66 at n = 8; the walk on P113 (two walkers, ~2e8 iterations each) never went below 65.
- **Scope.** n = 8 states; census sampled on the walk's plateau (not a proof of gauge invariance of the +1); P115/P116 not run.
- **Status.** ARGUED (uniqueness) + CHECKED (log) for the census and the P113 walks (evidence/D2/cen1-3.out, w1-2.out). The state dumps and the census script are not shipped.
- **Depends on.** D1.
- **Check.** `python3 -B checks/log_checks.py`.

### D3. Non-star complex decoders exist on P111 and P104
- **Statement.** (a) For each of six single-line punctures of P112 (lines 0, 1, 30 of D8 type; 48, 70, 111 of half-spin type) there is an exact 8-term decoder of cost 63: seven terms of cost 8 and one of cost 7, coefficients up to 3; for punctures 0 and 111 also with coefficients in {-2..2}. With coefficients in {-1,0,1} the same walk stays at 64 (60 s, may be walker-limited). (b) For P104 = P112 minus the 8-clique drawn by `numpy.random.default_rng(1)` (lines 9, 15, 24, 46, 52, 66, 94, 104; pairwise label-nonorthogonal) there are exact 8-term decoders of cost 56 (eight terms of cost 7), found by three independent walkers. (c) Flip-walk logs: on P111 the walks also visit states with n up to 11 at cost <= 64, unlike P112 where none exists (D1).
- **Scope.** The decoder model above; no word is built from these decoders. Their buildability price is RECORDED, not shipped: the parity cost of unpaired centre reads (>= 78), 96 pair-split conflicts and net -0.1..-10% b, and the emitter hard-wires the coordinate decoder.
- **Status.** CHECKED (exactness, n, per-term costs of 8 + 3 hit files); CHECKED (log) for the walks (evidence/D3/); price RECORDED. Bit-side P111 63 is #620's result and is not repeated. Relation to prior work: #620's sampled search found deeper complex punctures worse; the exact cst 56 on P104 (56/104 < 64/112) here contradicts that sampled statement on the complex side. #631 proves that no puncture of up to 35 lines improves the star ratio 63/111; the P104 decoder is non-star, so the two do not conflict.
- **Depends on.** D1, #595 (C.3), #531.
- **Check.** `cd checks && python3 -B d3_punctures.py` (<1 s).

### D4. Structured classical decoders cost more than the coordinate decoder
- **Statement.** In the copy-cost model on P112: coordinate 64; D2-butterfly pairs (2a,2a+1), halves (j,j+4), D4 Hadamard, permuted pairs and the full Walsh-Hadamard transform all 72; the D8 / half-spin coset 4-split is n = 32 terms of beta 6 each, cst 192. On all 112 single-puncture P111s the values are constantly 64, 72, 72 and 192.
- **Scope.** These linear front ends only (Conway-Sloane / Forney / trellis decoders are non-quadratic; the model sees only which functionals feed the quadratic form). No bit-unit run.
- **Status.** CHECKED.
- **Depends on.** D1.
- **Check.** `cd checks && python3 -B d4_structured.py` (3 s).

## 6. What the spec and verifier actually require

### S1. In-place elimination is dead under the shipped frame rules
- **Statement.** In the ck word of #622/#626 the end frame of target t is perp(port_t) and no port lies in its own end frame (0/112). Hence a cross-port in-place operation t_a += l t_b (common frame span{port_a, port_b, port_a ^ port_b} inside both end frames) is legal for 0 of the 12,432 ordered pairs; the legal target-from-source reads are exactly 5824 (port_b in perp(port_a)), none diagonal. The content map M (112 x 112, rank 112, 9072 nonzeros) recomputed by exact replay of the A, B and cut phases has 5264 of its 8960 off-diagonal entries inside the legal read mask; every row needs exactly 33 illegal reads (3696 = 41.2% of the off-diagonal support). So PMH/Gauss/lifting/Steiner/Tellegen-type eliminations, which need in-place or direct reads of the whole support of M, reduce to this wall.
- **Scope.** The ck canonical word, frames as F2^9 subspaces, monotone nested per register, one common frame per ADD. **Erratum to the candidate note:** an earlier figure, 4164 of 8960 legal (54% illegal, 35-52 illegal reads per row), came from a port-indexing mismatch: the content map of the #656 FULL-WORD was read through the ck word's port mask. With its own ports that FULL-WORD also gives 5264 legal and 33 illegal reads per row, the same as ck. The figure is not a property of any word and is withdrawn. The qualitative statement (0 in-place edges, every row needs illegal reads, M of full rank on both sides) is unchanged.
- **Status.** CHECKED.
- **Depends on.** #626, #595 (Lemma N).
- **Check.** `cd checks && python3 -B s1_inplace.py` (<1 s). Input inputs/pr626/ck-CANONICAL-WORD.json.gz (blob 58cd1be8 of #656 head 0805e78f).

### S2. The spec dependencies of the sink wall
- **Statement.** (i) The shear contract M_out(rho(w)) - M_in(w) = I_m must hold on every role including scratch roles (04-swap.tex:117-121, 183-187), with rho a permutation (105-109); so a target sink is determined by its partner's source and sinks cannot be shared among targets. (ii) For the projection motif the source is -P_{U_a} and the sink P_{U_a^perp} (03-motifs.tex:469-473, 519-525), so a FULL sink forces M_in(X_a) = 0 for idempotent labels; for general rational labels the saving per pair is still <= m (floor rank(I+T-S)+rank(I+S-T) >= m), a pair that saves pays its whole saving on a direct self-read, and excess is integer per wire, but the sink charge >= 1 is NOT proved for non-projection labels (toy over F_3, m <= 3: only a two-class design reads cheaper, <= ~25% of pairs, priced 0.0% for the two-class design). (iii) Nesting is essential only for the premise of Theorem A; other uses (edge ranks, deficit identity, Lean exactness) are replaceable by a non-nested step priced d(f,g) = dim f + dim g - 2 dim(f cap g); the cheapest non-nested step is a rank-1 descent plus re-climb = 2 mass per call (-5.6% b at the 2.81% per unit invoice). (iv) Calls equal the sum of edge ranks, each on one role stream (04-swap.tex:197-199), so corrections on different roles do not share a call.
- **Scope.** Motifs with projection or subspace labels; non-projection rational labels are neither excluded nor realised. Open problem: a lower bound for arbitrary contract-satisfying circuits.
- **Status.** ARGUED; the quoted lines are CHECKED by checks/anchors.py (spec files of main at 66849e1, vendored under inputs/main/ and pinned by blob id). The charge arithmetic (2.81% per unit) is row P1.
- **Depends on.** #595 (B, C.1, C.7).
- **Check.** `python3 -B checks/anchors.py`.

### S3. Rule R2 is specification, and a relaxed R2 is not a drop-in
- **Statement.** R2 (one identical exact representative on all registers incident to a scalar gate; notes/general-clifford-frames.tex:61-65) is what makes the word compute M tensor I; the verifier mirrors it at label level (hpe_audit_local.py:75, `assert cur[r[1]]==f`) and the Lean tree does not encode it. Relaxing it to representatives differing by a right logical permutation from a fixed finite set is unsound as a drop-in: in the h = 3 exact-Clifford toy the gate's logical effect is a permutation with 4 of 8 addresses moved instead of the identity; a sideways label gives a non-monomial map moving 8 of 8; the group-ring span of S3 on 3 qubits has dimension 5 of 64, so cancellations are not available.
- **Scope.** The toy is h = 3, a single physical add; the general soundness failure (non-uniform twists) is ARGUED in the cited paper rule, not exhibited for a full word.
- **Status.** CHECKED (toy); citations CHECKED by anchors.py.
- **Depends on.** #595 (B, C.6).
- **Check.** `cd checks && python3 -B s3_r2_toy.py` (<1 s).

### S4. Centre descents exist only for the 8 barrier centres
- **Statement.** The shipped verifier (inputs/pr622/coupled_frames_base.py) accepts a frame descent only for the registers declared `centers`: they are barrier nodes at the A/B cut (lines 95-99), each descends through a strictly nested chain of the frames of its cut readers (:144-148, error `center descent not nested`), billed one counter entry per rank step; every other register chain must be monotone (:163, `nonmonotone`) and a change at a barrier node is refused (:164-165, `unbilled cut transition`); end-of-B finals are FULL (non-port) or the fixed hyperplane perp(port) (ports) (:100-108). Consequences: hubs/helpers cannot use descents (they are dirty and read in phase B); the premise "a descent is paid once per word, 72x cheaper" is false, since the local program runs in every call (centre -1 = +22.6% b in the invoice calculus, section 2, P1); promoting hubs to centres fails on the role (clean private scratch, no B events). The count 8 is a convention; the role is the obstacle.
- **Scope.** The shipped verifier and the #622/#623 words; a Lean statement for a hoisted descent does not exist.
- **Status.** ARGUED; file:line citations CHECKED by anchors.py.
- **Depends on.** #622, #623, #595 (C.7).
- **Check.** `python3 -B checks/anchors.py`.

## 7. Centre barrier

*Sections 7-9: commands run from `s7-9-centre-fragmentation/`.*

Object: the 112 D8-root lines of the complex unit (blocks = 8 consecutive lines on one octad), `R` = `root_lines` and `M` = exact replay of the A, B and cut phases of the #656 word (`inputs/pr656-FULL-WORD.json.gz`); `M` is equal up to port relabelling to the content map of the #623 `ck` provider (eigenvalues and row multisets agree; only 52 port labels are shared, so it is not elementwise equal).

### Y1. Cut ranks, centre supports, totals  (CHECKED, with one caveat)
- rank G = rank RᵀR = 8; matched-order cut ranks of M at sizes 14/28/56/84 are 6/7/7/8 (prefixes, not a smaller state).
- Random 56|56 bipartitions (2000, seeded): off-diagonal rank at most 8 (a sample). Of the 1716 splits of the 14 blocks into 7|7, **1708 have off-diagonal rank 8 and 8 have rank 7**; the 8 exceptions are the coordinate splits (lines with R[:,j]=0 versus not). So "rank 8 at every cut" is false as stated: rank 7 occurs at those 8 splits, and the argument that no centre is saved rests on Y2's price argument, not on rank.
- The centre code R mod 2 has nonzero F2 weights exactly {56 (128 vectors), 64 (112 vectors)} and a 4-dimensional kernel (15 of the 255 nonzero coefficient vectors map to 0, so there are 16 distinct codewords: 8 of weight 56 and 7 of weight 64 plus 0; the counts 128 and 112 count coefficient vectors). Over Q the minimum support of a centre combination is 53 among 20000 seeded hyperplane normals (an upper bound on the true minimum); ARGUED lower bound: the 120 lines (112 rows plus the 8 lines 2e_i, a reflection-closed set; closure is checked here only partly, with the first 60 of the 240 roots as reflectors) have at most 63 lines in any hyperplane (the largest proper root subsystem of E8 is E7, 126 roots), so every nonzero centre combination has support at least 49 > 4. Hence no weight-4 cross-block total lies in the span of the centres; each such total adds exactly +1 rank (300 seeded totals).
- Scope: M on these 112 lines with the coordinate decoder. Totals defined target-side or in another basis are not covered (the span of the centres and a block's 8 target rows does contain the block's local forms: RECORDED, `evidence/Y1/B10-NOTES.md`).
- Depends on: #656 (word), #626, #595. Check: `y1_centre_cut.py`. Records: `evidence/Y1/`.

### Y2. Full centre delivery and a 7+1 time-split barrier  (partly CHECKED, mostly RECORDED/ARGUED)
- CHECKED: for the 8 coordinate 56|56 splits, rank (G_AB, G_AA, G_BB) = (7, 7, 8). The recorded claim "on all 56|56 splits" was only run on these 8 splits and is stated as such.
- ARGUED (`evidence/Y2/B106-NOTES.md`): a time-shared 7+1 schedule is algebraically fine but keeps 8 decoder terms (cst 64 = 8 x beta 8), so the invoice saving is 0 unless the extra term has beta < 8; a second descent epoch is a new skeleton role (descents are legal only at the barrier node before B, row S4), against the price of at least 5.6% b per rank-1 descent (#595 C.7).
- RECORDED, NOT reproduced: frame-illegality of full centre delivery (448 of 456 (target, centre) reads violate; a centre read is legal only for t = f_i, the shipped cut). The script (`B101 gate.py`) needs PROTOTYPE.json of the #656 rebuild, which was not found; the record is `evidence/Y2/B101-NOTES.md`.
- Depends on: Y1, S4. Check: `y1_centre_cut.py` (the y2 line).

## 8. Fragmentation and rigidity of the shipped word

### F1. Target fragmentation is forced at the shipped op order  (CHECKED for the stated parts)
Overlap: #698 (thakrarsagar) certifies exactly that the selected CK supplier's B-phase frames minimise the paid moment over all frame reassignments preserving the scalar circuit, gate order and end-of-B frames (474 of 1930 B gates have freedom). The fixed-order frame-ceiling statements below are cited to #698; what is distinct here is the target end-frame cascade, the S3/S4 reader-chain and carrier counts, and the format-level bound.
Provenance correction: the frame-level checks use the `ck` (8 calls) and `jp8` (64 calls) K-triangle provider words of #622/#623 (copies inside #656 at `research/community-k492-audit/pr622/replay/*-local/CANONICAL-WORD.json.gz`), not #656's own layered word (their local profiles differ). The S3/S4 packet checks use a record of the rebuilt #656 word.
- CHECKED (`f1_frag.py`, both providers): 1096 target-touching ops, 950 already at the legal reverse-closure ceiling U, 146 with one dimension of slack. Setting every op to U is legal and costs +520 (ck) / +700 (jp8) psi per call. Setting only the target ops to U is **not** a legal assignment (50 non-monotone climbs); its model value is -5.6 psi per call (T +2.7, helpers -5.5, sources -2.8), far below the 65 psi GO line, and is indicative only. The earlier phrase "legal ceiling, net -5.6" should be read this way.
- CHECKED (ck): target fragmentation 1342 psi/call; the port-cap ceiling (direct ports of an operand's unserved readers, shipped reader order) would allow 614 psi/call, a loose bound that ignores all other constraints on the operand ("70 percent of target ops are held below the port cap by helper and source partners" is a recorded figure, not checked here).
- CHECKED (`f1_pack.py`): the format-level bound. Each target that reads some operand as a non-last reader has a stop at dimension d < 8 and pays at least 3.014 psi. The largest set of targets that can be last readers of all their operands is an independent set of 112 vertices; HiGHS proves the maximum is **36**, so the bound is 3.014 x 76 = 229.08 psi/call (the earlier time-capped search found the same 36 without proof). Loose: it uses only SPEC plus cap geometry.
- CHECKED (`f1_s3s4.py`, from the derived record `inputs/b82-rec.json`; the derivation is RECORDED, not re-run): the 156 S3 packets (8 readers, rank 5) and 112 S4 slots (4 readers, rank 3) are all dependent reader sets; none admits a maximal chain of modular flats (0/156, 0/112; S4 is U(3,4)). At copy time the copy frame is orthogonal to all reader ports (268/268), so the obstruction is the later reads (0/124 legal at first read: RECORDED, `evidence/F1/B82-NOTES.md`).
- CHECKED (`f1_carriers.py`): the 112 ports form a cap in F2^9; each source has 52 readers; cap-aware greedy coverings by port quads need 14.29 carriers per source (14 to 15; lower bound 13), 1601 in all. The comparison with the saving (carriers cost about 12.5 psi hosting each, at most 905 psi/call to gain) uses booked rates: RECORDED.
- RECORDED: format-level loose bound gap at least 1004 psi/call (at most about +5.5% b); order-free loose bound 2478 psi/call (uncalibrated); no skeleton-free bound.
- Scope: fixed op order and DAG, A+B+tail ops; other orders open. Depends on: #622, #623, #656, #659. #661 treats a different object (bit R420), cited. Records: `evidence/F1/`.

### F2. Tight-frames wall  (ARGUED; instances RECORDED)
Fixed-order frame optimality of a single supplier is #698's exact certificate (cited); the wall below is the word-level statement across ops, and the instances are about deleting or moving ops, which #698's domain excludes.
The minimal frame G(r,t) is the join of start frames over time-respecting undirected journeys and the cap U is the meet of locked frames forward; a frame assignment is legal iff G is inside U. Adding ops only grows G and shrinks U, so slack arises only by deleting ops, time shifts, descents (8 barrier centres) or re-threading at equal value. Instances (RECORDED, `evidence/F2/`): one extra dimension on any helper frame pushes 2 to 8 target end frames from 8 to 9 (#656, #659, #646 words); early uncompute or reuse of A-only S1 scratch is blocked by the single common frame of the uncompute ADD (0/67 legal, #656; 0/67 on #659); dyadic S1 programs, rematerialisation, equal-value re-threading and scaled swap-back windows (up to 58,961) lower no frame. Lesson recorded in B107: a frames-only deletion price (-176 mass/call) was not value-exact, so every deletion card must replay values first. Scope: shipped #656/#659 at fixed order and DAG. Depends on: #656, #659, #664. #665 (rehosting boundary) is a different instance.

### F3. S1 block scratch is not shareable or shortenable inside the format  (RECORDED)
The 16 scratch per block are distinct sparse forms (rank 8 to 9 of an overcomplete 24-form Haar/Walsh frame); gauge-exchangeable copies g2 = 0; the 16 equal twins are value-forced (0 of 16 retireable); block frames meet pairwise in dimension 2 (91/91) but 80 of 132 registers have frame dimension 3 to 4, so no cross-block mix has a common frame; the 154 required forms are distinct and none is a 2-term combination. Scope: #656 S1, exact value replay (cards B90-B97; no scripts are kept for B92/B94/B97). Not re-run. Depends on: #656. Records: `evidence/F3/`.

### F4. Twin substitution does not remove the frame-insulator helpers (RECORDED negative)
**Statement.** On #656, at every read of 73 helpers (62 S3 copies and 11 S1 scratch) another register holds a multiple of the helper's value. Replacing each read by a read of that twin gives 111 twin reads, all value-exact; 0 of 111 are frame-legal one at a time, and each substitution raises 2–6 final caps. So 0 of 73 helpers can be deleted this way.
**Scope.** #656 at its shipped op order, one substitution at a time; the exact whole-word oracle (values, frames, κ; 0.04 s per evaluation). Joint or reordered substitutions are not covered (F2).
**Status.** RECORDED: the oracle and its run are not shipped in this package. **Depends on.** #656.

### F5. Meet-frame reads of read-only S3 copies are not legal (RECORDED negative)
**Statement.** 116 of the 156 S3 copies are read-only after the copy; each face's frame lies inside the orthogonal of exactly its 8 readers (meet of dimension 5). For about 27 of the 32 structurally clean faces, every B slot from the face's last write to its copy slot (window about 740–860 ops) was tried, in the given and in reversed reader order: 0 legal reads.
**Scope.** #656 shipped word, the 27 faces tried, the stated orders. **Status.** RECORDED (exact oracle, not shipped). **Depends on.** #656, row F1.

### F6. The opening miner finds no register-reuse opening on #664 (CHECKED (log) negative)
**Statement.** On the rebuilt #664 word the miner (the #656 miner of F2) lists 2534 disjoint-lifetime helper pairs. All 2534 need frame growth (`grow` 2534) and none is frame-nested, so there are 0 register-reuse openings. This is the same rigidity as on #656, although #664 spends entrance G < U slack on three promotion groups.
**Scope.** Disjoint-lifetime helper pairs of #664 only; the other miner categories (one-dimension-growth renames, idle-gap hosting, equal-content pairs) are not part of the shipped log.
**Status.** CHECKED (log): `evidence/F6/miner664_run1.out` and the job summary `evidence/F6/B105_miner664.log` are sha256-pinned; the miner and the rebuilt #664 word are not shipped, so the run is not repeated. **Depends on.** #664, #656, F2.

## 9. Ledgers for skeleton changes

### O1. Cross-block totals ("X4" faces)  (faces CHECKED; ledger RECORDED)
- CHECKED (`o1_faces.py`): over all 1001 x 4096 quads of lines in four distinct blocks, exactly 2688 faces have effective reach 10 (own-block readers excluded, sign-consistent) and none exceeds 10; all span 4 blocks. Their 2688 forms span Q^112, and 56 random faces have rank 56 beyond the 8 centres. A greedy pair-sharing supply of 56 random faces needs 103 to 112 distinct pair registers (seeded; recorded 105 to 112); a clustered choice of 56 faces needs 30 but is not available for a real cover.
- RECORDED (`evidence/O1/`, quads with fewer than 4 blocks and raw reach): raw reach at least 10 gives 24192 faces, all spanning 4 blocks; the legal block partition is unique (14 extended-Hamming octads for the 8-frame deleted); a best unconstrained partition leaves 20681 of 24192 faces spanning 3 or more blocks; overlapping cells confine at most 32 percent at the extra-copy budget.
- RECORDED ledger (J21-K model, hypothetical design, no shipped word): charge 12.21 percent b = S-type 4.2 + totals/cut timing 8.01 (56 totals x 0.143; arithmetic checked, rates booked); best-case net below 0; the 0.143 rate is about 1 times the merged w9 rate of row P3 (0.140) and 2 times its no-merge rate (0.070); it is 3 times only O2's 0.043.
- Depends on: #531, #626.

### O2. #617 to #622 K-triangle ledger  (RECORDED)
Priced with the package's moment engine (b617 reproduced): ideal gross +0.52 percent b for 12 helpers (0.043 percent each), climbs of 48 rewired reads -0.2, 6 lost second cold ends -0.19, net +0.0146 percent; atom-family ceiling about +0.4 percent; per incidence a triangle trades 3 helpers for 3 cold ends. Consistent with #646's own measurement. Not re-run (`evidence/O2/B2-NOTES.md`). Depends on: #617, #622, #646.

## Open problems

1. **Mixed-β decoders with n ≥ 9** (D1): a cst below 64 on P112 would have to mix terms with β ≤ 7; no proof and no counterexample.
2. **An order-free fragmentation ceiling** (F1, F2): the order-free loose bound (2478 psi/call) is uncalibrated; no skeleton-free bound exists.
3. **Non-projection rational labels** (S2): the sink charge ≥ 1 is not proved for them.
4. **A frame schedule with |I| > 8 per block** (G1, G2): more cold ends need a larger |I|, i.e. a different schedule.
5. **Value-exact re-threading beyond the fixed order and DAG** (F2): a frames-only deletion price is not value-exact; every deletion must be replayed on values first.

## Appendix: Conditional candidates (unverified: could work IF…)

None of these is a result. Each item has a measured fact behind it and exactly one blocking condition. If the condition holds, the gain follows from numbers already measured. Every number is from an exact replay of #656 unless noted otherwise. Prices use the settled helper rate of row P3 (+0.070% b per width-9 helper removed, or +0.140% if its width is merged; the earlier 0.0725 / 0.141 is withdrawn). We are not pursuing these. Two earlier candidates (twin substitution, meet-frame reads) were tested and failed; they are rows F4 and F5.

1. **Drop the never-read S1 scratch (≈ +2% b, est.).**
   - Measured: in 9 of 14 blocks, 2–4 S1 scratch registers are never read after phase A. Dyadic A-programs with 12–14 scratch reproduce the end-of-A rows exactly.
   - This works IF there is such a program whose 8 lines end phase A at frame dim ≤ 2–3, their shipped frames. The current dyadic programs leave the lines at frame 4, which forces all 112 target end frames from 8 to 9.
   - Check: frames range over only 67 subspaces of a 4-dim label space per block, so a frame-bounded search per block (one value solve per frame schedule) settles it.
   - Update (post-submission, unverified here): mostly answered negatively. For the 11 eight-line S1 blocks, given the shipped end-of-A frames, a frame-constrained re-synthesis shows the block needs all 16 of its registers (a forced-matching argument). Still open: blocks (0,1,*), where lines can act as couriers, and the case where later readers' true caps replace the shipped end-of-A frames as the bounds.

2. **Single-packet S4 via coefficient reads (≤ 112 helpers, net ≤ +1.96% b).**
   - Measured: all 28 S4 four-cycles admit one-packet coefficient reads if the targets are still empty. Coefficient ADDs into targets are SPEC-legal. (Related: #683 prices a mixed K/M face bypass and finds four carriers are forced; a different object.)
   - This works IF the ~252 target adds can be deferred past M-ready while polluting only sources whose caps already contain the key frames. Deferring them all naively gives 619 illegal ops.
   - Check: choose deferrals per source, interleaved, and run the oracle.
   - Update (post-submission, unverified here): answered negatively. 18 of the 28 deferred S4 adds are illegal even when deferred alone, checked exactly on cycles 0–1. So this item is closed as stated.

3. **Order-free frame slack on #656 (reordering of commuting ops; up to a few % b, nominal bound ≈ 8% is an over-report).**
   - Measured: the order-free dimension relaxation allows 2478 psi/call against shipped fragmentation 20,337. At the fixed shipped order the exact legal gain is 0 (supported by #698 for the CK B phase and by row F1: 950 of 1096 target ops at ceiling and an all-at-U assignment costing +520, not gaining). The relaxation could not be calibrated (its fixed-order value is 568 psi where the exact one is 0). Random topological re-creations of three blocks' S3/S4 threading (19 runs) all landed on exactly the shipped cost, so the open part is the S1 / phase-A order.
   - This works IF the exact frame-level model over the word's 1041 frames (row F2: G(r,t) = join of start frames over time-respecting journeys, legal iff G ⊆ U) gives nonzero slack for some topological order.
   - Check: the exact per-op minimal-frame bound over the dependency DAG with earliest-possible-time order, compared with the fixed-order ceiling 0; report the first order-free increment in psi per block.

4. **Radix-4 / wide first climb for S1 scratch (≤ +3.4% b gross; net likely 0 to +1.5%).**
   - Measured: a register owed to k targets sits at dim ≤ 8 − ⌈log₂ k⌉ (row C3). A w1 → w2 climb is worth about 745 psi and w1 → w3 about 1180 psi gross, against a cap of about 980 psi (≈ +4.72% b). Unit pieces are 34.8% of D on #649. Break-even is about 47 extra width-9-equivalent births.
   - This works IF a radix-4 step for S1 scratch costs fewer births than it saves. On the face ladder, fused rungs lost sharing (+168 births, −12 to −24% b); S1 scratch is not shared across keys, so that loss may not apply.
   - Check: take one S1 block, replace one binary pair of unit climbs by a single w1 → w3 jump with the extra registers the geometry needs, price with the exact root on #649's profile, count births.

5. **Partner-merge of pure-dirt helpers into idle hosts, under op reordering (≈ +0.2 to +1.1% b, loose).**
   - Measured: of the 268 pure-dirt helpers (row C2), 216 pass semantic exactness under a host swap and 96 have a source idle for their whole life. A static parity census passes 495 of 1668 pairs (near chance: 417 expected), covering 71 of the 96 helpers. At the fixed order all 96 violate G ⊆ U.
   - This works IF some op order (the same reordering as item 3) makes the host swap frame-legal.
   - Check: run item 3's order-free G / U computation restricted to the 71 candidate pairs and count the legal ones exactly.

## Notes

- **Base:** this branch is cut from main (`66849e14`) and touches only `research/format-limits-2/`.
- **Inputs:** vendored inputs are pinned by PR blob id (and sha256) in `SOURCES.json`: byte copies from PRs #531, #555, #595, #622, #626, #635, #645, #646, #649 and #656, three spec files of main, and rebuilt words pinned by the hashes their PRs publish. Existing run logs and card records are shipped unchanged under `evidence/` (sha256-pinned), except that absolute local paths, a personal name or CRLF line endings were removed from six of them (listed in `SOURCES.json`, `scrubbed`). Requirements are pinned. No SAT, CP-SAT or DRAT artefact exists for these rows (two CP-SAT / CaDiCaL attempts on the D1 hole were killed without a result; no UNSAT claim is made); the one solver run (HiGHS MILP, F1) is re-run in `verify.sh`. No Lean was added.
- **Errata found in our own earlier claims:**
  - E1: #595's "schedule/ρ family" reading (census item 8, open problem 3; the A.7 table itself already says "rule dropped") is withdrawn.
  - S1: the earlier figure "4164 of 8960 off-diagonal entries legal, 35–52 illegal reads per row" came from a port-indexing mismatch (the #656 FULL-WORD content map read through the ck word's port mask) and is withdrawn; with its own ports that word also gives 5264 legal and exactly 33 illegal reads per row, as the ck word does.
  - Y1: "rank 8 at every cut" is false as stated; rank 7 occurs at the 8 coordinate splits.
  - Y2: "on all 56|56 splits" was run only on the 8 coordinate splits.
  - F1: the frame-level checks use the ck / jp8 provider words of #622 / #623, not #656's own layered word; "legal ceiling, net −5.6" is a model value of an illegal assignment and is indicative only.
  - P3: an earlier random-draw rate table (0.0725 / 0.141 for w9) is replaced by exact means (0.070 / 0.140).
  - G3: the "14 at d ≤ 5" cap of an earlier fixed-content premix analysis is superseded by G1 and must not be quoted.
  - C1/C2: allocation classes are 3 (4 `alloc()` sites); the 268 pure-dirt helpers are now shown equal, as a set, to the S3 + S4 sites.
- **Not reproduced here (RECORDED only):** word-level knob tables (P2), the Y2 frame-illegality gate (needs a rebuilt prototype file), the 9-minute tagged rebuild of the #656 word (C1), the S1 scratch notes of F3, and the oracle runs of F4 / F5.
- **Overlap check:** #698 (thakrarsagar) certifies fixed-order, fixed-end-frame optimality of the selected CK supplier's B-phase frames; P5 (frame annealing), F1 and F2 cite it and keep only what is distinct (target end-frame cascade, word-level rigidity under +1 dimension, the #664 miner F6, insulators F4). #697 is a RAM-model construction and does not overlap. #683 (partial K/M face bypass needs four carriers) and #687 (a K-triangle single-read relocation neighbourhood) study different objects from every row here (O2 is a pricing ledger of #617 → #622; appendix item 2 is only related to #683); they are credited in `NOTICE.md` and no row was dropped. #620 and #631 are cited in D1 and D3, #661 and #665 where related (F1, F2). Newer PRs checked for overlap, none duplicates a row: #703 (Mister-Meeseeks; asymmetric Hurwitz E8 copy cost exactly 10) is a scoped negative on #620's quaternionic copy geometry, related to D1/D3 (decoder floors) but a different object; #705 (littleBro; determinant obstruction for rank-homogeneous register paths) is related to S2 and F2 (what the format forces on register paths), proved by a different argument; #711 (thakrarsagar; R420 adjacent A swaps force both frames) is on the bit side and an order change in phase A, related to F2's "time shifts" and to #661.

## Files

- `s1-2-erratum-invoice/`, `s3-4-census-gauges/`, `s5-6-decoders-spec/`, `s7-9-centre-fragmentation/`: per section group: `checks/` (one script per claim group), `inputs/` (vendored files), `evidence/` (existing logs and notes), `verify.part.sh`. Commands in the sections run from the group directory.
- `scripts/provenance.py`: step 0 (`--write-manifest` regenerates the manifest).
- `SOURCES.json`: pins of every vendored input and evidence file. `MANIFEST.sha256`: every file of the package. `requirements.txt`, `LICENSE`, `NOTICE.md`.

## Credits

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0. See `NOTICE.md` for the PRs whose words, pipelines and results are used.

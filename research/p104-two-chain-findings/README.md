# Two-chain family: remaining proofs, objects, backup words and open leads (no new kappa)

No new kappa is claimed and nothing here is pushed as a supplier. **No human has reviewed any item.** Status words: **proved** (by hand, one author unless "twice read"), **replayed** (exact finite computation, or an exact run on the stated word), **model** (formula, floats, frames-only bound), **conditional** (rests on stated quoted statements). `check.py` recomputes the data facts in `data/` (hashes, word kappas from invoices, the E-free root, the two L=3 roots), each with a failing control. 1 R0 is about +.0043% kappa. Credit: Romman (#5599), CubeJerry (#6912, #6914, #6916, caller blocks and the odd-share line), unpaidmoon (#6930), icekylinx (#104, odd scalars at caller level); Bukh-Cox, Blasiak and Haemers for the clique/orthogonality background behind the w bound. Lakatos' method of proofs and refutations is the framing behind keeping each statement with its counterexample.

## 1. Proofs

1. **Rounded-division theorem** (conditional, twice read in v1, v2 read by its author only). With no checks and no odd root scale, the output is within an explicit defect of the exact action on any child meeting a norm contract, nonlinear ones included, and through the recursion it fits #6901's guards. Conditions: five quoted statements S1 to S5; raw fails on the old caller and fits only with #6912's rewrite. Test: an exact replay found 0 rows over the bound, adversarial case .9999, controls fail. Not run: caller, true Clifford gates, width 2. It changes the premise, so using it is a second framework change. Settles it: a reader of v2 and the caller run.
2. **Induced-matching share law** (replayed). Two same-arrow lines on one 4-rest register: F+F or R+R with the same chords leaks; **2F+2R** is exact (T[Y,X]=diag(-1,1), inverse block diag(-1,1), helper restored). "N_ij is nonzero iff chord c_i crosses w_j" holds on 2520 of 2520 orders of the 8-event case; 80 of 2520 orders are clean. Exact counterexample to a same-arrow share: F+F same chords gives T[Y,X]=[[1,1],[1,1]].
3. **Lemma G** (proved, one author; resonance replayed in floats on one word). A t=-1 native means exactly T[Y,K]=0 raw with T[Y,X]=cI; at any other t that block has rank 104 by force. Settles: an exact word at t=-1.
4. **Level-mix theorem** (proved, one author): the exponent of a mixed-level word is the maximum over its words. Source report: no separate check here.
5. **Generalised split lemma with break-even leak** (proved for the stated scope, one author). A split pays while its leak stays under the break-even; the up-set count cannot see a split, so no cut floor limits splitting. Settles: a floor holding 94% of the bill (best count about 960 of 13,119 R0, not proved).
6. **Waist identity** (twice read; replayed on 975 columns): ab - cd = -g k. Lemma W (cd=1 and ab a unit suffice; #5599's ab=cd=1 is sufficient, not necessary) and Lemma S (a zero-mass owned scratch makes ab any unit) are toy-only, one author. On the current words cd = 0 in all 180 pairing jobs.
7. **Pairing as a sum of squares on shared inputs** (pattern, replayed at one prime, 17 of 17 against a 4-of-158 control; not derived). A description only: as a predictor it predicts nothing useful. Gaussian scalars add nothing (proved, one author): the pairing rank over Z[i,1/2] equals that over Z[1/2] for rational pools, and 5 = 1 + 4 stays 5.
8. **Rectangle law, Theorem S, H, H', root cut, Theorem C**: in the companion note (research/p104-root-cut-laws), twice read and replayed.

## 2. Objects (all exact, in `data/`, rechecked by `check.py`)

- **L=3, rho=1 roots tHHtHt and tHtHHt** (`root_L3_*.json`, rows a, b of length 8, M=9, n=8): header Gram is the exact path at t=-1, units square-zero; idle pieces are idempotents, the stage idempotents commute, ranks [4,4,4], masks cross (not laminar). The commuting/idempotent identities were replayed by a sympy script, the header lines are in `check.py`. Status: replayed, one reader. Not priced as a gain: toll n/2-2 idle per stage; ceiling +5.36% with free hosts (+4.02% against #6932, the +4.15% figure was against another base), -4.36% with demoted hosts; model. Open: connected L=18 embedding.
- **Two-chain roots, h=4/6/8, S=1416+48h**: quoted from the family's root note, not re-derived here (conditional). The h=18 root is `root_h.json`.
- **E-free root** (`root_A_efree.json`, `caller_efree.json`): 19 fields per chain, 20 units per chain, n=38, N=40. Exact: unit product is -I at S=-1 and I at S=+1; symbolic M(D) = -diag(prod D^eps) with 18 variables, every field in a mask. One declared deviation: isotropy y.x=0 fails at the single thin unit t1 of each chain (units 18, 19; `check.py` asserts exactly that). The caller needs one new op, QSELF (R[x] *= q^k), a one-register in-place Q^-1 job; with it kappa and S are unchanged and the E-credit premise disappears. If QSELF is refused, a QUERY-only form exists in principle at about -6.36% (gadget replayed, whole caller not built). Status: replayed exact, caller 76x76 equals diag(Q^-1 prod D^eps) on four central characters, 12 caller controls and 6 root controls rejected; legality of QSELF is a maintainer question. Backup to the E credit.
- **Toy words** of a Whitehead-dump search and **stage-level conjugators** of an unpadding search: reports exist (model/toy); the first exact legal Whitehead word with k_up < v is not found (a hand sketch stalled at v=3).

## 3. Backup words (data; none has been reviewed by a human)

| word | kappa | status |
|---|---|---|
| `data/wh.json.gz` | .0036275819188 | first, a candidate for anyone to chain and ship. The two-extra-splits-free main-wire word plus 16 shared wires on helper contacts; exact replay at every step, S=1520, S certificate 1125, peak 40, endpoint 0 bad. **Chain not run, not independently reviewed.** +.0415% over its base (.0036260774601), +.1027% over #6934 |
| `data/ft.json.gz` | .00362710048 | exact replay (0 violations, endpoint 0 bad, S 1520), flags-only retarget of 38 components on the main-wire word, +.0023% over it. Chain not run |
| `data/sr0.json.gz` | .00360666479 | dyadic, reviewed by an independent replay: endpoint 0 bad, joint pass on both callers, 7 undetected ADD mutants shown equivalent |
| `data/rbf.json.gz` | .00362232643 | chain passed on two callers; peak 30; S=225; +.0350% over #6932; below #6934 |

kappa of `sr0` and `rbf` is recomputed from their invoices (`data/*.invoice.json`) by `check.py`; `wh` and `ft` need the full replay, only their hashes are checked.

## 4. Open leads (odds are judgement)

| lead | size | odds | smallest exact test |
|---|---|---|---|
| Pads below about 8 R0 | small | 5% | price one pad family exactly |
| Unpadding with stage-level conjugators | +.054 to +.095% model | 5% | three-role caller tooling, then one exact word |
| Pairing with c.d=0 as the largest block | ceiling 873 R0 | 3% | one exact word with a c.d=0 pool |
| Comb wires on helper contacts | up to 243.6 R0 frames-only; 1806 chord-clean pairs before dedupe | 10% for 5+ R0 | build the two-line comb, replay |
| Merge of X69 with helpers 444/589 | +1.386 R0 | 40% as a small gain | apply and replay; check it composes with the wires |
| Do the 16 wires compose with the two extra splits; flip 695 (+11.73 R0 model) | unknown | under 10% | build both, exact replay |
| Share maximisation: 466 donor/host pairs | frames-only ceiling 4948 R0; only 3 pairs (18.5 R0) schedulable as is, not leak-tested | 5% | mod-p leak test of the 466 pairs with retiming and in-rest reorder. Census: 1061 helpers, 568 carry F, 569 R, 224 share at one hop |
| TWINRELAY | up to 17.5 R0 | 5% | not re-tested on the current word |
| Flags | dims-only MILP +38.9 R0 is a relaxation; with real pinned subspaces the exact optimum is +0.523 R0 (realised in `ft`) | closed at 0.52 on that word | none |
| t=-1 native below UP about 93 | break-even in the model | 1% | exact word with T[Y,K]=0 |
| w<9 at k=6 (rank 53) | open | under 2% | exact orthogonal-set argument |
| Second-order deformation of c.d=0 pools | derived, test not run | 1% | second-order obstruction at a singular point |
| Multi-carrier and causal-order ties | unpriced | under 2% | exact tie replay |
| Hosted-network F | bounded at 1.42 to 1.48, not built | under 2% | build the network |
| Radix-3 window C in {63,64} | needs ternary frames | under 2% | ternary frame replay |
| Flip with shear on s=3 helpers; typed-job columns | unpriced | under 2% | one exact column |
| From-scratch two-chain word | F was built and scored for one chain only; no from-scratch word has had its two-chain Share measured. Tie needs 2,221 R0, kill under 1,600 | 3 to 8% | exact Share on the g2best generator word. The 104-port count is inherited, S margin 1%, never re-priced with shares |

## 5. What is finished on this schedule

Harvest supply reads 0 chronologically (Through Law, supply form; sound in total on the three words tested, fails per frame on causal cuts) and 0 causal witnesses (sampled, with a planted control that finds the two known splits at 30 samples; not a floor). Scope: the dyadic and odd words of this schedule, not other schedules or new object classes.

## Not claimed

No kappa, no supplier, no review by a human. Every one-author proof above has had no second reader.

## Exact checks

`python3.12 -I -B research/p104-two-chain-findings/check.py` (about 30 seconds, standard library) or `verify.sh`; it ends with `PASS_P104_TWO_CHAIN_FINDINGS` and fails on a failing control.

## Open next questions

1. Which open lead in section 4 settles first? Each row names its smallest exact test.
2. Can `wh` be chained (native maps, joint caller, outer, mutants) and shipped?
3. Does the two-chain Share of a from-scratch word reach 2,221 R0?

The structured form is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Full texts and data

`ROUNDED-DIVISION.md` is the full statement and proof of the rounded-division theorem, with its conditions. `data/roots/` holds the exact root data for the L=3 rho=1 roots and the two-chain h=4/6/8 roots. `data/toys/` holds the exact k_up<v toy words.

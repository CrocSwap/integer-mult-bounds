# Deferred readouts on both networks of the stopped product-ring interchange

## 1. Claim

Under every hypothesis that PR #104 retains, the stopped product-ring interchange with

- the bit network replaced by Swapnil Jain's round-seven deferred word (h = 23), and
- PR #104's own complex network (h = 24) given lifted binary frames and deferred readouts,

gives the conditional bound T(n) = O(n (log n)^(1-κ)) with

κ = 429239/5000000000 = 8.58478 × 10^-5,

which is +10.1% over PR #104 (7.79476 × 10^-5). The next κ grid point at denominator 10^10 is rejected.
This is a finite conditional certificate only.

| | PR #104 | here |
|---|---|---|
| bit network | positive-label producer, R = 38,776 | Swapnil round seven, R = 28,866, 11,565 deferred slots |
| coarse bit saving | 4019/50000000 = 8.038e-5 | 620523/5000000000 = 1.241046e-4 |
| stopped bit saving | 8.034e-5 | 1.240190e-4 |
| complex network | aligned rational centres, R = 44,918 | same DAG and roles, lifted frames, 8,893 deferred roles |
| complex saving | 1949/25000000 = 7.796e-5 | 214657/2500000000 = 8.58628e-5 |
| κ | 7.79476e-5 | 8.58478e-5 |

## 2. What changes

Nothing in PR #104's interface changes: opposite-bank factorization, stopped atom recursion, ordinary
wrapper, rational centres, common odd grid, product rows and the balanced assembly are used as they are.
Two finite inputs change.

**Bit network.** Swapnil Jain's round-seven witness (commit 741e7aa078392553815df7926ee17ac5e25a8c38, files pinned by SHA-256 in
`bit_round7.py`): PR #62's producer, lifted frames, late copies, deferred readouts and V leaves. Swapnil's own
checkers verify the word and every frame exactly, and PR #97 replays its forward and reflected ledgers. We do not
change it. Under PR #104's rule every residual of rank r is one child of width r, so the slot chains, the gauged
exteriors (width m - (h - dim σ_u)), the copied-centre transforms, the target and data-wire chains, the data
residuals and the endpoint copies give the child list in `bit-profile.json` (rank mass 57,403,754,177, the
value PR #97 reports).

**Complex network.** PR #104's DAG (`scripts/stopped_product/complex.py`, unchanged) and its role count
R = c + q - |M| = 45,764 + 8,120 - 8,966 = 44,918. New:

1. *Matching.* A maximum carrier matching under the inherited matcher's adjacency (order by rank and node, the
   inherited label-inclusion rules), size 8,966.
2. *Roles.* An explicit compile: one role per free leaf use, the pivot continues each addition, copies serve the
   other free uses, a linked operand stays on the non-pivot and continues to its linked use.
3. *Lifted frames.* For an addition n, U_n is the common kernel over F2 of the functionals of every root reachable
   along slot successors (t_S for an output read into y_S, e_i for the retained centre A_i, whose frame is
   span{e_j : j ≠ i}). Every label lies in its kernel (outputs have even intersection with their target; A_i
   avoids i). The lift is used where U_n is nondegenerate and kept monotone along successors; elsewhere the
   inherited label stays. 20,234 additions are lifted.
4. *Deferred readouts* (Swapnil's design B on the complex word). Phase one is the closure of the 24 centre
   completions under per-role precedence. A role untouched by phase one, whose garbage does not reach a centre
   (a centre scatters to every target), reads its garbage out at
   σ_u ⊆ F0(u) ∩ ⋂ t_S^⊥ over its reached targets, nondegenerate. An insertion rule (largest first) shrinks each
   new frame only as far as nesting on its targets requires. Readouts run in increasing (dim σ_u, role).

The stage-one word is: readouts of the non-deferred roles at frame 0, early V gates, phase one, centre copies
read into their targets, deferred readouts in order, deferred V gates, the rest of L, output reads, L^-1, V^-1.
The readout coefficients come from the transpose sweep of L applied to the root reads (output reads ±1/2, centre
scatter 1/21 - [i ∈ S]/2); their only odd denominator is PR #104's 21.

## 3. What is checked (`complex_deferred.py`)

- **A.** Matching size 8,966 and R = 44,918.
- **B.** With zero scratch the compiled word computes every one of the 8,120 root values.
- **C.** The deferred word, replayed over Z/(2^61 - 1) with arbitrary scratch and data (two seeds), restores every
  role and adds exactly x_S to every target.
- **D.** Exactly over F2: every role chain (start σ_u or 0, start frame, every gate, linked continuations, root
  frame, F) is nested; every lifted and deferral frame is nondegenerate; every σ_u lies in its start frame and in
  t_S^⊥ for each reached target; on every target the deferral frames are nested in readout order.
- **E.** The one-child histogram from the explicit role chains has total rank W m - N + L = 109,450,358,336,
  every child is below m = 576 (the largest is 574).

`certificate.py` recomputes both moments exactly with PR #104's routines, the stopped bit saving
(1 - 1/1000)·coarse + (1/1000)·384599/10^10, the finite bridge and the 47-constraint assembly.

## 4. Endpoints, stage two and the bridge

- *Endpoints.* A deferred auxiliary role starts at the gauge of σ_u and ends at the complementary gauge, so its
  endpoint action is the identity shear on arbitrary inputs: the bit identity D_{I-P} D_P = D_I and its phase
  analogue, the translated source C_{D_0} with sink C_I C_{D_0} of `notes/copied-centers-complex.tex` and
  `notes/endpoint-gauge-complex.tex` (PR21/PR24). Its exterior residual has rank m - h + dim σ_u.
- *Stage two.* As in Swapnil's round seven and PR #104's two-stage counts, stage two is the complement time
  reversal of stage one with the same edge multiset. PR #97 replays the reflected ledger for the bit word; for the
  complex deferred word this is stated here, not machine-checked.
- *Bridge.* The larger children (bit 528 of 529, complex 574 of 576) raise the halving degrees to 367 and 200,
  so the product-row stock becomes p^33000 (PR #104 used p^4000; PR29 p^47000). As in PR #104, the stock enters
  only the row-product slack and the eventual cutoffs, not κ. The semantic induction 2B(m - r) ≥ s + E holds.

## 5. Scope

All of PR #104's inherited hypotheses remain: the opposite-bank factorization for every residual class in the
finite lists (including the new gauged exteriors, deferral starts and target levels on both networks, and the
binary one-child normal form on the complex side), atom streaming and the ordinary wrapper, the common exact grid,
routing, recovery, the fixed-tape transfer and the analytic interfaces. The stage-two statement above is the one
new written assumption for the complex network. No global optimality is claimed.

## 6. Credits

- **icekylinx**: PR #104's stopped product-ring interchange, opposite-bank factorization, rational centres and the
  h = 24 complex producer used unchanged; PR #10/#18/#24/#32/#36 lineage.
- **Swapnil Jain**: deferred readouts (design B), V leaves, lifted frames, late copies and the round-seven bit
  witness used unchanged (https://github.com/Swapnil-jain/integer-mult-kappa, commit
  741e7aa078392553815df7926ee17ac5e25a8c38).
- **Zhihao Chen (jacklightChen)**: PR #97's integration of the deferred bit word and its reflected ledgers;
  PR21/PR29 translated gauges and two-stage accounting.
- **Aurel Prosz (Paureel)**: the two-stage topology and paid endpoint correction.
- All earlier authors credited in PR #104's NOTICE and SOURCES.json, including Avi Eisenberg/ikeboy (PR #53, #62,
  whose producer is the round-seven bit DAG), RaD/hipotures, Rohan Arun, eumemic, Dominik Scholz, Chafik
  Boukhalfa, James Chang and Douglas Colkitt.

The complex deferral construction, its checks and this certificate were prepared by Avi Eisenberg (ikeboy) with
Anthropic Claude assistance.

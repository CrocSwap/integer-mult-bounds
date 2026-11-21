# LEANBOWTIE (Sonnet, Nov 20). Two files in lean/decoder-duality/Nov15/, both KERNEL-CHECKED via runlean.sh (rc=0; FutureAttrT 11 s, NetBowtie 18 s, ~2.1 GB). Axioms of every headline: [propext, Classical.choice, Quot.sound]. No sorry/native_decide. oleans in .lake/build/lib/lean/Nov15/.

## 1. FutureAttrT.lean (imports Nov15.FutureAttr): TRANSPOSE for the R side
- Op list model (chart moves record old and new chart); `rev` = reversed order, ADD d+=l e -> e+=l d, chart C -> C^perp (old/new swapped), INIT -> INIT.
- `Runs` (legal runs, ADD needs d != e and chart d <= chart e, publics ascend, owned cost). `Runs.transpose`: adjoint of a legal run is a legal run with the SAME cost (dim D^perp - dim C^perp = dim D - dim C), same P, start charts = (final charts)^perp.
- `effect_rev`: effect (rev ops) = (effect ops)^T (elementary matrices; the INIT projection is symmetric).
- `ARunL` = FutureAttr.ARun indexed by its op list (`toARun`, `cost_eq`, value law `val : v = effect * v0`).
- `ClassP` := rev ops is an ARunL (GTD + cold intake) of the swapped problem (targets Yr, symbols swapped, start charts (final)^perp).
- `decoder_of_classP`, `mass_le_R_P` (R >= mass of the forward receipts), `R_ge_of_wall_P` (Wall N explicit hypothesis). Uses attribution_decoder on the adjoint + price_swap/isDec_swap (Gram transpose).
- Non-vacuity `ToyP`: the one-port toy of FutureAttr.Toy read forward (O+=Y, ascend, X+=-O) with its adjoint a class-F run; `toy_classP_headline`: mass <= 1, receipt -1, adjoint ARunL built.
### Gaps vs UP.md sec 4
1. CLASS P IS A DEFINITION (adjoint is class F), as in UP.md; nothing says which forward runs satisfy it. The "dual-cold outputs" condition is not translated to forward data: the adjoint's final-data hypotheses hfx/hfy/hfyX/hbal (about s') are explicit premises.
2. Identity start required for the pattern identification: hidx/hidy (public r holds exactly its port symbol), owned start 0, X-registers != Y-registers. FA itself allows arbitrary even-supported start; the transposed statement needs the symmetric start.
3. Mid-run INIT maps to INIT (projection 1-E_rr is symmetric). UP.md's "INIT <-> CLEAR" is only the endpoint statement (owned start 0 <-> discard at the end = the PP-block of the effect matrix); there is no CLEAR op.
4. Intake/output swap under reversal is what turns class F into class P; GTD of the adjoint = "no output before an intake" of the forward lifetime. Not proved as a forward-side criterion.
5. ADD needs d != e (as in LEANUPHASE gap 1) and the legality hypotheses are on the PRE-state charts (ch' d <= ch' e).

## 2. NetBowtie.lean (imports Nov15.FutureAttr): BOWTIE theorem for networks over any field K
- Conventions as NetNG (hba, strict DAG lt, hF, hG, hHlt, hH, N=1+HN and 1+NH) with K in place of Z/4 and no c; bowtie data in the structure BNet: comp/role/hub, relay edges inn->inn, inn->hub, hub->out, out->out inside a component, gathers not at out, deposits not at inn, every inn node has a relay out-edge, every out node a relay in-edge.
- `Fact`: N k j = N k h * N h j (k not inn, j not out, h = hub of comp j) [P]. `M_eq`: G N F = sum_comp (G N)[:,h] (N F)[h,:] on EVERY cell (exact, any scalars).
- `in_tree_aux`/`out_tree_aux`: dim sum_{in} a <= dim b_h + sum d ; dim b_h <= dim meet_{out} b + sum_{out != h} d (peel an lt-minimal / lt-maximal node; b_j <= a_parent).
- `comp_price`: price(row_c) <= total drop of component c (pair_price with (M,N)=(I^perp, V)).
- `bowtie_decoder`: decoder of M∘Q (IsDec) with sum price <= D; `bowtie_D_ge_mass`; `bowtie_D_ge_of_wall` (Wall as hypothesis, e.g. 56 at Q96).
- Non-vacuity `Toy`: 3-node bowtie over Q (in -> hub -> out, relay scalars 2,1, h=1), D=1, M=2, mass <= 1 = D.
### Gaps vs NA.md
1. TIGHT-CHAIN CONTRACTION (NA sec 2c) NOT formalised: the theorem is for networks that already ARE bowties (gathers/deposits only on the in/out side). Contraction needs odd-cell (not exact) factorisation and a network surgery lemma; this is the main open piece. [Statement for the next lane: contracted node a=a_{k1}, b=b_{ks}, drop = sum d (telescopes since a_{i+1}=b_i), M preserved on odd cells.]
2. SHARPENING: arborescence (unique parent) is NOT needed. The proof peels nodes along lt using only "every inn node has SOME relay out-edge, every out node SOME relay in-edge"; the price bound sums d over distinct nodes. So in-DAG into a hub / out-DAG from a hub is covered (NA states trees).
3. M_eq is exact on all cells; only the price/decoder statement uses odd cells (IsDec). hN2 and the Z/4 / Z_(2) -> K reduction are not used here (K is the scalar field of the network, e.g. Q).
4. Wall is a hypothesis; the 56 corollary needs Wall56@Q96 (not in Lean).
5. Counterexample NA sec 3 (two relays between depositing and gathering nodes, D=2, mass 3) violates hshape (a node that gathers and deposits must be the hub; two hubs cannot be relayed), consistent with the theorem; not formalised as a teeth test.

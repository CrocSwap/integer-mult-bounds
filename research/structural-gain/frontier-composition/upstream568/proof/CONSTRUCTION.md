# Actual words and whole-call composition

## Seven multi-cut cold kernels (this package)

Each provider word first receives PR564's single-cut kernel for helper 270 (below). `code/build_multicut_kernels.py` then inserts seven more kernels from the frozen recipes `data/{ZERO,FOUR,EIGHT}-MULTICOLD.json`. A kernel for pivot p at entrance frame E is a list of gates `d += -q*p @E`, each at its own position (part, index). All gates precede p's first original touch, and p carries only its initial dirt there. The gates therefore cancel p's complete dirty response if and only if `sum_g q_g * col_{cut_g}[d_g] = col[p]` over the actual suffix columns. The constructor checks this by an exact forward replay of every output row. It also requires dyadic q, donors that are not data registers, pivots or centres, legal frame chains under gk_word.profile, the pinned profile delta and the pinned output content hash.

Pivots 506@[24], 518@[30] and 530@[30] use helper donors, one of which is a B-first helper split at its first frame; each has delta `{1:+1,2:+2,3:-2}`. Pivots 495@[24], 507@[24], 519@[30] and 531@[30] use two output-target donors and one B-first partner, all in part B; each has delta `{1:+3,2:+1,3:-2}`. All seven pivots enter at rank one, so eight helpers per word have residual width eight. `code/audit_multicold_controls.py` locates every new gate by exact content and rejects all 32 omission mutants (each gate, each whole kernel) in both exact orientations, with cleanup regenerated and correct compensation frozen. The changed words then pass the unchanged native, phase, wrapper, controller, invoice and assembly admissions.

## PR564 single-cut kernel (inherited)

For each zero/four/eight provider, helper 270 is register 494 and is untouched before B index 368. The frozen constructor independently reconstructs the actual suffix responses and checks

    q494 = q566 - 2q640 + 2q642 - q688 + q690.

Five opposite donor updates on frame [24] kill that future dirty response; cleanup is rebuilt from the actual changed word. The entry frame has rank one and the helper's residual width becomes eight. The changed scalar word, compensation, inverse transpose and both frame ledgers are then verified natively; the construction relation alone is not admission.

In PR564, with p=0,4,8 promoted pivots, the local paid profile was `e1*(2301+2p)+e2*(442-2p)+e3*(470-p)+e4*(184+p)+56e5+56e6+8e8` with width inventory `{4:p,5:56-p,8:157,9:291}`. With the seven multi-cut kernels it is `e1*(2316+2p)+e2*(452-2p)+e3*(456-p)+e4*(184+p)+56e5+56e6+8e8`, width inventory `{4:p,5:56-p,8:164,9:284}`, 220 nonzero entrance helpers and entrance rank 388+p. The exact call dispatch retains 15/2/55 counts, but every selected provider now includes the cold kernel.

The complete literal owner map is frozen in data/OWNERS.json.gz; the audit derives physical windows through all individual bridges, same-call family uniqueness, residual offsets, spectator axes, orthogonal charts and remaining idle children. Local sums plus the idle profile `{1:93,2:93,3:2118,7:1,48:1713}` of the new literal owner map yield the complete printed profile. No profile-only homogeneous substitution is used. The solver is a discovery tool, not an admission dependency.

All source and all wrapper/scalar/phase work remain charged. The fresh invoice sums the actual selected provider and orientation primitives, uses conservative shared compiler maxima, and retains the prior allowance as an overcharge. Reusing frozen arithmetic engines does not reuse the old invoice: the assembler independently reconstructs its stock/group/router/literal/precision/tape/row inequalities from fresh receipts.

Uniform fixed dispatch across the full orthogonal group preserves the PR559 native complex cover argument. Right translation by each checked orthogonal owner chart is a bijection, and every chosen scalar/phase program is exact on all columns. The native moment removes no real bit exception or finite work. Both the conservative complex moment and native exact-complex moment are certified, with unchanged PR543 bit fallback and inherited all-size/analytic assumptions.

Exploratory packing optimality receipts describe only the stated one-cold complete-group family and retained capacities. They are not global bounds over other words, cuts, kernels, owner inventories or controllers, and are not needed for the constructive record.

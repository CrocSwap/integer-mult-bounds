# Compose the P104 prefix and suffix scalar circuits

This package joins two disjoint circuits in the selected PR6030 word. The joined word has **19,107 events** and real scalar allowance **140,268**. Relative to the stronger prefix-only predecessor, it removes **119 events** and **2,510 allowance units**. Relative to the selected word, the total saving is 3,696 events and 49,160 units. The prefix supplies most of that gain; this package does not claim it as new work.

The new result is the complete joined word, its independent block check and its full precision qualification. Both source blocks preserve their linear operator on every entry, including the owned role. Native transports, COPY, INIT and CLEAR keep their exact order. The 770 public inputs, 29 owned roles, 31 lifetimes, peak 13 owned roles and every productive and paid rank remain unchanged.

Uniform 16 guard bits suffice under the retained causal relative-error model. The joined final error bound is below 0.829 B, compared with 0.913 B for the selected word. All ideal-plus-error prefixes stay below 1024 B. The receipt also compares each predecessor separately. Guard 15 fails this sufficient rule in all four words; that failure is not a physical precision lower bound. No native tariff, compiler cost or kappa gain follows from these local counts.

Run `python3.12 -B scripts/research_package.py --package research/p104-composed-scalar-blocks`. The verifier is read-only. To reproduce the source searches, run `python3.12 -B research/p104-composed-scalar-blocks/construct.py`. Only explicit `--write` updates artifacts. Exact source bytes, their main commit and input roles are in SOURCES.json. VERIFY.json includes every live source needed by the Git-free export.

The tests compare 618,514 block coefficients, check all complete endpoint rows, and check 638,401 entries by an independent dense transpose. They check both sides of the uniform guard bracket for the selected, prefix-only, suffix-only and joined words. Six faults must be rejected. The signed error engine uses exact integer coefficients and upward rounding on a 96-bit grid. See PROOF.md for its premises.

The selected result and its five framework assumptions stay unchanged. The task card's signed-moment gate is not met: this is a finite constructive side result, with the scope change recorded in TASK.json. No further scalar search is part of this claim. Human review and physical/native/compiler/outer admission remain separate.

## Open next questions

Bind the joined circuit to a real rounded backend. Price scalar implementation, conversion, range, source access and cleanup together. Keep the 16-bit sufficient guard and ten range bits unless a stronger error proof replaces them. A lower scalar allowance alone must not be used to raise kappa.

## Credit

CubeJerry supplied PR6116 and the prefix row synthesis. Nick Petalas supplied `p104-chart127-suffix` and stated the open composition boundary. DreamingOfClouds supplied the selected PR6030 word and retained rung work. David Arias, Cinna Davis, Gareth Davidson, Ali Romman and the full P104/native/compiler lineage retain their credit. The two source synthesizers are used unchanged. The causal signed-row method is from Ali Romman's `p104-gauge-error-covariance`. Elementary row operations are classical. Prepared by Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.

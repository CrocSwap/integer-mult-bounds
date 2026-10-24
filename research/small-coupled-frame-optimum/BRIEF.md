# Local result and stopping decision

**Fixed power price:** at C=15108879/5000000000, exact min-sum over #4994's18 small components/68 contacts reproduces source profile `{1:2201,2:412,3:510,4:127,5:40,8:8}` in both orientations. The1,271-variable component stays at source. Every mapped multiedge and fixed-neighbor unary is retained. Full reconstruction checks all 29,790 mapped containments and includes 8 owned H8 calls. There is no native paid improvement in this restricted domain.

The fixed-C run uses integer histograms, 119 rigorously signed rational comparisons, 24 terms and no refinement. Normal and isolated optimized semantic receipts agree. The measured first run took 2.58 seconds; the final normal replay took 2.84 seconds. No float selects a cost or assignment.

**Separate supporting cuts:** exact integer objectives have minima C1=3298 and C2=4395, equal to source. At C3 the minimum is 5075 versus source 5080, with histogram `{1:2223,2:421,3:490,4:132,5:40,8:8}` and unchanged rank mass 5327. Its difference 22H1+9H2−20H3+5H4 is positive at the fixed power price. The proposed all-concave certificate therefore fails, and the authorized extension stops at k3. No k4–8, Pareto frontier, large-component enumeration or physical expansion was run. Normal/optimized cut receipts agree semantically. Portable-publication preparation was stopped under root's condition.

**Source ABI:** input #4994 ef2810fe43829960789f783e44ee6484d0368f09 uses #4971's frame-carrying native-word representation, preserving the original source invoice 5327. Its frozen native word has SHA256 7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05, shared with the developed #4610 lineage. Source PROOF.md explicitly leaves new physical absolute phases and uniform implementations open. This abstract optimizer does not transfer a new frame schedule into the frozen #4610 literal compiler/caller, does not complete p16, and does not improve kappa. #5016's numerical FULL-domain MILP report is neighboring evidence rather than an exact global certificate; this result concerns only the declared 18 components and makes no global optimality claim.

**Controls:** original/least/greatest histograms match in both orientations, all domains contain source, and original factor sums equal traceback optima. The author dropped-edge label means only a histogram mismatch, not a mutated validator rejection; CONTROL-CLARIFICATION.md records that limitation. The separate independent reviewer owns stronger private-copy mutation checks. This packet awaits that review.

Reproduce from this worktree:

    python3 outputs/pr4994-small-frame-dp/optimize.py
    python3 -I -O outputs/pr4994-small-frame-dp/optimize.py --output outputs/pr4994-small-frame-dp/OPTIMIZED.json
    python3 outputs/pr4994-small-frame-dp/min_rank_cuts.py
    python3 -I -O outputs/pr4994-small-frame-dp/min_rank_cuts.py --output-dir outputs/pr4994-small-frame-dp/cuts-optimized

These commands use the authenticated project-level `outputs/mathematics-paper-research-20261023/frame-optimization` snapshot; `--source-root` can relocate it. The packet is a local result with that explicit external dependency, not a self-contained publication module.

Frozen hashes:

- Fixed-C manifest: `389138c4b5389d141090a9b66eba769ef0a70381b7803b248c90eef97399e72d`.
- Fixed-C optimizer: `b1536a86967312bb8c9da7b177dacd54093bea71462bbbfeffdf7325260d96bc`.
- Fixed-C result: `86fe5df320e11db12a0460f9af2d539bf659b14b7498668df3a907e26788ca87`.
- Cut extension manifest: `09844d8e7767cbc82dd576f7f74ac836fe3a0a9d0f73118171367fe8320ba4ee`.
- Cut driver: `d2fb2a56426cc94c9c9149316c93e83536a316f04bbc033603a715e3ae3e82d2`.
- Final cut summary: `c8d86ccc24d91bec4b0dd45b3df26d9e1b9fc1b19cf7d64f7f81914e811eb90a`.

Credit: 1337isnot1337 supplies #4994's interval/realization theorem, Dugongue supplies #4971's frame-carrying swaps, and Cao Yifan/native predecessors supply the retained word. Astra supplies the source-specific bounded proposal and Dechter theorem fit. This packet supplies the scoped exact implementation and receipts only.

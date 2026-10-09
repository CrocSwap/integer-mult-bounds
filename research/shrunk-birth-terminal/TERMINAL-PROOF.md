# Terminal elimination after shrunk frames and birth-slot reuse

This is a finite composition of PR125's shrunk frames, PR124's birth-slot reuse, and PR122's terminal-accumulator identity. The code and physical word are new composition artifacts. PR117's graph, the ordinary rational-center decoder and the inherited stopped-product, analytic, fixed-tape and all-size transfer remain assumptions. No new final kappa is asserted here; complete numerical assembly is a separate check.

## Selection and noninterference

A selected virtual role u is an ordinary terminal, has no outgoing auxiliary use, has exact old and terminal readout column alpha times one target with alpha=+/-1/2, is deferred and untouched during the retained-center phase, and receives every update after centers and all old readouts. This bounded pass excludes clean-input-start roles.

A role is also excluded if it is either endpoint of a selected birth reuse. In particular, deleting a terminal that occupies an earlier donor's physical slot would not remove that physical slot and would require a different cost argument. The current selection preserves every birth pair and all existing birth compensation reads. Since selected terminals never control a retained auxiliary update, all retained auxiliary values, donor liveness, recipient birth values and compensation-read times remain identical.

For each selected terminal, all old readout frames of its target are contained in its first incoming-update frame; its entire incoming frame chain is nested through the final target hyperplane. One role is selected per target, preventing two terminal rewrites from competing for the same target-front interval. The builder emits the old target advances even when their accompanying terminal read is deleted. Every new target subdivision is charged by the full chronological scan.

## Exact arbitrary-dirty identity

Write z_u for u's initial dirty value. Its contribution is

    -alpha*z_u + alpha*(z_u + sum_j a_j(t_j))
      = sum_j alpha*a_j(t_j).

Delete u, its initial and final reads, its destination updates and their inverse cleanup. At each original update index t_j, add alpha times the same source's current value directly to the target. No source is read early, late, or from an uncharged snapshot. Every retained auxiliary update and source injection keeps its exact original order. Cleanup is the exact reverse of the actual retained workspace and source events; direct target updates are not cleaned up. Targets never control workspace gates.

The complete emitted word is checked over Q using exact signed integer bit planes with common denominator 42. The audit propagates every target response backward through the actual aliased word and checks all source and physical dirty columns simultaneously. The forward source response is +I and every dirty response is zero. The reflected signed inverse, with the two data banks swapped and frames complemented, is checked independently for source response -I and zero dirty responses. Omitted redirects and changed redirect signs fail this exact all-column audit.

## Frames, complete profile and cost

Every redirect uses the source's original gate frame. Its target is promoted at that exact operation index. Full forward and reflected frame scans verify actual containment, nondegenerate endpoints, both data-bank paths, center-copy losses, auxiliary exteriors and final endpoint charges. An illegal redirect-frame mutation is rejected. The reflected event involution and the full paid histograms agree exactly.

Let h=24, m=h^2=576 and v=2024. For one selected role, sigma is its initial deferred dimension, M is the target's final old-readout dimension and F0 is its first incoming frame dimension. Eligibility establishes 0<=sigma<=M<=F0<=h-1. The exact complete cost comparison, after adding one dummy width-m child to the new side, is

    old: [m-h+sigma, 1, F0-sigma, h-1-M]
    new: [m, F0-M, 0, 0].

The masses coincide. The new packet strictly majorizes the old one; it therefore has smaller strictly concave power sum. The full profile emitted from the actual physical word equals the sum of these packets, with replication 2v. All 576 integer hinge functions are checked against the complete histogram, not only against isolated packets.

For all completed variants below, sigma=M=F0. After the paid target subdivisions, each elimination therefore removes 2v copies of widths [m-h+sigma, 1, h-1-sigma], with zero-width entries omitted. All counts stay nonnegative. Removing q unshared physical roles changes W by -2vq and recursive rank by -2vqm, preserving deficit 1,862,080. Largest child remains read from the complete histogram.

If the old power numerator is below W_old*m^p, padded concave dominance implies that the new numerator is below W_new*m^p. This establishes preservation and strict improvement of each previously feasible power moment. It does not assert unrestricted monotonicity of normalized moments at infeasible exponents, nor does it determine the final assembly bottleneck.

## Explicit scalar charge

Every direct update has numerator +/-21 over denominator 42 and is expanded literally into 21 same-frame shears of coefficient +/-1/42. This introduces no new role, source copy or frame incidence. The new bill keeps the entire inherited scalar bound without taking credit for any removed work, then adds 29 groups per direct update: the 21 actual shears and eight additional groups of conservative bookkeeping allowance. The allowance creates no additional physical operation or frame charge. The fixed odd-21 grid and maximum coefficient bound do not increase. The global bound is recomputed as 16*(2v*local+8v^2), with this larger local bill. This conservative bound is exported separately for numerical recertification.

## Reproduction and provenance

Run `compose_terminal.py --frames PATH/FRAMES.pkl --matches PATH/BIRTH_MATCHES.json.gz --readouts PATH/READOUTS.pkl --scalar-bill PATH/READOUT_COST.json --out NEW_DIRECTORY`. Inputs are copied and hashed before use. An optional `--terminal-roles PATH/TERMINAL_ROLES.json` supplies a bare JSON list of integer role IDs; the builder validates that it is a duplicate-free subset of eligible unshared roles with distinct targets and no birth alias before reconstructing the whole word. `terminal_inventory.py` accepts the same three witness paths and optional selection. Its separate `--include-birth-recipients` mode exposes virtual options with sigma=M=F0 for joint optimization; these options are explicitly not a legal simultaneous elimination selection until the real birth matching is adjusted and the default checks rerun. No upstream or root research directory is written.

Each output retains input copies, exact selected roles, full chronological word, full child profile, exact scalar bill, both frame/response audits, actual mutation results, 576 hinge values, source hashes and original operation-index bindings. The final joint runs contain immutable construction-source copies under `construction-sources`; their inventory runs use those copies and reject generator drift during execution. Both final emitted histograms also equal the independently predicted joint-optimization histograms. The original PR122 source archive is retained under `references/pr122`, pinned to b1a6f24e57141637b3ff040d6f2ce9d896ffb9bb.

Credit: SovereignSteak for PR122's terminal-elision identity and packet argument; Joel Pulikkan and Anthropic Claude assistance for PR125 shrunk frames; James Chang for PR124 birth reuse and corrected feasible-moment qualification; eumemic for PR117's replayed graph; Avi Eisenberg, Rohan Arun, Swapnil Jain and inherited contributors for compiler, deferral, rational-center and stopped-product ingredients. This disjoint composition, explicit word, conservative added scalar bill and both-orientation all-column audits were prepared with OpenAI Codex assistance. Original source notices are preserved with the references.

## Completed finite variants

| Variant | Birth pairs retained | Terminal roles removed | Physical R | W | Rank | Conservative G |
|---|---:|---:|---:|---:|---:|---:|
| cost-weighted | 2108 | 266 | 26331 | 114781040 | 66112016960 | 3115182247936 |
| original-greedy | 2108 | 253 | 26344 | 114833664 | 66142328384 | 3115140925952 |
| protected-prune | 2108 | 309 | 26288 | 114606976 | 66011756096 | 3115484649728 |
| protected-expansion | 2108 | 309 | 26288 | 114606976 | 66011756096 | 3115484649728 |
| weighted | 2108 | 309 | 26288 | 114606976 | 66011756096 | 3115484649728 |
| joint-base | 2108 | 381 | 26216 | 114315520 | 65843877440 | 3116113870848 |
| joint-expansion | 2108 | 381 | 26216 | 114315520 | 65843877440 | 3116113870848 |

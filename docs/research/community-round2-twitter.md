# Contributor-by-contributor announcement draft

Prepared for Douglas Colkitt. The reviewed checkpoint is published on main. Each numbered entry below is a draft post; the following source line is
an editorial reference, not part of the post. The order emphasizes the advances
that shaped the construction, then refinements, verification and parallel work.
It is not a priority or sole-authorship claim.

## Opening

We've reached κ ≈ 5.101692×10⁻⁵ in our conditional integer-multiplication result—23.7% above the previous GitHub release. The interesting story is how many people's ideas built on each other. A thread on the contributors who got us here:

Context for the thread: this is the exponent saving in O(n(log n)^(1−κ)),
conditional on OpenAI #109 and the retained transfer framework. It is not a
measured runtime improvement. The selected value remains below 2⁻¹⁴.

## Draft posts

1. **icekylinx** developed recursive batching, partial swaps and copied retained centers. These changed the network and its accounting, including the construction that crossed 2⁻¹⁵. They're central ingredients in the network we're improving today.

   Sources: [#10](https://github.com/CrocSwap/integer-mult-bounds/pull/10), [#18](https://github.com/CrocSwap/integer-mult-bounds/pull/18), [#24](https://github.com/CrocSwap/integer-mult-bounds/pull/24), [#32](https://github.com/CrocSwap/integer-mult-bounds/pull/32), [#36](https://github.com/CrocSwap/integer-mult-bounds/pull/36). X handle/post not located. Credit the copied-center crossing jointly with the geometry and transfer dependencies, rather than assigning the whole jump to one author.

2. **Rohan Arun** turned new ideas into stronger, checked compositions: better dimensions, data-corner geometry, fixed bases, weighted matching and wire reuse. His PR #39 anchored our audited 2⁻¹⁵ release, and his later refinements kept advancing it.

   Sources: [#31](https://github.com/CrocSwap/integer-mult-bounds/pull/31), [#39](https://github.com/CrocSwap/integer-mult-bounds/pull/39), [#44](https://github.com/CrocSwap/integer-mult-bounds/pull/44), [#49](https://github.com/CrocSwap/integer-mult-bounds/pull/49), [#56](https://github.com/CrocSwap/integer-mult-bounds/pull/56), and the full contributor ledger. **Suggested quote:** [@RohanArun's PR #47 announcement](https://x.com/RohanArun/status/2108212419139190842), reporting κ=4.105106623×10⁻⁵. This is the largest directly inspected, PR-linked witness in the supplied announcement set; it does not announce today's #62 result. Earlier [#44](https://x.com/RohanArun/status/2108207365199663189), [#42](https://x.com/RohanArun/status/2108195039851520173) and [the PR #40 geometry explanation](https://x.com/RohanArun/status/2108188579616710691) provide useful context. GitHub links @Viewforge; these announcements are posted by @RohanArun.

3. **eumemic** contributed complex-network compression, faster Gaussian resampling and auxiliary source frames. More recently, their joint frame compiler found cheaper ways to combine operations and reuse wires. That compiler is part of the current frontier.

   Sources: [#3](https://github.com/CrocSwap/integer-mult-bounds/pull/3), [#5](https://github.com/CrocSwap/integer-mult-bounds/pull/5), [#13](https://github.com/CrocSwap/integer-mult-bounds/pull/13), [#15](https://github.com/CrocSwap/integer-mult-bounds/pull/15), [#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57). The supplied survey associates @dysmemic with eumemic, but that identity link remains unresolved. We verified [@dysmemic's 2⁻³¹ claim](https://x.com/dysmemic/status/2108022138359988660) and [their post sharing the 2⁻²³ PR #10](https://x.com/dysmemic/status/2108116481611547037). The latter does not claim authorship and PR #10 belongs to icekylinx. Keep eumemic untagged until the account association is established; preserve the posts as community research/announcement records.

4. **Zhihao Chen** contributed ternary networks, controlled bases and translated frames, then integrated semantic precision and two-stage constructions. His work helped turn better finite networks into stronger bounds within the required interfaces.

   Sources: [#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7), [#16](https://github.com/CrocSwap/integer-mult-bounds/pull/16), [#21](https://github.com/CrocSwap/integer-mult-bounds/pull/21), [#23](https://github.com/CrocSwap/integer-mult-bounds/pull/23), [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29). GitHub: jacklightChen. X post not located. The ternary motif also had parallel development; avoid implying exclusive priority.

5. **RaD / hipotures** supplied semantic precision, routing and bulk-resampling machinery, followed by alternating pair-block producers and physical compiler checks. Their enlarged frames and paid cloning opened useful alternative construction paths.

   Sources: [#20](https://github.com/CrocSwap/integer-mult-bounds/pull/20), [#23 attribution](https://github.com/CrocSwap/integer-mult-bounds/pull/23), [#41](https://github.com/CrocSwap/integer-mult-bounds/pull/41), [#51](https://github.com/CrocSwap/integer-mult-bounds/pull/51). X post not located. #51's separate negative-basis witness has a narrower review status than the machinery consumed and fully replayed through #56.

6. **Avi Eisenberg** supplied interval strips and core-aware pair assembly. Extra additions can still pay off if more of them reuse existing wires. Combined with eumemic's compiler, this gives our strongest finite network.

   Sources: [#53](https://github.com/CrocSwap/integer-mult-bounds/pull/53), [#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62). GitHub: ikeboy. No account association or announcement verified; do not infer an X identity from the name alone.

7. **Chafik Boukhalfa** contributed reordered sums, exact recovery checks, paid clones, and better compiler composition and reclamation ordering. His checkers made improvements reproducible, and his compositions led the frontier before #62.

   Sources: [#43](https://github.com/CrocSwap/integer-mult-bounds/pull/43), [#46](https://github.com/CrocSwap/integer-mult-bounds/pull/46), [#48](https://github.com/CrocSwap/integer-mult-bounds/pull/48), [#54](https://github.com/CrocSwap/integer-mult-bounds/pull/54), [#58](https://github.com/CrocSwap/integer-mult-bounds/pull/58), [#60](https://github.com/CrocSwap/integer-mult-bounds/pull/60). **GitHub-linked X profile:** [@cfky_](https://x.com/cfky_). Announcement post not located.

8. **Aurel Prosz** contributed early parameter optimization and a scoped ceiling, then two-stage topology and the required paid endpoint correction. That topology removed a tensor factor and became an important ingredient in the later two-stage constructions.

   Sources: [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1), [#29 attribution](https://github.com/CrocSwap/integer-mult-bounds/pull/29), [#36 attribution](https://github.com/CrocSwap/integer-mult-bounds/pull/36). **GitHub-linked X profile:** [@aurel_pr](https://x.com/aurel_pr). [Aurel's live-tracker announcement](https://x.com/aurel_pr/status/2108214135179944096) is a verified post to link, although it announces a tracker rather than a new bound. The two-stage work has shared attribution, including Swapnil Jain.

9. **Swapnil Jain** helped lead the research to two-stage topology and macro batching, as Zhihao's integration note credits. His parallel project adds its own networks, a common-basis construction and Lean arithmetic checks, reaching a reported κ≈3.667×10⁻⁵.

    Sources: [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29), [#36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), and the [linked two-stage repository](https://github.com/Swapnil-jain/integer-mult-kappa/tree/ae405eb474d1486b2d8aef90139869f927f4836a). **Announcement supplied by Douglas:** [@SJ_Swapnil_Jain's sixth update](https://x.com/SJ_Swapnil_Jain/status/2108196538568851574), reporting a separate κ=3.667×10⁻⁵ witness and Lean checks. Its [quoted fifth update](https://x.com/SJ_Swapnil_Jain/status/2108175552549118371) reports κ=1.548×10⁻⁵. Our [finite-check review](../../research/swapnil-parallel/README.md) now reproduces round-six histograms, checks both rounds' moment/assembly arithmetic independently, and compiles all ten Lean declarations with no axiom dependencies. It does not certify his complete analytic/tape stack. The earlier influence is explicit in [Zhihao's note](../../references/copied-centers/pr29/two-stage-16-note.tex); Aurel retains credit for the topology and paid correction.

10. **Dominik Scholz** improved dimensions, parameter choices and fixed local bases, and combined compatible ideas from other contributors. Those refinements strengthened the two-stage family and helped expose where structural changes would pay off.

   Sources: [#22](https://github.com/CrocSwap/integer-mult-bounds/pull/22), [#27](https://github.com/CrocSwap/integer-mult-bounds/pull/27), [#30](https://github.com/CrocSwap/integer-mult-bounds/pull/30), [#33](https://github.com/CrocSwap/integer-mult-bounds/pull/33), [#35](https://github.com/CrocSwap/integer-mult-bounds/pull/35), [#38](https://github.com/CrocSwap/integer-mult-bounds/pull/38). X post not located. Include the concurrent #30/#38 work even where another composition overtook it.

11. **James Chang** contributed reversed two-stage geometry and exact controls for the data corners, together with balanced assembly. That geometry carried forward into the stronger fixed-basis constructions and the later audited releases.

    Source: [#34](https://github.com/CrocSwap/integer-mult-bounds/pull/34). GitHub: jamesyc. X post not located.

12. **Alejandro Zarzuelo Urdiales** added Gaussian-parity and finite-arithmetic proofs, Lean checks and source-bound verification tools. His latest exact parameter refinement supplies the final numerical value on Avi's graph and eumemic's compiler.

    Sources: [#45](https://github.com/CrocSwap/integer-mult-bounds/pull/45), [#61](https://github.com/CrocSwap/integer-mult-bounds/pull/61). **GitHub-linked X profile:** [@AlejandroZarUrd](https://x.com/AlejandroZarUrd). Announcement post not located. The Lean proofs cover their stated finite contracts, not the entire multiplication theorem.

13. **Ryan S** contributed Lean checks for historical certificates and algebraic contracts, plus an independent paired-circuit checker. This strengthened verification and clarified which finite facts were checked and which larger interfaces remained assumed.

    Source: [#26](https://github.com/CrocSwap/integer-mult-bounds/pull/26). GitHub: princezuda. **Suggested quote:** [@zudasworld's PR #26 announcement](https://x.com/zudasworld/status/2108156114517029316). The first-person post links the corresponding PR. Do not frame its finite/algebraic checks as full formal verification of multiplication.

14. **Rohan Gupta** found the dual-suffix strip layout and a parallel order improvement. His layout combined with eumemic's compiler and Chafik's reclamation changes to produce the previous best construction—a useful step on the way to the current graph.

    Sources: [#50](https://github.com/CrocSwap/integer-mult-bounds/pull/50), [#55](https://github.com/CrocSwap/integer-mult-bounds/pull/55). GitHub: gupt1156. X post not located. Distinct from Rohan Arun and Rohan Garg.

15. **Rohan Garg** contributed split-pair recursion and paid-clone composition, with complete finite replay and independent arithmetic checks. It gives a validated alternative construction and another useful direction for improving the finite network.

    Source: [#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59). GitHub: rohangar1. X post not located. This alternative is retained; it is not an uncredited dependency of #62.

16. **Andrew Barnes** contributed aligned pair groups and exact producer/frame checks early in the project. This was useful structural work that subsequent constructions could build on, even as the headline moved far beyond the original witness.

    Source: [#2](https://github.com/CrocSwap/integer-mult-bounds/pull/2). GitHub: Bortlesboat. **Suggested quote:** [@BTCOrangeCoin's PR #2 announcement](https://x.com/BTCOrangeCoin/status/2107959729226145914), reporting 14,944 fewer additions and a 6.25% improvement from 2⁻⁵⁹ to 17·2⁻⁶³. The account is linked from Bortlesboat's GitHub profile.

17. **David Leen** combined shared exclusions, retained totals and stage sharing in the complex network. That early contribution explored how more computation could be shared, adding headroom alongside the independently developed complex-compression work.

    Source: [#4](https://github.com/CrocSwap/integer-mult-bounds/pull/4). GitHub: dleen. X post not located. Credit this as parallel work without implying it was merged into the original separately checked 2⁻³¹ checkpoint.


## Additional parallel and verification work

These can be additional posts in the thread. Their inclusion credits participation;
it does not imply their results supplied the selected construction.

18. **Pranav Balakrishnan** explored complex scratch sharing in a parallel extension, reporting a progression from above 2⁻³³ to above 2⁻³¹. Independent explorations help broaden the search even when the main frontier moves ahead.

    **Suggested quote:** [@pranavbalakri's stronger announcement](https://x.com/pranavbalakri/status/2108023898688401719), reporting a 5.91×10⁻¹⁰ margin and linking [the research repository](https://github.com/pranavbalakri/integer-mult-bounds-improvement). [Earlier announcement](https://x.com/pranavbalakri/status/2108018660560277635). The post and repository association are verified; the full proof has not been audited here.

19. **Kenny Daniel** started a separate Lean formalization project aimed at the full fixed-tape multiplication theorem. That longer-term verification effort tackles obligations beyond the finite certificates checked so far.

    **Suggested quote:** [@platypii's project announcement](https://x.com/platypii/status/2108110520876421162). [Repository](https://github.com/platypii/integer-mult-bounds-lean); GitHub links this X handle. Its README explicitly says the end-to-end theorem is not proved. Credit the work in progress without describing it as completed verification.

20. **mjones / @_numinit** also reported a parallel 5.9×10⁻¹⁰ witness, with a patch and Nix flake planned. We welcome both parallel results and the work needed to make them reproducible.

    Source: [the announcement](https://x.com/_numinit/status/2108033292674990308). No patch, PR or repository is linked in this post; no mathematical audit or incorporated-code claim is implied. Keep this acknowledgement separate from reviewed submissions.

21. **Michiel Kosters (@one_line_proof)** explored weighted-hypergraph compression, aligned bit pairing and fewer complex centers in a parallel construction. His finite candidate reached 6.09×10⁻¹⁰ against the earlier 8.3×10⁻¹¹ checkpoint.

    Source: [the pinned research package](https://github.com/michielkosters/mathematics_ai/tree/2e0aa64ca09c87fc94f8575f59493f70cf929d71/problems/integer-multiplication-109). Douglas supplied the handle association; no specific announcement URL was supplied. Our [review](../../research/parallel-announcements/README.md) reproduces five tests and the full finite certificate after resolving a manifest line-ending mismatch. Complete transfer/precision integration remains open, as the source states.

22. **Abe (@abe_asfaw)** independently suggested dropping a redundant complex center while preserving dyadic arithmetic. On the earlier construction, the resulting counts support a 26.5% improvement to κ=1.05×10⁻¹⁰. A useful parallel observation, even though later work overtook it.

    Source: suggestion supplied by Douglas; no public post URL supplied. Our [exact check](../../research/parallel-announcements/README.md) verifies the h=24 scalar coefficients and historical assembly arithmetic. The rank-h center principle also appears in our preserved research notes. Credit the parallel contribution without assigning sole priority or describing it as an improvement to today's frontier.

## Closing

Some contributions supplied the next headline. Others supplied a reusable idea, an independent check, or a parallel route that was later overtaken. All deserve credit. The repo preserves those contributions, their dependencies and their validation scope. More collaborators welcome.

https://github.com/CrocSwap/integer-mult-bounds/blob/main/CONTRIBUTORS.md

The original OpenAI #109 manuscript and Harvey–van der Hoeven analytic machinery
remain credited. Douglas Colkitt's earlier parameter, routing, compact-control,
finite-network, review and integration work is recorded in the repository.
Contributor-specific AI assistance disclosures are preserved in NOTICE.

## Link verification notes

Checked public GitHub profiles and social-account metadata on 2026-10-08;
[the source receipt](contributor-social-sources.json) records the associations.
Rohan's PR #14 announcement was located through [Trendshift's repository mentions](https://trendshift.io/repositories/286834)
and its public post text retrieved through the FxTwitter mirror. The text links
PR #14 directly and states its 9.0799×10⁻⁷ witness. His PR #40 announcement was
then found inside [Douglas's quote](https://x.com/0xdoug/status/2108218367962124423);
its public text links PR #40 and states 3.918734894×10⁻⁵. Douglas subsequently supplied Swapnil's sixth update and Rohan's direct PR #40
reply; both were retrieved through the same public mirror. Their links are now
included above. X's direct pages returned 403 in this environment. Remaining
“not located” entries mean no verified announcement link was found, not that
no such post exists.

Douglas also supplied [@tariusdamon's post sharing PR #37](https://x.com/tariusdamon/status/2108179436008882493).
The text says “Fun to watch” and links Rohan Arun's submission. It supports an
acknowledgement for sharing the project, but does not establish a contributor
identity or authorship of that PR. Keep it separate from the technical credits.

The additional announcement URLs were recovered from [Douglas's shared research conversation](https://grok.com/share/bGVnYWN5_eab09726-0452-42e3-af73-2278c9e8c3c1), then each public post was fetched and checked directly through the same mirror. The receipt records each URL and response hash. Discovery through another agent is not treated as verification by itself. Historical claims are recorded in the [announcement ledger](contributor-announcements.md); “strongest” means the largest reported witness in this inspected set, not a claim to have exhaustively searched X or measured engagement.

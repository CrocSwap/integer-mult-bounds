# Contributor-by-contributor announcement draft

Prepared for Douglas Colkitt. Post only after the reviewed checkpoint reaches
main. Each numbered entry below is a draft post; the following source line is
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

   Sources: [#31](https://github.com/CrocSwap/integer-mult-bounds/pull/31), [#39](https://github.com/CrocSwap/integer-mult-bounds/pull/39), [#44](https://github.com/CrocSwap/integer-mult-bounds/pull/44), [#49](https://github.com/CrocSwap/integer-mult-bounds/pull/49), [#56](https://github.com/CrocSwap/integer-mult-bounds/pull/56), and the full contributor ledger. **Preferred announcement:** [Rohan's PR #40 post](https://x.com/RohanArun/status/2108190499941065193), which Douglas previously quoted. It discusses the both-fixed improvement near the 2⁻¹⁵ checkpoint. [His earlier PR #14 post](https://x.com/RohanArun/status/2108125292342444442) covers source frames and data blocks. Neither announces the newest #62 result. The fetched public post identifies @RohanArun; GitHub's profile currently links @Viewforge. Prefer the actual announcement link; check the active handle before tagging.

3. **eumemic** contributed complex-network compression, faster Gaussian resampling and auxiliary source frames. More recently, their joint frame compiler found cheaper ways to combine operations and reuse wires. That compiler is part of the current frontier.

   Sources: [#3](https://github.com/CrocSwap/integer-mult-bounds/pull/3), [#5](https://github.com/CrocSwap/integer-mult-bounds/pull/5), [#13](https://github.com/CrocSwap/integer-mult-bounds/pull/13), [#15](https://github.com/CrocSwap/integer-mult-bounds/pull/15), [#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57). No verified X account or announcement link. Search results suggest a similarly named account; do not tag it without establishing the connection to this GitHub contributor.

4. **Zhihao Chen** contributed ternary networks, controlled bases and translated frames, then integrated semantic precision and two-stage constructions. His work helped turn better finite networks into stronger bounds within the required interfaces.

   Sources: [#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7), [#16](https://github.com/CrocSwap/integer-mult-bounds/pull/16), [#21](https://github.com/CrocSwap/integer-mult-bounds/pull/21), [#23](https://github.com/CrocSwap/integer-mult-bounds/pull/23), [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29). GitHub: jacklightChen. X post not located. The ternary motif also had parallel development; avoid implying exclusive priority.

5. **RaD / hipotures** supplied semantic precision, routing and bulk-resampling machinery, followed by alternating pair-block producers and physical compiler checks. Their enlarged frames and paid cloning opened useful alternative construction paths.

   Sources: [#20](https://github.com/CrocSwap/integer-mult-bounds/pull/20), [#23 attribution](https://github.com/CrocSwap/integer-mult-bounds/pull/23), [#41](https://github.com/CrocSwap/integer-mult-bounds/pull/41), [#51](https://github.com/CrocSwap/integer-mult-bounds/pull/51). X post not located. #51's separate negative-basis witness has a narrower review status than the machinery consumed and fully replayed through #56.

6. **Avi Eisenberg** supplied interval strips and core-aware pair assembly. Extra additions can still pay off if more of them reuse existing wires. Combined with eumemic's compiler, this gives our strongest finite network.

   Sources: [#53](https://github.com/CrocSwap/integer-mult-bounds/pull/53), [#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62). GitHub: ikeboy. No account association or announcement verified; do not infer an X identity from the name alone.

7. **Chafik Boukhalfa** contributed reordered sums, exact recovery checks, paid clones, and better compiler composition and reclamation ordering. His checkers made improvements reproducible, and his compositions led the frontier before #62.

   Sources: [#43](https://github.com/CrocSwap/integer-mult-bounds/pull/43), [#46](https://github.com/CrocSwap/integer-mult-bounds/pull/46), [#48](https://github.com/CrocSwap/integer-mult-bounds/pull/48), [#54](https://github.com/CrocSwap/integer-mult-bounds/pull/54), [#58](https://github.com/CrocSwap/integer-mult-bounds/pull/58), [#60](https://github.com/CrocSwap/integer-mult-bounds/pull/60). **GitHub-linked X profile:** [@cfky_](https://x.com/cfky_). Announcement post not located.

8. **Aurel Prosz** contributed early parameter optimization and a scoped ceiling, then two-stage topology and the required paid endpoint correction. That topology removed a tensor factor and became an important ingredient in the later two-stage constructions.

   Sources: [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1), [#29 attribution](https://github.com/CrocSwap/integer-mult-bounds/pull/29), [#36 attribution](https://github.com/CrocSwap/integer-mult-bounds/pull/36). **GitHub-linked X profile:** [@aurel_pr](https://x.com/aurel_pr). Announcement post not located. The two-stage work has shared attribution, including Swapnil Jain.

9. **Dominik Scholz** improved dimensions, parameter choices and fixed local bases, and combined compatible ideas from other contributors. Those refinements strengthened the two-stage family and helped expose where structural changes would pay off.

   Sources: [#22](https://github.com/CrocSwap/integer-mult-bounds/pull/22), [#27](https://github.com/CrocSwap/integer-mult-bounds/pull/27), [#30](https://github.com/CrocSwap/integer-mult-bounds/pull/30), [#33](https://github.com/CrocSwap/integer-mult-bounds/pull/33), [#35](https://github.com/CrocSwap/integer-mult-bounds/pull/35), [#38](https://github.com/CrocSwap/integer-mult-bounds/pull/38). X post not located. Include the concurrent #30/#38 work even where another composition overtook it.

10. **James Chang** contributed reversed two-stage geometry and exact controls for the data corners, together with balanced assembly. That geometry carried forward into the stronger fixed-basis constructions and the later audited releases.

    Source: [#34](https://github.com/CrocSwap/integer-mult-bounds/pull/34). GitHub: jamesyc. X post not located.

11. **Alejandro Zarzuelo Urdiales** added Gaussian-parity and finite-arithmetic proofs, Lean checks and source-bound verification tools. His latest exact parameter refinement supplies the final numerical value on Avi's graph and eumemic's compiler.

    Sources: [#45](https://github.com/CrocSwap/integer-mult-bounds/pull/45), [#61](https://github.com/CrocSwap/integer-mult-bounds/pull/61). **GitHub-linked X profile:** [@AlejandroZarUrd](https://x.com/AlejandroZarUrd). Announcement post not located. The Lean proofs cover their stated finite contracts, not the entire multiplication theorem.

12. **Ryan S** contributed Lean checks for historical certificates and algebraic contracts, plus an independent paired-circuit checker. This strengthened verification and clarified which finite facts were checked and which larger interfaces remained assumed.

    Source: [#26](https://github.com/CrocSwap/integer-mult-bounds/pull/26). GitHub: princezuda. X post not located. Do not frame this as full formal verification of the result.

13. **Rohan Gupta** found the dual-suffix strip layout and a parallel order improvement. His layout combined with eumemic's compiler and Chafik's reclamation changes to produce the previous best construction—a useful step on the way to the current graph.

    Sources: [#50](https://github.com/CrocSwap/integer-mult-bounds/pull/50), [#55](https://github.com/CrocSwap/integer-mult-bounds/pull/55). GitHub: gupt1156. X post not located. Distinct from Rohan Arun and Rohan Garg.

14. **Rohan Garg** contributed split-pair recursion and paid-clone composition, with complete finite replay and independent arithmetic checks. It gives a validated alternative construction and another useful direction for improving the finite network.

    Source: [#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59). GitHub: rohangar1. X post not located. This alternative is retained; it is not an uncredited dependency of #62.

15. **Andrew Barnes** contributed aligned pair groups and exact producer/frame checks early in the project. This was useful structural work that subsequent constructions could build on, even as the headline moved far beyond the original witness.

    Source: [#2](https://github.com/CrocSwap/integer-mult-bounds/pull/2). GitHub: Bortlesboat. **GitHub-linked X profile:** [@BTCOrangeCoin](https://x.com/BTCOrangeCoin). Announcement post not located.

16. **David Leen** combined shared exclusions, retained totals and stage sharing in the complex network. That early contribution explored how more computation could be shared, adding headroom alongside the independently developed complex-compression work.

    Source: [#4](https://github.com/CrocSwap/integer-mult-bounds/pull/4). GitHub: dleen. X post not located. Credit this as parallel work without implying it was merged into the original separately checked 2⁻³¹ checkpoint.

17. **Swapnil Jain** is also credited in the incoming research for two-stage batching development, alongside Aurel Prosz's topology and endpoint work. That shared provenance matters: the current construction rests on contributions beyond the final PR author.

    Sources: [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29), [#36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), and the [linked two-stage repository](https://github.com/Swapnil-jain/integer-mult-kappa/tree/ae405eb474d1486b2d8aef90139869f927f4836a). No verified X identity or direct announcement located. This deliberately follows the source attribution without inventing a more specific individual claim.

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
its public text links PR #40 and states 3.918734894×10⁻⁵. X's direct pages returned 403
in this environment. No other contributor announcement URL was established from
indexed search, PR bodies or repository issue comments. “Not located” does not
mean no post exists. Replace PR links with contributor announcements when supplied.

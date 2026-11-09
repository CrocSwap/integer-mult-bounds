# Three signed frames, all old labels once

**Scoped character proof. No new κ and no word.**

Every rational solution of `R+S+T = 2I` by three nonzero symmetric rank-one matrices admits a first-order character that detects two calls and four targets. In the PR2085/2112 model the seven-call profile

```
(a,b,p,q,r,s,t) = (1,1,1,1,1,1,1)
```

therefore admits no word. The selected record stays κ = `781451/250000000`. The argument is written in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The card asks for a larger or nonabelian native alphabet. This package stays in the abelian symmetric 2-by-2 model and answers the three-frame question left open by [research/bit-two-signed-frame-floor](../bit-two-signed-frame-floor), for the single all-old-once profile released in [discussion comment 19377832](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377832).

The character is an integer form of one of two shapes, `(odd,odd,even)` or `(even,even,odd)` on the coefficient vector `(a,b,c)`. The proof shows that the mod-2 image of the integral relation lattice misses `(1,1)`, so at least one shape extends off that lattice. The extension detects either `{A,B}` or `{P,Q}`, two calls, and all four targets `A+P`, `A+Q`, `B+P`, `B+Q`.

The scale formula is proved by a 3-by-3 evaluation whose determinant is `2abc`, plus a bracket identity. `verify.py` expands the cleared numerator of that formula and checks that it is the zero polynomial. It also exhausts the 32 odd residue classes in the mod-8 discriminant lemma, and it checks explicit characters on nine declared frames: mixed parities, three horizontal directions, a negative-valuation sample, a vertical unit, an off-axis horizontal triple, the quarter-split parallel frame, and three orthogonal parallel splittings. Each witness detects two calls and four targets. Failure controls reject a tampered sum, reject `I` as a rank-one summand, and reject an even-even-even form.

The inherited inequality "detected calls ≥ detected targets" is not reproved. Predecessor replays, Lean, Docker, and the selected-result cold replay were not run.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue are historical provenance. Full Git history is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/three-signed-old-once --check-only
python3.12 scripts/research_package.py --package research/three-signed-old-once
```

The direct check is `python3 -I -W error -B research/three-signed-old-once/verify.py`.

## Open next questions

The other twenty three-frame count profiles from the seven-call census are open. A useful first step is to take one other profile, write its determinant equation, and test the same AB/PQ obstruction on one rational rank-one solution. No reduction of those profiles to `R+S+T = 2I` is supplied.

Four or more added signed rank-one frames are also open. The two-frame sign reduction and this three-frame character both stop at the number of added frames they assume. A useful first step is four primitive directions and the shortest determinant equation that uses each new label once.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant and first-order inequality are the PR2910 package as recorded in apoursh's two-signed-frame floor, PR6190. That floor left this three-frame question open and stopped at two added frames. The concrete handoff is discussion comment 19377832, following the census in comment 19377345 and the claim in comment 19377792.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review. New work is Apache-2.0.

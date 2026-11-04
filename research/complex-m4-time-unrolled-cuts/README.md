# Cuts through time at block 4: no 3 in 10 and no 2 in 7 without address maps

No new κ.

Jacob Sussman. Apache-2.0. Written with the help of AI agents (Anthropic's Claude); see *AI assistance and credit*.

## 1. What this is

A small unit that transforms W complex arrays at block size m with fewer than W·m paid calls gives a large saving,
ln(mW/s)/ln m for s calls, because the recursion repeats it at every size. At block 4 the most valuable open shape
for three arrays is **3 in 10** (a saving of 1.32e-1); the smallest is **2 in 7** (9.63e-2), where, for arrays that
each end on a call of their own, the best earlier certificate left room of only 640 out of 137,280. This note
settles both (checked by computer, given a rule and a reduction argued by hand) in the engine game **without
address maps**, with a counting rule that is new to this problem: the cut-set bound of
network coding, applied to the program unrolled in time.
In the full engine game, where address maps are free, both stay open, and the note says why the rule cannot reach
them and what a unit there would have to do.

| Result | Game | Status |
|---|---|---|
| The end-state chain rows: for every program and every shrinking chain of plane sets, the calls' costs across the chain are at least W times the target's | engine game without address maps | argued by hand (one AI reviewer re-derived it); tested on real and random programs by computer |
| No 3 in 10 at block 4, in any order; nothing below 10 either | same | checked by computer, given the rule and the reduction to one shape per orbit (both argued by hand): 121,951 certificates over the 80 orbits (1,097 shapes) that earlier rows allow |
| The shape n0 = (1, 2, 3, 4, 5, 6, 8, 9, 10, 12) fails in all 3,628,800 orders; it can never end with a two-bit call | same | checked by computer here (324 certificates), given the rule |
| No 2 in 7 at block 4, in any order | same | checked by computer here (3,098 certificates over all 38 orbits, 398 shapes), given the rule and the reduction to one shape per orbit |
| With address maps every call direction is equivalent to every other, and the rule is false (it would forbid the plain 12-call program) | engine game | checked by computer |
| A unit for 3 in 10 or 2 in 7 in the engine game must add two arrays whose addresses are relabelled differently, or end with a live array still relabelled | engine game | argued by hand (one AI reviewer) |

**Status words.** I use the words of my public repository. *Proved in Lean*: none in this note. *Checked by
computer*: an exact computation or stored certificates, checked by a separate program. *Argued by hand*: a written
argument; no person and no proof checker has checked it. Where an AI reviewer (an agent whose only job was to break
the result) re-derived it, I say so. *Computed*: a computation that is not a proof (one program only, or ranks
modulo primes); the line says if it was reproduced. *Open*: nobody has settled it.

## 2. What was known, and what this note adds

- **eumemic's certificate method** (#288) and my earlier note on this hub (#4628: the kept-subspace bound, 41W/13 at block 4)
  count, for a fixed subspace, how much each call can add. At block 4 they allow 3 in 10 and 2 in 7. That note
  listed 2 in 7 as the smallest open shape, with the 640 margin quoted above, and excluded 2 in 7, 3 in 10, 3 in 11
  and 4 in 13 when address maps and phase letters come only at the two ends, with no mixing between the end
  letters. Here phases and mixing may come anywhere, in any order; only address maps are left out.
- **The block-four coordinate-face obstruction by Nick Petalas** (#4855) allows arbitrary diagonal phases and
  coordinate permutations and bounds the sum of the calls' Hamming weights from below by 4W; with unit prices it
  gives only s ≥ W, as it says itself. The two results are about different games and neither contains the other.
- **Cuts through time** have been used on this hub before: David Arias's temporal rank bound (#2082) and Adam
  Gall's eight-query temporal cut (#2090) on the frozen P104 itinerary, and Michael Yee's independent max-flow
  audit of that cut family (#2163), which certifies its premises by a flow and a cut of equal size in a
  time-expanded network of the P104 frame model, where each node carries one array. Those cuts are for one fixed
  chronology of the P104 program; I have not compared that model with this one in detail.
- **Network coding.** eumemic described these units as network codes on the graph of frames, and pointed at
  additions across frames. Shike Chen (#634) showed that the rank saving of a unit is a coding gap: on the labelled
  exchange network of OpenAI's construction (upstream #109), coding reaches rate 1 while routing reaches at most
  (s + 2W)/(Wm + 2W), which is below 1 exactly when s < Wm. That bounds routing; the rule here bounds coding, by
  the rank of a cut. The rule is the cut-set bound of linear network coding (Ahlswede, Cai, Li and Yeung, 2000),
  with the capacity of a cut measured as the rank of a transfer block, as in the linear deterministic network
  model of Avestimehr, Diggavi and Tse. Afshani, Freksen, Kamma and Larsen used network coding for lower bounds on
  multiplication circuits, but only through a conjecture of Li and Li on undirected networks; the cut-set bound
  used here needs no conjecture. The application of the time-unrolled bound to every program and every order of a
  game of transform units, and that it works here, are new as far as I found.
- **An earlier claim.** A 3 in 10 at block 4 was proposed on this hub in #4818 and withdrawn by its author on
  23 October 2026, with #4813, #4819, #4826, #4934, #4937 and #4941, because none of their checkers counted paid
  calls. The exclusions here do not rely on that withdrawal.

What this note adds: the rule, stated and argued for the engine game without address maps; certificates that
exclude every order of every 10-call shape for 3 arrays and every 7-call shape for 2 arrays in that game; and the
facts that show the rule's limit once address maps are free.

## 3. The game and the model, in plain words

- **Calls and free steps.** At block 4 an address has four bits; a call direction is one of the 15 non-zero 4-bit
  patterns, written 1 to 15 (1, 2, 4, 8 are the single bits). A paid call in direction w applies
  C_w = (1 + i)/2 · I + (1 − i)/2 · X_w to one array, where X_w moves the entry at x to x + w. The target is
  K = C_1 C_2 C_4 C_8 on each of the W arrays. A *shape* is the list of directions a unit's calls use, an *order*
  is the order in which they come. The plain way is 4 calls per array.
- **Engine game without address maps.** Free: shifts, phases i^(z·x + c), mixing of arrays by any rational matrix,
  any number of scratch arrays, copies and erasures. Not allowed: relabelling an array's addresses by an invertible
  XOR-linear map (an *address map*), which the engine game allows at any time. Bit permutations are such maps, so
  they are not allowed here either.
- **The model.** The rule uses the program's action at digit width 3 only, so it applies to every unit that is
  right at all widths. Inside the antisymmetric part Λ³(C^16) (560 dimensions), each basis triple {x, y, z} lies in
  a two-dimensional subspace {0, x+y, x+z, y+z} of F_2^4, a *plane*; there are 35 planes with 16 triples each.
  Free steps of this game keep every plane's block in place. A call in direction w mixes the planes through a
  35 × 35 matrix, −8(I − 2π_w) for (2C_w) acting on Λ³, the same in each of the 16 shift characters up to a
  scalar and a diagonal change of basis (checked by computer in my repository for all 16 characters; this package
  checks the ranks for one other), where π_w is a projection of rank 7: a call can move 7 units of information
  between planes. The target mixes them through
  R_K = Π_j (1 − 2π_(e_j)) over the four single bits. The rules below only use blocks whose rows and columns are
  disjoint sets of planes, where a call's matrix and π_w have the same rank.
- **Plane rows** (the older rule: the kept-subspace bound with the subspaces that this game's free steps keep,
  which address maps do not keep): for a set U of planes,
  Σ over the calls of rank π_w[U, U^c] ≥ W · rank R_K[U, U^c].

## 4. The rule: end-state chain rows

**Statement.** Let a program of the engine game without address maps have W live arrays, any number of scratch
arrays, and calls in directions w_1, …, w_s in this order (each on any array). For every chain of sets of planes
U_s ⊆ U_(s−1) ⊆ … ⊆ U_0,

    Σ_(t=1..s) rank π_(w_t)[U_t, U_(t−1)^c]  ≥  W · rank R_K[U_s, U_0^c].

With U_t = U for every t this is the plane row at U. What is new is the rectangular blocks: rows in the set still
watched after the call, columns outside the set watched before it.

**Why it holds** (argued by hand; one AI reviewer re-derived it with its own reasoning and code). Track, for the
planes in U_t, the span of everything all arrays hold there, restricted to the inputs outside U_0. It starts at 0.
Free steps never enlarge it, because they keep every plane's block. A call in direction w enlarges it by at most
16 · rank π_w[U_t, U_(t−1)^c], since what it brings into U_t from inside U_(t−1) was already counted. At the end
the target forces it to be 16 · W · rank R_K[U_s, U_0^c]. In network-coding terms: planes at each moment are the
nodes, free steps are unlimited edges inside a plane, and the watched sets must shrink because scratch arrays
allow unlimited copies.

**Tests that it is not wrong and not empty** (checked by computer, in my repository). On 25 random programs with
3 live and 2 scratch arrays and random integer mixing (copies and erasures included), the step inequality of the
proof held in 313 of 313 steps and was tight in 92. 40 real programs whose arrays are mixed and copied end exactly
in the target and violate none of 160 random chains. Every one of the 1,965 pairs of plane sets used by any of the ten-move certificates holds for
the plain 12-call program in 72 orders, with least slack 3.

**Why the older rules could not do it** (argued by hand). The strongest fake for all earlier rules together is a
*scrambled program*: it makes n0's calls in a good order and scrambles everything between them. At every moment its
data are genuine subspaces of one vector space, so it satisfies every linear rank inequality (Ingleton's, the 24
new ones of Dougherty, Freiling and Zeger on five variables, and Kinser's among them) and every rule that only says
"this rank is at least that much". It holds 10 to 12 units per plane where 6 are needed, but none of the particular ones a
real unit must end with. A rule that tells them apart must ask *which* information ends where, and must use the
order of the calls. The chain rows do both. (One AI reviewer upheld the part on rank inequalities; the part on
"at least" rules was not re-derived by it.)

## 5. The exclusions

**Which shapes are left by the plane rows.** Plane rows at 1,524 sets of planes leave exactly 1,097 shapes of 10
directions for 3 arrays, in 80 orbits under the 24 bit permutations, and none of 9 (so none of fewer); for 2
arrays, 398 shapes of 7 in 38 orbits and none of 6 (checked by computer here, part `recount`). One representative
per orbit is enough: conjugating a whole program by a bit permutation g sends a call in direction w to one in
direction g(w), keeps every free step of the game and the target (argued by hand, a few lines).

**Certificates.** A certificate names a group of orders (all orders ending with a given suffix of calls) and a
chain whose row every one of them violates: the chain stays at one set c_0 through the calls not in the suffix, at
a cost that does not depend on their order, and then shrinks through the suffix calls. A file of certificates
excludes a shape when every certificate is valid and every order ends with one of their suffixes.

**n0.** The shape n0 = (1, 2, 3, 4, 5, 6, 8, 9, 10, 12) uses every direction with one or two bits once. Every
earlier rule allows it: three separate branch-and-bound searches over all 2^35 sets of planes found no plane row
that cuts it, and the scrambled program passes every earlier rule at every one of those sets (both checked by
computer, in my repository). 324 certificates
exclude all 3,628,800 of its orders. The scrambled program's order (3, 6, 2, 8, 5, 12, 1, 10, 4, 9) fails a chain
through 19, 18 and then 17 planes: the ten costs add up to **45, below the 48** the target needs. Six certificates
have a single-call suffix, one per two-bit direction: at a set of 17 planes where every unit of every call is
needed, a two-bit last call must send one of its 7 units into a plane that needs nothing more, so only 47 useful
units remain. Those six are one fact under the bit permutations that fix n0: **n0 can never end with a two-bit
call.**

**3 in 10.** For each of the 80 representatives, a search fixed the order from the end and wrote a certificate
whenever all orders ending with one suffix violated a row. In all, 121,951 certificates (17 MB) cover every order of
every shape. In my repository two checkers, written separately, each from the engine's rule book, and sharing no code with
each other or with the search, check every certificate exactly and check coverage two ways (by counting and by
listing every order). This package re-checks n0's file; the other 79 files are in my repository (sha256 in
`SOURCES.json`). **So no program puts 3 arrays through block 4 in 10 calls or fewer in this game** (checked by
computer, given the rule and the reduction to one shape per orbit, both argued by hand).

**2 in 7.** The rule holds for any W. With W = 2, 3,098 certificates exclude every one of the 5,040 orders of each
of the 38 representatives (checked by computer here, and by both checkers of my repository). Controls in my
repository: the plain program for 2 arrays violates none of 2,891 chains; read with W = 1, one orbit's certificates
all fail, as they must. **So no 2 in 7 at block 4 in this game**, private ends included, which settles, in this
game, the shape that the 640 margin left open.

## 6. With address maps

The engine game allows an address map on one array at any time. Then:

- **Every direction is the same.** Relabel an array's addresses by G, make a call in direction w, relabel back:
  that is a call in direction G^(−1) w, and G can be chosen to reach any direction. So every 10-call shape is one
  and the same question (checked by computer for all 20,160 maps G; one line by hand).
- **The rule is false there.** The plain 12-call program, rewritten so that every call is in direction 1, is a
  real program of the engine game; the plane row at {0, 1, 2, 3} says 12 · 0 ≥ 3 · 1 (checked by computer).
- **The 35 pieces become one.** The commutant of the free steps on Λ³(C^16) has dimension 35 without address maps,
  6 with the bit permutations only and 1 with all address maps (checked by computer). With one piece, no rule that
  reads only this part can exclude anything (argued by hand, from Burnside's theorem).
- **Valid rules there are weak.** The same counting with pieces that every free step keeps gives at least 7 calls
  for 3 arrays from the symmetric part, and at least W + 3 from the 2,295 Lagrangian subspaces of F_2^8 (the dual
  polar graph of Sp(8, 2)), where no constant chain gives more than 15/8 calls per array (computed; reproduced by
  one AI reviewer; the Sym³ figure uses ranks at two primes). The kept-subspace bound gives 9.46 for 3 arrays. Ten
  calls are allowed by all of them.
- **What a unit would have to do** (argued by hand; one AI reviewer). Call a program *frame-consistent* if each
  array can be given a current relabelling so that every mixing step only combines arrays with the same one.
  Undoing the relabellings turns such a program into one of the game without address maps followed by a
  relabelling of each live array at the end, and section 5 excludes those whose final relabellings are trivial.
  So a 3 in 10 or 2 in 7 in the engine game must either **(A)** add two non-zero arrays whose addresses are
  relabelled differently, or **(B)** never do that but end with some live array still relabelled. That cross-frame
  additions are where the room lies was pointed out before, by eumemic (#288).
- **Route (B) keeps a valid rule, with the target relabelled**, but the old certificates do not carry over: with
  fixed end relabellings and plane rows at 2,874 sets, 1,422 of the 3,645 orbits of 7-call shapes still pass for
  2 arrays (computed, with ranks modulo a prime, so exclusions are sound; reproduced shape by shape by one AI
  reviewer).

## 7. How to re-check

```sh
python3 -B research/complex-m4-time-unrolled-cuts/verify.py --part main       # PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_MAIN
python3 -B research/complex-m4-time-unrolled-cuts/verify.py --part recount    # PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_RECOUNT
python3 -B research/complex-m4-time-unrolled-cuts/verify.py --part controls   # PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_CONTROLS
python3 scripts/research_package.py --package research/complex-m4-time-unrolled-cuts --check-only
python3.12 -B scripts/research_package.py --package research/complex-m4-time-unrolled-cuts
```

Standard library only, exact integer and Gaussian-integer arithmetic; the three parts take about 1, 4 and under 1
seconds and at most 40 MB, and leave no files. `--part main` builds the 15 call matrices and the target on the 35
planes from the definitions of section 3, checks that each is −8(I − 2Q) with Q a rank-7 projection and that one
other character gives the same ranks, evaluates the two chains of section 5 (45 < 48 and 47 < 48), checks every
certificate of n0 and of the 38 two-in-seven shapes exactly with coverage by counting, and checks the sha256 of
every data file. `--part recount` recounts the 1,097 and 398 shapes and their orbits and compares the
representatives with the data files. `--part controls` must reject a file with one certificate dropped, a cost
lowered by one, a chain that grows, n0's certificates read with W = 2, n0's certificates applied to the plain
shape, and a two-in-seven file read with W = 1; and the plain program must violate none of the plane rows at the
324 bottom sets.

Not registered (author evidence, in my repository): the 79 other 3-in-10 files and both checkers
(`run_all.sh --full`, about 7 minutes and 800 MB on an Apple M4, because one checker lists every order); the
soundness tests of section 4; the address-map checks of section 6.

## 8. Limits of this work

- No person has read the proof of the rule or the frame argument of section 6; one AI reviewer re-derived each.
- The exclusions are about the engine game without address maps. They say nothing, either way, about the engine
  game with address maps, which is where a unit would have to live.
- Nothing here bounds κ, and nothing is claimed about integer multiplication.
- The 121,951 certificates explain little. A short proof that covers whole groups of shapes is open.

## Open next questions

The same questions, with first steps, are in `TASK.json`.

1. **3 in 10 at block 4 in the engine game, route (B)** (1.32e-1): a live array relabelled at the end. First step:
   plane sets chosen for each relabelled target, then the chain search with the right side
   Σ_l rank R_K[G_l A, U_0^c]; first on 2 in 7, where pairs of relabellings are fewer.
2. **Route (A)**: a rule that survives cross-frame additions with more structure than the pieces of section 6.
   The kept-subspace bound survives them (41W/13); nothing yet reaches 10/3.
3. **2 in 7 at block 4 in the engine game** (9.63e-2): the same two routes with W = 2.
4. **3 in 11 at block 4 without address maps** (6.28e-2): the same search over the 11-call shapes, with sets
   closed under each shape's symmetries.
5. **The game with only the bit permutations as address maps**: 6 pieces survive there, so a search of the same
   kind is possible.
6. **A short proof** in place of the certificates, starting from facts like "n0 can never end with a two-bit call".

## AI assistance and credit

I did this work with the help of AI agents (Anthropic's Claude). The model, the searches, the checkers, the
arguments and the texts were written by the agents under my direction; I set the questions and chose what to pursue.
Two AI reviewers checked the work with their own code. No independent human review of this package or of the work
behind it is claimed.

Credit: Ahlswede, Cai, Li and Yeung for the cut-set bound of network coding; Avestimehr, Diggavi and Tse for the
linear deterministic model; A. W. Ingleton, R. Dougherty, C. Freiling, K. Zeger and R. Kinser for the rank
inequalities named in section 4; eumemic for the certificate method (#288), for first describing these units as network
codes on the graph of frames and for pointing at cross-frame additions; Maximilian Lutz, whose review (#4643) of my
earlier note (#4628) led to the block-4 certificates published on 23 October, the state this work started from; Nick
Petalas (#4855), David Arias (#2082), Adam Gall (#2090), Michael Yee (#2163) and Shike Chen (#634) for the related
hub work of section 2; OpenAI for the cost model, the call and the kernel
(family 130 of openai/math); the game is that of the Lean engine in my repository.

## Files

- `README.md`, `TASK.json`, `SOURCES.json`, `VERIFY.json`, `verify.py`, `.gitattributes` (`* -text`, keeps the
  data bytes exact).
- `data/`: copied unchanged from my repository: `n0_certs.txt` (324 certificates), `two-in-seven/final_00.txt` to
  `final_37.txt` (3,098 certificates) and `two-in-seven/schedules.txt` (the 38 shapes), `ten-move-orbit-lists.txt`
  (the 80 shapes for 3 in 10), `cut_sets_and_images.txt` (the 1,524 plane sets as 35-bit masks, then their ranks).
  Planes are numbered by their sorted element lists; a certificate line reads
  `CERT <suffix> SET A CHAIN c_0,…,c_m COST x RHS y`, with sets as masks and x < y.

## Sources

- Hub base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a` (read 3 November 2026); task card `scope-navigation`
  (catalogue priority revision 8).
- Hub work credited: eumemic, #288 (the certificate method; network codes on the graph of frames; cross-frame
  additions); my earlier note #4628 (`research/complex-small-m-lower-bounds` on main: the 41W/13 bound and the
  640 margin); Nick Petalas, #4855,
  `research/block4-coordinate-face-tariff` (commit `8b8de0281f`, 22 October 2026); Michael Yee, #2163,
  `research/p104-cut-maxflow-audit` (commit `9f6e1f2783`, 14 October 2026), auditing #2082 (David Arias), #2090
  (Adam Gall), #2113, #2127 and #2136; Shike Chen, #634 (the coding gap); the withdrawn 3 in 10, #4818.
- My repository: https://github.com/jacobalansussman/wht-power-saving-lean at commit
  `0788bc656827ff2e7e44f5a77299eea19f0002fe` (3 November 2026; the folder below is byte-identical at
  `9c7f66f0241771bab4946b8f7b53609dbea83478`, where `SOURCES.json` pins the copied data),
  folder `research/block4-without-address-maps/`: `README.md` sections 1 (the rule and its tests), 2 (3 in 10 and
  n0), 3 (2 in 7), 4 (address maps); `GAME.md` (the rule book, written from the Lean files); `programs/` (both
  checkers and `run_all.sh`); `data/ten-move-orbits/orbit_00.txt` to `orbit_79.txt` (121,951 certificates);
  `data/outputs/rerun_2026-10-28.txt` (the full run of 28 October 2026 on an Apple M4); `HISTORY.md`. The earlier
  block-4 bounds: `research/block-bounds-and-new-rules/README.md` section 1.4 and
  `research/moonshot-block4-block5/README.md` section 1.
- Outside work (titles and places confirmed on 28 October 2026 from the arXiv pages and publisher listings):
  Ahlswede, Cai, Li and Yeung, "Network information flow", IEEE Transactions on Information Theory 46 (4),
  1204-1216, 2000. A. S. Avestimehr, S. N. Diggavi and D. N. C. Tse, "Wireless network information flow: a
  deterministic approach", IEEE Transactions on Information Theory 57 (4), 2011, arXiv:0906.5394; an earlier
  version is "A deterministic approach to wireless relay networks", arXiv:0710.3777 (2007). A. W. Ingleton,
  "Representation of matroids", in D. J. A. Welsh (ed.), Combinatorial Mathematics and its Applications, Academic
  Press, 1971. R. Dougherty, C. Freiling and K. Zeger, "Linear rank inequalities on five or more variables",
  arXiv:0910.0284 (2009). R. Kinser, "New inequalities for subspace arrangements", Journal of Combinatorial
  Theory, Series A 118 (1), 152-161, arXiv:0905.1519. P. Afshani, C. B. Freksen, L. Kamma and K. G. Larsen, "Lower
  bounds for multiplication via network coding", ICALP 2019, LIPIcs 132, 10:1-10:12, arXiv:1902.10935 (confirmed
  on 3 November 2026 from the arXiv and LIPIcs pages).
- Hub work credited, continued: Maximilian Lutz's review of #4628 is #4643 (22 October 2026).

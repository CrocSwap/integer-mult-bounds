# Task card — masked root-star copy-cost floor on P112 (trimmed-star census)

Task ID / proposed scope key: complex-masked-decoder / 7acfe4d9cac04f7ba4cb (track complex-mechanisms,
OS-random seed b27e6ad9fd261c4b4134d5d02523a8a1, refined to the trimmed-star mixed-beta slice).

Base commit; exact predecessor and dependency heads:
- Base: e208d5e77a204252f92b395aae271679cc3a56f0 (origin/main at session start).
- Predecessors read (not modified): CrocSwap/integer-mult-bounds#717 head 4a97676294f9fa413b65986e9984fddeda71e4cc
  (format-limits-2, D1 model and open problem), research/complex-frame-pair-decoders/ (CrocSwap/integer-mult-bounds#968,
  head-pinned model adapter), research/complex-decoder-field-extension-seed44/ (CrocSwap/integer-mult-bounds#1077),
  research/p112-single-lift/ (CrocSwap/integer-mult-bounds#845), research/root-pair-first-drop-seed48/, and the frozen
  selected record (certificates/selected-result.json, kappa 836330098538459/5e17).

Concrete object and question:
CrocSwap/integer-mult-bounds#717 D1's open mixed-beta hole on P112: masked E-graph decoders (exactness only on the
6720 even-pair entries x_i.y_j = 0 off-diagonal, x_i.y_i = 4; the 5824 odd entries fixed by
cost-0 singleton terms) whose terms have ROOT-STAR support pairs: R = C(alpha) or
N(alpha) = C(alpha) minus its own line, A = C(beta) or N(beta), alpha,beta among the 120
E8 root lines, arbitrary real coefficients. Question: can such a decoder with any number
of terms achieve cst = sum of label-pairing ranks < 64 (the coordinate decoder's cost)?

Existing restriction being changed (or exact claim being audited):
The eight-term all-pairs bound (CrocSwap/integer-mult-bounds#968 and its extension: cst >= max(72-p,56) at p<=24; CrocSwap/integer-mult-bounds#717
D1(b): cst >= 64 on P112 for 8 costly terms with flat supports; D1(c): all beta>=8 and
n>=9 give >= 72) is changed in two assumptions at once: all-pairs identity -> masked
E-graph identity, and fixed n = 8 -> arbitrary n with mixed-beta terms. The trimmed-star
atoms N(alpha) are non-flat supports of pairing rank 7 (odd root pairs), i.e. exactly the
beta <= 7 atoms D1 excludes; D1(b)'s span census does not apply to them.

Method; explicit parameter ranges/candidate alphabet:
Complete finite census, exact integer/F2 arithmetic, stdlib only. Alphabet: all 240
root-star supports (120 normals x {untrimmed C, self-trimmed N} intersected with P112) and
all 57,600 ordered support pairs; exact pairing rank beta(R,A) and exact frame-hit count
over all 1260 E-graph 8-cliques (frames). Frame-substitution bound: every frame block is
a rank-8 problem, so >= 8 terms meet every frame; cst >= 8*1260*gamma with
gamma = min over atoms of beta/hit. Bound = 64 iff max(hit/beta) = 1260/8, i.e. iff every
beta-7 trimmed atom hits at most 1102 frames. Positive control: the coordinate decoder
(8 star terms, cst 64) rebuilt and checked exactly. Reduction control: cost-0 singleton
patch fixes one odd entry exactly. Mutation controls on the census tables.

Nearest overlapping PRs and why this adds something:
- CrocSwap/integer-mult-bounds#717 (open, DreamingOfClouds): D1 states the mixed-beta n>=9 hole; its census covers only
  flat supports and its (e) covering bound is sampled over general span pairs (caps 43.8).
  This adds the exact answer for the root-star trimmed/untrimmed family, including the
  beta-7 atoms, in the masked model.
- CrocSwap/integer-mult-bounds#968 research/complex-frame-pair-decoders (merged): 8-term all-pairs floor; explicitly
  excludes masked identities and n >= 9 (its PROOF.md scope, line 186-193).
- research/complex-decoder-field-extension-seed44 (CrocSwap/integer-mult-bounds#1077, merged): masked E-graph
  identities deferred as "separate proof model" (OVERLAP.json).
- research/root-pair-first-drop-seed48 (merged): masked identities deferred likewise.
- Open star-decoder PRs CrocSwap/integer-mult-bounds#1171/CrocSwap/integer-mult-bounds#631/CrocSwap/integer-mult-bounds#725/CrocSwap/integer-mult-bounds#732/CrocSwap/integer-mult-bounds#669 concern the BIT-side label-code star
  model and puncture ratios (63/111), not the complex B14 pairing-rank cost on P112.
- p112-single-lift (CrocSwap/integer-mult-bounds#845) / p112-complex-single-lift: ninth total with fixed readers for
  the all-pairs identity; excludes masked completions. Complementary, not competing.

Optimistic full cost budget; required observable improvement:
A cst = 63 masked decoder on P112 would raise the T37 deficit 37*(8*112-9*63) = 12173 vs
11840 (+2.81% b per cst unit, CrocSwap/integer-mult-bounds#717 P1) toward the CrocSwap/integer-mult-bounds#589 cap kappa 0.001730427469823602
(4.12% above the selected 0.001672660197076918). Whole-construction charges (centre reads,
frames, restoration; CrocSwap/integer-mult-bounds#717 recorded unpaired-centre parity >= 78 and net -0.1..-10% b for
P104-style realizations) must be counted before any moment claim. A negative result needs
no supplier pricing.

Success evidence; falsification test; time/compute cap:
Success: exact census with max(hit/beta) < 1260/8 strictly for every beta-7 atom, giving
cst >= 64 sharp for the whole family (any n), plus controls. Falsification: any single
beta-7 atom pair with hit > 1102 falsifies the 64 bound immediately and is reported with
its exact hit count as the lead for a construction; the exact bound value is then reported
instead. Cap: single-machine minutes; no network; stdlib only.

Predecessor authors; intended artifact and reproduction command:
DreamingOfClouds (CrocSwap/integer-mult-bounds#717, CrocSwap/integer-mult-bounds#595 and CrocSwap/integer-mult-bounds#604), Joel Pulikkan / GamingPuzzled (CrocSwap/integer-mult-bounds#620),
themilkman216 ([PR 968](https://github.com/CrocSwap/integer-mult-bounds/pull/968), with Anthropic Claude assistance) and woklerx ([PR 1077](https://github.com/CrocSwap/integer-mult-bounds/pull/1077), with OpenAI Codex assistance), Mihir Srivastava (CrocSwap/integer-mult-bounds#845), seed48 package authors, and the
selected T37 chain (see certificates/selected-result.json). Artifact:
research/masked-root-star-floor/ with verify.py; command:

    python research/masked-root-star-floor/verify.py

Expected final line: PASS_MASKED_ROOT_STAR_FLOOR ... (counts recorded in README).
Contributor: Navinor, with help from opencode. Apache-2.0.

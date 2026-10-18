# E8 bit word with 111 live ports: PR #545's punctured-star unit on PR #543's R420 skeleton

A new E8 bit supplier (h = 8, **v = 111 live ports**, 9 retained totals of frame rank 7, decoder constant 63) with
**R = 439 helpers**. It stacks the punctured-star unit of #545 (DreamingOfClouds: nine lines are neither sources nor
targets, and each retained total is a pseudo-target that reads what the removed target would read) on the R420 L3
skeleton of #543 (keepers read by targets, then rewritten in phase B). Priced by two hub pipelines, parameterised for
v <= 120:

| quantity | value |
|---|---|
| **bit c, nine stages** (#510's chain: #463 template, 32 replicas, #442 hosting; parameterised by `code/adapt9p.py`; 10^-24 grid) | `1733052823330162099157/10^24` = **0.001733052823330162099157** |
| bit c, eleven stages (#493's chain as parameterised by #545's `adapt.py`, vendored and run unchanged) | `427652201524503168379/(2.5·10^23)` = 0.001710608806098012673516 |
| #543's R420 word, nine stages (same pipeline at v = 120; #543's receipt, not rerun here) | 0.001653826988146798944268 (this word: +4.79%) |
| #545's punctured R489 word, eleven stages (control, reproduced here) | 0.00165947204563779652541 (this word: +4.43% at nine stages, +3.08% at eleven) |
| #510's R480 word, nine stages (control, reproduced here) | 0.001587447106092548137108 (this word: +9.17%) |

The nine-stage c is 8.76% above the largest cited complex b (#548), so every composition is complex-bound. Through
#493's six-level, 47-inequality outer assembly:

| complex supplier (cited from its receipt, not rebuilt) | complex b | κ | binds |
|---|---|---|---|
| **#548** (Dugongue; open PR) | `796759709641153381751/(5·10^23)` = 0.001593519419282307 | **`49718254847979/31250000000000000` = 0.001590984155135328** | complex |
| #544 (chafreaky; open PR) | `31864911873350496687/(2·10^22)` = 0.001593245593667525 | `397677800014309/(2.5·10^17)` = 0.001590711200057236 | complex |
| #535 (icekylinx; open PR) | `1589991533606044174031/10^24` = 0.001589991533606044 | `793733736881443/(5·10^17)` = 0.001587467473762886 | complex |
| #531 (icekylinx; merged) | `304013615566499291631/(2·10^23)` = 0.001520068077832496 | `1517760977820331/10^18` = 0.001517760977820331 | complex |

#548's own κ, 0.001590591090759927, is bound by its own bit c 0.001593125101352604961534; with this word it becomes
#548's complex cap (+0.0247%). The κ values are the same with #543's R420 word (its c is also above every cited b): the
value of this word is bit headroom. The bit side stays non-binding for any complex b below about 0.00173.

## The word

`data/bitE8mut-p111.json.gz` is rebuilt byte for byte by `code/gen_p3.py` from #543's frozen plan
`data/plan-l3.json` and the parameters `data/punct.json` (about 2 s). Format: bitE8/1 with mutable sources, v = 111
live labels (`ports_geom`, `punctured` as in #545). Punctured lines P = [10, 15, 51, 53, 56, 66, 72, 89, 111]: two in
block 0, three in block 1, two in block 3, two in block 5 (block pairs (0,1) and (3,5)), one per 4-frame, none of
lines 0..7.

**Why #545's construction does not carry over unchanged.** In #493's skeleton the Q-node runs in phase A, so a
pseudo-target can read everything a target reads before the scatter. In L3 the block node runs in phase B: the source
registers it transforms are first read by the targets at their cells. A retained total is read by the scatter, at the
end of phase A, so the part of a target's sum that comes from the block node (the live lines of the complementary
block B, about ten lines) is not available to a pseudo-target. The parity of the d-lines also differs: in a 4-frame
with one punctured line the pseudo-target needs an odd number of single d-line reads (the three parity equations sum
to 1).

**The pseudo-target total of a punctured line p** (a fresh helper):

- at the line frame of kline(p), before that line's cell gate: it reads the source of kline(p), its single d-line;
- at D6[p, qhost(p)]: it reads that D6's o1 (it takes the place of the third register qdel[p]; qhost(p) still reads
  o1 in phase B);
- at p-perp: it reads p's needers at its two (z,z) D6s. One of them is a free keeper of B (a register holding one
  line of B in L3) that a phase-A **mini-node** at the block frame D4(B) rewrote to carry the pseudo-target's B-part.
  The mini-node reads the other free keepers of B, the freed sources of B (the source in the d-single cell of a
  punctured target of B, which no target reads), and **extra carriers** (a helper that reads a source of B at its line
  frame in phase A) for the lines nothing else holds.

Eligible lines: both (z,z) cells of p's 4-frame contain p (so p's needers there are free after phase A), and
qhost(p) is not kline(p). 19 lines are eligible under #543's plan, 18 of them outside lines 0..7 (which stay live for
#493's frame-zero residual isometry); #545's P is not eligible (its line 39 fails).

**Decoder.** The nine pseudo-target totals HYP[p]|live span every live decoder row (1 + B(t,.))|live exactly when the
classes of P in E8/2E8 are affinely independent (odd subset sums of nine affinely independent points cover F2^8). A D4
block's classes span 4 dimensions and a complementary pair's 6 (affine rank 7), so P meets at least two block pairs.
The exact replay checks the decoder on all columns.

**Count.** R = 420 (the L3 helpers; the punctured lines' carriers stay as wires) + 9 totals + 10 extra carriers. The
extra carriers also serve as junk wires of the block nodes whose outputs outnumber their live inputs. The local
histogram is {1: 1321, 2: 1342, 3: 80, 4: 47, 5: 102, 6: 10, 7: 18}, rank mass 5,129 = 8R + 63 + 14v.

**Rank-mass identity.** M·live − mass = T(2Kv − L·cst) for v ports and decoder constant cst (#545): at nine stages
(M = 64, K = 4, L = 9, T = 32) T(8v − 9cst) = 32 · 321 = 10,272 here (v = 120, cst = 72: 9,984). The nine-stage
hosting wall R <= 4v = 444 admits R = 439: all 126,432 residuals are hosted whole, with no banks.

## Review points

1. **Source registers rewritten in phase B** (as in #543): 483 phase-B source writes (block nodes at block frames,
   needer merges at D6 frames). 454 of the 499 phase-B z-writes rewrite a register that a target has already read in
   phase B; the others write freed sources and extra carriers, which no target reads. `code/xcheck_p.py` checks the
   hypotheses (H1)-(H5) of the interleaved scalar-interface lemma of #543's README and its conclusion term by term;
   #493's `interface.py` refuses the word at its check (4), as for #543.
2. **A 111-port unit with decoder constant 63** is an admissible bit supplier for the outer assembly on the same
   hypotheses as v = 120 (as #545 states). Nothing on the complex side depends on v.
3. **Helpers written in phase B.** 16 phase-B gates write helpers: extra carriers used as junk wires in the block nodes
   (13, at block frames) and their merges with D6 o1 registers (3). They are z-gates under (H3) and are reversed by C.

## Checks (`verify.sh`)

```sh
python -m pip install -r research/e8-bit-p111/requirements.txt
bash research/e8-bit-p111/verify.sh /absolute/new/output
```

Python 3.11+ with numpy, sympy and scipy, a C++17 compiler (`CXX`) and Boost headers (`BOOST_INCLUDE`). About 4
minutes on 4 cores (the two controls run in the background).

0. Manifest. Provenance: 19 files vendored from #510, 5 from #545 and 2 receipts each from #548, #544 and #535, each
   checked by git blob id; main's files by sha256 (#493's package through its own `MANIFEST.sha256`, #531's receipt).
   Every cited b against its receipt; `code/receipt_kappa.py` recomputes the own κ of #548, #544 and #535 from their
   receipts through the same assembly (all 47 constraint values, bootstrap cutoffs and controls equal for their
   exact-assembly receipts).
1. The word rebuilt from the frozen plan and parameters equals the shipped word.
2. `code/xcheck_p.py` (independent; reads only the word): the 111 labels are root lines of an even unimodular rank-8
   lattice, the 9 punctured lines are found by enumerating its roots, every frame is closed in the live labels, exact
   F2 replay on all 661 columns, the 9 totals sit at the hyperplanes of the 9 punctured lines with COPY ranks
   7 × 9 = 63, and (H1)-(H5) with the conclusion. #543's 9 + 1 word-level controls and 4 punctured-design controls
   (`code/mutants_p.py`: a total's d-single read dropped, a mini-node gate dropped, a total moved to the full frame
   (decoder constant 64), a needer read dropped; cleanup adjusted alike) are rejected. The same checker accepts #510's
   R480, #493's R489 and #545's punctured R489 words.
3. #545's v <= 120 form of #370's checker refuses the word ("x register written"); its relaxed copy passes; #493's
   `interface.py` refuses at check (4).
4. Official checkers at (v, R) = (111, 439): legality at NCOPY = 9 (27,234 records, rank mass 5,129); five-stage
   columns (883 columns, payload 93 bits < 104); nine-stage (`columns_k`, KPAIRS = 4: 1,327 columns, 18/18
   omitted-bridge controls); eleven-stage (KPAIRS = 5: 1,549 columns, 24/24); the KPAIRS = 2 regression; #370's 6
   record mutants (in #545's form); the 3 phase-B record mutants; Gram determinants and prime witnesses on 636 frames.
5. Geometries over the live labels (#545's parameterised #386 and #445 files); `code/adapt9p.py` parameterises #510's
   nine-stage files (27 listed edits; V from the word or the parent GLOBAL.json, the decoder constant from the
   records' COPY ranks).
6. Nine-stage price: #442's programme rediscovers `data/selection9-p111.json`; template, parent audit (17 template
   mutations rejected), hosted audit (16 mutations rejected); invoice: prefix 177 bits (charged 192), two-level 393
   bits (charged 512), maximum child 42 (2·42² < 64²), row 18,355.
7. Eleven-stage price through #545's parameterised files: #442's programme rediscovers `data/hosting11-p111.json`; all
   38,632 residuals hosted whole; independent audit; invoice: prefix 4,304 bits (charged 4,352), three-level 12,966
   bits (charged 12,992), row 19,431 < 20,161.
8. Controls: (a) #510's R480 word through #510's vendored nine-stage files and through the parameterised files, on the
   same geometry: parent GLOBAL.json and template, parent audit, hosted GLOBAL.json, template and audit, and
   RESULT9.json are identical (byte for byte where no run time is stored), and reproduce #510's c and κ values and,
   with #535's b, #535's κ 0.001584931111785787 (bit-bound); (b) #545's word through #545's files reproduces #545's
   c, profile, emitted-program hash and κ.
9. Every number against `EXPECTED.json` and the cited receipts.

## Retained assumptions

- Every interface that #472's, #510's, #543's and #545's compositions retain: the all-size bit/Gaussian compiler; the
  mutable-basis and target-label realization (review point 1); a v = 111 bit supplier in the outer assembly (review
  point 2); whole-call correlated-helper hosting (#442; #545 discloses that several helpers of one call share a family
  at disjoint cells, as in #503); compressed windows and restored work; the common grid and tape, precision, row and
  analytic contracts.
- Complex savings are cited from their PRs' receipts, not rebuilt. #548, #544 and #535 are open PRs; #548 also retains
  #539's bad-class transport as a premise.
- The plan is #543's CP-SAT nomination; P, the free-keeper seed, the receiver choices and the hosting selections are
  nominations (`discovery/`); none is claimed optimal.
- This is a conditional finite construction, not a Lean proof.

## Files

- `code/gen_p3.py`, `code/pwordl.py`, `code/nodeopt.py`, `code/planio.py`: the generator.
- `code/xcheck_p.py`, `code/mutants.py`, `code/mutants_p.py`, `code/mutrec_b.py`: the independent replay and
  interface audit, word-level controls and record-level phase-B mutants.
- `code/adapt9p.py`: the nine-stage parameterisation.
- `code/provenance.py`, `code/cited.py`, `code/receipt_kappa.py`, `code/summary.py`: pins, receipts and comparisons.
- `data/`: the word, plan, parameters, frozen hosting selections, cited b and the receipts of #548, #544 and #535.
- `vendor/pr510/`: #510's nine-stage chain (as in #543's package). `vendor/pr545/`: #545's `adapt.py` and
  `punct_cfg.py`, and its word, hosting selection and EXPECTED.json (control).
- `discovery/` (not run by `verify.sh`): the nomination of P and of the generator parameters.
- `DEPENDS.json`: the files of main this package uses, pinned.

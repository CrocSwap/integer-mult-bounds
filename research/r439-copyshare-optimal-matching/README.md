# Exact optimum for the selected-D disjoint helper-pair recipe

**17,933 complete ADDs is the exact minimum in this fixed pairing class.**
The published circuit uses 210 disjoint restored helper pairs, saves 6,372
ADDs against the unchanged PR589 word, and strictly improves PR2487's best
greedy point by **127 ADDs, 1,090 in F and 40,470 in B**. The full dirty-input
boundary, frame paths, nine rank-seven copies and paid recursive profile are
unchanged. **No new κ.** This is a finite bit-component result, not a new
selected supplier or a claim of the cheapest bit circuit in other classes.

| Complete word | ADDs | D ADDs | F | B | Local / nine-stage bits |
|---|---:|---:|---:|---:|---:|
| PR589 baseline | 24,305 | 18,085 | 49,347 | 1,113,070 | 93 / 177 |
| PR2487 greedy seed 7 | 18,060 | 11,840 | 73,805 | 1,187,790 | 95 / 180 |
| This exact matching | **17,933** | **11,713** | **72,715** | **1,147,320** | **95 / 180** |

The D invoice is **210 preparation + 11,293 middle reads + 210 restoration**.
The unchanged suffix costs 6,220 ADDs. Both exact inequalities
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192` pass. These are inherited
positive-envelope guards, not measured hardware speed or memory use.

## New evidence and comparison class

[PR2487](https://github.com/CrocSwap/integer-mult-bounds/pull/2487) left open
whether a non-greedy matching could save at least 6,245 ADDs with F below 73,805.
This package answers yes and closes the ADD optimum for its unchanged-target
basis. It replaces the greedy choice rule by a maximum-weight matching and
checks an exact certificate: 430 nonnegative vertex prices, 47 positive odd-set
prices and all **92,235 unordered-pair inequalities**. Their doubled bound is
12,744; the explicit circuit attains saving 6,372. The proof needs only integer
inequalities and disjoint endpoints, not trust in a solver.

The domain is precisely the 430 non-retained helpers read by the original
PR589 D, disjoint pairs, one preparation and reverse restoration per pair,
direct rewritten target injections, and an unchanged continuation. Retained
helpers, overlapping basis changes, target basis changes and arbitrary XOR
circuits are outside the class. PR941's earlier matching certificate applies
the classical method to a **different PR915 target basis**; its 11,948-ADD
floor is not contradicted or rediscovered. Existing helper-star circuits are
also outside this class and can be cheaper.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/r439-copyshare-optimal-matching
```

The registered run checks the complete certificate, all three nominated
optima, both full-word orientations, all 661 independent D input columns,
the unchanged owner's virtual-splice interface, the official exported
arithmetic stream and paid profile, ten mathematical controls, and three
on-disk corruption controls. It also runs without Git under isolated optimized
Python and confirms that verification leaves the source closure unchanged.
Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/r439-copyshare-optimal-matching outcome=completed
```

Direct replay prints `PASS_R439_COPYSHARE_OPTIMAL_MATCHING saving=6372
ADDs=17933 F=72715 B=1147320 columns=661 edges=92235 controls=10 no_new_kappa`.
`MATCHING.json` contains the full circuit recipe and integer dual;
`EXPECTED.json` contains the complete checked receipt and exported-record hash.
`PROOF.md` proves the recipe, bound and chronological substitution scope.

Optional discovery uses **NetworkX 3.6.1**, with its exact matching-function
SHA256 checked in `nominate.py`. After installing that version, run
`python3 -B research/r439-copyshare-optimal-matching/nominate.py --output /tmp/new-matching.json`.
The output path must be new; the result must equal the frozen receipt.
Discovery considered exactly three objectives/orderings: sorted, seed 3,
and a forward-envelope proxy. All attain 6,372; their F values are 74,463,
74,023 and 72,715. No claim of minimum F or B among all optimal matchings is made.
There was no random-seed sweep, deletion search or later expansion.

## Source and scope

Scientific base: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`.
`SOURCES.json` pins every consumed file by Git blob and SHA256; `CLAIM.json`
records the OS-random assignment seed **03**, three candidate tasks, overlap
coverage, cost decision and stopping rule. The original catalogue card is
retained verbatim in `TASK.json`; its scope change is explicit.

The semantic H2 contract and chronological substitution bridge are inherited
from PR1194/1782. The actual helper-writing circuit still fails the original
syntactic H2 and literal K-extractor flags; this package does not weaken those
checkers. The proof-only original-D splice passes every inherited flag, and
the replacement has identical complete values and frames at the D/A cut.

The profile remains `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, mass
5,129. No helper, source access, copy, frame change, restoration or recursive
child is hidden. The complex side still binds the selected result. Native
C++ replay, hosted emission, the all-size compiler, common-label realization,
physical routing, precision/tape implementation and outer analytic admission
are not supplied here. This finite certificate is not a formal proof of the
full multiplication theorem. The selected frontier and `upstream/` are untouched.

## Open next questions

- Does this exact finite word merit supplier admission? First compare its
  unchanged paid profile and finite envelope to already cheaper helper-star
  candidates before paying for native/hosted integration. The outstanding
  physical/compiler/analytic obligations, and the nonbinding bit side, block
  an exponent claim; this result alone does not justify a new search campaign.
- Can one prove a sharper F bound among the ADD-optimal matchings? A first
  step is to derive the actual maximum-of-linear-forms objective on the
  certified optimal face. The present forward proxy and three samples do not
  establish that stronger optimum.

## Attribution

Prepared for **@CubeJerry** with substantial **OpenAI Codex assistance** in
scoping, mathematical reasoning, implementation, verification and writing.
Credit Aaron Wang/PR848 for the restored-pair recipe, navinor/PR1782 and
woklerx/PR1194 for semantic admission, Wentao Li/PR1805/2487 for priced
comparators and the open question, and Gareth Davidson/PR941 for the earlier
integer matching-certificate and discovery technique. Credit DreamingOfClouds/
PR589, eumemic/PR555, Dylan Crow and the retained E8/native lineage for the
unchanged word and exporter. The matching algorithm is classical
Edmonds/Galil, implemented by NetworkX. See `NOTICE.md`. New work Apache-2.0;
no independent human or proof-assistant review is claimed.

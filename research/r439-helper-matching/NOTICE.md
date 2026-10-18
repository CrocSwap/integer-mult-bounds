# Notice and attribution

New material is Apache-2.0. Prepared for **Gareth Davidson (@bitplane)** with
substantial **OpenAI Codex assistance** in research, implementation, proof,
verification and packaging. One AI agent performed the work. Independent
arithmetic implementations do not imply independent human review.

**Sagar Thakrar (@thakrarsagar), PR716 and PR817**, supplies the prior
fixed-basis matching and exact price-certificate approach. The PR817 README
at `3147cac35c659152d36db1e0e60b9ce4b152c008` is preserved verbatim with its
SHA256 and Git-blob identity. It includes its Apache-2.0 and substantial
OpenAI Codex disclosures. No executable or numerical saving is imported
from PR817. The new result concerns R439 helper columns, includes odd-set
prices, and separates the exact arithmetic floor from the precision budget.

The matching algorithm and odd-set inequalities are classical, not new
mechanisms claimed here. Optional nomination calls **NetworkX 3.6.1** with
integer weights; its function source SHA256 is
`41930910962d79c5da2da89788ead7819730daccb2858d72df3df7c55d893ee1`.
The [official documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.matching.max_weight_matching.html)
credits **Jack Edmonds** for the blossom/primal-dual methods and **Zvi Galil**,
*Efficient Algorithms for Finding Maximum Matching in Graphs* (1986), for
the algorithmic reference. NetworkX developers retain their BSD license;
no NetworkX algorithm source is copied into this package. A scoped profile
hook reads its final dual variables during optional discovery. Default
verification uses only the resulting integers and the elementary proof in
PROOF.md, with no NetworkX import or solver trust.

**PR915**, `e9daefe320a0043000bd9746664ed02c3287d056`, provides this
contributor's frozen R439 target basis. **PR926**,
`0f216a345c37bc71cc0e22030ef11ec31b26a69e`, provides the immediate greedy
two-sided comparator and harness. Their word/recipe/proof/notice snapshots
are retained verbatim. PR926's receipt is also retained. I/O, package tests,
native-runner structure and the identified circuit-checking routines are
adapted from PR926; its native harness follows **Sagar Thakrar's
`research/r420-decoder-sharing/native.py`** pattern. The new runner executes
all five words and distinguishes the floor calibration's failed nine-stage
invoice cap from its passing local native checks.

**Scott Woolsey Biggart**, PR733 and PR713, retains credit for two-sided and
target-basis factoring and the explicit mixed-term obligation; **Greer
Guthrie**, PR694, for disjoint helper bases; **Mikhail R. Gadelha**, PR686,
for the semantic D boundary and restored helper pair; **commdata2338**,
PR794, for guarded target-basis nomination; **Dugongue**, PR476/478 and
earlier PR450, for target-factoring precedents. **navinor**, PR848, records
the unchanged-H2 barrier which this semantic contract explicitly replaces.
Their full lineage and disclosures remain in the parent notices. Relative
links in archival documents refer to their original packages; those source
manifests are preserved for provenance, not treated as imported dependencies.

The baseline and changed words derive from **DreamingOfClouds's PR589**
(`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`) on **eumemic's PR555/543**.
DreamingOfClouds disclosed Claude Opus 5.5 through Claude Code; eumemic's
retained notice discloses Anthropic Claude assistance. Their Apache-2.0
notices and licenses are immutable source inputs, with transport credit to
Dugongue and Rohan Arun. LICENSE here follows that source lineage.

The unmodified native tools retain **Dylan Crow / utcorvusvolat-dotcom**
(PR370) for exporter/staging/checker lineage, **DaysSky** (PR381) for bridged
columns, **Zhihao Chen / jacklightChen** (PR386) for the portable header and
common-label interface lineage, **DreamingOfClouds** for nine-stage accounting,
and **Chafik Boukhalfa** and the other credited hosting/audit contributors.
Their original AI disclosures remain in the pinned notices. **Niels Lohmann
and contributors** retain the MIT header in `json.hpp`; **Jacob Sussman**
introduced the E8 unit.

No priority is claimed for matching, its dual inequalities, basis factoring
or semantic substitution. Exact sources, the finite contribution and the
remaining integration work are recorded separately.

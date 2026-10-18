# Local task card — agent-52 (written before substantial computation)

Task ID / proposed scope key: `connector-alphabet-change` (drawn), refined scope key
  `connector-seven-source-duo-full-coverage`; package `research/connector-seven-source-duo`
Base commit: 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (origin/main); selected-record
  SHA-256 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32;
  catalogue SHA-256 d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7;
  priority revision 4; chooser OS seed 4e177efb421addcdb3ba4ff20efdaefd; track
  `recursive-interfaces`.
Exact predecessors (heads): research/universal-connector-boundary (merged, PR943 lineage,
  Ross Richardson); research/universal-connector-six-source (merged; f(6)=16,
  18 <= f(7) <= 24); research/duo-toggle-connector (merged; DUO alphabet, (10,12) at n=5);
  PR 2128 head 697369a971eed02c0fbcd75ebefec9f59945f08e (six-source DUO (14,16);
  branch research/agent-41-connector-six-duo-f6e1088f, Aaron Wang/Navinor lineage);
  PR 2156 head 05b4672fa4450ef50b06315e3a0893d4ba43d42d (six-source DUO batch optimum
  (140,142); r[(C2)^6]=14 after Gavrylkiv, JIS 20 (2017) Table 3); PR 2249 head
  0c6ed7958435... (high-arity toggle cost floor).

Concrete object and question: the prefix-walk model of
research/universal-connector-boundary (closed walk q_t on F2^7, steps of weight 1
[singleton] or 2 [charged DUO], paired readouts realize D(w) = {q_s xor q_t}; universal
iff D(w) = F2^7). Question: what is the shortest universal seven-source word in the
singleton+DUO alphabet, and does the DUO extension yield a *favorable completed budget*
for the all-127-row seven-source batch, i.e. fewer root queries at no more toggle-adds
than the merged singleton upper bound f(7) <= 24 (Gray word, 24 calls, 24 adds)?

Scope status: changed (recorded). The card asks for one added operation family; DUO is
already added and priced (research/duo-toggle-connector, PR 2128). Keeping the alphabet
and increasing the source count to seven is the card's declared scope-change trigger.
Why the new question still matters: the DUO extension is proven favorable at n <= 6 and
untested at n = 7, the first source count where the universal word is superlinear
(18 <= f(7) <= 24, heuristic-only above 22). This is the card's acceptance question at
the next unsaturated boundary.

Existing restriction being changed: none of the frozen hypotheses (complete calls,
arbitrary dirty rows, restoration, paired readouts, read-only sources, charged DUO at two
adds). The changed axis is source count n = 7; the claim is about the DUO extension's
completed budget at that n.

Method; parameter domain: exact stdlib search over closed walks with steps of weight
<= 2 on F2^7 (equivalently: point sets P with P+P = F2^7 carrying a closed spanning
walk of weight-<=2 steps), plus exact verification of any witness (closure, per-label
parity, coverage of all 128 masks), exact batch bill (queries = k + 254, adds = W + 254
for all 127 rows), and the o/p tariff comparison against the singleton Gray word.
Positive controls (smallest falsifying instances first): n = 3 (5,6) and n = 5 (10,12)
DUO witnesses of research/duo-toggle-connector, the 945-pairing n = 5 singleton census
control, n = 6 (14,16), and the singleton Gray construction for n = 1..8 from
research/universal-connector-six-source.

Nearest overlapping PRs and why this adds something: PR 2128/2156 close six sources
entirely; nothing surveyed covers seven-source full-coverage (128-mask) words in any
combined alphabet. Discussion 2221 / PR 2236 / claim 18942820 (06:44Z) cover a
different object: the 63 weight-1/2/3 masks at seven sources with 14/18 singleton
events. find_overlap terms 'seven-source DUO', 'seven source', 'f(7)' (fresh complete
snapshot 06:47Z) returned no full-coverage seven-source claim.

Optimistic full cost budget: queries k + 254 and adds W + 254 for the all-127-row batch
vs singleton (278, 278). Favorable completed budget requires (k + 254, W + 254) to
Pareto-improve (278, 278), or a stated exact tariff condition o/p under which the bill
falls. Required observable improvement: k < 24 (call saving) with the full bill charged;
nothing is free (DUO pays two adds and one dispatch, as in research/duo-toggle-connector).

Success evidence; falsification test; cap: success = a literal universal word with exact
replay and full bill; falsification = if no word with k <= 23 is found within the search
cap, record best-achieved coverage per length as a scoped search failure (not an
impossibility result). Compute cap ~25 minutes of search.

Predecessor authors; intended artifact: Ross Richardson (PR934/943), Douglas Colkitt
(PR1185), Hanson Sun (PR1215), Aaron Wang/Navinor + opencode lineage (PR 2128, duo
line), PR 2156 author. Contributor: Aaron Wang, with help from opencode. Artifact:
research/connector-seven-source-duo/ with TASK.json, README.md (Open next questions),
SOURCES.json, VERIFY.json, verify.py, CERTIFICATE.json;
replay `python3 scripts/research_package.py --package research/connector-seven-source-duo`.

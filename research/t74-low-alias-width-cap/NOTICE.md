# Source notice

New work: Jeremy Diviney, with substantial OpenAI Codex assistance, Apache-2.0.

All bundled sources come from CrocSwap/integer-mult-bounds under the repository's
Apache-2.0 contribution terms. Exact commits, upstream paths and byte hashes
are in INPUTS.json.

- inputs/word80-{base,extra}.json.gz: unchanged PR2339 words by Sagar Thakrar,
  with Claude Code assistance; borrowing and compensation by Cinna Davis
  (PR2226), T74 adaptation by Jeremy Kothe (PR2269), and their credited lineage.
- inputs/pr2269-plan.json.gz: compressed copy of Jeremy Kothe's PR2269 plan;
  the original uncompressed bytes are preserved exactly.
- inputs/pr2269-profile.json: unchanged PR2269 attained profile.
- vendor/fine_moment.py: unchanged PR2322 directed integer moment engine,
  submitted by Vlado Vojdanovski; base-two directed-enclosure lineage retained
  in that package and the repository. Runtime precision constants are set by
  this package's verifier, which retains the same series and tail formulas.

verify.py's cost-invoice traversal follows PR2322 generate_words.py:paid_profile,
reimplemented with explicit GF(2)^9 subspace sets. The bin-pattern weak-duality
argument is standard linear programming; no novelty is claimed for that method.
The contribution is its exact, source-bound application to this fixed interface.

The original repository notice and PR2322 generator lineage notice are retained
verbatim at vendor/UPSTREAM-NOTICE and vendor/GENERATOR-NOTICE.txt. These are
source attribution, not claims that all of those packages are replayed here.
Apache-2.0 is included at vendor/LICENSE for standalone source exports.

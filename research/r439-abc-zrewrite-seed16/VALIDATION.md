# Completed validation

Base: 1b59b624d21924f8e3537cdc1ac52d3be6eda2fe. macOS; Python3.9.6;
Apple clang21; Boost1.87.0. Standard-library Python only.

- Discovery reached its stated fixed point in three rounds. A second run
  regenerated MOVES.json, SEARCH-LOG.json and CANDIDATE-WORD.json byte identically.
- `python3 -I -B research/r439-abc-zrewrite-seed16/verify.py` and its
  `-O` variant independently regenerate the complete certificate and pass.
  These checks cover all 55 occurrence-aware moves, all five phase maps,
  both complete 661-column dirty endpoints, literal cleanup, copied-center
  lifetimes, exact positive envelopes, strict caps, source/formula pins and
  eleven negative controls. A code-disjoint bitset replay is used; discovery
  code is not imported.
- `BOOST_INCLUDE=/private/tmp/boost_1_87_0 python3 -I -B
  research/r439-abc-zrewrite-seed16/native.py --output NEW_DIRECTORY`
  passes, freshly exporting both words and compiling four native binaries.
  The two completed runs' logs are at `/private/tmp/seed16-native-20261013-1956`
  and `/private/tmp/seed16-native-final-20261013`. Both agree on the committed
  NATIVE.json: all 883/1327/1549 columns, every frame path, actual paid rank
  histogram/mass 5129, copied-center lifetimes, exact prefixes and 96 rejected
  bridge controls. The driver also checks CERTIFICATE.json before native work.
- The concurrent PR1188 frozen word was independently replayed in both literal
  directions and repriced: 10492 ADDs and 175 nine-stage bits, versus 10542 and 174
  here. No sibling composition, GL5 BFS replay or unrestricted comparison is
  claimed. Exact comparison head and input hashes are recorded.
- All retained repository dependencies match the PR1122 source pins at this
  new base. Selected PR1094 certificate hash is guarded; upstream/ and the
  selected-result record have no modifications. Staged whitespace checks
  accompany publication.

Not run: selected hosted-supplier cold replay, repository-wide historical
suites, Linux execution, full analytic theorem formalization, independent human
review, PR1188's GL5 optimality replay or adoption of PR1194's pending semantic-D
proof. The new evidence is limited to this finite word, unchanged physical
invoice, exact local 104/nine 192 precision and the scoped sibling comparison.

# NOTICE - KB3k (research/f7-mu2-evenhalf-kb3k-88a1)

Author: Aaron Wang, with help from opencode (substantial AI assistance; no model
named; no independent human review claimed). Set-level only; no words enumerated.

## Predecessor credit

Every cited PR author was re-verified at writing with
`gh pr view NNN --json author,title`:

- [PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
  [PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
  [PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
  [PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870),
  [PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911),
  [PR 2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933),
  [PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961),
  [PR 3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023),
  [PR 3034](https://github.com/CrocSwap/integer-mult-bounds/pull/3034),
  [PR 3108](https://github.com/CrocSwap/integer-mult-bounds/pull/3108)
  (Aaron Wang / navinor): the 17-point exclusion chain, the pair-representation
  rows and odd-coverage Fourier/Parseval identity, the (A,D) reduction and
  vanishing-character restriction, the class floors and tight-class decisions,
  the (5,1) decision and its walk engine, the KB3i remainder (parity demotion,
  m=5 obstruction localization), and the KB3j mu2 lead and (4,2) walk this
  package presses and continues.
- [PR 943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) (Ross
  Richardson): the prefix-walk model.
- [PR 1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185)
  (Mister-Meeseeks): the pinned `f(5)=12`, `f(6)=16` record.
- [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691),
  [PR 2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973)
  (Nicholas Stone) and [PR 3005](https://github.com/CrocSwap/integer-mult-bounds/pull/3005)
  (Nick Petalas): the word-level census line and its correction (recorded state;
  PR 2973 leaves the set-level chain intact). Untouched here.

## Vendored engines (byte-exact, SHA-256 pinned)

`vendor/parity_census.py`, `vendor/selfsum_classify_kb3j.py`,
`vendor/tight.py`, `vendor/cover18.py`, `vendor/vanish.py`,
`vendor/agent64_cover17.py`, `vendor/agent64_search17.py`,
`vendor/anchors.py`, `vendor/self_obstruction.py`, `vendor/split_census.py`,
`walk42.py`, `run42.py` are vendored byte-exact from the predecessor packages
(PR 2773/2961/3023/3034/3108) via `agent_tools.py pr-tree-extract` and
`git archive`, with SHA-256 pins recorded in `SOURCES.json`. The pins are
enforced by `verify.py`. All credit is retained; no predecessor file is
modified.

## New code (this package)

`mu2_search.py` (mu2 identity + complete F2^3/F2^4 censuses + sampling),
`mu2_mechanism.py` (minimality + (4,4) mechanism census),
`mu2_odd_search.py` (both-odd hill-climbing cover search), `verify.py` (the
verifier). All exact Python integers (int bitmasks); no floats.

## Model and pinned results

PR943 query model (Ross Richardson); pinned `f(5)=12`, `f(6)=16` (PR 1185) and
the word-level gap `22 <= f(7) <= 24` (PR 2973/3005). Under that gap the
18-point question is the deciding necessary condition for `f(7) = 22`. This
package is SET-level only and enumerates no words.

## Concurrency

Nicholas Stone's f(7) WORD line (PR 2973) and Nick Petalas's corroboration
(PR 3005) are WORD level and untouched here. Pair-collision checks (discussions
1317 and 1166 via `agent_tools.py disc-comments --grep`, including nested
replies, before computation) found no live claim on the mu2 even-half condition
or the (4,2) walk. The parallel autoresearch-pure session (another agent) is a
distinct object and untouched.

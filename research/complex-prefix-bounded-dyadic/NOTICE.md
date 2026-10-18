# Attribution and license

New work: Chris Pagolu (@AllStars101-sudo), with substantial OpenAI Codex
assistance in mathematical analysis, code, verification and writing.
Apache-2.0, under the repository's [LICENSE](../../LICENSE).

`vendor/pr696_lower.py` is retained **verbatim** from Sagar Thakrar's
[PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696), commit
`5a3f983715027c4fd83f50bc9001d4b18463bed1`, path
`research/complex-dyadic-lowering/lower.py`. Its original Apache-2.0 and
substantial OpenAI Codex assistance notice is retained. That work supplies the
copy/unit optimization; this package claims only the additional bounded
signed-digit saving. The comparison is with that exact pending implementation,
not a maintainer acceptance of PR696.

The unchanged selected finite sources retain these predecessors' credit:

- Jeremy Kothe / AtomScout's #622 K-triangle construction and #623 dispatch,
  including the disclosed Claude Code construction work.
- Chafik Boukhalfa's #626 owner repair, source package and independent checks.
- icekylinx's #425/#433/#531 scalar primitive, common-frame and direct-delivery
  lineage, including disclosed Codex assistance; the dyadic microcircuits in
  eumemic's #411 are earlier related work.
- DreamingOfClouds' native/emitted audits and cold-helper construction, Dominik
  Scholz's prefix work, Rohan Arun's #559 recurrence correction, and the other
  contributors retained in the [selected review](../../docs/research/community-k492-review.md).
- eumemic's unchanged #543 bit supplier and its predecessors.
- Rohan Arun's campaign-100 signed-digit negative result, which remains valid
  for its paid-climb scope.

Concurrent #681 (Alluri), #687 (Charles Bethin) and #698 (Sagar Thakrar) helped
identify overlap boundaries. Their code and pending mathematical results are
not dependencies. Sagar Thakrar's concurrent #723 independently applies signed
digits to JP8 with a slightly larger prefix envelope; that discovery retains
credit. This package adds the strict prefix-bounded recurrence, unchanged exact
envelopes, CK coverage and an independent graph check. @ellipsi2's #722 instead
shares preparation across macro boundaries. Neither pending implementation is
imported or verified here, and no combined saving is claimed.

This contribution has no delegated-agent or independent human review claim.
Existing source-specific notices and licenses are retained.

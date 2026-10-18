# Attribution and license

Contribution by **Aaron Wang**, with help from opencode (substantial AI
assistance in scoping, implementation, verification and writing; no independent
human review claimed). New work is Apache-2.0, under the repository LICENSE.

The model and the prefix-difference reduction are **Ross Richardson's PR943**
(`research/universal-connector-boundary`). The pinned five- and six-source
censuses, the values `f(5) = 12`, `f(6) = 16` and the recorded `f(7)` gap
`18 <= f(7) <= 24` are **Douglas Colkitt's**
(`research/universal-connector-six-source`, https://github.com/CrocSwap/integer-mult-bounds/pull/1185),
which extends PR943. Both are read and reproduced here, never imported: no
predecessor executable is vendored or called. Exact pins are in `SOURCES.json`.

The community five-bit nine-point census fact (all 7,888,725 normalized
nine-point sets of `F2^5`, maximum pair coverage 29, no cover) was published in
the DUO-line coordination thread
(https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18931315);
this package re-derives it independently as a control and credits that source.

The DUO pair-source alphabet work
(https://github.com/CrocSwap/integer-mult-bounds/pull/2396,
https://github.com/CrocSwap/integer-mult-bounds/pull/2128,
https://github.com/CrocSwap/integer-mult-bounds/pull/2156) and the sparse
weight-1/2/3 mask family
(https://github.com/CrocSwap/integer-mult-bounds/pull/2229,
https://github.com/CrocSwap/integer-mult-bounds/pull/2236,
https://github.com/CrocSwap/integer-mult-bounds/pull/2397) are distinct scopes,
recorded in `SOURCES.json`. Nothing here changes the selected frontier, any
supplier or kappa.

# Cycle 23 task card

- Track: `recursive-interfaces`
- Accepted OS seed: `98c45ff6de908e57187a43e63c8d80e3`
- Task ID: `joint-query-controller`
- Catalogue method: `Add one explicitly priced ordinary-to-selected observation and derive the ordered two-call map and inverse.`
- Selector scope key: `22e535909f1d243e7553`
- Refined scope: one affine 8-coordinate helper `H' = H + (B0 + M B2) X_U + c`, with arbitrary rational `M` (8x8), offset `c`, and common dirty pre-state `H`; fixed QQ16 `F0/B1` pair and existing standard observation set.
- Refined scope key: `af861a56b365ef79f151`
- Scope status: changed. The candidate replaces an isolated B2 read or a separate B0 read with one compressed mixed B0/B2 helper; arbitrary matrix mixing and a shared affine offset are allowed. This asks whether the proposed cheaper 8-coordinate interface can preserve injectivity.
- Priority revision: 4
- Catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`
- Exact base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
- Selected-result reproduction: `make frontier1094-verify`

## Question and bounded method

For every `M in Q^(8x8)`, does the fixed-controller observation map become injective when its standard observations are augmented by only `H'` above? Use the exact QQ16 route operators `B0,B1,B2` and the already-reviewed witness/trajectory. The bounded domain is the complete rational 8x8 matrix family, arbitrary rational offset, and arbitrary shared helper pre-state; fixed `F0/B1`, schedule, and observation cut.

Use the source-pinned stack-rank inequality `rank[B0;B1;B2] >= 144|G|/7`. Since `rank[B0+M B2;B1] <= 16|G|` and adjoining `B2` recovers the same row span as `[B0;B1;B2]`, an exact kernel dimension argument should either produce a lost direction with `B2 h != 0` for all `M`, or expose a failed premise. Apply the selected-output witness to that direction. Stop after exact derivation and source-pinned checks; do not enumerate matrices or broaden to multiple helpers/changed maps.

## Optimistic full cost and outcome gate

Grant the one 8-coordinate helper, the mixed source read, frame and address conversion, forward update, inverse/restoration, dirty-state handling, hosting, and recursive precision all for free. This zero-paid-cost envelope is deliberately more favorable than any implementable invoice. If injectivity still fails, stop and report no cost improvement or `kappa` change. If it succeeds for any `M`, derive the exact map and inverse and then invoice every operation before considering a controller claim.

## Overlap and predecessors

- PR #2079, head `49df8190b158e3028e702b2c6b798117006f7249`: B2-only pre-F0 observation of the eight-direction witness family.
- PR #2104, head `4bdc574da394a39f955e8cf4637075649c43a632`, exact base current: quantitative residual after the B2-only read, including the stack-rank bound.
- PR #2093, head `8b21a900eb520e4f11ea177b310f66316f8e8983`: qualitative three-port witness across nonzero charts.
- PR #2086, head `68dcf180ce3918a9ee1998bfc5455f42516c6009`: changed A-logger boundary.
- Discussion #2074 also contains the completed 252-pair first-forward catalogue, which leaves affine helper state outside its scope.

This scope is the exact one-helper mixed `B0+M B2` interface; it adds a dimension bound over all rational `M`, rather than repeating the B2-only query or first-pair catalogue.

## Deliverable and stopping rule

A small proof package with the all-`M` rank argument, exact pinned dependencies, a standard-library replay of the dimension/corollary arithmetic, positive and mutation controls, and an explicit statement that the result is a scoped obstruction rather than a native cost or `kappa` result. Recheck board overlap before submission. Claim expiry: `2026-10-14T21:50:00Z`.

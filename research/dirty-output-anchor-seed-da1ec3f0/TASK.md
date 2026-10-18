# Cycle 14 scope: two-sided compensation from a dirty product anchor

## Assignment and pins

- Track: `recursive-interfaces`.
- Accepted OS seed: `da1ec3f0e25e84544b9ea1499a0155f2`.
- Catalogue task: `persistent-boundary`, priority revision 3.
- Exact base commit: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Scope key: `persistent-boundary / dirty-anchor-two-sided-fanout-q2-112`.
- Scope status: refined; the seeded pair-restoration question is specialized to a shared bilinear term across arbitrary-dirty outputs.

## Object and question

For `q` arbitrary dirty output coordinates `A_0,...,A_(q-1)`, suppose each required output is

```text
A_i' = A_i XOR p(x,y) XOR t_i(u_i,v_i),
```

where `p` is one common bilinear product and each `t_i` is a private product of read-only operands disjoint from every target. Can `p` be computed once and fanned out without requiring any clean output or helper coordinate, while preserving the exact dirty-input map?

The direct schedule uses `2q` complete rank-one child calls. The candidate uses two XOR fanout waves around one child call into the dirty anchor `A_0`, followed by the `q` private child calls:

```text
for i=1..q-1: A_i ^= A_0       # old dirty anchor
child:        A_0 ^= p
for i=1..q-1: A_i ^= A_0       # updated anchor
for i=0..q-1: A_i ^= t_i
```

The first two waves send `A_0(old)` and `A_0(old) XOR p` into every other target, so each target receives exactly `p` and its original dirty value is preserved modulo the requested update. The whole map has `q+1` child calls and `2(q-1)` full output-coordinate XORs. The inverse is the reverse sequence with every child XOR oracle reversed. With one common child and only target-row XORs, a Hamming-weight argument proves that `2(q-1)` row ADDs are necessary and this schedule attains the minimum; the bound excludes helper/COPY/CLEAR and other whole-register operations.

## Changed assumption and domain

The changed contract permits an arbitrary-dirty output coordinate to serve as the anchor when its original value is compensated on both sides of the shared child call. No clean anchor, private helper, child uncomputation, input copy, or frame change is allowed or needed. The bounded parameter range is `q=2..112`; the package exhausts width-two oracle values for `q=2..4`, width-one values for `q=5`, and proves the symbolic identity for every declared `q`.

This is distinct from PR #1907's clean required-output anchor and PR #1872's clean helper that is later uncomputed. It is also distinct from PR #1930's three-stage linear prefix composition and PR #1917's cross-fed parity connector comparison. The closest new related claim is Discussion #1167 comment 18926048: it uses a separate dirty scratch row and a repeated common linear map across distinct source-prefix values. This scope instead uses a required output row as the carrier for one shared bilinear product, has private per-output products, uses no scratch or cleanup, and proves the minimum row-XOR count for that one-child boundary. The coordination claim is https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18925817.

## Optimistic complete cost screen

Let `mu` be the fully charged cost of one common rank-one child and `alpha(w)` the full cost of one width-`w` output XOR. Direct cost is `2q*mu`. The candidate cost is `(q+1)*mu + 2(q-1)*alpha(w)`. Its exact saving is

```text
(q-1) * (mu - 2*alpha(w)).
```

At the selected 112-port profile, eight hypothetical blocks replace 888 rank-one children (`n1: 2412 -> 1524`) and add 1,776 explicit scalar output XORs at width one. The matching rank-only ceiling screen is conditional and does not absorb those XORs: they are carried as the separate linear term in the recurrence. Under the selected superlinear multiplication exponent, a width-linear term is lower order; this is a mechanism screen only until an actual source-pinned block occurrence is found. No selected-provider mapping, new `kappa`, or frontier improvement is presumed.

## Evidence and stop rule

Success evidence: exact symbolic identity for all dirty target values; exhaustive Boolean replay and inverse checks for `q=2..5`; negative controls omitting either fanout wave or the shared child; exact child and affine-operation receipts; pinned moment calculation and package validation. Stop if the full cost comparison fails for the declared child/affine model, or if the conditional moment fails after charging the additive linear term. Do not infer a provider occurrence from the abstract map.

Nearest work: PR #1872 (`626ce207ec92a76f70a84843fe4ce3c39f67899d`), PR #1907 (`49b870f7a64f5f414208c3a82d4483b9cc95f5b8`), PR #1917 (`ee4d821c233f1072e99a5557c7001cd1dc20fa11`), PR #1930 (`11cb2266f7e99279c440a301ea4b862587a9afa2`), and Discussion #1516's fixed-frame centre-path scope. Their limits and the changed dirty-anchor premise will be disclosed in the contribution.

Prepared with substantial OpenAI Codex assistance. Apache-2.0. No selected-frontier change is claimed.

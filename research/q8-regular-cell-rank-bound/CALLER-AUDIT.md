# Selected-source caller inventory

## Binding and checked inventory

This audit is pinned to base main `463113d675af7410ac91d53a4fed51ec6494eb9a`
and `research/community-frontier1094-audit/SELECTED-SOURCE.json` (its raw file
SHA-256 is in `SOURCES.json`). That manifest names these 13 selected package
roots:

```text
research/complex-sw4-frame8
research/e8-bit-p111-tuned
research/e8-bit-carrier-skeleton
research/direct-delivery504-global
research/gauge44-frames-x
research/complex-t21-owners
research/complex-t21-owner-bound
research/complex-t37-owners
research/gauge44-leaver
research/gauge44-leaver8
research/gauge44-slots
research/gauge44-slots-t16
research/complex-t16-rare-pattern-exchanges
```

The search was limited to files named `README.md`, `TASK.json`, `FRONTIER.md`,
`FRONTIER.json`, and `PROOF.md` files, with case-insensitive terms `Q8`,
`quaternion`, `eight-address`, `8-address`, `address ... block`, and
`block ... address`. From the repository root, rerun:

```sh
roots=$(jq -r '.package_roots[]' research/community-frontier1094-audit/SELECTED-SOURCE.json)
rg -n -i 'q8|quaternion|eight[ -]address|8[ -]address|address.{0,24}block|block.{0,24}address' \
  $roots -g 'README.md' -g 'TASK.json' -g 'FRONTIER.md' -g 'FRONTIER.json' -g 'PROOF.md'
```

It returned no matches. This means no caller is named in the searched documents;
it is not proof that no code-level implementation or unlisted caller can exist.
The search did not enumerate every source file, every derived call graph, or
every open pull request's full diff.

## Related open work

At the refresh on 2026-10-17, PR #2235 was open at head
`e5a5d0651003e8774e98121250203b35c236b02b`. Its description presents verified
multitape machinery and a quadratic multiplier, and explicitly says that
serialized-input, alphabet, and full-cleanup bridges needed for a generic caller
remain missing. No Q8 address map or selected-supplier price is stated there.
That open PR is relevant interface work, but it does not fill this package's
caller contract. This exclusion is a comparison with its recorded scope, not a
claim that the full PR is mathematically reviewed.

Recent open PRs #3296 and #3311 also mention an eight-stream/`8 x 8` operator.
At checked heads `6f78fe217ed63ef84096d53ed3651b38bab81e15` and
`32a3fa83aaa639570db53beb381016711aa6f5b5`, respectively, they concern a
Gaussian-integer Fourier operator `i I_8` and an exact audit of two specific
P112 remainder transfers. That is not the binary Q8 regular permutation
`P_g` on eight arbitrary payload blocks used here, and neither PR supplies a
Q8 caller. This is a scope comparison from their descriptions, not a review of
their complete proofs.

## Exact missing interface

A caller would need to identify: (1) the eight contiguous equal-width address
blocks and their ordering, (2) the active role coupling `u,v` with `v^T u=1`,
(3) all dirty inputs and restored spectators, (4) chronological ownership/cut
constraints, (5) payload width `B`, (6) the native cost of every data and
transport instruction, and (7) the complete direct alternative it replaces.
Until that binding exists, the `4B/6B` theorem prices only the stated
rank-one-bit-cell alphabet. It cannot be converted into a selected child count,
supplier saving, or κ change.

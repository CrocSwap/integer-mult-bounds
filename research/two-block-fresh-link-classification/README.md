# Classify arbitrary-width fresh links on two binary blocks

The one-link model in [PR #7648](https://github.com/CrocSwap/integer-mult-bounds/pull/7648)
has a complete irreducibility test when both fresh factors are nonzero.
The two core factors must both equal the sum of the fixed block hubs,
and the fresh factors must have odd inner product. Disjoint fresh
supports cannot work. With r fresh coordinates there are exactly
`(2^r-2)*2^(r-1)` nonsymmetric positive links: four at width eight.
All positive links give the same action on their seven-dimensional
joint image, despite their different coordinate supports.

This is a scoped all-width proof with exact finite corroboration. Read
[PROOF.md](PROOF.md), [verify.py](verify.py) and [RESULT.json](RESULT.json).
The positive complete pool has seven projectors and a five-dimensional
unit-free pattern space. Some negative cases have an eighth projector,
so completeness is checked separately from the displayed generator list.
No new kappa or selected-assumption discharge is claimed.

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -I -W error -B research/two-block-fresh-link-classification/verify.py
python3.12 -I -W error -B -O research/two-block-fresh-link-classification/verify.py
python3.12 -B scripts/research_package.py --package research/two-block-fresh-link-classification
python3.12 -B scripts/check_research_commit.py --package research/two-block-fresh-link-classification --check-source-history --check-modes
```

Expected markers are PASS_TWO_BLOCK_FRESH_LINK_CLASSIFICATION,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The verifier scans all 40768 rank-one idempotents across widths seven
and eight. All 20605 candidate links get a complete-pool check and an
exact irreducibility or invariant-subspace certificate. It checks 889
positive census orbits, the source witness, a valid disjoint-fresh
negative, the eight-projector degenerate case and five controls.
No predecessor scientific replay, selected cold replay, Lean or Docker
run is required or claimed. Independent human and formal-kernel review
remain open. There is no external run-time input.

## Task and scope

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8, with selected PR #7000 unchanged. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19702706)
takes the released PR #7648 classification handoff. The source's square
family and single nonsymmetric witness are predecessors, not new results.
The overlap check covered open and closed PR bodies and Discussions;
sparse local notes and unpublished work remain coverage limits.

The `bit-new-register-model` card is explicitly changed to this structural
side question. No new operation alphabet or paid BIT word is supplied,
so that original construction gate remains unmet. General five-dimensional
pattern spaces, a zero fresh image/covector factor, and multiple links
are outside the theorem. [TASK.json](TASK.json) records this boundary.

## Open next questions

Can an irreducible seven-dimensional image arise from a five-dimensional
pattern space that does not contain these two fixed blocks? This would
change the action rather than only its coordinate support. Start with
one complete normal-form triple and test whether a second disjoint one
is forced. No structural reduction for that broader class is supplied
here. A paid word and a complete physical invoice remain separate tasks.

## Credit and exact sources

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Nick Petalas supplied the nonsymmetric witness and classification question
in [PR #7648's source](https://github.com/petalas/integer-mult-bounds/blob/f967555200c111925d48a46b65b124432a762b65/research/no-edge-asymmetric-block-link/README.md).
unpaidmoon supplied the square family and fixed-block model in
[PR #7281's proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/0cd5324c41490b856d0e94daa8b011683fc153f6/research/no-edge-dim5-fresh-link/PROOF.md),
building on [PR #7237](https://github.com/CrocSwap/integer-mult-bounds/pull/7237)
and [PR #6921](https://github.com/CrocSwap/integer-mult-bounds/pull/6921).
The source complete-pool method credits Nick Petalas's
[PR #5921](https://github.com/CrocSwap/integer-mult-bounds/pull/5921).
The special base-pool calculation is derived again here. No predecessor
code was copied. Sources are contextual citations; the proof and executable
are self-contained. New work is Apache-2.0.

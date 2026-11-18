# Classify kind B removal by frame exchange

For every address width, a nonplain kind B part can be removed from
an admissible other-array last call exactly when the call exchanges
its two frames and the coefficient is +1 or -1. This proves both
directions of the rule posed in
[PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629).
The proof gives the actual free preparations in an even alternating
cycle. Exchanging only one frame is insufficient.

Read [PROOF.md](PROOF.md), [verify.py](verify.py) and [RESULT.json](RESULT.json).
This concerns `y=WD+cW gamma`, with gamma free, c nonzero rational,
`level(WD)=level(TW)=2` and `W gamma` outside the first-call frame PD.
It does not classify finishing or joint decoding. There is no new kappa.

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -I -W error -B research/kind-b-frame-swap-removal/verify.py
python3.12 -I -W error -B -O research/kind-b-frame-swap-removal/verify.py
python3.12 -B scripts/research_package.py --package research/kind-b-frame-swap-removal
python3.12 -B scripts/check_research_commit.py --package research/kind-b-frame-swap-removal --check-source-history --check-modes
```

Expected markers are PASS_KIND_B_FRAME_SWAP_REMOVAL,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
All 10752 three-bit free elements and all 48 admissible calls are
examined. After the 768 plain cases are excluded, all 479232 pairs
receive a missing-coefficient certificate or an exact cyclic-span check.
Across five coefficients this covers 2396160 contracts. The 512 exchange
pairs work only at the two signs and give 128 distinct removable parts,
consistent with the predecessor's finite count. There are also 150 wider
full-span checks, five boundary controls and two linear-solver controls.
No external run-time input is used.

Predecessor scientific suites, selected cold replay, Lean and Docker
were not run. Independent human and formal-kernel review are unclaimed.
The theorem supplies no phase lift, native supplier or complete invoice.

## Task and scope

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`,
priority revision 8, with selected PR #7000 unchanged. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19703259) takes the source's kind B question. The card
`complex-rank-shape-decoder` is narrowed to this formal-frame theorem.
The source's kind A finishing and removal results concern a different
placement of gamma and do not classify this part.

The expansion decision keeps a bounded proof task. The completed
obligation is the arbitrary-width removal criterion. Physical delivery,
precision, restoration and a full signed invoice remain unpriced, so
no construction margin follows. The overlap search covered open/closed
PR bodies and Discussions; sparse local files and unpublished work
remain coverage limits.

## Open next questions

Can the frame-swap identities be used in a joint decoder without losing
the other input's target? First put both input parts and both last-call
outputs in the same formal system, with their shared preparations
explicit. The single-part removal identity does not answer this.
A Pauli-phase lift and complete physical costs are further obligations.

## Credit and exact sources

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Jacob Sussman supplied the definitions, finite evidence and frame-swap
question in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629),
[exact source](https://github.com/jacobalansussman/integer-mult-bounds/blob/c2a2131e7dba35f9396b16588e125a7e8b5fab8e/research/complex-m3-shared-call-finish-or-remove/README.md).
Nick Petalas supplied the related coset finishing method in
[PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649),
[exact proof](https://github.com/petalas/integer-mult-bounds/blob/f642d2740265a61f8ac64b3a087f0118382c56e3/research/kind-a-last-call-coset/README.md).
Ali Romman's kind A removal proof is
[PR #7677](https://github.com/CrocSwap/integer-mult-bounds/pull/7677),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/2bb938975cf34de19d1e1db820f4c9b42c486cb4/research/kind-a-removability-coset/PROOF.md).
The source credits the original frame geometry in
[PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628)
and [PR #4743](https://github.com/CrocSwap/integer-mult-bounds/pull/4743).
These are contextual sources. The new proof states its definitions
and the verifier uses binary row matrices. New work is Apache-2.0.

# Prove the kind A removal rule at every address width

A kind A shared-call part can be removed from an admissible other-array
last call exactly when its middle terms have the same frame and its
cyclic binomial is singular. This proves the removal half of Jacob
Sussman's rule in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629).
Nick Petalas already proved the complementary finishing half in
[PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649).
Together, their opposite tests exclude simultaneous single-output
finishing and removal in this model, with any number of spare bits.

Read [PROOF.md](PROOF.md), [verify.py](verify.py) and [RESULT.json](RESULT.json).
The theorem requires `level(TW)=2`, where W is the shared call and T is
the removing call. Four exact distinct-frame counterexamples with
`level(TW)=1` show why that restriction matters. This is a scoped proof,
not an exclusion of all 2-in-5 programs. There is no new kappa.

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -I -W error -B research/kind-a-removability-coset/verify.py
python3.12 -I -W error -B -O research/kind-a-removability-coset/verify.py
python3.12 -B scripts/research_package.py --package research/kind-a-removability-coset
python3.12 -B scripts/check_research_commit.py --package research/kind-a-removability-coset --check-source-history --check-modes
```

Expected markers are PASS_KIND_A_REMOVABILITY_COSET,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The verifier builds all 10752 free elements at three bits and checks
43008 coefficient contracts by rational span membership with complete
literal coset sets. The nonplain counts are 639, 767, 0 and 0 for
c in {1,-1,2,1/2}. These counts corroborate the predecessor's finite
table; the new result is the all-width proof. It also checks 1407
explicit deletion relations, 150 wider contracts by a separate membership
route, and five boundary controls. There is no external run-time input.

Predecessor scientific suites, selected cold replay, Lean and Docker
were not run. Independent human and formal-kernel review are unclaimed.
No Pauli-phase lift, native implementation or full invoice is supplied.

## Task and scope

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`,
priority revision 8, with selected PR #7000 unchanged. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19703032) takes the source's open removability question.
The card `complex-rank-shape-decoder` is narrowed to that formal-frame
question. No complete decoder or native reduction is claimed.
The overlap check covered open/closed PR bodies and Discussions. Sparse
local files and unpublished work remain coverage limits.

## Open next questions

Does a joint decoder of both last-call outputs evade this separate
finish/remove conflict? First project both output families for a fixed
three-direction setup with one spare bit, while retaining the shared
preparation constraints. The present theorem treats one part and one
removing call. It supplies no joint-decoder obstruction. Kind B and
post-call free processing also remain separate questions.

## Credit and exact sources

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Jacob Sussman defined removal, gave the finite rule and posed the
all-width question in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629),
[exact source](https://github.com/jacobalansussman/integer-mult-bounds/blob/c2a2131e7dba35f9396b16588e125a7e8b5fab8e/research/complex-m3-shared-call-finish-or-remove/README.md).
Nick Petalas supplied the coset method and finishing theorem in
[PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649),
[exact proof](https://github.com/petalas/integer-mult-bounds/blob/f642d2740265a61f8ac64b3a087f0118382c56e3/research/kind-a-last-call-coset/README.md).
The original frame geometry context includes
[PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628)
and [PR #4743](https://github.com/CrocSwap/integer-mult-bounds/pull/4743).
Sources are contextual citations. The proof states all needed definitions
and derives the required geometry. No predecessor code was copied.
New work is Apache-2.0.

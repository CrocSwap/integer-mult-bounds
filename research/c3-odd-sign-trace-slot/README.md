# An odd minus on u keeps the X_3 trace -48

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

On the explicit c=3 pair from the sign-split certificate, `X_3` has trace
`-48` on the trivial `(+1, +1)` joint space. Adding the minus sign on
coordinate 1 to `u`, and leaving `v` and the even signs unchanged, keeps that
trace on the eigenvalue `(+1, +1)`. The same holds for every odd sign added
to this `u`. The selected conditional kappa stays `781451/250000000`.
[PROOF.md](PROOF.md) separates the trace-formula proof from the facts that
are not claimed.

## Result

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
The unvaried pair is

    u = (0 2)(4 6) with minus signs on coordinates 0 and 2,
    v = (0 4)(2 6) with minus signs on coordinates 0 and 4.

Its product is `(0 6)(2 4)` with mask 65. The assigned variation is the
composition of `u` with the diagonal sign on coordinate 1. The new mask is 7,
the product permutation is unchanged, and the product mask is 67.

On the trivial character, the four joint traces of `X_3` remain
`-48, 16, 16, 16` for eigenvalues
`(+1,+1), (+1,-1), (-1,+1), (-1,-1)`. The value `-48` remains on
`(+1, +1)`. That space still has dimension 216, so the `X_3` eigenvalues
there are still dimensions 84 and 132. The same four traces occur for all 16
diagonal signs supported on `{1, 3, 5, 7}`, with this `v` and these even
signs held fixed. The verifier enumerates those 16 signs, the 16 characters
of `H`, and all 512 addresses.

The sign change moves a different trace. On the weight-1 character that is
`-1` on coordinate 1, the trace 36 and the dimension 180 move from
`(+1, +1)` to `(-1, +1)`. The value `-48` does not occur on that character.
The weight-1 character supported on coordinate 3 keeps the unvaried row
`(36, -12, -12, -12)`.

This is a proof. The address counts are exhaustive on 512 elements, once by
enumeration and once by an affine solve, and the two counts agree. The odd
signs are all `2^4` subsets of the four odd coordinates. It is not a stopped
search, and it is not a claim about every cross-coset pair.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The live question is open question 2 of
[PR #7020](https://github.com/CrocSwap/integer-mult-bounds/pull/7020),
recorded in discussion comment
[19514155](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514155).
The first step named there is to repeat the trace with one odd minus sign
added to `u`. The masks and the unvaried pair come from
[PR #6965](https://github.com/CrocSwap/integer-mult-bounds/pull/6965).

This package does not redo the payload-involution split. It does not compute
the characteristic polynomial of the 84-dimensional subspace, and it does not
factor the degree-16 weight-4 polynomial of
[PR #7021](https://github.com/CrocSwap/integer-mult-bounds/pull/7021).
The mask of `v` stays 17. The other legal even-cycle pattern, minus signs on
coordinates 4 and 6, is not evaluated.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c3-odd-sign-trace-slot/verify.py
python3 -B -O research/c3-odd-sign-trace-slot/verify.py
python3 -B scripts/research_package.py --package research/c3-odd-sign-trace-slot --check-only
```

The direct marker is `PASS_C3_ODD_SIGN_TRACE_SLOT`. Acceptance uses explicit
checks, so `-O` does not skip them. On the measured host the direct run takes
about two seconds. No Lean, Docker, degree-881 coefficient replay, or
selected cold replay was run.

## Overlap

`scripts/find_overlap.py` was refreshed on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Coverage: local notes 10178 of
10178 HEAD paths, complete; 339 open PRs, pagination complete, fetched
2026-11-10T10:28:46Z; 7013 discussion records, pagination complete, fetched
2026-11-10T10:29:46Z. Closed PRs were searched through local READMEs, task
metadata and the ledger only. The search terms were `trace -48`,
`odd minus`, and `cross-coset`.

The matches are the predecessor statements and one unrelated use of the words
"cross-coset". PR #7020 records the trace `-48` and leaves other cross-coset
sign patterns unevaluated. PR #7021 asks whether a nontrivial odd-sign pattern
splits a degree-16 weight-4 polynomial; that polynomial is not this trace.
No open PR body reports the joint trace of `X_3` after an odd sign is added
to this pair. This search is not a novelty certificate.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- One odd minus added to `v`, with the mask of `u` held at 5, was not
  evaluated. The reindexing above uses a sign added to `u`. The smallest
  check is the same joint formula with the minus on coordinate 1 added to
  `v` instead.
- The other legal even-cycle pattern on `(0 2)(4 6)`, with minus signs on
  coordinates 4 and 6 and no odd minuses, was not evaluated. It is one of
  the 32 stabilizer patterns of PR #6965, and it is not an element of `H`.

## Credit

The explicit pair, the free odd signs, and the joint-dimension table are the
certificate in upstream PR #6965. The trace `-48`, the 84+132 split, and the
question answered here are upstream PR #7020, head
`6025743bc95e096845af0962ba0c4c37cce89c4e`. Krzysztof Wojt's
`research/exact-one-slot-gram/` defines `X_3`. Ali Romman's #4958 and #4720
retain the query and the Bell action. Nick Petalas's #5120 is the degree-410
lower bound. JoyboyBrian's handoff recorded the sign-character dimensions.
The doubled representation comes from #1719. New work is Apache-2.0.

## Workflow feedback

The named open question fixed the masks and named the one sign to add, so
the trace stayed a sum over the existing group of 64 operators.
https://github.com/CrocSwap/integer-mult-bounds/discussions/1200

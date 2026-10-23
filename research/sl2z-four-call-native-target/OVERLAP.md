# Overlap checks for the scoped SL2(Z) shear target

Assignment: bit-new-register-model, priority revision 6, selector scope key
7084092dd726e7ba1f2f, base commit
20ecf2891d80b5acf18d980b2164fb44ea7faa90.

## Cached search

Ran the assigned broad search:

~~~sh
python3 scripts/find_overlap.py --task bit-new-register-model --offline --cache /home/user/int-bounds-pass/20261018-luna-xhigh/overlap.json --limit 8
~~~

It returned POSSIBLE_OVERLAP_NOT_A_NOVELTY_CERTIFICATE. The cache covered
586 open PRs and 2,536 discussions, fetched 2026-10-19 UTC; the offline run
warned that live changes could be missing. The first relevant matches included
the [free-group commutator-pair claim #1997](https://github.com/CrocSwap/integer-mult-bounds/discussions/1997),
the [four-role UT5(Z) claim #2094](https://github.com/CrocSwap/integer-mult-bounds/discussions/2094),
and Q8/S3/S4 proposals. No conclusion of novelty follows.

A second cached query for S5, five-cycle and adjacent-transposition terms
found prior S_n work. The S5 route was dropped: [discussion #1740 comment
18928637](https://github.com/CrocSwap/integer-mult-bounds/discussions/1740#discussioncomment-18928637)
states the exact minimum for all diagonal targets in F2[S_n] using paid adjacent
transpositions and arbitrary dirty registers. [Discussion #1167 comment
18936078](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18936078)
records an eight-call minimum for the S5 inverse-5-cycle pair.

## Live handoffs and open PRs

Read the top-level Start here #1163, Handoffs #1166, and Mechanism proposals
#1167 through the GitHub API. The live handoff scan covered all 684 comments
in #1166 and found no SL2(Z), SL_2(Z), or integer-shear proposal. The latest
register-model handoff was [#1166 comment
19021147](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19021147),
the Q8 t<=2 sharpness result; its target, group and alphabet differ.

The current open PR search found related but distinct register-model work:

- [#3774](https://github.com/CrocSwap/integer-mult-bounds/pull/3774), head
  713c28c1b0ebbdf3f30d7887fcb173e7a786f245, uses UT3(F4), four involution
  labels, and the three-output central target.
- [#3788](https://github.com/CrocSwap/integer-mult-bounds/pull/3788), head
  595b9426cc2fac34d31a71b24b98ed080f54c99a, adjoins the two w^2 labels to
  that UT3(F4) alphabet and retains the twelve-call minimum.
- [#3800](https://github.com/CrocSwap/integer-mult-bounds/pull/3800), head
  5e4d41cb0e99e4773abca244cdc8c376686421b8, independently reconstructs that
  UT3(F4) model and performs a bounded shorter-word search.
- [#3783](https://github.com/CrocSwap/integer-mult-bounds/pull/3783) records
  the twelve- and fourteen-call UT3(F4) central words without a shorter-word
  search.
- Open PR searches for SL2(Z), SL_2(Z), and opposite elementary matrices
  returned zero results. Search for integer shear returned #3678, which checks
  a scatter inverse identity and invoices, not an address-group target.
- Reviewed predecessors #1974 and #2027, captured in the revision-6 review, cover a GL3(F2)
  census with a bounded third-role probe and a UT4(F2) mixed-root tariff.
  Their alphabets and address groups differ from the integer-shear group here.

These are overlap checks, not a novelty certificate. The exact minimum proved
here applies only to the stated generators and endpoint.

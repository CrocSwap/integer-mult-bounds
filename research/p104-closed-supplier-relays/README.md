# Paid relays on the closed P104 supplier

**Conditional κ ≥ 0.00385068874146** on the complete 48-call multiplier. This exceeds the directed upper endpoint of the strongest submitted precursor, PR #7767, by **0.00002253269229**, and Ali Romman’s stronger public 48-call supplier by **0.00001046690700**. Both 48-call words use the same signed rank tariff, original BIT bound 0.00385248 and finite compiler. The original target was 0.00383069832566. [Directed prices](evidence/price.json) · [Complete qualification](evidence/application.json)

| Construction | Native calls | Conditional lower | Directed raw crossing |
| --- | ---: | ---: | --- |
| Original #7761 comparator | 2,048 | 0.00382069832557 | 0.00382069832565–0.00382069832566 |
| Submitted base #7767 | 2,048 | 0.00382815604908 | 0.00382815604916–0.00382815604917 |
| Ali Romman’s released supplier | 48 | 0.00384022183437 | 0.00384022183445–0.00384022183446 |
| Two retained hubs and eight retained relay routes on Ali’s supplier | 48 | 0.00384601452746 | 0.00384601452754–0.00384601452755 |
| Joint word after 10 additional paid edits | 48 | **0.00385068874146** | **0.00385068874154–0.00385068874155** |

At 02:50 UTC on November 19, Ali independently reported that several #7767 bypasses already occur in his earlier journal. His later local graph crossed 0.00384886106116–0.00384886106117 on an older 1,024-call price. The author identified the released 48-call word at `6b0b2f7d` as his complete public artifact. The gain above uses that released comparison. [Parallel handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19721588)

## Construction

Reconstruct the submitted #7767 word `eb8a9cbf` from its public parent using #7767’s two published differentials. Reverse seven bypasses whose original route preimages have changed. This gives back fourteen rank-one legs and removes seven rank-two legs per native call. Rename eight internal bank identifiers while updating every dependent row. Adopt the two independent helpers and recoded banks of Ali’s released supplier, carrying forward two hub rebindings, their terminal repairs and eight 4+2→6 relay restorations. The ordered reversible patch records the preimage of every changed coefficient. Its inverse recovers #7767 byte for byte. A separate build from Ali’s `f30aece9` graph arrives at the identical full intermediate `126352b5`. [Bridge receipt](evidence/base.json) · [Retained edits](RETAINED-EDITS.json) · [Public #7767 source](https://github.com/CrocSwap/integer-mult-bounds/pull/7767) · [Ali’s source and proof](https://github.com/aliromman/integer-mult-bounds/blob/6b0b2f7de0f068834264fc50b75a39a72c52ea22/research/p104-dual-supplier-lift/complex/PROOF.md)

The final edits change paid scalar deliveries. For a source combination, substitute rational coefficients at the surviving sender so its unwanted contributions cancel at the observed terminal charts. Rebuild the useful observation from the newly priced route and available donors. The journal gives the actual senders, terminal pivots, substitutions, and full paid and scalar differentials. Rebuild them in order against each preceding state. The verifier enforces the old coefficients, acyclic availability, and the final digest. The independent forward and transposed calculations preserve all 400 main fields and all 864 independent helpers. [Ordered paid edits](PAID-EDITS.json) · [Arbitrary-input and CLEAR controls](evidence/rows.json)

At the first new edit, remove send 99771, recode funded sender 96048 with slope 4, and eliminate terminal pivot 104247. Paid leg 53 sends the restored value from chart 712 directly to chart 127. This exchanges ranks 2+3 for rank 5. The final three edits use a combination of two funded producers. The first retires identifiers 34 and 44. The last two allocate new paid lifetimes to those identifiers with different endpoints and coefficients. Omitting any one of the ten final repairs changes a named public output on a named input. [Ten exact omission witnesses](evidence/omissions.json)

The final native digest is `c048d660a0e77925a91597c3a554c736bab11d870c1753c2c35e5657a4974f48`. The full 48-call schedule contains 192 mixed roots, 120 homogeneous A roots and 384 B visits. Its 840,912 emitted records bind each physical port to the owner prescribed for that clock. The older 2,048-call and newer 48-call invoices are evaluated separately. [Source pins](SOURCE-LOCK.json) · [Signed caller readback](evidence/application.json)

## Paid, productive and ordinary costs

Ali’s supplier uses 5,720 native paid positions per call. The joint construction uses **5,702**. Its native paid-count changes are -7 at rank 1, -9 at rank 2, -11 at rank 3, -3 at rank 4, +4 at rank 5, +6 at rank 6, +2 at rank 7. Across the complete caller, the paid count moves from **283,776** to **282,912**, with the full productive histogram equal at **51,312** in both words. At 0.00384022183446 the candidate has a directed signed surplus of at least **10.74341781763620774160924998943188**. The raw crossing has opposite strictly directed signs at the two reported endpoints. [Both complete histograms and derivative bound](evidence/price.json)

| Ordinary charge for the full batch | Public supplier | Joint word | Change |
| --- | ---: | ---: | ---: |
| Scalar services | 1,255,425,024 | 1,257,699,840 | +2,274,816 |
| Elementary ordinary record allowance | 151,803,649,536 | 151,639,724,544 | -163,924,992 |
| Ordinary map slots | 1,600,224 | 1,598,496 | -1,728 |
| Guarded resets | 79,484,256 | 80,090,976 | +606,720 |
| Typed transfer legs | 21,365,088 | 21,512,448 | +147,360 |

The minimum product grid is 332,739,660,860,006,400, half the donor minimum. Both graphs use odd scale 40,617,634,382,325. Its factors 12,404,509 and 3,274,425 are charged on installation and removal. The physical run checks 12,141,870 coefficient products, 6,930,859 nontrivial exact divisions, full retirement and 5,056 integer conversion round trips. All 2,982 ordered chart pairs used by either word pass signed Pauli and absolute-phase tests. Dense forward and adjoint checks cover 27,648 Gaussian columns, and the entrance and return adapters cover all 104 real ports. A changed paid sign, a cyclic read, an occupied sender, a partially cleared home, a missing MOVE and an altered productive rank each trigger an independent rejection. [Complete physical and finite compiler receipt](evidence/application.json) · [Owner and CLEAR controls](evidence/rows.json) · [Paid and productive rank controls](evidence/price.json)

## Reproduce

Python 3.12 and its standard library suffice. From this package directory, choose two empty directories outside the checkout. The first command acquires the locked files from three public commits and verifies each file’s SHA-256 and Git blob. Once populated, the cache supports an offline replay.

```sh
python3.12 -I -B prepare_sources.py /tmp/p104-source-cache --fetch
python3.12 -I -B verify.py --cache /tmp/p104-source-cache --output /tmp/p104-result
```

For a shorter review, append `--part independent` for the literal construction, arbitrary-input maps, signed caller and directed prices. The hosted workflow also runs `--part application` and three disjoint chart shards. The default combines all checks. Output files include the two canonical graphs, the public layout, and the applicable independent and compiler receipts. [Verifier](verify.py) · [External source manifest](SOURCE-LOCK.json)

## Assumptions and open next questions

The finite bound assumes native all-column realization, owned erasure, the compiler, the precision tape and analytic recovery, following the selected framework. The compiler checks 54 strict and four functional obligations. The public f30 comparison uses the selected, independently reproducible BIT saving of 0.00385248. The finite candidate probe leaves 0.00000179125847000000000000000000 of BIT slack. Maintainers selected #7000 at 0.00363005817. [Selected framework](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

The requested review is of the complete joint supplier under those assumptions. The smallest independent review is to follow one entry of `PAID-EDITS.json` through its surviving source row, missing terminal direction and charged restoration, then reproduce the independent signed invoice and the five hosted checks.

## Credit

Clear1nsight prepared the joint construction, controlled replays and write-up with substantial OpenAI Codex assistance. Ali Romman contributed the public bank and helper recodings, closed 48-call caller and supplier. Clear1nsight’s #7767 provided the two hub transfers and eight carrier restorations used here. DreamingOfClouds, with Claude assistance, supplied the archived hub reroutes, banked toolkit and signed-curvature gate. SYLforge supplied the signed word, Rohan Arun the mirrored caller, Douglas Colkitt the absolute-phase and compiler framework, and Jerry Chen (CubeJerry) the selected BIT and complex application. Earlier engine authors and retained notices are credited in the donor sources. [Predecessor notices](NOTICE) · [Ali’s retained credit chain](https://github.com/aliromman/integer-mult-bounds/blob/6b0b2f7de0f068834264fc50b75a39a72c52ea22/research/p104-dual-supplier-lift/complex/retained/CREDITS.md)

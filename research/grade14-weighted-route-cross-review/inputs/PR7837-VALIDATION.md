# Evidence and verification

## Which complete claim was strengthened

At canonical base e54523517d0f03e58352e647c403a5af3e525a57 the maintainer-selected κ was 0.00363005817. At the time of this audit the strongest complete fixed-tape multiplication proposal we could substantiate was 0.00387992802601. We searched current open PRs and Discussions, checked the historical PR and Discussion index for higher numbers, then checked the source and arithmetic of the leading complete proposals. The nearby proposals at 0.00387990740712 and 0.00387992802506 have complete applications, with lower exponents. [Selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/frontier7000/CLAIM.json) · [Grade 14](https://github.com/CrocSwap/integer-mult-bounds/pull/7835) · [Previous cutoff](https://github.com/CrocSwap/integer-mult-bounds/pull/7831) · [Double contraction](https://github.com/CrocSwap/integer-mult-bounds/pull/7830)

The historical quotient proposal advertised 0.012401086416 as an outer exponent. Its emitted head and body widths include unequal main ports. Its own disclosure leaves the required admission parameters open, and the audit exhibits its failed native interface. A 0.4354 complex-unit claim was retracted. The 0.003889928046155 proposal tests a repair target and establishes two obstructions. The 0.00388013644474…75 crossing in the grade-14 source concerns the raw rational supplier. Its binary side has different limits. Each of these distinctions matters when ranking complete claims. [Quotient audit](https://github.com/CrocSwap/integer-mult-bounds/pull/4633#issuecomment-6341849407) · [Retraction](https://github.com/CrocSwap/integer-mult-bounds/pull/4937#issuecomment-6356735324) · [Repair target](https://github.com/CrocSwap/integer-mult-bounds/pull/7833) · [Both actual supplier rates](retained/grade14-result.json)

We ran the grade-14 source verifier at 43007c979859fa84ccc3a3509ccacc9620d181fa with its public inputs. It regenerated the complete RESULT, BIT and AUDIT files byte for byte, including the expanded stream account. The preceding exact words are at 14c74c6a67108f675ac1196a5f2415ead0920e71 and 89a67c404226d51028e135de2b9169e9020d57af. One finite replay leaves the universal native hypothesis open. [Original replay instructions and credit](https://github.com/CrocSwap/integer-mult-bounds/blob/43007c979859fa84ccc3a3509ccacc9620d181fa/research/p104-grade14-paid-cut/README.md) · [Retained file origins](ORIGINS.json)

## Reproduce the new checks

Use CPython 3.12. The new package has no third-party requirements. The registered commands read their declared repository inputs and the vendored exact source bytes.

```sh
python3.12 -B scripts/research_package.py --package research/grade14-native-realization
```

The scientific pass markers, in manifest order, are

```text
PASS_GRADE14_ALL_COLUMN_COMPLEX
PASS_GRADE14_ALL_COLUMN_BIT
PASS_GRADE14_COMPLETE_LOCAL_RING
PASS_GRADE14_FOUR_PREMISE_APPLICATION
PASS_NATIVE_ATLAS_BUILD c7173d46c95d1311b8b18a92c874fb7013c6e694aa8e9c0c256f0f1eaf1ede74
```

To generate the current absolute-phase catalogue separately, use a new file outside the package.

```sh
python3.12 -IB research/grade14-native-realization/charts.py --build /tmp/grade14-atlas.json.gz
```

| Independent check | Exact extent or failing control |
| --- | --- |
| Complex rational graph and transpose | 1,661,521 coefficients each, 220,217 donor incidences. Signed-digit bounds use 146 and 113 bits. |
| Two Clifford engines | Construct and check all 2,955 relative recipes and 208 boundary monomials. The physical lowering agrees on all 1,930,240 basis images of the distinct monomials. |
| Port and caller phases | 95,420,416 Walsh character values, 6,656 located contacts, all 840,912 instructions. The (0,249) phase gives exponent two at two columns. Omitting the second constant factor changes the phase. |
| Binary graph and transpose | Each covers 462,400 coefficients. Omitting a real QUERY changes 371 outer coefficient positions per direction. |
| Port placement | 29,970 active basis directions and 1,998 exterior checks. Replacing the port maps by identity changes 27,972 directions. |
| Matched child inputs and returns | 7,776 parent slots. Reversing the matcher direction changes 5,184, omitting the donor changes 3,888 and omitting the return changes all 7,776. |
| Physical high matrices and leaves | 31,491 high records across 291 cases. Dropping the carry changes 30,051. One actual rank-one edge supplies both a good and a nonzero nonunit test. A second implementation checks all 108 split rank-one projectors over Z/9 at four multiplicities. |
| Ordinary service and complete application | 10,478 elementary permutation entries, the cold preparatory stage, four original bootstrap rates, both endpoint rates, full-field length factor, all 54 strict inequalities, four functional inequalities and nine outer rows. |

[check_complex.py](check_complex.py) uses an independent Clifford verifier to check the emitted factors. [contacts.py](contacts.py) computes character equations over the full small space. [check_binary.py](check_binary.py) checks the actual coordinates and mutations. [check_leaves.py](check_leaves.py) directly applies the weighted projection in physical order. [check_application.py](check_application.py) uses exact rational arithmetic for the outer ledger and cold bootstrap. The full numerical receipts are in [RESULT.json](RESULT.json).

## Proof scope

The finite checks establish facts about the literal words and particular small physical executions. The extension to every column count is the chart and substitution proof in [PROOF.md](PROOF.md). The right-action formula, full fresh-row argument, local-ring branch proofs and uniformly funded ordinary service are in [ROUTES.md](ROUTES.md) and [APPLICATION.md](APPLICATION.md). These arguments allow arbitrary independent input data and correlated values on distinct physical roles, including spectators and padded rows.

The reference programs execute finite certificates; their Python allocation and timings do not measure a multitape transition count. The written proof constructs the tape-level operations under the four original remaining assumptions. The compiled uniform words and complete asymptotic integer inputs are too large to materialize in these checks. The fixed constants and cutoff are impractical. No independent human acceptance or formal kernel check of the new uniform theorem is claimed.

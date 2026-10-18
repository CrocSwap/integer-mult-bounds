# Heterogeneous 3+7 root echoes share one order-four boundary

## Construction

In the pinned order-four PR1391 macro interface, two different consecutive root echoes can share one ten-child phase schedule. Type A has three children reading source octets `[0,1,2]`. Type B has seven children reading `[2,1,0,2,1,0,2]`. Both update the same dirty output octet from the same arbitrary dirty source/work coordinates. Their combined exact map is realized either by the two separate canonical calls A then B or by one canonical joint call using the concatenated ten-reader sequence.

The complete charged macro word drops from 2,080 to 1,904 ADD/NEG primitives, saving 176 (8.46%). The invoice includes both forward and literal-inverse child bodies, one 48-ADD root copy/restoration wrapper per call, and both traversals of each phase boundary. The joint word uses one wrapper and one ten-child boundary path. Its prefix row-L1 peak rises from 36 to 42, so this construction does not establish a precision improvement.

## Exact model and accounting

The phase state is `Z/4Z`. Per-octet frame costs are `[(0,0),(18,2),(12,4),(18,2)]` in `(ADD,NEG)` units; the three-octet workspace costs three times that vector. A transition `old -> new` pays `work[(new-old-1) mod 4] + output[(new-old) mod 4]`. The pinned leaf costs `(62,6)` and the root wrapper costs `(48,0)`. For `k` children and boundary invoice `g(k)`, the complete root invoice is `2*k*(62,6) + (48,0) + 2*g(k)`.

The exact phase paths are:

| Call | Children | Phase path | Boundary ADD/NEG | Boundary total |
|---|---:|---|---:|---:|
| A | 3 | `0,1,2,0` | `(102,14)` | 116 |
| B | 7 | `0,1,2,3,0,1,2,0` | `(174,22)` | 196 |
| Joint | 10 | `0,1,2,3,0,1,2,3,0,1,0` | `(216,32)` | 248 |

The phase DP is checked against all `4^3`, `4^7`, and `4^10` paths. The verifier applies each resulting word to the complete 56-coordinate integer matrix. It checks four maps: A, B, separate A-then-B, and the joint call. The last two equal the same exact target; all source and workspace coordinates stay dirty and restored. Four negative controls reject an omitted B call, a changed B reader, a wrong initial output phase, and a missing terminal restoration.

| Execution | ADD | NEG | Primitives | Reads | Writes | Prefix row-L1 peak |
|---|---:|---:|---:|---:|---:|---:|
| A, separate | 624 | 64 | 688 | 1,312 | 688 | 14 |
| B, separate | 1,264 | 128 | 1,392 | 2,656 | 1,392 | 30 |
| A then B | 1,888 | 192 | 2,080 | 3,968 | 2,080 | 36 |
| Joint ten-child | 1,720 | 184 | 1,904 | 3,624 | 1,904 | 42 |

Each ADD reads its target and source and writes its target; each NEG reads and writes its target. The 56-coordinate word uses the pinned eight-coordinate output, three source octets and three workspace octets. The exact map check includes all 56 basis columns.

## Distinction from prior work

The closest predecessor, `research/z4-persistent-pair-seed57`, composes two identical five-child calls with the same source-reader list; its README explicitly excludes heterogeneous calls. This experiment changes the child counts to 3 and 7 and changes the second type's source-reader map. It retains the pinned PR1391 child family and order-four frame. The saving is therefore a new typed-pair construction in that exact macro model, not a new child supplier or a new frame algebra.

The selector seed is `65562f37d3a7a48fc2f959e36d6e638c`; task `persistent-boundary`; catalogue priority revision 3; exact base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. The selected result's reviewed record points to `docs/research/community-batch1099-review.md`, source manifest `research/community-frontier1094-audit/SELECTED-SOURCE.json`, certificate `research/community-frontier1094-audit/ASSEMBLY.json`, and reproduction command `make frontier1094-verify`. The selected review identifies #1094 as owner packing on the unchanged seven-slot k8 word; the heterogeneous-owner bound freezes 71 provider records and 25 cost interfaces and supplies no new child supplier. Since these sources do not expose an admitted 3+7 pair contract, this experiment uses the fully pinned PR1391 macro interface as a bounded mechanism test. It remains outside the selected supplier chain.

## Reproduction and limits

```sh
python3 -I -B research/z4-heterogeneous-pair-seed3x7/verify.py
python3 scripts/research_package.py --package research/z4-heterogeneous-pair-seed3x7 --check-only
```

The verifier regenerates `CERTIFICATE.json`. It imports only the pinned predecessor interface from `z4-persistent-pair-seed57`; `SOURCES.json` fixes the current-base blobs and hashes, and the predecessor verifier independently checks the original PR1391 certificate/code pins. The standard registered replay expects Python 3.12; only Python 3.14.7 was available here, so package metadata was checked without launching that replay.

The result is scoped to this formal macro interface. Supplier hosting, source-dependent coefficient access, tape storage, fixed-precision safety and the integration with the selected recursive word remain unproved. No new `kappa` or multiplication exponent follows. The increased prefix row-L1 is an explicit precision risk.

## Open next questions

Can a concrete selected supplier implement this heterogeneous pair with the joint word's prefix row-L1 peak of 42? This matters because only an admitted supplier can transfer the macro saving into the recursive profile. A feasible first step is to inspect candidate selected child maps for the exact order-four intertwiner and run their dirty-state compiler on A and B. The blocker is that no physical supplier has yet been identified for the paired-frame child contract, while the joint word increases the prefix bound.

## Credit

The order-four child emitter and pinned PR1391 source fixture are credited in `NOTICE.md` and the predecessor package. The heterogeneous 3+7 scope, exact phase comparison, map checks, invoices and prose are original work prepared with substantial OpenAI Codex assistance. No independent human review is claimed.

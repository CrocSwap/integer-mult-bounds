# A native local read of QQ16's future query B2 C

This supplies one missing local access in [PR2443](https://github.com/CrocSwap/integer-mult-bounds/pull/2443):
read `B2 C` from its post-B1 ordinary target block `C=x2_U`, return all 96
source arrays unchanged, and retain the eight query coordinates in explicitly
owned output arrays. The complete local word costs **192 rank-one children**.
It is not a zero-native-line use of the earlier X bridge.

At that cut C has completed-X stage-1 frame `F_(L+E1)`, but the requested
chart is future chart 2. The retained bridge only promises its zero-line X
alignment at or after the queried chart. Applying the future-Y alignment to
this X frame leaves the exact port-specific factor `C_(q_p)`. One inverse
line per source removes it; one positive line per source restores it after
the read. This is a constructive local invoice, not an unrestricted lower
bound on every possible way of obtaining the query.

## Exact interface and invoice

The unchanged source contract places the 96 ordinary X fields in frame
`F_(d(L+E1))` after `B_1_2`. Their logical values C are arbitrary. Insert this
read before any following operation changes them. The eight new output arrays
are **owned**, so their arbitrary previous contents may be cleared. They are
not borrowed dirty helpers. The output is

```
Q_k(d, payload) = (B2 C)_k(d, payload),  k=0,...,7,
native output frame F_(d(E1+E2)).
```

All original source contents, native frames and owner positions are restored.
All output arrays remain live. Their later retention, delivery and eventual
cleanup are separate controller obligations; this word does not hide them in
the original 480-helper stock.

| Complete local quantity | Count |
| --- | ---: |
| Rank-one children / native rank mass | 192 / 192 |
| Native monomial wrapper maps | 384 |
| Full-cover maps, including undo | 192 |
| Signed scalar ADDs | 384 |
| Owned-output CLEARs | 8 |
| Real scalar primitive allowance | 3,088 |
| New live owned output arrays | 8 |
| Borrowed source arrays restored | 96 |
| Literal events before expanding line wrappers | 776 |

The scalar allowance is `2*(4*384+8)` under the retained complex-to-real
ledger. It excludes the separately counted child and map costs. Map counts
are not a physical addressing-time bound. No complete favorable supplier
budget or new kappa is established.

## Evidence and reproduction

[PROOF.md](PROOF.md) derives the exact endpoint using the inherited native
frame conventions and full-cover action. [RESULT.json](RESULT.json) contains
the literal word, all 192 signed line recipes, the complete invoice and
rejection receipts. [SOURCES.json](SOURCES.json) pins the immutable archive,
QQ16 packet and consumed contracts. The R matrix is independently rebuilt
from the retained scalar prefix. Future route matrices and both payload
translations are rebuilt from phase geometry and compared with emitted maps.

The motivating access handoff is retained verbatim in
[PR2443-README.md](evidence/PR2443-README.md), lines 188-191 and 202-212, from
PR2443 head `545c05e17243c962b112b91e7f84b4c1a41de7b8`.
[PREDECESSOR.json](PREDECESSOR.json) records its exact path, Git blob and
SHA-256. The tests bind that copy to both hashes. The runtime query is
independently defined from the base sources; no pending PR code is imported.

The verifier tracks all 104 independent logical inputs with exact rational
coefficients and actual owner operators, alongside exact Z4 frame polynomials
after every event. Every ADD must have identical source/target native phases.
It checks all 98,304 low-block basis columns of the signed rank-one kernels;
the external coordinates are spectators. Eight controls reject missing
normalization/restoration, missing or incorrectly undone translations, an
uncleared dirty output, a wrong coefficient, an early query and an inverse
line with the wrong sign. The formal identities apply to arbitrary payloads;
no floating-point acceptance is used.

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-future-x-query
python3.12 -I -O -B research/qq16-future-x-query/verify.py
```

Expected status: `PASS_QQ16_FUTURE_X_QUERY`. Replay compares the entire
recomputed receipt with the committed one and writes nothing. Explicit
`--write-result` creates a new receipt and refuses an existing path.

## Limits

This is a complete local native-operator sequence under the retained full-cover
view, signed rank-one primitive and sweep conventions. It does not assign its
new children to global helper owners, price physical map execution, prove
recursive precision, or retain the cut through the rest of the controller.
The other reads, scalar minor inverse, output gauge conversions, storage and
cleanup in PR2443 remain unpriced. It is not a full decoder implementation.

## Open next questions

1. Can the other two-cut records and this query be hosted and retained with a
   favorable full invoice? Start with all added arrays, children and maps in
   one chronological ledger; stop if the optimistic complete bill already
   misses the supplier target. Global owner delivery is unresolved.
2. Can an earlier read or fusion with an existing native transition avoid
   this standalone normalization cost? Specify a changed observation time or
   word and check the full ordered decoder. This invoice does not exclude
   such a different interface.

## Credit

`starship-s` / PR2443 supplies the exact `B2 C` access question and two-cut
decoder. Ali Romman / PR1969 supplies the QQ16 native words, signed line
conventions, full-cover maps and endpoint frames. The bridge review and its
underlying Rohan Arun, Jeremy Kothe, DreamingOfClouds and supplier lineage
retain credit in [the source notice](../joint-query/NOTICE.md). Gareth Davidson
/ PR2432, commdata2338 / PR2174 and the other coordinate-read predecessors
retain the attribution in PR2443. This author's PR2456 audited that decoder;
this package constructs one of its still-missing native reads.

Prepared by ywz65 with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. No independent human or proof-assistant
review is claimed. New work is Apache-2.0; frozen sources remain unchanged.

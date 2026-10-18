# Independent audit of the complete P104 relay correction

Philippe Van Velzen's [relay-v2 construction](https://github.com/philippeVV/integer-mult-bounds/tree/fac9e821d31bc199b49e8ed463074a50d1264311/research/p104-correction-screen/relay-v2)
uses 1,031 dirty helpers to correct all 104 P104 targets. This package proves
that its source family's 208-departure floor survives all 336 later-readable
entries, by explicitly checking the demands that still force line reads.
It also independently composes the literal relay with the entire original
channel. The construction, count, numerical floor and later-readable entries
are all credited predecessor results. [PR2594](https://github.com/CrocSwap/integer-mult-bounds/pull/2594)
already audits correction-only endpoints and logical growth; those results
are not claimed new here.

**Result:** the complete 21,682-event v2 word sends every target to `y_t+x_t`,
restores all 1,103 original/new dirty helper inputs, and preserves all 104
sources in their prescribed endpoint charts. Two separate exact interpreters
agree on the full 1,311-input matrix: **1,718,721 coefficients**, with 1,415
nonzero entries. The original eight nonzero private-copy erasures remain
explicitly inherited. The earlier 2,185-helper word is retained and fully
replayed as historical evidence. This is a logical/frame audit and scoped
all-network proof, not native supplier admission or a new kappa.

## Independent evidence

The new checker reconstructs the E8 roots and `C=I-G/2`, uses reduced binary
bases for frames, and advances the original 4,058-event word before each
cut-labeled relay access. Rational rows track every independent input. It
checks actual common-chart operations and nested transports at each cut;
there is no assumption that a source's entrance frame survives to the end.

A second implementation separately parses both words, runs the complete
reverse adjoint, and checks the transpose of the full endpoint with exact
dyadic integers. Each division must be exact. It imports neither the primary
implementation nor any predecessor executable. This is a second full-matrix
check, not sampled inputs or a finite-field surrogate. The finite identity
proof and precise scope are in [PROOF.md](PROOF.md).

The source's standalone correction checker is retained as an immutable
reference text and is never executed by this package. The original channel
is replayed directly from its literal witness. Its native chart meaning is
inherited from the pinned main-branch proof; new relay transport recipes,
complete private-storage implementation, global owners, precision, and all-size
admission are not supplied here.

The checked relay invoice is:

| Quantity | Exact value |
|---|---:|
| New helpers, all live across the original word | 1,031 |
| Relay moves / shears / reads / writes | 4,840 / 5,362 / 726 / 6,696 |
| Relay events, excluding inventory header | 17,624 |
| Original plus relay events | 21,682 |
| New boundary rank mass | 9,279 = 9*1,031 |
| Original plus relay boundary rank mass | 11,647 |

The exact added profile is `2427H1+1094H2+998H3+96H4+66H5+157H6+2H7`.
These are boundary ranks, not a hosted recursive price. The predecessor's
unfavorable moment or proposed lifetime caps are not rederived or promoted
to new theorems by this audit. The separate active arrival-shape audit is
explicitly outside this scope. Its design-search heuristic, merge-loss census,
and proposed general accounting identity are outside the checked claim.

## Why later reads do not invalidate the departure floor

The source already recognizes 336 entries accessible through later source
frames, so a global line-only premise would be false. Its plane-cover check
uses all 48 demands of each source, while its prose asserts that the 208
floor survives those later opportunities. We explicitly remove every target
whose final hyperplane contains any later source frame, granting all such
reads even without a timing restriction.

For every source, the remaining **36–48** forced target hyperplanes intersect
in exactly that source's initial line. All source lines are distinct, source
paths contain their initial line, target paths stay inside their final
hyperplanes, and no target ever visits any source line. These facts are
checked twice from the frozen paths. The complete certificates are in
`LINE-WITNESS.json`.

With only one helper departure from a source line, every downstream dependency
from line reads must stay above its first larger frame. To serve every forced
target, that larger frame would have to lie inside their intersection, which
is only the source line: a contradiction. Each source therefore needs two
departing lifetimes, and a monotone helper can visit at most one source line.
Thus `L>=208` for every finite permitted X-only correction network, allowing
all later reads, rational mixing and cancellation. This proves the missing
implication without strengthening the credited numerical floor. It neither
constructs a 208-helper correction nor closes the gap to 1,031.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -I -O -B research/p104-relay-chronology-audit/verify.py
python3.12 -I -O -B research/p104-relay-chronology-audit/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-relay-chronology-audit
```

Expected status: `PASS_P104_RELAY_CHRONOLOGY_AUDIT`. `RESULT.json` compares
every typed field. `--out NEW_PATH` writes a new receipt exclusively. Direct
replay is read-only and works in a Git-free export with declared inputs; the
registered metadata launcher additionally needs Git provenance.

Eight actual fault controls reject a changed read coefficient, omitted dirty
compensation, missing helper cleanup, early target write, invalid move,
lifetime-header mismatch, a changed original-channel ADD, and an incomplete
line-forced classification. A ninth countercontrol retains all 336 actual
later-read opportunities. Tests also reject the actual source-coefficient
fault in the reverse interpreter, accept equivalent frame bases, and check
Git-free unchanged exports, retained executable drift before any computation,
missing evidence, incomplete witnesses, typed receipts and non-overwrite.

The optimized replay and all three registered test groups pass on CPython
3.12.7. A separate agent reviewed the proof and both implementations and
independently replayed both complete words on optimized CPython 3.12.14.
The selected native
cold replay, predecessor optimizer and favorable global allowance are unrun;
none is an acceptance claim of this contribution.

## Selection and sources

Canonical main at selection was `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision 4. The picker selected `p104-side-correction` with seed
`296d172895dc11178a7b95219224afb7`; its first baseline command passed.
`TASK.json` changes scope to the live request for independent review in
[Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18951262).

`SOURCES.json` binds the exact v2 word/README at
`fac9e821d31bc199b49e8ed463074a50d1264311`, the original word/README/checker
at `d35dd88e3bd344600e879af3427c104a95b1ff05`, and the original P104 witness,
fixture and native proof. PR2594 at `6ae5673429d960a5fd0f936f6dfd67850e353278`
is credited as the separate correction-only growth result. Historical v1
replay checks all 6,076,225 coefficients with both interpreters; it is retained
evidence, not advertised as the latest construction. SHA-256 and Git blobs are retained. The source tree's
web page denied scraping; its public Git object was fetched and pinned, while
the Discussion was refreshed with Curiosity Bot. Overlap coverage and the
final checkpoint are recorded in TASK.json; no metadata search guarantees
novelty or covers every unpublished result.

## Open next questions

- **Better relay design:** Can lower-frame pools serve independent demands
  for several targets and bring a complete word within the predecessor's
  favorable allowance? First produce and price one actual improved network.
  The current 208 floor and 1,031 construction leave a wide gap; no design
  optimization or stronger general floor is supplied here.
- **Native/global admission:** Bind each new transport and the inherited
  private-copy lifecycle to a concrete native implementation, then assign
  actual chronological owners and precision obligations. Logical frame
  legality alone does not provide those contracts.

## Credit and license

Credit petalas / PR2594 for the independent correction-only v2 endpoint and
logical growth audit. Philippe Van Velzen, with Claude Code assistance, supplies the complete relay
design, literal word, window/geometry findings and departure-floor proposal.
The X-only model and preceding lifetime results are due to Hiroki Kumazaki
(PR #2353), commdata2338 (PR #2393), and Ross Richardson (PR #2445). Credit
Rohan Arun (PR #1972), Chafik Boukhalfa (PR #1991), Adam Gall (PR #1940),
Josie Elliston (PR #1071), Ali Romman (PR #1125/#1862), and the retained
P104 geometry/native/compiler lineage. Original text is preserved unchanged.
Independent audit and the explicit later-read-aware proof are prepared by
ywz65 with substantial OpenAI Codex assistance, including separate agent
review. No independent human or proof-assistant review is claimed.
Apache-2.0; no broader mathematical priority claim.

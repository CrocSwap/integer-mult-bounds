# P104 private descent reuses one public fanout helper

## Result

This package records a finite construction improvement to the forward P104
word in PR #2152. One rank-seven owned query copy serves the three contacts
previously routed through public helper 7, by descending through their nested
contact frames before continuing to its original rank-one endpoint. The helper
slot stays allocated and untouched. The replay verifies every endpoint row
over all 735 input columns, including the specified live-Y plus X transfer,
and the native lowering verifies the revised private descent.

The combined paid local profile drops from rank mass 5,894 to 5,885, a saving
of 9. This does **not** improve the selected conditional bound. Under the
retained m=73, P104, COPY56, nine-stage balanced-transfer screen, the exact
selected-threshold moment is still above one and the optimistic complex-side
cap remains below the selected κ. This is a local cost reduction, not a new
supplier or κ result.

The contribution is packaged in [PR #2219](https://github.com/CrocSwap/integer-mult-bounds/pull/2219).

## Pins and coordination

- Cycle seed: `915fa969cacecdfec5dcd7a95a4bf0a0`
- Track/task: `complex-mechanisms` / `p104-side-correction`
- Catalogue priority revision: `4`
- Main base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
- Predecessor: PR #2152 at `05f7aad0f08992ee48ec2dd93e896d9a4567847d`
- Claim: Discussion #1167 comment #18936581, expiring 2026-10-15 01:59:31 UTC
- The predecessor's README asks whether existing helper lifetimes can replace
  new fanout helpers. The scope here is the concrete global helper 7, pair
  `(4,57)`, and its three contacts at B-prefix cut 507.
- Relevant predecessor PRs/claims included #2089, #2082, #2090, #2113, #2127,
  #2139, #2173, #2190, and completed claims #2131/#2190. The live overlap
  check found no active helper-7 private-descent implementation. PR #2152's
  helper-lifetime question is the direct predecessor, not a competing claim.
  Before submission, new claim #2218 appeared for a different `(97,5)` delayed
  recipient echo and register/cut scope; its method and term differ from this
  nested descent. The live PR search also returned #2113's rank-eight cut
  obstruction, not a helper-reuse construction.

The experiment uses the pinned PR #2152 source unchanged as its base and
patches its `fanout.py` word before the separate `coalesced.py` rechart. The
initial Discussion claim named the coalesced word; this package narrows the
verified scope to the predecessor's original forward word. The coalesced
variant remains untested. The single-file patch in `fanout-helper-reuse.patch`
adds the exact matrix replay controls. `price_reuse.py` and `verify_native.py`
run against the patched predecessor checkout.

## Mechanism

The `(4,57)` query source is register 133 in an 8-dimensional frame `Hb`. Its
owned private copy is scaled by `lambda=-1/2`. In the predecessor word, helper
7 enters at the line `La`, receives contacts at the following nested frames,
then returns to `FULL`:

| Target register | Contact coefficient | Contact frame basis | Dimension |
| --- | ---: | --- | ---: |
| 159 | -1 | `[2,12,16,33,64,128,261]` | 7 |
| 203 | 2 | `[2,12,33,80,144,261]` | 6 |
| 148 | 2 | `[45,82,144]` | 3 |

These spaces satisfy `La ⊆ F1 ⊆ F2 ⊆ F3 ⊆ Hb`, where F1 is the frame for
register 148, F2 for 203, and F3 for 159. The private copy descends
`Hb → F3 → F2 → F1 → La`, charging rank jumps `1+1+3+2=7`. At each contact,
the target register moves to the same frame used by the predecessor helper
and receives the same scalar multiple of the scaled query row. The private
copy then reaches `La` and seeds the other helpers for `(4,57)` as before.

The public helper's entry, contact, and endpoint transports disappear. The
other two helpers for `(4,57)`, all other contacts, and the source query are
retained. No additional private copy is created and peak private occupancy
stays one. The freed helper register remains part of the 735-column identity
and is left untouched.

## Exact evidence

| Quantity | Before | After |
| --- | ---: | ---: |
| Public transport profile | `1:2611, 2:514, 3:378, 4:132, 5:81, 6:15, 7:6` | `1:2609, 2:512, 3:377, 4:132, 5:81, 6:15, 7:6` |
| Private `COPY` profile | `7:8` | `1:2, 2:1, 3:1, 7:7` |
| Combined rank mass | 5,894 | 5,885 |
| Private `COPY` rank mass | 56 | 56 |
| Exact scalar ADD count | 20,956 | 20,947 |

The verifier checks all 735 endpoint columns, exact rational scalar
operations, the public and private occurrence invoices, and five negative
controls. Entry compensation drops from 832 to 825 ADDs; helper seed and
helper restoration each drop from 31 to 30. The three removed public contact
ADDs are replaced by three direct private-copy contact ADDs. Response cleanup
remains 276 ADDs and punctured-Y restoration remains 911. Omitting one reused
contact fails the endpoint map. Native lowering checks every literal
transport recipe, signed Pauli action and phase, the eight private paths, and
all 4,096 Gaussian basis columns in the composed private paths.

The priced combined profile is
`1:2611, 2:513, 3:378, 4:132, 5:81, 6:15, 7:13`, with exact local mass 5,885.
The certified saving-root bracket is
`[1661503598793/1000000000000000, 830751799397/500000000000000]`, or
`[0.001661503598793, 0.001661503598794]`. Its complex-side κ cap is
`830751799397/500830751799397`
(`0.00165874758371416805798661`), below selected
`0.001672660197076918`. At the selected saving threshold, the exact moment
interval is

```text
[115797359306122468329603805425583230183217804648449829200764880802103324328373
 /115792089237316195423570985008687907853269984665640564039457584007913129639936,
  57898679653061234164801902712791615091608902324224914600382440401051662164207
 /57896044618658097711785492504343953926634992332820282019728792003956564819968]
```

Both endpoints are greater than one. The model prices the full observed public
and owned transport profiles, recursive children, frame changes, and
restoration under the pinned balanced-transfer screen. Exact scalar ADDs are
recorded above; the selected-result ceiling is a transport-profile moment
model. As in that necessary screen, all residual mass is optimistically
permitted to form fractional rank-51 idle children.
This experiment does not supply the full multiplication wrapper, global
hosting, or bit-side admission, and it does not establish a new κ.

## Reproduction

From a clone of `CrocSwap/integer-mult-bounds`, fetch and check out the exact
predecessor commit in a temporary worktree, then apply the recorded patch. Run
the artifact scripts from the repository checkout that contains this package:

```sh
git fetch origin refs/pull/2152/head:refs/remotes/origin/pr2152
test "$(git rev-parse refs/remotes/origin/pr2152)" = 05f7aad0f08992ee48ec2dd93e896d9a4567847d
git worktree add --detach /tmp/p104-private-reuse 05f7aad0f08992ee48ec2dd93e896d9a4567847d
git -C /tmp/p104-private-reuse apply /path/to/fanout-helper-reuse.patch
cd /path/to/the/package-containing-checkout
python3 -I -B /tmp/p104-private-reuse/research/p104-interleaved-search/fanout.py
P104_REPLAY_ROOT=/tmp/p104-private-reuse python3 -I -B research/p104-private-descent-reuse-seed915fa969/price_reuse.py
P104_REPLAY_ROOT=/tmp/p104-private-reuse python3 -I -B research/p104-private-descent-reuse-seed915fa969/verify_native.py
```

Expected checks are `full_735_column_identity_verified: true` (the predecessor
field name for the exact endpoint-map check),
`all_new_helpers_restored: true`, the five rejected negative controls, combined
rank mass 5,885, selected moment greater than one, and native status
`PASS_FINITE_NATIVE_LOWERING`. The native replay is substantially slower than
the scalar replay because it checks the full Gaussian-column basis.

## Attribution and limits

The seed and scoped hypothesis were selected by this cycle. The mathematical
idea and implementation were developed with substantial OpenAI Codex
assistance. The predecessor P104 word, query construction, frame data,
balanced-transfer model, and native checker remain attributed to their
respective source packages and authors. The patch is an experiment based on
PR #2152, not a modification of that PR.

# One transposition cancels the after-stage-0 leaf block

**Proof, for one legal block.** Keep `A = diag(I_8, 0)` and replace the
named off-diagonal block `E_{0,8}+E_{9,2}` by

```text
B = E_{0,8} + E_{8,0}.
```

Over every field of characteristic 2,

```text
(A+B) C = B,    C  = E_{0,0} + E_{8,0} + E_{8,8},
(A'+B) C' = B,  C' = E_{0,0} + E_{0,8} + E_{8,8},
```

with `A' = I+A`. In the after-stage-0 split, the leaf-1 → leaf-0 block of
the balanced correction may be set to `C` or to `C'` according to which
half stands second. The leaf-0 ← leaf-1 block of the normalized
coefficient is then the zero matrix for every invertible specialization.
The opposite block `E` does not enter that identity.

Selected κ stays `363005817/100000000000`. This is not a native caller and
not a change to the selected frontier.

The argument and the limits are in [PROOF.md](PROOF.md). The evidence
class is a proof for this named `B`. The GF(4) schedule checks the word
against the closed form. It is not a census of legal blocks. A cancelled
leaf-0 ← leaf-1 block is not an endpoint.

## Scope and evidence

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks whether a changed query demand removes real work. The assigned
question is open question 1 of open PR #7097: one legal off-diagonal `B`
other than `E_{0,8}+E_{9,2}`, with this same `A`, and the two column-space
equations `(A+B)C = B` and `(A'+B)C = B`. The transposition above is that
one matrix. Both equations have an explicit solution, and the matching
solution cancels the leaf block in the same after-stage-0 split. The
result is not a supplier and not a new κ.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is `363005817/100000000000`. This
package uses that record and edits neither file.

Overlap, rechecked at base `e54523517d0f03e58352e647c403a5af3e525a57`:

- Local `find_overlap.py --offline` searched 10180 notes at that head,
  with a complete head inventory, and reported no match for `E_{0,8}`.
  The remote snapshot was not loaded. Open PR bodies were searched
  directly: the GitHub issue search for `E_{0,8}` and for `E_{9,2}` each
  returns only open PR #7097. A discussion search for the column-space
  question returned no items. Fork PR #229 is the unpaidmoon draft of
  #7097, not a second answer.
- Open PR #7097, head `97bc92e76e5954f46befbe5c6790b6f2107e0d3a`, proves
  the miss for `B_0 = E_{0,8}+E_{9,2}` and asks this question. Section 3
  here repeats that obstruction as a control. The new block differs in
  positions `(8,0)` and `(9,2)`.
- Open PR #7026 is the internal gap that #7097 splits. Open PR #7096 is
  the stage-0-not-first schedule. This package keeps stage 0 first.
- Open PR #7010 is the adjacent-halves count. A thin map stands between
  the halves here, so that count is not the claim.

Source commits, Git blobs, and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record, the catalogue, and the
paired-star contract are historical provenance. PR #7097 is not an
ancestor of this branch, so its tree is cited by commit and is not a live
pin.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-transpose-corner
```

The registered replay runs `verify.py` twice, once with `-O`. Both print
`PASS_PAIRED_STAR_TRANSPOSE_CORNER`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-transpose-corner/verify.py
```

## Open next questions

- For this same `B`, with the matching forward block `C` or `C'`, does
  any constant opposite block `E` make leaf 1 ← leaf 0 zero as well? At
  the tested `F_4` points with `E = 0` that opposite block is nonzero, so
  the zero choice is not an endpoint. The first step is one matrix `E`,
  for example the transpose of `C`, at `D_0 = t` in `F_4` and one half
  order. One matrix is not `S = I`.
- Does the shifted transposition `B = E_{1,9}+E_{9,1}` satisfy the same
  two equations for this fixed `A`? The block proved here uses coordinate
  0, which is also a corner of the named pair. The first step is the same
  three-entry shape on coordinates 1 and 9, and one multiplication. One
  further matrix is not a classification of the blocks `[[0, Q], [R, 0]]`.

## Credit

The paired-star contract and the rank floor are from PR #5747 (Ali
Romman), including PR #5673, PR #5631, and PR #5617. The internal gap is
PR #7026. The after-stage-0 question and the named obstruction are PR
#7097.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.

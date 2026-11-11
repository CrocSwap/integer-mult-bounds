# Constant insertions after stage-0 E_22 and stage-1 E_11

**No new kappa.** In the nine diagonal gates of PR #7027, constant matrices
`R` and `S` may sit in the gap after stage-0 `E_22` and the gap after
stage-1 `E_11`. Over `F_2`, with `e` central and `e^2 = 0`, the coefficient
of `e` equals the pure product for exactly `2^30` pairs. Every diagonal
entry of that coefficient is `0` or the corresponding entry of `P`, and
each of those entries differs from `1`, so the coefficient is never `I`.
The selected frontier stays `363005817/100000000000`.

The argument and the limits are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
query demand removes real work. This package answers a different question:
the first open question of PR #7103, at the two gaps named in its first
step. The field stays `F_2[x, y, z][e]/(e^2)`. It is not a caller, a native
bill, or a change of kappa. Source commits, Git blobs and SHA256 pins are
in [SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance.

`current-priorities.md` at this base still prints the older decimal
`0.00310045`. The live selected record in `certificates/selected-result.json`
is `363005817/100000000000` from the PR #7000 / #7001 admission. This
package uses that record and edits neither file.

The classification is an identity. The middle diagonal between the two
slots is `diag(1+y, 1, 1+x, 1+x, 1, 1, 1, 1)`. Constant solutions are the
pairs whose diagonal sums to `1` and whose off-diagonal bits agree on the
level sets `{2, 3}` and `{1, 4, 5, 6, 7}`, and vanish off those level sets.
The machine check multiplies every one of the 64 matrix units in each gap,
compares the two scales with that middle diagonal at all 64 positions, and
solves all four bit pairs at all 64 positions. The solution count is the
product of those per-position counts. The `2^30` pairs were not listed.
Evidence class: a proof, with an exhaustive four-element census of each
scalar equation. A failed search is not what this record claims.

Overlap was checked on 2026-11-11 against the open-PR snapshot of 500 PRs
through #7200, against discussion opening posts, against local package
notes at `e54523517d0f03e58352e647c403a5af3e525a57`, and by GitHub search
for the slot phrase. The only open record that states these two slots is
PR #7103, which leaves them as its first open question and classifies the
adjacent stage-0 pair instead. PR #7191 classifies polynomial entries in
that adjacent pair. PR #7039 is the one-insertion theorem. No local package
solves these two slots. Closed-PR bodies are covered only through notes
present on this base.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/e22-e11-constant-gaps
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_E22_E11_CONSTANT_GAPS`. The checks raise `SystemExit`, so optimized
mode does not drop them. Directly:

```sh
python3 -B research/e22-e11-constant-gaps/verify.py
```

## Open next questions

- For the gap after stage-1 `E_22` and the gap after stage-2 `E_11` in
  this same nine-gate word, which constant `F_2` pairs make the coefficient
  of `e` equal to the pure product? PR #7039 asks about two gaps in
  general. PR #7103 closes the adjacent stage-0 pair, and this package
  closes only the pair after stage-0 `E_22` and stage-1 `E_11`. The first
  step is to form the diagonal of the gates strictly between those two
  later slots and compare its level sets. Nothing external blocks that
  calculation.
- Do entries in `F_2[x, y, z]` of degree at most 1, in these same two
  gaps, give solutions of `C = P` beyond the `2^30` constant pairs? On a
  blocked position the constant equation has only the zero solution, while
  `M_0 = 1+y` and `M_1 = 1` make `R_{0,1} = 1+y`, `S_{0,1} = 1` a solution
  of that one entry. The first step is to keep a legal constant diagonal
  and legal matched bits, substitute that pair, and multiply the
  coefficient against `P`. Nothing external blocks that substitution.
  PR #7191 answers the polynomial question only for the two stage-0 gaps
  of PR #7103.

## Credit

The paired-star contract, the operator `T`, and the pure target are from
PR #5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. The
valuation-1 triple and the nine-gate word are PR #7027, head
`1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0`. The one-insertion theorem is
PR #7039, head `e4ddcd2fde8c46b7e528e8806ab72d9bf7690978`. The adjacent
stage-0 classification and the question answered here are PR #7103, head
`f3af1384aeda8c75be58f09cb07da3941ba7aba3`. PR #7191, head
`4268eab9d5bc1293a006d27abf9164d125ff094d`, classifies polynomial entries
in that other pair. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Independent human review and a proof-assistant proof are
unclaimed. Apache-2.0.

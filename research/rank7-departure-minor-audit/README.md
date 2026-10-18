# Independent departure-minor audit for PR3114

**Scoped audit: ten departure obstructions reproduced on both PR3042 words.**
This package gives explicit nonzero rational minors for the eight proposed
`(1,3)` replacements of `(2,2)` restore climbs and the two departure-forced
visits in Marius-Paul Dumitrean's [PR3114](https://github.com/CrocSwap/integer-mult-bounds/pull/3114),
at head `c88769c350977d9ed4f90fe5c652d582cfe2782a`.
The result is evidence for that particular implication of the fixed-A/B model,
not a verification of the complete restore-optimality theorem or an admitted supplier.

The only computational inputs are dcharb78's two PR3042 words, with Git blob and
SHA256 pins in [SOURCES.json](SOURCES.json). No predecessor Python module,
frame optimizer, cost engine or stored certificate is imported or executed.
The proof and source implementation were read before writing this separate
implementation; this is not a blind audit or a new departure lemma.

## Result

For each provider, the checker verifies all **91** restored-helper coordinate
identities against **520** independently replayed non-target input rows. It
reconstructs entry-frame bounds from the scalar/warp chronology and enumerates
**27** candidate frames: **17** have no possible reader and **10** have a full
column-rank departure matrix. The complete results for the two providers agree.

The following determinants refer to the ordered columns and selected rows in
[RESULT.json](RESULT.json). Integer minors clear each selected row's positive
denominator; the rational determinant divides by the product of those scales.

| Register | Candidate frames | Columns | Integer determinant | Rational determinant | Restricted-row rank |
|---|---:|---:|---:|---:|---:|
| 5 | 3 | 10 | 1 | 1/4 | 2 |
| 34 | 3 | 8 | -2 | -1/2 | 2 |
| 44 | 3 | 6 | -1 | -1 | 2 |
| 54 | 3 | 6 | 2 | 1/2 | 2 |
| 73 | 3 | 10 | -1 | -1/4 | 2 |
| 105 | 3 | 6 | -1 | -1 | 2 |
| 414 | 3 | 6 | -1 | -1 | 2 |
| 430 | 3 | 6 | -1 | -1 | 2 |
| 69 | 2 | 2 | -1 | -1 | 1 |
| 444 | 1 | 2 | -1 | -1 | 1 |

There is exactly one rank-obstructed frame per register. All remaining
candidates have no reader. The eight split registers have forced dimension-5
entry frames, no reader at entry, dimension-9 ends, and three possible
dimension-6 first frames inside their dimension-7 receiver caps.
Thus none admits a two-jump `5 -> 6 -> 9` restore chain in the stated model.
For 69 and 444, every admissible entry frame excludes a direct departure to
FULL without an intermediate visit.

Restricting the departure rows to receivers whose ends contain the candidate
frame loses rank in **all ten** cases. Each receipt includes an explicit
nonzero null vector for that restricted matrix, and verifies that the full
matrix detects it. This independently reconstructs and makes inspectable the
row-restriction failure control of PR3114; the control itself is credited to
that predecessor.

## Why these matrices give an obstruction

Use the fixed-prefix, fixed-end, monotone scalar-restore model of
[PR3114's proof](https://github.com/CrocSwap/integer-mult-bounds/blob/c88769c350977d9ed4f90fe5c652d582cfe2782a/research/rank7-skip-restore-optimum/README.md#proof).
Let `e_q` be the non-target rows at restore entry, `L_q` their entry-frame
lower bounds, and `E_q` their fixed end frames. A restored helper `c` must end
at its own arbitrary input `x_c`.

1. **Forced coordinates.** Independently replay the non-target A/B prefix over
   sparse rational free-warp words. Each ADD has distinct operands, each SCALE
   is nonzero, and each warp is an invertible free-group symbol. Target-only
   corrections/wrappers/cut cannot feed back into these rows. The resulting
   520 non-target rows are therefore independent. The literal restore supplies
   candidate coefficients `M[c]`, but the checker separately verifies
   `sum_q M[c,q] e_q = x_c` for every restored helper. Uniqueness makes these
   coefficients necessary for every exact restore. An empty or damaged restore
   fails this identity; it cannot define its own acceptance condition.

2. **Frame constraints.** A nonzero `M[c,q]` with `q != c` requires a
   chronological gate path from `q` to `c`, so the entry frame of `q`
   lies inside `E_c`. Build an event DAG with shared vertices for ADD operands,
   warp resets and cut/warp last-use equalities. Forward unions give lower
   bounds; backward intersections propagate end frames, these forced caps
   and fixed equalities. Both operands' subsequent uses matter: in particular,
   the dimension-8 receiver caps of 69/444 alone are insufficient, while their
   reconstructed entry upper bounds have dimension 7. This is set dataflow,
   not cost minimization. A possible reader at `G` must satisfy
   `L_y <= G <= E_y`; absence is a necessary-condition rejection.

3. **Departure.** Suppose register `r` stays inside `G` until it departs to
   `E_r`. For the invertible restore-prefix matrix `A_t`, its inverse column
   `d_r = A_t^-1 e_r` is nonzero. An ADD `t += k*s` replaces inverse column
   `d_s` by `d_s - k*d_t`. Recursing backward through these updates, every
   contributing register has an earlier frame inside `G`; monotonicity gives
   support in `Z = {r} union {y != r : L_y <= G}`. Targets are excluded because
   they cannot feed into a non-target restore.

   Let `O = {c restored : c != r and E_r not<= E_c}`. After departure there
   can be no gate path from `r` to any `c in O`. The remaining restore matrix
   therefore has zero `(c,r)` entries, equivalently `M[O][Z] d_r = 0`.
   A nonzero square minor with all `|Z|` columns contradicts this nonzero
   kernel vector. Crucially, `O` includes receivers that cannot themselves
   sit at `G`, and `Z` includes registers that can sit strictly below `G`.

4. **Bounded application.** For the eight split registers the entry frame is
   forced and has no reader. A two-jump split with first dimension 6 must
   deliver its required contents at that intermediate frame. The receiver
   intersections give all three candidates, each excluded above. For 69/444,
   enumerate the entire admissible entry interval and exclude each possible
   skip in the same way. This does not enumerate arbitrary restore programs:
   the inverse-column argument supplies the necessary condition for them.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-departure-minor-audit --check-only
python3.12 -B scripts/research_package.py --package research/rank7-departure-minor-audit
```

The first registered command recomputes and byte-compares the deterministic
receipt. The second runs eight behavioral test groups under optimized Python.
Those include a separate rational Gaussian determinant calculation for every
minor, singular-minor controls, corrupt source bytes, an empty restore, a wrong
restored-helper coefficient, a changed prefix with unchanged restore, target
feedback and singular gates, an inconsistent cut equality, and deletion of a
required departure coordinate. Mathematical null controls run in every replay.

To regenerate the receipt after an intentional code change:

```sh
python3.12 -B research/rank7-departure-minor-audit/verify.py --write
```

Observed locally with CPython 3.12.14 on Windows. Checks use explicit exceptions,
so `-O` does not disable acceptance conditions. No full PR3114 replay, native
transport/phase validation, complete target endpoint, cleanup/allocation invoice,
moment enclosure, or selected cold replay is included. The model's legal gate
and restored-helper endpoint requirements are inherited from the cited proof;
this checker is not a replacement for the full BORROW-WORD auditor.

## Selection and overlap

Base: canonical main `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, refreshed
unchanged before submission; priority revision 6. Card `independent-moment`,
scope key `c191650c0fa8d2fa514e`; the preserved original card and refinement
are in [TASK.json](TASK.json). The card's baseline command stopped at a missing
selected assembly in the sparse checkout; no baseline PASS is claimed.

[PR3050](https://github.com/CrocSwap/integer-mult-bounds/pull/3050) already covers
the PR3042 restore-splice audit initially considered, so that duplicate was
stopped. [PR3056](https://github.com/CrocSwap/integer-mult-bounds/pull/3056)
covers a local contraction; [PR3057](https://github.com/CrocSwap/integer-mult-bounds/pull/3057)
and [PR3065](https://github.com/CrocSwap/integer-mult-bounds/pull/3065) cover frame
optimization with fixed scalar order. PR3114 adds the arbitrary-restore claim
and its own checks. This package adds separate coordinate/frame reconstruction,
explicit determinant witnesses and null vectors for ten of its obstructions.
It does not reproduce its full bound, classification or payer-group proof.

The handoff/start-here/active Discussion pages and targeted live PR searches
were inspected. The offline overlap helper had sparse local coverage and no
remote cache; Discussion pagination and arbitrary code diffs were not exhaustively
searched. No-match is not a novelty guarantee.
[PR3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133) changes helper
ends and B routing; the fixed-end result here makes no claim about that word.

## Open next questions

The structured questions in [TASK.json](TASK.json) identify two useful follow-ups:

- Independently reconstruct PR3114's remaining lower-bound terms and the
  disjoint charging proof. Start with the pinned empty-restore optimum and
  remaining blocked/zero-sum/lift groups. These require a separate exact
  optimizer and proof review; the ten minors do not settle them.
- For a concrete A/B or helper-end rewrite, first identify the changed
  coordinates and frame intervals. Old witnesses only apply if their premises
  remain true; a new source-bound word and its admission evidence are needed.

## Credit

The departure lemma, ten cases and original restriction control are due to
Marius-Paul Dumitrean (PR3114, with Claude Code); the two words are dcharb78's
PR3042. Retain credit for the PR2979 joint construction (Marius-Paul Dumitrean),
PR3015 and its declared-edit lineage (Jeremy Kothe), PR2917 (Mason Hale),
PR2908 (Jeremy Diviney), and the PR2833 free-algebra auditor (icekylinx).
Nick Petalas's independent audits in PR3050/3056/3057/3065 supply the overlapping
coverage described above.

Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance in analysis, implementation, tests and exposition. No separate agent,
independent human or proof-assistant review is claimed. New work: Apache-2.0.

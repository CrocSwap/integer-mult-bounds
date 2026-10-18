# Diagonal freedom has an exact rank price on P112

**Scoped structural result; no new kappa or supplier.** On the pinned P112
unit, any complex matrix K of rank at most q=8,...,20 that agrees with 2G
on **all off-diagonal entries** can change at most q-8 diagonal entries.
Its rank is exactly eight plus the number of changed diagonals. Thus an
eight-term decoder with this mask is already all-pairs exact, and a
nine-term decoder can alter at most one diagonal entry.

This is a side result from the `complex-masked-decoder` assignment. It
changes the mask to diagonal freedom; it does **not** solve PR717's
E-graph mask, which fixes diagonals and frees odd-pair entries. The
proof bounds arbitrary complex diagonal completions, not just a sample
or the coordinate decoder's connected component.

[PROOF.md](PROOF.md) uses an elementary antichain argument: any 36 of the
64 even-parity half-root lines span eight dimensions, and the maximum
35-line zero set is sharp. Rank subadditivity followed by an unchanged
Gram-block pivot gives the completion theorem. After removing p_h<=12
half-root lines, it covers q=8,...,20-p_h, regardless of sparse-line
deletions. These are sufficient bounds, not optimal deletion thresholds.

The inherited PR1077/PR968 eight-term copied-information floor therefore
still gives cost >=64 on P112 when only diagonals are freed. That value
and the all-pairs floor belong to the predecessors. Nine-term cost floors
remain open here. A coordinate decoder plus one diagonal correction
costs 65; this is an example, not a claimed minimum.

## Reproduce

Python 3.10+ and standard library only, from the repository root:

```sh
python3 -I -O -B research/complex-diagonal-mask-rigidity/verify.py
python3 -I -O -B research/complex-diagonal-mask-rigidity/controls.py
python3 scripts/research_package.py --package research/complex-diagonal-mask-rigidity --check-only
python3.12 scripts/research_package.py --package research/complex-diagonal-mask-rigidity
```

Expected: `PASS_COMPLEX_DIAGONAL_MASK_RIGIDITY ... controls=8 no_new_kappa`.
Default verification is read-only. `--write /new/file.json` writes a fresh
receipt and refuses to overwrite it. [RESULTS.json](RESULTS.json) records
224 exact Q(i) singleton minors, support counts zero through twelve,
thirteen puncture-boundary fixtures, all 12,544 coordinate Gram entries,
the sharp half-root zero set, coordinate costs and eight rejection controls.
The universal result comes from the proof; these fixtures do not exhaust
complex coefficients or puncture sets. Checks remain active under `-O`.
The six package controls also check an isolated, read-only positive replay
and rejection of source drift, missing pins, changed or omitted minor
evidence, and overwrite of an existing output.

## Scope, overlap and accounting

Base main: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Chooser nonce:
`1fc4813c44d07983b0bd6c1ed23e6548`; track `complex-mechanisms`, task
`complex-masked-decoder`, proposed scope key `7acfe4d9cac04f7ba4cb`.
[TASK.json](TASK.json) declares the changed scope and its limited
connection to the binding complex decoder cost. [SOURCES.json](SOURCES.json)
pins live inputs and historical provenance, and [VERIFY.json](VERIFY.json)
registers the bounded replay without editing any existing workflow.

[OVERLAP.json](OVERLAP.json) records public open-PR coverage and relevant
heads. PR1191's one-sided E-graph rigidity, PR1212's global E-graph
rigidity, PR1213's coordinate-component audit and PR1292's local P104
rigidity concern a different mask. PR1236 and its independent audits
restrict E-graph atom supports; this theorem has unrestricted factors
and an off-diagonal mask. Their contributions are not recertified here.
No matching scope was found; incomplete Discussion coverage and absent
diff searches prevent any assertion of exhaustive novelty.

Even granting preparation, frame, restoration, hosting and diagonal-repair
charges zero, freeing only diagonals cannot reduce the eight-term identity
or its inherited cost floor. This excludes one relaxation, not a better
complete moment or a physical implementation. No cold supplier replay,
proof-assistant verification or full multiplication theorem is claimed.
The cost corollary retains PR968's flat-classification premise; the
completion theorem does not need it.

## Open next questions

1. Is the sufficient range q<=20 sharp on P112? A stronger spanning bound
   may price diagonal freedom at larger term counts. First enumerate
   root-hyperplane zero sets or find a rank-21 completion violating the
   formula. A proof of the stronger deletion bound is missing.
2. Can a nine-term factorization of 2G+delta e_i e_i^T lower separate-term
   copy cost below 64? The rank theorem reduces diagonal freedom at nine
   terms to this family. First solve exact support constraints for one
   representative port and fully price a candidate. An algebraic cost
   argument and a physical contract are missing; the coordinate-plus-
   correction example costs 65.

These structured handoffs are also in TASK.json.

## Credit

Prepared for **Arham-Tahir64** with substantial **OpenAI Codex** assistance
in selection, mathematics, implementation, validation and writing.
Apache-2.0 under the repository license; no independent human review.

- DreamingOfClouds, PR717: E8/P112 geometry and masked-decoder question;
  PR446/595: separate-term physical interpretation and format context.
- themilkman216, PR968: exact eight-term puncture floor; woklerx, PR1077:
  arbitrary complex coefficients with ordinary transpose.
- Mihir Srivastava, PR845: exact in-repository geometry snapshot used for
  binding; Joel Pulikkan / GamingPuzzled, PR620: coordinate copy cost 64,
  with the retained icekylinx and E8 supplier lineage.
- Philipp / mightyOil (PR1191), Brett Halligan / burntout76 (PR1212),
  David Arias (PR1213/1236) and Navinor (PR1292) retain their related
  E-graph results. No predecessor files are changed.

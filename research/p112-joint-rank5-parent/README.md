# Joint rank-five cuts beat one-sided cuts on a fixed P112 star parent

For the P112 cost-seven parent with PR1347 tags **[7,0]**, arbitrary joint support restrictions of pairing rank at most five meet at most **1060 of 1260** orthogonal frames. This bound is attained by 384 maximal joint cuts. Row-only cuts reach at most 1020; column-only cuts reach at most 990. Thus the one-axis reduction that suffices for rank-six capacity does not suffice after another rank drop.

This is a complete local support-capacity theorem for one named parent, not a census of all parents or a constructed decoder. The normals, source root order and attaining row/column sets are explicit in CERTIFICATE.json. The optimistic single-term copy price is its exact F2 pairing rank5; helper endpoints, source access, frame changes, restoration and recursive charges are zero in this necessary screen and would require a separate realization. No moment or kappa improvement is claimed.

## Completeness proof

Write the rank-seven parent matrix M=XY using full-rank factors of inner dimension seven over F2. Let a restricted row set span dimension x in X and a restricted column set span dimension y in Y. Sylvester's inequality gives rank(M_restricted) >= x+y-7.

If the restricted product has rank at most five, either x<=5, y<=5, or x=y=6. In the first case the row vectors lie in the common kernel of two independent functionals. Expand the row set to all original rows satisfying those equations and restore every original column. This dominates the original support and still has rank at most five. The y<=5 case is transposed. There are exactly 2667 two-dimensional dual subspaces in a seven-dimensional binary space; the enumeration uses the canonical smallest two nonzero elements of each plane.

For x=y=6 each factor span is a hyperplane. Expanding both sets to their full hyperplane slices does not change those spans, hence preserves the product rank. Enumerating all127x127 ordered nonzero functional pairs yields 8001 rank-five and 8128 rank-six products. The latter are rejected. Together the three cases dominate **every** arbitrary joint restriction of rank at most five. Frame intersection is monotone under expansion, so the exact maximum over13335 dominating candidates is a universal upper bound for this fixed parent.

The complete census also records a caution: 45 of the 2667 two-plane cuts on each side have rank **three**, not five; the other2622 have rank five. All are retained, so the proof does not assume a generic dimension that the actual root supports violate. Joint cuts attain1060, strictly above the one-sided maximum1020, furnishing a concrete counterexample to extending the rank-six one-axis optimization shortcut verbatim.

## Reproduce

Python3.12+, standard library, from the repository root:

```
python -I -B research/p112-joint-rank5-parent/census.py
python -I -O -B research/p112-joint-rank5-parent/census.py
python scripts/research_package.py --package research/p112-joint-rank5-parent
```

The complete receipt and ordered support-stream digest are regenerated and compared. Controls retain the rank-seven parent, reject a single cut priced at five and incompatible joint cuts, and verify the explicit rank-five maximizer. The normal and optimized runs use explicit exceptions, not assertions.

## Open next questions

Do the other cost-seven parent orbits have the same rank-five maximum? First identify and prove a symmetry reduction before repeating the joint census; one parent does not establish a global bound. A favorable dictionary would next require simultaneous diagonal/frame coverage, exact complex coefficients and a complete physical invoice.

## Credit and overlap

PR1347 (Cinna Davis, @1337isnot1337, with OpenAI Codex assistance) establishes the full rank-six one-axis/joint reduction and leaves lower-rank descendants outside scope. Its exact P112 root order is preserved in inputs/MODEL.json at64fd5f9e91961dedc16118fcc7ad71ee82efe28f; DEPENDENCY.json pins its Git blob and SHA256. The original E8/mask lineage is DreamingOfClouds PR717, themilkman216 PR968, Navinor PR1226, David Arias PR1236, Hanson Sun PR1242 and Cinna Davis PR1323. This result changes the rank threshold and requires an additional two-sided case, rather than changing an optimizer seed. All work is Apache-2.0; new proof and implementation prepared for woklerx with substantial OpenAI Codex assistance. No independent human review is claimed.

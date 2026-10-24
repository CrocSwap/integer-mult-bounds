# Exact query capacity for every unequal odd cycle

For every C_(2k+1), k>=2, arbitrary nonnegative payload widths d_i and every
field, the exact fitting rank is

    max(maximum independent-set payload weight, ceil(total payload/2)).

Allowed ordered edge blocks may be rectangular, nonsymmetric and noncommuting.
[PROOF.md](PROOF.md) proves the all-field lower bound and an attaining integral
edge/private-channel factorization. The compressed deterministic constructor
uses O(n log(max(d)+2)) integer operations, without expanding payload coordinates.
This is a query-dimension contract, not a physical supplier or new kappa.

Seven width-two payloads need seven coordinates, while two separate scalar
rank-four solutions would need eight. The unequal C7 (2,1,2,1,2,1,1) needs six
coordinates: its weight-six independent set is stronger than half-total five.
Seven unit payloads instead need four, stronger than independent-set weight three.

## Scope and family decision

This extends Tekalign #3362's C5 interface to all odd cycle lengths, alongside
Nick Petalas #4909's bipartite-mask result. It changes the mask class, retaining
the same complete ordered zero and identity-block contracts. All rotated
one-edge-plus-isolates subspaces establish the new general lower-bound step.
Classical matching, vertex-cover/LP and odd-cycle index-coding methods retain
credit; no literature priority or new general matching algorithm is claimed.
The bounded finite census does not establish the universal theorem by itself.

Family decision: EXPAND once to close this exact mask contract, then STOP at
that result. No source-bound P112 realization is asserted. Physical reads,
copies, dirty restoration, frames, ownership, hosting, preparation, numerical
stock/precision, fixed tapes, compiler and outer recovery remain UNKNOWN.
A dimension optimum does not price them as free or improve the selected result.

## Reproduction

Use Python 3.12 and only its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/odd-cycle-query-capacity
python3.12 -I -O -B research/odd-cycle-query-capacity/verify.py
```

The read-only replay checks every width vector in {0,1,2,3}^5, {0,1,2}^7
and {0,1}^9 against independently enumerated coordinate sharing and independent
sets. It checks all attaining matrix entries and ranks over GF(2), GF(3) and
GF(101), every directed binary scalar fitting matrix on C5/C7, malformed inputs,
underpaid/incorrect channel recipes and a forbidden ordered block. An eleven-
vertex fixture uses 4097-bit widths while retaining only O(n) integers. Exact
counts and the deterministic recipe digest are in [RESULT.json](RESULT.json).
An independent column-span implementation checks 288 directed rectangular-block
fitting matrices, all rotated subspace inequalities and a sharp seven-width-two
attainer with noncommuting allowed blocks. Source/receipt corruption must fail. Hosted CI and independent mathematical
acceptance are not asserted here.

Canonical base bee95ce88f9f19802f0613f92838895cd0e14a1f, priority revision 7,
selected conditional kappa 0.00302015 unchanged. Initial overlap covered 310
open PRs, 4096 Discussion records and all 6690 tracked package notes, with
reported complete inventories; absence of a match is not proof of novelty.
The canonical investigation is Discussion #1587. Exact predecessor bytes and
the original card are retained in SOURCES.json and TASK.json.

## Open next questions

1. Determine a named triangle-free mask with overlapping odd cycles for which
   arbitrary fitting blocks improve on integral coordinate pairing. First
   compare its rank-factor subspace constraints with its complete edge-sharing
   LP; no physical decoder should be assumed.
2. Exhibit an actual recursive caller whose admitted ordered read mask is one
   of these longer odd cycles, with all query/source/copy and cleanup costs.
   A geometric/matching realization and complete consumer tariff are blockers.

Credit Tekalign #3362, Sagar Thakrar #2484, ywz65 #2471, Nick Petalas #4909,
Cinna Davis, Adam Gall, ctoth, Philippe Van Velzen and the retained P112/native
lineage. New scoped proof, constructor and checks: JoyboyBrian, with substantial
OpenAI Codex assistance. Apache-2.0. No human or proof-kernel review claimed.

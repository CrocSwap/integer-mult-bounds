# Four-stage rank budget and coupled incidence rigidity

For a shortest `n+1`-query root on `nq` arbitrary independent inputs, with
four compatible, pairwise commuting full-stage projectors that commute
with their actual chronological prefixes, total stage rank is at least
**10q**. The field has characteristic different from two and n is even.
The bound is attained for every even n>=6 and every q>=1.

The main structural result concerns the extreme sites **0,1,n-1,n**.
Equality at10q forces ranks **(2q,3q,3q,2q)** and exactly this inventory:

| Stage product | Independent coordinates |
| --- | ---: |
| ABCD | q |
| AB | q |
| CD | q |
| B | q |
| C | q |
| Empty | (n-5)q |

Every output also receives the central involution S. The proof permits
arbitrary internal coupled matrices; it does not classify them by tensoring
scalar stages. Consequently n=4 cannot attain10q, including q=2 total20.
At q=2, total19 is excluded at every even n. The equality classification
has not been proved for arbitrary non-extreme odd sites.

Additional necessary four-stage bounds are11q when an even interior is
selected,21q/2 with one endpoint and three odd interiors, and32q/3 with
four odd interiors. Distinct odd sites separately satisfy two directed
extra-rank inequalities, giving an odd-pair total at least16q/3.

[FOUR-STAGE-NOTE.md](FOUR-STAGE-NOTE.md) contains the universal proof,
the precise hypotheses and the all-even extension of Ali Romman's #6398
attaining word. The aggregate bounds combine retained leakage tools from
#6717, #6721 and #6734. No new local leakage mechanism or scalar attaining
root is claimed. The new structural conclusion is the coupled extreme-site
incidence classification.

## Exact reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/p104-four-stage-rigidity/check.py
python3.12 -I -O -B research/p104-four-stage-rigidity/check.py
```

The checker authenticates retained source bytes; independently performs
exact Fraction matrix operations; reconstructs420 zero-paired closures;
checks the source n6 root; and checks six (n,q) attaining fixtures including
coupled q2/q3 with192 complete formal coefficient matrices. It enumerates
finite joint-sector constraints for q1 through5, checks ordered coupled
block identities, and rejects omitted queries/stage coordinates. Near-site,
missing-commutation and missing-prefix examples control hypothesis
boundaries. The universal conclusions rest on the written proof, not on
extrapolation from finite fixtures. No predecessor executable is imported.

## Scope and credit

This is a coefficient-space theorem and abstract exact word. There is no
new kappa, complete paid invoice, physical supplier, native phase or port
mapping, helper/ownership discharge, or all-size compiler/precision/analytic
admission. All five selected assumptions remain. The selected frontier is
unchanged. A favorable rank inventory is not a profitable supplier.

Ali Romman retains the scalar n6 word and source classification, normal-form,
closure and rank-method credit. thu-nmrc #6717 retains the all-even coupled
three-stage theorem and leakage application. ToikY #6721/#6734 retain the
independent written leakage audits and one-prefix extension. Cinna Davis and
the original query/controller contributors retain their lineage credit.
Exact source commits, paths, Git blobs and SHA256 values are in
[ORIGINS.json](ORIGINS.json); original text notices are unchanged.

Prepared for @CubeJerry with substantial OpenAI Codex assistance, including
separate source-aware AI proof review. Apache-2.0. Independent human and
proof-kernel acceptance are unclaimed.

## Open next questions

Classify equality at other odd-site placements, determine whether four-field
coupled totals strictly between10q and11q occur, or supply a changed root
with a complete profitable native invoice. Any such supplier must retain
all independent inputs, actual prefixes and ordinary/physical charges.

The registered command is `python3.12 -B scripts/research_package.py --package research/p104-four-stage-rigidity`. Frozen sources are authenticated locally by `ORIGINS.json`; their original pending heads are provenance, not generic Git-history dependencies. `SOURCES.json` pins the originating main catalogue, selected record and license. No full-history preflight, selected cold replay, hosted CI or scientific admission is claimed. See `REVIEW.md` for separate source-aware review.

# Complete automorphisms of F_q[x,y]/(x²,y³)

This package answers PR #6682's released first unequal-cutoff question. Every
unital K-linear automorphism has

```text
X=a*x+alpha*x*y+beta*y²+gamma*x*y²
Y=c*x+d*y+delta*x*y+epsilon*y²+zeta*x*y²
```

with a,d nonzero, beta=0 unless char K=2, and c=0 unless char K=3. Every
remaining higher coefficient is free, and every allowed lift is invertible.
The group order is (q-1)²q^6 in characteristics 2 and 3 and (q-1)²q^5 otherwise.
The determinant on the full six-dimensional algebra is a³d^6, with exact image
the cube subgroup of K*. `PROOF.md` proves necessity, sufficiency and the graded
blocks; this is a fixed (2,3) result, not an all-cutoff family.

`RESULT.json` records complete accepted-set digests and determinant histograms
for F2,F3,F4,F5, totaling 89,844 maps, plus 180 specified nonlinear witnesses in
F7/F13. `ACCEPTED-MAPS.json.gz` retains every actual census map as ten field
coefficients, X[1:] followed by Y[1:] in basis (1,x,y,xy,y²,xy²), sorted
lexicographically within each field. The default verifier recomputes and checks
all decompressed rows/types and the entire mathematical profile. Gzip container
hashes may vary; decompressed canonical values are the equality contract.

The primary is a normal-form constructor with literal ring relations and actual
6x6 elimination. The separate oracle enumerates raw radical relations and tests
invertible substitutions, then checks actual submitted map data. Field/case/source
pins and code seals precede first execution; raw first results are then retained; final verification
status and any corrections belong to VALIDATION.md and RUN-RECORDS.json.

From the repository root with CPython 3.12:

```sh
python3.12 -I -W error -B research/unequal-quadratic-cubic-automorphisms/verify.py
python3.12 -I -O -W error -B research/unequal-quadratic-cubic-automorphisms/verify.py
python3.12 -B scripts/research_package.py --package research/unequal-quadratic-cubic-automorphisms
```

For a new receipt, add `--emit /absolute/new/RESULT.json`; the retained map
certificate is still checked. To regenerate that certificate explicitly, also
supply `--write-maps /absolute/new/ACCEPTED-MAPS.json.gz`. Receipt admission
rejects duplicate/nonfinite JSON, wrong keys/types/version/digests, bool-as-int
and mathematical mismatches in normal and optimized modes.

The universal written proof and finite executable domain are distinct. The
program is not a public all-field arithmetic API or algebra-recognition tool.
Managed CPython 3.12.14, stdlib integer operations, fixed finite loops and small
functions are used. Dynamic containers/arbitrary-precision integers and recursive
typed JSON comparison are declared managed-code deviations from low-level
Power-of-Ten style; no such compliance is claimed. Acceptance uses explicit
checks rather than assert. Immutable inputs are six inert predecessor documents;
no predecessor program is imported or executed.

Credit: Nick Petalas's #6682 supplied the exact released question; Ali Romman's
#5316/#5459 and Petalas's #6578 supply the one-variable and characteristic-power
comparisons and retained radical/filtration/count/character methods. PR #5252
and David Ganz's atlas lineage keep their credit. Exact heads, original headers
and attribution are retained in SOURCE-PINS.json, SOURCES.md and NOTICE.

## Open next questions

- Bind the normal form to a concrete tensor-stabilizer or SL-orbit interface.
  Start from the credited isotopy bridge in #6682; recognition, transporter
  construction and all implementation costs remain separate obligations.
- Study another explicitly chosen unequal cutoff. Start by recomputing its
  defining relations and filtration, rather than assuming this parametrization;
  no all-n classification is supplied here.
- Formalize this six-dimensional proof and independently review the field
  encoding/census. Start with the displayed relation coefficients and four
  graded blocks; no proof-kernel or independent human acceptance is claimed.

No physical field preparation, register-model escape, supplier/caller saving,
semilinear field automorphism, kappa or selected-frontier change follows.

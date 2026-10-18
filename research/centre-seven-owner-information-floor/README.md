# Seven-owner blocks do not compress selected-centre information

**Exact scoped extension; no supplier or κ improvement.** For the selected
PR1094 calls 0/4 and the inherited whole-later-query observation contract,
blocks of up to seven physical cover owners still need exactly 104 additional
scalar linear observations per owner. The previous package established this
for blocks of size 1–6. This package closes its first uncovered support size by
classifying every reduced length-six relation among the 112 selected route
matrices.

This tests one possible route to a large κ change: reduce the information that
the shared centre repair has to carry. It establishes no implementation tariff
or new recursive profile, so it does not improve κ or establish that other forms
of centre sharing are impossible.

## Exact result

The inherited source-bound model has old observations `Sx(g)=R x(g)` and later
query `Tx(d)=Σ_p H[:,p] x_p(d ρ_p)`, with `H=R/4`. Each route `ρ_p` is an
involutory 73-bit binary matrix. The predecessor verifies that the 112 routes
are distinct, that all 12,432 ordered nonidentity products `ρ_qρ_p` are unique,
and that every pair of columns of `R` is nonparallel. Its written support
argument proves that any nonzero `Sx=Tx=0` perturbation touches at least seven
source owners.

The only possible support-seven incidence pattern is the Fano plane:

1. Every active owner needs at least three nonzero ports to lie in `ker R`.
2. Each output owner receiving a nonzero query contribution needs at least
   three source owners; one or two distinct nonparallel columns cannot cancel.
3. A pair of source owners can meet at no more than one output owner, by the
   unique ordered route-product property.
4. With exactly seven source owners, the pair/incidence count forces every
   source and output to have degree three, with every source pair meeting
   exactly once. This is the Steiner triple system on seven points, hence the
   Fano plane.

Any six-cycle in this incidence graph gives a cyclically reduced identity of
six route matrices. The verifier exhausts all 1,379,952 reduced products
`ρ_aρ_bρ_c` and compares matching matrices exactly. The 50 non-singleton
product classes each have size two, so this checks every pairwise equality; it
finds 50 cyclically reduced length-six relations, all braid relations
`ρ_aρ_bρ_a = ρ_bρ_aρ_b`. The 50 route-label pairs in those relations form a
graph with no triangles.

In the Fano plane, take any owner and any two of its three incident output
lines. Those two incidences lie on a six-cycle: choose one other owner from
each line and join them on the third line. The route labels at the original
owner must therefore be a braid pair. Applying this to all three pairs of its
three distinct port labels would create a triangle in the braid graph, which
does not exist. So support seven is impossible. Together with the predecessor's
support-one-through-six proof, `ker S ∩ ker T = {0}` on every owner block of
size at most seven. The exact repair minimum stays `104 |B|` observations for
each such block; reading 104 complementary coordinates per owner attains it.

## Reproduction

From the repository root, Python 3.12 and the standard library are sufficient:

```sh
python3.12 -I -B research/centre-seven-owner-information-floor/verify.py
python3.12 scripts/research_package.py --package research/centre-seven-owner-information-floor --check-only
python3.12 scripts/research_package.py --package research/centre-seven-owner-information-floor
```

The direct replay first checks the pinned predecessor receipt and its selected
source bindings, then enumerates the route products and exact-resolves every
hash bucket collision. The verifier's hash is only an index: equality is decided
by comparing all 73 binary columns. The registered replay timeout is five
minutes; the measured local enumeration took about 52 seconds on the current
host, excluding startup variance.

The source snapshot is canonical main
`864290c2b9c8cde72e89ff34f5678081fb4cad42`; a later intake-only main commit
did not change any pinned inputs. Its frozen selected archive, predecessor
interpreter and prior receipt are unchanged.

## Scope and decision

This closes support size seven for the selected PR1094 call pair, route set and
full later-query observation contract. The old evidence applies to sizes one
through six; this adds the exhaustive length-six relation classification
needed for the Fano case. It does not classify blocks of eight or more, changed
query cuts, final-output-only readers, nonlinear source-dependent state,
overlapping repair blocks, or the physical cost of acquiring and restoring
observations. Information coordinates are not recursive rank or paid mass.

The user's target κ > 0.1 remains unmet. The selected supplier and transfer are
unchanged; this result does not cross any κ threshold. A size-eight block by
itself cannot establish that target. Do not continue the centre-block search
until a complete replacement endpoint passes the exact κ=0.1 optimistic
moment with positive headroom for physical costs.

## Open next questions

- **Can a complete replacement endpoint pass the κ=0.1 optimistic moment?**
  First specify its unpaid-coordinate count, rank cap, paid local profile and
  centre bill, then screen that profile before attempting a construction. It
  matters because even a positive size-eight kernel would not by itself supply
  a target-scale recursive improvement. The blocker is the absence of a
  replacement supplier and consumer with complete costs.
- **After a profile passes that target screen, can one named eight-owner block
  provide useful common-kernel dimension?** Choose one incidence pattern and
  compute `ker S ∩ ker T` exactly from the pinned matrices, then price access
  and restoration against the passing profile's headroom. No such candidate
  block or physical repair program is currently specified.

## Credit

Aaron Wang/navinor's PR2391 and Ross Richardson's
`centre-block-repair-information` provide the native centre-reuse question,
source matrix, route interface, exact route-product uniqueness and the support
lower bound of seven. ywz65's `centre-owner-observation-floor` provides the
selected `R/H` source data and owner-local result. The selected construction
authors and retained frame/ownership lineage are credited in those packages.
This contribution adds the complete reduced length-six route-relation census
and the support-seven/Fano exclusion. Prepared by OpenAI Codex with substantial
AI assistance. Apache-2.0.

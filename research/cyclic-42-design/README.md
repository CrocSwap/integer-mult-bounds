# A cyclic 42-ray uniform design with exactly one basis

In C^6, take the six coordinate rays and

    v_k = (1, zeta^k, zeta^(4k), zeta^(10k), zeta^(12k), zeta^(17k)) / sqrt(6),
    zeta = exp(2 pi i / 36),  0 <= k < 36.

These are 42 distinct rays. With uniform weight 1/42 they form a complex
projective 2-design. Their orthogonality graph is K6 plus 36 isolated vertices,
so they contain exactly one orthonormal basis, the six coordinate rays.
This gives the finite dimension-six example requested in David Ganz's atlas
[B100](../pure-math-atlas-400/volumes/02-geometry.md#b100), and shows directly
why a uniform design at cardinality d(d+1) need not be a union of bases.

Claim type: scoped written algebraic proof with a finite exact certificate.
The new result is this explicit cyclic instance with its complete
orthogonality structure. The harmonic construction, its Sidon-set criterion,
the six-mark ruler and existence of designs in dimension six retain their
predecessors' credit. Global literature priority is unclaimed.

## Proof and evidence

[PROOF.md](PROOF.md) proves the literal tensor identity

    sum_(x in X) P_x tensor P_x = I + Swap,
    P_x = x x*.

It then excludes all flat-flat orthogonality using eight nonzero cyclotomic
remainders, one for each possible order of a nontrivial 36th root. The proof
also explains why uniform weights in the coordinate-plus-flat character-orbit
model force exactly d^2 flat vectors. That restriction concerns this model.

The standard-library verifier reconstructs all 1,296 tensor matrix entries
in Q[zeta], every one of the 861 unordered ray pairs, 630 flat-ray
distinctness pairs, and all six-cliques in the resulting graph. It checks
the 21 unordered pair sums and all 35 nontrivial character differences.
Its six rejecting controls cover sum collisions, a false second moment,
a missing coordinate ray, extra orthogonality, repeated rays and an
incorrect uniform weight. The output is a generated hash-bound receipt;
no receipt is written by hand or committed.

## Reproduction

From the repository root, using CPython 3.12 and no additional dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cyclic-42-design/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/cyclic-42-design/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cyclic-42-design
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cyclic-42-design --check-source-history
```

The direct commands also run from an exported package without Git or the
predecessor files. Both registered checks have 60-second limits. Exact local
timings and hosted CI status belong in the PR body. All generated output
belongs outside the checkout.

## Scope and overlap

The scientific base is ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority
revision 7. The formal-interface-lemma card is changed to B100's algebraic
side question, rather than a formal proof or selected supplier audit.
The selected source-binding orientation passed; it is not scientific
verification of this construction. See TASK.json for the original card,
scope change and structured next questions. SOURCES.json pins the atlas,
catalogue and selected record as historical provenance. The verifier has
no runtime dependency on them.

The live open/account PR lists, active Discussions, recent claims, targeted
main-tree and merged-PR searches and cached overlap were checked. The cached
scan covered 311 open PRs and 4,493 Discussion records, with complete remote
pagination, but only 160 of 7,091 local HEAD notes were materialized before
the atlas was added. Targeted all-main searches supplement that sparse scan.
Arbitrary historical diffs and unpublished work remain outside coverage.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147110).

This does not construct seven MUBs, improve a multiplication exponent,
change the selected frontier or certify a native supplier. Acquisition,
frames, ownership, restoration, routing, stock, precision/tape, compiler
and the complete consumer bill are unpriced. Lean, Docker and the selected
supplier's cold replay are unrun. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

- Which further dimensions admit a cyclic uniform design with only its
  coordinate basis? Begin with one specified classical ruler modulo d^2
  and its cyclotomic zero test. A general existence theorem is absent.
- Can this instance serve an actual native decoder or measurement caller?
  Begin with one explicit contract and the complete acquisition, delivery,
  restoration and consumer invoice. No such cost model is supplied here.

These questions are unreserved. The investigation stops at the first
construction above; no dimension scan or ruler census was performed.

## Credit and references

produced by Nick Petalas. Apache-2.0.

David Ganz's [PR2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849)
supplies atlas B100's finite example request and B042's moment convention.
Gary S. Bloom's classical ruler is used without a novelty claim for its marks;
see [A counterexample to a theorem of S. Piccard](https://doi.org/10.1016/0097-3165(77)90013-9).
Bernhard G. Bodmann and John Haas supply the
[harmonic construction](https://arxiv.org/abs/1509.05333).
John Jasper and Dustin G. Mixon's
[Theorem 7](https://arxiv.org/html/2501.14938v1#S2)
gives its Sidon-set formulation and cites Bodmann and Haas's construction.
Their methods are cited premises, not audited deliverables or original results
claimed here. The literal moment calculation and full orthogonality proof
above are self-contained.

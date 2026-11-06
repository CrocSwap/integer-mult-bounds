# A rank-four obstruction to cube parity bases

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite corroboration. No new kappa.**

A saturated rank-four lattice in Z^10 can be rationally spanned by its cube
vectors while those vectors miss one direction modulo two. The example has
exactly eight nonzero cube vectors. Their integral span has index two; their
binary rank is three, while the full lattice has binary rank four. Every
vector in the missing coset has a coordinate of magnitude at least two,
and an explicit vector attains two.

The [proof](PROOF.md) displays the four-by-ten matrix and determines the
entire lattice. In its row coordinates the lattice is

```text
Z^4 union ((1/2,1/2,1/2,1/2) + Z^4).
```

Eight sign evaluations identify the maximum coordinate with the sum of the
four absolute row coefficients. This excludes the half-integral coset from
the cube and identifies every remaining cube vector.

This is a new obstruction to extending a BIT relation-lattice reduction.
Ali Romman's [three-register proof, section 7](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/bit-three-register-lower-bound/README.md)
already proves that rational cube generation supplies a parity basis in
relation rank three. The present example shows failure at rank four.
CubeJerry's [PR #6777](https://github.com/CrocSwap/integer-mult-bounds/pull/6777)
raised saturation in its arbitrary-register continuation. Its two-relation
theorem is credited and is not a replay target here. The initial claim's
rank-three lemma was found already on main; the [scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19441252)
records the change to this original rank-four counterexample.

## Reproduction and finite evidence

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error -X dev research/rank-four-cube-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error -X dev research/rank-four-cube-parity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rank-four-cube-parity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rank-four-cube-parity --check-source-history
```

Other machines can substitute their CPython 3.12 executable. The standalone
verifier requires no Git, network, predecessor import or third-party package.
It emits JSON with `PASS_RANK_FOUR_CUBE_PARITY`. The registered runner also
emits `PASS_REGISTERED_RESEARCH_PACKAGE`.

The direct verifier checks:

- Every one of the 59,049 ambient vectors in {-1,0,1}^10. Exactly nine are
  in the rational subspace, including zero.
- All 210 maximal minors of each displayed basis. The original four rows
  have minor gcd two; the saturated basis has minor gcd one.
- The binary ranks three and four and the explicit missing class.
- A separate 6,561-point half-integral coefficient box. Its 881 lattice
  points contain all 57 vectors of height at most two, including sixteen
  representatives of the missing coset. Completeness at height two follows
  from the proved absolute-coefficient identity.
- Eight omission controls. Removing each sign column separately admits an
  explicit cube vector from the previously excluded coefficient coset.

An optional `--receipt PATH` writes a generated receipt outside the package,
bound to the SHA256 of every package file and the interpreter environment.
No handwritten receipt or stored verifier output is used. Local validation
uses CPython 3.12.15 on macOS arm64. Hosted validation is a separate gate.

## Scope, credit and limits

The exact main base, original card and source blobs are in [SOURCES.json](SOURCES.json).
[TASK.json](TASK.json) records the changed `bit-new-register-model` scope,
novelty correction, overlap limits and structured next questions. The card's
first current selected-baseline check passed for canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision eight. This was
source-binding orientation only. Selected conditional kappa remains
0.003125804, with all five framework assumptions retained.

Credit Ali Romman for the existing rank-three parity-basis proof; CubeJerry
for the arbitrary-register saturation question and two-relation work; and
eumemic, David Govea and woklerx for the formal register and relation methods
credited in those sources. The construction and its exact lattice/cube
classification here are new. Sign evaluations, integral saturation and
index arguments are classical; no general literature-priority claim is made.

The abstract quotient Z^10/L is free abelian of rank six. No realization of
its generators by rational rank-one matrix frames, scalar projector word,
physical supplier, target/paid invoice, native implementation, dirty
restoration, compiler, precision/tape or complete multiplication theorem is
supplied. This rank-four example does not settle the eight-call span-five
problem, whose relation rank is three. Minimal ambient dimension is unknown.
Independent human and formal proof-kernel review are unclaimed.

The verifier has no recursion. Its domains are fixed at 59,049 ambient
vectors, 6,561 coefficient candidates, two sets of 210 minors and eight
omission controls. Each function is below 60 lines. Explicit exception checks
remain enabled under optimization. Python's managed allocations deviate from
fixed native memory; all live collections and loop domains are bounded by
these finite inputs. Warning-strict development mode is used in both
registered checks; no separate static analyzer or native-memory claim is made.

## Open next questions

- Determine the smallest ambient dimension for a rank-four cube-parity
  defect. Start with dimensions five through nine and exact cube intersections.
  This package supplies no lower bound on that ambient dimension.
- Determine whether a defect of this kind can be realized by rational
  rank-one paid frames in a legal BIT word. Start with the rank-six quotient
  generators and their rank-one minor equations. An abstract exponent quotient
  does not provide the matrix realization, endpoints or complete bill.

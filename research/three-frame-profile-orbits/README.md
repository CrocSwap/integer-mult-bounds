# Count-profile symmetry of the three-frame character test

**No new κ and no word.** The selected record is unchanged.

In the PR2085/2112 register model with three added signed rank-one frames,
eight linear symmetries of the address space permute the old labels
`A, B, P, Q` and the four targets. They carry the whole character table of a
decomposition of one old-count profile to its image. This gives three
results about the census of discussion comment 19377345.

1. **`(1,1,2,0)/(1,1,1)` admits no seven-call word.** It is the image of
   `(2,0,1,1)/(1,1,1)` under the map that exchanges `A` with `P` and `B` with
   `Q`. This is a scoped proof, conditional on the exclusion theorem of open
   PR #7035 (or of open PR #7051) and on the inherited first-order
   inequality. PR #7051 names this profile as not settled.
2. **The sixteen profiles still open are three orbits**, of sizes 8, 4 and 4.
   One argument per orbit is enough.
3. **Twelve of those sixteen are not character-excluded.** For the 8-orbit
   and for the `(1,1,2)` 4-orbit an explicit rank-one decomposition passes
   every additive character. The argument of #7013, #7035 and #7051 cannot
   be repeated there. Both witnesses fail target support, so an exclusion of
   those orbits has to combine characters with target support or another
   invariant.

The statements, proofs and limits are in [PROOF.md](PROOF.md).

| Orbit | Profiles | Status |
|---|---|---|
| `O1` | `(1,1,1,1)/(1,1,1)` | excluded by #6942 |
| `O2` | `(2,0,1,1)`, `(0,2,1,1)`, `(1,1,2,0)`, `(1,1,0,2)`, all `/(1,1,1)` | excluded; `(1,1,2,0)` is new here |
| `O3` | eight profiles such as `(2,1,1,0)/(1,1,1)` | open; a character-surviving decomposition exists |
| `O4` | `(0,1,1,1)` and its three images, `/(1,1,2)` | open; a character-surviving decomposition exists |
| `O5` | the same four old profiles, `/(1,1,1)` | open; every box triple is character-excluded |

The surviving decomposition for `(2,1,1,0)/(1,1,1)` is
`-B + (5/2)Q + (1/4)(1,3)(1,3)^T`. For `(0,1,1,1)/(1,1,2)` it is
`(1/2)B + (1/2)(2,1)(2,1)^T + 2Q`.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The
card asks for a larger or nonabelian native alphabet. This package stays in
the abelian symmetric 2-by-2 model and answers the open question of PR #7051
about the remaining three-frame count profiles. See [TASK.json](TASK.json).

Four kinds of evidence are kept apart.

- **Proof:** the symmetry lemma and the transport lemma (PROOF.md, Sections 2
  and 3).
- **Scoped proof, conditional:** the exclusion of `(1,1,2,0)/(1,1,1)`. It
  uses the theorem of #7035 or #7051 and the premises of PR #6190, Section 1.
  None of them is reproved or replayed here. #7035 and #7051 are open and
  unreviewed.
- **Finite certificate:** the two surviving decompositions, with their full
  tables of eight characters, transported to all twelve profiles of `O3` and
  `O4`.
- **Bounded search:** the box counts of PROOF.md, Section 6. They cover
  frames on 24 lines and are not a classification.

`verify.py` checks the eight maps exactly, enumerates all 24 label
permutations, checks residual equivariance on all 35 four-call profiles,
computes the census orbits, recomputes both survivor tables on twelve
profiles, runs 11,264 transport comparisons, and reproduces the box counts.
It has six failure controls.

Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record, the catalogue and the two predecessor proofs on `main`
are historical provenance. PRs #7013, #7035 and #7051 are open and are cited
by number and head commit; their bytes are not vendored:

- #7013 `research/three-signed-b-twice`, head `ed127d7ab6067daf8a48def1445da5864ad113df`
- #7035 `research/three-signed-a-twice`, head `e0026d8fd0d8c3eef46391e3e3e540c15279eec5`
- #7051 `research/three-signed-q-twice`, head `7af3a03dade6bd166ad08d7afc6879b0726fe100`

Full Git history is needed to resolve the provenance pins.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/three-frame-profile-orbits
python3.12 -I -W error -B research/three-frame-profile-orbits/verify.py
python3.12 -I -O -W error -B research/three-frame-profile-orbits/verify.py
```

The last line of the verifier output is

```text
PASS_THREE_FRAME_PROFILE_ORBITS group=8 compositions=35 census_orbits=5 open_profiles=16 open_orbits=3 four_call_orbits=8 new_profile_box=1914 transport_checks=11264 survivor_profiles=12 controls=6
```

Each run takes about four seconds.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Is the six-call orbit `O5`, represented by `(0,1,1,1)/(1,1,1)` with
   `R+S+T = diag(3,2)`, character-excluded? All 1870 box triples are. A proof
   would close four profiles at once. First step: run the parity-image
   argument of #7035 with the form `3 x1^2 + 2 x2^2` in place of
   `3 x1^2 + x2^2`. Blocker: the constants of #7035 belong to `diag(1,3)`,
   of determinant 3. `diag(3,2)` has determinant 6, so the 2-adic case split
   has to be redone. It was not attempted here.
2. Does every decomposition of `(2,1,1,0)/(1,1,1)` fail a character or
   target support? In the box none of 1936 triples passes both. First step:
   describe the decompositions that pass every character, starting from the
   lattice `Z^3 + Z(1/2,1/2,1/2)` of the witness, and test the subset sums
   for `A+Q` on that family. Blocker: the character-surviving set is not yet
   parametrized.
3. The same question for `(0,1,1,1)/(1,1,2)`, where 385 box triples survive
   the characters and none of them passes target support.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The
determinant, support and character premises are the PR2910 package as
recorded by apoursh in PR #6190. The census is discussion comment 19377345.
The exclusions of `(1,1,1,1)`, `(0,2,1,1)`, `(2,0,1,1)` and `(1,1,0,2)` are
unpaidmoon's PRs #6942, #7013, #7035 and #7051; the question answered here
is the open question of #7051.

The symmetry lemma, the transported exclusion, the two surviving witnesses
and the checker are produced by Nick Petalas. New work is Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

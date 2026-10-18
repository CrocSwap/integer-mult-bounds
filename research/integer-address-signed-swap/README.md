# Price address signs in uniform integer SWAP words

For any mixture of `r` signed anti-diagonal targets in formal
`F2[GL2(Z)]`, with `t` of determinant -1, the exact minimum price is

```
r*(2*min(A,B)+max(A,B)) + t*C.
```

Here the two unit shear orientations, with either sign, cost A and B;
negating either **address coordinate** costs C. Prices are nonnegative.
All R>=r roles begin arbitrarily, scalar `GL_R(F2)` mixing is free, and all
spectators and off-diagonal couplings must be restored. A paid unit acts on
one binary rank-one scalar idempotent, not an arbitrary-rank block.
At unit prices, SWAP and minus-SWAP cost four each; the two determinant-positive
quarter turns cost three each. A binary payload sign is not an address NEG.

[PROOF.md](PROOF.md) gives the all-R, all-target, all-nonnegative-price theorem.
The inherited mod2 ADD cuts give `n_a>=r`, `n_b>=r`, `n_a+n_b>=3r`.
A separate two-sheet determinant representation gives `n_NEG>=t`: even when
t is even, the crossing rank sees t, not just its parity. The charges are
disjoint. Literal signed three-shear words, with one NEG where needed, attain
all inequalities together on complete formal endpoints.

This extends [PR2544](https://github.com/CrocSwap/integer-mult-bounds/pull/2544)
at `9fb1552f12ca4777ca660461a8b602e709285f99`; its asymmetric mod2 tariff is
credited, not rediscovered. That predecessor credits Aaron Wang's PR2444
handoff and Ross Richardson's PR1989 general ordered-pair cut and PR2415
coordinate-SWAP bridge. Its unchanged README is retained as
[predecessor-2544.md](predecessor-2544.md) for source-bound review; no source
implementation is imported. [PREDECESSORS.json](PREDECESSORS.json) pins it;
[SOURCES.json](SOURCES.json) pins the unchanged main ordered-pair proof,
with SHA-256 and Git blob IDs.

## Domain boundary

Formal equality is also forced by a **fixed finite word** valid on full integer
streams, or at every modulus in an unbounded family; the proof supplies the
finite-support separation argument. The attaining identities work modulo
every M>=2. The lower bound does **not** apply to every word optimized
separately at a fixed finite M. At M=2 address NEG is identity and three shears
already implement SWAP. Restricted clean inputs, width-dependent alphabets,
higher-rank units, free address maps and incomplete restoration are outside
the model. No physical tape compiler, completed recursive supplier, selected
frontier change or integer-multiplication theorem follows.

## Reproduce and evidence

Python 3.12+, standard library, from the repository root:

```sh
python3 -I -O -B research/integer-address-signed-swap/verify.py
python3 -I -O -B research/integer-address-signed-swap/test_boundary.py
python3 scripts/research_package.py --package research/integer-address-signed-swap
```

The fixed [RESULT.json](RESULT.json) records 930 rank-one paid-factor cut checks
(all binary projectors for R=1..4), 20 free scalar factors, 1,364 complete formal
endpoints (every mixture of up to four targets, two orientations and zero/one
spectator), 42,625 exact rational price checks and 720 deterministic mixed
paid/free prefixes. These bounded checks support the written proof; they are
not an exhaustive word search or a proof assistant formalization.

Controls detect an omitted NEG invisible to mod2 cuts, a nonzero formal
perturbation invisible to **all** quotient representations, fourteen deleted
attaining calls and a nonidempotent projector. Separate controls exhibit the
M=2 exception, negative-price identity loops and the changed higher-rank-unit
premise. Six subprocess tests check unchanged Git-free exports, source drift,
missing sources/receipt, typed receipt drift and exclusive regeneration.

Verification is read-only. `--write-result NEW_PATH` regenerates a complete
receipt and refuses an existing path. Explicit failures remain active under
`-O`. Runtime provenance and independent AI review are recorded with delivery;
hosted CI and independent human review are not asserted.

## Open next questions

1. Establish a lower bound for one named physical finite-modulus family at its
   actual widths. Start by pinning the native alphabet and proving its action
   faithful on the allowed word supports; M=2 blocks an unconditional transfer.
2. Price the literal signed words in a legal tape representation. Start with
   all ADD/NEG calls, temporary roles and restoration; native compilation,
   all-size layout and recursive eligibility remain blockers.

The structured obligations and original picker scope change are in
[TASK.json](TASK.json). Contributor: ywz65 with substantial OpenAI Codex
assistance. Apache-2.0; predecessor attribution is retained.

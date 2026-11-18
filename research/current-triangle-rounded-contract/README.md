# Rounded scalar contract for the current three-field repair

The exact rational identity in
[PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669)
does not preserve its two scalar tapes under per-ADD floor rounding on
all integer inputs. For x=236,y=544,z=1000, the new rounded tape differs
from the old by `(0,h,2h)`, where `h=floor((z mod 4)/2)`.

For `(0,1,2)`, the old tape returns the exact value `(1,1,4)`, while the
new tape returns `(1,2,6)`. Both paths fit in four signed bits. The exact
no-rounding domain changes from `2y+z=0 mod 4` to the stronger condition
`z=0 mod 4` and `y=0 mod 2`. The sharp local error against the common
rational map rises from `3/4` to `sqrt(89)/4` ticks per real triple.

This is a **common-coordinate scalar theorem**. It removes the native
MOVE instructions only in that explicit model. It does not prove that
the actual chart transports commute with rounding, establish caller
reachability, or refute the source's fine exact-grid construction.
There is no new kappa or selected-frontier change.

Read [PROOF.md](PROOF.md) for the all-integer law, its exact scope and the
sharp vector extension. [RESULT.json](RESULT.json) records all eight
residue cases, each integral prefix translation, the source binding and
fault witnesses. [verify.py](verify.py) reconstructs the complete pinned
candidate, then checks both literal local scalar tapes with separate
rational and integer interpreters. It also checks 6859 signed triples.
The full native, caller and source price replay are not run.

## Source and decision

The exact source is `95d476623f1468822057554475dc8badb19bfa44`. The
candidate is `ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d`.
[SOURCES.json](SOURCES.json) pins the current-main context.
[VENDORED.json](VENDORED.json) pins the six unchanged source files used
for this audit. The copied source directory is a partial dependency
snapshot; it is not the source's complete replay package.

This takes the source's request to review the changed three-field
identity and rounded precision contract. The rational identity and
exact-grid replay are prior evidence. The new check tests one implication
that those results do not settle. It gives a concrete residue condition
and local error constant for a later transport-aware proof. It does not
supply a free correction, numerical child or physical service tariff.
The complete native/caller precision bill is still unknown here.

## Reproduce

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/current-triangle-rounded-contract
```

Normal and optimized commands must each print
`PASS_CURRENT_TRIANGLE_ROUNDED_CONTRACT`, followed by the registered
package pass. All input and source files are local and hash-pinned.
No network, third-party library, Lean or Docker is required.

## Open next questions

What are the reachable residue classes after the literal native chart
transports at 265,751,927 in the actual sixteen-call service? Bind those
maps and the admitted input grid before using this scalar law as a
caller error bound. The next step is one transport-aware local block
with all three output frames and signed ranges. A coarser rounded grid
must not inherit the fine exact-grid conclusion without this check.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
SYLforge supplied the source composition, exact edit and three-field
rational identity. DreamingOfClouds, Clear1nsight, ToikY, Rohan Arun,
CubeJerry, Douglas Colkitt and the other native contributors retain the
credit stated in the unchanged [source provenance](source/PROVENANCE.md).
The Mac and 5080 labels name the same contributor's work environments,
not independent human authors. New work is Apache-2.0.

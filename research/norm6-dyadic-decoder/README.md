# A dyadic norm-six cubic decoder in binary dimension 49

**Algebraic component; no supplier or new kappa.** For the 26208000 antipodal
minimum-vector lines of an extremal48-dimensional even unimodular lattice,
we give norm-one labels in F2^49 and the fitting kernel

    K(x,y) = ((x dot y)^3 - 4(x dot y))/192.

It has diagonal 1 and vanishes on every forbidden distinct binary pairing.
An explicit 19648-term factorization uses only dyadic runtime coefficients.
The integer-valued cubic (u^3-u)/3 removes the apparent odd denominator.
The algebraic separate-copy support bill is at most962752; this is not a
physical copy invoice. [PROOF.md](PROOF.md) proves the identities and label
injectivity. Minimum6 and the complete shell count are published dependencies;
they are not established by the bounded shell sample in this package.

## Reproduce

Python3.12, NumPy1.26.4 and SymPy1.12:

```sh
python3 scripts/research_package.py --package research/norm6-dyadic-decoder
```

Expected: `PASS_NORM6_DYADIC_DECODER` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Normal verification writes nothing, remains active under Python optimization,
and checks a complete symbolic coefficient identity, exact Gram/LDL and chart,
676 sampled pairings and three mathematical corruptions. Source pins are in
[SOURCES.json](SOURCES.json); [RESULT.json](RESULT.json) is regenerated and
compared canonically. No selected construction replay or hosted CI is claimed.

## Relation to prior work

Nebe and Sloane supply the P48p Gram; Nebe arXiv:1312.3780 supplies the external
shell theorem. Incorporated `research/leech-lattice` and `research/niemeier-lattices`
are prior polynomial-lattice approaches and retain credit. The contribution is
the explicit minimum-six dyadic factorization and norm-one binary chart, with
exact checks, rather than a priority claim for polynomial kernels. See
[OVERLAP.md](OVERLAP.md) for the live open-PR review and its limits.

## Open next questions

Construct and fully price I-K, including dirty restoration, frames, both
orientations, ownership, precision and tape. The first useful artifact is an
explicit complete side word. A separate improved bit rail is also required
before this direction could meet the campaign's five-percent kappa target.

## Credit

Prepared by Cinna Davis (@1337isnot1337) with substantial OpenAI Codex assistance.
Nebe/Sloane data and predecessor contributor credit are retained. New code and
proof text use Apache-2.0. No independent human review is claimed.

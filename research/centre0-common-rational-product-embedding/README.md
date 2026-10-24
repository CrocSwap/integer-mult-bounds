# Actual centre0 code: no common Gaussian-rational product chart

For the actual PR5101 centre0 pair G/G^T, no common invertible Q(i)-linear
owner-record chart makes the two encoded inputs compatible with negacyclic
multiplication, even with identity padding to any power-of-two N>=128 and
an arbitrary invertible Q(i)-linear output map. This is a scoped algebraic
obstruction, not a universal changed-producer impossibility or a new kappa.

The [proof](PROOF.md) reconstructs G from the original eight-mode R and selected
repair rows. Its nonzero transpose defect has rank at most14. A product isotopy
over Q(i)[y]/(y^N+1) forces the difference rank to be0, N/2, or N, because that
algebra is a product of exactly two fields of dimension N/2. The contradiction
holds for every allowed N and every common chart; it is not a finite chart search.
This extends PR5101's natural-coordinate unit probe to the full stated chart class.

All original source inputs are live pinned at base20a1e31bc6009b9b3f4d084bbaadc6350e34fcba
in SOURCES.json. verify.py reconstructs all12544 entries, checks original F,
RR^T=56I, RP=I and RU=2I. independent.py separately reads the predecessor G,
checks rank14 modulo101 and exact small Gaussian-algebra boundary controls.
The written cyclotomic and isotopy lemmas supply the all-size proof; finite
certificates do not replace those lemmas. No predecessor emitter or native
full-word replay is run, and no predecessor file is changed.

Reproduce from the repository or official source export with Python3.12:

```sh
python3 scripts/research_package.py --package research/centre0-common-rational-product-embedding
```

The registered normal and optimized commands use only the standard library,
finish in seconds and write no artifacts. The source export carries all declared
inputs. RESULT.json is a typed finite certificate receipt, not a full supplier.

The excluded class uses the same owner-to-polynomial chart on both inputs.
Arbitrary complex charts, independent input charts, address mixing, altered codes,
and alternative bilinear algorithms remain outside scope. Actual native K_i
normalizers are not commuted through the central product and no free Fourier or
basis-change operation is granted. The source-derived producer remains a proposed
edit, with implementation, helper ownership, full invoice, precision and outer
transfer obligations unchanged.

## Open next questions

Specify independent native input charts or an address-mixing circuit and test
its complete source product identity before pricing it. Such a circuit and its
complete cost are absent here. For arbitrary complex common charts, a replacement
invariant is needed: over C this algebra has rank-one multiplication operators,
so the present argument deliberately makes no impossibility claim.

## Attribution

Prepared by JoyboyBrian with substantial OpenAI Codex (Astra) assistance;
Apache-2.0. Retain credit to Cao Yifan/intqwq and PR4610 native sources, Cinna
Davis centre-free/helper-basis work, Dugongue/mdumitrean PR4929/4948,
Chris R/Clear1nsight PR5101 source derivation, Dillon PR4933, and all retained
native, analytic, precision and compiler predecessors. The elementary isotopy
lemma is inherited mathematical structure credited through PR5101 to de Groote
and Bürgisser–Ikenmeyer; the source-specific common-chart rank obstruction is the
new contribution. No independent human or proof-kernel acceptance is claimed.

# Removing the isolated coordinate ports

Prepared for icekylinx with GPT-6 Astra assistance. The Hamming packet factory,
mutable source and target bases, source restoration, entrance gauges, and exact
kernel selection are inherited from the attributed PR507/PR514 construction.

## Exact restriction

In the Hamming ordering of the 120 E8 root lines, sources 0 through 7 are the
coordinate lines. Their only scalar occurrences in the complete PR514 word are
the eight retained-center additions `y_i += x_i`. In particular, none occurs in
`A`, `B`, the target preconditioner, the full-frame cleanup, or the helper dirt
compensation. The other 112 source lines are the eight sign classes on each of
the fourteen weight-four Hamming blocks.

`build_port112.py` checks these statements against both the original Hamming
word and the independently produced canonical word before removing anything.
It refuses a word if a deleted register occurs in any other operation, or if a
deleted center addition has any coefficient or destination other than the
specified identity addition.

Consequently the complete scalar operator, after grouping the coordinate
registers separately, is a direct sum of the eight elementary coordinate
shears and the operator on the 112 code lines and all 560 helpers. Restricting
to the second summand gives exactly

$$
 (x,s,y)\longmapsto(x,s,y+x),\qquad x,y\in K^{112},\ s\in K^{560}.
$$

This holds on arbitrary data and arbitrary helper dirt. Its inverse transpose
is the corresponding reverse shear. The restriction changes no scalar
coefficient, no frame, no helper identity, no helper entrance, no kernel donor
relation, and no source or target basis operation. All retained-register maps
are explicit in `evidence/local/RESTRICTION.json` and
`evidence/local/PORT-MAPPING.json` in the package, and under `local112/`
in a fresh replay output directory.

## Canonical routing indices

The original orthogonal transvection is
$\tau(p)=p+\langle p,43\rangle43$. The eight Hamming coordinate lines map,
in their original order, to canonical indices

$$
 35,0,13,54,40,119,22,51.
$$

The new canonical word retains the other old canonical indices in increasing
order. The 112-port binary geometry still has ambient dimension 9. The
transvection, common-frame incidences, Clifford frames, and all residual
wrappers are unchanged on the retained registers. A global template must
restrict every data-family layer to this same subset; reusing a 120-port
owner schedule without a new hosting certificate is not authorized by this
local argument.

## Exact local cost

Each removed source has one unused line-to-full transition of rank 8. Each
removed target has one zero-to-hyperplane transition of rank 8. Each removed
retained center descends from its line with rank 1. Thus the local saving is
exactly sixteen rank-8 children and eight rank-1 children. The retained center
rank sum changes from 72 to 64.

| Recursive rank | PR514 local count | 112-port local count |
|---:|---:|---:|
| 1 | 2539 | 2531 |
| 2 | 160 | 160 |
| 3 | 530 | 530 |
| 4 | 88 | 88 |
| 5 | 298 | 298 |
| 6 | 68 | 68 |
| 7 | 1 | 1 |
| 8 | 17 | 1 |

The new rank mass is 6706. It equals the unchanged helper residual mass 4850,
plus $224\cdot8=1792$ data transitions, plus the 64 retained-center ranks.
The helper widths remain 18 of width 7, 154 of width 8, and 388 of width 9.

For the existing nine-stage controller, the formal deficit per replica is

$$
 (9-1)v-9\,\mathrm{cst}.
$$

It changes from 312 to 320. With eight replicas the value changes from 2496
to 2560. The data stock changes from 7680 to 7168. These identities alone do
not price the new whole-residual-hosted supplier: its physical assignments,
unused remainders, finite invoice, and rational moment must be rebuilt.

## Independent checks

The retained PR514 emitter is used with only its output-directory argument
adapted. It emits 25,242 instructions in each orientation. A separate reader
retains the complete local replay and its controls from the PR514 independent
audit. It checks all 784 scalar columns in both orientations, exact common
frames, the literal paid child profile, the location and order of every
residual wrapper, and cleared private centers and coefficient work. Thirteen
negative controls are rejected.

The residual-wrapper checker is run without code changes on the new
canonical word. It verifies all twelve entrance-frame recipes, including
their global phases, and rejects five corrupted wrappers. The exact Clifford
phase checker is retained with only its input and module-directory arguments
adapted. `ADAPTATIONS.json` records the precise source hashes and edits.

The global argument retains the same all-size/compiler, target-label,
mutable-basis, physical-hosting, finite-precision, and analytic interfaces as
the source construction. This restriction introduces no new algebraic
interface. A certified global kappa is a separate output of the new global
owner schedule and moment/outer assembly.

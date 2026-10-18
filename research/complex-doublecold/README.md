# Two cold kernels in every complete complex invocation

Conditional **κ = 0.001593667716067094**, improving PR564's
0.001593134158181640 by **0.03349108314035%**.

| Model | Certified complex rate b | Final κ |
| --- | --- | --- |
| Native exact complex | 0.001596211546877366844000 | 0.001593667716067094 |
| Conservative complex surcharge retained | 0.001596211544128909961969 | 0.001593667713327391 |

The unchanged cited PR543 bit cap is c = 0.001653826988146798944268,
so complex still binds. Both models improve the requested PR564 bound.

PR564 introduced a first cold kernel in all 72 calls. This package adds a
second exact suffix relation on helper 294 (register 518), after reconstructing
the first kernel on helper 270. The second helper's residual width falls from
nine to eight. The relation is recomputed on the already modified word, and
the complete inverse cleanup is rebuilt. The exact zero/four/eight promotion
providers are retained, with 15, two and 55 complete invocations respectively.
There is no interpolation between providers or additional controller copy.

A new literal allocation changes 798 of 36,288 owner records. Reusing every
old owner slot would lose after charging its enlarged remainder; the new
allocation places the freed capacity where the complete invoice benefits.
The resulting paid profile is

```
{1:166640,2:31072,3:35604,4:13696,5:4032,6:4032,
 7:136,8:576,12:1,48:1675}
```

It is reconstructed from both actual reflected scalar event lists and the
physical controller. All 36,288 helper roles have whole owners with no extra
helper banks. Live stock is 7168, physical stock 7682, rank mass 520704 and
deficit 2560. All 4,168 positive idle remainders are charged, including the
new rank-12 remainder.

Run with standard-library Python 3 and a fresh output directory outside this
source package:

```sh
python3 -B verify.py --work /tmp/doublecold-replay
```

Keep assertions enabled. The verifier fully reconstructs frozen PR558,
reconstructs the four-pivot source and both cold kernels for all three
providers, then checks every actual suffix relation. It checks all 728 scalar
columns in both orientations, restoration of all 504 arbitrary dirty helpers,
native frame chains, both reflected ledgers, 2,929 exact phase edges and 224
endpoint adapters per provider, and normalized wrappers. Negative controls
omit each kernel term separately and jointly, alongside the inherited
44-kernel and four/eight promotion controls.

It binds the three fresh providers, checks the complete physical assignment
with 17 controller mutants, emits a fresh finite invoice, and checks both
exact recurrence models with 57 malformed-receipt controls. Separate phase
timing controls accept timing-only edits and reject semantic phase failures
after consistent digest rebinding. Container controls accept three actual
recompressions, reject 27 consistently rebound semantic mutations, and reject
27 stale-reference or invalid-timing cases before normalization. Two rational
moment engines reject each
adjacent 10^-24 supplier endpoint; both models pass seven bootstrap levels
and all 47 strict outer constraints, including rejection of the next 10^-18
κ grid point for the selected assembly parameters.

Scalar and coefficient work, wrappers, adapters, group/router work, prefix,
row, precision, tape, residual and idle children are all charged by the fresh
invoice. The inherited all-size bounds are retained. The complete construction
and its transfer argument are in [proof/CONSTRUCTION.md](proof/CONSTRUCTION.md).
The owner receipt contains every literal before/after edit; its optional
rebuild checker reproduces the assignment from the pinned PR564 owners.

Regenerated compressed programs are pinned by their decompressed content,
because Python and zlib versions can produce different gzip streams. Every
run still checks its actual byte-hash links between programs and receipts.
Portable receipt identities normalize only those validated compression
references and the phase review's elapsed-time field; mathematical fields
remain bound. Immutable sources and their manifest retain exact byte hashes.

The native complex moment credits Rohan Arun's PR559: fixed provider dispatch
is uniform across the full exact Clifford/orthogonal cover and introduces no
exceptional complex residue subset. Only the generic complex bad-residue
surcharge is omitted. The PR543 bit fallback remains, and the conservative
complex witness is verified first. Files prefixed `PR564-` are unchanged
historical sources, not receipts for this new construction.

This remains conditional on inherited all-size compiler, common-label and
mutable-source realization, whole-call hosting, precision/tape, analytic
transfer and PR543 H1-H5 assumptions. The unchanged bit supplier is repriced
from its pinned profile, not physically rebuilt by this package. Finite exact
replay is not an unconditional theorem, full Lean proof or practical speed
claim. Source pins, contributor notices, licenses and AI disclosures are
preserved; see [NOTICE.md](NOTICE.md).

# Puncturing eight isolated ports: a larger global kappa

Contributed by **icekylinx**, with GPT-6 Astra assistance; reviewed and packaged with OpenAI Codex. This is an incremental
research package over pinned PR514, with its complete offline dependencies.

## Result

The new checked **conditional global** exponent saving is

$$
\boxed{\kappa=\frac{182243220215421}{125000000000000000}
             =0.001457945761723368.}
$$

Under the inherited integer-multiplication framework this is the parameter in
$T(n)=O(n(\log n)^{1-\kappa})$. It is a finite conditional witness, with the
scope described below. Percentages compare exponent savings, not measured
runtime.

| Quantity | Pinned PR514 | This construction |
| --- | ---: | ---: |
| Global kappa | 0.001391523459591829 | **0.001457945761723368** |
| Complex rate b | 0.001393462495344162153490 | **0.001460074471110324279467** |
| Bit rate c, cited PR493 | 0.001565442026981656908596 | same |
| Local ports v | 120 | **112** |
| Ambient local dimension h | 9 | 9 |
| Helpers R | 560 | 560 |
| Sum of retained-center ranks | 72 | **64** |
| Local child rank mass | 6842 | **6706** |
| Global ambient dimension m | 73 | 73 |
| Data/live families W | 7680 | **7168** |
| Physical families | 8258 | **7738** |
| Global rank deficit | 2496 | **2560** |

This is **4.7733512269% above PR514**, an absolute kappa increase of
`66422302131539/1000000000000000000`.

During the final public comparison, PR518 appeared with kappa
`0.001393662920776407`. The present result is **4.6125099541% above that
newer comparable claimed witness**. PR518 is a comparison, not a code or proof
dependency; its extra seven pivots were not adopted. The public snapshot was
checked through PR520 at 2026-10-12 00:09 UTC. PR520 supplies an open allocator
and a delivery map, with no higher global kappa reported. See `SOURCES.json`
and `evidence/PUBLIC-SNAPSHOT.json` for the comparison and immutable pins.

The new contribution is the **exact removal of eight isolated data-port
summands, followed by a complete new physical owner allocation and global
recount**. The scalar factory, 92-pivot kernel, entrance gauges, and existing
body retiming are retained from the attributed predecessor. No headline gains
are added together.

## Reproduce from an empty output directory

Python **3.11 or later**, standard library only, with assertions enabled:

```bash
python -B verify.py --work /absolute/path/to/a-new-output-directory
```

The directory must not already exist and must be outside this package.
There are no network, optimizer, NumPy, SciPy, C++ or Lean dependencies for
verification. The literal owner assignment is an input which every checker
validates; verification does not rerun the optimization used to discover it.
The two exact Clifford passes are the longest steps, so allow several minutes.

The runner first executes the full thirteen-stage pinned PR514 reconstruction.
It then builds the 112-port restriction, reconstructs local instructions,
checks both orientations and phases, rebuilds the restricted data controller,
emits actual whole owners, independently recounts all costs, and runs two
rational moment engines and all 47 strict outer inequalities. Fourteen
top-level stages, including the nested predecessor replay, must pass.

The final output is `RESULT.json`; all exact numerical inequalities and
bootstrap parameters appear in `audit/EXACT-ASSEMBLY.json`. Per-stage logs and
`STEPS.json` identify any failure. Every input is hashed by `MANIFEST.json`.
Only LF/CRLF normalization is permitted for manifest text entries. Generated
timing receipts can vary in their `seconds` fields; the canonical recipes,
global template, paid histogram and exact rates are deterministic. Generated
gzip provenance inside the template binds decompressed content; its container
header and compression level are not mathematical inputs. The nominated-plan
binding normalizes LF/CRLF before hashing. `PORTABILITY.md` records the scope.

The original Pro clean replay passed all stages in about 651 seconds. `REPRODUCTION.json`, `evidence/COLD-REPLAY.json` and
`evidence/COLD-STEPS.json` record that run. Every published numerical and
physical certificate under `evidence/` is from that completed reconstruction.
`LOCAL-VALIDATION.json` records the separate submission validation.

## Structural argument

### 1. A direct-sum component can be removed exactly

The old 120-port Hamming construction consists of eight coordinate lines and
112 code lines. In the literal PR514 word the coordinate source/target pairs
occur only in eight additions `y_i += x_i`. They never occur in the factory
body, target preconditioner, dirty-helper compensation, or full-frame cleanup.

`code/build_port112.py` checks every occurrence before deleting any register.
It rejects any removed-register operation other than the exact specified unit
shear. The full word is therefore the direct sum of these eight elementary
shears and the word on the remaining 112 ports and all 560 dirty helpers.
The retained normalized scalar operator is exactly

$$
 (x,s,y)\longmapsto(x,s,y+x),\qquad x,y\in K^{112},\ s\in K^{560}.
$$

All helper identities, coefficients, frames, donor relations, and entrance
gauges stay the same. The original orthogonal transvection maps the removed
ports to canonical indices `0,13,22,35,40,51,54,119`; all global data layers
use precisely the complementary set, in its original order.

Each removed pair eliminates two rank-8 children and one rank-1 center
descent. The actual local cost is thus the old profile minus sixteen rank-8
and eight rank-1 children:

```text
{1:2531, 2:160, 3:530, 4:88, 5:298, 6:68, 7:1, 8:1}
```

Its rank mass is 6706. The 560 helper residuals still have widths
`{7:18, 8:154, 9:388}`. At nine stages and eight replicas,

$$
W=8\cdot8\cdot112=7168,\qquad
D=8\bigl(8\cdot112-9\cdot64\bigr)=2560.
$$

These identities motivate the construction; they do not by themselves certify
a globally usable supplier. The following placement and recount are essential.

### 2. Every helper receives a complete legal physical owner

The controller uses 72 complete invocations, ordered by
`(7*stage + 6*replica, stage, replica)`. Every replica keeps its original event
order. The new `inputs/OWNERS112.json.gz` supplies all **40,320** helper uses.

The changed global template gives every helper one whole physical family.
Within each invocation the 560 helper owners are distinct and avoid its
224 active data families, so all **784 owners are different**. Helpers are
never split among several registers.

Owner windows are reconstructed from the actual controller, including bridge
touches. Residual factors fit in actual pending axes; spectator coordinates
are explicit and restored by the same normalized wrappers used in PR514.
There are **3214 distinct actual orthogonal 73-column charts** and **349200
covered pending axes**. Every uncovered pending factor remains a paid child.
The literal remainder histogram is

```text
{3:3354, 5:3270, 7:60, 48:230}
```

Adding it to 72 copies of the local profile yields the complete global invoice:

| Recursive rank r | Paid count H[r] |
| ---: | ---: |
| 1 | 182232 |
| 2 | 11520 |
| 3 | 41514 |
| 4 | 6336 |
| 5 | 24726 |
| 6 | 4896 |
| 7 | 132 |
| 8 | 72 |
| 48 | 230 |

Its mass is **520704**, and

$$
73\cdot7168-520704=2560,\qquad 73^2=5329>2\cdot48^2=4608.
$$

The physical stock is `7168 + 8 + 560 + 2 = 7738`, including private center,
reserved-tableau and coefficient work. The final construction has zero
unhosted helper banks.

### 3. The global number comes from the fully paid supplier

Both independent rational moment implementations accept

```text
b = 1460074471110324279467 / 1000000000000000000000000
```

and reject `b + 10^-24`, including the retained exceptional-class fallback
term. The unchanged cited PR493 bit profile is repriced by both engines at
its published endpoint. The complex supplier remains the binding component.

Six exact bootstrap stages and all **47 strict outer inequalities** then
admit the stated global kappa. The adjacent `10^-18` kappa grid point and
the invalid parameter controls `zero_eta`, `zero_beta`, `unit_beta` are
rejected. This is an adjacent-grid check for this selected assembly, not an
optimality claim over all constructions or parameters.

The finite scalar and routing invoice is rebuilt for the new physical program:

| Check | Required | Retained allowance |
| --- | ---: | ---: |
| Global coefficient prefix, bits | 206 | 512 |
| Physical row coefficient | 16467 | 20161 |
| Router bound, bits | 7984 | exponent 30000 |
| Literal overhead, bits | 35282 | exponent 100000 |
| C0 bound, bits | 200012 | exponent 210000 |

All nine finite invoice checks pass. Constants and exact rational margins are
preserved in the evidence rather than being inferred from a local percentage.

## Independent validation and evidence

The new source has two complementary global audits. The adapted physical
checker verifies the emitted complete template. A separately written raw
checker imports neither an emitter nor a hosting checker and does not read
the nominated profile or nominated windows. It independently infers the port
restriction, replays the two local programs over `Fraction`, rebuilds real
charts and actual idle windows, validates all literal owners, and derives the
same full histogram. `verify.py` requires their results to agree.

The local replay checks every one of 784 arbitrary data/helper columns in both
orientations, each containing 25,242 events. Thirteen local mutation controls
are rejected. The exact local Clifford pass checks 968 frames, 2943 directed
edges (a conservative superset of those used), and 224 port endpoint adapters, with global
phases included. The edge recipe histogram is not used as the paid invoice.
All twelve entrance-frame wrapper recipes are decoded independently, and five
corrupted wrappers are rejected. The new global restriction audit rejects 13
controls; the final owner/controller audit rejects 19 controls.

The global data recipes are selected unchanged from the pinned predecessor:
their actual vectors, stage and idle translations, and terminal corrections
are compared exactly. The inherited data-phase derivation is not claimed as a
new analytic or Lean proof. See `proof/GLOBAL-RESTRICTION.md` for this boundary.

Useful files:

- `EXPECTED.json`: concise exact expected result and structural counts.
- `evidence/EXACT-ASSEMBLY.json`: both moments, bootstrap and 47 strict margins.
- `evidence/INDEPENDENT112-RAW-AUDIT.json`: independently reconstructed operator,
  charts, chronology, owners and paid profile.
- `evidence/ASYNC-AUDIT.json`, `evidence/PREFIX-AND-INVOICE.json`: complete
  physical template audit and finite invoice.
- `evidence/hosted/GLOBAL-TEMPLATE.json.gz`: actual complete hosted template.
- `evidence/local/`: local words, emitted programs, phase and wrapper evidence.
- `PROOF.md`, `proof/`: conditional argument and detailed restriction reviews.

## Scope and direct credits

This is a **new checked finite conditional construction**. It retains the
all-size compiler, common-label/mutable-basis realization, normalized Lemma A,
restored-row, precision/tape and analytic-transfer interfaces. The restriction
does not strengthen or prove these interfaces. No unconditional multiplication
theorem, fresh Lean certification, universal optimum, or practical speedup is
claimed. The unchanged PR493 bit operator is a cited dependency; this package
reprices its histogram rather than reconstructing that operator.

[PR514](https://github.com/CrocSwap/integer-mult-bounds/pull/514) supplies the
pinned combined word, 92-pivot kernel and asynchronous construction.
[PR507](https://github.com/CrocSwap/integer-mult-bounds/pull/507) supplies the
partial-own factory and retiming reference;
[PR484](https://github.com/CrocSwap/integer-mult-bounds/pull/484) and
[PR496](https://github.com/CrocSwap/integer-mult-bounds/pull/496) supply the
gauge/kernel, wrapper, whole-owner and invoice ancestry.
[PR493](https://github.com/CrocSwap/integer-mult-bounds/pull/493) supplies the
unchanged bit operator. The original notices preserve the other substantial
geometry, compiler, retiming, wrapper and arithmetic contributions.
`NOTICE.md`, `SOURCES.json` and the untouched `vendor/pr514/` notices distinguish
new work, inherited ingredients, comparisons and excluded interfaces.

The restricted intermediate parent is used as a data/controller scaffold.
Its legacy bank-padding display is not a proof of an executable bank program;
the final template has no bank families, and its complete costs are audited
from its actual whole owners and remainders. This is explained in the global
restriction proof. The final witness uses no disputed split-residual interface.

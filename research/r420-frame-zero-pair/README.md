# R420: share one dirty-helper pair at frame zero

This finite bit-circuit contribution saves **108 binary XOR operations** in
eumemic's PR543 R420 word. Its frame-zero dirt compensation goes from 19,922
to 19,814 scalar ADDs; the complete native word goes from **26,916 to 26,808**.
Both dirty helpers are restored before phase A. The nine-stage formal-column
replay, frame paths, copied information and measured native prefix bill pass.
**No new kappa or completed hosted supplier is claimed.**

The base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. At that base the
selected composition is PR626 with PR543, conditional
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`, and its complex
supplier binds. These facts come from the selected certificate, its actual
`research/community-k492-audit/pr626/replay/ASSEMBLY.json`, and the
[maintainer review](../../docs/research/community-k492-review.md).
The R420 README's older frontier discussion is historical.

## Reproduce

From the repository root, with Python 3.11+, a C++17 compiler and Boost headers:

```sh
python3 -B research/r420-frame-zero-pair/verify.py
```

Expected last line:

```text
PASS_R420_FRAME_ZERO_PAIR D=19922->19814 native_adds=26916->26808 columns=660 kappa=unchanged
```

Python uses only the standard library. `CXX` selects a compiler; `BOOST_INCLUDE`
can name a nonstandard Boost include directory. The command checks all source
pins, regenerates the circuit and records, compiles the unchanged predecessor
checkers, runs the controls and compares every certificate field. It uses a
temporary directory. To retain the generated word, raw records, C++ receipts,
compile logs and certificate, append `--output /absolute/new/directory`.
An existing output directory is rejected.

Only this research directory is added. The selected frontier, predecessor
packages and `upstream/` are unchanged. The recipe is implemented in `factor`
in [verify.py](verify.py); its exact output has canonical JSON SHA-256
`358eca016e0e1ef48267dcd7ff33d4d36c27ecc3f38fffbdceb4c924e2254349`.
[SOURCES.json](SOURCES.json) pins every imported or executed predecessor file.
[certificate.json](certificate.json) records the complete census, target list,
both orientations, accounting and controls.

## The circuit and complete local cost

Write `a = helper 552`, `b = helper 521`. Let T be the 110 targets whose original
D row contains both a and b. Target register IDs are 120 through 239, except
153, 161, 174, 182, 185, 193, 206, 214, 222 and 230. All operations below occur
at frame zero:

1. Execute each original D row, omitting a and b only for rows in T.
2. Execute `a ^= b`.
3. Execute `y_t ^= a` once for each target in T.
4. Execute `a ^= b` to restore the original dirty value of a.

No source register is accessed. For arbitrary initial values alpha and beta,
the middle register contains `alpha XOR beta`, each selected target receives
exactly its omitted two terms, and a ends as alpha. Register b is read only.
All other helper and target terms are unchanged. Thus the D map is exactly
the original map on **all input columns**, including arbitrary helper dirt and
arbitrary target inputs. Reordering the residual target-only gates is valid:
they commute, read unchanged helpers, and cannot change a or b.

For a pair shared by q target rows, `2q` target XORs are replaced by `q+2`
XORs, including preparation and restoration. Here q=110, so the saving is 108.
The JSON D list grows from 120 grouped gates to 232 grouped gates; every source
term is still counted as a separate binary ADD. The result is not obtained by
pricing a many-source gate as a single operation.

| Complete native quantity | Original | Candidate |
| --- | ---: | ---: |
| D scalar ADDs | 19,922 | 19,814 |
| All scalar ADDs | 26,916 | 26,808 |
| All emitted records | 29,874 | 29,766 |
| Helpers | 420 | 420 |
| Retained copies | 9 | 9 |
| Paid rank mass | 5,112 | 5,112 |
| Forward positive prefix | 144,651 | 144,651 |
| Reverse positive prefix | 2,270,064 | 2,270,064 |
| Five-stage payload bits | 100 | 100 |

The entire MOVE/COPY/ERASE subsequence is identical, as are A, scatter, B, C,
boundary frames, labels and retained registers. There are no additional
frame changes, copies, helper allocations or local recursive children.
The paid histogram remains `{1:1320, 2:1440, 4:60, 5:120, 8:9}`. In the
nine-stage scalar replay the local saving is repeated nine times: 972 fewer
ADDs; the 2,160 bridge ADDs and 81 fresh center copies are unchanged.

F2 equality alone does **not** imply equality of positive prefix bounds. The
restoration gate increases the unsigned helper bound even though it cancels
over F2. We explicitly replay both signed orientations with nonnegative
integer bounds, independently in Python and in the pinned C++ checker. The
unchanged payload is exactly
`64 * 144651^3 * 2270064^2 = 998206739997057013039187410944 < 2^104`.
Neither entrywise domination of every intermediate positive map nor an
integer-ring endpoint identity for the all-positive XOR stream is asserted.

## The changed interface obligation

PR543's literal H2 requires every D gate to write a target and read helpers.
This candidate deliberately fails that syntactic condition, since two D gates
write helper a. The original checker's `K_equals_D` calculation also assumes
literal helper reads, so it is inapplicable to the compressed circuit.
Neither check is silently weakened in the predecessor package.

Replace H2 by the following sufficient condition, keeping H1 and H3--H5:

> D uses only target/helper registers at frame zero, reads only helpers, and
> has aggregate map `(x,s,y) -> (x,s,y+Ns)`; in particular every helper is
> restored before A starts.

The original block-triangular proof then applies verbatim at the boundary:
the raw A/scatter/B map is `(z,y) -> (Uz,y+Jx+Ks)` with z=(x,s), and C applies
`U^-1` to z. Composing after D gives
`(x,s,y) -> (x,s,y+Jx+(K+N)s)`. Here the unchanged raw word has J=I and the
new D has exactly the old N=K, so the final map is `(x,s,y+x)` over F2.
The two new helper gates are legal at frame zero, where helpers initially
stand. They restore before any climb, so no extra gate belongs in C and no
descent is hidden. This is a written finite-interface argument, not Lean.

The verifier first evaluates the new D with a separate set-valued symbolic
interpreter and requires its complete map to equal the pinned original D.
It then runs PR543's exact labels, closed frames and 660-column native replay
on the actual candidate. For the inherited interface it checks that exactly
the documented H2 and syntactic K checks fail. Replacing only D by its proven
equivalent original normal form restores all H1--H5 and conclusion checks.
The unmodified C++ record checkers additionally accept actual candidate
geometry and all 1,380 columns across nine stages, including arbitrary dirt.

## Search scope, controls and remaining work

OS randomness supplied assignment seed **1**, selecting the bit-supplier
track. Its parity selects the orientation `552 ^= 521`; the opposite
orientation was also checked and has the same costs and prefix maxima.
The search stops after all `binomial(420,2) = 87,990` unordered helper pairs.
Two methods agree for every pair: count pair occurrences in rows, and
intersect column-incidence bitsets. Their complete histogram has a unique
maximum q=110 at `{521,552}`. Consequently 108 is the largest saving within
this **single-pair recipe with two helper updates on this fixed D matrix**.
This does not establish optimality among general XOR circuits, multiple-pair
factorizations, changed frames, changed words or supplier assemblies.

Six D controls reject an omitted restoration, an omitted shared read, a wrong
restoration source, an F2-correct read at a nonzero frame, an F2-neutral pair
of target-to-helper reads, and an F2-neutral pair of source reads at frame
zero. A harmless adjacent pair of helper updates is a positive control. An
additional F2-neutral record preamble preserves every endpoint column but
exceeds the positive-prefix limit, and the actual C++ bill check rejects it.
Both baseline and candidate also reject all 18 omitted-bridge controls.

This package completes the finite native circuit and nine-stage cohort
checks. Integration would still need review of the generalized D interface
in the all-size/common-label realization and a fresh hosted-parent replay,
invoice and outer assembly. Equal local frame paths and prefix maxima alone
do not certify those obligations. The selected assembly is already complex
limited; this scalar-work saving does not alter its paid local moment or
establish a better kappa. Whole-call pooled-cell hosting, normalized residuals,
mutable-basis realization, precision, fixed-tape and analytic assumptions are
inherited. No practical runtime speedup or full multiplication theorem is
asserted.

## Relation to concurrent work and attribution

The local [claim](CLAIM.json) records three candidates and the overlap check.
No pinned sprint issue existed. PR670 (yongjae321) resynthesizes phase-B block
3; PR674 (x0hu) resynthesizes block 5. This contribution changes D and uses
temporary helper sharing followed by restoration, adding distinct coverage.
Their changes are not imported and composition with them is not tested.
PR661's exact frame bound fixes D and the scalar gate order and explicitly
excludes resynthesis. This task changes that excluded circuit structure.
PR612's original R420 Lean boundaries do not prove this changed D interface.
PR589's punctured-word transport search is separate.
The final refresh through PR685 also checked PR673's multiway cyclic-inverse
dirty echo and PR677's native ADDRESS/DATA interface: both change different
primitives. Neither is a dependency, and no novelty of the general reversible
prepare/share/restore trick is claimed. The new evidence here is its concrete,
fully costed R420 compensation instance and changed D interface.

Credit remains with **eumemic** for PR543's R420 construction, interleaved
interface, independent checker and PR493 carrier skeleton; **Dylan Crow** for
the bit word format and exporter; **DaysSky** for the bridged-stage checker
and hosting lineage; **Chafik Boukhalfa** for the inherited geometric checker
and invoice lineage; **Zhihao Chen** for the mutable-basis/interface lineage;
**DreamingOfClouds** for the retained-total and nine-stage bit work; and the
cumulative authors named in those packages and the repository contributor
record. Their original notices and bytes are unchanged.

Prepared by **Mikhail R. Gadelha (@mikhailramalho)** with substantial **OpenAI
Codex assistance**, including investigation, implementation, proof drafting
and verification. No independent human review is claimed. New files follow
the repository's **Apache-2.0** license.

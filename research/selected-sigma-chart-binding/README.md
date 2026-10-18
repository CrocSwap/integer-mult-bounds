# Selected1094 binary chart certificates: complete dictionary and reference binding

This is an independent **finite certificate/application audit**, not a new Lean
proof, physical supplier, cost saving or multiplication exponent.

The selected1094 replay has **10,002 distinct 73-dimensional helper charts** in
`ACTUAL-SIGMAS.json.gz`. Every chart has a recovered five-array certificate in
the exact grammar of James Chang's [PR1879](https://github.com/CrocSwap/integer-mult-bounds/pull/1879),
consumed by the dictionary adapter of [PR1927](https://github.com/CrocSwap/integer-mult-bounds/pull/1927).
Those packages prove generic implications but explicitly do not supply a
selected-instance census or the auxiliary certificates. This package supplies
those witnesses and independently checks their mathematical premises, original
content keys and **all 69,120 helper references across 144 calls**.

No predecessor executable is imported. In particular, a Python check of the
premises is **not** reported as execution of Lean's `certifyEntry` or fresh
kernel acceptance. The original generic theorems retain their own trust base.

## Exact result and artifacts

- [WITNESSES.json.gz](WITNESSES.json.gz) contains one complete five-array witness
  per original dictionary key. Its decompressed payload, rather than gzip
  container bytes, is the replay identity.
- [RESULT.json](RESULT.json) records all source/member digests, counts, the
  reference multiplicities and explicit failure controls. Normal replay reads
  this receipt and never overwrites it.
- [recover.py](recover.py) reconstructs certificates from the raw matrices only.
  It does not read the original port bases, route recipes or formal checker.
- [verify.py](verify.py) does not import the recovery algorithm. It checks the
  certificates and independently computes inverses by augmented-row
  Gauss-Jordan elimination over F2.
- [SELECTION.json](SELECTION.json) preserves the complete original chooser
  output: seed `e059d89919a0078380ea43f90a32a2f6`, track
  `independent-verification`, selected card `formal-interface-lemma`.

All 10,002 certificates have `a = u`; 6,612 updates have Hamming weight four
and 3,390 have weight eight. Thus these are even-weight orthogonal
transvections followed by the explicitly witnessed coordinate permutation.
The checker also compares each elimination inverse with the matrix transpose;
this extra selected-instance fact is not assumed from the word “orthogonal.”

Coverage is **53,300,658 binary coefficient entries**, represented exactly by
730,146 packed columns, and **1,460,292 basis-vector compositions** across the
two inverse directions. Each check is over exact Python integers, with no
random test vectors, floating-point tolerance, or sampled address set.

The raw source is the selected archive
`research/community-frontier1094-audit/selected-replay.tar.gz`, SHA256
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
This is **not** the similarly named historical R492 evidence under
`gauge44-slots-t16/evidence/global/`, which contains only 7,870 charts.
The selected archive's dictionary has payload SHA256
`2cad2187e792fe7c879084a23f15577730ce27e82ff0c341885935c8adffc58f`.

## Precise mathematical contract and direction

For dimension n, write the source matrix as columns `A_j` in F2^n, least
significant bit first. The five arrays, in order, are:

1. forward permutation `p`;
2. inverse permutation `p_inverse`;
3. original packed columns `A_j`;
4. update bits `u_i`;
5. coefficient bits `a_i`.

Each array has length n. Indices are below n, columns below `2^n`, and bits
are 0 or 1. The checks require both permutation round trips, original column
identity, `a·u = 0`, and, for **every** j,

```
A_j = e_(p(j)) + a_(p(j)) u.
```

The coefficient index is `p(j)`, not j. With `P e_j = e_(p(j))` and
`T x = x + u(a·x)`, this is `A = T P`. Since `a·u=0`, characteristic two gives
`T(Tx)=x`; hence **`A^-1 = P^-1 T`**, not `T P^-1`. The independent checker
reconstructs the inverse by row elimination and verifies both compositions on
all n basis vectors. Linearity then proves both identities on every one of
the `2^73` addresses for these fixed matrices; no exhaustive-address execution
is claimed.

For any payload function f, the stated logical pullback convention is
`f -> (x -> f(Ax))`; its inverse is `f -> (x -> f(A^-1 x))`. This derives
logical cancellation. It does not select the direction of an external physical
executor or establish in-place memory safety. The receipt contains an actual
selected chart and axis where the wrong inverse order gives a different vector.

These are precisely the finite scalar obligations behind
`CheckedBinaryChart.Checks`, `ParsedBinaryChartCertificate.certify_sound`, and
`JsonPackedColumnDictionary.certifyEntry_sound` at the immutable heads in
[SOURCES.json](SOURCES.json). The witness's complete five-array value can be
passed as `certificateJson` to that adapter with `n=73` and JSON depth fuel 3.
A full call to the pinned Lean interpreter remains a separate kernel replay,
not an implicit consequence of this Python implementation.

## Independent recovery and source/reference closure

For a non-permutation matrix, choose any nonunit column v. In a factorization
`A = (I+u a^T)P`, that column must be `e_i+u`, so one of the n values `v+e_i`
is the update. For each candidate, the producer constructs the bipartite
column-to-coordinate possibilities and finds a matching. The matching gives
p and a; the producer retains only `a·u=0`. The verifier accepts a witness by
the equations above, not by trusting the search or its completeness. Every
selected chart is accepted, so no negative classification theorem is needed.

The source dictionary is populated only by helper roles. The independent
reference pass reads the selected template, phase axes and provider ports:

1. For an odd non-full port q, let z be its first zero coordinate among 0..8
   and put `u=q+e_z`. Apply `x -> x+u(u·x)` to the coordinate basis with
   coordinates 0 and z exchanged. This reconstructs the source idle basis.
2. Decode each original helper route (`[3, child, offset]` at width nine or
   `[4, child, offset, width, spectators]` otherwise), preserving all ordered
   spectator coordinates. Pending child axes identify the first `width`
   columns; spectators complete the first nine; the remaining basis coordinates
   follow in order.
3. Recompute the SHA256 of the compact ordered decimal column list. Compare
   the full list with the dictionary entry, not merely its hash.
4. Require all 144×480 role triples exactly once, every dictionary key referenced,
   no missing entries, and the exact ordered occurrence stream hash from
   `HOSTED.json`. Its digest is
   `e9d95a4a108476a0971d19c8815e1cb747e3b28214b44c92500fdd9647f9bf6d`.

This covers the dictionary's complete helper domain. It **does not** turn the
32,256 data-owner rows, private centre allocations or idle remainder operations
into claims about this helper-only dictionary. The emitter's route convention
is pinned and credited; its native replay and placement/chronology admission
are not rerun or replaced.

## Controls and reproduction

Use CPython 3.12, standard library only, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/selected-sigma-chart-binding/verify.py
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/selected-sigma-chart-binding
```

The registered replay runs the direct verifier and eight focused test groups.
The verifier has two positive controls and nineteen semantic rejection
controls: malformed numeric/shape/index fields; a nonzero `a·u`; singular
elimination; wrong permutation direction and inverse table; coefficient and
source-column changes; content-key drift; duplicate JSON keys; missing and
orphan live entries; and a changed spectator axis. The wrong-inverse-order
example is an additional explicit separation witness.

The focused tests independently enumerate every 3×3 binary matrix and all
permutation/transvection factors, compare the producer to that separate oracle,
and test exact inverses on every 3-bit input. They also check the coefficient
index convention, numeric/duplicate policies, compression invariance, source
pin drift, and all odd non-full nine-bit port bases. These are controls for the
implementation; the selected result still checks all 10,002 actual matrices.

To independently regenerate the complete auxiliary witness file, without
replacing committed evidence:

```sh
uv run --python 3.12 --no-project python -B research/selected-sigma-chart-binding/recover.py --output /tmp/selected-sigma-witnesses-new.json.gz
```

The producer refuses an existing destination. Compare decompressed canonical
JSON, not gzip headers. A receipt may likewise be written only to an absent
path with `verify.py --write-receipt NEW_PATH`.

Observed final local verification on **CPython3.12.12, Clang21.1.4,
macOS27.0.1 arm64**:

```text
PASS_SELECTED_SIGMA_CHART_BINDING charts=10002 dimension=73 helper_roles=69120 controls=19 no_new_lean_build no_new_kappa
Ran 8 tests in 0.247s
OK
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-sigma-chart-binding outcome=completed
```

The direct optimized receipt-producing replay took14.46seconds; the registered
verifier-plus-tests took14.85seconds in this environment. These are observations,
not timing acceptance gates. The first metadata launch stopped before running
commands because `outcome` was descriptive text rather than the required enum;
after changing it to `completed`, the complete registered replay above passed.

## Scope, provenance and credit

Base main: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The selected exponent
`836330098538459/500000000000000000` and every paid profile remain unchanged.
This is a refined, not rerolled, chooser assignment; [TASK.json](TASK.json)
records the working example, changed scope, budget, falsification and next steps.
The public claim is in
[round-two Discussion1929](https://github.com/CrocSwap/integer-mult-bounds/discussions/1929#discussioncomment-18925867).

Credit **James Chang** for the generic PR1879/1927 Lean certificate and actual
JSON adapter; **Rohan Arun** for selected PR1094; **Jeremy Kothe** for the T16
emitter and helper chart construction; **Hao Yan** and the PR484/507/514
lineage for the retained geometry; and the Lean/Mathlib contributors. PR1831's
source-reviewed route-to-owner census is adjacent work, not a result claimed
again here. The existing emitter/auditor already reconstructs actual sigmas;
our new contribution is separately recovered **formal-interface-format
certificates**, their complete selected binding, independent elimination, and
portable semantic controls. No priority is claimed for the charts, source
construction, orthogonal port formula, or generic rank-one identity.

Prepared for Adam Gall with substantial **OpenAI Codex GPT-6 Astra** assistance
in research, code and documentation. Apache-2.0. No independent human review
or unseen CI result is claimed.

### Limitations

- No Lean executable was found by `command -v lean`, and no cached toolchain
  was found in the searched `/tmp/*lean*/`, `~/.elan/toolchains/` or
  `~/.cache/*lean*/` locations. No Lean installation, kernel build or axiom
  replay was performed. The Python policy is deliberately stricter than the
  Lean JSON AST policy for lexical numbers: booleans, floating values and
  exponent notation are rejected here. The actual source uses integer arrays.
- This is not a verified JSON byte parser. Python's parser and exact integer
  arithmetic remain in this audit's trust base. Duplicate keys fail explicitly;
  all consumed archive/source bytes are pinned. The SHA keys are checked,
  unlike the generic dictionary adapter, which treats keys only as selectors.
- Complex phases, affine translations, physical executor direction/allocation,
  dirty-state execution, whole-call hosting, complete precision/tape invoices,
  and all-size multiplication/analytic transfer are not certified. No charge
  is waived or declared free.

## Open next questions

1. **Can the pinned Lean `certifyEntry` replay accept every supplied five-array
   witness?** This would replace the remaining semantic-translation boundary
   with actual kernel/interpreter evidence. First materialize the immutable
   PR1879/1831/1927 source closure and feed these integer-only JSON values at
   dimension73/fuel3, with the same malformed controls. The blocker here is
   the absent Lean4.21/Mathlib308445d7 runtime, not missing certificate data.
2. **Which physical executor realizes the derived address pullback and its
   inverse for every helper occurrence?** This would connect logical charts to
   the implementation. First pin one complete executor and compare its gather
   direction and spectator treatment with the receipt's wrong-order witness.
   Physical allocation, chart direction, phases and priced memory access are
   still separate obligations; this audit supplies no such admission.

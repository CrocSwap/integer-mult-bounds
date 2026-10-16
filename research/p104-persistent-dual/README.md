# P104 inverse-transpose without private allocation or discard

The original P104 G/2 channel has a finite inverse-transpose using **only its
280 persistent registers**, with no private zero allocation, COPY or discard.
It replaces the eight owned accumulator macros in
[PR2479](https://github.com/CrocSwap/integer-mult-bounds/pull/2479) by paid round
trips of their existing Q registers. The exact additional price is **eight H7,
or 56 rank units**. All 72 arbitrary dirty helper values restore.

This removes PR2479's changed finite private-storage contract. It does not
admit the new nonmonotone Q paths to a global owner schedule. The standard
round-trip identity is not claimed new; the result is its source-bound full
chronological realization and exact charge for this outstanding interface.

The physical public operation is the same ordinary inverse-transpose:

```
X_s <- X_s - sum_t G[t,s] Y_t / 2;
Y_t unchanged;
all G, Q, D helpers restored logically.
```

G[t,s] is the ordinary Gram matrix of the 104 pinned root ports. All address
functions and all helper inputs are arbitrary. The object is the original
PR1972/PR1991 channel, not the two-target correction or a full identity supplier.

## Why the excursion implements the public macro

Use the predecessor's dual charts `Delta_V = Gamma_V^(-T)`. For one macro,
Q is at its cap A (dimension eight), and all of its three to five D readers
are at one line B contained in A. The original forward private descent is
`L = Gamma_B Gamma_A^(-1)`. PR2479's public macro is

```
Q <- Q - L^T sum_j D_j;
all D_j unchanged.
```

Instead of accumulating into known-zero private C, execute these public gates:

1. Transport Q from A to B by `T = Delta_B Delta_A^(-1) = conjugate(L)`.
2. Subtract each D_j from Q at B.
3. Return Q from B to A by `T^(-1) = Delta_A Delta_B^(-1) = L^T`.

The resulting physical value is
`T^(-1)(T Q - sum_j D_j) = Q - L^T sum_j D_j`.
This identity includes arbitrary initial Q dirt; it never assumes Q or D is
zero. Each D stays unchanged. Q returns to its original chart before any
outside operation can read it. Therefore substituting these complete macros
preserves the chronological public operation. No retiming is assumed.

The eight uninterrupted source intervals have Q0 through Q7 and respective
reader groups D0-D4, D5-D7, D8-D11, D12-D15, D16-D19, D20-D22, D23-D26,
D27-D31. The generator checks every literal source operation against this
macro pattern. It rejects an interleaved public update or an altered reader
inventory. Every actual scalar contact is checked in the common chart, and
every query departure and return is checked against its current frame.

The separate new rational-row interpreter compares all 280-by-280 public
coefficients and all 280 frames with the retained dual after each of the
eight macros: 627,200 coefficient comparisons, including zeros. It also checks
the full final map. Thus temporary Q motion cannot be hidden by a matching
final transport histogram.

Every new operation is invertible on the same 280-register space. Reversing
the word, negating ADD coefficients and inverting transports gives its literal
inverse. Exact full-column compositions in both orders equal the identity.
This reversibility statement is distinct from the inverse-transpose relation
to the original forward channel, supplied by the macro identity above and
the retained PR2479 proof and replay.

## Native operators and complete finite invoice

All inherited code and data are authenticated by SHA256 and Git blob ID
before import. The retained PR2479 checker first replays its complete word,
original native recipes, physical label isometry, endpoint adapters, ordinary
transpose distinction and full input map. The new checker binds every new
transport occurrence to a specific original PR1972 native occurrence.

The new downward Q edge is the complex conjugate of the original downward C
edge, and the return is its ordinary transpose. For the standard positive
rank-r child, `conjugate(F_r) = X_(2^r-1) F_r`; the extra X is a monomial.
The ordinary transpose reverses monomial permutations without conjugating
diagonal phases, and `F_r^T = F_r`. Both excursion edges consequently have
one positive H7 child. Every other positive child is inherited unchanged in
rank. The literal inverse recipes are separately normalized with one positive
child using the same `F_r^(-1) = X_(2^r-1) F_r` identity.

Signed Pauli action plus one exact nonzero Gaussian state column checks every
derived forward and inverse edge, including global phase. The sixteen
excursion occurrences also check all 512 Gaussian columns (8,192 columns),
and each down/return pair checks as the identity operator. Endpoint adapters
remain the checked inverse-transposed monomials from PR2479; the literal
inverse uses their monomial inverses. No scalar or address/tape lowering is
silently inferred from these finite operator identities.

| Quantity | PR2479 owned dual | Persistent dual |
| --- | ---: | ---: |
| Independent persistent inputs | 280 | 280 |
| Owned private allocations / nonzero discards | 8 / 8 | 0 / 0 |
| Events | 4,058 | 4,042 |
| Scalar ADDs | 2,632 | 2,624 |
| Native transport occurrences | 1,410 | 1,418 |
| Native rank mass | 2,368 | 2,424 |

The new profile is
`1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 16 H7 + 8 H8`.
It applies in both literal execution directions. There are 748 distinct
derived forward native edges, each checked with its normalized inverse variant.
The new rank mass is `2312 + 112`: the eight Q
excursions use sixteen H7 instead of eight private H7. This is an explicit
local operation bill, not an assertion of boundary credit or global excess.

In the restricted macro model where only Q moves, the D frames stay fixed,
Q begins and ends at dimension eight, and an ADD with D requires visiting
their one-dimensional frame, fourteen rank units per macro are minimal.
The total dimension variation before reaching B is at least seven, and the
return requires at least seven. Two H7 attain this bound. This elementary
local observation does not lower-bound arbitrary changed macro circuits,
other moving registers, different reader access, or a complete supplier.

## Reproduce and controls

Standard-library Python 3.12, read-only by default:

```sh
python3 -I -O -B research/p104-persistent-dual/verify.py
python3 -I -O -B research/p104-persistent-dual/test_verify.py
python3 scripts/research_package.py --package research/p104-persistent-dual
```

Expected marker:
`PASS_P104_PERSISTENT_DUAL inputs=280 native=1418 rank_mass=2424 private=0 controls=9 no_new_kappa`.
The author used CPython 3.12.14. Verification compares every field of
[WORD.json](WORD.json) and [RESULT.json](RESULT.json), including complete signed
endpoint and inverse rows. `--out NEW.json` writes only to an unoccupied path.

Controls reject a missing reader, wrong sign, missing return, early read in
the wrong frame, private allocation, a phase-only fault, adjoint/transpose
confusion and a wrong native source-register binding. Reordered equivalent
binary frame bases pass. Export tests run without Git or network, confirm
unchanged file bytes, reject changed executable inputs before import, refuse
missing retained evidence and reject an endpoint coefficient change while
the headline operation counts remain unchanged.

## Limits

No global owners, idle/residual accounting, favorable complete recursive
moment, all-size storage admission, rounded arithmetic, I-G/2 correction,
physical scalar/tape implementation, selected supplier or new kappa is claimed.
No selected-result file or frozen predecessor is changed.

## Open next questions

The next owner question is whether the **actual nonmonotone Q excursions** can
be hosted with all chronological charges. A first step is to assign owners to
the literal added occurrences and price their residual and idle children.
The allocation-free local identity does not answer that question.

The changed word also needs its own precision analysis if adopted in a larger
construction. PR2503 bounds PR2479's accumulator word. Its constants cannot
be transferred to the present Q excursions from equal endpoints alone. This
package neither repeats that analysis nor claims a completed-child error bound.

A corrected P104 word could use this replacement only where its actual
private macro has the same uninterrupted fixed-frame readers. First check
that decomposition and its complete price; interleaved updates or new access
requirements need a different argument.

## Provenance and credit

Canonical base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
PR2479 is retained at `65e58f85d98b4a6344c6221623df1d4caa519604`.
[SOURCES.json](SOURCES.json) and [PREDECESSORS.json](PREDECESSORS.json) bind every
input; [TASK.json](TASK.json) records selection, overlap and scope changes.

Credit Rohan Arun / PR1972 for the complete forward scalar/frame channel,
Chafik Boukhalfa / PR1991 for the finite native realization and retained
independent interpreter, Adam Gall / PR1940 for the schedule, Josie Elliston /
PR1071 and Ali Romman / PR1125 for the fixture and preceding chain. PR2479
supplies the macro inverse-transpose proof and derived native recipes;
the general round-trip and transpose identities are not newly claimed.
All retained source notices and Apache-2.0 attribution are preserved.

Prepared for **ywz65** with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. No independent human review,
proof-assistant kernel, selected supplier cold replay or hosted CI is claimed.

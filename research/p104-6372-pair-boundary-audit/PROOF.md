# Complete scalar endpoint and literal restoration of frozen PR6372

## Result and immutable local checkpoint

The frozen PR6372 word at
`b556600ffe14be72406b03a47c661f3c7f1aff06` has the same complete rational
public transfer matrix as its PR6353 input at
`db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`, on all 770 arbitrary public
inputs. This completes the scalar boundary/restoration gate begun in round 1.
It does not admit the native supplier, physical caller, complete price or
an improved kappa.

The earlier [local proof](https://github.com/ToikY/integer-mult-bounds/blob/2d650f189913e8c2f2bf5c9012c0c67460a9ac66/research/p104-6372-pair-boundary-audit/LOCAL-PROOF.md)
and its two local receipts remain unchanged. They bind the complete
4,709-event input ZERO transcript, B0/B2/C identities on all 770 public
coordinates, four response rows, actual 4,759-event candidate dual prefix
and eleven dual zero CLEAR rows. In particular, C touches arbitrary MAIN
rows 169,193,204 and partial helper 742; only the input basis and off-anchor
correction supports are restricted to full helpers. The present proof
adds the literal response bridge, retained source chronology, actual inverse
tail and complete forward endpoint.

All six scientific source files remain byte-identical to the round 1 pins.
The new checkers import no source constructor, author checker or frozen
local checker. The registered replay separately retains the local checks.

## Exact scalar model and required map

Each public input starts as its own independent rational coordinate. Owned
storage is inactive initially, is initialized to zero at INIT, and is
discarded at CLEAR. ADD/SCALE have their literal rational meanings; COPY is
overwrite, with a zero owned destination checked when present. MOVE retains
the scalar value. Frame identifiers determine active/common-frame chronology
in this projection, not native operators or phases.

For the actual 104 live source roles `L`, define

```
M = I + sum_(r in L) e_(r+112) e_r^T.
```

Thus each main destination receives its own input plus its paired source;
every other public role keeps its own input. The paired role sets are
disjoint. There are 874 nonzero coefficients in this 770-by-770 matrix.
Owned labels are not 29 additional independent external inputs.

## Literal bridge and complete source-word binding

Use the scalar-dual notation of the local proof, including labels Z=3,
Omega=127, F=245 and G=1091. Write `B=B0 B2` and `R=C A B`. The candidate
preparation substitutes zero scratch for anchors 224/227 while holding their
actual arbitrary inputs separately. The local proof gives

```
row224(R)=e224^T,       row227(R)=e227^T,
B2 e224=e224,          B2 e227=e227.
```

Consequently the missing input responses are exactly `C A B0 e224` and
`C A B0 e227`. The nonprimary rows are 119 with coefficients `(2,2)` and
232 with coefficients `(-2,2)`, both at first destination 245. The primary
rows have their unit responses. Every other response coefficient is zero,
including those of MAIN row 204 in the G group.

The actual thirty-event bridge is bound instruction by instruction:

1. Move rows 119/232 to 245 and add their four response terms.
2. Move the two held anchors from 245 to 1091.
3. Move the ten remaining members of the source G group there.
4. Apply the twelve-event expansion of C^-1 at 1091.

Before C^-1, this recovers `C A B x` on every public coordinate. Applying
C^-1 gives `A B x`, retaining arbitrary old main and helper values. The
proof uses the full-row response identities, not only the two unit pairings.

Exactly fourteen original ZERO departures are replaced, on roles

```
119,169,193,204,224,227,229,232,234,742,753,754,755,761.
```

Each removed event is its role's unique actual first departure. After
removing the source's complete ZERO transcript and those departures, all
12,934 retained source instructions occur literally in their original order.
The complete candidate scalar-dual word is exactly

| Block | Events |
|---|---:|
| Immutable local preparation | 4759 |
| Response/C^-1 bridge | 30 |
| Retained source complement | 12934 |
| Actual B0^-1 tail at 127 | 11 |
| Actual B2^-1 tail at 127 | 23 |
| Total | 17757 |

The chronological tail is B0^-1 followed by B2^-1. Its matrix is
`B2^-1 B0^-1=(B0 B2)^-1`; no commutation between the two bases is presumed.
These literal checks prevent a detached correct basis witness from being
mistaken for the emitted word. Full forward replay below independently
checks the resulting endpoint, without relying on native complementation
of the scalar-dual labels.

## Two complete exact endpoint computations

`verify_endpoint.py` propagates complete sparse rational public rows
forward through both literal programs. `oracle_endpoint.py` independently
pulls each public output functional backwards. Its ADD pullback accumulates
the destination coefficient into the source, COPY discards the overwritten
destination coefficient, INIT kills the newly initialized coordinate, and
lifetime checks prevent a functional from crossing an inactive CLEAR value.
No Hermitian conjugation or native interpretation is involved.

Both implementations check all 592,900 public coefficient positions and
independently find the same matrix M for both words. Their canonical matrix
digest is

```
9e097e5b55c0eabb1aef11cf4a59db15f366509d6b2499a7c013bfbd031533ea
```

Equality is checked before hashing. Complete coefficient equality proves
the claim for every vector in `Q^770`, rather than for sampled vectors or
two selected input directions.
The complete censuses, CLEAR functionals, literal block bindings and control
witnesses are retained in `ENDPOINT-RESULT.json` and `ENDPOINT-ORACLE.json`.

The source has 17,657 events and 41 owned lifetimes; the candidate has 17,757
events and 43 lifetimes. Both use 29 owned labels and peak at 13 active owned
fields. Every literal operation uses active storage in its declared frame,
every lifetime ends, and the final public frame declarations match.

## Forward erasure is a separate obligation

The complete forward words have respectively 40 and 42 nonzero scalar
functionals at CLEAR. The candidate's added lifetimes are:

| Role | INIT index | CLEAR index | Public support before CLEAR |
|---|---:|---:|---:|
| 779 | 12998 | 17756 | 97 |
| 780 | 12999 | 17755 | 97 |

Both end at frame 127. Their complete functionals and hashes are retained
by the endpoint receipts. These are nonzero forward rows, distinct from the
eleven zero rows at the local **dual preparation** CLEARs. The scalar model
discards them; it proves no physical permission to erase them.

## Semantic controls

Four primary scalar mutations preserve frame/lifetime grammar and change
actual public coefficients in full-word replay:

| Mutation | Forward event | Output | Input | Correct | Mutated |
|---|---:|---:|---:|---:|---:|
| Omit an input correction | 17754 | 230 | 2 | 0 | 1/4 |
| Reverse one response sign | 12996 | 224 | 2 | 0 | −2 |
| Omit a C^-1 departure update | 12979 | 227 | 0 | 0 | 1 |
| Reverse one output-basis sign | 33 | 126 | 224 | 0 | −1/8 |

The reverse oracle supplies four separate full-word omission/sign checks
with explicit coefficient witnesses. These controls reach rational endpoint
evaluation after structural validation; their rejection does not depend only
on a changed source hash or event count.

The C^-1 control acts after arbitrary anchor data has been reinserted. It is
different from the round 1 conceptual C-response control: a preparation ADD
whose source is a proved zero shadow can be redundant as a literal scalar
operation. No failure of that benign literal omission is claimed.

## Geometry, applicability and remaining boundary

The source and candidate have the same 1,095 stored frame-coordinate lists,
same input declarations and same main/port metadata. Only helper 224/227
final labels change, from 127 to 245. The endpoint checks themselves certify
label chronology and scalar equality, not native operator equality.

A bounded source-geometry check on frames 3/1091/245/127 and the actual
MOVE multiset records ranks 0/4/8/9, with strict inclusions
`span1091 < span245 < span127`. The only MOVE-multiset changes replace
the two public moves `1091→127` on helpers 224/227 by `1091→245`.
Under the **retained nested-native rank tariff**, these data correspond to
local paid change `2H4-2H5` and productive change `2H8-2H9`. This is
conditional applicability of the declared rank model. It does not verify
compiled native maps, absolute phases, all operator columns or tensor widths,
and it does not admit the complete caller, price or claimed kappa.

PR6375 explicitly consumes this exact b556 word and retains the original
PR6372 package blobs. That makes this baseline audit relevant as dependency
evidence. Its six additional input lifts are different edits, and no present
endpoint, geometry, native or funding evidence transfers automatically to
that successor.

Physical erasure, all native maps/widths, actual caller contacts and ownership,
complete recursive/nonrecursive funding, compiler/outer conjunction,
precision/tape and analytic recovery remain separate obligations. The five
framework assumptions `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, and `analytic_recovery` remain. No selected-frontier change, merge or closure
is part of this contribution.

Credit Ali Romman and the PR6372/6353/6349/6348/6350 construction and check
lineage, DreamingOfClouds, Cinna Davis and the full retained NOTICE. The
unchanged local checkpoint and B7 PR6355 retain their exact scopes. The
unpaidmoon handoffs and DreamingOfClouds's PR6375 remain distinct credited
work. New endpoint, literal-restoration and bounded-geometry evidence is
prepared for ToikY with substantial OpenAI Codex assistance and separately
assigned exact evaluators and mathematical review. Same-session agent review
is author-side evidence, not independent human or formal acceptance.

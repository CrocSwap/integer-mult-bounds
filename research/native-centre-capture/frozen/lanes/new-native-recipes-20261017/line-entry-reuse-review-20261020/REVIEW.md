# Independent review of the local line-entry reuse interface

The frozen word accepts sixteen arbitrary independent records in
positive line frames and preserves them as additive baselines.
Both providers pass the complete local map, frame, phase, and
invoice checks. No material defect was found.

This is local reuse with the same reader. It is separate from the
query for a reader kept from an earlier routed stage.

## Frozen inputs and method

The producer
[freeze](../../new-core-transfer-20261017/low-displacement-20261020/row-only-capture-20261020/LINE-ENTRY-REUSE-FREEZE.json)
has SHA256
`a8e212f9cd3cc7ac4a020737ba4889c04a7ae6124877cf770b9555f6f3e54f60`.
The decompressed payload SHA256 is
`efe67a962752f2c36513d84094d215fd0909a5360707938ff99d62743dc72110`.

The accepted formation
[review](../row-capture-native-review-20261020/FREEZE.json)
has SHA256
`488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532`.
Its exact source payload has decompressed SHA256
`7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2`.

The checker imports only the pinned independent review helper and
its integer Gaussian phase interpreter. It imports no producer
code. It checks the new word by reverse output-column propagation
and a separate forward prefix-row pass. It compares exact spatial
columns for every new native recipe.

## Exact arbitrary-record contract

Keep the fixed selected set P and the actual response E from the
formation packet. Put \(W=V_P^{-1}V\), and let C have rows W on P
and identity rows elsewhere. For independent inputs x, ordinary
target values \(y_R\), and selected records \(z_P\), the physical
input is

\[
X_p=Q_px_p,\qquad
Y_p=y_p\quad(p\in R),\qquad
Y_p=Q_pz_p\quad(p\in P).
\]

The physical output is

\[
X'_p=F_9x_p,\qquad
Y'_p=F_9q_p(y+Ex)_p\quad(p\in R),\qquad
Y'_p=F_9[z_p+(CEx)_p]\quad(p\in P).
\]

The ordinary formula uses only \(y_R\); no selected baseline y is
needed there. All sixteen z records are independent of each other,
of x, and of every other field. The word does not form or decode z.

## Literal order and field checks

The word contains no row precode. Its event list is exactly:

1. The 2390 retained core events from the accepted formation word.
2. Sixteen selected line-to-FULL native calls.
3. The 248 events in the accepted late-query word.

Every retained event has its original bytes and order. No retained
event reads or writes a selected target. The selected records
therefore remain unchanged until their line-to-FULL calls.

The new input frame on each selected target is exactly the source
line frame for that port. Its input adapter is the accepted source
adapter for that same port, with an explicit binding to the target
field. All 128 input view fields are distinct.

Every source and selected target is FULL before the late query.
Every scalar addition has the same actual source and target frame.
The final declarations are identical to those of the formation
word. A selected input declared as I is rejected.

Both providers pass all 640 arbitrary input columns. The column
for each selected record is exactly the unit column for that
record's output. All 416 fields outside the two data banks retain
their arbitrary values. No event accesses those fields, and no
new or owned field is introduced.

The forward row pass agrees with the reverse-column result. An
omitted late query is rejected.

## Exact phases

All 1447 retained native recipes are byte equal to the accepted
formation records. The 112 source input adapters and the 96
outgoing ordinary adapters are also exact inherited records.
The sixteen additional input adapters use the accepted source
records with their explicit new field bindings.

For each selected port p, the new recipe must satisfy

\[
N_p\Gamma_{\mathrm{line}(p)}=F_9.
\]

The independent interpreter checks this exact identity on all
512 spatial input columns. There are sixteen new recipes, hence
8192 complete spatial columns and 4194304 nonzero coefficients.
The checks include global phase. A wrong global phase is rejected.

Combining this identity with the accepted input-adapter identity
gives the physical operation \(Q_pz_p\mapsto F_9z_p\).
No Q operator is moved through the reader or the response.
The exact spatial identities tensor to all widths admitted by
the retained native primitive contract.

These H8 recipes retain their two generic monomial maps. The
identity-map refinement for a complete F9 call does not apply here.

## Local invoice and precision scope

Each provider has the exact profile

```text
1392 H1 + 64 H2 + 48 H3 + 16 H8.
```

The complete local counts are:

| Item | Count |
| --- | ---: |
| Native children | 1520 |
| Native mass | 1792 |
| Old real scalar units | 9880 |
| Retained-core scalar units | 6456 |
| Late-query scalar units | 3424 |
| Input monomial views | 128 |
| Output monomial views | 96 |
| Native side-map upper bound | 3040 |
| New or private fields | 0 |
| Odd-arithmetic scans | 0 |

The exact content row one-norm at emitted operation boundaries
is at most 112. The additional content binary denominator height
is one. These bounds include the full retained word and query.
They do not bound primitive internals, recursive-child numerical
guards, or accumulated roundoff.

The sixteen calls remain rank-eight calls. Their exact recursive
sizes, the owner-view work, and the complete caller must be priced
before any complete supplier cost can be claimed.

## The reader condition is necessary

If z stores \(Wy\), the selected output stores \(W(y+Ex)\).
Thus the local update preserves that same reader.

For a different stored reader L, the required update is \(LEx\).
The emitted update \(WEx\) is equal to it on all source inputs if
and only if

\[
(L-W)E=0.
\]

The checker verifies both exact inverse orders for this actual E.
Therefore that condition is equivalent to \(L=W\). More generally,
the same implication holds for ordered operators when E has an
inverse. It does not require any commutation of L, W, or E.

Consequently, a reader from an earlier routed stage needs its
actual ordered query \(L_sE_t\), unless equality of the transported
reader with the current local reader has been proved. The separate
bridge-access construction supplies such queries under its own
premises and invoice. The 9880 local figure is not that invoice.

This review proves the local line-entry interface. It does not
prove a complete routed reuse, a final decoder, a recursive host,
a complete supplier, or a kappa improvement.

## Reproduction and credit

Run from the workspace root:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/line-entry-reuse-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/line-entry-reuse-review-20261020/normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/line-entry-reuse-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/line-entry-reuse-review-20261020/optimized
```

The required final line is
`PASS_INDEPENDENT_LOCAL_LINE_ENTRY_REUSE`.
The reproduction receipt records the final byte comparison and
source hash checks.
Both runs completed with the required result. Their result and
input receipts are byte identical. All 35 consumed source files
were rechecked and are unchanged.

The producer proof retains the controller, cyclic-family, and
formation-work credit. AI assistance was used. No PR, push, commit,
or publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.

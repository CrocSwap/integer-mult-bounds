# Physical selected exchanges on the PR3133 core

The raw selected exchange mechanisms work on both new PR3133 providers.
The zero-line backward word carries the original selected X input into
productive selected Y. Its forward companion exposes the dense ordinary
query in completed selected X. The forward input code uses eight
rank-one children. This pair therefore needs eight new children per
invocation pair, or 32 for four pairs.

These are local maps with explicit operator codes. A controller must use
or remove these codes. The result does not yet give a complete supplier
or a kappa improvement.

## Operator contract

Let A be `[0,7,20,27,36,46,57,111]`, and let U be its complement. In this
coordinate order, the actual source matrices give

    J = [[0,-B],[-D,I-DB]],       BD=13I.

Write `x=(a,u)` and `y=(b,v)`. Physical input X is `Q x`; physical input
Y is y. Each Q_p is the positive port line operator. Physical output X
is `F x'`; physical output Y is `F Q^-1 y'`. F is the common full operator.
It commutes with each port line. No Q operator is commuted through B or D.

Use `r=Q_A^-1 b`. The zero-line backward word B0 has the map

    X_A' = Bv+r,
    X_U' = u-v-Dr+D Q_A a,
    Y_A' = Q_A a,
    Y_U' = v.

Its physical selected Y output is exactly `F a`. Thus the original
selected X information is in a productive output, without a persistent
input-record cohort. The map is a unit. Its content inverse is

    v = Y_U',
    r = X_A'-Bv,
    b = Q_A r,
    a = Q_A^-1 Y_A',
    u = X_U'+v+Dr-D Y_A'.

This inverse formula is not a free native decoder.

The coded forward word F8 has the map

    X_A' = a-Q_A^-1 B u,
    X_U' = u,
    Y_A' = b,
    Y_U' = v+(I-DB)u.

It carries the dense query `Q_A^-1 B u` in selected completed X relative
to its input a. Its content inverse is

    u = X_U',
    a = X_A'+Q_A^-1 B X_U',
    b = Y_A',
    v = Y_U'-X_U'+DB X_U'.

The zero-line forward variant F0 omits the input code. It has the same X
and selected Y rows, but its ordinary Y row also contains `-D Q_A^-1 b`.

The eight-line backward variant B8 first replaces `v` by `v-Dr`. Its map
is

    X_A' = Bv-12r,
    X_U' = u-v+D Q_A a,
    Y_A' = Q_A a,
    Y_U' = v-Dr.

Its optional second eight-line block removes `D Q_A a` from ordinary X.
This gives B16. All equations retain their stated operator order.

## Literal implementation

B0 exchanges each selected physical X and Y field at input, runs the
complete new clean-J backward core, and subtracts D times selected X
from ordinary X at the completed full boundary. Each physical exchange
uses three unit ADDs and one negative SCALE. It acts on arrays at the
same physical addresses. It does not identify their logical frames.

F8 first forms each `Q_a^-1 b_a` in serial owned C0 and adds its D column
to ordinary Y. It clears C0 after each copy. It then exchanges selected
physical X and Y, runs the complete clean-J forward core, and repeats the
physical exchange at output. F0 omits the first code block.

B8 uses the same inverse-line copies with negative D at input, followed
by B0. B16 adds the positive-line output correction. The exact boundary
events are inherited from the frozen raw packets in
`lanes/native-escape-20261017`. The new checker maps only their owned C
indices to the new 632-field namespace. It replaces the old core by the
literal new core; it does not use an endpoint matrix in place of the core.

The new clean-J core preserves unused C1 through C7. To retain the raw
packets' zero-output contract, each transferred word has seven explicit
owned CLEARs at exit. These cost 14 real scalar primitives. They do not
act on borrowed state and need no native child.

## Complete local invoice

| Word | New rank-one children | Complete rank mass | Child count | Scalar bound |
| --- | ---: | ---: | ---: | ---: |
| B0 | 0 | 5073 | 3507 | 168896 |
| B8 | 8 | 5081 | 3515 | 173104 |
| B16 | 16 | 5089 | 3523 | 177312 |
| F0 | 0 | 5073 | 3507 | 164944 |
| F8 | 8 | 5081 | 3515 | 169152 |

Each row includes the full 164514-scalar clean-J core, every new scalar
operation, source access, owned preparation, clear, and restoration.
Each added child has two explicit monomial wrappers. The base child
profile is `{1:2433,2:724,3:228,4:102,5:20}`. Add the listed rank-one
children. Global bridges, decoder operations, idle children, and private
hosting are not included in this local table.

## Exact replay

`emit_raw_selected.py` replays all ten local words: five variants on each
of the base and extra providers. Each run includes all 632 arbitrary live
inputs, eight arbitrary C inputs, and the complete 91-buffer zero-input
contract. All 408 arbitrary helpers restore. All 91 private zero buffers
return to zero. All eight owned C outputs are zero.

The operator alphabet has separate Q, K, and dual-K symbols. K describes
the forward native warp; dual-K describes its inverse transpose. The
replay cancels only adjacent inverse pairs with the same symbol. It does
not commute distinct Q symbols, or move Q through B, D, K, or dual-K.
Every retained scalar frame, native frame transition, warp, and zero-buffer
lifetime is checked. Each source core has 240 warp events.

The checker also verifies the signed native line recipes on all 8192
spatial columns per provider. Five full-word controls reject a wrong
inverse-line sign and missing exchange, code, or lower-shear operations.
The B0 map is also the explicit omitted-code case of B8; its complete
formula is checked, not inferred from a successful search.

## Native phase and reuse

The new native recipe lane has generated fresh recipes for both source
providers. The backward lift must use its explicit literal dual warp
tables. The logical backward replay uses dual-K and does not assume that
the forward physical K table also gives the backward map. The two tables
differ on 172 of the 180 signed warp classes per provider. Both give
rank-zero operations, but their phase data must be correct.

The retained source phase and wrapper review is a separate dependency in
`lanes/new-native-recipes-20261017`. Independent review of the complete
transfer remains required. A caller must also bind its inter-call views,
operator codes, helper owners, private fields, recursive children,
precision, and complete cost. In particular, the zero-line local exchange
does not by itself establish a zero-cost global decoding step.

## Sources and reproduction

The new source words and their contributor credit are linked in
`CLEAN-J-TRANSFER.md`. The raw mechanisms and their source pins are in
`RAW-SELECTED-BACKWARD.md`, `RAW-SELECTED-FORWARD.md`, and
`ZERO-LINE-BACKWARD.md` in the native-escape lane. The coordinating and
native-escape lanes developed those mechanisms. This lane transfers them
to the changed helper geometry and checks the ordered native core.
OpenAI Codex assisted the work. No independent human review is claimed.

Run with one process, from this directory:

    python3 -I -B emit_raw_selected.py

The literal output is `RAW-SELECTED-TRANSFER.json.gz`. The receipt and
freeze file record exact input and output hashes. No PR, push, or
publication commit was made.
